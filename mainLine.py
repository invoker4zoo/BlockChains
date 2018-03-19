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

# Instantiate the server
app = Flask(__name__)