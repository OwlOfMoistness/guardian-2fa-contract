// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.2;

/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import "@owl/interfaces/ILockERC721.sol";

contract GuardianLite {

	ILockERC721 public immutable LOCKABLE;

	mapping(address => address) public pendingGuardians;
	mapping(address => address) public guardians;

	event GuardianSet(address indexed guardian, address indexed user);
	event GuardianRenounce(address indexed guardian, address indexed user);
	event PendingGuardianSet(address indexed pendingGuardian, address indexed user);


	constructor(address _lockable) public {
		LOCKABLE = ILockERC721(_lockable);
	}

	function proposeGuardian(address _guardian) external {
		require(guardians[msg.sender] == address(0), "Guardian set");
		require(msg.sender != _guardian, "Guardian must be a different wallet");

		pendingGuardians[msg.sender] = _guardian;
		emit PendingGuardianSet(_guardian, msg.sender);
	}

	function acceptGuardianship(address _protege) external {
		require(pendingGuardians[_protege] == msg.sender, "Not the pending guardian");

		pendingGuardians[_protege] = address(0);
		guardians[_protege] = msg.sender;
		emit GuardianSet(msg.sender, _protege);
	}

	function renounce(address _tokenOwner) external {
		require(guardians[_tokenOwner] == msg.sender, "!guardian");
		guardians[_tokenOwner] = address(0);
		emit GuardianRenounce(msg.sender, _tokenOwner);
	}

	function lockMany(uint256[] calldata _tokenIds) external {
		address owner = LOCKABLE.ownerOf(_tokenIds[0]);
		require(guardians[owner] == msg.sender, "!guardian");
		for (uint256 i = 0; i < _tokenIds.length; i++) {
			require(LOCKABLE.ownerOf(_tokenIds[i]) == owner, "!owner");
			LOCKABLE.lockId(_tokenIds[i]);
		}
	}

	function unlockMany(uint256[] calldata _tokenIds) external {
		address owner = LOCKABLE.ownerOf(_tokenIds[0]);
		require(guardians[owner] == msg.sender, "!guardian");
		for (uint256 i = 0; i < _tokenIds.length; i++) {
			require(LOCKABLE.ownerOf(_tokenIds[i]) == owner, "!owner");
			LOCKABLE.unlockId(_tokenIds[i]);
		}
	}

	function unlockManyAndTransfer(uint256[] calldata _tokenIds, address _recipient) external {
		address owner = LOCKABLE.ownerOf(_tokenIds[0]);
		require(guardians[owner] == msg.sender, "!guardian");
		for (uint256 i = 0; i < _tokenIds.length; i++) {
			require(LOCKABLE.ownerOf(_tokenIds[i]) == owner, "!owner");
			LOCKABLE.unlockId(_tokenIds[i]);
			LOCKABLE.safeTransferFrom(owner, _recipient, _tokenIds[i]);
		}
	}
}
