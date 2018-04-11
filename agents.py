from getpass import getpass
from mnemonic_utils import mnemonic_to_private_key
from mnemonic import Mnemonic
import os.path, json

from easy_web3_connection import easy_web3_connection

web3 = easy_web3_connection()
print("web3 connection configured.")

GLOBAL_FROMBLOCK = 4435671
AGENTS_FILENAME = "agents.json"

class Agent(json.JSONEncoder):
    def __init__(self, mnemonic):
        self.mnemonic = mnemonic
        self.priv = mnemonic_to_private_key(mnemonic)
        self.address = web3.eth.account.privateKeyToAccount(self.priv).address

    def default(self, o):
        return o.priv

agents = {}

def saveAgents():
    dictToSave = {}
    for name in agents:
        dictToSave[name] = agents[name].mnemonic

    with open(AGENTS_FILENAME, 'w') as f:
        json.dump(dictToSave, f)

def createAndSaveNewAgent(name, mnemonic=None, printMnemonic=False):
    if not mnemonic:
        mnemonic = Mnemonic('english').generate()
    if printMnemonic:
        print("Mnemonic of new agent:\n", mnemonic)
    newAgent = Agent(mnemonic)
    agents[name] = newAgent

    saveAgents()

def loadAgents():
    global agents
    with open(AGENTS_FILENAME, 'r') as f:
        agentMnemonics = json.load(f)

    for name in agentMnemonics:
        agents[name] = Agent(agentMnemonics[name])
