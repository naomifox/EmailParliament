#
# file: sendEUEmailsMulti.py
# send an email to the member of EU parliament
#
# To test (place your email into country XX in EU-emails.json)
# python sendEUEmailsMulti.py -i testSigners.txt -m actamessageMulti.txt -c XX 


import sys

# fixes some issues with unicode
from django.utils.encoding import smart_str, smart_unicode

# these two files must be in the current working directory
euEmailsFilename='EU-emails.json'
euCountriesFilename='EU-countrycodes.json'

def sendEmail(fromEmail, toEmail, subject, message):
    '''
    fromEmail is a string, such as Al Arthritis <al@arthritis.org>.  if no fromEmail is specified, pass None
    toEmail is a string, such as \'<greg@gastritis.org>, <brian@bursitis.org>\'
    subject is a string
    message is a string
    will send the emails and may print a status message
    '''
    SENDMAIL = "/usr/sbin/sendmail" # sendmail location
    import os
    p = os.popen("%s -t " % SENDMAIL, "w")
    if fromEmail:
        p.write("From: %s\n" % fromEmail)
    p.write("To: %s\n" % toEmail)
    p.write("Subject: %s\n" % subject)
    p.write("\n") # blank line separating headers from body
    p.write(message)
    sts = p.close()
    if sts != None:
        print "Sendmail exit status", sts


def parseMessageFile(messageFile):
    '''
    example message file:
    The subject is Vote NO on ACTA
    This is the body of the email.

    This is more of the body of the email.
    '''
    
    f = open(messageFile, 'r')
    subject=f.readline()
    body=f.read()
    return (subject,body)

def getNamesAndEmailsString(nameAndEmailList):
    '''
    converts to a string ready to paste into an email To: field
    example:
    mem1 <mem1@country1.eu>, mem2 <mem2@country2.edu>
    '''
    emailString = ""

    
    for (name, email) in nameAndEmailList:
        if name and email:
            emailString = emailString + ("%s <%s>, " % (smart_str(name), email.encode("iso-8859-15")))
        else:
            print ("Cannot send to %s, %s" % (smart_str(name), email))
    #remove the last comma
    emailString = emailString[0:len(emailString)-2]
    return emailString

def getNamesString(nameAndEmailList):
    '''
    converts to a string ready to place into a greeting
    Dear ...,
    mem1, mem2, mem3,
    '''
    return ''.join(["%s, "% smart_str(name).title() for (name, email) in nameAndEmailList])

def usage():
    print "Usage: "
    print "-h for help"
    print "-d for dry-run"
    print "-f \"name <email>\" - from from-email"
    print "-i acta_emails.txt -m message-file -c country-code"
    print "Correct format for input file"
    print "email1@email1.com"
    print "email2@email2.com"
    print "Correct format for message file"
    print "Subject: This is the subject"
    print "Body: This is the body"
    print "Dear $EU_MEPS$ "
    print "And this is more of the body"
    print "Thank you,"
    print "$SIGNERS$"

def main(argv):    
    import getopt
    try:                                
        opts, args = getopt.getopt(argv, "hdf:i:m:c:", ["help", "dry-run", "from-email", "input-file", "message-file", "country-code"]) 
    except getopt.GetoptError:
        usage()                          
        sys.exit(2)

    fromEmail=None
    signersAndEmailAddressesFilename=None
    messageFilename=None
    countryCode=None
    dryrun=False
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--dry-run"):
            dryrun=True
        elif opt in ("-f", "--from-email"):
            fromEmail=arg
        elif opt in ("-i", "--input-file"):
            signersAndEmailAddressesFilename=arg
        elif opt in ("-m", "--message-file"):
            messageFilename=arg
        elif opt in ("-c", "--country-code"):
            countryCode=arg

    if signersAndEmailAddressesFilename == None or messageFilename==None or countryCode == None:
        print "Need signers file, message file, and country-code"
        usage()
        sys.exit()

    import json
    memDict = json.load(open(euEmailsFilename, 'r'))
    countryDict = json.load(open(euCountriesFilename, 'r'))
    
    signers=""
    signersfile=open(signersAndEmailAddressesFilename, 'r')
    ctr=0
    for line in signersfile:
        ctr +=1
        signers += "%d : %s" % (ctr, line)
        (subject, body) = parseMessageFile(messageFilename)
       
    if countryCode not in memDict:
        print 'unknown country error.  %s \n' % countryCode
        sys.exit(1)
    toEmails=getNamesAndEmailsString(memDict[countryCode])
    mepsNamesString=getNamesString(memDict[countryCode])

    country="your country"
    if countryCode in countryDict:
        country = smart_str(countryDict[countryCode])
    #country=countryDict[countryCode]

    body=body.replace('$EU_MEPS$', mepsNamesString).replace('$SIGNERS$', signers).replace('$COUNTRY$', country)

    if dryrun:
        print "Will send email:"
        if fromEmail:
            print "From: " + fromEmail
        print "To: " + toEmails
        print "Subject: " + subject
        print "Message:" + body
    else:
        print "sending email to %s %s\n" % (toEmails, countryCode)
        sendEmail(fromEmail, toEmails, subject, body)
            
        #reps=memDict[country]
        #print reps    
    
if __name__ == "__main__":
    main(sys.argv[1:])
