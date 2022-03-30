from brownie import reverts

def test_guardian_set(nft_lock, guardian_lite, minter_, accounts):
	caller = {'from':minter_}
	for i in range(5):
		nft_lock.mint(i + 1, caller)
	nft_lock.updateApprovedContracts([guardian_lite], [True], caller)

	guardian_lite.setGuardian(accounts[2], {'from':minter_})
	assert guardian_lite.guardians(minter_) == accounts[2]
	with reverts('Guardian set'):
		guardian_lite.setGuardian(accounts[3], {'from':minter_})

def test_guardian_lock(nft_lock, guardian_lite, minter_, accounts):
	caller = {'from':minter_}
	with reverts('!guardian'):
		guardian_lite.lockMany([1, 2, 3, 4, 5], {'from':accounts[1]})

	guardian_lite.lockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	with reverts('ID already locked by caller'):
		guardian_lite.lockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	for i in range(1, 6):
		assert nft_lock.lockCount(i) == 1
	
	with reverts('Token is locked'):
		nft_lock.safeTransferFrom(minter_, minter_, 1, caller)

def test_guardian_unlock(nft_lock, guardian_lite, minter_, accounts):
	with reverts('!guardian'):
		guardian_lite.unlockMany([1, 2, 3, 4, 5], {'from':accounts[1]})
	guardian_lite.unlockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	with reverts('ID not locked by caller'):
		guardian_lite.unlockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	for i in range(1, 6):
		assert nft_lock.lockCount(i) == 0

def test_guardian_lock_some(nft_lock, guardian_lite, minter_, accounts):
	guardian_lite.lockMany([5], {'from':accounts[2]})
	guardian_lite.lockMany([3], {'from':accounts[2]})
	guardian_lite.lockMany([1, 2], {'from':accounts[2]})

	guardian_lite.lockMany([4], {'from':accounts[2]})

def test_guardian_unlock_some(nft_lock, guardian_lite, minter_, accounts):
	guardian_lite.unlockMany([1], {'from':accounts[2]})
	guardian_lite.unlockMany([5], {'from':accounts[2]})
	guardian_lite.unlockMany([2, 4], {'from':accounts[2]})
	guardian_lite.unlockMany([3], {'from':accounts[2]})

def test_guardian_renounce(nft_lock, guardian_lite, minter_, accounts):
	guardian_lite.lockMany([1, 2, 3, 4, 5], {'from':accounts[2]})
	with reverts('!guardian'):
		guardian_lite.renounce(minter_, {'from':accounts[1]})
	guardian_lite.renounce(minter_, {'from':accounts[2]})

def test_guardian_new_guardian(nft_lock, guardian_lite, minter_, accounts):
	caller = {'from':minter_}
	guardian_lite.setGuardian(accounts[1], {'from':minter_})
	guardian_lite.unlockMany([1, 2, 3, 4, 5], {'from':accounts[1]})
	for i in range(1, 6):
		assert nft_lock.lockCount(i) == 0
	nft_lock.safeTransferFrom(minter_, minter_, 1, caller)
	guardian_lite.lockMany([1, 2, 3, 4, 5], {'from':accounts[1]})

def test_guardian_retrieve_with_extra_lock(nft_lock, guardian_lite, minter_, accounts):
	caller = {'from':minter_}
	nft_lock.setApprovalForAll(guardian_lite, True, caller)
	nft_lock.updateApprovedContracts([accounts[7]], [True], caller)
	for i in range(5):
		nft_lock.lockId(i + 1, {'from':accounts[7]})
	with reverts('Token is locked'):
		guardian_lite.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})
	for i in range(5):
		nft_lock.unlockId(i + 1, {'from':accounts[7]})
	guardian_lite.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})
	with reverts('!guardian'):
		guardian_lite.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})
	assert nft_lock.balanceOf(accounts[4]) == 5

def test_guardian_retrieve_not_locked(nft_lock, guardian_lite, minter_, accounts):
	for i in range(5):
		nft_lock.safeTransferFrom(accounts[4], minter_, i + 1, {'from':accounts[4]})

	with reverts('ID not locked by caller'):
		guardian_lite.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})
	guardian_lite.lockMany([1, 2, 3, 4, 5], {'from':accounts[1]})
	guardian_lite.unlockManyAndTransfer([1, 2, 3, 4, 5], accounts[4], {'from':accounts[1]})

def test_guardian_same_as_sender(guardian_lite, accounts):
	with reverts('Guardian must be a different wallet'):
		guardian_lite.setGuardian(accounts[5], {'from':accounts[5]})
	