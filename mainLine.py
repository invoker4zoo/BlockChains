# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechat: whatshowlove
@ software: PyCharm
@ file: mainLine
@ time: 18-3-19
"""

from flask import Flask, jsonify, request
import random
import requests
import json

# initial the server
app = Flask(__name__)

ADDRESSLIST = []
IDLIST = []
TRANSACTIONLIST = []


@app.route('/register', methods=['POST'])
def mine():
    # values = request.get_json()
    address = request.form.get('address')
    id = request.form.get('id')
    if address in ADDRESSLIST:
        return 'address already in server', 400
    else:
        ADDRESSLIST.append(address)
        IDLIST.append(id)
        return 'success regist address', 200


@app.route('/freshChain', methods=['GET'])
def fresh_chain():
    for address in ADDRESSLIST:
        try:
            res = requests.get('{address}/chain/resolve'.format(address=address))
        except Exception, e:
            print 'fresh nodes chain failed for %s with server %s'%(str(e), address)


@app.route('/nodes', methods=['GET'])
def nodes():
    response = {
        'nodes': ADDRESSLIST,
        'length': len(ADDRESSLIST)
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def add_transaction():
    # values = request.get_json()
    transaction = request.form.get('transaction', None)
    if transaction:
        try:
            broad_transaction(transaction)
            return 'add transaction success', 200
        except:
            return 'add transaction failed', 400
    else:
        return 'invailed transaction info', 400


@app.route('/transactions/random', methods=['GET'])
def random_transaction():
    transaction = _random_transaction()
    if transaction:
        try:
            broad_transaction(transaction)
            return 'add random transaction success', 200
        except:
            return 'add random transaction failed', 400
    else:
        return 'invailed random transaction info', 400


@app.route('/transactions', methods=['GET'])
def transaction():
    return jsonify({'transactionList':TRANSACTIONLIST})


def _random_transaction():
    """
    创建随机的交易数据
    :return:
    """
    if len(ADDRESSLIST) >= 2:
        [source, target] = random.sample(IDLIST, 2)
        amount = round(random.random()/100, 3)

        print 'add a random transaction'
        return {
            'sender': source,
            'recipient': target,
            'amount': amount
        }

    else:
        print 'not enough node for generating transaction'
        return None


def broad_transaction(transaction):
    """

    :param transaction:
    :return:
    """
    for address in ADDRESSLIST:
        requests.post(address + '/transactions/new', data={'transaction': json.dumps(transaction)})

if __name__ == '__main__':
    # from argparse import ArgumentParser

    # parser = ArgumentParser()
    # parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    # args = parser.parse_args()
    # port = args.port

    app.run(host='0.0.0.0', port=5050)