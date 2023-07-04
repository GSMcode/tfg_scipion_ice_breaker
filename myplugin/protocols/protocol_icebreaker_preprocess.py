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

from pyworkflow.protocol import Protocol, params, Integer
from pyworkflow.utils import Message
from emtable import Table
from pwem.objects import SetOfMicrographs, Set
import relion.convert as convert

class PreprocessMicrographsIceBreaker(Protocol):
    """
    This protocol will aplppy to a set of motionCorrected micrographs a low pass filter
    Being this the preprocessing operation needed to
    """
    _label = "Preprocess Flatten"
    _result = None
    _output_directory = None

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
        form.addParam('outputDirectory',
                      params.FolderParam,
                      label="Output directory",
                      important=False,
                      help="Path where the results of the preprocess operation will be staged, default location is...")

    # --------------------------- STEPS functions ------------------------------
    def _insertAllSteps(self):
        # Insert processing steps
        self._insertFunctionStep('preprocessStep')
        self._insertFunctionStep('createOutputStep')

    def preprocessStep(self):
        if self.outputDirectory.get():
            msg = "Output directory: " + self.outputDirectory.get()
            output = self.outputDirectory.get()
        else:
            msg = "Not output directory selected, folders will be created in " + self._getExtraPath()
            output = self._getExtraPath()
        self._log.info(msg)
        self._output_directory = self._getExtraPath()
        """Create a .star file as expected by iceBreaker"""
        self._log.info("Creating star input files...")
        self._createInputFiles()
        self._log.info("Input star files created.")
        self._log.info("Applying low pass filter --> IB_JOB - FLATTEN")
        # Setting arguments for ib_job
        ib_args = self._getArgs()
        cmd = 'ib_job'
        # Ejecutar el comando utilizando runJob
        self.runJob(cmd, arguments=ib_args)

    def createOutputStep(self):
        outputName = "flattenedMicrographs"
        outputMicrographs = self._getFlattenedMicrographs()
        pass

    # --------------------------- INFO functions -----------------------------------

    # --------------------------- UTILS functions ------------------------------
    def _createInputFiles(self):
        self._log.info("Create a .star file as expected by iceBreaker")
        micsTable = Table(columns=['rlnMicrographName'])
        # Por ahora guardaremos el fichero .star en output
        self._log.info("Micrographs path: ")
        for mic in self.inputMicrographs.get():
            self._log.info(os.path.abspath(mic.getFileName()))
            micsTable.addRow(os.path.abspath(mic.getFileName()))
        with open(os.path.join(self._output_directory, 'input_micrographs.star'), 'w') as f:
            f.write("# Star file generated with Scipion\n")
            micsTable.writeStar(f, tableName='micrographs')

    def _getArgs(self):
        # Return the lsit of args for the c_getArgsommand
        args = [
            '--o', self._output_directory,
            '--in_mics', self._getInputFilename(),
            '--mode', 'flatten',
            '--j', str(self.numberOfCores.get())
        ]
        return args

    def _getInputFilename(self):
        return self._getExtraPath('input_micrographs.star')
    def _getOutputFilename(self):
        return self._getExtraPath('')
    def _getFlattenedMicrographs(self):
        micSet = SetOfMicrographs(filename=':flattened:')
        starWriter = convert.createWriter(outputDir=self._output_directory,
                                          useBaseName=True)
        starWriter.writeSetOfMicrographs(micSet, os.path.join(self._output_directory,
                                                              ))
