EmailParliament
===============

Code and data files for emailing parliament

Author: Naomi Fox 
Date: June 1, 2012

= Introduction =
This directory contains python code, data files, and sample data for emailing parliament.

To use:
sendEUEmails.py --help

= Contents =
* EU-emails.json   - contains the countries, names, and emails of EU current parliament members as of June 1, 2012.
* sampleemails.csv - a file containing example emails and countries for EU constituents who are participating in the email campaing
* actamessage.txt  - message subject and body for ACTA campaign
* sendEUEmails.py  - the main python file containing code for sending emails
* sendEUEmailsMulti.py  - python file for sending an email to all MEPs from the same country
* ParseEuData/	 - directory containing data files, code, and instructions for generating the EU-emails.json file.

= Requirements =
* sendmail in /usr/bin/

= About = 
This code was written by Naomi for Center for Rights.

= Notes =

* About mailto links: http://email.about.com/od/mailtoemaillinks/a/mailto_elements.htm
* Mailto link generator: http://email.about.com/library/misc/blmailto_encoder.htm

A space must be translated to "%20", for example, and a line break becomes "%0D%0A".