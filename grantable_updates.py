from utils import loadABI
from init_web3 import *
from accounts import *

GrantableUpdatesAddress = "0xc9e8E364a009fcf35BD493b84959eDFf6caCCF72"
GrantableUpdatesABI = loadABI('ABIs/GrantableUpdates.json');

#Contract instances
grantableUpdates = web3.eth.contract(address = GrantableUpdatesAddress, abi = GrantableUpdatesABI)

def printUpdates():
	grantableUpdatesFilter = grantableUpdates.eventFilter("Update", {'fromBlock': GLOBAL_FROMBLOCK})
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
