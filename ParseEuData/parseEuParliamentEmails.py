#!/usr/bin/env python
#
# File: parseEuParliamentEmails.py
# Author: Naomi Fox
# Date: June 1, 2012
# 
# Takes json files collected from https://memopol.lqdn.fr
# and writes a json file  containing a lookup dictionary
# of country codes to names

import json
import sys

DEBUG=False

class ParliamentaryMemberEmailParser:
    '''
    A class which parses through json files taken from https://memopol.lqdn.fr
    and retrieves a table
    '''
    def __init__(self,
                 repnamefilename='reprepresentative.json',
                 repemailfilename='mepemail.json',
                 repfilename='mepmep-0-711-and-713-1232.json',
                 countryfilename='mepcountry.json'):

        # lookup table for country codes and names
        self.countryCodeToCountryNameDict = {}

        # lookup table for names and emails
        self.countryToNamesAndEmails={}

        #open with json
        repnamedata=json.load(open(repnamefilename, 'r'))
        repemaildata=json.load(open(repemailfilename, 'r'))
        repdata=json.load(open(repfilename, 'r'))
        countrydata=json.load(open(countryfilename, 'r'))

        #intermediate dicts used to build name_id => country_code dict

        countryIdToCountryCodeDict={}
        
        # id => country
        countryiddict={}
        # name_id => email
        emaildict={}
        # name_id => full_name
        namedict={}
        # name_id => country_code
        countrydict={}
        # country_code => country_name
        countrycodedict={}

        for mem in repdata['objects']:
            id=mem['id']
            countrymep_set=mem['countrymep_set']
            active=mem['active']
            if active:
                if DEBUG: print "ID: ", id
                if DEBUG: print "active: ", active
                if DEBUG: print "countrymep_set", countrymep_set
                if DEBUG: print len(countrymep_set)
                if len(countrymep_set) != 1:
                    raise ("Problem.  multiple countries")
                countrymepid=countrymep_set[0].split('/')[-2]
                if DEBUG: print countrymepid
                countryiddict[id]=countrymepid

        for mem in repnamedata['objects']:
            if DEBUG: print "%s :  %s" % (mem['full_name'], mem['id'])
            namedict[mem['id']] = mem['full_name']

        for mem in repemaildata['objects']:
            id=mem['representative'].split('/')[-2]
            if DEBUG: print "%s :  %s" % (id, mem['email'])
            emaildict[id] = mem['email']

        for country in countrydata['objects']:
            code=country['code']
            countryname=country['name']
            self.countryCodeToCountryNameDict[code]=countryname
            countrymep_set=country['countrymep_set']
            if DEBUG: print "Country:", code
            if DEBUG: print countrymep_set
            for countrymep in countrymep_set:
                if DEBUG: print "countrymep",countrymep
                countrymepid=countrymep.split('/')[-2]
                if DEBUG: print "id", countrymepid
                countryIdToCountryCodeDict[countrymepid]=code

        for (nameid,countryid) in countryiddict.items():
            countrydict[nameid]=countryIdToCountryCodeDict[countryid]
    
        if DEBUG: print "names and emails"
        for nameid in countrydict.keys():
            if nameid not in emaildict:
                emaildict[nameid] = None
            country=countrydict[nameid]
            if DEBUG: print  nameid, countrydict[nameid], namedict[nameid], emaildict[nameid]

        #load the lookup table for country codes to names and emails
        for (nameid, countrycode) in countrydict.items():
            fullName=namedict[nameid]
            email=emaildict[nameid]
            if countrycode not in self.countryToNamesAndEmails:
                self.countryToNamesAndEmails[countrycode] = []
            self.countryToNamesAndEmails[countrycode].append((fullName, email))

        


    def getCountryToNamesAndEmailsDict(self):
        return self.countryToNamesAndEmails

    def getNamesAndEmails(self, countryCode):
        return self.countryToNamesAndEmails[countryCode]

    def getNamesAndEmailsString(self, countryCode):
        '''
        converts to a string ready to paste into an email To: field
        example:
        mem1 <mem1@country1.eu>, mem2 <mem2@country2.edu>
        '''
        if countryCode not in self.countryToNamesAndEmails:
            raise "Country not found: " + countryCode
        emailString = ""
        print self.countryToNamesAndEmails[countryCode]
        for (name, email) in self.countryToNamesAndEmails[countryCode]:
            if name and email:
                emailString = emailString + ("%s <%s>," % (name, email))
            else:
                print ("Cannot send to %s, %s" % (name, email))
        emailString = emailString[0:len(emailString)-1]
        return emailString

    def dumpCountriesNamesAndEmailsToFile(self, outputfilename):
        of = open(outputfilename, 'w')
        json.dump(self.countryToNamesAndEmails, of)

    def dumpCountryCodesAndCountryNamesToFile(self, outputfilename):
        of = open(outputfilename, 'w')
        json.dump(self.countryCodeToCountryNameDict, of)

def usage():
    print "Usage: "
    print "-h for help"
    print "-i acta_emails_and_countries.csv"
    print "Correct format for input file"
    print "\"name1\", \"email1\""
    print "\"name2\", \"email2\""

        
def main():               
    parser = ParliamentaryMemberEmailParser()
    parser.dumpCountriesNamesAndEmailsToFile('EU-emails.json')
    parser.dumpCountryCodesAndCountryNamesToFile('EU-countrycodes.json')

    if DEBUG:
        testDict = json.load(open('test.txt', 'r'))
        print testDict
        print len(testDict)
       

if __name__ == "__main__":
    main()
