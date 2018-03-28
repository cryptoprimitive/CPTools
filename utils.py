import json, os
from urllib.request import urlopen
# pip install pycrypto
from Crypto.Cipher import XOR
import base64

def encrypt(key, plaintext):
  cipher = XOR.new(key)
  return base64.b64encode(cipher.encrypt(plaintext))

def decrypt(key, ciphertext):
  cipher = XOR.new(key)
  return cipher.decrypt(base64.b64decode(ciphertext))

def loadABI(contract_json_filename):
    fullpath_filename = os.path.dirname(os.path.realpath(__file__)) + '/' + contract_json_filename
    with open(fullpath_filename, 'r') as infile:
        data = json.load(infile)
    if isinstance(data, dict) and data["abi"]:
        return data["abi"]
    else:
        return data

def fetchABIFromEtherscan(address):
	html = urlopen("https://api.etherscan.io/api?module=contract&action=getabi&address=" + address + "&apikey=9TBD9VA31ASIGDRID7SBASUHPAHJGPKT17")
	result = json.loads(html.read())
	if (result['status'] == '1'):
		return json.loads(result['result'])
	else:
		return None

def contractInstanceFromAddress(address):
	abi = fetchABIFromEtherscan(address)
	return web3.eth.contract(address = address, abi = abi)

def getTxHashIfSuccessful(txHash):
	isBytes = isinstance(txHash, bytes)
	if (isBytes):
		return web3.toHex(txHash)
	else:
		print("Error! expected txhash, but got a " + str(type(txHash)))
		return False
