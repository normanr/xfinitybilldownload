#!/usr/bin/python

import datetime
import json
import mechanize
import os
import sys

# Create .xfinitybilldownload in your home directory like this:
# { "username": "user@example.com", "passsword": "letmein" }
with open(os.path.expanduser('~/.xfinitybilldownload')) as fp:
  config = json.load(fp)

if len(sys.argv) > 1:
  os.chdir(sys.argv[1])

# Browser
br = mechanize.Browser()

# Browser options
br.set_handle_robots(False)

# Want debugging messages?
def debug():
  br.set_debug_http(True)
  br.set_debug_responses(True)

cj = mechanize.CookieJar()
br.addheaders = [('User-Agent', 'xfinitybilldownload/0.1')]
br.set_cookiejar(cj)

# Start oauth connection
br.open('https://customer.xfinity.com/oauth/force_connect/')

# Login
br.select_form(name='signin')
br.form['user'] = config['username']
br.form['passwd'] = config['password']

br.submit()

# Account data
br.open('/apis')
account_data = json.loads(br.response().read())

account_suffix = account_data['accountNumber'].replace('*', '')

br.open('/apis/bill/past-statements')

# Parse past-statements and download pdfs
data = json.loads(br.response().read())

for statement in data['statements']:

  statement_date = datetime.datetime.utcfromtimestamp(statement['statementDateInMillis'] / 1000)

  localPdf = 'comcast-%s-%s.pdf' % (
      account_suffix, statement_date.strftime('%Y-%m'))

  if os.path.exists(localPdf):
    continue

  print 'Fetching %s...' % localPdf

  br.open('/apis/bill/statement/%(id)s' % statement)

  pdf_data = br.response().read()

  with open(localPdf, 'wb') as f:
    f.write(pdf_data)
