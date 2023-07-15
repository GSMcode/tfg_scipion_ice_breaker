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
# *  e-mail address guillermo.solla@estudiante.uam.es
# *
# **************************************************************************


import os.path
import enum
from pyworkflow.protocol import Protocol, params, Integer
from pyworkflow.utils import Message
from emtable import Table
from pwem.objects import SetOfMicrographs, Set, Micrograph, SetOfParticles, Particle
from relion.convert.convert31 import Writer, Reader
from pwem.protocols import ProtParticles
import shutil
import gemmi
import json
import numpy as np

class ProtGroupThicknessIceBreaker(ProtParticles):
    _label = "estimate ice thickness"

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
                      label='Clustered micrographs',
                      important=True,
                      help='Set of clustered micrographs')
        form.addParam('inputParticles',
                      params.PointerParam,
                      pointerClass='SetOfParticles',
                      label='Input particles',
                      important=True,
                      help='Set of particles')
        form.addParam('maxIceGroups',
                      params.IntParam,
                      label='Maximum number of groups',
                      important=True,
                      help='This parameter sets the maximum number of particles subsets that the protocol should return')
    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep('createInputFilesStep')
        self._insertFunctionStep('groupingStep')
        self._insertFunctionStep('createOutputStep')

    def createInputFilesStep(self):
        inputStarWriter = Writer()
        inputStarWriter.writeSetOfParticles(self._getInputParticles(), self._getInputParticlesFile())
        # Hay problemas con las rutas en las que espera ib_group las micrografias
        # Se replica la forma que tiene de crear las rutas para las micrografias esperadas en ib_group
        in_doc = gemmi.cif.read_file(self._getInputParticlesFile())
        data_as_dict = json.loads(in_doc.as_json())["particles"]

        micNamesAux = list(set(data_as_dict["_rlnmicrographname"]))
        micNames = []
        for n in micNamesAux:
            micNames.append(n[:-4])
        newMicSet = SetOfMicrographs.create(self._getExtraPath())
        newMicSet.copyInfo(self._getInputMicrographs())

        for mic in self._getInputMicrographs():
            newMic = Micrograph()
            newFilename = mic.getFileName()
            for n in micNames:
                if n in mic.getFileName():
                    newFilename = n + '_grouped.mrc'
            newMic.copy(mic, ignoreAttrs='_filename')
            os.rename(shutil.copy(mic.getFileName(), self._getExtraPath()), self._getExtraPath(newFilename))
            newMic.setFileName(os.path.abspath(self._getExtraPath(newFilename)))
            newMicSet.append(newMic)

        inputStarWriter.writeSetOfMicrographs(newMicSet, self._getInputMicrographsFile())

        """for mic in self._getInputMicrographs():
            shutil.copy(mic.getFileName(), self._getTmpPath())
            newMic = Micrograph()
            newMic.copy(mic, ignoreAttrs='_filename')
            newMic.setFileName(os.path.abspath(self._getTmpPath(os.path.basename(mic.getFileName()))))
            atts = newMic.getAttributes()
            for att in atts:
                            msg = att[0] + "-->" + str(newMic.getAttributeValue(att[0]))
                            self._log.info(msg)"""
        """"list = []
        for part in self._getInputParticles():
            if part.getMicId() not in list:
                list.append(part.getMicId())
                atts = part.getAttributes()
                for att in atts:
                    msg = att[0] + "-->" + str(part.getAttributeValue(att[0]))
                    self._log.info(msg)
        for i in list:
            self._log.info(i)"""


    def groupingStep(self):
        cmd = 'ib_group'
        ib_args = self._getArgs()
        self.runJob(cmd, arguments=ib_args)

    def createOutputStep(self):
        outputStarReader = Reader()
        outputPartSet = SetOfParticles.create(self._getExtraPath())
        outputStarReader.readSetOfParticles(self._getOutputParticlesFile(), outputPartSet)
        in_doc = gemmi.cif.read_file(self._getOutputParticlesFile())
        data_as_dict = json.loads(in_doc.as_json())["particles"]
        # Vamos a asignar a cada grosor de hielo las particulas que tienen este grosor
        iceThicknessGroups = {}
        tuples = (data_as_dict['_rlnhelicaltubeid'], data_as_dict['_rlnimageid'])
        for i in range(len(tuples[0])):
            ice = tuples[0][i]
            img = tuples[1][i]
            if tuples[0][i] in iceThicknessGroups.keys():
                iceThicknessGroups[ice].append(img)
            else:
                iceThicknessGroups[ice] = []
                iceThicknessGroups[ice].append(img)
        partSets = {}
        iceGroups = self._organizeSubsets(iceThicknessGroups)
        # Creamos un subset de particulas por cada grosor de hielo
        for i in range(len(iceGroups)):
            label = iceGroups[i]['label']
            setname = 'subset_icegroup_' + label
            iceparts = iceGroups[i]['values']
            subset = SetOfParticles.create(self._getExtraPath(), suffix=setname)
            subset.copyInfo(outputPartSet)
            for id in iceparts:
                subset.append(outputPartSet.__getitem__(id))
            partSets[label] = subset
        self._defineOutputs(**partSets)
    # --------------------------- UTILS functions ------------------------------
    def _getInputMicrographs(self) -> SetOfMicrographs:
        return self.inputMicrographs.get()

    def  _getInputParticles(self) -> SetOfParticles:
        return self.inputParticles.get()

    def _getInputMicrographsFile(self):
        return self._getExtraPath("input_micrographs.star")
    def _getInputParticlesFile(self):
        return self._getExtraPath("input_particles.star")

    def _getArgs(self):
        """
        Return the list of arguments for iceBreaker's ib_job command
        --o:         directory where the flattened_*.star will be created
        --in_mics:   star file with the information of the input micrograph set
        --mode:      Can be flatten or group. flatten is the preprocessing part of icebreaker.
        --j:         Cores that will be used to run the job.
        """
        args = [
            '--o', self._getExtraPath('output_group'),
            '--in_mics', os.path.abspath(self._getInputMicrographsFile()),
            '--in_parts', os.path.abspath(self._getInputParticlesFile()),
        ]
        return args

    def _getOutputParticlesFile(self):
        return self._getExtraPath('output_group/particles.star')

    def _getMaximumGroups(self):
        if self.maxIceGroups.get() <= 0:
            return 1
        else:
            return self.maxIceGroups.get()

    def _organizeSubsets(self, icegroups):
        newIceGroups = []
        min = np.min(list(icegroups.keys()))
        max = np.max(list(icegroups.keys()))
        thresholds = []
        labels = []
        step = int(np.floor((max-min)/self._getMaximumGroups()))
        self._log.info(step)
        actual = min
        for i in range(self._getMaximumGroups()-1):
            previous = actual
            actual = actual + step
            thresholds.append(actual)
            labels.append(str(previous) + '_' + str(actual))
        labels.append(str(actual) + '_' + str(max))
        thresholds.append(max)
        self._log.info(thresholds)
        prvt = 0
        for i in range(len(thresholds)):
            t = thresholds[i]
            newIceGroups.append({})
            newIceGroups[i]['label'] = labels[i]
            newIceGroups[i]['values'] = []

            for k in icegroups.keys():
                if prvt < k <= t:
                    newIceGroups[i]['values'].extend(icegroups[k])
            prvt = t
            newIceGroups[i]['values'] = list(set(newIceGroups[i]['values']))
        self._log.info(newIceGroups)
        return newIceGroups