# CryptoPrimitive Tools

## Setup

Install required pip modules:

```
pip install -r requirements.txt
```

## Usage

While many of these Python scripts can be used on their own (utils, easy_web3_connection), this project is mainly aimed at supporting a single script, agents.py. We may add other user-facing scripts in the future.

## agents.py

Agents is designed as a quick wallet-like utility for common Ethereum operations. The following command exemplifies the intended utility:

`send anton $20`

Assuming the name 'anton' has been added with an address via the `addname` command, and that the agent in use has been funded with enough ether, this command will automatically:
- Convert $2 into the relevant ETH amount.
- sign the transaction with the local private key for the selected agent
- broadcast the transaction
- remember the txhash, so that the user can check on the mined status by running the `status` command.

The list of agents and names are preserved between script calls, meaning that the user can send payments to registered names immediately after starting the script, if they've set up the relevant name and funded the agents on a previous run.

We are currently extending this functionality to call contract methods and read contract state with the same ease.

The following info can be displayed anytime via the 'help' command:

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
