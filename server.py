from flask import Flask,request
from flask import render_template
import helper
import json
import subprocess
app = Flask(__name__)


METHOD = ['REG', 'LOGIN', 'LOGOUT', 'CHAT', 'ADDFRIEND', 'DELFRIEND', 'LISTFRIEND', 'USERLIST', 'PING']

@app.route('/manage', methods=['POST', 'GET'])
def manage():
	if request.method == 'POST':
		print(request.get_data().decode('utf-8'))
		json_dict = json.loads(request.get_data().decode('utf-8'))
		try:
			if json_dict['version'] != '1.0' and json_dict['version'] != '1.1':
				print(json.dumps(helper.ERROR['ERROR_VERSION']))
				return json.dumps(helper.ERROR['ERROR_VERSION'])
			else:
				if json_dict['method'] in METHOD:
					func = getattr(helper, 'on_'+json_dict['method'])
					result = func(json_dict)
					print(result)
					return result
				else:
					print(json.dumps(helper.ERROR['ERROR_METHOD']))
					return json.dumps(helper.ERROR['ERROR_METHOD'])

		except KeyError:
			print(json.dumps(helper.ERROR['ERROR_MISSING_ARGUMENT']))
			return json.dumps(helper.ERROR['ERROR_MISSING_ARGUMENT'])

	else:
		print(json.dumps(helper.ERROR['ERROR_NOT_POST']))
		return json.dumps(helper.ERROR['ERROR_NOT_POST'])

@app.route('/', methods=['GET'])
def index():
	if request.method == 'GET':
		return render_template("index.html")

@app.route('/log', methods=['GET'])
def log():
	if request.method == 'GET':
		return "<h2>LOG</h2>"+str(subprocess.check_output('tail log -n 200', shell=True)).replace('\n','<br>')


if __name__ == '__main__':
	helper.connect_redis()
	app.run(host='0.0.0.0',port=80,threaded=True)
