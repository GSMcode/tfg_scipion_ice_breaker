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
from pwem.objects import SetOfMicrographs, Set, Micrograph
from relion.convert.convert31 import Writer, Reader
import shutil

class GroupThicknessIceBreaker(Protocol):

    # -------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        """ Define the input parameters that will be used.
                Params:
                    form: this is the form to be populated with sections and params.
                """
        form.addSection(label=Message.LABEL_INPUT)
        form.addParam('flattenedMicrographs',
                      params.PointerParam,
                      pointerClass='SetOfMicrographs',
                      label='Input micrographs',
                      important=True,
                      help='Set of preprocessed micrographs')
        form.addParam('micrographParticles',
                      params.PointerParam,
                      pointerClass='SetOfMicrographs',
                      label='Input micrographs',
                      important=True,
                      help='Set of preprocessed micrographs')
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