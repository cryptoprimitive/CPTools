from utils import loadABI
from init_web3 import *

BPFactoryAddress = "0xA225EbE73347dd87492868332F9B746bEb8499bb"
BPFactory = web3.eth.contract(address = BPFactoryAddress, abi = loadABI('ABIs/BPFactory.json'))

# BPCreationFilter = BPFactory.eventFilter("NewBurnablePayment", {'fromBlock':GLOBAL_FROMBLOCK})
# BPCreationEvents = BPCreationFilter.get_all_entries()

# grantableUpdatesFilter = grantableUpdates.eventFilter("Update", {'fromBlock':GLOBAL_FROMBLOCK})
# allUpdates = grantableUpdatesFilter.get_all_entries()

def getBPCount():
    bp_count = BPFactory.functions.getBPCount().call()
    return bp_count

if __name__ == "__main__":
    print("Number of BP contracts:", getBPCount())
