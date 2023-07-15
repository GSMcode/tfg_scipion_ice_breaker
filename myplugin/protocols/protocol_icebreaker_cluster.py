# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     Guillermo Solla Martin(guillermo.solla@estudiante.uam.es)
# *
# * UAM - EPS - Computer engineer - Final degree project
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address guillermo.solla.martin@gmail.com
# *
# **************************************************************************


import os.path
import enum
from pyworkflow.protocol import Protocol, params, Integer
from pyworkflow.utils import Message
from emtable import Table
from pwem.objects import SetOfMicrographs, Set, Micrograph, Image
from relion.convert.convert31 import Writer, Reader
from pwem.protocols import ProtMicrographs
import shutil

class ProtClusterIceBreaker(ProtMicrographs):
    """
    This protocol executes external job ib_job from icebreaker-em.
    The inputs for this command are .star relion type files.
    If preprocess enabled this protocol apply a low pass filter to the input-micrograph set
    to increase contrast of the set.
    Wether preprocess is enabled or not, the protocol create a new set of micrographs based on the input
    which shows the different noise level (intended to be related with ice-thickness) for each zone of the image
    using k-means clustering.
    """
    _label = "micrographs k-means clustering"
    _result = None
    class ProtIcebreakerToMicsOutput(enum.Enum):
        outputMicrographs = SetOfMicrographs()
    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
                Params:
                    form: this is the form to be populated with sections and params.
                """
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam('inputMicrographs',
                      params.PointerParam,
                      pointerClass='SetOfMicrographs',
                      label='Input micrographs',
                      important=True,
                      help='Set of micrographs to be preprocessed with a low-pass filter')
        form.addParam('numberOfCores',
                      params.IntParam,
                      label="Number of cores",
                      important=True,
                      help='Number of cores that will be used in the preprocess operation'
                      )
        form.addParam('preprocessEnabled',
                      params.BooleanParam,
                      label="Flatten the micrograph set (recommended)",
                      important=True,
                      help="This option determine if the micrographs will be flattened with a low-pass filter to increase contrast or not")

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep('createInputFilesStep')
        if self._preprocessEnabled():
            self._insertFunctionStep('preprocessStep')
        self._insertFunctionStep('clusteringStep')
        self._insertFunctionStep('createOutputStep')

    def preprocessStep(self):
        """Create a .star file as expected by iceBreaker"""
        self._log.info("Starting preprocess step...")
        self._log.info("Applying low pass filter --> IB_JOB - FLATTEN")
        cmd = 'ib_job'
        ib_args = self._getArgs('flatten', self._getInputFilename())
        # Ejecutar el comando utilizando runJob
        self.runJob(cmd, arguments=ib_args)
        self._log.info("Icebreaker flatten preprocess ended")
    def createInputFilesStep(self):
        """
        IceBreaker's ib_job command create the flattened files in the same folder where the original files are.
        First step is to create a new step and copy the original micrographs file to tmp path and copy the info
        of the input SetOfMicrographs to the new one updating the new path to temp.
        The last step is to write the SetOfMicrographs in a relion star file which icebreaker can understand.
        """
        newSet = SetOfMicrographs.create(self._getExtraPath())
        newSet.copyInfo(self._getInputMicrographs())
        for mic in self._getInputMicrographs():
            shutil.copy(mic.getFileName(), self._getTmpPath())
            newMic = Micrograph()
            newMic.copy(mic, ignoreAttrs='_filename')
            newMic.setFileName(os.path.abspath(self._getTmpPath(os.path.basename(mic.getFileName()))))
            atts = newMic.getAttributes()
            newSet.append(newMic)
            """for att in atts:
                msg = att[0] + "-->" + str(newmic.getAttributeValue(att[0]))
                self._log.info(msg)"""
            #micsTable.addRow(os.path.abspath(self._getTmpPath(os.path.basename(mic.getFileName()))), mic.getObjId())
        inputStarWriter = Writer()
        inputStarWriter.writeSetOfMicrographs(newSet, self._getExtraPath("input_micrographs.star"))

    def clusteringStep(self):
        cmd = 'ib_job'
        if self._preprocessEnabled():
            ib_args = self._getArgs('group', self._getFlattenedStarFile())
        else:
            ib_args = self._getArgs('group', self._getInputFilename())
        self._log.info("Icebreaker group clustering without preprocessing ended")
        self.runJob(cmd, arguments=ib_args)
    def createOutputStep(self):
        # Ahora a partir del fichero .star debemos crear el SetOfMicrographs con flattened
        extraFltDir = self._getExtraPath('flatten/')
        extraGrpDir = self._getExtraPath('group/')
        for f in os.listdir(self._getTmpPath()):
            fx = os.path.splitext(f)
            if fx[0].endswith('flattened'):
                file = self._getTmpPath(os.path.basename(f))
                shutil.copy(file, extraFltDir)
            elif fx[0].endswith('grouped'):
                file = self._getTmpPath(os.path.basename(f))
                shutil.copy(file, extraGrpDir)
        if self._preprocessEnabled():
            flatMicSet = SetOfMicrographs.create(self._getExtraPath('flatten/'), suffix='flatten' )
            flatMicSet.copyInfo(self._getInputMicrographs())
            flatMicSet.copyAttributes(self._getInputMicrographs())

        groupMicSet = SetOfMicrographs.create(self._getExtraPath('group/'), suffix='group')
        groupMicSet.copyInfo(self._getInputMicrographs())
        groupMicSet.copyAttributes(self._getInputMicrographs())
        self._log.info('OUTPUT MICROGRAPHS:')
        for mic in self._getInputMicrographs():
            fx = os.path.splitext(os.path.basename(mic.getFileName()))
            if self._preprocessEnabled():
                fltMic = Micrograph()
                fltMic.copy(mic, ignoreAttrs='_filename')
                fltFilename = fx[0] + '_flattened' + fx[1]
                fltMic.setFileName(self._getExtraPath('flatten/' + fltFilename))

                flatMicSet.append(fltMic)
                grpFilename = fx[0] + '_flattened_grouped' + fx[1]
            else:
                grpFilename = fx[0] + '_grouped' + fx[1]
            grpMic = Micrograph()
            grpMic.copy(mic, ignoreAttrs='_filename')
            grpMic.setFileName(self._getExtraPath('group/' + grpFilename))
            self._log.info(grpMic.getFileName())
            groupMicSet.append(grpMic)

        if self._preprocessEnabled():
            self._defineOutputs(flattenedOutputSet=flatMicSet, groupedOutputSet=groupMicSet)
        else:
            self._defineOutputs(groupedOutputSet=groupMicSet)
        #self._defineOutputs(, outputSet=groupMicSet)

        # self._defineOutputs(outputFile=self._getOutputFilename())
        # self._defineRelation('flattened', self.inputMicrographs.get(), flatMicSet)
    # --------------------------- INFO functions -----------------------------------

    # --------------------------- UTILS functions ------------------------------
    def _getArgs(self, mode, micrographs):
        """
        Return the list of arguments for iceBreaker's ib_job command
        --o:         directory where the flattened_*.star will be created
        --in_mics:   star file with the information of the input micrograph set
        --mode:      Can be flatten or group. flatten is the preprocessing part of icebreaker.
        --j:         Cores that will be used to run the job.
        """
        args = [
            '--o', self._getExtraPath(mode),
            '--in_mics', os.path.abspath(micrographs),
            '--mode', mode,
            '--j', str(self.numberOfCores.get())
        ]
        return args

    def _getInputFilename(self):
        return self._getExtraPath('input_micrographs.star')

    def _getOutputFilename(self):
        return self._getExtraPath('flattened_micrographs.star')

    def  _getInputMicrographs(self) -> SetOfMicrographs:
        return self.inputMicrographs.get()

    def _getOutputFilename(self):
        return self._getExtraPath('')

    def _preprocessEnabled(self):
        return self.preprocessEnabled.get()
    def _getFlattenedStarFile(self):
        return os.path.abspath(self._getExtraPath('flatten/flattened_micrographs.star'))
