# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
import subprocess
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
    print('[DEBUG]---- : 変更前の設定 -->', end='')
    print(os.getenv('ALSADEV'))
    os.environ['ALSADEV'] = alsadev
    print('[DEBUG]---- : 変更後の設定 -->', end='')
    print(os.getenv('ALSADEV'))

    # 設定結果の確認
    if os.getenv('ALSADEV') != alsadev:
        print('[FAILED]--- : ${ALSADEV}を'+alsadev+'に変更することができませんでした。')
        sys.exit() 
    elif os.getenv('ALSADEV') == alsadev:
        print('[SUCCESS]-- : ${ALSADEV}を'+alsadev+'に変更しました。')

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
    print("[DEBUG]---- : Julius will be started with following parameters...")
    print("[DEBUG]---- :     HMM     : ", hmm)
    print("[DEBUG]---- :     HMMlist : ", hmmlist)
    print("[DEBUG]---- :     Grammar : ", grammar)
    print("[DEBUG]---- :     Strip   : ", strip)
    print("[DEBUG]---- :     Input   : ", infile)
    print("[DEBUG]---- :     Reject  : ", reject)
    print("[DEBUG]---- :     Level   : ", level)
    print("[DEBUG]---- :     Mode    : ", mode)
    stamp = exec_cmd.timestamp()
    back = '> logs/julius-'+stamp+'.log 2>&1'

    cmd = 'julius'+' '+hmm+' '+hmmlist+' '+grammar+' '\
            +strip+' '+infile+' '+reject+' '+level+' '+mode+' '+back
    print(cmd)

    p = Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return p

if __name__ == '__main__':

    # JSONファイルの読み込み
    jfile = 'setting.json'
    jsondata = readjson(jfile)

    # 事前の環境設定
    setenv(jsondata)

    # Juliusの起動
    p = startjulius(jsondata)
    print('[DEBUG]---- : p ;', p)
    #print('[DEBUG]---- : stdout :', stdout)
    #print('[DEBUG]---- : stderr :', stderr)
