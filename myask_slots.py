# coding: utf-8
################################################################################
#
# myask_slots : functions to read, normalize and write slot and session attributes
#
#-------------------------------------------------------------------------------
# https://github.com/acmurmeltier69/myask
# Written 2017 by acmurmeltier69 (acmurmeltier69@mnbvcx.eu)
# Shared under GNU GENERAL PUBLIC LICENSE Version 3
# https://github.com/acmurmeltier69/myask
#-------------------------------------------------------------------------------
################################################################################


import myask_log
import re
from datetime import datetime, date, timedelta

CONST_UNDEF_DURATION = 999
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
            elif isinstance(val, date):
                session_attributes[slotname] = "DATE:"+val.strftime('%Y-%m-%d')
            elif slottype == list:
                # todo: print/read sequence
                session_attributes[slotname] = str(slots[slotname])
            elif slottype == int:
                session_attributes[slotname] = str(slots[slotname])
            else:
                session_attributes[slotname] = str(slots[slotname])
            
            if slotname+".literal" in slots:
                session_attributes[slotname+".literal"] = slots[slotname+".literal"]
                
    return session_attributes  

def readAmazonDate(date_str):
    #check for exact date e.g. 2015-11-25.
    if re.match("\d\d\d\d-\d\d-\d\d$", date_str): 
        start_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        duration = 1
    #check for weekend e.g. 2015-W49-WE
    elif re.match("\d\d\d\d-W\d\d-WE$", date_str): 
        tmp_str = date_str[:-3]
        tmp_str = tmp_str+ ":6"
        start_date = datetime.strptime(tmp_str, "%Y-W%W:%w").date()
        duration = 2
    #check for week e.g. 2015-W49
    elif re.match("\d\d\d\d-W\d+$", date_str): 
        tmp_str= date_str+":0"
        start_date = datetime.strptime(tmp_str, "%Y-W%W:%w").date()
        duration = 7
    #check for month e.g. 2015-12
    elif re.match("\d\d\d\d-\d+$", date_str): 
        tmp_str= date_str +"-01"
        start_date = datetime.strptime(tmp_str, "%Y-%m-%d").date()
        duration = 30
    #check for year e.g. 2015
    elif re.match("\d\d\d\d$", date_str): 
        tmp_str= date_str+"-01-01"
        start_date = datetime.strptime(tmp_str, "%Y-%m-%d").date()
        duration = 365
    #handle unknown dates
    else:
        myask_log.error(" unknown date format '" + date_str +"'")
        start_date = date.today() 
        duration = CONST_UNDEF_DURATION
    return (start_date, duration)



def this_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead < 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)

def weekday_nextweek(d, weekday):
    next_week_start = next_weekday(d, 0)
    return next_week_start + timedelta(weekday)

def get_startofmonth(month):
    # returns the 1st day of the specified month. If the month has already passe, use next year
    today =  date.today()
    if today.month <= month:
        year = today.year
    else:
        year = today.year +1
    return date(year, month, 1)
   
def readMyRelativeDate(date_canon):
    today =  date.today()
    # translates a canonicalized relative date into a date + duration information
    if(date_canon =="?"):
        myask_log.warning("undefined relative date canonical '?'. Using current date")
        start_date = today
        duration = CONST_UNDEF_DURATION
    elif  (date_canon =="TODAY"):
        start_date = today
        duration = 1       
    elif(date_canon =="TOMORROW"):
        start_date = today + timedelta(1)
        duration = 1       
    elif(date_canon =="DAY_AFTER_TOMORROW"):
        start_date = today+ timedelta(2)
        duration = 1       
    elif(date_canon =="THIS_WEEK"):
        # define this week as today + <= 7days
        start_date = today
        duration = 7       
    elif(date_canon =="NEXT_WEEK"):
        # return next sunday +- 1 week later
        start_date = this_weekday(today, 0)
        duration = 7               
    elif(date_canon =="WEEK_AFTER_NEXT"):
        # return next sunday+7 +- 1 week later
        start_date = this_weekday(today+timedelta(7), 0)
        duration = 7               
    elif(date_canon =="MONDAY"):
        start_date = this_weekday(today, 0)
        duration = 1               
    elif(date_canon =="TUESDAY"):
        start_date = this_weekday(today, 1)
        duration = 1               
    elif(date_canon =="WEDNESDAY"):
        start_date = this_weekday(today, 2)
        duration = 1               
    elif(date_canon =="THURSDAY"):
        start_date = this_weekday(today, 3)
        duration = 1               
    elif(date_canon =="FRIDAY"):
        start_date = this_weekday(today, 4)
        duration = 1               
    elif(date_canon =="SATURDAY"):
        start_date = this_weekday(today, 5)
        duration = 1               
    elif(date_canon =="SUNDAY"):
        start_date = this_weekday(today, 6)
        duration = 1               
    elif(date_canon =="NEXT_MONDAY"):
        start_date = next_weekday(today, 0)
        duration = 1               
    elif(date_canon =="NEXT_TUESDAY"):
        start_date = next_weekday(today, 1)
        duration = 1               
    elif(date_canon =="NEXT_WEDNESDAY"):
        start_date = next_weekday(today, 2)
        duration = 1               
    elif(date_canon =="NEXT_THURSDAY"):
        start_date = next_weekday(today, 3)
        duration = 1               
    elif(date_canon =="NEXT_FRIDAY"):
        start_date = next_weekday(today, 4)
        duration = 1               
    elif(date_canon =="NEXT_SATURDAY"):
        start_date = next_weekday(today, 5)
        duration = 1               
    elif(date_canon =="NEXT_SUNDAY"):
        start_date = next_weekday(today, 6)
        duration = 1               
    elif(date_canon =="MONDAY_NEXTWEEK"):
        start_date = weekday_nextweek(today, 0)
        duration = 1               
    elif(date_canon =="TUESDAY_NEXTWEEK"):
        start_date = weekday_nextweek(today, 1)
        duration = 1               
    elif(date_canon =="WEDNESDAY_NEXTWEEK"):
        start_date = weekday_nextweek(today, 2)
        duration = 1               
    elif(date_canon =="THURSDAY_NEXTWEEK"):
        start_date = weekday_nextweek(today, 3)
        duration = 1               
    elif(date_canon =="FRIDAY_NEXTWEEK"):
        start_date = weekday_nextweek(today, 4)
        duration = 1               
    elif(date_canon =="SATURDAY_NEXTWEEK"):
        start_date = weekday_nextweek(today, 5)
        duration = 1               
    elif(date_canon =="SUNDAY_NEXTWEEK"):
        start_date = weekday_nextweek(today, 6)
        duration = 1               
    elif(date_canon =="MONTH_JAN"):
        start_date = get_startofmonth(1)
        duration = 31               
    elif(date_canon =="MONTH_FEB"):
        start_date = get_startofmonth(2)
        duration = 29               
    elif(date_canon =="MONTH_MAR"):
        start_date = get_startofmonth(3)
        duration = 31               
    elif(date_canon =="MONTH_APR"):
        start_date = get_startofmonth(4)
        duration = 30               
    elif(date_canon =="MONTH_MAY"):
        start_date = get_startofmonth(5)
        duration = 31               
    elif(date_canon =="MONTH_JUN"):
        start_date = get_startofmonth(6)
        duration = 30               
    elif(date_canon =="MONTH_JUL"):
        start_date = get_startofmonth(7)
        duration = 31               
    elif(date_canon =="MONTH_AUG"):
        start_date = get_startofmonth(8)
        duration = 31               
    elif(date_canon =="MONTH_SEP"):
        start_date = get_startofmonth(9)
        duration = 30               
    elif(date_canon =="MONTH_OCT"):
        start_date = get_startofmonth(10)
        duration = 31               
    elif(date_canon =="MONTH_NOV"):
        start_date = get_startofmonth(11)
        duration = 30              
    elif(date_canon =="MONTH_DEC"):
        start_date = get_startofmonth(12)
        duration = 31               
    else:
        myask_log.error("invalid relative date canonical '"+date_canon+"'")
        start_date = date.today() 
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
                    slots[sessionslot] = time.strptime(tmp_str, "DATE:%Y-%m-%d").date()
                else: slots[sessionslot] = session_attributes[sessionslot]
        else:
            myask_log.error("SESSION_ATTRIBUTES: ERROR NO ATTRIBUTES FOUND \n"+ str(session) +"\nEND_SESSION_ATTRIBUTES")

    if 'slots' in intent:        
        for inputslot in intent['slots']:
            if 'value' not in intent['slots'][inputslot]:
                continue
            if appdef.isApplicationSlot(inputslot):
                literal = intent['slots'][inputslot]['value']
                if appdef.getSlottype(inputslot) == "MY_RELATIVE_DATE": 
                    canonical_date = appdef.GetSlotCanonical(inputslot,literal, strict=True)              
                    (slots[inputslot],slots[inputslot+'.duration']) = readMyRelativeDate(canonical_date)
                    slots[inputslot+'.literal'] = literal
                elif appdef.getSlottype(inputslot) == "AMAZON.DATE":                
                    (slots[inputslot],slots[inputslot+'.duration']) = readAmazonDate(literal)
                    slots[inputslot+'.literal'] = literal
                elif appdef.getSlottype(inputslot) == "AMAZON.NUMBER":
                    slots[inputslot] = literal
                else:
                    slots[inputslot] = appdef.GetSlotCanonical(inputslot,literal, strict=True)
                    slots[inputslot+".literal"] = literal
    else:
        myask_log.debug(2, "No slots section found")
    myask_log.debug(5, "SLOTS: "+ str(slots))    
    return slots

def main():
    myask_log.error("This module does not offer command line functionality")
if __name__ == "__main__":
    main()    
