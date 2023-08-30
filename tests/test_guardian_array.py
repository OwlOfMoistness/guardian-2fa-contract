from brownie import reverts

def test_guardian_set(nft_lock, guardian_arr, minter_, accounts):
	caller = {'from':minter_}
	for i in range(5):
		nft_lock.mint(i + 1, caller)
	nft_lock.updateApprovedContracts([guardian_arr], [True], caller)

	guardian_arr.proposeGuardian(accounts[2], {'from':minter_})
	assert guardian_arr.guardians(minter_) == '0x0000000000000000000000000000000000000000'
	with reverts('Not the pending guardian'):
		guardian_arr.acceptGuardianship(minter_, {'from':accounts[3]})
	guardian_arr.acceptGuardianship(minter_, {'from':accounts[2]})
	assert guardian_arr.guardians(minter_) == accounts[2]
	with reverts('Guardian set'):
		guardian_arr.proposeGuardian(accounts[3], {'from':minter_})

def test_guardian_lock(nft_lock, guardian_arr, minter_, accounts):
	caller = {'from':minter_}
	with reverts('!guardian'):
		guardian_arr.lockMany([1, 2, 3, 4, 5], {'from':accounts[1]})

	guardian_arr.lockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	with reverts('ID already locked by caller'):
		guardian_arr.lockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	for i in range(1, 6):
		assert nft_lock.lockCount(i) == 1

	locked = guardian_arr.getLockedAssetsOfUsers(minter_)
	assert len(locked) == 5
	assert locked == [1, 2, 3, 4, 5]
	
	with reverts('Token is locked'):
		nft_lock.safeTransferFrom(minter_, minter_, 1, caller)

def test_guardian_unlock(nft_lock, guardian_arr, minter_, accounts):
	with reverts('!guardian'):
		guardian_arr.unlockMany([1, 2, 3, 4, 5], {'from':accounts[1]})
	guardian_arr.unlockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	with reverts('ID not locked by caller'):
		guardian_arr.unlockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	for i in range(1, 6):
		assert nft_lock.lockCount(i) == 0
	
	locked = guardian_arr.getLockedAssetsOfUsers(minter_)
	assert len(locked) == 0
	assert locked == []

def test_guardian_lock_some(nft_lock, guardian_arr, minter_, accounts):
	guardian_arr.lockMany([5], {'from':accounts[2]})
	guardian_arr.lockMany([3], {'from':accounts[2]})
	guardian_arr.lockMany([1, 2], {'from':accounts[2]})

	locked = guardian_arr.getLockedAssetsOfUsers(minter_)
	assert len(locked) == 4
	assert locked == [5, 3, 1, 2]

	guardian_arr.lockMany([4], {'from':accounts[2]})
	assert guardian_arr.getLockedAssetsOfUsers(minter_) == [5, 3, 1, 2, 4]

def test_guardian_unlock_some(nft_lock, guardian_arr, minter_, accounts):
	guardian_arr.unlockMany([1], {'from':accounts[2]})
	assert guardian_arr.getLockedAssetsOfUsers(minter_) == [5, 3, 4, 2]
	guardian_arr.unlockMany([5], {'from':accounts[2]})
	assert guardian_arr.getLockedAssetsOfUsers(minter_) == [2, 3, 4]
	guardian_arr.unlockMany([2, 4], {'from':accounts[2]})
	assert guardian_arr.getLockedAssetsOfUsers(minter_) == [3]
	guardian_arr.unlockMany([3], {'from':accounts[2]})

def test_guardian_renounce(nft_lock, guardian_arr, minter_, accounts):
	guardian_arr.lockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	with reverts('!guardian'):
		guardian_arr.renounce(minter_, {'from':accounts[1]})
	guardian_arr.renounce(minter_, {'from':accounts[2]})

def test_guardian_new_guardian(nft_lock, guardian_arr, minter_, accounts):
	caller = {'from':minter_}
	guardian_arr.proposeGuardian(accounts[1], {'from':minter_})
	guardian_arr.acceptGuardianship(minter_, {'from':accounts[1]})
	guardian_arr.unlockMany([1, 2, 3, 4, 5], {'from':accounts[1]})
	for i in range(1, 6):
		assert nft_lock.lockCount(i) == 0
	nft_lock.safeTransferFrom(minter_, minter_, 1, caller)
	guardian_arr.lockMany([1, 2, 3, 4, 5], {'from':accounts[1]})

def test_guardian_retrieve_with_extra_lock(nft_lock, guardian_arr, minter_, accounts):
	caller = {'from':minter_}
	nft_lock.setApprovalForAll(guardian_arr, True, caller)
	nft_lock.updateApprovedContracts([accounts[7]], [True], caller)
	for i in range(5):
		nft_lock.lockId(i + 1, {'from':accounts[7]})
	with reverts('Token is locked'):
		guardian_arr.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})
	for i in range(5):
		nft_lock.unlockId(i + 1, {'from':accounts[7]})
	guardian_arr.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})
	with reverts('!guardian'):
		guardian_arr.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})
	assert nft_lock.balanceOf(accounts[4]) == 5

def test_guardian_retrieve_not_locked(nft_lock, guardian_arr, minter_, accounts):
	for i in range(5):
		nft_lock.safeTransferFrom(accounts[4], minter_, i + 1, {'from':accounts[4]})

	with reverts('ID not locked by caller'):
		guardian_arr.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})
	guardian_arr.lockMany([1, 2, 3, 4, 5], {'from':accounts[1]})
	guardian_arr.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})

def test_guarduan_many_users(nft_lock, guardian_arr, minter_, accounts):
	for i in range(3, 8):
		guardian_arr.proposeGuardian(accounts[2], {'from':accounts[i]})
		guardian_arr.acceptGuardianship(accounts[i], {'from':accounts[2]})
	assert guardian_arr.guardianUserCount(accounts[2]) == 5
	assert guardian_arr.getProtegesFromGuardian(accounts[2]) == [accounts[3],accounts[4],accounts[5],accounts[6],accounts[7]]
	guardian_arr.renounce(accounts[5], {'from':accounts[2]})
	assert guardian_arr.guardianUserCount(accounts[2]) == 4
	assert guardian_arr.getProtegesFromGuardian(accounts[2]) == [accounts[3],accounts[4],accounts[7],accounts[6]]

	guardian_arr.renounce(accounts[3], {'from':accounts[2]})
	assert guardian_arr.guardianUserCount(accounts[2]) == 3
	assert guardian_arr.getProtegesFromGuardian(accounts[2]) == [accounts[6],accounts[4],accounts[7]]

def test_guardian_same_as_sender(guardian_arr, accounts):
	with reverts('Guardian must be a different wallet'):
		guardian_arr.proposeGuardian(accounts[5], {'from':accounts[5]})