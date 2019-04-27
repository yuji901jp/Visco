# 1. マイク/スピーカーの設定

Raspberry Pi 3 B+で動作させるにはマイクとスピーカーの設定を確認する必要がある。
今回はサンワサプライの400-MC012を使った場合の設定、及び設定内容確認方法について記載する。

[使用機材]
[400-MC012](https://direct.sanwa.co.jp/ItemPage/400-MC012)（400-MC012はマイクとスピーカーが一体型となったUSB機器である。）

## 1-1. マイクの設定確認
まずRaspbian OSのインストールが終わった後、USBマイクを接続する。
Raspberry PiでUSBマイクを使用するにはカード/デバイスという二つの値によって、操作するUSB機器を指定する必要があるため、以下コマンドによって接続したUSBマイクの認識状態を確認する。
```
$ arecord -l
**** ハードウェアデバイス CAPTURE のリスト ****
カード 1: AUDIO [CONEXANT USB AUDIO], デバイス 0: USB Audio [USB Audio]
  サブデバイス: 1/1
  サブデバイス #0: subdevice #0
```
上記の場合、カード1、デバイス0として認識されている。実際の録音にはarecordコマンドによって以下のように実施する。

```
$ arecord -D plughw:1,0 -d 10 -f cd test.wav
録音中 WAVE 'test.wav' : Signed 16 bit Little Endian, レート 44100 Hz, ステレオ
 ~~ 何か話す ~~
$ ls -lsa | grep test.wav
736 -rw-r--r--  1 pi   pi   749812  4月 27 20:31 test.wav
```
上記によってtest.wavファイルが生成されており、一定量のファイル容量があることから正常に音声からファイルへ録音できていることがわかる。

## 1-2. スピーカーの設定確認
次にスピーカーの設定確認を実施する。スピーカーについてもマイクと同様にカード/デバイスという二つの値によって操作するUSB機器を指定する。確認は以下コマンドによって実施できる。
```
$ aplay -l
**** ハードウェアデバイス PLAYBACK のリスト ****
カード 0: ALSA [bcm2835 ALSA], デバイス 0: bcm2835 ALSA [bcm2835 ALSA]
  サブデバイス: 7/7
  サブデバイス #0: subdevice #0
  サブデバイス #1: subdevice #1
  サブデバイス #2: subdevice #2
  サブデバイス #3: subdevice #3
  サブデバイス #4: subdevice #4
  サブデバイス #5: subdevice #5
  サブデバイス #6: subdevice #6
カード 0: ALSA [bcm2835 ALSA], デバイス 1: bcm2835 ALSA [bcm2835 IEC958/HDMI]
  サブデバイス: 1/1
  サブデバイス #0: subdevice #0
カード 1: AUDIO [CONEXANT USB AUDIO], デバイス 0: USB Audio [USB Audio]
  サブデバイス: 1/1
  サブデバイス #0: subdevice #0
```
上記のうち、"USB"という文字列が含まれるものがUSB認識されている機器のため、今回は"CONEXANT USB AUDIO"としてカード1、デバイス0として認識されていることがわかる。実際の動作確認は以下コマンドによって実施できる。今回は1-1で録音したtest.wavを再生してみる。
```
$ aplay -D hw:1,0 test.wav
再生中 WAVE 'test.wav' : Signed 16 bit Little Endian, レート 44100 Hz, ステレオ
```
スピーカーから先ほど1-1で録音した音声が流れれば、正常にUSBスピーカーが動作している。
