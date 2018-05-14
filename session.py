from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
import json

class SBankenSession:
	def __init__(self, client_id, secret):
		self.auth = HTTPBasicAuth(client_id, secret)
		client = BackendApplicationClient(client_id=client_id)
		self.session = OAuth2Session(client=client)

		self.refresh_session()

	# no refresh tokens yet, grr
	def refresh_session(self):
		self.session.fetch_token(token_url='https://api.sbanken.no/identityserver/connect/token', auth=self.auth)

	def get_accounts(self, customer_id, retry=True):
		try:
			response = self.session.get("https://api.sbanken.no/bank/api/v1/Accounts/{}".format(customer_id)).json()
			
			if response["isError"]:
				raise Error("{}: \"{}\"".format(response["errorType"], response["errorMessage"]))

			return response["items"]
		except TokenExpiredError as error:
			self.refresh_session()

			# retry once
			if retry:
				self.get_accounts(customer_id, retry=False)

	def transfer(self, customer_id, from_accnumber, to_accnumber, amount, message="Overføring via API", retry=True):
		try:
			data = {"fromAccount": from_accnumber, "toAccount": to_accnumber, "message": message, "amount": amount}

			response = self.session.post(
				"https://api.sbanken.no/bank/api/v1/Transfers/{}".format(customer_id),
				json=data
			).json()

			if response["isError"]:
				raise Error("{}: \"{}\"".format(response["errorType"], response["errorMessage"]))

			return True
		except TokenExpiredError as error:
			self.refresh_session()

			# retry once
			if retry:
				return self.transfer(customer_id, retry=False)

			return False