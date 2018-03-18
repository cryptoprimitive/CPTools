from web3 import Web3, HTTPProvider
import json

#addresses and ABIs
BPFactoryAddress = "0xA225EbE73347dd87492868332F9B746bEb8499bb"
with open(r'ABIs\BPFactory.json', 'r') as infile:
	BPFactoryABI = json.load(infile)



web3 = Web3(HTTPProvider("https://gladly-golden-parrot.quiknode.io/8959339e-f0ab-4403-876f-1aed9422a44f/xh9aJBYpYQHEhu6q8jQrkA==/"))

BPFactory = web3.eth.contract(address = BPFactoryAddress, abi = BPFactoryABI)

BPCreationFilter = BPFactory.eventFilter("NewBurnablePayment", {'fromBlock':4435671})

creationEvents = BPCreationFilter.get_all_entries()

print(creationEvents[0])

#get nonce with:  web3.eth.getTransactionCount(addr)