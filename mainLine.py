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

# initial the server
app = Flask(__name__)

@app.route('/register', methods=['POST'])
def mine():
    pass

if __name__ == '__main__':
    # from argparse import ArgumentParser

    # parser = ArgumentParser()
    # parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    # args = parser.parse_args()
    # port = args.port

    app.run(host='0.0.0.0', port=5000)