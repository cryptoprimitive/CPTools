from getpass import getpass
from utils import *
from init_web3 import *

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
