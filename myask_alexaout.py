# coding: utf-8
################################################################################
#
# myask_alexaout : functions to create output structure for ask
#
################################################################################

import myask_log
from sre_compile import isstring

def createAlexaErrorOutput(error_msg, slots):
    out = alexaout()
    out.speech_output = error_msg
    out.card_text = error_msg

    return out.createOutput()

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
        self.card_text = self.speech_output
        
    def createOutput(self, slots, session_attributes={}):
        if myask_log.GetDebugLevel()> 3:
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
        output = "\n-----Slots----\n"
        for slotname in slots:
            if slotname.endswith(".literal"):
                continue
        
            litname = slotname +".literal"
            if litname in slots:
                output += u'   {:s}={:s}({:s})'.format(slotname, slots[slotname].decode("unicode-escape"), slots[litname].decode("unicode-escape"))
            else:
                slotval = slots[slotname]
                if isstring(slotval): 
                    slotval = unicode(slotval.decode("unicode-escape"))
                else: slotval = str(slotval)
                output += u'   {:s}={:s}'.format(slotname, slotval)
            output += " "
            output += "\n"
        output += "-------------\n"
        return output    
    