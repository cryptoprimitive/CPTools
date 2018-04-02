# CryptoPrimitive Tools

A Python script that currently connects to the slutty CP server and shows the titles of all 'BPCreated' events.

This should serve as a good core for any other Python CryptoPrimitive contract interface.

To actually send eth/gas and interact with the contracts (i.e. create or commit to a BP), you'll need a personal account (see web3py docs). The only issue is that the server, as I said, is the slutty one.

... Don't put a lot of money on it. I have it in mainnet because developing on Ropsten is for pussies.

We are using the beta branch of Web3py as well as the [current version](https://github.com/cryptoprimitive/contracts/blob/master/BurnablePayment.sol) of the BP contract (Burnable Service upgrade).

## Usage

Install web3py beta, and required libraries

```
pip install -r requirements.txt
```

Add cptools to your project
```
git submodule add https://github.com/cryptoprimitive/CPTools.git cptools

# Update cptools to the latest code
git submodule update
```

Use cptools functions
```
# Start python cli
cd cptools
python # or python3
```

```python
from cptools import *
printUpdates()
```

Use additional utils speedup your development
```python
# To loads cptools from source code
# you need to include cptools dir in system path
import os, sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + '/../cptools')

from init_web3 import loadABI
from burnable_payment import *
from cptools import *

BP_ABI = loadABI("ContractName.json")
```
