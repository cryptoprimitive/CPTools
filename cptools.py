from web3 import Web3, HTTPProvider
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

BPCreationFilter = BPFactory.eventFilter("NewBurnablePayment", {'fromBlock':GLOBAL_FROMBLOCK})
BPCreationEvents = BPCreationFilter.get_all_entries()

grantableUpdatesFilter = grantableUpdates.eventFilter("Update", {'fromBlock':GLOBAL_FROMBLOCK})
allUpdates = grantableUpdatesFilter.get_all_entries()

print("Updates from the GrantableUpdates contract:")
for update in allUpdates:
	print(str(update.args.agent) + ": " + update.args.data)
print()

output = """Defined in cptools.*:
- web3 (initialized with connection to the CP "slutty" QuikNode)
- BPFactory and grantableUpdates (web3 contract instances) pointed to mainnet instance of contracts in https://github.com/cryptoprimitive/contracts
- BPCreationFilter (filter for BP 'NewBurnablePayment' events)
- BPCreationEvents (list of all BPs created at time of cptools initialization)
"""

print(output)