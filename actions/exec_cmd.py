# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
import subprocess
from datetime import datetime
from time import sleep 

###############################################################################
#                          OSコマンド実行モジュール                           #
#                                                                             #
#  このモジュールではshellコマンドをホストOSレベルで実行する差異に使用される。#
###############################################################################
def oscmd(cmd):
    p = Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_data, stderr_data = p.communicate()

    out = stdout_data.decode()
    output = out.split('\n')

    return output

###############################################################################
#                   タイムスタンプ生成モジュール                              #
#                                                                             #
#  このモジュールではタイムスタンプ用の時刻情報を収集する。                   #
#　収集された時刻情報は主に各モジュールのログファイル名に使用される           #
###############################################################################
def timestamp():
    d = datetime.now()
    stamp = '%s%s%s%s%s%s' % (\
            str(d.year).zfill(4),\
            str(d.month).zfill(2),\
            str(d.day).zfill(2),\
            str(d.hour).zfill(2),\
            str(d.minute).zfill(2),\
            str(d.second).zfill(2))

    return stamp

###############################################################################
#                       テキスト読上げモジュール                              #
#                                                                             #
#  このモジュールではテキストで与えられた文字列をOpen-JTalkによって音声読み   #
#  上げする。使用するためには事前にOpen-JTalkが必要になる。                   #
#   [Open JTalkについて]　http://open-jtalk.sourceforge.net/                  #
#   <option>                                                                  #
#     word         : 読み上げる文字列を受け渡し                               #
#     log - on/off : 読み上げた音声ファイル(wav)を残すか否か                  #
#   <log>                                                                     #
#     logs/jtalk-YYYYMMDDHHMMSS.wav                                           #
###############################################################################
def jtalk(word, log='on'):
    # タイムスタンプの取得
    stamp = timestamp()

    # wavファイル作成用のオプション指定
    open_jtalk=['open_jtalk']
    mech=['-x','/var/lib/mecab/dic/open-jtalk/naist-jdic']
    htsvoice=['-m','/usr/share/hts-voice/mei/mei_normal.htsvoice'] # 音声ファイルの指定
    speed=['-r','1.0']                        # 読み上げ速度指定
    outwav=['-ow','logs/jtalk-'+stamp+'.wav'] # 出力ファイルの指定

    # wavファイルの作成
    cmd=open_jtalk+mech+htsvoice+speed+outwav # コマンドの生成
    p = subprocess.Popen(cmd,stdin=subprocess.PIPE)
    p.stdin.write(word)
    p.stdin.close()
    p.wait()

    # wavファイルの再生
    aplay = ['aplay','-q','logs/jtalk-'+stamp+'.wav']
    oscmd(aplay)

    # ログの削除 
    if log == 'off':
        print("[DEBUG]---- logオプションがoffなのでファイルを削除します", aplay[2])
        cmd = ['rm', '-f', str(aplay[2])]
        p = subprocess.Popen(cmd)

###############################################################################
#                          反応通知モジュール                                 #
#                                                                             #
#  このモジュールでは音声から正常に単語を識別できた際の反応を定義する。       #
#   <option>                                                                  #
#     word    : 認識された文字列を受け渡す                                    #
#     wav     : 反応時に再生する音声ファイルを指定(wav形式)                   #
#   <log>                                                                     #
#     logs/response-YYYYMMDDHHMMSS.log                                        #
###############################################################################
def response(word, wav='sounds/response.wav'):
    path = 'logs/response-'+timestamp()+'.log'
    cmd = ['aplay', wav]
    print("[DEBUG]---- ["+word+"]と認識しました。認識音["+wav+"]を再生中です。")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_data, stderr_data = p.communicate()

    with open(path, mode='w') as f:
        f.write("[DEBUG]---- ["+word+"]と認識しました。認識音["+wav+"]を再生します。")

    return

###############################################################################
#                          Ping試験モジュール                                 #
#                                                                             #
#  このモジュールでは指定されたIPアドレスに対してPing試験を実施する。IPv4のみ #
#  対応しており、試験回数、試験間隔をパラメーターで定義することができる。     #
#   <option>                                                                  #
#     target        : Pingを打つIPv4アドレスを指定                            #
#     count         : Pingを打つ回数を指定                                    #
#     interval      : Pingを打つ間隔を指定[秒](0.2以上を指定)                 #
#     read - on/off : 結果の読み上げをするか否か                              #
#   <log>                                                                     #
#     logs/ping-YYYYMMDDHHMMSS.log                                            #
###############################################################################
def ping(target='8.8.8.8', count='5', interval='0.2', read='off'):
    cmd = ['ping', target, '-c', count, '-i', interval]
    path = 'logs/ping-'+timestamp()+'.log'

    if read is 'on':
        joutput = "ピング試験を実行します。"
        joutput = joutput.encode('utf-8')
        jtalk(joutput)
        sleep(2)

    cmd_ping = str(cmd[0])+" "+\
               str(cmd[1])+" "+\
               str(cmd[2])+" "+\
               str(cmd[3])+" "+\
               str(cmd[4])+" "+\
               str(cmd[5])
    print("[STARTED]-- Ping試験を実行します。("+cmd_ping+")")

    with open(path, mode='w') as f:
        f.write("[STARTED]-- Ping試験を実行します。("+cmd_ping+")")
        for line in oscmd(cmd):
            f.write(line+'\n')
            if "packet loss" in line:
                val = line.split(' ')
                loss = val[5].strip().replace('%','')
                if loss == '0':
                    output = target+"までロスなくPingが実行されました。"
                    print("[SUCCESS]-- "+output)
                    f.write("[SUCCESS]-- "+output)

                    if read is 'on':
                        output = target+"までロスなくピングが実行されました。"
                        output = output.encode('utf-8')
                        jtalk(output)
                else:
                    output = target+"まで"+loss+"%のPingロスがありました。"
                    print("[FAILED]--- "+output)
                    f.write("[FAILED]--- "+output)

                    if read is 'on':
                        joutput = target+"まで"+loss+"%のピングロスがありました。"
                        joutput = joutput.encode('utf-8')
                        jtalk(output)

    return

###############################################################################
#                          時刻確認モジュール                                 #
#                                                                             #
#  このモジュールでは本スクリプトが実行されるサーバから時刻情報を取得し、     #
#  現在の時刻を返答する。                                                     #
#   <option>                                                                  #
#     read - on/off : 音声の読み上げを指定                                    #
#   <log>                                                                     #
#     logs/date=YYYYMMDDHHMMSS.log                                            #
###############################################################################
def date(read='off'):
    path = 'logs/date-'+timestamp()+'.log'
    d = datetime.now()
    output = '今日は%s月%s日、時間は%s時%s分です。' % (d.month, d.day, d.hour, d.minute)
    print("[SUCCESS]-- "+output)

    with open(path, mode='w') as f:
        f.write("[SUCCESS]-- "+output)

    if read is 'on':
        output = output.encode('utf-8')
        jtalk(output)

    return

###############################################################################
#                          再度再生モジュール                                 #
#                                                                             #
#  このモジュールでは直前に再生された音声メッセージを再度再生する。           #
#   <option>                                                                  #
#     read - on/off : 音声の読み上げを指定                                    #
###############################################################################
def recall(read='on'):
    cmd = ['ls', 'logs']
    time = []

    # ファイル名からタイムスタンプ部を抽出
    for line in oscmd(cmd):
        if len(line) != 0:
            line = line.split('-')
            key = line[1].split('.')
            if key[1] == 'wav':
                if len(time) == 0:
                    time = key[0]
                else:
                    if int(time) <= int(key[0]):
                        time = key[0]

    # 処理内容の再生
    joutput = "最後に再生されたメッセージをもう一度再生します。"
    joutput = joutput.encode('utf-8')
    print("            前半メッセージを再生中")
    jtalk(joutput, log='off')

    # 最後に再生されたメッセージを再生
    aplay = ['aplay','-q','logs/jtalk-'+time+'.wav']
    print("            後半メッセージ"+aplay[2]+"を再生中")
    wr = subprocess.Popen(aplay, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_data, stderr_data = wr.communicate()
