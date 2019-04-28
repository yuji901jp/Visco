# -*- coding: utf-8 -*-
import time
import socket
import re
import os
import xml.etree.ElementTree as ET

def extract_words(response):
        # 正規表現で切り出し
        xml_recogout = re.search(
            r'<RECOGOUT>.+</RECOGOUT>',
            response,
            flags=re.DOTALL)

        print("=====================================")

        if xml_recogout is None:
            return

        # XMLパース
        recogout = ET.fromstring(xml_recogout.group(0))
        words = []
        for whypo in recogout[0]:
            attrib = whypo.attrib
            print("[RAW]------ WORD=", attrib['WORD'],\
                               " CM=", attrib['CM'],\
                          " CLASSID=", attrib['CLASSID'],
                            " PHONE=", attrib['PHONE'])

            if attrib['WORD'] not in ('[s]', '[/s]'):
                if float(attrib['CM']) > 0.5:
                    print("[HIT]------ WORD=", attrib['WORD'],\
                                       " CM=", attrib['CM'],\
                                  " CLASSID=", attrib['CLASSID'],\
                                    " PHONE=", attrib['PHONE'])
                    words.append(attrib['WORD'])

        return ''.join(words)

def julius_speech_to_text(callback=None):
    host = '127.0.0.1'
    port = 10500
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    while True:
        time.sleep(0.1)
        response = client.recv(4096).decode('utf-8')

        text = extract_words(response)
        if text is None:
            continue

        print("[KEYWORD]-- Picked up keyword is : ", text)

        if 'Ping' in text:
            ping()

        if callback is not None:
            callback(text)

def exec_cmd(cmd):
    from subprocess import Popen, PIPE

    p = Popen(cmd.split(' '), stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()

    out = out.decode()
    output = out.split('\n')

    return output

def ping():
    target   = '192.168.1.1'
    count    = '5'
    interval = '0.2'
    cmd = 'ping '+target+' -c '+count+' -i '+interval

    print("[RUNNING]-- Ping試験を実行します。("+cmd+")")
    for line in exec_cmd(cmd):
        if "packet loss" in line:
            val = line.split(' ')
            loss = val[5].strip().replace('%','')
            if loss == '0':
                print("[SUCESS]--- "+target+"までロス無くPingが実行されました")
            else:
                print("[FAILED]--- "+target+"まで"+loss+"%のPingロスがありました")

    return

if __name__ == '__main__':
    try:
        julius_speech_to_text()

    except KeyboardInterrupt:
        print('keyboard interrupt')
