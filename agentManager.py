from getpass import getpass
from utils import *
from init_web3 import *

from mnemonic_utils import mnemonic_to_private_key
from mnemonic import Mnemonic

import os.path
import json

AGENTSFILE = "agents.json"

class Agent:
    def __init__(self, mnemonic):
        self.mnemonic = mnemonic
        self.priv = mnemonic_to_private_key(mnemonic)
        self.address = web3.eth.account.privateKeyToAccount(self.priv).address
    
    def callContractFunction(self, function, *args, **kwargs):
        kwargs['nonce'] = web3.eth.getTransactionCount(self.address)
        if (not 'chainId' in kwargs):
            kwargs['chainId'] = 1
        if (not 'gas' in kwargs):
            kwargs['gas'] = 200000
        if (not 'gasPrice' in kwargs):
            kwargs['gasPrice'] = web3.toWei('5', 'gwei')
        txn = function(*args).buildTransaction(kwargs)
        return txn
        kwargs['gas'] = web3.eth.estimateGas(txn)
        print(kwargs)
        txn = function(*args).buildTransaction(kwargs)
        signed_txn = web3.eth.account.signTransaction(txn, private_key=self.priv)
        print(getTxHashIfSuccessful(web3.eth.sendRawTransaction(signed_txn.rawTransaction)))

agents = {}

def initAgents():
    global agents
    if (not os.path.exists(AGENTSFILE)):
        print("No agents file found. Creating file with one agent.")
        mnemonic = Mnemonic('english').generate()
        shouldPrint = input("New agent created. Print seed phrase? (y/n) ")
        if (shouldPrint == 'y'):
            print(mnemonic)
        agents['main'] = Agent(mnemonic)
        with open(AGENTSFILE, 'w') as f:
            json.dump({'main':agents['main'].mnemonic}, f)
    
    else:
        with open(AGENTSFILE, 'r') as f:
            agentNamesToMnemonic = json.load(f)
            agents = {}
            for name in agentNamesToMnemonic:
                agents[name] = Agent(agentNamesToMnemonic[name])
    
    print("Agents:")
    for agentName in agents:
        print(agents[agentName].address, "(",agentName,")")

def getAgent(name):
    return agents[name]