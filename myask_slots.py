# coding: utf-8
################################################################################
#
# myask_slots : functions to read, normalize and write slot and session attributes
#
################################################################################


import myask_log
import re
from datetime import datetime

CONST_UNDEF_DURATION = 99
FAKEDATE_EVENT_NOT_FOUND = "1988-01-01"
FAKEDATE_CALENDAR_NOT_FOUND = "1999-01-01"


def error_slots_missing(function_name):
    myask_log.error("Slot missing in function " + function_name)
    return "ERROR: Sorry, da fehlt irgendeine Information in " + function_name


#-------------------------------------------------------------------------------
def checkslots(slots, checklist, functionname):
#-------------------------------------------------------------------------------
# checks if all slots in checklist are contained in the slots data structure
# returns False and prints an error message if not
    
    for check in checklist:
        if check not in slots:
            myask_log.error ("ERROR in function "+ functionname+ ": missing slot '" + check + "' in slotlist \n" +\
                  "Slots: "+ str(slots) + "\n")
            return False
    return True

def store_session_slots(intent, slotlist, slots):

# Stores selected information from the current state in the session cookie
# This info will be available next time
# intent: name of the active intent ("" if none)
# slotlist: list of slotnames, for which the infor shall be stored
# slots current slot values
#-------------------------------------------------------------------------------

    myask_log.debug(3, "storing session attributes for intent "+str(intent))
    session_attributes = {}
    if intent != "": session_attributes['prev_intent'] = intent
        
    for slotname in slotlist:
        if slotname in slots:
            val =  slots[slotname]
            slottype = type(val)
            if isinstance(val, datetime):
                session_attributes[slotname] = "DATE:"+val.strftime('%Y-%m-%d')
            elif slottype == list:
                # todo: print/read sequence
                session_attributes[slotname] = str(slots[slotname])
            elif slottype == int:
                session_attributes[slotname] = str(slots[slotname])
            else:
                session_attributes[slotname] = str(slots[slotname])
            
            if slotname+".literal" in slots:
                session_attributes[slotname+".literal"] = slots[slotname+".literal"].decode("unicode-escape")
                
    return session_attributes  

def readAmazonDate(date_str):
    #check for exact date e.g. 2015-11-25.
    if re.match("\d\d\d\d-\d\d-\d\d$", date_str): 
        start_date = datetime.strptime(date_str, "%Y-%m-%d")
        duration = 1
    #check for weekend e.g. 2015-W49-WE
    elif re.match("\d\d\d\d-W\d\d-WE$", date_str): 
        tmp_str = date_str+ ":7"
        start_date = datetime.strptime(tmp_str, "%Y-W%W:%w")
        duration = 2
    #check for week e.g. 2015-W49
    elif re.match("\d\d\d\d-W\d+$", date_str): 
        tmp_str= date_str+":0"
        start_date = datetime.strptime(tmp_str, "%Y-W%W:%w")
        duration = 7
    #check for month e.g. 2015-12
    elif re.match("\d\d\d\d-\d+$", date_str): 
        tmp_str= date_str +"-01"
        start_date = datetime.strptime(tmp_str, "%Y-%m-%d")
        duration = 30
    #check for year e.g. 2015
    elif re.match("\d\d\d\d$", date_str): 
        tmp_str= date_str+"-01-01"
        start_date = datetime.strptime(tmp_str, "%Y-%m-%d")
        duration = 365
    #handle unknown dates
    else:
        myask_log.error(" unknown date format '" + date_str +"'")
        start_date = datetime.today() 
        duration = CONST_UNDEF_DURATION
    return (start_date, duration)
#-------------------------------------------------------------------------------
# 
def parse_slots(intent, session, continue_session, input_locale, appdef):
    #---------------------------------------------------------------------------
    # parse the slots from the intent structure 
    # and combine it with the session attributes if requested
    # PARAMETERS:
    # - intent: Alexa intent structure including 'slots' data 
    # - session: Alexa session structure, including 'attributes' data
    # - continue_session: If True,session_attributes are used 
    # - input_locale: used to set locale and language correctly
    # - appdef
    # RETURN:
    # data structure with all application slots.
    # slots are provided as canonicals with an additional SLOTNAME.literal field
    #---------------------------------------------------------------------------
    slots = {}
    if input_locale in ["de-DE", "deu_deu"] : 
        lang = "de-DE"
        utc_offset = 1
    else:
        myask_log.error("Unsupported input locale '"+ input_locale +"'")
        lang = input_locale
        utc_offset = 0

    slots['lang'] = lang
    slots['utc_offset'] = utc_offset

    if continue_session == True: 
        if  'attributes' in session: 
            myask_log.debug(3, "SESSION_ATTRIBUTES: "+ str(session) )    
            session_attributes = session['attributes']
            for sessionslot in session_attributes:
                if re.match("DATE:\d\d\d\d-\d+-\d+$", session_attributes[sessionslot]): 
                    tmp_str= session_attributes[sessionslot]
                    slots[sessionslot] = datetime.strptime(tmp_str, "DATE:%Y-%m-%d")
                else: slots[sessionslot] = session_attributes[sessionslot]
        else:
            myask_log.error("SESSION_ATTRIBUTES: ERROR NO ATTRIBUTES FOUND \n"+ str(session) +"\nEND_SESSION_ATTRIBUTES")

    if 'slots' in intent:        
        for inputslot in intent['slots']:
            if 'value' not in intent['slots'][inputslot]:
                continue
            if appdef.isApplicationSlot(inputslot):
                literal = intent['slots'][inputslot]['value']
                if appdef.getSlottype(inputslot) == "AMAZON.DATE":                
                    (slots[inputslot],slots[inputslot+'.duration']) = readAmazonDate(literal)
                    slots[inputslot+'.literal'] = literal
                elif appdef.getSlottype(inputslot) == "AMAZON.NUMBER":
                    slots[inputslot] = literal
                else:
                    slots[inputslot] = appdef.GetSlotCanonical(inputslot,literal)
                    slots[inputslot+".literal"] = literal.encode('utf-8')
    else:
        myask_log.debug(2, "No slots section found")
    myask_log.debug(5, "SLOTS: "+ str(slots))    
    return slots
    
