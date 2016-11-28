#! /usr/bin/python
# -*- coding: utf8 -*-

import mailbox
import quopri
import base64
import csv
from datetime import datetime


mboxFileName = 'your_mbox_file.mbox'
outputCSVFileName = 'your_csv_file.csv'
codingMethods = ['cp936', 'utf-8', 'big5', 'gb2312', "iso-2022-jp", "us-ascii", "euc-kr", "gb18030" ,"gbk"] #here is where you edit

codingMethodPrefix = []
conversationJSON = {}


def main():
	setupCodingMethodPrefixArray()
	writer = csv.writer(open(outPutCSVFileName, "wb"))
	writer.writerow(["message-id", "subject", "date", "sender", "addressee", "body"])

	for message in mailbox.mbox(mboxFileName):
		messageID = message['message-id']
		subject = decodeStringWithPrefix(message['subject'])
		date = dateInISO(message)
		sender = decodeSenderOrAddressee(message['from'])
		addressee = decodeSenderOrAddressee(message['to'])
		body = decodeBody(more_payloads(message), codingMethod(message), contentTransferEncoding(message))

		writer.writerow([messageID, subject, date, sender, addressee, body])



# ---------------------------------------------Main Function---------------------------------------------

def more_payloads(message):
	body = ""
	if message.is_multipart():
		for payload in message.get_payload():
			body += more_payloads(payload)
	else:
		if message.get_content_type() == 'text/plain':
			body = message.get_payload()
	return body
	
def decodeBody(string, codingMethod, contentTransferEncoding):
	if contentTransferEncoding == 'quoted-printable':
		return quopri.decodestring(string).decode(codingMethod, 'ignore').encode('utf-8')
	elif contentTransferEncoding == 'base64':
		string += "=" * ((4 - len(string) % 4) % 4)
		return base64.decodestring(string).decode(codingMethod, 'ignore').encode('utf-8')
	elif contentTransferEncoding == '7bit':
		#this is weird. Mbox says it uses 7bit, but actually quoted-printable.
		return quopri.decodestring(string).decode(codingMethod, 'ignore').encode('utf-8')
	else:
		print('function decodeBody does not support ' + contentTransferEncoding + '-decoding, please add another elif yourselves.')
		return string

def decodeSenderOrAddressee(string):
	name = string.rsplit('<', 1)[0]
	string = string.replace(name, '')
	string = decodeStringWithPrefix(name) + string

	return string

def decodeStringWithPrefix(string):
	try:
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
	except:
		return string


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
	print('please add "' + str(contentType.lower()) + '" to your codingMethods array.')
	return contentType.lower()

def findStringBetween(string, firstString, lastString):
    try:
        start = string.index(firstString) + len(firstString)
        end = string.index(lastString, start)
        return string[start:end]
    except ValueError:
        return ""

def dateInISO(message):
	date = datetime.strptime(message['Date'].split('+')[0], '%a, %d %b %Y %H:%M:%S ')
	dateInISO = str(date.isoformat()) + 'Z'
	return dateInISO

if __name__ == '__main__':
	main()
