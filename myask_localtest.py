# coding: utf-8
################################################################################
#
# myask_localtest : functions test an aw lambda function on windows
#
################################################################################

import json
import csv
import myask_log
# import myask_appdef


g_total_count = 0
g_passed_count = 0
g_failed_count = 0
g_total_with_errors = 0
g_total_with_warnings = 0
g_total_ok = 0
g_correct_final_states = 0
g_incorrect_final_states = 0

def inittest():
    global g_total_count
    global g_passed_count
    global g_failed_count
    global g_total_with_errors
    global g_total_with_warnings
    global g_total_ok
    global g_correct_final_states
    global g_incorrect_final_states
    g_total_count = 0
    g_passed_count = 0
    g_failed_count = 0
    g_total_with_errors = 0
    g_total_with_warnings = 0
    g_total_ok = 0
    g_correct_final_states = 0
    g_incorrect_final_states = 0

def printTestStatistics():
    global g_total_count
    global g_passed_count
    global g_failed_count
    global g_total_with_errors
    global g_total_with_warnings
    global g_total_ok
    global g_correct_final_states
    global g_incorrect_final_states
    
    print ("================================")
    print ("Summary:")
    print ("Total tests:    " + str(g_total_count))
    print ("Passed:         " + str(g_passed_count))
    print ("  with errors:    " + str(g_total_with_errors))
    print ("  with warnings:  "  + str(g_total_with_warnings))
    print ("  no issues:      "  + str(g_total_ok))
    print ("Failed:         " + str(g_failed_count))
    print ("Correct end state: " + str(g_correct_final_states))
    print ("Wrong end state:   " + str(g_incorrect_final_states))
    
    print ("================================")
    
def batchtest(batchfile, testdir, intentfilter, handlerfunction):    
    #--------------------------------------------------------------------------
    # run a number of test utterances listed in 'filename'
    # PARAMETERS:
    # 'batchfile' : csv file listing 
    #                - intent  (for filtering)
    #                - user input (for debug output
    #                - jsonfile (NLU output from Alexa
    # 'testdir' : basedir where all jsonfiles are located
    # 'intentfilter' list of intents to be tested. [] for all intents
    # 'handlerrfunction' (pointer to) lambda handler function
    #--------------------------------------------------------------------------    
    inittest()
    with open(batchfile, 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        first = True
        for row in spamreader:
            if (first): # skip header
                first= False
                continue
            if row[0] == "END": break;
            test_intent= row[0]
            user_input = row[1]
            jsonfile = row[2]
            if len(row) > 3: 
                    expected_state = row[3]
            else: expected_state =""
            
            
            if test_intent == "":
                continue
            elif (len(intentfilter) == 0 or intentfilter[0] == '*'  or test_intent in intentfilter):
                myask_log.ResetErrorCounters()
                print ("---Testing intent '"+ test_intent +"'")
                print (">>>>> "+ user_input)
                filename = testdir + jsonfile
                input_event = ReadInputJSON(filename)
                TestEvent(input_event, handlerfunction, expected_state)
    printTestStatistics()
    
    
def randomtest(num_tests, intentfilter, appdef, handlerfunction):
    #--------------------------------------------------------------------------
    # creates random Alexa NLU output and runs them through the system
    # PARAMETERS:
    # 'num_tests': number of test events to generate and test
    # 'intentfilter' list of intents to be tested. [] for all intents
    # 'appdef'   : application definition class object 
    #              (intent/slot definitions from which test cases are created)
    # 'handlerrfunction' (pointer to) lambda handler function
    #--------------------------------------------------------------------------    
    inittest()
    
    for i in range(num_tests):
        myask_log.ResetErrorCounters()        
        sessionresult = appdef.getRandomResponse(intentfilter)
        event = CreateSessionData(sessionresult, appdef.GetAppID())
        print("Random session" + str(i) +":"+str(event))
        TestEvent(event, handlerfunction)

    printTestStatistics()
    

def ReadInputJSON(filename):
    jsonfile = open(filename, 'r')
    event = json.load(jsonfile)

    return event


def TestEvent(event, handlerfunction, expected_result_state=""):
    #--------------------------------------------------------------------------
    # tests a single input event (JSON structure) using the handler function
    # 'event': input event (output of Alexa NLU)
    # 'handlerfunction' pointer to lambda handler function
    #
    # The function calls the lambda event handler 'handlerfunction' with
    # the specified input 'event' and analyzes the output
    # The function updates the global variables
    # - g_total_count
    # - g_passed_count
    # - g_failed_count
    # - g_total_with_errors
    # - g_total_with_warnings
    # - g_total_ok
    #--------------------------------------------------------------------------
    
    global g_total_count
    global g_passed_count
    global g_failed_count
    global g_total_with_errors
    global g_total_with_warnings
    global g_total_ok
    global g_correct_final_states
    global g_incorrect_final_states
    
    context = {}
    g_total_count += 1

    returnjson = handlerfunction(event, context, True)
    
    myask_log.debug(1, "RESULT: " +str(returnjson))
    speech_output="ERROR"
    if 'response' in returnjson and 'outputSpeech' in returnjson['response']: 
        if 'type' in  returnjson['response']['outputSpeech']:                                            
            if  returnjson['response']['outputSpeech']['type'] == "SSML" and 'ssml' in returnjson['response']['outputSpeech']: 
                speech_output = returnjson['response']['outputSpeech']['ssml']
            elif returnjson['response']['outputSpeech']['type'] == "PlainText" and 'text' in returnjson['response']['outputSpeech']: 
                speech_output = returnjson['response']['outputSpeech']['text']
        
        print("<<<<< " + speech_output)
        print("------\n" + returnjson['response']['card']['content'] +"\n-----")
        g_passed_count += 1
        final_state = myask_log.GetDialogState()
        if(expected_result_state != ""):
            if final_state == expected_result_state:   
                print("Final State: "+final_state+ "--> OK")
                g_correct_final_states += 1
            else:  
                print("Final State: '"+final_state+ "'--> ERROR (expected '"+expected_result_state+"')")
                g_incorrect_final_states += 1
        else:
            print("Final State: "+final_state+ "  (no expected state given)")
        [errors, warnings] = myask_log.GetErrorCounters()
        if errors > 0: g_total_with_errors +=1
        elif warnings > 0: g_total_with_warnings +=1      
        else: g_total_ok +=1              

    else:
        print("!!!ERROR")
        g_failed_count += 1

    
    
def CreateSessionData(intent, app_id):
    result = {}
    result["session"] = {
            "sessionId": "SessionId.dc0a5c5b-2ba8-407b-9187-55e76ffb2bf7",
            "application": {
                    "applicationId": app_id
            },
            "attributes": {},
            "user": {
                "userId": "amzn1.ask.account.AEFJ2G32AUAOAU4XHZMYRF2YO7IN5RZ6LNDZCKOT3MBMJAIJF4MJGED3764LVY4477AK3MRRUSGHEBLWNFRBAUAGYADOGKNPM4Z4U5LOJIGRBKUKITLDXNHOL33SOAXG2LT3NUBIGDOVFLSDMYQ7IHFZGDOXOCZO465MV65CMBSZIWRUQZJWA7HNA73KPVYMIIS7MS6IPUPGYMQ"
            },
            "new": True
        }
    result["request"] = {
            "type": "IntentRequest",
            "requestId": "EdwRequestId.b69d72af-83e7-4c40-b9a7-1cc23f33e5b8",
            "locale": "de-DE",
            "timestamp": "2017-02-05T23:07:34Z",
        }
    result["request"]["intent"] =  intent
    result["version"] = "1.0"

    return result
