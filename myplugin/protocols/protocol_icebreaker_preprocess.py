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

from pyworkflow.protocol import Protocol, params, Integer
from pyworkflow.utils import Message

class PreproceessIceBreakerPlugin(Protocol):
    """
    This protocol will aplppy to a set of motionCorrected micrographs a low pass filter
    Being this the preprocessing operation needed to
    """
    _label = "Preprocess Flatten"
    _result = None
    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
                Params:
                    form: this is the form to be populated with sections and params.
                """
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam('micrographs'
                      ,params.FileParam,
                      label='Input micrographs',
                      important=True,
                      help='Path to the star file referencing the micrographs')

        # --------------------------- STEPS functions ------------------------------
        def _insertAllSteps(self):
            # Insert processing steps
            self._insertFunctionStep('preprocessStep')
            self._insertFunctionStep('createOutputStep')

        def preprocessStep(self):

            pass
        def createOutputStep(self):
            pass

            # --------------------------- INFO functions -----------------------------------

        def _summary(self):
            """ Summarize what the protocol has done"""
            summary = []

            if self.isFinished():
                summary.append(('Operation --> %s\n' +
                                'Operand 1 --> %1.2f\n' +
                                'Operand 2 --> %1.2f\n' +
                                'RESULT ==> %1.2f\n') %
                               (self.operation.get(), self.operand1.get(),
                                self.operand2.get(), self.result))
                return summary