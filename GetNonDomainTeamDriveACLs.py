#!/usr/bin/env python2
"""
# Purpose: Delete all drive file ACLs for Team Drives shared outside of a list of specified domains
# Note: This script requires Advanced GAM with Team Drive support:
#	https://github.com/taers232c/GAMADV-XTD, https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DOMAIN_LIST.
# Usage:
# 1: Get all Team Drives
#  $ gam redirect csv ./teamdrives.csv print teamdrives
# 1: Get ACLs for all Team Drives
#  $ gam redirect csv ./teamdriveacls.csv multiprocess csv ./teamdrives.csv gam print drivefileacls teamdriveid ~id
# 2: From that list of ACLs, output a CSV file with headers "teamDriveId,permissionId,role,type,emailAddress,domain"
#    that lists the driveFileIds and permissionIds for all ACLs except those from the specified domains.
#    (n.b., role, type, emailAddress and domain are not used in the next step, they are included for documentation purposes)
#  $ python GetNonDomainTeamDriveACLs.py ./teamdriveacls.csv deletetdacls.csv
# 3: Inspect deletetdacls.csv, verify that it makes sense and then proceed
# 4: Delete the ACLs
#  $ gam redirect stdout ./deletetdacls.out multiprocess redirect stderr stdout multiprocess csv deletetdacls.csv gam delete drivefileacl teamdriveid "~teamDriveId" "~permissionId"
"""

import csv
import re
import sys

# Substitute your domain(s) in the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = ['domain.com',]

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'wb')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['teamDriveId', 'permissionId', 'role', 'type', 'emailAddress', 'domain'], lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'rbU')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in row.iteritems():
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if v == u'domain':
        domain = row['permissions.{0}.domain'.format(permissions_N)]
        emailAddress = ''
      elif v in ['user', 'group']:
        if row['permissions.{0}.deleted'.format(permissions_N)] == u'True':
          continue
        emailAddress = row['permissions.{0}.emailAddress'.format(permissions_N)]
        domain = emailAddress[emailAddress.find(u'@')+1:]
      else:
        continue
      if domain not in DOMAIN_LIST:
        outputCSV.writerow({'teamDriveId': row['id'],
                            'permissionId': 'id:{0}'.format(row['permissions.{0}.id'.format(permissions_N)]),
                            'role': row['permissions.{0}.role'.format(permissions_N)],
                            'type': v,
                            'emailAddress': emailAddress,
                            'domain': domain})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
