# T1nk-R's Update Checker for Blender Add-Ons
# - part of T1nk-R Utilities for Blender
#
# Version: Please see the version tag under bl_info below.
#
# This module is responsible for managing add-on and settings lifecycle.
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

from __future__ import annotations

# Add-on information ==============================================================================================================
bl_info = {
    "name": "T1nk-R Update Checker for Blender Add-Ons (T1nk-R Utilities)",
    "author": "T1nk-R (GusJ)",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "Edit > Preferences > Add-Ons (this window)",
    "description": "An independent component for other Blender add-ons to check for their updates",
    "category": "System",
    "doc_url": "https://github.com/gusztavj/T1nkR-Update-Checker-for-Blender-Add-Ons",
}


# Lifecycle management ############################################################################################################

# Unregister the plugin -----------------------------------------------------------------------------------------------------------
def unregister():
    """
    Delete/unregister what has once been registered, such as menus, hotkeys, classes and so on.
    """

    # Exception are suppressed as we can't do much in case of failure, it's superfluous to annoy the user.
    # In addition, the function is performed as part of the registration to clean up previous leftovers,
    # and in this scenario all operations below shall fail (in a clean state, none of the objects shall exist).
    with contextlib.suppress(Exception):
        
        # Try to delete add-on setting. Don't panic in case of failure, it was probably not registered
        with contextlib.suppress(Exception):
            del bpy.types.Scene.T1nkerUpdateCheckerForBlenderAddOnsSettings
        

        # Unregister classes (in reverse order)
        for c in reversed(classes):
            # Don't panic in case of failure, it was probably not registered
            with contextlib.suppress(Exception):
                bpy.utils.unregister_class(c)
                
# Reload each module to make sure everything is up to date ========================================================================
if "bpy" in locals():
    unregister()
    
    from importlib import reload
        
    # Mind the order to maintain dependency chain
    libs = [updateChecker, updateCheckerUI]
    
    for lib in libs:   
        # Make sure to not fail in case of reload failure
        with contextlib.suppress(Exception):             
            reload(lib)        
    
    del reload

# Imports =========================================================================================================================

import bpy
import contextlib
from . import updateChecker
from . import updateCheckerUI


# Properties ======================================================================================================================


classes = [
    updateChecker.T1nkrUpdateCheckingInfo,
    updateChecker.T1NKER_OT_UpdateCheckerForBlenderAddOns,    
    updateCheckerUI.T1nkerUpdateCheckerAddonPreferences    
]
"""
List of classes requiring registration and unregistration.
"""


# Public functions ================================================================================================================

# Register the plugin -------------------------------------------------------------------------------------------------------------
def register():
    """
    Perform registration of the add-on when being enabled.
    """
    
    # Make sure to avoid double registration
    unregister()
    
    # Register classes
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.Scene.T1nkerUpdateCheckerForBlenderAddOnsSettings = bpy.props.PointerProperty(type=updateChecker.T1nkrUpdateCheckingInfo)
    


                
                
# Developer mode ##################################################################################################################

# Let you run registration without installing. You'll find the command in Edit menu
if __name__ == "__main__":
    register()
