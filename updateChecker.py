# T1nk-R's Update Checker Python Template for Blender Add-Ons
#
#
# This module is responsible for checking if updates are available.
#
# Module authored by T1nk-R (https://github.com/gusztavj/)
#
# PURPOSE & USAGE *****************************************************************************************************************
# You can use this template module to add scheduled update check against a GitHub repo to your Blender add-ons.
#
# Help, support, updates and anything else: https://github.com/gusztavj/Blender-Add-On-GitHub-Update-Checker
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
# This module is provided as-is. Use at your own risk. No warranties, no guarantee, no liability,
# no matter what happens. Still I tried to make sure no weird things happen:
#   * This module is intended to check a GitHub repository of your choice to get information on the latest published version
#     of whatever is contained in the given repository.
#   * CAUTION. This module requires an access token to the GitHub repository. The token is stored as clean text. 
#     Make sure to create a personal token
#     * restricted to only access the repos you want everyone to be able to access
#     * restricted to access code only
#     * restricted to only read code.
#     Note that your personal token expires in a year (or sooner if you decided so). Update check won't work afterwards. To not 
#     disturb your users, such errors are ignored silently. Make sure to change the code and update the token to a newer one
#     before the current expires.
#   * CAUTION. When people use your add-on using this module, they can generate many requests against your repo, 
#     and your GitHub rate limit may be exceeded. To overcome this, be sure to set a proper frequency, but don't forget, users
#     will have access to your source code and may change it.
#   * This template assumes you use semantic versioning using x.y.z tags in the form of x.y.z, vx.y.z or vx.y.z-label.
#
# You may learn more about legal matters on page https://github.com/gusztavj/Blender-Add-On-GitHub-Update-Checker
#
# *********************************************************************************************************************************


# *********************************************************************************************************************************
# IMPLEMENTATION GUIDE
# *********************************************************************************************************************************
#
# See the Readme.md file on how to implement update check functionality.
# 
# *********************************************************************************************************************************


from __future__ import annotations
from . import bl_info
import requests
import re
from datetime import datetime
from bpy.types import PropertyGroup, Operator, Context
from bpy.props import StringProperty, BoolProperty, IntProperty

# Repository information for help and updates #####################################################################################
class RepoInfo:
    """
    Information to access the repository for update checking and help access.
    """
    
    _repoBase = "https://github.com/<USERSLUG>/"
    """Base address of my repositories"""
    
    _repoApiBase = "https://api.github.com/repos/<USERSLUG>/"
    """Base address of my repositories for API calls"""
    
    _repoSlug = "<REPOSLUG>/"
    """Slug for the repository"""

    repoUrl = _repoBase + _repoSlug
    """URL of the repository"""
    
    repoReleasesUrl = _repoBase + _repoSlug + "releases"
    """URL of the releases page of the repository"""
    
    repoReleaseApiUrl = _repoApiBase + _repoSlug + "releases/latest"
    """API URL to get latest release information"""
    
    username = "<USERSLUG>"
    """My username for API access"""
    
    token = "<TOKEN>"
    """A token restricted only to read code from Blender add-on repos (public anyway)"""
    
# Structured update info ##########################################################################################################
class CLASSPREFIXUpdateInfo(PropertyGroup):
    """
    Information about the current and the latest update
    """
    
    checkFrequencyDays: IntProperty(
        name="Update check frequency (days)",
        default=3
    )
    """
    Frequency of checking for new updates (days).
    """
    
    updateAvailable: BoolProperty(
        name="Is update available",
        default=False
    )
    """
    Tells whether an update is available (`True`).
    """
        
    currentVersion: StringProperty(
        name="Installed version",
        default=""
    )
    """
    Version number of the current version running in x.y.z format.
    """
        
    latestVersion: StringProperty(
        name="Latest available version",
        default=""
    )
    """
    Version number of the latest release (the release tag from the repo).
    """
    
    latestVersionName: StringProperty(
        name="Name of latest version",
        default=""
    )
    """
    Name of the latest release.
    """
    
    lastCheckedTimestamp: StringProperty(
        name="When last successful check for updates happened",
        default=""
    )
    """
    Date and time of last successful check for updates.
    """
        
# Operator for checking updates ###################################################################################################
class AUTHORPREFIX_OT_ADDONNAMEUpdateChecker(Operator):    
    """
    Check for updates or retrieve cached update information
    """
    
    # Properties ==================================================================================================================
    
    # Blender-specific stuff ------------------------------------------------------------------------------------------------------    
    bl_idname = "BLIDNAME"
    bl_label = "Check updates for <ADDON-TITLE>"
    bl_description = "Check updates for <ADDON-TITLE>"
    bl_options = {'REGISTER', 'UNDO'}    
    
    # Other properties ------------------------------------------------------------------------------------------------------------
    forceUpdateCheck = BoolProperty(default = False)
    """
    Whether to force update check. Use only for testing. Once the operator is called,
    this is set back to False to prevent accidental flooding of GitHub.
    """

    # Public functions ============================================================================================================
    
    # Perform the operation -------------------------------------------------------------------------------------------------------
    def execute(self, context: Context):
        """
        Performs update check for the add-on and caches results. The cache expires in some days as specified in
        the update info class, and then new check is performed. Until that the cached information is served.

        Args:
            context (bpy.types.Context): A context object passed on by Blender for the current context.
            event: The event triggering the operation, as passed on by Blender.

        Returns:
            {'FINISHED'} or {'ERROR'}, indicating success or failure of the operation.
        """
                
        updateInfo = context.preferences.addons[__package__].preferences.updateInfo
        
        # Check cache expiry only if update check is not forced
        if not self.forceUpdateCheck:                    
            # Check if update check shall be performed based on frequency
            try:                        
                lastCheckDate = datetime.strptime(updateInfo.lastCheckedTimestamp, '%Y-%m-%d %H:%M:%S')
                delta = datetime.now() - lastCheckDate
                if delta.days < updateInfo.checkFrequencyDays: # Successfully checked for updates in the last checkFrequencyDays number of days
                    # Do not flood the repo API, use cached info
                    return
            except: # For example, lastCheck is None as no update check was ever performed yet
                # Could not determine when last update check was performed, do nothing (check it now)
                pass
        else: # turn forcing check off to prevent accidental flooding                
            self.forceUpdateCheck = False
                
        
        try: # if anything goes wrong we silently fail, no need to perform double-checks
            response = requests.get(RepoInfo.repoReleaseApiUrl, timeout=5, auth=(RepoInfo.username, RepoInfo.token))            
        
            updateInfo.latestVersionName = response.json()["name"]
            updateInfo.latestVersion = response.json()["tag_name"]
            
            # Trim leading v and eventual trailing qualifiers such as -alpha
            latestVersionCleaned = re.match("[v]((\d+\.)*(\d+)).*", updateInfo.latestVersion)[1]
            
            # Parse into a list
            latestVersionTags = [int(t) for t in latestVersionCleaned.split(".")]
            
            # Get installed version (already stored as a list by Blender)
            installedVersionTags = bl_info["version"]
            updateInfo.currentVersion = ".".join([str(i) for i in installedVersionTags])
            
            updateInfo.updateAvailable = False
            
            if latestVersionTags[0] > installedVersionTags[0]:
                updateInfo.updateAvailable = True
            else:
                if latestVersionTags[1] > installedVersionTags[1]:
                    updateInfo.updateAvailable = True
                else:
                    if len(installedVersionTags) > 2 and latestVersionTags[2] > installedVersionTags[2]:
                        updateInfo.updateAvailable = True
                        
            # Save timestamp
            updateInfo.lastCheckedTimestamp = f"{datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')}"
            
        except requests.exceptions.Timeout as tex:
            # Timeout, let's not bother the user
            print("<ADDON-TITLE>: Version checking timed out")
            updateInfo.updateAvailable = False
        except Exception as ex: 
            print(f"<ADDON-TITLE>: Error during version check: {ex}")
            updateInfo.updateAvailable = False
                
        return {'FINISHED'}