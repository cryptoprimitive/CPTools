import json, utils

DEFAULT_ADDRESS = "0xf08E15fD318B3b73da8359Fc026F6Ce186F16486"
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
