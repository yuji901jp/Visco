# -*- coding: utf-8 -*-
import time
import socket
import re
import xml.etree.ElementTree as ET
from actions import exec_cmd
import json
import os

def readjson(jfile):

    f = open(jfile, 'r')
    jsondata = json.load(f)

    return jsondata

def setenv(jsondata):
    # 各グループ毎にパラメーターの変数格納
    groupdict = jsondata["OsEnv"]
    alsadev   = groupdict["AlsaDev"]

    # 事前設定
    print('変更前の設定 -->', end='')
    print(os.getenv('ALSADEV'))
    os.environ['ALSADEV'] = alsadev
    print('変更後の設定 -->', end='')
    print(os.getenv('ALSADEV'))

    # 設定結果の確認
    if os.getenv('ALSADEV') != alsadev:
        print('[FAILED]--- ${ALSADEV}を'+alsadev+'に変更することができませんでした。')
        sys.exit()
    elif os.getenv('ALSADEV') == alsadev:
        print('[SUCCESS]-- ${ALSADEV}を'+alsadev+'に変更しました。')

def voice2words(response):
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
                if float(attrib['CM']) > 0.3:
                    print("[HIT]------ WORD=", attrib['WORD'],\
                                       " CM=", attrib['CM'],\
                                  " CLASSID=", attrib['CLASSID'],\
                                    " PHONE=", attrib['PHONE'])
                    words.append(attrib['WORD'])

        return ''.join(words)

def speech2text(responsesoundfile, callback=None):
    host = '127.0.0.1'
    port = 10500
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    while True:
        time.sleep(0.1)
        response = client.recv(4096).decode('utf-8')

        text = voice2words(response)
        if text is None:
            continue

        if len(text) is not 0:
            #exec_cmd.response(word=text, wav='/home/pi/Visco/sounds/response.wav')
            aplay = ['aplay']
            wav   = [responsesoundfile]
            cmd = aplay+wav
            print(cmd)
            exec_cmd.oscmd(cmd, shell=False)
            print("[KEYWORD]-- Picked up keyword is : ", text)

        if 'Ping' in text:
            exec_cmd.ping(target='8.8.8.8', read='on')
        elif '時間' in text or '何時' in text:
            exec_cmd.date(read='on')
        elif 'もう一度' in text or 'もう一回' in text or 'リコール' in text:
            exec_cmd.recall(read='on')
        elif 'アドレス' in text:
            exec_cmd.getaddress(read='on')

        if callback is not None:
            callback(text)

if __name__ == '__main__':

    # JSONファイルの読み込み
    jfile = 'setting.json'
    jsondata = readjson(jfile)

    # 事前設定
    setenv(jsondata)

    groupdict = jsondata["Sounds"]
    responsesoundfile = groupdict["ResponseSoundFile"]
    print("Sounds :")
    print("     responsesoundfile :", responsesoundfile)

    aplay = ['aplay']
    wav   = [responsesoundfile]
    cmd = aplay+wav
    print(cmd)
    exec_cmd.oscmd(cmd, shell=False)

    try:
        speech2text(responsesoundfile)

    except KeyboardInterrupt:
        print('keyboard interrupt')
