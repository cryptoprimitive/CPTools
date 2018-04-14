import json, utils

DEFAULT_ADDRESS = "0x9EeDC96E06C34c77627170E1bE7C0844A6CbAF5f"
ABI = utils.loadABI('ABIs/InterfaceLog.abi')
DEFAULT_FROMBLOCK = 5422115

class InterfaceLogInterface:
    def __init__(self, web3, address=DEFAULT_ADDRESS, defaultFromblock = DEFAULT_FROMBLOCK):
        self.contract = web3.eth.contract(address = address, abi = ABI)
        self.defaultFromblock = defaultFromblock

    def fetchInterface(self, id, fromBlock=None):
        if fromBlock is None:
            fromBlock = self.defaultFromblock

        filter = self.contract.eventFilter("Log", {'fromBlock': fromBlock})
        matches = filter.get_all_entries()

        if len(matches) == 0:
            return None
        else:
            return matches[0]
