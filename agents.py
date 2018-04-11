from getpass import getpass
from mnemonic_utils import mnemonic_to_private_key
from mnemonic import Mnemonic
import os.path, json, re, pyperclip

from easy_web3_connection import easy_web3_connection

web3 = easy_web3_connection()
print("web3 connection configured.")

GLOBAL_FROMBLOCK = 4435671
AGENTS_FILENAME = "agents.json"

class InputError(ValueError):
    pass

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

def loadAgentsOrInitializeAgentsFile():
    try:
        loadAgents()
    except FileNotFoundError:
        createAndSaveNewAgent('main')


def nameToAddress(recipientStr):
    if web3.isAddress(recipientStr):
        return recipientStr
    elif recipientStr in agents:
        return agents[recipientStr].address
    else:
        raise InputError("'"+recipientStr+"' is not a valid address or name")

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def amountStrToWei(amountStr):
    #pull out number, and check for right format
    amountComponents = re.split('([\d.]+)', amountStr)
    if len(amountComponents) != 3 or amountComponents[1] == '':
        raise InputError("Incorrectly formatted amount: " + amountStr)
    amountNumber = num(amountComponents[1])

    #pull out unit str
    if amountComponents[0] == '' and amountComponents[2] == '':
        raise InputError("Must specify unit for amount: " + amountStr)
    elif amountComponents[0] != '':
        unitStr = amountComponents[0]
    elif amountComponents[2] != '':
        unitStr = amountComponents[2]

    #intermediate processing before passing to web3.toWei
    if unitStr.lower() == 'e' or unitStr.lower() == 'eth':
        unitStr = 'ether'
    elif unitStr.lower() == 'w' or unitStr.lower() == 'wei':
        unitStr = 'wei'
    elif unitStr.lower() == 'gw' or unitStr.lower() == 'gwei':
        unitStr = 'gwei'

    #pass to web3 to translate to wei
    return web3.toWei(amountNumber, unitStr)

def trackTx(commandString, txHash):
    print("txHash for '"+commandString+"': ", web3.toHex(txHash))

def cmd_gp(args):
    global gasPrice
    if len(args) > 0:
        gasPrice = amountStrToWei(args[0])
    else:
        print("Current gas price:", gasPrice)

def cmd_send(args):
    transaction = {
        'to': nameToAddress(args[0]),
        'value': amountStrToWei(args[1]),
        'nonce': web3.eth.getTransactionCount(agents[selectedAgent].address),
        'chainId': 1,
        'gasPrice': gasPrice
    }
    transaction['gas'] = web3.eth.estimateGas(transaction)

    signed = web3.eth.account.signTransaction(transaction, agents[selectedAgent].priv)

    return web3.eth.sendRawTransaction(signed.rawTransaction)

def cmd_newagent(args):
    if len(args) == 1:
        createAndSaveNewAgent(name=args[0], printMnemonic=True)
    elif len(args) == 2:
        createAndSaveNewAgent(args[0], args[1])

def cmd_agents():
    print("agents:")
    for name in agents:
        print(name+":", agents[name].address)

def cmd_copyaddr(args):
    if len(args) > 0:
        addr = nameToAddress(args[0])
    else:
        addr = agents[selectedAgent].address
    pyperclip.copy(addr)

    print("'"+addr+"' copied to clipboard.")

def cmd_balance(args):
    if len(args) > 0:
        addr = nameToAddress(args[0])
    else:
        addr = agents[selectedAgent].address

    print(web3.fromWei(web3.eth.getBalance(addr), 'ether'))

def main():
    global agents
    global selectedAgent
    global gasPrice

    loadAgentsOrInitializeAgentsFile()
    selectedAgent = 'main'

    print("Setting gasPrice to 5 gwei.")
    gasPrice = web3.toWei(5,'gwei')

    while True:
        try:
            commandString = input('main > ')
            commandName = commandString.split(' ')[0]
            commandArgs = commandString.split(' ')[1:]

            if commandName == 'q':
                return

            if commandName == 'gp':
                cmd_gp(commandArgs)

            if commandName == 'send':
                if len(commandArgs) != 2:
                    raise InputError("2 arguments needed (recipient, amount) for send command")
                trackTx(commandString, cmd_send(commandArgs))

            if commandName == 'newagent':
                if len(commandArgs) < 1:
                    raise InputError("1-2 arguments needed (name, [mnemonic-seed]) for newagent command")
                cmd_newagent(commandArgs)

            if commandName == 'agents':
                cmd_agents()

            if commandName == 'copy':
                cmd_copyaddr(commandArgs)

            if commandName == "balance":
                cmd_balance(commandArgs)

        except InputError as e:
            print("Error:", str(e))

if __name__ == "__main__":
    main()
