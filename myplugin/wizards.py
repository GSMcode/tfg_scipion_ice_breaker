# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     you (you@yourinstitution.email)
# *
# * your institution
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
# *  e-mail address 'you@yourinstitution.email'
# *
# **************************************************************************
from pwem.wizards import DownsampleWizard
from pyworkflow.gui import ListTreeProviderString, dialog
from pyworkflow.object import String
from pyworkflow.wizard import Wizard
from myplugin.protocols.protocol_icebreaker_cluster import PreprocessMicrographsIceBreaker

"""
class PreprocessIceBreakerWizard(Wizard):
    # Dictionary to target protocol parameters
    _targets = [(PreprocessMicrographsIceBreaker ['input'])]
    def show(self, form, *params):

        # This are the greetings:
        operations = [String("Sum"), String("Subtract"),
                     String("Multiply"), String("Divide")]
        # Get a data provider from the greetings to be used in the tree (dialog)
        provider = ListTreeProviderString(operations)

        # Show the dialog
        dlg = dialog.ListDialog(form.root, "My calculation operations", provider,
                                "Select one of the operations")

        # Set the chosen value back to the form
        form.setVar('operation', dlg.values[0].get())
"""