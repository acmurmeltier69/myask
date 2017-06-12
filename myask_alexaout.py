# coding: utf-8
################################################################################
#
# myask_alexaout : functions to create output structure for ask
#
#-------------------------------------------------------------------------------
# https://github.com/acmurmeltier69/myask
# Written 2017 by acmurmeltier69 (acmurmeltier69@mnbvcx.eu)
# Shared under GNU GENERAL PUBLIC LICENSE Version 3
# https://github.com/acmurmeltier69/myask
#-------------------------------------------------------------------------------
#
################################################################################

import myask_log
import re
from sre_compile import isstring
from datetime import date

def createAlexaErrorOutput(error_msg, slots):
    out = alexaout()
    out.speech_output = error_msg
    out.card_text = error_msg

    return out.createOutput(slots)

class alexaout:
    #----------------------------------------------------------------------
    # Creates properly formated output JSON structure from parameters
    # 'card_title' Headline for the app display
    # 'card_text'  Text to be displayed on the app display
    # 'ssml' TTS output text, including SSML tags (<speak>, </speak> are added)
    # 'reprompt_text': text for repeated prompt
    # 'should_end_session' if False, Alexa is instructed to continue the session
    # 'session_attributes' key-value pairs to be returned in next utterance
    # 'slots' current set of slots (output if debuglevel >3)
    #----------------------------------------------------------------------
    def __init__(self):
        self.session_attributes = {}
        self.slots = []
        self.should_end_session = True
        self.card_title = ""
        self.speech_output = ""
        self.reprompt_text = ""
        self.card_text = "" 
    
    def DisplaySpeechOutputOnCard(self):
        ssmltext = self.speech_output
        self.card_text = ssmltext
        self.card_text = re.sub('<break[^/]*/>','\n', self.card_text) 
        self.card_text = self.card_text.replace('<p>','') 
        self.card_text = self.card_text.replace('</p>','\n') 
        self.card_text = self.card_text.replace('</say-as>','') 
        self.card_text = re.sub(r'<say-as[^>]*>','', self.card_text) 
        
    def createOutput(self, slots, session_attributes={}):
        if(self.card_text == ""):
            self.DisplaySpeechOutputOnCard()
        if myask_log.show_debugslots == True:
            self.card_text = self.printcardslots(slots) + "\n" + self.card_text
    
        speechlet_response = self.build_speechlet_response()
        return self.build_response(session_attributes, speechlet_response)

    def build_speechlet_response(self):
        speech_output = "<speak>"+self.speech_output+"</speak>"
        return {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': speech_output
            },
            'card': {
                'type': 'Simple',
                'title':  self.card_title,
                'content': self.card_text
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': self.reprompt_text
                }
            },
            'shouldEndSession': self.should_end_session
            }
        


    def build_response(self, session_attributes, speechlet_response):
        return {
            'version': '1.0',
            'sessionAttributes': session_attributes,
            'response': speechlet_response
        }


    def printcardslots(self, slots):
        #---------------------------------------------------------------------------
        # prints the content of the slots data structure to the output cars
        # debugging purposes
        # PARAMETERS: slots
        # RETURN: String with slot info
        #---------------------------------------------------------------------------
        output = u"\n-----Slots----\n"
        for slotname in slots:
            if slotname.endswith(".literal"):
                continue
        
            litname = slotname +".literal"
            if isinstance(slots[slotname], date):
                output += u" '"+slotname+u"'='"+slots[slotname].strftime('%Y-%m-%d')
                if litname in slots: output +=  u"'("+unicode(slots[litname])+u")"
            elif litname in slots:
                output += u" '"+slotname+u"'='"+slots[slotname]+u"'("+unicode(slots[litname])+u")"
            else:
                slotval = slots[slotname]
                if not isstring(slotval): 
                    slotval = str(slotval)
                output += u" '"+slotname+u"'='"+slotval+u"'"
            output += u" "
            output += u"\n"
        output += u"-------------\n"
        return output    

def main():
    myask_log.error("This module does not offer command line functionality")
if __name__ == "__main__":
    main()    