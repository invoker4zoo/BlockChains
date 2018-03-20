# coding=utf-8
"""
@ license: Apache Licence
@ github: invoker4zoo
@ author: invoker/cc
@ wechat: whatshowlove
@ software: PyCharm
@ file: main
@ time: 18-3-20
"""
import sys
import os
import requests
import time
import random
import copy
import json


if __name__ == '__main__':
    STRAT_PORT = 5000
    MAIN_ADDRESS = 'http://0.0.0.0:5050'
    node_list = []
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-n', '--num', default=3, type=int, help='number of the nodes')
    parser.add_argument('-t', '--type', default='mining simulation', type=str, help='simulation type')
    args = parser.parse_args()
    num = args.num
    simulation_type = args.type

    # strat main line
    os.system('nohup python mainLine.py >/dev/null 2>&1 & ')

    # start node services
    for i in range(0, num):
        node_list.append('http://0.0.0.0:%d'%(STRAT_PORT + i))
        os.system('nohup python node.py -p %d >/dev/null 2>&1 &'%(STRAT_PORT + i))

    # registe address
    for i in range(0, num):
        node_id = requests.get(node_list[i] + '/id').content
        post_data = {
            'address': node_list[i],
            'id': node_id
        }
        requests.post(MAIN_ADDRESS + '/register', data=post_data)
        _node_list = copy.deepcopy(node_list)
        _node_list.pop(i)
        requests.post(node_list[i] + '/nodes/register', data={'nodes':json.dumps(_node_list)})

    while 1:
        # 每20秒一次区块链更新
        # 随机区块挖掘速度，控制区块产生速度
        miner_random_list = [int(random.random()*10 + 5) for i in range(1, num)]
        for count in range(0, 20):
            time.sleep(1)
            for index, random_time in enumerate(miner_random_list):
                if not count % random_time:
                    requests.get(node_list[index] + '/mine')
            if not count % 1:
                requests.get(MAIN_ADDRESS + '/transactions/random')
        requests.get(MAIN_ADDRESS + '/freshChain')