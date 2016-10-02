#!/usr/bin/python

import Checksum
import requests
import base64
import json
import requests

print "Content-type: text/html\n"
MERCHANT_KEY = 'kbzk1DSbJiV_O3p5';
import cgi

form = cgi.FieldStorage()
respons_dict = {}

for i in form.keys():
 respons_dict[i]=form[i].value
 if i=='CHECKSUMHASH':
    checksum = form[i].value

if 'GATEWAYNAME' in respons_dict:
	if respons_dict['GATEWAYNAME'] == 'WALLET':
		respons_dict['BANKNAME'] = 'null';

verify = Checksum.verify_checksum(respons_dict, MERCHANT_KEY, checksum)
print verify

if verify:
	if respons_dict['RESPCODE'] == '01':
		print "order successful";
	else:
		print "order unsuccessful because"+respons_dict['RESPMSG'];
else: 
	print "order unsuccessful because"+respons_dict['RESPMSG'];
