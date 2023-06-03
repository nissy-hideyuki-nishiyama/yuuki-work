# yuuki-work

## 事前準備
1. 作業ディレクトリの作成と本gitリポジトリのclone
```bash
cd ~/
mkdir workdir
git clone https://github.com/nissy-hideyuki-nishiyama
```
2. python の venv モジュールのインストール
```bash
cd yuuki-work
python3 -m venv .venv
```
3. venvによる仮想環境の構築とモジュールのインポート
```bash
pip3 install -r requirements.txt
```
4. python仮想環境の起動
```bash
source .venv/bin/activate
# 下記のように コマンドプロンプトに、(.venv)と表示されていればOK
(.venv)$  
```

## プログラムの実行
### 1．なにかの管理ページへの認証と管理ページを表示する
1. ログインIDとパスワードを設定する
login_proc.pyの24-26行目をエディタで編集する
```bash
url_top = 'https://manage-demo-sci-recruit.resv.jp/manage/'
loginid = 'manager'
loginpw = ''
```

2. プログラムの実行
```bash
cd login_session
python3 login_proc.py
```

### 2. 某船舶会社の貨物・コンテナの情報ページに接続する
#### ひとつの貨物追跡番号を指定して、全ての情報を取得する
1. config_yuuki.json をエディタで開いて、cargoの値を検索したい貨物追跡番号に変更する
````bash
    },
    "cargo": "237300139244"
}
````

2. プログラムの実行

各プログラムを実行すると、スクリプトと同じディレクトリにWEBサイトからダウンロードしたHTMLソースページが保存され、最後にメモリ上に格納した貨物情報をJSON形式でダンプ表示する。
一部の項目については、面倒だったのでHTMLタグのものも散在する。
また、エラー処理はほとんどないため、改修してください。
Selenium版とrequests版を2つ用意したのは、下記を確認するため
- HTTPアクセス部分とHTMLページ解析部分は分けて開発すると後々、苦しまない
- クラス定義して書くともっときれいなコードになるけど、今回は面倒なので、止めた

2-1. Selenium版
````bash
cd login_session
python3 nishiyama_dsv.py
````

2-2. requests版
````bash
cd login_session
python3 nishiyama_requests_dsv.py
````

