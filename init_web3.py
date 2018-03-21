from web3 import Web3, HTTPProvider
import json, os

GLOBAL_FROMBLOCK = 4435671

BPFactoryAddress = "0xA225EbE73347dd87492868332F9B746bEb8499bb"
GrantableUpdatesAddress = "0xc9e8E364a009fcf35BD493b84959eDFf6caCCF72";

def loadABI(contract_json_filename):
    fullpath_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + contract_json_filename
    with open(fullpath_filename, 'r') as infile:
	        return json.load(infile)

web3 = Web3(HTTPProvider("https://gladly-golden-parrot.quiknode.io/8959339e-f0ab-4403-876f-1aed9422a44f/xh9aJBYpYQHEhu6q8jQrkA==/"))
