from brownie import reverts

def test_guardian_set(nft_lock, guardian, minter_, accounts):
	caller = {'from':minter_}
	for i in range(5):
		nft_lock.mint(i + 1, caller)
	nft_lock.updateApprovedContracts([guardian], [True], caller)

	guardian.proposeGuardian(accounts[2], {'from':minter_})
	assert guardian.guardians(minter_) == '0x0000000000000000000000000000000000000000'
	with reverts('Not the pending guardian'):
		guardian.acceptGuardianship(minter_, {'from':accounts[3]})
	guardian.acceptGuardianship(minter_, {'from':accounts[2]})
	assert guardian.guardians(minter_) == accounts[2]
	with reverts('Guardian set'):
		guardian.proposeGuardian(accounts[3], {'from':minter_})

def test_guardian_lock(nft_lock, guardian, minter_, accounts):
	caller = {'from':minter_}
	with reverts('!guardian'):
		guardian.lockMany([1, 2, 3, 4, 5], {'from':accounts[1]})

	guardian.lockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	with reverts('ID already locked by caller'):
		guardian.lockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	for i in range(1, 6):
		assert nft_lock.lockCount(i) == 1

	locked = guardian.getLockedAssetsOfUsers(minter_)
	assert len(locked) == 5
	assert locked == [1, 2, 3, 4, 5]
	
	with reverts('Token is locked'):
		nft_lock.safeTransferFrom(minter_, minter_, 1, caller)

def test_guardian_unlock(nft_lock, guardian, minter_, accounts):
	with reverts('!guardian'):
		guardian.unlockMany([1, 2, 3, 4, 5], {'from':accounts[1]})
	guardian.unlockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	with reverts('ID not locked by caller'):
		guardian.unlockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	for i in range(1, 6):
		assert nft_lock.lockCount(i) == 0
	
	locked = guardian.getLockedAssetsOfUsers(minter_)
	assert len(locked) == 0
	assert locked == []

def test_guardian_lock_some(nft_lock, guardian, minter_, accounts):
	guardian.lockMany([5], {'from':accounts[2]})
	guardian.lockMany([3], {'from':accounts[2]})
	guardian.lockMany([1, 2], {'from':accounts[2]})

	locked = guardian.getLockedAssetsOfUsers(minter_)
	assert len(locked) == 4
	assert locked == [5, 3, 1, 2]

	guardian.lockMany([4], {'from':accounts[2]})
	assert guardian.getLockedAssetsOfUsers(minter_) == [5, 3, 1, 2, 4]

def test_guardian_unlock_some(nft_lock, guardian, minter_, accounts):
	guardian.unlockMany([1], {'from':accounts[2]})
	assert guardian.getLockedAssetsOfUsers(minter_) == [5, 3, 4, 2]
	guardian.unlockMany([5], {'from':accounts[2]})
	assert guardian.getLockedAssetsOfUsers(minter_) == [2, 3, 4]
	guardian.unlockMany([2, 4], {'from':accounts[2]})
	assert guardian.getLockedAssetsOfUsers(minter_) == [3]
	guardian.unlockMany([3], {'from':accounts[2]})

def test_guardian_renounce(nft_lock, guardian, minter_, accounts):
	guardian.lockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	with reverts('!guardian'):
		guardian.renounce(minter_, {'from':accounts[1]})
	guardian.renounce(minter_, {'from':accounts[2]})

def test_guardian_new_guardian(nft_lock, guardian, minter_, accounts):
	caller = {'from':minter_}
	guardian.proposeGuardian(accounts[1], {'from':minter_})
	guardian.acceptGuardianship(minter_, {'from':accounts[1]})
	guardian.unlockMany([1, 2, 3, 4, 5], {'from':accounts[1]})
	for i in range(1, 6):
		assert nft_lock.lockCount(i) == 0
	nft_lock.safeTransferFrom(minter_, minter_, 1, caller)
	guardian.lockMany([1, 2, 3, 4, 5], {'from':accounts[1]})

def test_guardian_retrieve_with_extra_lock(nft_lock, guardian, minter_, accounts):
	caller = {'from':minter_}
	nft_lock.setApprovalForAll(guardian, True, caller)
	nft_lock.updateApprovedContracts([accounts[7]], [True], caller)
	for i in range(5):
		nft_lock.lockId(i + 1, {'from':accounts[7]})
	with reverts('Token is locked'):
		guardian.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})
	for i in range(5):
		nft_lock.unlockId(i + 1, {'from':accounts[7]})
	guardian.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})
	with reverts('!guardian'):
		guardian.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})
	assert nft_lock.balanceOf(accounts[4]) == 5

def test_guardian_retrieve_not_locked(nft_lock, guardian, minter_, accounts):
	for i in range(5):
		nft_lock.safeTransferFrom(accounts[4], minter_, i + 1, {'from':accounts[4]})

	with reverts('ID not locked by caller'):
		guardian.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})
	guardian.lockMany([1, 2, 3, 4, 5], {'from':accounts[1]})
	guardian.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})

def test_guarduan_many_users(nft_lock, guardian, minter_, accounts):
	for i in range(3, 8):
		guardian.proposeGuardian(accounts[2], {'from':accounts[i]})
		guardian.acceptGuardianship(accounts[i], {'from':accounts[2]})
	assert guardian.guardianUserCount(accounts[2]) == 5
	assert guardian.getProtegesFromGuardian(accounts[2]) == [accounts[3],accounts[4],accounts[5],accounts[6],accounts[7]]
	guardian.renounce(accounts[5], {'from':accounts[2]})
	assert guardian.guardianUserCount(accounts[2]) == 4
	assert guardian.getProtegesFromGuardian(accounts[2]) == [accounts[3],accounts[4],accounts[7],accounts[6]]

	guardian.renounce(accounts[3], {'from':accounts[2]})
	assert guardian.guardianUserCount(accounts[2]) == 3
	assert guardian.getProtegesFromGuardian(accounts[2]) == [accounts[6],accounts[4],accounts[7]]

def test_guardian_same_as_sender(guardian, accounts):
	with reverts('Guardian must be a different wallet'):
		guardian.proposeGuardian(accounts[5], {'from':accounts[5]})