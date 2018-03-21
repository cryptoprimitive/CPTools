from init_web3 import *

BPFactory = web3.eth.contract(address = BPFactoryAddress, abi = loadABI('ABIs/BPFactory.json'))

# BPCreationFilter = BPFactory.eventFilter("NewBurnablePayment", {'fromBlock':GLOBAL_FROMBLOCK})
# BPCreationEvents = BPCreationFilter.get_all_entries()

# grantableUpdatesFilter = grantableUpdates.eventFilter("Update", {'fromBlock':GLOBAL_FROMBLOCK})
# allUpdates = grantableUpdatesFilter.get_all_entries()

def getBPCount():
    bp_count = BPFactory.call().getBPCount()
    print("Number of BPs:", bp_count)
    return bp_count
