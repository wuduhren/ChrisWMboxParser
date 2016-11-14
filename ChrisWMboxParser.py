#! /usr/bin/python
# -*- coding: utf8 -*-

import mailbox
import quopri
import base64
import csv

mboxFileName = '/Users/eph/desktop/quiz_ranger_mails/quiz_ranger_mails_ios/郵件/e- 題目.mbox'
outPutCSVFileName = '/Users/eph/desktop/quiz_ranger_mails/quiz_ranger_mails_ios_csv/題目.csv'
codingMethods = ['cp936', 'utf-8', 'big5'] #here is where you edit
codingMethodPrefix = []

def main():
	setupCodingMethodPrefixArray()
	writer = csv.writer(open(outPutCSVFileName, "wb"))
	writer.writerow(["message-id", "subject", "from", "body"])

	for message in mailbox.mbox(mboxFileName):
		body = decodeBody(more_payloads(message), codingMethod(message), contentTransferEncoding(message))
		writer.writerow([message['message-id'], decodeStringWithPrefix(message['subject']), decodeFrom(message['from']), body])
		# writer.writerow([message['message-id'], message['subject'], message['from'], , message['Content-Type'].split("=",1)[1] ,body])


# ---------------------------------------------Main Function---------------------------------------------
def decodeBody(string, codingMethod, contentTransferEncoding):
	if contentTransferEncoding == 'quoted-printable':
		return quopri.decodestring(string).decode(codingMethod, 'ignore').encode('utf-8')
	elif contentTransferEncoding == 'base64':
		string += "=" * ((4 - len(string) % 4) % 4)
		return base64.decodestring(string).decode(codingMethod, 'ignore').encode('utf-8')
	else:
		return string

def decodeFrom(string):
	name = string.rsplit('<', 1)[0]
	string = string.replace(name, '')
	string = decodeStringWithPrefix(name) + string

	return string

def decodeStringWithPrefix(string):
	for codingMethod in codingMethods:
		if codingMethod in string.lower():
			contentTransferEncoding = findStringBetween(string.lower(), codingMethod + '?', '?') # b: base64, q: quopri
			string = deleteCodingMethodPrefix(string)
			if contentTransferEncoding == 'b':
				string += "=" * ((4 - len(string) % 4) % 4)
				string = base64.decodestring(string).decode(codingMethod, 'ignore').encode('utf-8')
			elif contentTransferEncoding == 'q':
				string = quopri.decodestring(string).decode(codingMethod, 'ignore').encode('utf-8')
			return string
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


# ---------------------------------------------Utilities---------------------------------------------
def setupCodingMethodPrefixArray():
	for codingMethod in codingMethods:
		codingMethodPrefix.append('=?' + codingMethod.lower()+ '?' + 'q' + '?')
		codingMethodPrefix.append('=?' + codingMethod.lower()+ '?' + 'Q' + '?')
		codingMethodPrefix.append('=?' + codingMethod.lower()+ '?' + 'b' + '?')
		codingMethodPrefix.append('=?' + codingMethod.lower()+ '?' + 'B' + '?')
		codingMethodPrefix.append('=?' + codingMethod.upper()+ '?' + 'q' + '?')
		codingMethodPrefix.append('=?' + codingMethod.upper()+ '?' + 'Q' + '?')
		codingMethodPrefix.append('=?' + codingMethod.upper()+ '?' + 'b' + '?')
		codingMethodPrefix.append('=?' + codingMethod.upper()+ '?' + 'B' + '?')

#replace string like =?Big5?Q?
def deleteCodingMethodPrefix(string):
	for eachCodingMethodPrefix in codingMethodPrefix:
		if eachCodingMethodPrefix in string:
			string = string.replace(eachCodingMethodPrefix, '')
			return string

def contentTransferEncoding(message):
	if message['Content-Transfer-Encoding'] is not None:
		return message['Content-Transfer-Encoding']
	else:
		return findStringBetween(str(message), 'Content-Transfer-Encoding: ', '\n')

def codingMethod(message):
	contentType = findStringBetween(str(message), 'charset=', '\n')
	for codingMethod in codingMethods:
		if codingMethod in contentType.lower():
			return codingMethod

def findStringBetween(string, firstString, lastString):
    try:
        start = string.index(firstString) + len(firstString)
        end = string.index(lastString, start)
        return string[start:end]
    except ValueError:
        return ""











if __name__ == '__main__':
	main()
