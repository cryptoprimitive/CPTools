from web3 import Web3, HTTPProvider
from pprint import pprint
from getpass import getpass
import json, os

GLOBAL_FROMBLOCK = 4435671

#addresses
BPFactoryAddress = "0xA225EbE73347dd87492868332F9B746bEb8499bb"
GrantableUpdatesAddress = "0xc9e8E364a009fcf35BD493b84959eDFf6caCCF72";

#ABIs
with open('ABIs/BPFactory.json', 'r') as infile:
	BPFactoryABI = json.load(infile)
with open('ABIs/GrantableUpdates.json', 'r') as infile:
	GrantableUpdatesABI = json.load(infile)

web3 = Web3(HTTPProvider("https://gladly-golden-parrot.quiknode.io/8959339e-f0ab-4403-876f-1aed9422a44f/xh9aJBYpYQHEhu6q8jQrkA==/"))

#Contract instances
BPFactory = web3.eth.contract(address = BPFactoryAddress, abi = BPFactoryABI)
grantableUpdates = web3.eth.contract(address = GrantableUpdatesAddress, abi = GrantableUpdatesABI)

#BPCreationFilter = BPFactory.eventFilter("NewBurnablePayment", {'fromBlock':GLOBAL_FROMBLOCK})
#BPCreationEvents = BPCreationFilter.get_all_entries()

#grantableUpdatesFilter = grantableUpdates.eventFilter("Update", {'fromBlock':GLOBAL_FROMBLOCK})
#allUpdates = grantableUpdatesFilter.get_all_entries()

def printNumberedAccountList():
	for i in range(len(web3.personal.listAccounts)):
		print(str(i) + ".  " + web3.personal.listAccounts[i])
	
def pickAccountInteractively():
	printNumberedAccountList()
	print()
	
	accountNum = input("Use which account #? ")
	return web3.personal.listAccounts[int(accountNum)]

def authorizeAndUnlock(account):
	password = getpass("Ready to sign. Account password: ")
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
	account = pickAccountInteractively()
	
	message = input("message: ")
	
	if (not authorizeAndUnlock(account)):
		return
	
	print(grantableUpdates.functions.postUpdate(message).transact({"from":account}))
	
	relock(account)

def grantUpdateTo():
	account = pickAccountInteractively()
	
	grantToAddress = input("Grant 'update' permission to what address? ")
	
	if (not authorizeAndUnlock(account)):
		return
	
	print(grantableUpdates.functions.grantUpdatePermissionTo(grantToAddress).transact({'from':account}))
	
	relock(account)
	

output = """functions:
printUpdates() - prints all updates from the GrantableUpdates contract
postUpdate() - interactively posts message to the update feed
grantUpdateTo() - interactively grant update rights to another address for the GrantableUpdates contract
"""

print()
print(output)
print()
#printUpdates()