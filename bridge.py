from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware #Necessary for POA chains
from pathlib import Path
import json
from datetime import datetime
import pandas as pd
import eth_account
import os
import time


def connect_to(chain):
    if chain == 'source':  # The source contract chain is avax
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'destination':  # The destination contract chain is bsc
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['source','destination']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def get_contract_info(chain, contract_info):
    """
        Load the contract_info file into a dictionary
        This function is used by the autograder and will likely be useful to you
    """
    try:
        # Handle both Path objects and strings (open() handles Path in Python 3.6+)
        with open(contract_info, 'r')  as f:
            contracts = json.load(f)
    except Exception as e:
        print( f"Failed to read contract info\nPlease contact your instructor\n{e}" )
        return 0
    return contracts[chain]



def scan_blocks(chain, contract_info="contract_info.json"):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return 0
    
    secret_key_file = None
    possible_paths = [
        "secret_key.txt",
        "sk.txt",
        os.path.join(os.path.dirname(__file__), "secret_key.txt"),
        os.path.join(os.path.dirname(__file__), "sk.txt"),
        os.path.join(os.getcwd(), "secret_key.txt"),
        os.path.join(os.getcwd(), "sk.txt"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            secret_key_file = path
            break
    
    if secret_key_file is None:
        print( f"Error: Could not find secret_key.txt or sk.txt in any of the expected locations" )
        return 0
    
    with open(secret_key_file, "r") as f:
        private_key = f.read().strip()
    account = eth_account.Account.from_key(private_key)
    
    # Get contract info for the current chain
    contracts_data = get_contract_info(chain, contract_info)
    if contracts_data == 0:
        return 0
    
    # Connect to the chain and get contract
    w3 = connect_to(chain)
    contract_address = Web3.to_checksum_address(contracts_data["address"])
    contract_abi = contracts_data["abi"]
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    
    if chain == 'source':
        # Scan the last 5 blocks on source chain
        end_block = w3.eth.get_block_number()
        start_block = max(1, end_block - 5)
        
        print(f"Scanning source blocks {start_block} - {end_block}")
        
        # Look for Deposit events on source chain
        all_events = []
        try:
            event_filter = contract.events.Deposit.create_filter(
                from_block=start_block, 
                to_block=end_block
            )
            events = event_filter.get_all_entries()
            all_events.extend(events)
        except Exception as e:
            print(f"Error scanning for Deposit events: {e}")
            all_events = []
        
        events = all_events
        print(f"Found {len(events)} Deposit events")
        
        if len(events) > 0:
            # Get destination contract info
            dest_contracts_data = get_contract_info("destination", contract_info)
            if dest_contracts_data == 0:
                return 0
            
            # Connect to destination chain
            dest_w3 = connect_to("destination")
            dest_contract_address = Web3.to_checksum_address(dest_contracts_data["address"])
            dest_contract_abi = dest_contracts_data["abi"]
            dest_contract = dest_w3.eth.contract(address=dest_contract_address, abi=dest_contract_abi)
            
           
            for evt in events:
                token = evt['args']['token']
                recipient = evt['args']['recipient']
                amount = evt['args']['amount']
                
                print(f"Processing Deposit: token={token}, recipient={recipient}, amount={amount}")
                
                # Build and send wrap transaction
                nonce = dest_w3.eth.get_transaction_count(account.address, 'pending')
                transaction = dest_contract.functions.wrap(token, recipient, amount).build_transaction({
                    'from': account.address,
                    'nonce': nonce,
                    'gas': 300000,
                    'gasPrice': dest_w3.eth.gas_price,
                })
                
                signed_txn = dest_w3.eth.account.sign_transaction(transaction, account.key)
                tx_hash = dest_w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                
                print(f"Sent wrap transaction: {tx_hash.hex()}")
    
    elif chain == 'destination':

        end_block = w3.eth.get_block_number()
        start_block = max(1, end_block - 15)  
        
        print(f"Scanning destination blocks {start_block} - {end_block}")
        
        all_events = []
        try:
            event_filter = contract.events.Unwrap.create_filter(
                from_block=start_block, 
                to_block=end_block
            )
            events = event_filter.get_all_entries()
            all_events.extend(events)
        except Exception as e:
            print(f"Error scanning for Unwrap events: {e}")
            all_events = []
        
        events = all_events
        print(f"Found {len(events)} Unwrap events")
        
        if len(events) > 0:
            # Get source contract info
            source_contracts_data = get_contract_info("source", contract_info)
            if source_contracts_data == 0:
                return 0
            
            # Connect to source chain
            source_w3 = connect_to("source")
            source_contract_address = Web3.to_checksum_address(source_contracts_data["address"])
            source_contract_abi = source_contracts_data["abi"]
            source_contract = source_w3.eth.contract(address=source_contract_address, abi=source_contract_abi)
            
            # For each Unwrap event, call withdraw() on source contract
            for evt in events:
                underlying_token = evt['args']['underlying_token']
                to = evt['args']['to']
                amount = evt['args']['amount']
                
                print(f"Processing Unwrap: token={underlying_token}, to={to}, amount={amount}")
                
                # Build and send withdraw transaction
                nonce = source_w3.eth.get_transaction_count(account.address, 'pending')
                transaction = source_contract.functions.withdraw(underlying_token, to, amount).build_transaction({
                    'from': account.address,
                    'nonce': nonce,
                    'gas': 300000,
                    'gasPrice': source_w3.eth.gas_price,
                })
                
                signed_txn = source_w3.eth.account.sign_transaction(transaction, account.key)
                tx_hash = source_w3.eth.send_raw_transaction(signed_txn.raw_transaction)
                receipt = source_w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                
                if receipt['status'] == 1:
                    print(f"Withdrew {amount} tokens to {to} on source chain. Tx: {tx_hash.hex()}")
                else:
                    print(f"Failed to withdraw {amount} tokens. Tx: {tx_hash.hex()}")
    
    return 1
