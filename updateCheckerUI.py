# T1nk-R's Update Checker for Blender Add-Ons
# - part of T1nk-R Utilities for Blender
#
# Version: Please see the version tag under bl_info below.
#
# This module is responsible for showing add-on preferences
#
# Module and add-on authored by T1nk-R (https://github.com/gusztavj/)
#
# PURPOSE & USAGE *****************************************************************************************************************
# You can use this add-on to synchronize the names of meshes with the names of their parent objects.
#
# Help, support, updates and anything else: https://github.com/gusztavj/T1nkR-Update-Checker-for-Blender-Add-Ons
#
# COPYRIGHT ***********************************************************************************************************************
#
# ** MIT License **
# 
# Copyright (c) 2023-2024, T1nk-R (Gusztáv Jánvári)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, 
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# ** Commercial Use **
# 
# I would highly appreciate to get notified via [janvari.gusztav@imprestige.biz](mailto:janvari.gusztav@imprestige.biz) about 
# any such usage. I would be happy to learn this work is of your interest, and to discuss options for commercial support and 
# other services you may need.
#
# DISCLAIMER **********************************************************************************************************************
# This add-on is provided as-is. Use at your own risk. No warranties, no guarantee, no liability,
# no matter what happens. Still I tried to make sure no weird things happen:
#   * This add-on is intended to check if there are updates to it and other Blender add-ons using its services
#   * This add-on is not intended to modify your Blender configuration, nor your objects and other Blender assets in any way.
#
# You may learn more about legal matters on page https://github.com/gusztavj/T1nkR-Update-Checker-for-Blender-Add-Ons
#
# *********************************************************************************************************************************

from . import updateChecker
from bpy.props import PointerProperty
from bpy.types import AddonPreferences


# Addon preferences ###############################################################################################################
class T1nkerUpdateCheckerAddonPreferences(AddonPreferences):    
    """
    Preferences of the add-on.
    """
    
    # Properties required by Blender ==============================================================================================
    bl_idname = __package__
    """
    Blender's ID name for it to know to which add-on this class belongs. This must match the add-on name, 
    so '__package__' shall be used when defining this in a submodule of a python package.
    """        
    
    updateInfo: PointerProperty(type=updateChecker.T1nkrUpdateCheckingInfo) # type: ignore
    """
    Information about the current version and the latest available
    """
    
    # Public functions ============================================================================================================

    # Display addon preferences ---------------------------------------------------------------------------------------------------
    def draw(self, context):
        """
        Draws the UI of the add-on preferences (default settings)

        Args:
            context (bpy.types.Context): A context object passed on by Blender for the current context.
        """
        
        self.updateInfo.init(
            gitHubUserName = "gusztavj", 
            gitHubRepoSlug = "T1nkR-Update-Checker-for-Blender-Add-Ons", 
            updateCheckerProxyUrl = "https://apps.imprestige.biz/gitHubUpdateChecker/", 
            addOnName = T1nkerUpdateCheckerAddonPreferences.bl_idname
            )
        
        updateChecker.T1NKER_OT_UpdateCheckerForBlenderAddOns.drawUpdateAvailableUI(
            context, T1nkerUpdateCheckerAddonPreferences.bl_idname, self.layout)
