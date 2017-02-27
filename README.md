# myask
myask: My Alexa Skills Kit (ASK)  helper library

(C) 2017 by "acmurmeltier69"

This library contains a set of functions and classes I found helpfule when creating my own Alexa Skills
 h2. Modules in the package
  - *myask_appdef*    : a class to manage the application data structure of the skill
                     The application structure is is loaded from a separate file and is used to 
                     1) create the "Interaction Model" for Alexa 
                         - definition of intent structure
                         - definition of custom slot types
                     2) read, write and validate slots (using "myask_slots")
                     3) generate random Alexa output structures for testing the handler (using myask_localtest)
                                         
 - *myask_slots*     : functions to read, normalize (i.e. convert to canonical) and write slot and session attributes
 - *myask_alexaout*  : functions to create output structure for Alexa
 - *myask_log*       : functions for logging (debug, print, error) and error counting
 - *myask_dynamodb*  : a class and functions for storing user profile info in aws dynamodb
 - *myask_utterancegen* : tool to generate a large number of input samples for an Alexa skill from a compact generation grammar
 - *myask_localtest* : functions test an aw lambda function on windows

 h2. Application Data Structure
 The core of myask functions is a data structure that describes the application data (intents, slots, values)
 Thee data structure consists of
  - an application name (used in the title of output cards)
  - an ASK application ID (used to verify the application in the handler)
  
  - a list of intents with a list of slots for each intent
  - the definition of the slot type for each slot
  - the definition of custom slot types
  -- For each custom slottype, the application definition provides a set of standardized values (canonicals)
 -- for each canonical value, the application definition provides a set of spoken words (literals) that can be used to express this value

Example:
`                          
                    Example: 
                    
 
APPNAME = "SAMPLE"
APPID   = "amzn1.ask.skill.aaaaaaaa-bbbb-cccc-dddd-1234567890ab"
INTENTS = {
            "TellColor":    ["Color"],
            "MixColors":    ["MixColor1", "MixColor2"],
            "Confirm":      ["YesNo"]
            "AMAZON.HelpIntent"  : []
           }

SLOTS = {
            "Color" :     "LIST_OF_COLORS",
            "MixColor1" : "LIST_OF_COLORS",
            "MixColor2" : "LIST_OF_COLORS",
            "YesNo"     : "MY_YES_NO"
         }

SLOTTYPES = {
            "LIST_OF_COLORS":[
                ["RED", ["red", "fire red"]],
                ["GREEN", ["green"]]
                ["YELLOW", ["yellow"]]
                ["BLUE", ["blue"]]
                
            ],
            "YES_NO_TYPE" :[ 
                ["YES_CANONICAL",   ["yes", "yep", "of course"]],
                ["NO_CANONICAL",    ["no", "nope", "no way"]] 
            ]
   }
`