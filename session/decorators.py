from oauthlib.oauth2 import TokenExpiredError

# decorator for ensuring the function has an access token to use
def ensure_token(func):
	def ensured(*args, **kwargs):
		self = args[0]
		try:
			return func(*args, **kwargs)
		except TokenExpiredError:
			self.refresh_session()

			# retry once
			if kwargs["retry"]:
				kwargs["retry"] = False
				return func(*args, **kwargs)

	return ensured
