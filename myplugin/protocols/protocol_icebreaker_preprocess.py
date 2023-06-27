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


"""

"""
import os.path

from pyworkflow.protocol import Protocol, params, Integer
from pyworkflow.utils import Message
from emtable import Table
class PreprocessMicrographsIceBreaker(Protocol):
    """
    This protocol will aplppy to a set of motionCorrected micrographs a low pass filter
    Being this the preprocessing operation needed to
    """
    _label = "Preprocess Flatten"
    _result = None
    _sumaryInfo = None
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
            """Create a .star file as expected by iceBreaker"""
            micsTable = Table(colums=['rlnMicrographName'])
            #Por ahora guardaremos el fichero .star en output

            for mic in self.inputMicrographs:
                micsTable.addRow(os.path.abspath(mic.getFileName()))
                self.logger.info(mic.getFileName())
            with open(os.path.join(self.outPutDirectory, 'output_micrographs.star'), 'w') as f:
                f.write("# Star file generated with Scipion\n")
                micsTable.writeStar(f, tableName='')


            """with open(self._getExtraPath('input_micrographs.star'), 'a') as f:
                f.write("# Star file generated with Scipion\n")
                micsTable.writeStar(f, tableName='')"""

        def createOutputStep(self):
            pass
        #--------------------------- INFO functions -----------------------------------

        def _summary(self):
            """ Summarize what the protocol has done"""
            summary = []

            if self.isFinished():
                return summary

        # --------------------------- UTILS functions ------------------------------


