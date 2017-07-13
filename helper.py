
import json
import redis
import random
import string

global VERSION
VERSION = '1.1'

ERROR = {
	'ERROR_NOT_POST': {'error':'1', 'message':'You can only use POST method to access this server.', 'version': VERSION},
	'ERROR_MISSING_ARGUMENT': {'error':'1', 'message':'Argument is missing.', 'version': VERSION},
	'ERROR_VERSION': {'error':'1', 'message':'Version is not match.', 'version': VERSION},
	'ERROR_METHOD': {'error':'1', 'message':'No such method.', 'version': VERSION},
	'ERROR_PASSWORD_FORMAT': {'error':'1', 'message':'Password must be encryped by MD5 with length 32 characters.', 'version': VERSION},
	'ERROR_PASSWORD': {'error':'1', 'message':'Wrong password.', 'version': VERSION},
	'ERROR_NAME_FORMAT': {'error':'1', 'message':'Username should be small than 8 characters.', 'version': VERSION},
	'ERROR_USERID': {'error':'1', 'message':'Userid does not exist.', 'version': VERSION},
	'ERROR': {'error':'1', 'message':'Can not add(del) yourself as a friend.', 'version': VERSION},
	'ERROR_FRIEND_NOT_EXIST': {'error':'1', 'message':'Request friend does not exist.', 'version': VERSION},
	'ERROR_SESSION': {'error':'1', 'message':'Session is expired or you need login.', 'version': VERSION},
	'ERROR_NOT_FRIEND': {'error':'1', 'message':'NO USER HAS BEEN DEL..', 'version': VERSION},
	'ERROR_UNKNOWN': {'error':'3', 'message':'UNKNOWN ERROR.', 'version': VERSION},

}

def create_userid(userid_pool):
	tmp=random.randint(100000,999999)
	while (tmp in userid_pool):
		tmp=creat_userid()
	return str(tmp)
def create_session():
	session = ''.join([random.choice(string.ascii_letters+string.digits) for i in range(8)])
	return session

def connect_redis():
	pool = redis.ConnectionPool(host='localhost', port=16379, db=0)
	global r
	r = redis.StrictRedis(connection_pool=pool)

def on_REG(payload):
	username=payload['username']
	password=payload['password']

	try:
		if len(username)>8:
			return json.dumps(ERROR['ERROR_NAME_FORMAT'])
		if len(password)!=32:
			return json.dumps(ERROR['ERROR_PASSWORD_FORMAT'])

		manufacturer=payload.get('manufacturer',None)
		device=payload.get('device',None)

		userid_pool=r.smembers('userid_pool')
		userid=create_userid(userid_pool)
		
		user_info_dic={"username":username, "password":password, "userid":userid}
		r.hmset(userid+'_info',user_info_dic)
		r.sadd('userid_pool',userid)

		return json.dumps({"error": "0","message": "Success.","userid": userid,"username": username,"version": VERSION})
	except:
		return json.dumps(ERROR['ERROR_UNKNOWN'])

def on_LOGIN(payload):
	userid=payload['userid']
	password=payload['password']

	try:
		if len(password)!=32:
				return json.dumps(ERROR['ERROR_PASSWORD_FORMAT'])

		userid_pool=r.smembers('userid_pool')
		user_info=r.hmget(userid+"_info", ["username", "password"])
		if user_info:
			if password != user_info[1].decode('ascii'):
				return json.dumps(ERROR['ERROR_PASSWORD'])

			session=create_session()
			r.setex(userid,30,session)
			return json.dumps({"error": "0","message": "Success.","userid": userid,"session": session, 'username': user_info[0].decode('ascii'), "version": VERSION})
		else:
			return json.dumps(ERROR['ERROR_USERID'])
	except Exception as e:
		raise e
		return json.dumps(ERROR['ERROR_UNKNOWN'])
		


def on_LOGOUT(payload):
	session=payload['session']
	userid=payload['userid']

	try:
		client_state=r.get(userid)
		if client_state and session==client_state.decode('ascii'):
			r.delete(userid)
			return json.dumps({"error": "0","message": "Success.", "version": VERSION})
		else:
			return json.dumps(ERROR['ERROR_SESSION'])
	except:
		return json.dumps(ERROR['ERROR_UNKNOWN'])

def on_PING(payload):
	session=payload['session']
	userid=payload['userid']

	try:
		client_state=r.get(userid)
		print(client_state)
		if client_state and session==client_state.decode('ascii'):
			r.setex(userid,30,session)
			userlist=[]
			want_friend=[]
			for user in r.smembers("userid_pool"):
				if(r.get(user)):
					userlist.append(user.decode('ascii'))
			for friend in r.keys('*'+'_add'+userid):
				want_friend.append(friend[:6].decode('ascii'))
			return json.dumps({"error": "0","message": "Success.", 'userlist': userlist, "want_friend": want_friend, "version": VERSION})
		else:
			return json.dumps(ERROR['ERROR_SESSION'])
	except Exception as e:
		return json.dumps(ERROR['ERROR_UNKNOWN'])

def on_USERLIST(payload):
	session=payload['session']
	userid=payload['userid']

	try:
		client_state=r.get(userid)
		print(client_state)
		if client_state and session==client_state.decode('ascii'):
			r.setex(userid,30,session)
			userlist=[]
			for user in r.smembers("userid_pool"):
				if(r.get(user)):
					userlist.append(user.decode('ascii'))
			return json.dumps({"error": "0","message": "Success.", 'userlist': userlist, "version": VERSION})
		else:
			return json.dumps(ERROR['ERROR_SESSION'])
	except Exception as e:
		return json.dumps(ERROR['ERROR_UNKNOWN'])

def on_CHAT(payload):
	session=payload['session']
	userid=payload['userid']
	request=payload['request']

	try:
		client_state=r.get(userid)
		if client_state and session==client_state.decode('ascii'):
			r.setex(userid,30,session)
			flag_has_user_not_online = False
			topic={}
			for request_user in request:
				topic_list=[]
				user_session=r.get(request_user)
				if user_session:
					topic_list.append('/'+request_user.decode('ascii')+'/'+user_session.decode('ascii')+'/QoS_0')
					topic_list.append('/'+request_user.decode('ascii')+'/'+user_session.decode('ascii')+'/QoS_1')
					topic_list.append('/'+request_user.decode('ascii')+'/'+user_session.decode('ascii')+'/QoS_2')
					topic[str(request)]=topic_list
				else:
					flag_has_user_not_online=True
			if not flag_has_user_not_online:
				return json.dumps({"error": "0","message": "Success.", 'topic': topic, "version": VERSION})
			else:
				return json.dumps({"error": "2","message": "Some user is not online.", 'topic': topic, "version": VERSION})
		else:
			return json.dumps(ERROR['ERROR_SESSION'])
	except Exception as e:
		return json.dumps(ERROR['ERROR_UNKNOWN'])


def on_ADDFRIEND(payload):
	session=payload['session']
	userid=payload['userid']
	request=payload['request']

	try:
		client_state=r.get(userid)
		if client_state and session==client_state.decode('ascii'):
			r.setex(userid,30,session)
			friend_name=r.hget(request+'_info','username')
			my_name=r.hget(userid+'_info', 'username')
			if friend_name:
				if request==userid:
					return json.dumps(ERROR['ERROR_FRIEND'])
				else:
					r.setex(userid+'_add'+request, 300, request+'_add'+userid)
					if(r.get(request+'_add'+userid)):
						r.delete(userid+'_add'+request)
						r.delete(request+'_add'+userid)
						r.hset(userid+'_friendlist', request, friend_name)
						r.hset(request+'_friendlist', userid, my_name)
					return json.dumps({"error": "0","message": "Success. But your friend need to confirm.", "version": VERSION})

			else:
				return json.dumps(ERROR['ERROR_FRIEND_NOT_EXIST'])
		else:
			return json.dumps(ERROR['ERROR_SESSION'])
	except:

		return json.dumps(ERROR['ERROR_UNKNOWN'])


def on_DELFRIEND(payload):
	session=payload['session']
	userid=payload['userid']
	request=payload['request']

	try:
		client_state=r.get(userid)
		if client_state and session==client_state.decode('ascii'):
			r.setex(userid,30,session)
			friend_name=r.hget(request+'_info','username')
			if friend_name:
				if request==userid:
					return json.dumps(ERROR['ERROR_FRIEND'])
				else:
					del_number_1 = r.delete(request+'_add'+userid)
					del_number_2 = r.hdel(userid+'_friendlist', request, friend_name)
					del_number_3 = r.hdel(request+'_friendlist', userid, friend_name)
					if del_number_1 != 0:
						return json.dumps({"error": "0","message": "Success.", "version": VERSION})
					else:
						if del_number_2 != 0:
							return json.dumps({"error": "0","message": "Success.", "version": VERSION})
						else:
							return json.dumps(ERROR['ERROR_NOT_FRIEND'])

			else:
				return json.dumps(ERROR['ERROR_FRIEND_NOT_EXIST'])
		else:
			return json.dumps(ERROR['ERROR_SESSION'])
	except:
		return json.dumps(ERROR['ERROR_UNKNOWN'])

def on_LISTFRIEND(payload):
	session=payload['session']
	userid=payload['userid']

	try:
		client_state=r.get(userid)
		newlist = {}
		if client_state and session==client_state.decode('ascii'):
			r.setex(userid,30,session)
			friendlist=r.hgetall(userid+'_friendlist')
			for (i,j) in friendlist.items():
				tmp1=i.decode('ascii')
				tmp2=j.decode('ascii')
				newlist[tmp1]=tmp2
			print(newlist)
			return json.dumps({"error": "0","message": "Success.", "friendlist": newlist, "version": VERSION})
		else:
			return json.dumps(ERROR['ERROR_SESSION'])
	except Exception as e:
		return json.dumps(ERROR['ERROR_UNKNOWN'])

