#!/bin/python
import hashlib
import os
import random


def mine_block(k, prev_hash, transactions):
    """
        k - Number of trailing zeros in the binary representation (integer)
        prev_hash - the hash of the previous block (bytes)
        rand_lines - a set of "transactions," i.e., data to be included in this block (list of strings)

        Complete this function to find a nonce such that 
        sha256( prev_hash + rand_lines + nonce )
        has k trailing zeros in its *binary* representation
    """
    if not isinstance(k, int) or k < 0:
        print("mine_block expects positive integer")
        return b'\x00'

    transaction_bytes = ''.join(transactions).encode('utf-8')
    
    nonce = 0
    while True:
        nonce_bytes = str(nonce).encode('utf-8')
        
        combined = prev_hash + transaction_bytes + nonce_bytes
        
        block_hash = hashlib.sha256(combined).digest()
        
        hash_int = int.from_bytes(block_hash, byteorder='big')
        
        trailing_zeros = 0
        temp = hash_int
        while temp & 1 == 0 and trailing_zeros < k + 1:
            trailing_zeros += 1
            temp >>= 1
        
        if trailing_zeros >= k:
            nonce_str = str(nonce)
            nonce = nonce_str.encode('utf-8')
            break
        
        nonce += 1

    assert isinstance(nonce, bytes), 'nonce should be of type bytes'
    return nonce


def get_random_lines(filename, quantity):
    """
    This is a helper function to get the quantity of lines ("transactions")
    as a list from the filename given. 
    Do not modify this function
    """
    lines = []
    with open(filename, 'r') as f:
        for line in f:
            lines.append(line.strip())

    random_lines = []
    for x in range(quantity):
        random_lines.append(lines[random.randint(0, quantity - 1)])
    return random_lines


if __name__ == '__main__':
    filename = "bitcoin_text.txt"
    num_lines = 10

    diff = 20

    prev_hash = b'previous_block_hash'
    transactions = get_random_lines(filename, num_lines)
    nonce = mine_block(diff, prev_hash, transactions)
    print(nonce)
