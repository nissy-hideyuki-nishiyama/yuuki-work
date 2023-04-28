## HTMLクローラー関連
import requests
import time

## HTML解析関連
from bs4 import BeautifulSoup
import urllib
## 正規表現
import re

## ファイルIO、システム関連
import sys

# ログ関連
from logging import (
    getLogger,
    StreamHandler,
    Formatter,
    DEBUG, INFO, WARNING, ERROR, CRITICAL
)
from logging.handlers import RotatingFileHandler

url_top = 'https://manage-demo-sci-recruit.resv.jp/manage/'
loginid = 'manager'
loginpw = ''

# ログレベルの設定
_level_fh = 'INFO'
_level_sh = 'DEBUG'

# HTTPのリクエスト回数
http_req_num = int(0)

# loggerの設定
def mylogger():
    """
    ロガーを定義し、ロガーのインスタンスを返す
    """
    global _level_fh, _level_sh
    #ロガーの生成
    logger = getLogger('mylog')
    #出力レベルの設定
    logger.setLevel(DEBUG)
    #ハンドラの生成
    #fh = FileHandler(_logfile_path)
    fh = RotatingFileHandler('/tmp/yuuki_login_proc.log', mode='a', maxBytes=1000000, backupCount=10)
    sh = StreamHandler(sys.stdout)
    # ハンドラーのレベルを設定
    ## ファイルハンドラーのレベル設定
    if _level_fh == 'CRITICAL':
        fh.setLevel(CRITICAL)
    elif _level_fh == 'ERROR':
        fh.setLevel(ERROR)
    elif _level_fh == 'INFO':
        fh.setLevel(INFO)
    elif _level_fh == 'DEBUG':
        fh.setLevel(DEBUG)
    else:
        fh.setLevel(WARNING)
    ## ストリームハンドラーのレベル設定
    if _level_sh == 'CRITICAL':
        sh.setLevel(CRITICAL)
    elif _level_sh == 'ERROR':
        sh.setLevel(ERROR)
    elif _level_sh == 'WARNING' or _level_sh == 'WARN':
        sh.setLevel(WARNING)
    elif _level_sh == 'DEBUG':
        sh.setLevel(DEBUG)
    else:
        sh.setLevel(INFO)
    #ロガーにハンドラを登録
    logger.addHandler(fh)
    logger.addHandler(sh)
    #フォーマッタの生成
    fh_fmt = Formatter('%(asctime)s.%(msecs)-3d [%(levelname)s] [%(funcName)s] [Line:%(lineno)d] %(message)s', datefmt="%Y-%m-%dT%H:%M:%S")
    sh_fmt = Formatter('%(message)s')
    #ハンドラにフォーマッタを登録
    fh.setFormatter(fh_fmt)
    sh.setFormatter(sh_fmt)
    return logger

# 管理ページに接続する
def Connect_ManagePage(url):
    """
    管理ページに接続する
    """
    global http_req_num
    with requests.Session() as ses:
        __res = ses.get(url)
        http_req_num += 1
        __cookies = ses.cookies
        #__cookies = Get_Cookies(__res)
        # for key, value in ses.cookies.items():
        #     print(f"{key} : {value}")
        return ses, __res, __cookies

# リクエストパラメータを作成する
def Create_Request_Parameter(response):
    """
    レスポンスボディを取得し、解析し、リクエストパラメータを作成する
    """
    # ログインのためのリクエストパラメータを作成する
    request_params = {}
    # リクエストボディを作成する
    form_data = {}
    form_data['loginid'] = loginid
    form_data['loginpw'] = loginpw
    form_data['regi2'] = 'ログイン'
    form_data['mode'] = 'auth'
    # リクエストURLを取得する
    login_url = Analystic_FormData(response.text)
    # リクエストパラメータを作成する
    request_params['form_data'] = form_data
    request_params['login_url'] = login_url
    return request_params
    
# ログイン画面を解析し、リクエストパラメータに必要な値を取得する
def Analystic_FormData(form):
    """
    フォームデータを解析し、リクエストパラメータを作成する
    """
    # フォームデータを解析する
    soup =BeautifulSoup(form, "html.parser")
    # 実際にログインするときに必要なURLを取得する
    elems = soup.find_all("form")
    login_url = elems[0]['action']
    return login_url

# セッション、クッキー、リクエストパラメータをセットして、ログインする
def Do_login(session, cookies, request_params):
    """
    ログインして、ログイン後のレスポンスを返す
    """
    global http_req_num
    # HTTPセッションを引き継ぐ
    ses = session
    # リクエストヘッダの初期化と設定
    req_headers = {}
    req_headers['origin'] = 'https://manage-demo-sci-recruit.resv.jp'
    req_headers['referer'] = 'https://manage-demo-sci-recruit.resv.jp/manage/login.php'
    login_url = request_params['login_url']
    form_data = request_params['form_data']
    login_response = ses.post(login_url, cookies=cookies, headers=req_headers, data=form_data)
    http_req_num += 1
    return login_response

# メインルーチン
def main():
    """
    メインルーチン
    """
    global http_req_num
    # ロギングを設定する
    logger = mylogger()
    # 管理ページに接続する
    ( session, res, cookies ) = Connect_ManagePage(url_top)
    # ログインパラメータを作成する
    request_params = Create_Request_Parameter(res)
    # ログインIDとパスワードを入力して、ログインする
    login_res = Do_login(session, cookies, request_params)
    # デバッグのために、ログイン後の管理画面を表示する
    print(login_res.text)
    return logger
    
if __name__ == '__main__':
    # 実行時間を測定する
    start = time.time()
    logger = main()
    # デバッグ用(HTTPリクエスト回数を表示する)
    logger.debug(f'HTTP リクエスト数: {http_req_num} 回数')
    # 実行時間を表示する
    elapsed_time = time.time() - start
    logger.debug(f'HTTP リクエスト時間: {elapsed_time} sec')
    exit()
