from getpass import getpass
from utils import *
from init_web3 import *

import os, sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + '/ethereum-mnemonic-utils')
from mnemonic_utils import mnemonic_to_private_key

import os.path
CYPHER_SECRETE_FILE = 'cyphersecrete.txt'
LOCAL_STORAGE = {'private_key': None, 'account': None}

from web3.auto import w3

def createLocalAccount():
    seed = input("Enter your 12 seed words to init your private key: ")
    password = getpass("Enter your password to protect your private key: ")
    encrypt_private_key = encrypt(password, mnemonic_to_private_key(seed))
    with open(CYPHER_SECRETE_FILE, 'wb') as f:
        f.write(encrypt_private_key)

def initLocalAccount():
    if (not os.path.exists(CYPHER_SECRETE_FILE)):
        createLocalAccount()
    with open(CYPHER_SECRETE_FILE, 'rb') as f:
        encrypt_private_key = f.read()
    password = getpass("Enter your password to use local account: ")
    LOCAL_STORAGE['private_key'] = decrypt(password, encrypt_private_key)
    LOCAL_STORAGE['account'] = w3.eth.account.privateKeyToAccount(LOCAL_STORAGE['private_key'])

# https://pythontips.com/2013/08/04/args-and-kwargs-in-python-explained/
# buildSignSendTx(donator.functions.donate, 7, value=3, gas=99000)
def buildSignSendTx(fargs,*args,**kwargs):
    if not LOCAL_STORAGE['account']:
        initLocalAccount()
    print(kwargs)
    kwargs['nonce'] = web3.eth.getTransactionCount(LOCAL_STORAGE['account'].address)
    if (not 'chainId' in kwargs):
        kwargs['chainId'] = 1
    if (not 'gas' in kwargs):
        kwargs['gas'] = 200000
    if (not 'gasPrice' in kwargs):
        kwargs['gasPrice'] = web3.toWei('1', 'gwei')
    print(kwargs)
    txn = fargs(*args).buildTransaction(kwargs)
    signed_txn = web3.eth.account.signTransaction(txn, private_key=LOCAL_STORAGE['private_key'])
    web3.eth.sendRawTransaction(signed_txn.rawTransaction)

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

if __name__ == "__main__":
	initLocalAccount()
