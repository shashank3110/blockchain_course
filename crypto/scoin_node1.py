'''
Creating and Mining a basic Proof of Work (PoW) based block chain and a proprietery crypto-currency 
in a decentralised network using Python.
Steps:
1. Building a BlockChain
2. Mining Blocks
3. Decentralizing a Blockchain
'''
import datetime
import json
import hashlib
from flask import Flask,jsonify,request
import requests
from uuid import uuid4
from urllib.parse import urlparse

#Creating a Block Chain
class Blockchain:
    
    def __init__(self):
        #initialize chain
        self.chain = []
        #list of transactions
        self.transaction_list=[]
        #genesis block
        self.create_block(proof = 1, previous_hash = '0')
        self.nodes = set()

    def create_block(self,proof,previous_hash):
        '''
        create a block after a block is mined
        proof: returned after solving PoW function
        '''

        block = {'index': len(self.chain)+1,
        'timestamp' : str(datetime.datetime.now()),
        'proof' : proof,
        'previous_hash' : previous_hash ,
        'transactions' : self.transaction_list,
        'data' : 'optional'}

        self.transaction_list = [] #emptying the list as each block has unique set of transactions
        self.chain.append(block)

        return block

    def get_previous_block(self):
        '''
        Returns last block of the blockchain
        '''
        return self.chain[-1]

    def proof_of_work(self,previous_proof):
        '''
        Function to solve and return PoW
        Number hard to find but easy to verify
        Hash Func used SHA256 and a non-symmetric
        operation.
        To increase the complexity use:
        1) a complex aymmetric hash_op
        2) increase leading 0s in verify operation.
        '''
        new_proof = 1
        verify = False
        
        while verify is False:
            #hash_op = hashlib.sha256(str(new_proof % previous_proof).encode()).hexdigest() 
            hash_op = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest() 
            #simpler operation new_proof**2 - previous_proof**2
            if hash_op[0:4] == '0000' : 
                #the number of leading characters can be increased to make it more difficult for miners
                verify = True
            else:
                new_proof += 1
            #here % is an asymmetric func. unlike addition/multiplication
        return new_proof
    
    def hash(self, block):
        '''
        Hash an incoming block in our blockchain
        '''

        encoded_block = json.dumps(block, sort_keys = True).encode()
        hashed_block  = hashlib.sha256(encoded_block).hexdigest()

        return hashed_block

    def is_valid_chain(self, chain):
        '''
        check correctness of each block in a blockchain
        so that there is no forged block introduced
        if there us any forged block then is_valid_check will
        fail and return False.
        '''
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False

            previous_proof = previous_block['proof']
            proof = block['proof']
            #Difficult Hash op
            #hash_op = hashlib.sha256(str(proof % previous_proof).encode()).hexdigest()
            
            #Easier Hash op challenge
            hash_op = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            
            if hash_op[:4] != '0000' :
                return False
            previous_block = block
            block_index +=1

        return True

    def add_transaction(self, sender, receiver, amt):
        '''
        Adding Transactions as a dict to the transaction
        list in a block.
        '''
        self.transaction_list.append({'sender':sender,'receiver':receiver,'amount':amt})
        prev_block = self.get_previous_block()
        return prev_block['index'] + 1 #returns index of current block

    def add_node(self,address):
        '''
        Decentralizing a Block chain
        '''
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def replace_chain(self):
        '''
        Compare chains of nodes in network and 
        update the blockchain the largest chain
        '''
        network = self.nodes
        longest_chain = None
        max_len = len(self.chain)
        print(max_len)
        for node in network:
            print(node)
            response = requests.get(f'http://{node}/get_block_chain')
            print(response)
            if response.status_code == 200:
                print(response.json())
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_len and self.is_valid_chain(chain):
                    max_len = length
                    longest_chain = chain

        if longest_chain:
            self.chain = longest_chain
            return True

        return False



#A Flask based Web server to interact with Blockchain and mine blocks
app = Flask(__name__)

#create address for node on a port, uuid4 creates random address
node_address = str(uuid4()).replace('-','')

#create a blockchain
block_chain = Blockchain()


@app.route('/mine_block', methods=['GET'])
def mine_block():
    '''
    Mine a Block
    '''
    previous_block = block_chain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = block_chain.proof_of_work(previous_proof)
    previous_hash = block_chain.hash(previous_block)
    block_chain.add_transaction(sender = node_address, receiver = 'Ram' , amt = 2)

    block = block_chain.create_block(proof, previous_hash)
    response = {'Message': 'Congrats on mining a Block',
    'index': block['index'],
    'timestamp': block['timestamp'],
    'proof': block['proof'],
    'previous_hash': block['previous_hash'],
    'transactions' : block['transactions']}

    return jsonify(response), 200 #Response in json format & HTTP Status code for Success

@app.route('/get_block_chain', methods=['GET'])
def get_block_chain():
    '''
    Display the Full Block Chain
    '''
    response = {'chain': block_chain.chain,
                'length': len(block_chain.chain)}

    return jsonify(response), 200 #Response in json format & HTTP Status code for Success

# Homework 1
@app.route('/check_valid_chain', methods=['GET'])
def check_valid_chain():
    '''
    Check and get response  if the blockchain is valid.
    False Response indicates possibility of a Forged block in the chain.
    '''

    chain = block_chain.chain
    valid = block_chain.is_valid_chain(chain)

    response = {'chain': block_chain.chain,
                'check_valid': valid}

    return jsonify(response), 200

@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    '''
    Post a transaction.
    '''
    json_file = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    if not all (key in json_file for key in transaction_keys):
        return 'Some elements of a transaction are missing', 400
    index = block_chain.add_transaction(json_file['sender'],json_file['receiver'],json_file['amount'])  
    response = {'message' : f'transaction will be added to block {index}'}

    return jsonify(response), 201 #http status code for post/created
    
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    '''
    Used to add a new node in our decentralised network.
    '''
    json_file = request.get_json()
    nodes = json_file.get('nodes')
    if nodes is None:
        return 'no nodes', 400
    for node in nodes:
        block_chain.add_node(node)
    response = {'message'  : 'all nodes added in this block chain','all_nodes' : list(block_chain.nodes)}
    return   jsonify(response), 201 

@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    '''
    Replace the existing chain by the longest one.
    '''
    is_replace = block_chain.replace_chain()
    if is_replace:
        response = {'message' : 'The chain was replaced by longest one.','new_chain':block_chain.chain}
    else:
        response = {'message' : 'The existing chain is the longest one.','esisting_chain':block_chain.chain}

    return jsonify(response), 200


app.run(host ='0.0.0.0', port = 5001) #0.0.0.0 publicly visibly host