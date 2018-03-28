from pprint import pprint
from getpass import getpass
from init_web3 import *
from urllib.request import urlopen
import json

GrantableUpdatesABI = loadABI('ABIs/GrantableUpdates.json');

#Contract instances
grantableUpdates = web3.eth.contract(address = GrantableUpdatesAddress, abi = GrantableUpdatesABI)

def fetchABIFromEtherscan(address):
	html = urlopen("https://api.etherscan.io/api?module=contract&action=getabi&address=" + address + "&apikey=9TBD9VA31ASIGDRID7SBASUHPAHJGPKT17")
	result = json.loads(html.read())
	if (result['status'] == '1'):
		return json.loads(result['result'])
	else:
		return None
	
def contractInstanceFromAddress(address):
	abi = fetchABIFromEtherscan(address)
	return web3.eth.contract(address = address, abi = abi)

def getTxHashIfSuccessful(txHash):
	isBytes = isinstance(txHash, bytes)
	if (isBytes):
		return web3.toHex(txHash)
	else:
		print("Error! expected txhash, but got a " + str(type(txHash)))
		return False

def newAccount():
	password = getpass("Password for new account: ")
	if (getpass("Confirm password: ") != password):
		print("Passwords do not match!")
		return

	newAddress = web3.personal.newAccount(password)
	accountNum = len(web3.personal.listAccounts) - 1

	assert(web3.personal.listAccounts[accountNum] == newAddress)
	print()
	print("---Account created!---")
	print("Account number: " + str(accountNum))
	print("Address: " + newAddress)

	willFund = input("Fund new account with 0.005 ETH from an existing account? (y/n):  ")
	if (willFund.lower() == 'y'):
		fundingAddress = pickAccountInteractively("Fund from account # ")
		authorizeAndUnlock(fundingAddress, "Password for funding account: ")
		txHash = getTxHashIfSuccessful(web3.eth.sendTransaction({'from':fundingAddress, 'to':newAddress, 'value':web3.toWei(0.005, 'ether')}))
		if (txHash):
			print("Transaction signed and broadcast: " + txHash)
		relock(fundingAddress)

def getAccountAddress(accountNum):
	return web3.personal.listAccounts[accountNum]

def printNumberedAccountList():
	# Oddly, web3.personal.listAccounts looks like a variable but behaves like a function.
	# So we have to "run" the variable and store the result, to avoid "running" the variable every loop
	accounts = web3.personal.listAccounts

	for i in range(len(accounts)):
		print(str(i) + ".  " + accounts[i])

def pickAccountInteractively(prompt = "Account #"):
	printNumberedAccountList()
	print()

	accountNum = int(input(prompt))
	return getAccountAddress(accountNum)

def authorizeAndUnlock(account, prompt="Account password: "):
	password = getpass(prompt)
	if (not web3.personal.unlockAccount(account, password)):
		print("password incorrect. Aborting.")
		return False
	print("Authenticated and unlocked.")
	return True

def relock(account):
	print("Relocking account.")
	web3.personal.lockAccount(account)

def printUpdates():
	grantableUpdatesFilter = grantableUpdates.eventFilter("Update", {'fromBlock':GLOBAL_FROMBLOCK})
	allUpdates = grantableUpdatesFilter.get_all_entries()
	for update in allUpdates:
		print(str(update.args.agent) + ": " + update.args.data)

def postUpdate():
	account = pickAccountInteractively("Post from account #")

	message = input("message: ")

	if (not authorizeAndUnlock(account)):
		return

	txHash = getTxHashIfSuccessful(grantableUpdates.functions.postUpdate(message).transact({"from":account}))
	if (txHash):
		print("Transaction signed and broadcast: " + txHash)

	relock(account)

def grantUpdateTo():
	account = pickAccountInteractively("Use which account to grant permissions? #")

	grantToAddress = input("Grant 'update' permission to what address? ")

	if (not authorizeAndUnlock(account)):
		return

	txHash = getTxHashIfSuccessful(grantableUpdates.functions.grantUpdatePermissionTo(grantToAddress).transact({'from':account}))
	if (txHash):
		print("Transaction signed and broadcast: " + txHash)

	relock(account)


if __name__ == "__main__":
	output = """functions:
	newAccount() - Interactively creates a new account, optionally granting it 0.005 ETH of "seed funds" from another account
	printUpdates() - prints all updates from the GrantableUpdates contract
	postUpdate() - interactively posts message to the update feed
	grantUpdateTo() - interactively grant update rights to another address for the GrantableUpdates contract
	"""

	print()
	print(output)
	print()
	printUpdates()
