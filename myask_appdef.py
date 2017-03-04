# coding: utf-8
################################################################################
# 
# myask_appdef : A class to work with the intents and slot types of the application
#
#-------------------------------------------------------------------------------
# https://github.com/acmurmeltier69/myask
# Written 2017 by acmurmeltier69 (acmurmeltier69@mnbvcx.eu)
# Shared under GNU GENERAL PUBLIC LICENSE Version 3
# https://github.com/acmurmeltier69/myask
#-------------------------------------------------------------------------------
# 
# The application structure is is loaded from a separate file and is used to 
#   1) create the "Interaction Model" for Alexa 
#       - definition of intent structure
#       - definition of custom slot types
#   2) read, write and validate slots (using "myask_slots")
#  Note: 
#       - for each custom slottype, the application definition provides a set of standardized values (canonicals)
#       - for each canonical value, the application definition provides a set of spoken words (literals) that can be used to express this value
#                          
#   Example: 
#        "YES_NO_TYPE" :[ ["YES_CANONICAL",   ["yes", "yep", "of course"]],
#                         ["NO_CANONICAL",    ["no", "nope", "no way"]] ]
################################################################################

import argparse

import random
from datetime import datetime
import myask_log

class applicationdef:
    def __init__(self, applicationname, applicationid, intentdef, slotdefinitions, slottypedefs, pronlex={}):
        self._intentdef = intentdef 
        self._applicationname = applicationname
        self._applicationid = applicationid
        self._slotdefinitions = slotdefinitions
        self._slottypedefs = slottypedefs
        self._pronlex = pronlex 
        self._slotnames = []
        for slotname in self._slotdefinitions:
            self._slotnames.append(slotname)


    def _get_slot_value_map(self, slotname):
        #-----------------------------------------------------------------------      
        # Private  member function of class applicationslots
        # Parameters
        #  - slotname (string): name of a slot to be checked
        # Returns: (dict) a map with all the canonical/literal values for a slot
        #        - the key is the canonical
        #        - the values are all possible literals
        #        - the first value is the generic output entry
        #-----------------------------------------------------------------------
        if slotname not in self._slotdefinitions:
            myask_log.error("_get_slot_value_map: unknown slotname '"+ slotname + "'")
            return []
        slottype =  self._slotdefinitions[slotname]

        if slottype not in self._slottypedefs:
            if slottype == "AMAZON.NUMBER":
                return ["AMAZON.NUMBER"]
            elif slottype == "AMAZON.DE_REGION":
                return ["AMAZON.DE_REGION"]
            elif slottype == "AMAZON.DATE":
                return ["AMAZON.DATE"]
            else:
                myask_log.error("_get_slot_value_map: unknown slottype '" + slottype + "' found for slot '"+ slotname + "'")
                return []
        
        return self._slottypedefs[slottype]    

    def GetAppID(self):
        return self._applicationid
    
    def CreateIntentDef(self):
        #---------------------------------------------------------------------------
        #
    
        intent_json = ""
        intent_json += "{\n"
        intent_json += "   \"intents\": ["
        firstintent = True
        for intent in self._intentdef:
            if firstintent: 
                firstintent = False
                intent_json +="\n"
            else:
                intent_json +=",\n"
            intent_json += "        {\n"
            intent_json += "         \"intent\": \""+ intent +"\""
            if intent not in ["AMAZON.HelpIntent", "AMAZON.StopIntent", "AMAZON.CancelIntent", "AMAZON.NoIntent", "AMAZON.YesIntent"]:
                intent_json += ",\n"
                intent_json += "         \"slots\": ["
                firstslot = True
                for slotname in self._intentdef[intent]:
                    if firstslot == True: 
                        firstslot = False
                        intent_json +="\n"
                    else:
                        intent_json +=",\n"
                    slottype = self.getSlottype(slotname) 
                    intent_json += "            {\n"
                    intent_json += "               \"name\": \""+ slotname+ "\",\n"
                    intent_json += "               \"type\": \""+ slottype+ "\"\n"
                    intent_json += "            }"
                intent_json += "\n"
                intent_json += "          ]\n"
            else:
                intent_json += "\n"
            intent_json += "        }"
        intent_json += "\n"
        intent_json += "    ]\n"
        intent_json += "}\n"

        return intent_json
        
    def getAllSlots(self):
        #-----------------------------------------------------------------------      
        #  Public member function of class applicationslots
        # Parameters : . 
        # Returns: (list of strings) list of all slotnames  defined in this app
        #-----------------------------------------------------------------------
        return self._slotnames
    
    def isApplicationSlot(self, slotname):
        #-----------------------------------------------------------------------      
        #  Public member function of class applicationslots
        # Parameters 
        #  - slotname (string): name of a slot to be checked
        # Returns: (Boolean). True if the slot is defined in this application
        #-----------------------------------------------------------------------
        return slotname  in self._slotdefinitions
        
    def getSlottype(self, slotname):
        #-----------------------------------------------------------------------      
        #  Public member function of class applicationslots
        # Parameters 
        #  - slotname (string): name of a slot to be checked
        # Returns: (string) Type of the slot or "" if not defined
        #-----------------------------------------------------------------------
        if slotname not in self._slotdefinitions:
            myask_log.error("getSlottype: unknown slotname '"+ slotname + "'")
            return ""
        return self._slotdefinitions[slotname]
                
                
    def isBuiltinType(self,slotname):
        #----------------------------------------------------------------------
        # returns True if the slot 'slotname' is of a built-in type
        # (starting with 'AMAZON'
        #----------------------------------------------------------------------
        
        if slotname not in self._slotdefinitions:
            myask_log.error("getSlottype: unknown slotname '"+ slotname + "'")
            return False
        return str(self._slotdefinitions[slotname]).startswith("AMAZON.")
        
    def GetSlotOutputName(self, slotname, canonical):
        #-----------------------------------------------------------------------      
        #  Public member function of class applicationslots
        # Parameters 
        #  - slotname (string): name of the slot
        #  - canonical (string): normalized internal identifier for a slot value
        # Returns: (string) generic (spekable) output name for the canonical value
        #              if the value cannot be mapped, return canonical
        #-----------------------------------------------------------------------
        slotmap = self._get_slot_value_map(slotname)
        if len(slotmap) == 0: 
            myask_log.error("GetSlotOuputName: No slotmap found for slot'"+ slotname + "' using canonical '"+canonical+"'")
            return canonical      
        elif len(slotmap) == 1 and slotmap[0].startswith("AMAZON"): 
            return canonical      
          
        for entry in slotmap:
            if len(entry) < 2: 
                myask_log.error("gen_GetOuputName: incorrect format for dictionary entry '"+str(entry)+"'")
                return "ERROR"
            if entry[0] == str(canonical): # we got a match
                return entry[1][0]
     
        # if we are here, we did not find a match
        myask_log.warning("GetOuputName: No match found for'" + str(canonical)+"'")    
        return canonical
        
    def GetSpokenSlotOutputName(self, slotname, canonical):
        #-----------------------------------------------------------------------      
        #  Public member function of class applicationslots
        # Parameters 
        #  - slotname (string): name of the slot
        #  - canonical (string): normalized internal identifier for a slot value
        # Returns: (string) generic (spekable) output name for the canonical value
        #              if the value cannot be mapped, return canonical
        #               Check the exception lexicon for specific output formats
        #-----------------------------------------------------------------------
        text = self.GetSlotOutputName(slotname, canonical)
        
        if text in self._pronlex:
            return self._pronlex[text]
        else:
            return text
   

    def GetSlotCanonical(self, slotname, literal, strict=False):
        #-----------------------------------------------------------------------      
        #  Public member function of class applicationslots
        # Parameters 
        #  - slotname (string): name of the slot
        #  - literal (string):slot value as spoken by the user 
        #  - strict If True, '?' is returned if no match was found
        # Returns: (string) canonical, i.e. normalized internal identifier for a slot value
        #              if the value cannot be mapped, and strict is False, return literal
        #-----------------------------------------------------------------------
        slotmap = self._get_slot_value_map(slotname)
        if len(slotmap) == 0: 
            myask_log.error("GetSlotCanonical: no slotmap found for slot'"+ slotname + "'")
            return literal
        elif len(slotmap) == 1 and slotmap[0].startswith("AMAZON"):
            return literal
        
        #OK, let's look for the canonical value
        literal = literal.lower()
        literal.encode("utf-8")
        for entry in slotmap:
            if len(entry) < 2: 
                myask_log.error("gen_GetOuputName: incorrect format for dictionary entry '"+str(entry)+"'")
                return "?"
            for value in entry[1]:
                value.encode("utf-8")
                if value == literal:
                    return entry[0]
      
        myask_log.warning("GetSlotCanonical: No match found for'" + literal + "'")    
        if strict == True: return "?"
        else: return literal

    def GetAllSlotLiterals(self):
        #-----------------------------------------------------------------------      
        #  Public member function of class applicationslots
        # Parameters - 
        # Returns: list of slottypes and for each a list of all literals 
        # This function can be used to create the list for ASK custom types
        #-----------------------------------------------------------------------
        slotinfo = []
        for slottype in self._slottypedefs:
            # create a list of all literals for this type
            slot_literals = []
            values  = self._slottypedefs[slottype]
            for value in values:
                literals = value[1]
                for literal in literals:
                    slot_literals.append(literal)
            slotinfo.append((slottype,slot_literals))
        return (slotinfo)
    
    def getRandomResponse(self, intentlist):
        #-----------------------------------------------------------------------
        # returns a random input for one of the intents in the intent list
        # if the intentlist is emty any intent can be TestActionsReturned
        # the response consists of a data structure that represents the
        # 'intents' part of a Alexa resonse, e.g.
        #  "intent": {
        #               "name": "NextBus",
        #               "slots": {
        #                  "Destination": {
        #                     "name": "Destination",
        #                     "value": "elisenbrunnen"
        #                   },
        #                   "Buslinie": {
        #                      "name": "Buslinie"
        #                   },
        #               }
        #           }
        
        # select random slot
        resulstructure = {}
        if len(intentlist) == 0 or intentlist[0] == "*": # select from all slots
            intentname= random.choice(self._intentdef.keys())
        else: # select from the list
            intentname = random.choice(intentlist)
        myask_log.debug(5,"Intent: "+intentname)
        resulstructure["name"] = intentname
        if intentname not in self._intentdef:
            myask_log.error("Invalid random intent name '"+intentname+"'")
            return resulstructure
        
        slotlist = self._intentdef[intentname]
        slotstructure = {}
        #now loop over all slots forr this intent and decide if we assign a value and which one
        for slotname in slotlist:
            slotstructure[slotname] = {}
            slotstructure[slotname]['name'] = slotname
            # decide if we assign a value to this slot or not
            if random.choice([True, False]) == False: # no value for this slot
                # append it as empty value
                myask_log.debug(5,"Slot '"+slotname+"' does not get a value")
            else: # we want to get a random value for this slot
                # append it as em
                slottype = self.getSlottype(slotname)
                if str(slottype).startswith("AMAZON"):
                    # Amazon internal slot
                    if slottype == "AMAZON.NUMBER":
                        slotvalue = 47
                        literal = str(slotvalue)
                    elif slottype == "AMAZON.DATE":
                        slotvalue = datetime.today()
                        literal = slotvalue.strftime('%Y-%m-%d')
                    elif slottype == "AMAZON.DE_REGION":
                        literal = random.choice(["nrw","bayern"])
                    else:
                        myask_log.error("_getRandomRespons: Built-in type "+str(slottype)+" not yet handled")
                        literal ="UNKNOWN_AMAZON_TYPE"
                else: # custom type
                    if slottype not in self._slottypedefs:
                        myask_log.error("_getRandomRespons: no slot definition found for slot "+str(slottype))
                        literal ="UNKNOWN_USER_TYPE"
                    else:
                        slotvalue_list = self._slottypedefs[slottype]
                        slotvalue = random.choice(slotvalue_list)
                        # ok, we got the vlaue (literal,canonicals, let's pick a literal
                        literal_list = slotvalue[1]
                        literal = unicode(random.choice(literal_list))
                        
                slotstructure[slotname]['value'] = literal
                myask_log.debug(5, "Using value' "+literal+"' for slot '"+slotname+"'")
                
        resulstructure["slots"] = slotstructure
        return resulstructure
    
###############################################################################
#
# stand alone usage as command line tool
#
# parses application definition file and creates files fo ASK:
# intent structure --> ROOT+"_intentstruct_generated.js"
# custom slottypes  --> ROOT+"_customtypes_generated.txt"
###############################################################################
   
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", type=int,
                        help="define output verbosity")

    parser.add_argument("-out", "--outputfile_root", type=str, 
                        help="basename for output files")
    parser.add_argument("inputfile", help="grammar file as input")

    args = parser.parse_args()    
    
    if args.verbosity:
        myask_log.SetDebugLevel(args.verbosity)

    if  args.inputfile: inputfile = args.inputfile
    else: inputfile = "input.py" # dummy, we will never get here
    
    if inputfile.endswith('.py'):
        inputfile = inputfile[:-3]
    else:
        myask_log.error("application definition file muyst end with #.py'. Got "+inputfile+"'")
        return

    if args.outputfile_root: output_root = args.outputfile_root
    else: output_root = ""
        
    # now import the application definition from that file
    try:
        appdef_module = __import__(inputfile)
    except ImportError:
        # Display error message
        myask_log.error("Could not import appdef file '"+inputfile+"'")
    else:
        myask_log.debug(3, "Application definition importet from '"+inputfile+".py'")
   
        myask_log.debug(5, "Initializing application definition")

        appdef = applicationdef(appdef_module.APPNAME, 
                                appdef_module.APPID,
                                appdef_module.INTENTS, 
                                appdef_module.SLOTS, 
                                appdef_module.SLOTTYPES)
    
        myask_log.debug(5, "Creating ASK intent structure")
        intent_json = appdef.CreateIntentDef()
 
   
        if output_root == "":
            # print to standard outpt
            print("=======BEGIN INTENT DEF=====================================\n\n")
            print intent_json
            print("\n=======END INTENT DEF=====================================\n\n")
        else: 
            intentfile = output_root+"_intentstruct_generated.js"
            myask_log.debug(3, "Writing intent structure to file '"+intentfile+"'")
            intentout = open(intentfile, 'w+')
            intentout.write(intent_json)
            intentout.close()

        typeinfo = appdef.GetAllSlotLiterals()
        if output_root == "":
            # print to standard outpt
            print("=======BEGIN CUSTOM_TYPE DEFINITIONS========================\n\n")
            for (slottype, slotliterals) in typeinfo:
                print("\n--- "+slottype+" ---")
                for literal in slotliterals:
                    print literal
            print("\n=======END CUSTOM_TYPE DEFINITIONS========================\n\n")
        else: 
            typefile = output_root+"_customtypes_generated.txt"
            myask_log.debug(3, "Writing custom data type definitions to file '"+typefile+"'")
            typeout = open(typefile, 'w+')
            for (slottype, slotliterals) in typeinfo:
                typeout.write("\n--- "+slottype+" ---\n")
                for literal in slotliterals:
                    typeout.write(literal.encode('utf8')+"\n")
                    
            typeout.close()
            myask_log.debug(3, "Done")
if __name__ == "__main__":
    main()