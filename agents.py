from getpass import getpass
from mnemonic_utils import mnemonic_to_private_key
from mnemonic import Mnemonic
from urllib.request import urlopen
from pprint import pprint
import os.path, json, re, pyperclip

import utils
from easy_web3_connection import easy_web3_connection

web3 = easy_web3_connection()
web3.eth.enable_unaudited_features()
print("web3 connection configured.\n")

GLOBAL_FROMBLOCK = 4435671
AGENTS_FILENAME = "agents.json"
NAMES_FILENAME = "names.json"

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
names = {}
contracts = {}

lastTransactionHash = None

waitForTx = True

def ethPriceFromCMC():
    url = "https://api.coinmarketcap.com/v1/ticker/ethereum/"
    returned = urlopen(url)
    decoded = json.loads(returned.read())
    return float(decoded[0]['price_usd'])

def usdToEth(usd):
    return usd / ethPriceFromCMC()

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
        print("Mnemonic of new agent '" + name + "':\n", mnemonic, '\n')
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
        print("No agents file found. Initializing with a 'main' agent; this will be autoloaded on the next run.")
        createAndSaveNewAgent(name='main', printMnemonic=True)

def saveNames():
    with open(NAMES_FILENAME, 'w') as f:
        json.dump(names, f)

def createAndSaveNewName(name, address):
    global names
    names[name] = address

    saveNames()

def loadNames():
    global names
    try:
        with open(NAMES_FILENAME, 'r') as f:
            names = json.load(f)
    except FileNotFoundError:
        names = {}

def nameToAddress(recipientStr):
    if web3.isAddress(recipientStr):
        return recipientStr
    elif recipientStr in agents:
        return agents[recipientStr].address
    elif recipientStr in names:
        return names[recipientStr]
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
    elif unitStr == "$":
        amountNumber = usdToEth(amountNumber)
        unitStr = 'ether'

    #pass to web3 to translate to wei
    return web3.toWei(amountNumber, unitStr)

def trackTx(commandString, txHash):
    if waitForTx:
        print("Waiting to mine '"+commandString+"': ", web3.toHex(txHash))
        web3.eth.waitForTransactionReceipt(txHash)
        print("Mined!")
    else:
        print("txHash for '"+commandString+"': ", web3.toHex(txHash))

def cmd_gp(args):
    global gasPrice
    if len(args) > 0:
        gasPrice = amountStrToWei(args[0])
    else:
        print("Current gas price:", gasPrice)

def cmd_send(args):
    global lastTransactionHash
    transaction = {
        'to': nameToAddress(args[0]),
        'value': amountStrToWei(args[1]),
        'nonce': web3.eth.getTransactionCount(agents[selectedAgent].address),
        'chainId': 1,
        'gasPrice': gasPrice
    }
    transaction['gas'] = web3.eth.estimateGas(transaction)

    signed = web3.eth.account.signTransaction(transaction, agents[selectedAgent].priv)

    lastTransactionHash = web3.eth.sendRawTransaction(signed.rawTransaction)

    return lastTransactionHash

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

def cmd_addname(args):
    if not web3.isAddress(args[1]):
        raise InputError("'"+args[1]+"' is not a valid address")

    checksummed = web3.toChecksumAddress(args[1])
    createAndSaveNewName(args[0], checksummed)

    print("Name '"+args[0]+"' added with address '"+checksummed+"'")

def cmd_names():
    print("names:")
    for name in names:
        print(name+":", names[name])

def cmd_use(args):
    global selectedAgent
    if not args[0] in agents:
        raise InputError("'"+args[0]+"' not in agents")
    selectedAgent = args[0]

def cmd_status(commandArgs):
    if len(commandArgs) == 0:
        txHash = lastTransactionHash
    else:
        txHash = commandArgs[0]
    tx = web3.eth.getTransaction(txHash)

    if tx.blockNumber:
        print("Transaction has been mined in block",tx.blockNumber)
    else:
        print("Transaction has not yet been mined.")

def cmd_addcontract(commandArgs):
    global contracts

    name = commandArgs[0]

    contract = utils.contractInstanceFromAddress(web3, commandArgs[1])

    contracts[name] = contract

def contract_function_call(contractName, functionName, args, amountStr='0E'):
    contract = contracts[contractName]
    argTypes = utils.getContractFunctionArgTypes(contract, functionName)

    for i in range(len(argTypes)):
        if argTypes[i].startswith("uint"):
            args[i] = int(args[i])

    tx =   {'value': amountStrToWei(amountStr),
            'nonce': web3.eth.getTransactionCount(agents[selectedAgent].address),
            'chainId': 1,
            'gasPrice': web3.toWei('5', 'gwei')}

    tx['gas'] = contract.functions.__dict__[functionName](*args).estimateGas()*2

    tx = contract.functions.__dict__[functionName](*args).buildTransaction(tx)

    pprint(tx)

    signed = web3.eth.account.signTransaction(tx, agents[selectedAgent].priv)

    lastTransactionHash = web3.eth.sendRawTransaction(signed.rawTransaction)

    return lastTransactionHash

def main():
    global agents
    global names
    global selectedAgent
    global gasPrice

    loadAgentsOrInitializeAgentsFile()
    loadNames()

    selectedAgent = 'main'

    print("Setting gasPrice to 5 gwei.\n")
    gasPrice = web3.toWei(5,'gwei')

    print("Type \"help\" for info on commands")

    while True:
        try:
            commandString = input(selectedAgent + ' > ')

            if commandString[0] == '~':
                commandArgs = commandString[1:].split(' ')
                trackTx(commandString, contract_function_call(commandArgs[0], commandArgs[1], commandArgs[2:]))

            commandName = commandString.split(' ')[0]
            commandArgs = commandString.split(' ')[1:]

            if commandName == 'help':
                print(helpMessage)

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

            if commandName == "addname":
                if len(commandArgs) != 2:
                    raise InputError("2 arguments needed (name, address) for addname command")
                cmd_addname(commandArgs)

            if commandName == "names":
                cmd_names()

            if commandName == "use":
                if len(commandArgs) != 1:
                    raise InputError("1 argument needed (agent-name) for use command")
                cmd_use(commandArgs)

            if commandName == "status":
                cmd_status(commandArgs)

            if commandName == "addcontract":
                if len(commandArgs) != 2:
                    raise InputError("2 argument needed (name, address) for addcontract command")
                cmd_addcontract(commandArgs)

        except InputError as e:
            print("Error:", str(e))

        except ValueError as e:
            if str(e)[:16] == "{'code': -32000,": # Hacky. I wish web3py raised something more specific than a ValueError.
                print("Error: insufficient funds")
            else:
                raise

helpMessage = """

Commands:

- help: show this message
- q: quit
- gp [value]: set gas price to [value]
- send [target] [value]: send [value] to [target]
- newagent [seed-phrase]: if [seed-phrase] is not supplied, create new agent and print seed phrase. Otherwise, restore agent from seed and add.
- agents: print a list of all loaded agents
- copy [agent]: copy address of agent to clipboard. If [agent] is not supplied, use currently selected agent.
- balance [agent]: print balance of [agent]. If [agent] is not supplied, use currently selected agent.
- addname [name] [address]: add [address] to addressbook under [name].
- names: print all names in addressbook.
- use [agent]: select [agent].
- status [txhash]: print whether transaction has been mined. If [txhash] is not supplied AND a method had been called previously, check the status of that call.
- addcontract [name] [address]: add a named contract. Then call contract methods with ~contractname.functionname(args).

Any time an address is needed, the name of an agent or addressbook entry can be used instead.
Any time an amount is needed, it can be specified in e (ether), w (wei), gw (gigawei) or $ (USD). If $ is used, coinmarketcap.com is queried for the exchange rate.
(As an example of the two above, assuming a name "anton" has been added: "send anton $2" will convert $2 to the appropriate amount and send it to the address logged for "anton").
"""

if __name__ == "__main__":
    main()
