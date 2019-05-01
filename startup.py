# -*- coding: utf-8 -*-
from actions import exec_cmd
import json
import os
import sys

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

def startjulius(jsondata):
    groupdict = jsondata["Julius"]
    hmm     = groupdict["HMM"]
    hmmlist = groupdict["HMMlist"]
    grammar = groupdict["Grammar"]
    strip   = groupdict["Strip"]
    infile  = groupdict["Input"]
    reject  = groupdict["Reject"]
    level   = groupdict["Level"]
    mode    = groupdict["Mode"]
    print("Julius will be started with following parameters...")
    print("     HMM     : ", hmm)
    print("     HMMlist : ", hmmlist)
    print("     Grammar : ", grammar)
    print("     Strip   : ", strip)
    print("     Input   : ", infile)
    print("     Reject  : ", reject)
    print("     Level   : ", level)
    print("     Mode    : ", mode)
    
    julius  = ['julius']
    hmm     = str(hmm).split(' ')
    hmmlist = str(hmmlist).split(' ')
    grammar = str(grammar).split(' ')
    strip   = str(strip).split(' ')
    infile  = str(infile).split(' ')
    reject  = str(reject).split(' ')
    level   = str(level).split(' ')
    mode    = str(mode).split(' ')
    back    = ['&']

    with open('julius-run.sh', 'w') as f:
        f.write(' '.join(julius)+' ')
        f.write(' '.join(hmm)+' ')
        f.write(' '.join(hmmlist)+' ')
        f.write(' '.join(grammar)+' ')
        f.write(' '.join(infile)+' ')
        f.write(' '.join(strip)+' ')
        f.write(' '.join(reject)+' ')
        f.write(' '.join(level)+' ')
        f.write(' '.join(mode)+' ')
        f.write(' '.join(back)+' > /dev/null')

    stdout, stderr = exec_cmd.oscmd(['sh','julius-run.sh'])

    return stdout, stderr

if __name__ == '__main__':

    # JSONファイルの読み込み
    jfile = 'setting.json'
    jsondata = readjson(jfile)

    # 事前の環境設定
    setenv(jsondata)

    # Juliusの起動
    stdout, stderr = startjulius(jsondata)
