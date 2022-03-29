# <ins>Guardian 2FA Contract</ins>

This contract allows users to lock their assets from a guardian address via the Guardian contract. This prevents the assets from being able to move, securing your assets and making them untransferable as long as the guardian address is safe.

## <ins>How does it work?</ins>
Lets focus on the `GuardianLite` contract. It contains a single mapping:
	mapping(address => address) public guardians;
Its utility is very simple. A user that holds NFTs on their wallet can assign a guardian to that address.
	mapping(NFT_owner => guardian)
This means a user can only have, at any given time, only one guardian guarding his assets. A guardian can guard as many addresses.