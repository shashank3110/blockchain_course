'''
Creating and Mining a basic Proof of Work (PoW) based block chain in Python
'''
import datetime
import json
import hashlib
from flask import Flask,jsonify


#Creating a Block Chain
class Blockchain:
    
    def __init__(self):
        #initialize chain
        self.chain = []
        #genesis block
        self.create_block(proof = 1, previous_hash = '0')

    def create_block(self,proof,previous_hash):
        '''
        create a block after a block is mined
        proof: returned after solving PoW function
        '''

        block = {'index': len(self.chain)+1,
        'timestamp' : str(datetime.datetime.now()),
        'proof' : proof,
        'previous_hash' : previous_hash ,
        'data' : 'optional'}

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

#A Flask based Web server to interact with Blockchain and mine blocks
block_chain = Blockchain()

app = Flask(__name__)

@app.route('/mine_block', methods=['GET'])
def mine_block():
    '''
    Mine a Block
    '''
    previous_block = block_chain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = block_chain.proof_of_work(previous_proof)
    previous_hash = block_chain.hash(previous_block)
    block = block_chain.create_block(proof, previous_hash)

    response = {'Message': 'Congrats on mining a Block',
    'index': block['index'],
    'timestamp': block['timestamp'],
    'proof': block['proof'],
    'previous_hash': block['previous_hash']}

    return jsonify(response), 200 #Response in json format & HTTP Status code for Success

@app.route('/get_block_chain', methods=['GET'])
def get_block_chain():
    '''
    Display the Full Block Chain
    '''
    response = {'chain': block_chain.chain,
                'Length': len(block_chain.chain)}

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

app.run(host ='0.0.0.0', port = 5000) #0.0.0.0 publicly visibly host