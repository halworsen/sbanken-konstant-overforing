from session import SBankenSession
from dotenv import load_dotenv
from os import getenv
from datetime import datetime

def main():
	print('[{}]'.format(datetime.utcnow().strftime('%d-%m-%Y @ %H:%M:%S')))
	print('Initializing SBanken session...')
	session = SBankenSession(getenv('KASJFLOW_CLIENT_ID'), getenv('KASJFLOW_API_PASSWORD'))
	accounts = session.get_accounts(getenv('KASJFLOW_CUSTOMER_ID'))

	interesting_accounts = {}
	# find the accounts we're going to use
	for account in accounts:
		if account['name'] == getenv('KASJFLOW_TO_ACCT'):
			interesting_accounts['to'] = {
				'name': account['name'],
				'accountId': account['accountId'],
				'available': account['available']
			}
			print('Found account to transfer to!')
		if account['name'] == getenv('KASJFLOW_FROM_ACCT'):
			interesting_accounts['from'] = {
				'name': account['name'],
				'accountId': account['accountId'],
				'available': account['available']
			}
			print('Found account to transfer from!')

	# Make sure we found both the account to transfer to and from
	if not interesting_accounts['to'] or not interesting_accounts['from']:
		print('Unable to find either account. Aborting.')
		return

	from_available = interesting_accounts['from']['available']
	from_threshold = int(getenv('KASJFLOW_FROM_THRESHOLD'))
	if from_available <= from_threshold:
		print('Account to transfer from has insufficient balance. Aborting.')
		return

	usage_available = interesting_accounts['to']['available']
	to_threshold = int(getenv('KASJFLOW_TO_THRESHOLD'))
	if usage_available >= to_threshold:
		print('Account to transfer to already has sufficient balance. Aborting.')
		return

	# Attempt to fill the account up to the threshold
	to_transfer = (to_threshold - usage_available)
	if (from_available - to_transfer) <= from_threshold:
		# If that would exceed the 'from account threshold' then take as much as we can, leaving us at the threshold exactly
		to_transfer = (from_available - from_threshold)
	to_transfer = round(to_transfer, 2)

	print('Transfering {}kr from {} to {}...'.format(
			to_transfer,
			interesting_accounts['from']['name'],
			interesting_accounts['to']['name']
		)
	)

	# Perform the transfer
	success = session.transfer(
		getenv('KASJFLOW_CUSTOMER_ID'),
		interesting_accounts['from']['accountId'],
		interesting_accounts['to']['accountId'],
		to_transfer,
		message='Kasjflow (API)'
	)

	if success:
		print('Succesfully transfered {}kr!'.format(to_transfer))
	else:
		print('Transfer failed.')

if __name__ == '__main__':
	load_dotenv()
	main()