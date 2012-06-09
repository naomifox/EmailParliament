
import sys
from time import sleep


# fixes some issues with unicode
from django.utils.encoding import smart_str, smart_unicode


# these two files must be in the current working directory
euEmailsFilename='EU-emails.json'
euCountriesFilename='EU-countrycodes.json'

# this file is produced as a log file
logfile="log.txt"

#how many seconds to wait before sending out the next email                     
delay=1


DEBUG=False


# email key words.  We will search for these strings and replace them with other values
# $MEPEMAILS$ - the emails of the constituent's MEPs, ready to paste into To: field in an email
# $MEPS$ - a list of names of a constituent's MEPS, to be pasted after "Dear" 
# $MAILYOURMEPSLINK$ - a mailto: link which provides everything necessary to email your MEP
# $COUNTRY$ - the name of the country 

def sendEmail(fromEmail, toEmail, subject, message):
    '''
    fromEmail is a string, such as Al Arthritis <al@arthritis.org>
    toEmail is a string, such as \'<greg@gastritis.org>, <brian@bursitis.org>\'
    subject is a string
    message is a string
    will send the emails and may print a status message
    '''
    SENDMAIL = "/usr/sbin/sendmail" # sendmail location
    import os
    p = os.popen("%s -t " % SENDMAIL, "w")
    p.write("From: %s\n" % fromEmail)
    p.write("Bcc: %s\m" % fromEmail)
    p.write("To: %s\n" % toEmail)
    p.write("Subject: %s\n" % subject)
    p.write("\n") # blank line separating headers from body
    p.write(message)
    sts = p.close()
    if sts != None:
        open(logfile, 'a').write( "Sendmail exit status" + str(sts))
        print "Sendmail exit status", sts

def convertmessageToMailToLink(toEmail, subject, message, ccEmail=None, bccEmail=None):
    url="mailto:"
    url +=toEmail
    url += "?subject=%s" % subject
    if ccEmail:
        url += "&cc=%s" % ccEmail
    if bccEmail:
        url += "&bcc=%s" % bccEmail
    url += "&body=%s" % message
    url = url.replace(' ', '%20').replace('\n', '%0D%0A')
    return url
    #import urllib
    #input_url = urllib.quote ( url )
    #return "mailto:"+input_url

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
    print "Send one email to each 500 constituents (bcc'd of course) with a mail-to link to email their reps"
    print "Usage: "
    print "-h for help"
    print "-d (for dry-run, optional)"
    print "-i signers-file -s signers-message-file -m mep-message-file -c country-code"
    print "Correct format for input file"
    print "\"name1\", \"email1\""
    print "\"name2\", \"email2\""
    print "Correct format for message file"
    print "Subject: This is the subject"
    print "Body: This is the body"
    print " "
    print "And this is more of the body"
    print ""
    print "Run example:"
    print "python sendEUEmailsWithMailToLinks.py -d -f me@me.com -i testSigners.txt -s actamessageForSigners.txt -m actamessageForMeps.txt -c XX"


def main(argv):
    import getopt
    try:
        opts, args = getopt.getopt(argv, "hdf:i:s:m:c:", ["help", "dry-run", "from-email", "signers-file", "signers-message-file", "mep-message-file", "country-code"]) 
    except getopt.GetoptError:
        usage()                          
        sys.exit(2)


    # If you just want to test sending emails, without actually doing it,
    # then set the dryRun flag
    dryRun=False
    
    # the fight for the future email address.
    # must match that used for the gmail account, if we are relaying through gmail.
    # example: Fight For The Future <fightfortheftr@gmail.com>
    fromEmail=None
    
    # the text file containing the signers email addresses
    signersEmailFilename=None

    # the message we're sending to the signers
    signersMessageFilename=None

    # the message the signers will then relay to their MEPs
    mepMessageFilename=None

    # the country code
    countryCode=None
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-d", "--dry-run"):
            dryRun=True
        elif opt in ("-f", "--from-email"):
            fromEmail=arg
        elif opt in ("-i", "--signers-file"):
            signersEmailFilename=arg
        elif opt in ("-s", "--signers-message-file"):
            signersMessageFilename=arg
        elif opt in ("-m", "--mep-message-file"):
            mepMessageFilename=arg
        elif opt in ("-c", "--country-code"):
            countryCode=arg

    if not (fromEmail and signersEmailFilename and signersMessageFilename and mepMessageFilename and countryCode):
        print "missing some command line args:"
        print "from-email %s" % fromEmail
        print "signersEmailAddressesFilename %s" % signersEmailFilename
        print "signers-message-file %s" % signersMessageFilename
        print "mepMessageFile %s" % mepMessageFilename
        print "country-code %s" % countryCode
        print ""
        usage()
        sys.exit()

    # load the lookup tables
    import json
    memDict = json.load(open(euEmailsFilename, 'r'))
    countryDict = json.load(open(euCountriesFilename, 'r'))

    signers=[]
    signersfile=open(signersEmailFilename, 'r')
    for line in signersfile:
        signers.append(line.strip())
    print signers

    if countryCode not in memDict:
        print 'unknown country error.  %s \n' % countryCode
        sys.exit(1)
    country = smart_str(countryDict[countryCode])
    
    toEmails=getNamesAndEmailsString(memDict[countryCode])
    mepsNamesString=getNamesString(memDict[countryCode])

    # read the message that should be relayed to the MEPs
    (mepsMessageSubject, mepsMessageBody)=parseMessageFile(mepMessageFilename)
    mepsMessageBody = mepsMessageBody.replace('$MEPS$', mepsNamesString).replace('$COUNTRY$', country)
    #print mepsMessageBody

    signersToString=''.join(["%s, " % signer for signer in signers])
    
    mepsMailToLink=convertmessageToMailToLink(signersToString, mepsMessageSubject, mepsMessageBody, ccEmail=None, bccEmail=None)
    #print mepsMailToLink
        
    # read the message to the signers
    (signersMessageSubject, signersMessageBody)=parseMessageFile(signersMessageFilename)

    # place the mailto link into the email
    signersMessageBody=signersMessageBody.replace('$MAILYOURMEPSLINK$', mepsMailToLink)
    
    
    
    #signersMessageBody.replace('$MAILYOURMEPSLINK$', 
    
    if dryRun:
        print "Will send email:"
        if fromEmail:
            print "From: " + fromEmail
        print "To: " + toEmails
        print "Subject: " + signersMessageSubject
        print "Message:" + signersMessageBody
    else:
        print "sending email to %s %s\n" % (toEmails, countryCode)
        sendEmail(fromEmail, toEmails, signersMessageSubject, signersMessageBody)


    sys.exit()

    ctr=0
    unknownCountries=[]
    for (email, country) in r:
        print email, country
        if country not in memDict:
            open(logfile, 'a').write('unknown country error.  %s %s\n' % (email, country))
            if country not in unknownCountries:
                unknownCountries.append(country)
            continue
        ctr += 1
        fromEmail=email
        toEmails=getNamesAndEmailsString(memDict[country])
        if DEBUG:
            print "Will send email:"
            print "From: " + fromEmail
            print "To: " + toEmails
            print "Subject: " + subject
            print "Message:" + body
        else:
            open(logfile, 'a').write("sending email from %s %s\n" % (email, country) )
            sendEmail(fromEmail, toEmails, subject, body)
            sleep(delay)
            
        #reps=memDict[country]
        #print reps

    if DEBUG: print "unknown countries", unknownCountries
    unknownStr = str(unknownCountries)
    open(logfile, 'a').write("unknown countries: %s\n" % unknownStr)
    print ctr

    open(logfile, 'a').write("Check /var/log/mail.log to see if emails were sent successfully\n")
    
    
if __name__ == "__main__":
    #print convertmessageToMailToLink("naomifox@gmail.com", "This is a test", "And this is my message.\nAnd this is more of my message.\n", "naomi.fox@gmail.com")
    #print ""
    #print convertmessageToMailToLink("\"Na Na\" <naomifox@gmail.com>,naom.i.fox@gmail.com", "This is a test", "And this is my message.\nAnd this is more of my message.\n", "naomi.fox@gmail.com,naom.fox@gmail.com")
    #sys.exit()
    main(sys.argv[1:])
