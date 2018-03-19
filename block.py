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
        self.network = ''

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
            'timeStamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previousHash': self.hash(self.chain[-1]) if len(self.chain) else '1',
        }

        # Reset the current list of transactions
        self.transactions = []

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

        :return: 区块链中最后一个区块的index
        """
        return self.chain[-1]['index']

    def last_block(self):
        """

        :return: 返回最后一个区块
        """
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

        guess = '{previous_proof}{proof}{last_hash}'.format(previous_proof=previous_proof, proof=proof, previous_hash=previous_hash)
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash.startswith('0000')

    def get_transaction_list(self, block_gain = 1):
        """
        模拟区块从网络中收集近期的交易列表,并加上打包权益
        :param address: 网络模拟的server/transaction 地址
        :param block_gain: 区块交易打包的收益
        :return: current_transaction: 打包在区块中的交易列表
        """
        res = requests.get(self.network + '/transactions')
        net_transaction_list = res['transactionList']
        return net_transaction_list.append({
                'sender': "0",
                'recipient': self.id,
                'amount': block_gain,
            })

    def get_neighbours(self):
        res = requests.get(self.network + '/nodes')
        return res['nodes']

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
            if block['previous_hash'] != self.hash(last_block):
                return False
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block['previous_hash']):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: True if our chain was replaced, False if not
        """
        neighbours = self.get_neighbours()
        new_chain = None
        # We're only looking for chains longer than ours
        max_length = len(self.chain)
        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get('http://{node}/chain'.format(node=node))
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False