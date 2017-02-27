# coding: utf-8
################################################################################
# 
# myask_log : functions for logging (debug, print, error) and error counting
#
################################################################################

DEBUG_LEVEL = 99
errorcount = 0
warningcount = 0
final_state = ""

def ResetErrorCounters():
    #--------------------------------------------------------------------------
    # resets error and warning counter
    #--------------------------------------------------------------------------
    global  warningcount
    global  errorcount
    global final_state
    errorcount = 0
    warningcount = 0
    final_state = ""

def SetDebugLevel(level):
    #--------------------------------------------------------------------------
    # set debug level to the specified value
    #--------------------------------------------------------------------------
    global DEBUG_LEVEL 
    DEBUG_LEVEL = level

def GetDebugLevel():
    #--------------------------------------------------------------------------
    # returns current debug level 
    #--------------------------------------------------------------------------
    global DEBUG_LEVEL 
    return DEBUG_LEVEL
    
def GetErrorCounters():
    #--------------------------------------------------------------------------
    # return array with number of errors and number of warnings
    #--------------------------------------------------------------------------
    return [errorcount, warningcount]

def ReportDialogState(state_id):
    #--------------------------------------------------------------------------
    # allows the application to log a dialog state, which can be retrieved via GetFinalState
    # This can be used to validate dialog results against expected result for batch testing
    #--------------------------------------------------------------------------
    global final_state
    debug(2,"Dialog state reported: '"+str(state_id)+"'")
    final_state = str(state_id)
  
def GetDialogState():
    #--------------------------------------------------------------------------
    # Returns the Finalallows the application to log a dialog state, which can be retrieved via GetFinalState
    # This can be used to validate dialog results against expected result for batch testing
    #--------------------------------------------------------------------------
    global final_state
    return final_state

def error(text):
    #--------------------------------------------------------------------------
    # prints error message ad increments errorcount
    #--------------------------------------------------------------------------
    global  errorcount
    print (" ERROR: " + text)
    errorcount += 1

def warning(text):
    #--------------------------------------------------------------------------
    # prints warning message ad increments warningcount
    #--------------------------------------------------------------------------
    global  warningcount#
    print (" WARNING: " + text)
    warningcount += 1

def debug(level, text):
    #--------------------------------------------------------------------------
    # prints debug message if level <= DEBUG_LEVEL
    #--------------------------------------------------------------------------
    if level <= DEBUG_LEVEL:
        print("  Debug ("+str(level)+"): "+ text)
        
