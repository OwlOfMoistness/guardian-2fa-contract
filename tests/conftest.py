import pytest

@pytest.fixture(scope="module")
def minter_(accounts):
    return accounts[0]

@pytest.fixture(scope="module")
def nft_lock(TestNFT, minter_):
    return TestNFT.deploy({'from':minter_})

@pytest.fixture(scope="module")
def guardian(Guardian, nft_lock, minter_):
    return Guardian.deploy(nft_lock, {'from':minter_})

@pytest.fixture(scope="module")
def guardian_arr(GuardianPendingArray, nft_lock, minter_):
    return GuardianPendingArray.deploy(nft_lock, {'from':minter_})


@pytest.fixture(scope="module")
def guardian_lite(GuardianLite, nft_lock, minter_):
    return GuardianLite.deploy(nft_lock, {'from':minter_})