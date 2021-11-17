from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from urllib.parse import quote

from .decorators import ensure_token

class SBankenSession:
	def __init__(self, client_id, secret):
		client_id = quote(client_id)
		secret = quote(secret)
		self.auth = HTTPBasicAuth(client_id, secret)
		client = BackendApplicationClient(client_id=client_id)
		self.session = OAuth2Session(client=client)

		self.refresh_session()

	def refresh_session(self):
		self.session.fetch_token(
			token_url='https://auth.sbanken.no/identityserver/connect/token',
			client_id=self.auth.username,
			client_secret=self.auth.password,
		)

	@ensure_token
	def get_accounts(self, retry=True):
		response = self.session.get("https://publicapi.sbanken.no/apibeta/api/v2/accounts")

		if response.status_code != 200:
			raise RuntimeError("failed to fetch accounts")

		return response.json()["items"]

	@ensure_token
	def transfer(self, from_accid, to_accid, amount, message="Overføring via API", retry=True):
		if amount <= 1 or amount >= 100000000000000000:
			return False

		data = {"fromAccountId": from_accid, "toAccountId": to_accid, "message": message, "amount": amount}
		response = self.session.post(
			"https://publicapi.sbanken.no/apibeta/api/v2/transfers",
			json=data
		)

		# oh yeah, its funky
		# check if the response code is 2xx
		if response.status_code // 100 != 2:
			raise RuntimeError(f"failed to execute transfer. status code {response.status_code}")

		return True
