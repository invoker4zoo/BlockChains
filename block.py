# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechat: whatshowlove
@ software: PyCharm
@ file: block
@ time: 18-3-19
"""

import hashlib
import json
from time import time
from uuid import uuid4
import time
import random
import json
import requests


class BlockNode(object):
    """
    创建区块node
    """
    def __init__(self):
        """
        transaction:交易记录列表
        block:区块内容
        chain:链列表
        """
        # 当前收集到的交易记录列表
        self.transaction = []
        # 区块链的记录，账本
        self.chain = []
        # 生成一个node的id
        self.id = str(uuid4()).replace('-', '')
        # 模拟网络的地址
        self.network = 'http://0.0.0.0:5050'
        # 相邻node
        self.neighbours = []

    def new_block(self, proof):
        """
        打包一个新的区块
        :param proof: 工作量证明，hash运算的次数
        :return: 区块包含的数据
        区块数据结构{
            index: 区块的位置,
            timeStamp: 区块产生的时间,
            proof: 工作量证明,
            previousHash: 前一个区块的hash值
        }
        """
        block = {
            'index': len(self.chain) + 1,
            'timeStamp': time.time(),
            'transactions': self.transaction,
            'proof': proof,
            'previousHash': self.hash(self.chain[-1]) if len(self.chain) else '1',
        }

        # Reset the current list of transactions
        self.transaction = []

        self.chain.append(block)
        return block

    @staticmethod
    def hash(block):
        """
        通过区块的内容，使用SHA-256计算出区块的hash值
        :param block: Block
        """
        # 为了保证字典中的顺序每次计算时是一致的，需要进行key的排序
        block_content = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_content).hexdigest()

    def last_index(self):
        """
        取到链上的最后一个区块的index值
        :return: 区块链中最后一个区块的index
        """
        return self.chain[-1]['index']

    def last_block(self):
        """
        取到连上的最后一个区块
        :return: 返回最后一个区块
        """
        if len(self.chain):
            return self.chain[-1]
        else:
            self.get_transaction_list()
            self.new_block(100)
            return self.chain[-1]

    def proof_of_work(self, last_block):
        """
        寻找符合工作量证明的proof,使用的算法如下：
         - 找到一个proof，使得hash(proof||previous_proof||previous_hash) 的值是以4个零开头
         - 4个零开头的规则是示例规则
        :param last_block: 前一个区块
        :return: proof
        """

        previous_proof = last_block['proof']
        previous_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(previous_proof, proof, previous_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(previous_proof, proof, previous_hash):
        """
        验证proof有效性
        :param previous_proof:
        :param proof:
        :param previous_hash: 前一个区块的hash值
        :return: proof的有效性 bool
        """

        # guess = '{previous_proof}{proof}{previous_hash}'.format(previous_proof=previous_proof, proof=proof, previous_hash=previous_hash)
        guess = str(previous_proof) + str(proof) + str(previous_hash)
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash.startswith('0000')

    def get_transaction_list(self, block_gain = 1):
        """
        模拟区块从网络中收集近期的交易列表,并加上打包权益
        # :return: current_transaction: 打包在区块中的交易列表
        """
        self.transaction.append({
                'sender': "0",
                'recipient': self.id,
                'amount': block_gain,
            })

    def add_neighbour(self, neighbour):
        """
        添加邻居
        :return:
        """
        if neighbour not in self.neighbours and neighbour:
            self.neighbours.append(neighbour)

    def varify_chain_validate(self, chain):
        """
        验证一个区块链是否合法,验证区块的hash值是否符合，proof值是否合法
        :param chain: 验证的链
        :return: 是否合法 bool
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # Check that the hash of the block is correct
            if block['previousHash'] != self.hash(last_block):
                return False
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], block['previousHash']):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        """
        解决区块链冲突
        """
        neighbours = self.neighbours
        new_chain = None
        # We're only looking for chains longer than ours
        max_length = len(self.chain)
        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            print node
            response = requests.get('{node}/chain'.format(node=node))
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # Check if the length is longer and the chain is valid
                if length > max_length and self.varify_chain_validate(chain):
                    max_length = length
                    new_chain = chain
        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def mine_once(self):
        """
        挖掘一个区块
        :return:
        """
        try:
            last_block = self.last_block()
            proof = self.proof_of_work(last_block)
            # collect transactions
            self.get_transaction_list()
            block = self.new_block(proof)
            # time.sleep(int(random.random()*10))
            return block
        except:
            return None

    def new_transaction(self, transaction):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.transaction.append({
            'sender': transaction['sender'],
            'recipient': transaction['recipient'],
            'amount': transaction['amount'],
        })

        return self.last_block()['index'] + 1

    def count(self):
        """
        通过区块链信息计算所有用户的余额
        :return:
        """
        node_count_info = {}
        for item in self.chain:
            transaction_list = item.get('transactions',[])
            for transaction in transaction_list:
                if transaction['sender'] not in node_count_info.keys():
                    node_count_info[transaction['sender']] = 0
                if transaction['recipient'] not in node_count_info.keys():
                    node_count_info[transaction['recipient']] = 0
                node_count_info[transaction['sender']] -= transaction['amount']
                node_count_info[transaction['recipient']] += transaction['amount']
        return node_count_info