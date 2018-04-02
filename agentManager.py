from getpass import getpass
from utils import *
from init_web3 import *

from mnemonic_utils import mnemonic_to_private_key
from mnemonic import Mnemonic

import os.path
import json

AGENTSFILE = "agents.json"

class Agent:
    def __init__(self, address, password):
        self.address = address
        self.password = password
    
    def unlockAccount(self):
        web3.personal.unlockAccount(self.address, self.password)
    
    def lockAccount(self):
        web3.personal.lockAccount(self.address)
    
    def callContractFunction(self, function, *args, **kwargs):
        kwargs['from'] = self.address
        self.unlockAccount()
        txHash = getTxHashIfSuccessful(function(*args).transact(kwargs))
        self.lockAccount()
        print(txHash)

agents = {}

def newAgent():
    password = Mnemonic('english').generate()
    
    address = web3.personal.newAccount(password)
    
    return Agent(address, password)

def initAgents():
    global agents
    if (not os.path.exists(AGENTSFILE)):
        print("No agents file found. Creating file with one agent.")
        
        agents['main'] = newAgent()
        with open(AGENTSFILE, 'w') as f:
            json.dump({'main':{'address':agents['main'].address,'password':agents['main'].password}}, f)
    
    else:
        with open(AGENTSFILE, 'r') as f:
            agentsDict = json.load(f)
            agents = {}
            for name in agentsDict:
                agents[name] = Agent(agentsDict[name]['address'], agentsDict[name]['password'])
    
    print("Agents:")
    for agentName in agents:
        print(agents[agentName].address, "(",agentName,")")

def getAgent(name):
    return agents[name]