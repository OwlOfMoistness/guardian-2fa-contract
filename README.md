# <ins>Guardian 2FA Contract</ins>

This contract allows users to lock their assets from a guardian address via the Guardian contract. This prevents the assets from being able to move, securing your assets and making them untransferable as long as the guardian address is safe.

## <ins>Prerequisites</ins>
The NFT contract you are interacting with must use the `LockRegistry` implementation that can be found here: https://github.com/OwlOfMoistness/erc721-lock-registry

## <ins>How does it work?</ins>
Lets focus on the `GuardianLite` contract. It contains a single mapping:
	
	mapping(address => address) public guardians;
Its utility is very simple. A user that holds NFTs on their wallet can assign a guardian to that address.
	
	mapping(NFT_owner => guardian)
This means a user can only have, at any given time, one guardian guarding his assets. A guardian can however guard as many addresses as they can.
Once the guardian has been set by a user, it can only be changed if the guardian renounces to its role. This prevents the user address to change guardians once set. If the user is compromised, we want to make sure the guardian cannot be changed.

With the guardian set, the guardian address can then call: 
 * `lockMany`: Allows to lock in place the token IDs held in the `_tokenIds` array, preventing them from being transferred
 * `unlockMany`: Allows to unlock the token IDs held in the `_tokenIds` array, potentially enabling them from beieng transferred (if lock count per token is 0)
 * `unlockManyAndTransfer`: Allows to unlock the token IDs held in the `tokenIds` array and trnasfer them to a `_recipient` address, all done atomically to keep assets secure at all times. Prerequisite is that the Guardian contract can move the tokens from the user address

The `Guardian` implementation behaves exactly like the `GuardianLite` implementation under the hood. The only differences are that it contains more logic for easier tracking management. It contains on-chain the array of users a guardian guards as well as data structure that holds all the tokens a user has locked. This is to prevent using event calls that seem to be unstable on polygon.
