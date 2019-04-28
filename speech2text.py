# -*- coding: utf-8 -*-
import time
import socket
import re
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
            print("              WORD=", attrib['WORD'],\
                                 " CM=", attrib['CM'],\
                            " CLASSID=", attrib['CLASSID'],
                              " PHONE=", attrib['PHONE'])

            if attrib['WORD'] not in ('[s]', '[/s]'):
                if float(attrib['CM']) > 0.2:
                    print("[FILTERED]--  WORD=", attrib['WORD'],\
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

        print("PRINT OUT FROM julius_speech_to_text section : ", text)
        if callback is not None:
            callback(text)

if __name__ == '__main__':
    try:
        julius_speech_to_text()

    except KeyboardInterrupt:
        print('keyboard interrupt')
