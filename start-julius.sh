#!/bin/sh

# 環境変数の設定
export ALSADEV="plughw:1,0"
export JULIUSHOME="/home/pi/julius"

usage() {
	echo $" $ ./start-julius.sh <辞書ファイル名> <動作モード>"
	echo $"  動作モード:"
	echo $"	-server : サーバモードでjuliusを起動し、10500ポートにてリクエストを待機"
	echo $"	-mic    : マイク直接入力でjuliusを起動し、接続されたマイクからの入力を待機"
	echo $""
	exit 0
}

# 実行引数をチェック
if [$# != 2 ]; then
	echo "実行引数の渡し方が不適切です。以下のように辞書ファイル名と動作モードを選択してください。"
	usage
fi

dict=$1
mode=$2

# Juliusの起動
if [ $2 = "-server" ]; then
	julius -C jconf/$dict.jconf -module
elif [ $2 = "-mic" ]; then
	julius -C jconf/$dict.jconf -input mic
else
	echo "不正な動作モードが指定されています。'-server'/'-mic'のいずれかを選択してください。"
	usage
	exit 1;
fi

