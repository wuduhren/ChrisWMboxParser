#! /usr/bin/python
# -*- coding: utf8 -*-

import mailbox
import quopri
import base64
import csv

# This is the weird part...
def decodeBody(string):
	string = quopri.decodestring(string).decode('big5', 'ignore').encode('utf-8')
	# decode string like '=B3o=ACO=BDd=A8=D2=ABH'
	# .encode('utf-8') because python 2.7 doesn't support unicode input

	if ' ' not in string:
		try:
			string += "=" * ((4 - len(string) % 4) % 4)
			return base64.decodestring(string).decode('big5', 'ignore').encode('utf-8')
			# decode string like 'DQrpgJnkupvmmK/mgqjmiYDoqILplrHnmoTmnIDmlrDlvbHniYfjgILoi6XopoHorormm7Tmgqjn' 
			# those string don't have space as far as I can tell
		except:
			return string
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
			string = string.replace("=?big5?b?", "")
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
writer = csv.writer(open("mboxOutput.csv", "wb"))
writer.writerow(["message-id", "subject", "from", "body"])


for message in mailbox.mbox('YourMboxFile.mbox'):
	body = more_payloads(message)
	writer.writerow([message['message-id'], decodeSubject(message['subject']), decodeFrom(message['from']), decodeBody(body)])


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

