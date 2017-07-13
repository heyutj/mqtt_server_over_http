import requests
import json
import time

#We assume that account A is 371893
#We assume that account B is 291274

#A try to login
print("A try to login")
data = {
	'method': 'LOGIN',
	'userid': '371893',
	'password':'827CCB0EEA8A706C4C34A16891F84E7B',
	'version': '1.0'
}
result = requests.post('http://10.102.24.227/manage', data=json.dumps(data))
print(result.text)
json_dic = result.json()
session_A = json_dic.get('session')
print

#B try to login
print("B try to login")
data = {
	'method': 'LOGIN',
	'userid': '291274',
	'password':'827CCB0EEA8A706C4C34A16891F84E7B',
	'version': '1.0'
}
result = requests.post('http://10.102.24.227/manage', data=json.dumps(data))
print(result.text)
json_dic = result.json()
session_B = json_dic.get('session')
print

#A try to add B as friend
print("A try to add B as friend")
data = {
	'method': 'ADDFRIEND',
	'userid': '371893',
	'session': session_A,
	'request': '291274',
	'version': '1.0'
}
result = requests.post('http://10.102.24.227/manage', data=json.dumps(data))
print(result.text)
print

#A try to list all his friend
print("A try to list all his friend")
data = {
	'method': 'LISTFRIEND',
	'userid': '371893',
	'session': session_A,
	'version': '1.0'
}
result = requests.post('http://10.102.24.227/manage', data=json.dumps(data))
print(result.text)
print

#A try to delete B
print("A try to delete B")
data = {
	'method': 'DELFRIEND',
	'userid': '371893',
	'session': session_A,
	'request': '291274',
	'version': '1.0'
}
result = requests.post('http://10.102.24.227/manage', data=json.dumps(data))
print(result.text)
print

#A try to list all his friend again
print("A try to list all his friend again")
data = {
	'method': 'LISTFRIEND',
	'userid': '371893',
	'session': session_A,
	'version': '1.0'
}
result = requests.post('http://10.102.24.227/manage', data=json.dumps(data))
print(result.text)
print

#A want to know who is online
print("A want to know who is online")
data = {
	'method': 'USERLIST',
	'userid': '371893',
	'session': session_A,
	'version': '1.0'
}
result = requests.post('http://10.102.24.227/manage', data=json.dumps(data))
print(result.text)
print

#A has nothing to do, but he still need to PING. So as B.
while True:
	print("A has nothing to do, but he still need to PING. So as B.")
	data = {
		'method': 'PING',
		'userid': '371893',
		'session': session_A,
		'version': '1.0'
	}
	result = requests.post('http://10.102.24.227/manage', data=json.dumps(data))
	print(result.text)
	data['userid']='291274'
	data['session']=session_B
	result = requests.post('http://10.102.24.227/manage', data=json.dumps(data))
	print(result.text)
	time.sleep(10)
	print

