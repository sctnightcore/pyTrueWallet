import os.path, time, requests, hashlib, hmac, base64, os, re, json
from datetime import datetime, timedelta

class Truewallet(object):
	Secret_key = "9LXAVCxcITaABNK48pAVgc4muuTNJ4enIKS5YzKyGZ".encode('utf-8')
	Base_url = "https://mobile-api-gateway.truemoney.com/mobile-api-gateway"
	RequestLoginOTP_url = Base_url + "/api/v1/login/otp/"
	SubmitLoginOTP_url = Base_url + "/api/v1/login/otp/verification/"
	Login_url = Base_url + "/api/v1/login/"
	Logout_url = Base_url + "/api/v1/signout/"
	GetProfile_url = Base_url + "/user-profile-composite/v1/users/"
	GetBalance_url = Base_url + "/user-profile-composite/v1/users/balance/"
	GetTransaction_url = Base_url + "/user-profile-composite/v1/users/transactions/history/"

	def __init__(self, email=None, password=None, reference_token=None):
		self.device_id = None
		self.mobile_tracking = None
		self.data = {}
		self.credentials = {}
		if self.mobile_tracking is None and self.device_id is None:
			if os.path.isfile("truewallet_identity.json"):
				with open("truewallet_identity.json", 'r') as File:
					data = json.load(File)
					self.device_id = str(data["Device_id"])
					self.mobile_tracking = str(data["Mobile_tracking"])
			else:
				with open("truewallet_identity.json", 'w') as File:
					json.dump(self.generate_identity(), File)

		if email is not None and password is not None:
			self.setCredentials(email, password, reference_token)
		elif email is not None:
			self.setAccessToken(email)

	def _check_response(self, data):
		try:
			data_json = json.load(data.content)
			if data_json.get("data"):
				if data_json["data"]["access_token"]:
					self.setAccessToken(data_json["data"]["access_token"])
				if data_json["data"]["reference_token"]:
					self.setReferenceToken(data_json["data"]["reference_token"])
				self.data = data_json["data"]
				return data_json
			else:
				return data.content
		except ValueError:
			raise Exception("{}|{}".format(data.status_code, data.content))

	def generate_identity(self):
		self.mobile_tracking = base64.b64encode(os.urandom(40))
		self.device_id = hashlib.md5(self.mobile_tracking).hexdigest()
		return {'Device_id': self.device_id[0:16], 'Mobile_tracking': self.mobile_tracking.decode() }

	def setCredentials(self, username=None, password=None, reference_token=None, type=None):
		if type is None:
			if re.search(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', username):
				type = "email"
			else: 
				type = "mobile"
		self.credentials["username"] = str(username)
		self.credentials["password"] = str(password)
		self.credentials["password_enc"] = str(hashlib.sha1((self.credentials['username']+self.credentials['password']).encode('utf-8')).hexdigest())
		self.credentials["type"] = str(type)
		self.setAccessToken(None)
		self.setReferenceToken(reference_token)

	def setAccessToken(self, access_token):
		if access_token is None:
			self.access_token = None
		else:
			self.access_token = str(access_token)

	def setReferenceToken(self, reference_token):
		if reference_token is None:
			self.reference_token = None
		else:
			self.reference_token = str(reference_token)

	def getTimestamp(self):
		return str(round(time.time() * 1000))

	def RequestLoginOTP(self):
		if self.credentials["username"] is None or self.credentials["password"] is None or self.credentials["type"] is None: return False
		timestamp = self.getTimestamp()
		r = requests.post(self.RequestLoginOTP_url,
				json={
					'type': self.credentials["type"],
					'device_id': self.device_id,
					'timestamp': timestamp,
					'signature': str(hmac.new(self.Secret_key, "{}|{}|{}".format(self.credentials["type"], self.device_id, timestamp).encode('utf-8'), hashlib.sha1).hexdigest())
				},
				headers={
					'host': 'mobile-api-gateway.truemoney.com',
					'Content-Type': 'application/json',
					'User-agent': 'okhttp/3.8.0',
					'username': self.credentials["username"],
					'password': self.credentials["password_enc"]
				}
			)
		return self._check_response(r)

	def SubmitLoginOTP(self, otp_code, mobile_number, otp_reference):
		if mobile_number is None and self.data["mobile_number"] is not None: mobile_number = self.data["mobile_number"]
		if otp_reference is None and self.data["otp_reference"] is not None: otp_reference = self.data["otp_reference"]
		if mobile_number is None or otp_reference is None: return False
		timestamp = self.getTimestamp()
		r = requests.post(self.SubmitLoginOTP_url,
				json={
					'type': self.credentials["type"],
					'otp_code': str(otp_code),
					'mobile_number': str(mobile_number),
					'otp_reference': str(otp_reference),
					'device_id': self.device_id,
					'mobile_tracking': self.mobile_tracking,
					'timestamp': timestamp,
					'signature': str(hmac.new(self.Secret_key, "{}|{}|{}|{}|{}|{}|{}".format(self.credentials['type'], otp_code, mobile_number, otp_reference, self.device_id, self.mobile_tracking, timestamp).encode('utf-8'), hashlib.sha1).hexdigest())
				},
				headers={
					'host': 'mobile-api-gateway.truemoney.com',
					'Content-Type': 'application/json',
					'User-agent': 'okhttp/3.8.0',
					'username': self.credentials["username"],
					'password': self.credentials["password_enc"]
				}
			)
		return self._check_response(r)

	def Login(self):
		if self.credentials["username"] is None or self.credentials["password"] is None or self.credentials["type"] is None or self.reference_token is None: return False
		timestamp = self.getTimestamp()
		r = requests.post(self.Login_url,
				json={
					'type': self.credentials["type"],
					'reference_token': self.reference_token,
					'device_id': self.device_id,
					'mobile_tracking': self.mobile_tracking,
					'timestamp': timestamp,
					'signature': str(hmac.new(self.Secret_key, "{}|{}|{}|{}|{}".format(self.credentials['type'], self.reference_token, self.device_id, self.mobile_tracking, timestamp).encode('utf-8'), hashlib.sha1).hexdigest())
				},
				headers={
					'host': 'mobile-api-gateway.truemoney.com',
					'Content-Type': 'application/json',
					'User-agent': 'okhttp/3.8.0',
					'username': self.credentials["username"],
					'password': self.credentials["password_enc"]
				}
			)
		return self._check_response(r)

	def Logout(self):
		if self.access_token is None: return False
		r = requests.get(self.Logout_url + self.access_token,
				headers={
					'host': 'mobile-api-gateway.truemoney.com',
					'User-agent': 'okhttp/3.8.0'
				}
			)
		return self._check_response(r)
	def GetProfile(self):
		if self.access_token is None: return False
		r = requests.get(self.GetProfile_url,
				headers={
					'host': 'mobile-api-gateway.truemoney.com',
					'User-agent': 'okhttp/3.8.0',
					'Authorization': self.access_token
				}
			)
		return self._check_response(r)

	def GetBalance(self):
		if self.access_token is None: return False
		r = requests.get(self.GetBalance_url,
				headers={
					'host': 'mobile-api-gateway.truemoney.com',
					'User-agent': 'okhttp/3.8.0',
					'Authorization': self.access_token
				}
			)
		return self._check_response(r)
