
import sys
from time import sleep

# import the file containing the smtp server
# credentials
from smtpServerCredentials import *

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

def sendEmail(fromEmail, toEmail, subject, html):
    '''
    fromEmail is a string, such as Al Arthritis <al@arthritis.org>
    toEmail is a string, such as \'<greg@gastritis.org>, <brian@bursitis.org>\'
    subject is a string
    message is a string
    will send the emails and may print a status message
    '''
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fromEmail
    msg['To'] = toEmail
    part2 = MIMEText(html, 'html')
    msg.attach(part2)

    print "full MIME message:", msg
    #sys.exit()

    import smtplib
    server = smtplib.SMTP()
    server.connect(host, port)
    server.ehlo()
    server.starttls()
    server.login(user, password)
    
    server.sendmail(fromEmail, toEmail, msg.as_string() )
    server.quit
    
def convertmessageToMailToLink(toEmail, subject, message, ccEmail=None, bccEmail=None):
    '''
    Create an email with a mail-to link.
    Looks something like:
    mailto:toEmail?subject=blah&message=blahblah

    There is a limit to the url length that Gmail/Chrome is willing to open
    '''
    url="mailto:"
    url +=toEmail
    url += "?subject=%s" % subject
    if ccEmail:
        url += "&cc=%s" % ccEmail
    if bccEmail:
        url += "&bcc=%s" % bccEmail
    url += "&body=%s" % message
    url = url.replace(' ', '%20').replace('\n', '%0D%0A').replace('"', '%22')
    if len(url) > 10000:
        raise Exception('url is too long, %d.  shorten your message' % len(url))
    return url

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
    
    mepsEmails=getNamesAndEmailsString(memDict[countryCode])
    mepsNamesString=getNamesString(memDict[countryCode])

    # read the message that should be relayed to the MEPs
    (mepsMessageSubject, mepsMessageBody)=parseMessageFile(mepMessageFilename)
    mepsMessageBody = mepsMessageBody.replace('$MEPS$', mepsNamesString).replace('$COUNTRY$', country)
    #print mepsMessageBody

    signersToString=''.join(["%s," % signer for signer in signers])
    signersToString=signersToString[0:len(signersToString)-1]
    
    mepsMailToLink=convertmessageToMailToLink(mepsEmails, mepsMessageSubject, mepsMessageBody, ccEmail=None, bccEmail=None)
    #print mepsMailToLink
        
    # read the message to the signers
    (signersMessageSubject, signersMessageBody)=parseMessageFile(signersMessageFilename)

    # place the mailto link into the email
    signersMessageBody=signersMessageBody.replace('$MAILYOURMEPSLINK$', mepsMailToLink)

    signersMessageBody="<html>%s</html>" % signersMessageBody
    
    
    #signersMessageBody.replace('$MAILYOURMEPSLINK$', 
    
    if dryRun:
        print "Will send email:"
        if fromEmail:
            print "From: " + fromEmail
        print "To: " + signersToString
        print "Subject: " + signersMessageSubject
        print "Message:" + signersMessageBody

        print "Length of url: %d " % len(signersMessageBody)
    else:
        print "sending email to %s %s\n" % (signersToString, countryCode)
        sendEmail(fromEmail, signersToString, signersMessageSubject, signersMessageBody)


    sys.exit()

    
if __name__ == "__main__":
    main(sys.argv[1:])
