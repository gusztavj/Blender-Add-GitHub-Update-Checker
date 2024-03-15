# T1nk-R's Update Checker for Blender Add-Ons
# - part of T1nk-R Utilities for Blender
#
# Version: Please see the version tag under bl_info below.
#
# This module is responsible for checking if updates are available.
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
from . import bl_info
import requests
import contextlib
from datetime import datetime
from bpy.types import PropertyGroup, Operator, Context, UILayout
from bpy.props import StringProperty, BoolProperty, IntProperty, PointerProperty


# Repository information for help and updates #####################################################################################
class UpdateChecker:
    """
    Information to access the GitHub Update Checker service
    """

    # Properties ==================================================================================================================
    
    # Private properties ----------------------------------------------------------------------------------------------------------        

    _addOnName: str = None
    """Name of the add-on for which to check updates"""    
    
    _userName: str = None
    """The repository owner's GitHub user name"""
        
    _repoSlug: str = None
    """Slug for the repository"""
    
    _proxyApiRootAddress: str = None
    """URL of the GitHub Update Checker proxy's API (root)"""
    
    def _repoBase(self) -> str:
        return UpdateChecker._combineUri("https://github.com", self._userName)
    """Base address of my repositories"""
    
    def _repoApiBase(self) -> str:
        return UpdateChecker._combineUri("https://api.github.com/repos", self._userName)
    """Base address of my repositories for API calls"""        
    
    
    # Public properties ----------------------------------------------------------------------------------------------------------        

    currentVersion: str = ""
    """Version number of the current version running in `x.y.z` format"""
    
    forceUpdateCheck: bool = False
    """Whether to force checking for the updates against the proxy or the cache is okay unless expired"""
    
    def repoUrl(self) -> str:
        """URL of the repository"""
        return UpdateChecker._combineUri(self._repoBase(), self._repoSlug)
    
    def repoReleasesUrl(self) -> str:
        """URL of the releases page of the repository"""
        return UpdateChecker._combineUri(self._repoBase(), self._repoSlug, "releases")
    
    def repoReleaseApiUrl(self) -> str:
        """API URL to get latest release information"""
        return UpdateChecker._combineUri(self._repoApiBase(), self._repoSlug, "releases", "latest")
    
    def updateCheckingServiceUrl(self) -> str:
        """URL to the service endpoint of tge GitHub Update Checker service"""
        
        # Production URL
        return UpdateChecker._combineUri(self._proxyApiRootAddress, "getUpdateInfo")
        
        # Test URL
        return UpdateChecker._combineUri("http://localhost:5000", "getUpdateInfo")
    
    
    # Private functions ===========================================================================================================

    # Strip leading and trailing slashes ------------------------------------------------------------------------------------------    
    @staticmethod
    def _stripSlashes(uriSegment) -> str:
        """Strips leading and trailing slashes"""
        return uriSegment.lstrip("/").rstrip("/")
    
    # Combine segments into a URI -------------------------------------------------------------------------------------------------
    @staticmethod
    def _combineUri(*args: str) -> str:        
        """Combines strings into an URI by stripping all leading and trailing slashes beforehand"""
        return "/".join( f"{UpdateChecker._stripSlashes(segment)}" for segment in args )
            
        
    # Compile proxy request body --------------------------------------------------------------------------------------------------
    def _getRequestBody(self):
        """Compile the body of the request to submit to the proxy"""
        return {
                "appInfo": 
                    {
                        "repoSlug": self._repoSlug,
                        "currentVersion": self.currentVersion
                    },
                    "forceUpdateCheck": self.forceUpdateCheck
            }
    
    # Public functions =============================================================================================================
    
    # Check for updates ------------------------------------------------------------------------------------------------------------                
    def checkForUpdates(self, updateInfo: T1nkrUpdateCheckingInfo):
                
        # Check cache expiry only if update check is not forced
        if not self.forceUpdateCheck:            
            # Check if update check shall be performed based on frequency
            with contextlib.suppress(Exception):
                lastCheckDate = datetime.strptime(updateInfo.lastCheckedTimestamp, '%Y-%m-%d %H:%M:%S')
                delta = datetime.now() - lastCheckDate
                if delta.days < updateInfo.checkFrequencyDays: # Successfully checked for updates in the last checkFrequencyDays number of days
                    # Do not flood the repo API, use cached info
                    return        

        requestTimeoutSec = 5

        try: # if anything goes wrong we silently fail, no need to perform double-checks
            print(f"{self._addOnName}: Trying to check for updates")
            
            # Get installed version (already stored as a list by Blender)

            installedVersionTags = bl_info["version"]
            updateInfo.currentVersion = ".".join([str(i) for i in installedVersionTags])

            self._repoSlug = updateInfo.gitHubRepoSlug
            self.currentVersion = updateInfo.currentVersion
            headers = {'Content-Type': 'application/json'}
            payload = self._getRequestBody()
            response = requests.post(self.updateCheckingServiceUrl(), headers=headers, json=payload, timeout=requestTimeoutSec)

            # For errors, enable raising exceptions
            if response.status_code != 200:
                response.raise_for_status()

            # Being here means a response has been received successfully

            repoInfo = response.json()["repository"]

            updateInfo.latestVersionName = repoInfo["latestVersionName"]
            updateInfo.latestVersion = repoInfo["latestVersion"]                        
            updateInfo.releasesUrl = repoInfo["releaseUrl"]
            updateInfo.repoUrl = repoInfo["repoUrl"]
            updateInfo.updateAvailable = response.json()["updateAvailable"]

            # Save timestamp
            updateInfo.lastCheckedTimestamp = f"{datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')}"
            
            print(f"{self._addOnName}: Checking for updates completed, there is {'a' if updateInfo.updateAvailable else 'no' } new version available")

        except requests.exceptions.Timeout as tex:
            # Timeout, let's not bother the user
            print(f"{self._addOnName}: Version checking timed out after {requestTimeoutSec} second(s)")
            updateInfo.updateAvailable = False
        except Exception as ex: 
            print(f"{self._addOnName}: Error during version check: {ex}")
            updateInfo.updateAvailable = False
        finally:
            # Turn forcing check off to prevent accidental flooding                
            self.forceUpdateCheck = False
            
        # Nothing to return explicitly, changes are conveyed in updateInfo
        
    # Lifecycle management ========================================================================================================
    
    def __init__(self, addOnName: str, userName: str, repoSlug: str, proxyApiRootAddress: str):
        """
        Initializes an instance of the UpdateCheckingInfo class.

        Args:
            userName (str): The GitHub user name of the repository owner.
            repoSlug (str): The slug for the repository.
            proxyApiRootAddress (str): The URL of the GitHub Update Checker proxy's API (root).
        """
        self._userName = userName
        self._repoSlug = UpdateChecker._stripSlashes(repoSlug)
        self._proxyApiRootAddress = UpdateChecker._stripSlashes(proxyApiRootAddress)
                    

# Structured update info ##########################################################################################################
class T1nkrUpdateCheckingInfo(PropertyGroup):
    """
    Information about the current and the latest update
    """
    
    checkFrequencyDays: IntProperty(
        name="Update check frequency (days)",
        default=1
    ) # type: ignore
    """
    Frequency of checking for new updates (days).
    """
    
    forceUpdateCheck: BoolProperty(default = False) # type: ignore
    """
    Whether to force update check. Use only for testing. Once the operator is called,
    this is set back to False to prevent accidental flooding of GitHub.
    """
    
    updateAvailable: BoolProperty(
        name="Is update available",
        default=False
    ) # type: ignore
    """
    Tells whether an update is available (`True`).
    """
        
    currentVersion: StringProperty(
        name="Installed version",
        default=""
    ) # type: ignore
    """
    Version number of the current version running in x.y.z format.
    """
        
    latestVersion: StringProperty(
        name="Latest available version",
        default=""
    ) # type: ignore
    """
    Version number of the latest release (the release tag from the repo).
    """
    
    latestVersionName: StringProperty(
        name="Name of latest version",
        default=""
    ) # type: ignore
    """
    Name of the latest release.
    """
    
    lastCheckedTimestamp: StringProperty(
        name="When last successful check for updates happened",
        default=""
    ) # type: ignore
    """
    Date and time of last successful check for updates.
    """
    
    repoReleasesUrl: StringProperty(
        name="URL of the Releases page of the add-on's repository",
        default=""
    ) # type: ignore
    """
    Date and time of last successful check for updates.
    """

    repoUrl: StringProperty(
        name="URL of the add-on's repository",
        default=""
    ) # type: ignore
    """
    Date and time of last successful check for updates.
    """
    
    gitHubUserName: StringProperty(default = "") # type: ignore
    """GitHub user name of the repository owner."""
    
    gitHubRepoSlug: StringProperty(default = "") # type: ignore
    """The slug for the repository."""
    
    updateCheckerProxyUrl: StringProperty(default = "") # type: ignore
    """The URL of the GitHub Update Checker proxy service. Note that the repoSlug shall be registered on the proxy service
    instance for the requests to be processed."""
    
    addOnName: StringProperty(default = "") # type: ignore
    """Name of the add-on for which to check updates. Used only to correlate log entries in the System Console with the add-on.
    It's best to set it to the `__package__` attribute of your add-on module."""
    
    def init(self, gitHubUserName: str, gitHubRepoSlug: str, updateCheckerProxyUrl: str, addOnName:str):
        self.gitHubUserName = gitHubUserName
        self.gitHubRepoSlug = gitHubRepoSlug
        self.updateCheckerProxyUrl = updateCheckerProxyUrl
        self.addOnName = addOnName
        
        uc = UpdateChecker(addOnName=addOnName, userName=gitHubUserName, repoSlug=gitHubRepoSlug, proxyApiRootAddress=updateCheckerProxyUrl)
        
        self.repoUrl = uc.repoUrl()
        self.repoReleasesUrl = uc.repoReleasesUrl()        
    

# Operator for checking updates ###################################################################################################
class T1NKER_OT_UpdateCheckerForBlenderAddOns(Operator):    
    """
    Checks for updates of a specified Blender add-on
    """
    
    # Properties ==================================================================================================================
    
    # Blender-specific stuff ------------------------------------------------------------------------------------------------------    
    bl_idname = "t1nker.updatecheckerforblenderaddons"
    bl_label = "Update Checker for Blender add-ons"
    bl_description = "Check for updates of a specified Blender add-on"
    bl_options = {'REGISTER'}    
    bl_category = "T1nk-R Utils"

    # Other properties ------------------------------------------------------------------------------------------------------------
    forceUpdateCheck: BoolProperty(default = False) # type: ignore
    """
    Whether to force update check. Use only for testing. Once the operator is called,
    this is set back to False to prevent accidental flooding of GitHub.
    """
    
    gitHubUserName: StringProperty(default = "") # type: ignore
    """GitHub user name of the repository owner."""
    
    gitHubRepoSlug: StringProperty(default = "") # type: ignore
    """The slug for the repository."""
    
    updateCheckerProxyUrl: StringProperty(default = "") # type: ignore
    """The URL of the GitHub Update Checker proxy service. Note that the repoSlug shall be registered on the proxy service
    instance for the requests to be processed."""
    
    addOnName: StringProperty(default = "") # type: ignore
    """Name of the add-on for which to check updates. Used only to correlate log entries in the System Console with the add-on.
    It's best to set it to the `__package__` attribute of your add-on module."""
    
    # Public functions ============================================================================================================
    
    @staticmethod
    def drawUpdateAvailableUI(context: Context, addOnName: str, layout: UILayout, showForceOption: bool = False) -> UILayout:
        # Update available button
        #
        
        box = layout.box()
        buttonRow = box.row()
        
        try: # to see if we know anything about updates
            updateInfo: T1nkrUpdateCheckingInfo = context.preferences.addons[addOnName].preferences.updateInfo
            
            # Note that checking update is part of executing the main operator, that is, performing at least
            # one synchronization. Until that no updates will be detected. Updates are not checked each time
            # this dialog is drawn, but as set in `updateInfo.T1nkerMeshNameSynchronizerUpdateInfo.checkFrequencyDays`.
            if updateInfo.updateAvailable:
                # Draw update button and tip
                opUpdate = buttonRow.column().row().operator(
                        'wm.url_open',
                        text = "Update available",
                        icon = "URL"
                        )                                            
                opUpdate.url = updateInfo.repoReleasesUrl
                
                opCheck = box.column().row().operator(
                    T1NKER_OT_UpdateCheckerForBlenderAddOns.bl_idname,
                    text = "Force re-check",
                    icon = "FILE_REFRESH"
                )
                
                opCheck.gitHubUserName = updateInfo.gitHubUserName 
                opCheck.gitHubRepoSlug = updateInfo.gitHubRepoSlug
                opCheck.updateCheckerProxyUrl = updateInfo.updateCheckerProxyUrl                
                opCheck.addOnName = addOnName
                
                
                box.row().label(text=f"You can update from v{updateInfo.currentVersion} to {updateInfo.latestVersion}")
            else:
                opCheck = box.column().row().operator(
                    T1NKER_OT_UpdateCheckerForBlenderAddOns.bl_idname,
                    text = "Check for Updates",
                    icon = "FILE_REFRESH"
                )
                
                box.column().row().prop(updateInfo, "forceUpdateCheck", text="Force check to bypass proxy cache")
                
                opCheck.gitHubUserName = updateInfo.gitHubUserName 
                opCheck.gitHubRepoSlug = updateInfo.gitHubRepoSlug
                opCheck.updateCheckerProxyUrl = updateInfo.updateCheckerProxyUrl
                opCheck.addOnName = addOnName                
        except Exception as ex: 
            print(ex)
            # Do nothing, if we could not check updates, probably this is the first time of enabling the add-on
            # and corresponding data structures are not yet available.
            pass
        
        return layout
        
    @staticmethod
    def drawUpdateCheckingAndHelpUI(context: Context, addOnName: str, layout: UILayout) -> UILayout:   
        
        updateInfo: T1nkrUpdateCheckingInfo = context.preferences.addons[addOnName].preferences.updateInfo
        
        # Help and update buttons
        #
        box = layout.box()
        buttonRow = box.row()
        
        # Help button
        #
        
        opHelp = buttonRow.column().row().operator(
            'wm.url_open',
            text='Help',
            icon='URL'
            )
        opHelp.url = updateInfo.repoUrl
        
        # Update available button
        #
        
        try:                        
            # Note that checking update is part of executing the main operator, that is, performing at least
            # one synchronization. Until that no updates will be detected. Updates are not checked each time
            # this dialog is drawn, but as set in `updateInfo.T1nkerMeshNameSynchronizerUpdateInfo.checkFrequencyDays`.
            if updateInfo.updateAvailable:
                # Update button            
                opUpdate = buttonRow.column().row().operator(
                        'wm.url_open',
                        text="Update available",
                        icon='URL'
                        )            
                opUpdate.url = updateInfo.repoReleasesUrl
                box.row().label(text=f"You can update from v{updateInfo.currentVersion} to {updateInfo.latestVersion}")
        except Exception as ex:
            # Fail silently if we cannot check for updates or draw the UI
            print(ex)
            pass    
        
        return layout
    
    # Perform the operation -------------------------------------------------------------------------------------------------------
    def execute(self, context: Context):  # sourcery skip: extract-method
        """
        Performs update check for the add-on and caches results. The cache expires in some days as specified in
        `UpdateInfo.checkFrequencyDays`, and then new check is performed. Until that the
        cached information is served unless checking is forced via `forceUpdateCheck` of the operator object.

        Args:
            context (bpy.types.Context): A context object passed on by Blender for the current context.
        
        Indirect args you can or need to set for the function to make sense:
        
            gitHubUserName: str = None: Class property to specify GitHub user name of the repository owner.
    
            gitHubRepoSlug: str = None: Class property to specify the slug for the repository.
    
            updateCheckerProxyUrl: str = None: Class property to specify the URL of the GitHub Update Checker proxy service. 
            Note that the repoSlug shall be registered on the proxy service instance for the requests to be processed.
    
            addOnName: str = None: Class property to specify the name of the add-on for which to check updates. 
            Used only to correlate log entries in the System Console with the add-on. It's best to set it to the `__package__` attribute 
            of your add-on module.

        Returns:
            {'FINISHED'} whatever happens to not disturb the user. The console log may contain information on success or failure of the
            operation.
        """
        
        # Suppress all exceptions to not distract the user
        with contextlib.suppress(Exception):
            updateInfo = context.preferences.addons[self.addOnName].preferences.updateInfo

            # Create update checker engine
            uc = UpdateChecker(
                addOnName=self.addOnName, 
                userName=self.gitHubUserName, 
                repoSlug=self.gitHubRepoSlug, 
                proxyApiRootAddress=self.updateCheckerProxyUrl
            )
            
            uc.forceUpdateCheck = updateInfo.forceUpdateCheck
                    
            # Check for updates by passing known update info
            uc.checkForUpdates(updateInfo=updateInfo)
            if updateInfo.updateAvailable:
                self.report({"INFO"}, f"{self.addOnName}: New version is available")
            else:
                self.report({"INFO"}, f"{self.addOnName}: No new version is available")

        return {'FINISHED'}