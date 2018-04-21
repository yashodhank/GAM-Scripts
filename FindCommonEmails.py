#!/usr/bin/env python2
"""
# Purpose: Create a CSV file showing email addresses that appear in all CSV files generated by separate gam report commands
# Usage:
# 1: Issue various report commands:
#  $ gam report users filter "gmail:num_emails_sent<1" parameters gmail:num_emails_sent > num_emails_sent.csv
#  $ gam report users filter "accounts:creation_time<2017-09-01T00:00:00.000Z" parameters accounts:creation_time > creation_time.csv
#  $ gam report users filter "gmail:last_interaction_time<2016-01-01T00:00:00.000Z" parameters gmail:last_interaction_time > last_interaction_time.csv
# 2: From that list of files, output a CSV file with the header email that shows the email addresses that appear in all files
#  $ python FindCommonEmails.py ./CommonEmails.csv ./num_emails_sent.csv ./creation_time.csv ./last_interaction_time.csv
"""

import csv
import sys

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

if sys.argv[1] != '-':
  outputFile = open(sys.argv[1], 'wb')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['email',], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

users = {}
allFilesCount = len(sys.argv)-2
for i in range(2, len(sys.argv)):
  inputFile = open(sys.argv[i], 'rbU')
  for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
    email = row['email']
    users.setdefault(email, 0)
    users[email] += 1
  inputFile.close()
for user, count in sorted(users.iteritems()):
  if count == allFilesCount:
    outputCSV.writerow({'email': user})

if outputFile != sys.stdout:
  outputFile.close()
