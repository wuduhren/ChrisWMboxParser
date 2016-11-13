#! /usr/bin/python
# -*- coding: utf8 -*-

import mailbox
import quopri
import base64
import csv

mboxFileName = '/Users/eph/desktop/quiz_ranger_mails/quiz_ranger_mails_ios/郵件/e- 題目.mbox'
outPutCSVFileName = '/Users/eph/desktop/quiz_ranger_mails/quiz_ranger_mails_ios_csv/題目.csv'

def findStringBetween(string, firstString, lastString):
    try:
        start = string.index(firstString) + len(firstString)
        end = string.index(lastString, start)
        return string[start:end]
    except ValueError:
        return ""


def contentType(message):
	codingMethod = ['cp936', 'utf-8', 'big5'] #here is where you edit
	contentType = findStringBetween(str(message), 'charset=', '\n')
	for eachCodingMethod in codingMethod:
		if eachCodingMethod in contentType.lower():
			# print('contentType: ')
			return eachCodingMethod

def contentTransferEncoding(message):
	if message['Content-Transfer-Encoding'] is not None:
		return message['Content-Transfer-Encoding']
	else:
		return findStringBetween(str(message), 'Content-Transfer-Encoding: ', '\n')

def decodeBody(string, contentType, contentTransferEncoding):
	if contentTransferEncoding == 'quoted-printable':
		return quopri.decodestring(string).decode(contentType, 'ignore').encode('utf-8')
	elif contentTransferEncoding == 'base64':
		string += "=" * ((4 - len(string) % 4) % 4)
		return base64.decodestring(string).decode(contentType, 'ignore').encode('utf-8')
	else:
		return string

def decodeFrom(string):
	name = string.rsplit('<', 1)[0]
	string = string.replace(name, '')
	string = decodeSubject(name) + string
	return string


def decodeSubject(string):
	try:
		if '=?Big5?Q?' in string:
			string = string.replace("=?Big5?Q?", "")
			string += "=" * ((4 - len(string) % 4) % 4)
			return base64.decodestring(string).decode('big5').encode('utf-8')

		elif '=?Big5?B?' in string:
			string = string.replace("=?Big5?B?", "")
			string += "=" * ((4 - len(string) % 4) % 4)
			return base64.decodestring(string).decode('big5').encode('utf-8')

		elif '=?big5?b?' in string:
			string = string.replace("=?big5?b?", "")
			string += "=" * ((4 - len(string) % 4) % 4)
			return base64.decodestring(string).decode('big5').encode('utf-8')

		elif '=?big5?B?' in string:
			string = string.replace("=?big5?B?", "")
			string += "=" * ((4 - len(string) % 4) % 4)
			return base64.decodestring(string).decode('big5').encode('utf-8')

		elif '=?utf-8?Q?' in string:
			string = string.replace("=?utf-8?Q?", "")
			string += "=" * ((4 - len(string) % 4) % 4)
			return quopri.decodestring(string).encode('utf-8')

		elif '=?utf-8?b?' in string:
			string = string.replace("=?utf-8?b?", "")
			string += "=" * ((4 - len(string) % 4) % 4)
			return quopri.decodestring(string).encode('utf-8')

		elif '=?utf-8?B?' in string:
			string = string.replace("=?utf-8?B?", "")
			string += "=" * ((4 - len(string) % 4) % 4)
			return quopri.decodestring(string).encode('utf-8')

		elif '=?UTF-8?B?' in string:
			string = string.replace("=?UTF-8?B?", "")
			string += "=" * ((4 - len(string) % 4) % 4)
			return quopri.decodestring(string).encode('utf-8')

		elif '=?UTF-8?Q?' in string:
			string = string.replace("=?UTF-8?Q?", "")
			string += "=" * ((4 - len(string) % 4) % 4)
			return quopri.decodestring(string).encode('utf-8')

		elif '=?utf-8?q?' in string:
			string = string.replace("=?utf-8?q?", "")
			string += "=" * ((4 - len(string) % 4) % 4)
			return quopri.decodestring(string).encode('utf-8')

		else:
			return quopri.decodestring(string).decode('big5', 'ignore').encode('utf-8')
	except:
		return string


def more_payloads(message):
	body = ""
	if message.is_multipart():
		for payload in message.get_payload():
			body += more_payloads(payload)
	else:
		if message.get_content_type() == 'text/plain':
			body = message.get_payload()
	return body


# --------------------------------------Main--------------------------------------
writer = csv.writer(open(outPutCSVFileName, "wb"))
writer.writerow(["message-id", "subject", "from", "body"])

for message in mailbox.mbox(mboxFileName):
	body = more_payloads(message)
	body = decodeBody(body, contentType(message), contentTransferEncoding(message))
	writer.writerow([message['message-id'], decodeSubject(message['subject']), decodeFrom(message['from']), body])
	# writer.writerow([message['message-id'], message['subject'], message['from'], , message['Content-Type'].split("=",1)[1] ,body])



# --------------------------------------Test--------------------------------------
# string = 'v823/rT6tGE6SlRZOUotVFctemgtVFctMS45ODggDQrX95hJz7W9eTppUGhvbmUgT1MgOS4yIA0K'
# string += "=" * ((4 - len(string) % 4) % 4)
# string = base64.decodestring(string).decode('cp936', 'ignore').encode('utf-8')
# print(string)






# --------------------------------------Readme--------------------------------------
'''

0. This is a tool you can convert Gmail .mbox file in to .csv file. 
Especially mails that are mixed up with 中文 and English.
Those decoding and encoding are insane, but it works for me.
I am a beginner, if there are better way to do it, please let me know.

1. If your mails are mostly mixed up with '中文' and English, this should work.

2. If your mails are mostly in English you don't need most of the decode function.
just simply: writer.writerow([message['message-id'], message['subject'], message['from'], body])
and add 'decode=True' in get_payload, so your def more_payloads become:
	def more_payloads(message):
		body = ""
		if message.is_multipart():
			for payload in message.get_payload():
				body += more_payloads(payload)
		else:
			if message.get_content_type() == 'text/plain':
				body = message.get_payload(decode=True)
		return body

3. Others:
For example, if your mails are Japanese + English just change big-5 to shift-jis...etc.

'''

