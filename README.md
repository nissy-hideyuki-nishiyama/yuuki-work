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

