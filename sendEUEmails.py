
import sys
from time import sleep


euEmailsFilename='EU-emails.json'
logfile="log.txt"

#how many seconds to wait before sending out the next email                     
delay=1


DEBUG=False

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
    p.write("To: %s\n" % toEmail)
    p.write("Subject: %s\n" % subject)
    p.write("\n") # blank line separating headers from body
    p.write(message)
    sts = p.close()
    if sts != None:
        open(logfile, 'a').write( "Sendmail exit status" + str(sts))
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
    print "list:", nameAndEmailList
    for (name, email) in nameAndEmailList:
        if name and email:
            emailString = emailString + ("%s <%s>, " % (name.encode("iso-8859-15"), email.encode("iso-8859-15")))
        else:
            open(logfile, 'a').write("Cannot send email to member: %s, email-address: %s.\n" % (name, email))
            print ("Cannot send to %s, %s" % (name, email))
    #remove the last comma
    emailString = emailString[0:len(emailString)-2]
    return emailString

def usage():
    print "Usage: "
    print "-h for help"
    print "-i acta_emails_and_countries.csv -m message-file"
    print "Correct format for input file"
    print "\"name1\", \"email1\""
    print "\"name2\", \"email2\""
    print "Correct format for message file"
    print "Subject: This is the subject"
    print "Body: This is the body"
    print " "
    print "And this is more of the body"

def main(argv):
    import getopt
    try:                                
        opts, args = getopt.getopt(argv, "hi:m:", ["help", "input-file", "message-file"]) 
    except getopt.GetoptError:
        usage()                          
        sys.exit(2)

    signersAndEmailAddressesFilename=None
    messageFilename=None

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-i", "--input-file"):
            signersAndEmailAddressesFilename=arg
        elif opt in ("-m", "--message-file"):
            messageFilename=arg

    if signersAndEmailAddressesFilename == None or messageFilename==None:
        print "Need signers file and message file"
        usage()
        sys.exit()

    import json
    memDict = json.load(open(euEmailsFilename, 'r'))
    import csv
    r = csv.reader(open(signersAndEmailAddressesFilename, 'r'))
    (subject, body) = parseMessageFile(messageFilename)
       
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
    main(sys.argv[1:])
