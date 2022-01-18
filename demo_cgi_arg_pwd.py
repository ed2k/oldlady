#!/usr/bin/python

print("Content-type: text/plain\n")
import sys
#print sys.version

#for m in sys.modules:
#  print m

import cgi
import cgitb; cgitb.enable()
#cgi.print_environ()
#cgi.print_directory()
#cgi.print_environ_usage()
form = cgi.FieldStorage()
msg = form.getvalue('flproxyB','')
print('--svrcv',msg)

import os
cmd = 'pwd'
r = os.popen(cmd).read() 
print(r)
