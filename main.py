from session import SBankenSession
import cfg

def main():
	session = SBankenSession(cfg.client_id, cfg.secret)
	accounts = session.get_accounts(cfg.customer_id)

	interesting_accounts = {}

	# find the accounts we're going to use
	for account in accounts:
		print(account)
		if account["name"] == cfg.usage_account:
			interesting_accounts["usage"] = {
				"name": account["name"],
				"accountId": account["accountId"],
				"available": account["available"]
			}

			print("Found usage account: {}".format(account["name"]))
		if account["name"] == cfg.from_account:
			interesting_accounts["from"] = {
				"name": account["name"],
				"accountId": account["accountId"],
				"available": account["available"]
			}

			print("Found from account: {}".format(account["name"]))

	# precautions
	if not interesting_accounts["usage"] or not interesting_accounts["from"]:
		print("Couldn't find usage/from accounts!")
		return

	from_available = interesting_accounts["from"]["available"]
	if from_available <= cfg.from_threshold:
		print("The from account available funds limit is exceeded")
		return

	# this is where the fun begins
	usage_available = interesting_accounts["usage"]["available"]
	print("Your available balance on {} is: {}NOK".format(interesting_accounts["usage"]["name"], usage_available))
	if usage_available <= cfg.available_threshold:
		# attempt to fill the account up to the threshold
		to_transfer = (cfg.available_threshold - usage_available)
		if (from_available - to_transfer) <= cfg.from_threshold:
			# if that would exceed the "from account threshold" then take as much as we can, leaving us at the threshold exactly
			to_transfer = (from_available - cfg.from_threshold)
		to_transfer = round(to_transfer, 2)

		print("Transfering {} from the \"from\" account to the usage account".format(to_transfer))

		success = session.transfer(
			cfg.customer_id,
			interesting_accounts["from"]["accountId"],
			interesting_accounts["usage"]["accountId"],
			to_transfer,
			message="Konstant overføring (API)"
		)

		if success:
			print("Successfully transfered the monies. New balance on the usage account should now be {}.".format(usage_available + to_transfer))
	else:
		print("No need to transfer!")

if __name__ == "__main__":
	main()