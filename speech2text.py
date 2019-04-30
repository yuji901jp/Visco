# -*- coding: utf-8 -*-
import time
import socket
import re
import xml.etree.ElementTree as ET
from actions import exec_cmd

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
                if float(attrib['CM']) > 0.3:
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

        if len(text) is not 0:
            exec_cmd.response(word=text, wav='sounds/response.wav')
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
    try:
        julius_speech_to_text()

    except KeyboardInterrupt:
        print('keyboard interrupt')
