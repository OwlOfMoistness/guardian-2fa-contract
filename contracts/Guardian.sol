// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.2;

/*
 *     ,_,
 *    (',')
 *    {/"\}
 *    -"-"-
 */

import "@owl/interfaces/ILockERC721.sol";

contract Guardian {

	struct UserData {
		address guardian;
		uint256[] lockedAssets;
		mapping(uint256 => uint256) assetToIndex;
	}

	ILockERC721 public immutable LOCKABLE;

	mapping(address => address) public guardians;
	mapping(address => UserData) public userData;
	mapping(address => mapping(uint256 => address)) public guardianToUsers;
	mapping(address => mapping(address => uint256)) public guardianToUserIndex;
	mapping(address => uint256) public guardianUserCount;

	event GuardianSet(address indexed guardian, address indexed user);
	event GuardianRenounce(address indexed guardian, address indexed user);

	constructor(address _lockable) public {
		LOCKABLE = ILockERC721(_lockable);
	}

	function setGuardian(address _guardian) external {
		require(guardians[msg.sender] == address(0), "Guardian set");
		require(msg.sender != _guardian, "Guardian must be a different wallet");

		guardians[msg.sender] = _guardian;
		userData[msg.sender].guardian = _guardian;
		_pushGuardianrray(_guardian, msg.sender);
		emit GuardianSet(_guardian, msg.sender);
	}

	function renounce(address _protege) external {
		require(guardians[_protege] == msg.sender, "!guardian");

		guardians[_protege] = address(0);
		userData[_protege].guardian = address(0);
		_popGuardianrray(msg.sender, _protege);
		emit GuardianRenounce(msg.sender, _protege);
	}

	function lockMany(uint256[] calldata _tokenIds) external {
		address owner = LOCKABLE.ownerOf(_tokenIds[0]);
		require(guardians[owner] == msg.sender, "!guardian");

		UserData storage _userData = userData[owner];
		uint256 len = _userData.lockedAssets.length;
		for (uint256 i = 0; i < _tokenIds.length; i++) {
			require(LOCKABLE.ownerOf(_tokenIds[i]) == owner, "!owner");
			LOCKABLE.lockId(_tokenIds[i]);
			_pushTokenInArray(_userData, _tokenIds[i], len + i);
		}
	}

	function unlockMany(uint256[] calldata _tokenIds) external {
		address owner = LOCKABLE.ownerOf(_tokenIds[0]);
		require(guardians[owner] == msg.sender, "!guardian");

		UserData storage _userData = userData[owner];
		uint256 len = _userData.lockedAssets.length;
		for (uint256 i = 0; i < _tokenIds.length; i++) {
			require(LOCKABLE.ownerOf(_tokenIds[i]) == owner, "!owner");
			LOCKABLE.unlockId(_tokenIds[i]);
			_popTokenFromArray(_userData, _tokenIds[i], len--);
		}
	}

	function unlockManyAndTransfer(uint256[] calldata _tokenIds, address _recipient) external {
		address owner = LOCKABLE.ownerOf(_tokenIds[0]);
		require(guardians[owner] == msg.sender, "!guardian");

		UserData storage _userData = userData[owner];
		uint256 len = _userData.lockedAssets.length;
		for (uint256 i = 0; i < _tokenIds.length; i++) {
			require(LOCKABLE.ownerOf(_tokenIds[i]) == owner, "!owner");
			LOCKABLE.unlockId(_tokenIds[i]);
			LOCKABLE.safeTransferFrom(owner, _recipient, _tokenIds[i]);
			_popTokenFromArray(_userData, _tokenIds[i], len--);
		}
	}

	function getLockedAssetsOfUsers(address _user) external view returns(uint256[] memory lockedAssets) {
		uint256 len = userData[_user].lockedAssets.length;
		lockedAssets = new uint256[](len);
		for (uint256 i = 0; i < len; i++) {
			lockedAssets[i] = userData[_user].lockedAssets[i];
		}
	}

	function getLockedAssetsOfUsers(address _user, uint256 _startIndex, uint256 _maxLen) external view returns(uint256[] memory lockedAssets) {
		uint256 len = userData[_user].lockedAssets.length;

		_maxLen = (len - _startIndex) < _maxLen  ? len - _startIndex : _maxLen;
		lockedAssets = new uint256[](_maxLen);
		for (uint256 i = _startIndex; i < _startIndex + _maxLen; i++) {
			lockedAssets[i] = userData[_user].lockedAssets[i];
		}
	}

	function getProtegesFromGuardian(address _guardian) external view returns(address[] memory proteges) {
		uint256 len = guardianUserCount[_guardian];
		proteges = new address[](len);
		for (uint256 i = 0; i < len; i++) {
			proteges[i] = guardianToUsers[_guardian][i];
		}
	}

	function _pushTokenInArray(UserData storage _userData, uint256 _token, uint256 _index) internal {
		_userData.lockedAssets.push(_token);
		_userData.assetToIndex[_token] = _index;
	}

	function _popTokenFromArray(UserData storage _userData, uint256 _token, uint256 _len) internal {
		uint256 index = _userData.assetToIndex[_token];
		delete _userData.assetToIndex[_token];
		uint256 lastId = _userData.lockedAssets[_len - 1];
		_userData.assetToIndex[lastId] = index;
		_userData.lockedAssets[index] = lastId;
		_userData.lockedAssets.pop();
	}

	function _pushGuardianrray(address _guardian, address _protege) internal {
		uint256 count = guardianUserCount[_guardian];
		guardianToUsers[_guardian][count] = _protege;
		guardianToUserIndex[_guardian][_protege] = count;
		guardianUserCount[_guardian]++;
	}

	function _popGuardianrray(address _guardian, address _protege) internal {
		uint256 index = guardianToUserIndex[_guardian][_protege];
		delete guardianToUserIndex[_guardian][_protege];
		guardianToUsers[_guardian][index] = guardianToUsers[_guardian][guardianUserCount[_guardian] - 1];
		delete guardianToUsers[_guardian][guardianUserCount[_guardian] - 1];
		guardianUserCount[_guardian]--;
	}
}
