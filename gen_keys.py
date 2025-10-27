from web3 import Web3
from eth_account.messages import encode_defunct
import eth_account
import os

def get_keys(challenge):
    """
    challenge - byte string
    Creates a new account, signs the challenge, and returns signature and address.
    The account must have funds on both BSC and Avalanche testnets.
    """
    w3 = Web3()
    
    private_key_hex = "aff3b7c486df52bcb78f62d0523b472c5ba59a511598c8366e9c2bd2145dd7e3"
    account_object = eth_account.Account.from_key(private_key_hex)
    eth_addr = account_object.address
    
    message = encode_defunct(challenge)
    
    signed_message = account_object.sign_message(message)
    
    assert eth_account.Account.recover_message(message, signature=signed_message.signature.hex()) == eth_addr, f"Failed to sign message properly"
    
    return signed_message, eth_addr

def sign_message(challenge, filename="secret_key.txt"):
    """
    challenge - byte string
    filename - filename of the file that contains your account secret key
    To pass the tests, your signature must verify, and the account you use
    must have testnet funds on both the bsc and avalanche test networks.
    """
    # This code will read your "sk.txt" file
    # If the file is empty, it will raise an exception
    with open(filename, "r") as f:
        key = f.readlines()
    assert(len(key) > 0), "Your account secret_key.txt is empty"

    w3 = Web3()
    message = encode_defunct(challenge)

    # Read the private key from file and create account
    private_key_hex = key[0].strip()
    account_object = eth_account.Account.from_key(private_key_hex)
    eth_addr = account_object.address
    
    # Sign the message
    signed_message = account_object.sign_message(message)

    assert eth_account.Account.recover_message(message,signature=signed_message.signature.hex()) == eth_addr, f"Failed to sign message properly"

    #return signed_message, account associated with the private key
    return signed_message, eth_addr


if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr = get_keys(challenge=challenge)
        print(f"Address: {addr}")
        print(f"Signature: {sig.signature.hex()}")
        print("---")
