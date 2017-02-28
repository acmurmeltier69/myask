# coding: utf-8
################################################################################
#
# myask_utterancegen : functions to generate sample utterances from a grammar
#
#-------------------------------------------------------------------------------
# https://github.com/acmurmeltier69/myask
# Written 2017 by acmurmeltier69 (acmurmeltier69@mnbvcx.eu)
# Shared under GNU GENERAL PUBLIC LICENSE Version 3
# https://github.com/acmurmeltier69/myask
#-------------------------------------------------------------------------------
################################################################################

import sys
import argparse
import codecs
import re
from idlelib.idle_test.test_io import PseudeOutputFilesTest
import myask_log

    

def AddNonterminalRule(nonterminal, ntrule, non_terminal_list):
    myask_log.debug(5, "adding non-terminal '"+nonterminal+"' Rule: '"+ntrule+"'")
    nt_elements =  ntrule.split("|")
    for counter in range(len(nt_elements)):
        nt_elements[counter] = nt_elements[counter].strip(" ")
        
    if nonterminal in non_terminal_list: non_terminal_list[nonterminal].append(nt_elements) 
    else:     non_terminal_list[nonterminal] = nt_elements
    return True  

def AddIntentRule(intent, rule, input_utterances):
    if intent in input_utterances: input_utterances[intent].append(rule)   
    else:   input_utterances[intent] = [rule] 
    return True  


def PrintNonTerminals(non_terminal_list):
    myask_log.debug(5, "non-terminals:")
    for nt in non_terminal_list:
        myask_log.debug(5, "'"+nt+"' =")
        for alternative in non_terminal_list[nt]:
            myask_log.debug(5, "    '"+alternative+"'")

def AppendWord(old_list, word):
    # appends word 'word' to all eleements in 'old_list' 
    # returns a modified copy of the list
    newlist = []
    for alternative in old_list:
        if alternative != "" and alternative[len(alternative)-1] != " " : alternative += " "
        alternative += word
        newlist.append(alternative)                    
    return newlist

def AppendNT(old_list, nonterminal, non_terminal_list):
    new_alternatives = []
    if nonterminal in non_terminal_list:
        ntalternatives = non_terminal_list[nonterminal]
        for ntword in ntalternatives:
            new_alternatives.extend(AppendWord(old_list, ntword))
    else:
        print("      unknown nt found: '"+nonterminal+"'")
        new_alternatives.extend(AppendWord(old_list, nonterminal))                  
    return new_alternatives

def  AppendOption(old_list, optiontext, non_terminal_list):   
    # alternative without new world
    new_alternatives = old_list
    # alternative with new world
    if re.match("^<\S+>$", optiontext): # nt-found
        new_alternatives.extend(AppendNT(old_list, optiontext, non_terminal_list))
    else:
        new_alternatives.extend(AppendWord(old_list, optiontext))         
    return new_alternatives

def ProcessLine(input_sentence, non_terminal_list):
    current_alternatives = [""]
    in_option = False
    optionstr = ""
    for input_element in input_sentence:
        if(in_option):
            if re.match("(\S+)\]$", input_element): # end of option found
                match = re.match("(\S+)\]$", input_element)
                word = match.group(1)
                optionstr +=" "+word
                current_alternatives = AppendOption(current_alternatives, optionstr, non_terminal_list)
                in_option = False
            else:
                optionstr +=" "+input_element            
        else:
            if re.match("^<\S+>$", input_element): # nt-found
                current_alternatives = AppendNT(current_alternatives, input_element, non_terminal_list)
            elif re.match("^\[\S+\]$", input_element):
                match = re.match("^\[(\S+)\]$", input_element)
                optional_text = match.group(1)
                current_alternatives = AppendOption(current_alternatives, optional_text, non_terminal_list)
            elif re.match("^\[\S+$", input_element):
                match = re.match("^\[(\S+)$", input_element)
                optionstr = match.group(1)
                in_option = True
            else: # regular word found. just add to all alternatives
                current_alternatives = AppendWord(current_alternatives, input_element)
 
    
    return current_alternatives

    
def StripComments(line):
    line = line.strip()
    line = line.split('#', 1)[0]
    line = line.rstrip()

    return line               
      
def createSampleUtterancesFromGrammar(inputfile):
    #---------------------------------------------------------------------------
    # reads a generation grammar from 'iputfile' and returns 
    # an array of sample utterances created from that grammar
    #---------------------------------------------------------------------------
    input_utterances = {}
    non_terminal_list = {}
#    fin = codecs.open(inputfile, "r", "utf-8")
    fin = open(inputfile, "r")
    content = fin.readlines()
    
    # --------------------------------------------------------------------------
    # 1st step: parse input file
    # parse the input file and create
    # a dictionary of non-terminals (non_terminal_list)
    # a list of input utterances (input_utterances)
    # --------------------------------------------------------------------------
    
    linecount = 0
    myask_log.debug(3, "---->>>Parsing input file"+inputfile)
    for line in content:
        linecount +=1
        line = StripComments(line)

        if  re.match("^\s*$",line):
            continue
        
        blocks = re.match("^\s*(.*)\s*::=\s*(.*)$", line)
        if blocks: 
            leftside = blocks.group(1)
            leftside = leftside.strip()
            rightside = blocks.group(2)
            rightside = rightside.strip()
        else:
            myask_log.error("Invalid Syntax in line '"+line+"'")
            return ()
        
        if re.match("<.*>", leftside): # non terminal rule found
            myask_log.debug(7, "NON-TERMINAL '"+leftside+"' found in line "+str(linecount))
            AddNonterminalRule(leftside, rightside, non_terminal_list)
        else: 
            AddIntentRule(leftside, rightside,input_utterances)

    myask_log.debug(3, "---->>>Parsing done. "+ str(linecount)+" lines read")
    fin.close()


    # --------------------------------------------------------------------------
    # 1nd step: create all possible output sentence
    # loop over all input utterances
    # For each inout utterance, create variants for all possible (combinations of)
    # non-terminal symbols and optional phrases
    # --------------------------------------------------------------------------
    training_corpus = {}
    linecount = 0
    for intent in input_utterances:
        training_corpus[intent] = []
        for input_sentence in input_utterances[intent]:
            linecount +=1
            myask_log.debug(3, "Processing line ("+intent+") '"+str(input_sentence)+"'")
            input_words = input_sentence.split(" ")
            line_alternatives = ProcessLine(input_words, non_terminal_list)
            for training_sentence in line_alternatives:
                myask_log.debug(5, "-> "+training_sentence)
            training_corpus[intent].extend(line_alternatives)
     
     
    return training_corpus

################################################################################
# function for command line usage
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
def main():
    outputfile =""
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", type=int,
                        help="define output verbosity")

    parser.add_argument("-out", "--outputfile", type=str, 
                        help="Use local database on the given port on localhost")
    parser.add_argument("inputfile", help="grammar file as input")

    args = parser.parse_args()    
    
    if args.verbosity:
        myask_log.SetDebugLevel(args.verbosity)

    if  args.inputfile: inputfile = args.inputfile
    else: inputfile = "input"

    if args.outputfile: outputfile = args.outputfile
    else: outputfile = ""

    myask_log.debug(3, "input: "+inputfile)
    myask_log.debug(3, "output: "+outputfile)
  
    corpus = createSampleUtterancesFromGrammar(inputfile)    
        
    if outputfile == "":
        for intent in corpus:
            intent_sentences = corpus[intent] 
            for i in range(len(intent_sentences)):
                line = intent +" "+ intent_sentences[i]
                print line
    else:
        fout = open(outputfile, 'w+')
        for intent in corpus:
            intent_sentences = corpus[intent] 
            for i in range(len(intent_sentences)):
                line = intent +" "+ intent_sentences[i]
                fout.write(line+"\n")
        fout.close()


    
if __name__ == "__main__":
    main()