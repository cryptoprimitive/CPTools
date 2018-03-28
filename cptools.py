from utils import *
from accounts import *
from grantable_updates import *

output = """functions:
newAccount() - Interactively creates a new account, optionally granting it 0.005 ETH of "seed funds" from another account
printUpdates() - prints all updates from the GrantableUpdates contract
postUpdate() - interactively posts message to the update feed
grantUpdateTo() - interactively grant update rights to another address for the GrantableUpdates contract
"""

print()
print(output)
print()

if __name__ == "__main__":
	printUpdates()
