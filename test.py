import requests

#280099
#226664
data = {
	'method': 'LOGIN',
	'username': 'test2',
	'userid': '226664',
	'password':'827CCB0EEA8A706C4C34A16891F84E7B',
	'session': 'JFUmxcCO',
	'request': ['280099'],
	'version': '1.0'
}
result = requests.post('http://127.0.0.1:5000/manage', data=data)
print(result.text)