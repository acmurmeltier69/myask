# myask
myask: My Alexa Skills Kit (ASK)  helper library

(C) 2017 by "acmurmeltier69"

This library contains a set of functions and classes I found helpfule when creating my own Alexa Skills

## Modules in the package
#### myask_appdef.py 
a class to manage the application data structure of the skill.

The application structure is is loaded from a separate file and is used to 
 1) create the "Interaction Model" for Alexa 
  - definition of intent structure
  - definition of custom slot types
 2) read, write and validate slots (using "myask_slots")
 3) generate random Alexa output structures for testing the handler (using myask_localtest)
 Note: 
  - for each custom slottype, the application definition provides a set of standardized values (canonicals)
  - for each canonical value, the application definition provides a set of spoken words (literals) that can be used to express this value
  - I have deliberately decided to specify the application data as global variables in an importet python file rather than reading it from JSON file to
     - speed-up reading of data structure at run-time when handler function is invoked
     - avoid parsing error at run time
     - easily allow import of external data structures (e.g. long list of station names stored in a different file)

See *Application Data Structure* below

This module can also be called on the command line: myask_appdef [-out ROOTFILE] appdef
Call with '--help' for syntax
                                         
#### myask_slots.py     
Helper functions to read, normalize (i.e. convert to canonical) and write slot and session attributes

#### myask_alexaout.py  
Functions to create output structure for Alexa

#### myask_log.py
Functions for logging (debug, print, error) and error counting

#### myask_dynamodb.py
A class and functions for storing user profile info in aws dynamodb

This tool can be called on the commandline to
- create new db tables
- scan all user profiles and access statistics in a db table
- print a specific user profile
- print access statistics for a specific user
- add a new user profile
- delete a user profile

Call with '--help' for syntax

#### myask_utterancegen.py
Tool to generate a large number of input samples for an Alexa skill from a compact generation grammar
This tool can be called from the commandline

Call with '--help' for syntax

#### myask_localtest
Functions test an aw lambda function on windows
Can currently not be called from the commandline (maybe later)

## Application Data Structure
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
```                          
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
```