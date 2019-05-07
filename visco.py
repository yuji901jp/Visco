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
    #print('変更前の設定 -->', end='')
    #print(os.getenv('ALSADEV'))
    os.environ['ALSADEV'] = alsadev
    #print('変更後の設定 -->', end='')
    #print(os.getenv('ALSADEV'))

    # 設定結果の確認
    if os.getenv('ALSADEV') != alsadev:
        print('[FAILED]--- : ${ALSADEV}を'+alsadev+'に変更することができませんでした。')
        sys.exit()
    elif os.getenv('ALSADEV') == alsadev:
        print('[SUCCESS]-- : ${ALSADEV}を'+alsadev+'に変更しました。')

def speech2text(jsondata, callback=None):
    # 効果音のファイル取得
    groupdict = jsondata["Sounds"]
    responsesoundfile = groupdict["ResponseSoundFile"]
    print("[DEBUG]---- : Sounds :")
    print("[DEBUG]---- :    responsesoundfile :", responsesoundfile)

    # juliusサーバの設定情報取得
    groupdict = jsondata["Julius"]
    serverip   = groupdict["ServerIp"]
    serverport = groupdict["ServerPort"]
    threshold  = groupdict["Threshold"]
    print("[DEBUG]---- : Julius :")
    print("[DEBUG]---- :    serverip   :", serverip)
    print("[DEBUG]---- :    serverport :", serverport)
    print("[DEBUG]---- :    threshold  :", threshold)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((serverip, int(serverport)))

    # Action用のパラメータを読み込み
    groupdict = jsondata["Actions"]
    pingtarget   = groupdict["PingTarget"]
    pingcount    = groupdict["PingCount"]
    pinginterval = groupdict["PingInterval"]
    print("[DEBUG]---- : Actions :")
    print("[DEBUG]---- :    PingTarget   :", pingtarget)
    print("[DEBUG]---- :    PingCount    :", pingcount)
    print("[DEBUG]---- :    PingInterval :", pinginterval)

    # juliusサーバからのレスポンスを処理
    data = ''
    while True:
        new_data = client.recv(1024).decode().replace('\n','')
        print('[DEBUG]---- : Client is recieved following DATA at this time : \n', \
                new_data.replace('>','>\n'))

        # レスポンスの中に認識区間の区切りがあった場合
        if '</RECOGOUT>' in new_data :
            print('[DEBUG]---- : new raw data is from here ---:\n', \
                    new_data.replace('>','>\n'))
            print('[DEBUG]---- : end tag is found !!!\n')
            key  = ''
            data = data + new_data
            start_number = data.find('<RECOGOUT>')
            end_number   = data.find('</RECOGOUT>')+11
            print('[DEBUG]---- : data list is updated !!!!')
            print('[DEBUG]---- : total raw is from here ------:\n', \
                    data.replace('>','>\n') + new_data.replace('>','>\n'))
            print('[DEBUG]---- : data.find is from here ------:\n', \
                    data[start_number:end_number].replace('>','>\n'))
            print('[DEBUG]---- : RECOGOUT tag length is -: ', \
                    len(data[start_number:end_number]))
           
            # レスポンスの中に単語が正常に含まれているか確認
            if len(data[start_number:end_number]) <= 1:
                print('[DEBUG]---- : length of RECOGOUT tag is not enouth to parse')
            else:
                print('[DEBUG]---- : data.find is picked up collectory and good to trase ---:\n', \
                        data[start_number:end_number].replace('>','>\n'))

                # 完全はXML形式へ整形し、XMLからパラメータをパース
                root = ET.fromstring('<?xml version="1.0"?>\n' + data[start_number:end_number].replace('.', ''))
                for shypo in root.findall('SHYPO'):
                    score = shypo.get('SCORE')
                    print('!!!!SCORE   :', score)
                for whypo in root.findall('./SHYPO/WHYPO'):
                    word  = whypo.get('WORD')
                    score = float(whypo.get('CM'))
                    print('!!!!WORD    :', word, 'CM :', score)

                    # 単語の認識(単語毎に認識合致率の閾値を設定)
                    if 'Ping' in word and score/1000.0 >= 0.5:
                        key = key + word
                    elif '打って' in word and score/1000.0 >= 0.25:
                        key = key + word
                    elif '今' in word and score/1000.0 >= 0.3:
                        key = key + word
                    elif '何時' in word and score/1000.0 >= 0.3:
                        key = key + word
                    elif 'アドレス' in word and score/1000.0 >= 0.3:
                        key = key + word
                    elif '教えて' in word and score/1000.0 >= 0.3:
                        key = key + word
                    elif ( 'もう一度' in word or 'もう一回' in word) and score/1000.0 >= 0.3:
                        key = key + word
                    elif '言って' in word and score/1000.0 >= 0.3:
                        key = key + word

                # 認識された全ての単語に対して処理を実施
                print('[DEBUG]---- : input key is ', key)
                if 'Ping' in key:
                    exec_cmd.response(word=key,wav=responsesoundfile)
                    exec_cmd.ping(target=pingtarget, count=pingcount, interval=pinginterval, read='on')
                elif '何時' in key:
                    exec_cmd.response(word=key,wav=responsesoundfile)
                    exec_cmd.date(read='on')
                elif 'アドレス' in key:
                    exec_cmd.response(word=key,wav=responsesoundfile)
                    exec_cmd.getaddress(read='on')
                elif ('もう一度' in key or 'もう一回' in key):
                    exec_cmd.response(word=key,wav=responsesoundfile)
                    exec_cmd.recall(read='on')



            print('[DEBUG]---- : data list is initialized ')
            data = ''

        else:
            print('[DEBUG]---- : NO tag is found !! recieved data is :\n', \
                    new_data.replace('>','>\n'))
            data = data + new_data

if __name__ == '__main__':

    # JSONファイルの読み込み
    jfile = 'setting.json'
    jsondata = readjson(jfile)

    # 事前設定
    setenv(jsondata)

    try:
        speech2text(jsondata)

    except KeyboardInterrupt:
        print('keyboard interrupt')
