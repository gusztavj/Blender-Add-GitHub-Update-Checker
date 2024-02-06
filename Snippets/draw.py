def draw(self, context):
    # -- Other stuff to do
    
    try: # to see if we know anything about updates
        updateInfo = context.preferences.addons[__package__].preferences.updateInfo
        
        # Note that checking update is part of executing the main operator, that is, performing at least
        # one synchronization. Until that no updates will be detected. Updates are not checked each time
        # this dialog is drawn, but as set in `updateInfo.CLASSPREFIXUpdateInfo.checkFrequencyDays`.
        if updateInfo.updateAvailable:
            # Draw update button and tip
            opUpdate = layout.column().row().operator(
                    'wm.url_open',
                    text=f"Update available",
                    icon='URL'
                    )            
            opUpdate.url = updateChecker.RepoInfo.repoReleasesUrl
            layout.row().label(text=f"You can update from {updateInfo.currentVersion} to {updateInfo.latestVersion}")
    except:
        # Do nothing, if we could not check updates, probably this is the first time of enabling the add-on
        # and corresponding data structures are not yet available.
        pass
    
    # -- Other stuff to do