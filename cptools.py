from web3 import Web3, HTTPProvider
from pprint import pprint
from getpass import getpass
import json, os

GLOBAL_FROMBLOCK = 4435671

#addresses
BPFactoryAddress = "0xA225EbE73347dd87492868332F9B746bEb8499bb"
GrantableUpdatesAddress = "0xc9e8E364a009fcf35BD493b84959eDFf6caCCF72";

#ABIs
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(dir_path + '/ABIs/BPFactory.json', 'r') as infile:
	BPFactoryABI = json.load(infile)
with open(dir_path + '/ABIs/GrantableUpdates.json', 'r') as infile:
	GrantableUpdatesABI = json.load(infile)

web3 = Web3(HTTPProvider("https://gladly-golden-parrot.quiknode.io/8959339e-f0ab-4403-876f-1aed9422a44f/xh9aJBYpYQHEhu6q8jQrkA==/"))

#Contract instances
BPFactory = web3.eth.contract(address = BPFactoryAddress, abi = BPFactoryABI)
grantableUpdates = web3.eth.contract(address = GrantableUpdatesAddress, abi = GrantableUpdatesABI)

#BPCreationFilter = BPFactory.eventFilter("NewBurnablePayment", {'fromBlock':GLOBAL_FROMBLOCK})
#BPCreationEvents = BPCreationFilter.get_all_entries()

#grantableUpdatesFilter = grantableUpdates.eventFilter("Update", {'fromBlock':GLOBAL_FROMBLOCK})
#allUpdates = grantableUpdatesFilter.get_all_entries()

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


output = """functions:
newAccount() - Interactively creates a new account, optionally granting it 0.005 ETH of "seed funds" from another account
printUpdates() - prints all updates from the GrantableUpdates contract
postUpdate() - interactively posts message to the update feed
grantUpdateTo() - interactively grant update rights to another address for the GrantableUpdates contract
"""

print()
print(output)
print()
#printUpdates()
