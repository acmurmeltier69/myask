# coding: utf-8
################################################################################
#
# myask_speech : general-purpuse functions directly related to speech I/O
#
#-------------------------------------------------------------------------------
# https://github.com/acmurmeltier69/myask
# Written 2017 by acmurmeltier69 (acmurmeltier69@mnbvcx.eu)
# Shared under GNU GENERAL PUBLIC LICENSE Version 3
# https://github.com/acmurmeltier69/myask
#-------------------------------------------------------------------------------
################################################################################


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
Kölner Phonetik von
https://www.python-forum.de/viewtopic.php?t=17177
Dieses Modul stellt eine Implementation der 'Kölner Phonetik' dar.
https://de.wikipedia.org/wiki/K%C3%B6lner_Phonetik
"""

import re
import myask_log

RULETABLE = {re.compile(r".[A|E|I|J|O|U|Y|Ä|Ö|Ü].", re.I):     "0",
             re.compile(r".[B].", re.I):                       "1",
             re.compile(r".[P][^H]", re.I):                    "1",
             re.compile(r".[D|T][^C|S|Z]", re.I):              "2",
             re.compile(r".[F|V|W].", re.I):                   "3",
             re.compile(r"[P][H].", re.I):                     "3",
             re.compile(r".[G|K|Q].", re.I):                   "4",
             re.compile(r"[\b][C][A|H|K|L|O|Q]", re.I):        "4",
             re.compile(r"[^S|Z][C][A|H|K|O|Q|U|X]", re.I):    "4",
             re.compile(r"[^C|K|Q][X].", re.I):                "48",
             re.compile(r".[L].", re.I):                       "5",
             re.compile(r".[M|N].", re.I):                     "6",
             re.compile(r".[R].", re.I):                       "7",
             re.compile(r".[S|Z|ß].", re.I):                   "8",
             re.compile(r"[S|Z][C].", re.I):                   "8",
             re.compile(r"\b[C][^A|H|K|L|O|Q|R|U|X]", re.I):   "8",
             re.compile(r".[C][^A|H|K|O|Q|U|X]", re.I):        "8",
             re.compile(r".[D|T][C|S|Z]", re.I):               "8",
             re.compile(r"[C|K|Q][X].", re.I):                 "8"
            }

def encode_cgnph(inputstring):
    """
    encode(string) -> string
      Gibt den phonetischen Code des übergebenen Strings zurück.
    """

    encoded = ""
    for i in xrange(len(inputstring)):
        part = inputstring[i - 1:i + 2]
        if len(inputstring) == 1:
            part = " %s " % inputstring[0]
        elif i == 0:
            part = " %s" % inputstring[:2]
        elif i == len(inputstring) - 1:
            part = "%s " % inputstring[i - 1:]
        for rule, code in RULETABLE.iteritems():
            if rule.match(part):
                encoded += code
                break

    while [v for v in RULETABLE.itervalues() if encoded.find(v * 2) != -1]:
        for v in RULETABLE.itervalues():
            encoded = encoded.replace(v * 2, v)

    if encoded:
        encoded = encoded[0] + encoded[1:].replace("0", "")

    return encoded

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Levinsthein  distance (Edit-distance
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def levenshtein(s1, s2):
    #--------------------------------------------------------------------------
    # calculates the levinsthein distance ("edit distance") 
    # between two strings s1 and s2
    #--------------------------------------------------------------------------
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def bestPhoneticMatch(searchstr, choices, maxdistance):
    #--------------------------------------------------------------------------
    # finds the best phonetic match for "searchstr" amongst a number of
    # strings stored in the array 'choices'
    # This is optimized for German names only.
    # if the best match is still > maxdistance, no result is returned.
    # to retrurn the best match irrepective of distance, use axdistancce = -1
    #
    # The distance is calculated by calculating the levinsthein distance 
    # between the phonetic encoding using "Kölner Phonetic
    #--------------------------------------------------------------------------
    searchphon = encode_cgnph(searchstr)
    if maxdistance < 0: maxdistance = len(searchphon)
    mindistance = maxdistance
    bestmatch = ""
    
    searchphon = encode_cgnph(searchstr)
    for checkstring in choices:
        checkphon = encode_cgnph(checkstring)
        d = levenshtein(searchphon, checkphon)
        myask_log.debug(9, "phonetic Dist : " + str(d) +" = "+ searchstr+ "("+searchphon+ ") - " +checkstring+"("+checkphon+")")
        if d < mindistance :
            mindistance = d
            bestmatch = checkstring
        elif d == mindistance:
            # calculate the smaller levinstein distance on the orthography
            if(levenshtein(searchstr,checkstring) < levenshtein(searchstr,bestmatch)):
                bestmatch = checkstring

        
    myask_log.debug(9, "BEST match: '"+bestmatch+"'")
    return bestmatch
    
def main():
    names = ["Katharina", "Konstantin", "Andi", "Alina", "Christoph", "Christian", "Tabea", "Daniel", "David"]
    string2 = "Michael"
    
    print bestPhoneticMatch(string2, names, -1)
    
if __name__ == "__main__":
    main()    
