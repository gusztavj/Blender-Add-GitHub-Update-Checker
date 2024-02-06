def execute(self, context):
    # -- Other stuff to do
    
    # Call the update checker to check for updates time to time, as specified in 
    # `updateInfo.CLASSPREFIXUpdateInfo.checkFrequencyDays`
    try:
        bpy.ops.BLIDNAME()            
    except:
        # Don't mess up anything if update checking doesn't work, just ignore the error
        pass
    
    # -- Other stuff to do