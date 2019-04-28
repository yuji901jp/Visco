#!/bin/sh

# 実行引数をチェック
if [ $# -ne 1 ]; then
	echo "実行引数の渡し方が不適切です。以下のように辞書ファイル名だけを指定してください。"
	echo ""
	echo " $ ./edit-dict.sh <辞書ファイル名>"
	echo ""
	exit 1;
fi

# 編集する辞書ファイル名の取得
dic=$1

# 読みファイルへの単語追加
echo "##現在、以下の単語が辞書("$dic")に登録されています。==============================="
cat $dic.yomi
echo "##新規に辞書登録する単語を入力してください。-------------------------"
echo "##    入力例：$テスト<tab>てすと"
read word
echo "$word" >> ./$dic.yomi

# 読みファイルから音素ファイルの作成
cat $dic.yomi | yomi2voca.pl > $dic.phone 2>&1
#iconv -f utf8 -t eucjp ./$1.yomi | yomi2voca.pl | iconv -f eucjp -t utf8 > $1.phone >> $1.log 2>&1
iconv -f utf8 -t eucjp $dic.phone > $dic.euc >> $dic.log 2>&1

# 編集後の登録単語と要素の確認
echo "現在以下の単語が辞書("$dic")に登録されています。---------------------"
cat $dic.phone
cat $dic.phone >> $dic.log 2>&1

# 辞書ファイルを作成
mkdfa.pl $dic >> $dic.log 2>&1

echo ""
echo "新規単語を読みファイル、音素ファイルへ追加しました。------------------"
echo "文法ファイル("$dic".grammar)と語彙ファイル("$dic".voca)を編集してから辞書ファイルを生成してください"
echo "    $ mkdfa.pl "$dic
echo ""

