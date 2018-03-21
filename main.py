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

# global parameters
STRAT_PORT = 5000
MAIN_ADDRESS = 'http://0.0.0.0:5050'

def simulation(num =3):
    """
    启动一个最小的模拟分布式系统
    :return:
    """
    node_list = []
    # strat main line
    os.system('nohup python network.py >/dev/null 2>&1 & ')

    # start node services
    for i in range(0, num):
        node_list.append('http://0.0.0.0:%d' % (STRAT_PORT + i))
        os.system('nohup python node.py -p %d >/dev/null 2>&1 &' % (STRAT_PORT + i))
        time.sleep(1)

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
        requests.post(node_list[i] + '/nodes/register', data={'nodes': json.dumps(_node_list)})

    while 1:
        # 每20秒一次区块链更新
        # 随机区块挖掘速度，控制区块产生速度
        miner_random_list = [int(random.random() * 10 + 5) for i in range(1, num)]
        for count in range(0, 20):
            time.sleep(1)
            for index, random_time in enumerate(miner_random_list):
                if not count % random_time:
                    requests.get(node_list[index] + '/mine')
            if not count % 1:
                requests.get(MAIN_ADDRESS + '/transactions/random')
        requests.get(MAIN_ADDRESS + '/freshChain')


def add_node(port=None):
    """
    将一个新的node加入到网络之中
    :return:
    """
    if port:
        pass
    else:
        res = requests.get(MAIN_ADDRESS + '/nodes')
        data = json.loads(res.content)
        length = data.get('length', 3)
        address_list = data.get('nodes', [])
        port = STRAT_PORT + length
    # start new node service
    os.system('nohup python node.py -p %d >/dev/null 2>&1 &' % port)
    time.sleep(1)
    # register node
    new_address = 'http://0.0.0.0:%d'%port
    new_id = requests.get(new_address+ '/id').content
    post_data = {
        'address': new_address,
        'id': new_id
    }
    requests.post(MAIN_ADDRESS + '/register', data=post_data)
    # get neighbours
    requests.post(new_address + '/nodes/register', data={'nodes': json.dumps(address_list)})
    # update chain
    while 1:
        random_freq = int(random.random() * 10 + 5)
        for count in range(0, 20):
            time.sleep(1)
            if not count % random_freq:
                requests.get(new_address + '/mine')
            if not count % 1:
                requests.get(MAIN_ADDRESS + '/transactions/random')
        requests.get(MAIN_ADDRESS + '/freshChain')

if __name__ == '__main__':


    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-n', '--num', default=3, type=int, help='number of the nodes')
    parser.add_argument('-t', '--type', default='simulation', type=str, help='system type')
    parser.add_argument('-p', '--port', default=0, type=int, help='addition node port')
    args = parser.parse_args()
    num = args.num
    simulation_type = args.type
    port = args.port

    if simulation_type=='simulation':
        simulation(num=num)

    if simulation_type=='add':
        if not port:
            add_node()
        else:
            add_node(port=port)
    if simulation_type=='kill':
        os.system('pkill -f python')

