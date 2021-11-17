from session import SBankenSession
import yaml

def main():
	cfg = None
	with open('/etc/sbko/sbko.yaml', 'r') as cfgf:
		try:
			cfg = yaml.safe_load(cfgf)
		except yaml.YAMLError as e:
			print(e)
			return
	print(cfg)
	
	cfg["from_threshold"] = int(cfg["from_threshold"])
	cfg["available_threshold"] = int(cfg["available_threshold"])

	session = SBankenSession(cfg["client_id"], cfg["secret"])
	accounts = session.get_accounts()

	interesting_accounts = {}

	# find the accounts we're going to use
	for account in accounts:
		if account["name"] == cfg["usage_account"]:
			interesting_accounts["usage"] = {
				"name": account["name"],
				"accountId": account["accountId"],
				"available": account["available"]
			}
		if account["name"] == cfg["from_account"]:
			interesting_accounts["from"] = {
				"name": account["name"],
				"accountId": account["accountId"],
				"available": account["available"]
			}

	# precautions
	if not "usage" in interesting_accounts or not "from" in interesting_accounts:
		print("Couldn't find usage/from accounts!")
		return

	from_available = interesting_accounts["from"]["available"]
	if from_available <= cfg["from_threshold"]:
		print("The from account available funds limit is exceeded")
		return

	# this is where the fun begins
	usage_available = interesting_accounts["usage"]["available"]
	if usage_available <= cfg["available_threshold"]:
		# attempt to fill the account up to the threshold
		to_transfer = (cfg["available_threshold"] - usage_available)
		if (from_available - to_transfer) <= cfg["from_threshold"]:
			# if that would exceed the "from account threshold" then take as much as we can, leaving us at the threshold exactly
			to_transfer = (from_available - cfg["from_threshold"])
		to_transfer = round(to_transfer, 2)

		print("Transfering {}NOK from {} to {}".format(to_transfer, interesting_accounts["from"]["name"], interesting_accounts["usage"]["name"]))

		success = session.transfer(
			interesting_accounts["from"]["accountId"],
			interesting_accounts["usage"]["accountId"],
			to_transfer,
			message="Konstant overføring (API)"
		)

		if success:
			print("Transfer successful".format(usage_available + to_transfer))
	else:
		print("Usage account had sufficient balance. No transfer performed")

if __name__ == "__main__":
	main()