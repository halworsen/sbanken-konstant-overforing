from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from urllib.parse import quote
import json

from .decorators import ensure_token

class SBankenSession:
	def __init__(self, client_id, secret):
		client_id = quote(client_id)
		secret = quote(secret)
		self.auth = HTTPBasicAuth(client_id, secret)
		client = BackendApplicationClient(client_id=client_id)
		self.session = OAuth2Session(client=client)

		self.refresh_session()

	# no refresh tokens yet, grr
	def refresh_session(self):
		self.session.fetch_token(token_url='https://api.sbanken.no/identityserver/connect/token', auth=self.auth)

	@ensure_token
	def get_accounts(self, customer_id, retry=True):
		response = self.session.get(
			"https://api.sbanken.no/bank/api/v1/Accounts",
			headers={"customerId": customer_id}
		).json()

		if response["isError"]:
			raise RuntimeError("{}: \"{}\"".format(response["errorType"], response["errorMessage"]))

		return response["items"]

	@ensure_token
	def transfer(self, customer_id, from_accid, to_accid, amount, message="Overføring via API", retry=True):
		data = {"fromAccountId": from_accid, "toAccountId": to_accid, "message": message, "amount": amount}

		response = self.session.post(
			"https://api.sbanken.no/bank/api/v1/Transfers",
			headers={"customerId": customer_id},
			json=data
		).json()

		if response["isError"]:
			raise RuntimeError("{}: \"{}\"".format(response["errorType"], response["errorMessage"]))

		return True
