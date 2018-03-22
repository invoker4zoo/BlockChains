# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechat: whatshowlove
@ software: PyCharm
@ file: node
@ time: 18-3-19
"""

from flask import Flask, jsonify, request
from block import BlockNode
import requests
import json

# initial the server
app = Flask(__name__)


# initial the block node
blockchain = BlockNode()


@app.route('/id', methods=['GET'])
def get_id():
    if blockchain.id:
        return blockchain.id, 200
    else:
        return 'get invalid id', 500


@app.route('/mine', methods=['GET'])
def mine():
    block = blockchain.mine_once()
    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previousHash'],
    }
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/chain/resolve', methods=['GET'])
def consensus():
    if blockchain.resolve_conflicts():
        return 'solve conflicts, change chain', 200
    else:
        return 'solve conflicts, save self chain', 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    # values = request.get_json()
    transaction = json.loads(request.form.get('transaction'))

    # Create a new Transaction
    index = blockchain.new_transaction(transaction)

    response = {'message': 'Transaction will be added to Block {index}'.format(index=index)}
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    try:
        nodes = json.loads(request.form.get('nodes', None))
        for node in nodes:
            blockchain.add_neighbour(node)
        return 'register nodes success', 200
    except Exception, e:
        return 'register nodes failed for %s'%str(e), 500


@app.route('/count', methods=['GET'])
def count():
    try:
        count_info = blockchain.count()
        return jsonify(count_info), 200
    except:
        'get count info failed', 500


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)