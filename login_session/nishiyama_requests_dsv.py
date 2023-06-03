# モジュールの読み込み
# ## HTMLクローラー関連
import requests
# from selenium import webdriver
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.common import exceptions
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome import service as fs

## HTML解析関連
from bs4 import BeautifulSoup
from bs4.element import nonwhitespace_re
import urllib
import unicodedata
import pprint
## 正規表現
import re

# Pandas関連
import pandas as pd

## ファイルIO、システム関連
import json
import sys
import time
from time import sleep

# ログ関連
from logging import (
    getLogger,
    StreamHandler,
    Formatter,
    DEBUG, INFO, WARNING, ERROR, CRITICAL
)
from logging.handlers import RotatingFileHandler

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

# selenium(chrome)のレスポンスをHTMLファイルを保存する
def save_selenium_html(response, filename):
    with open(filename, mode='w', encoding='utf-8', errors='ignore') as f:
        f.write(response)

# requestsメソッドのレスポンスをHTMLファイルを保存する
def save_requests_html(response, filename):
    html = response.text
    with open(filename, mode='w', encoding='utf-8', errors='ignore') as f:
        f.write(html)

# 設定ファイルの読み込みとConfigオブジェクトの生成
def read_config(cfg_file_name):
    """
    JSON形式のconfigファイルを読み込み、Configのdictに入れる
    """
    with open(cfg_file_name, mode='r', encoding='utf-8', errors='ignore' ) as json_cfg:
        cfg = json.load(json_cfg)
        return cfg

# EverGreenのデータファイルの読み込みとEverオブジェクトの生成
def read_data(cfg):
    """
    CSV形式のファイルを読み込み、column_dataに入れる
    """
    df = {}
    # df = pd.read_csv("/Users/yuuki/Desktop/" + 'ever.csv'  ,encoding="shift-jis")
    df = pd.read_csv(cfg['datacsv']['filepath']  ,encoding=cfg['datacsv']['encoding'])
    df['EVERGREEN'] = df['EVERGREEN'].astype("str")
    column_data = df['EVERGREEN'].tolist()
    column_data = ['0' + item if len(item) == 11 else item for item in column_data]
    return column_data

# Dict型データをJSONファイルとして保存する
def save_dict(cfg, dict):
    """Dict型のデータをjsonファイルとして保存する

    Args:
        cfg (dict): JSON形式のcfgファイル
        dict (dict): 出力したいdict型データ
    Returns:
        filename: _description_
    """
    path = cfg['output_json']
    output_file = open(path, mode="w")
    json.dumps(dict, output_file, indent=2, ensure_ascii=False)
    output_file.close()
    return None

# クローラーのセットアップをする (selenium版のみ)
def setup_driver(cfg):
    """
    seleniumを初期化する
    デバッグ時にはChromeの動作を目視確認するために、options.add_argument行をコメントアウトする。
    ヘッドレスモードを利用する場合は、options.add_argument行のコメントアウトを外す。
    """
    # Chromeを指定する
    chromedriver_location = cfg['chromedriver']['driver_path']
    chrome_service = fs.Service(executable_path=cfg['chromedriver']['driver_path'])
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    # Docker+Python3の場合に必要
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f'--user-agent={cfg["chromedriver"]["user-agent"]}')
    options.binary_location = cfg['chromedriver']['opt_binary']
    # GUIによるデバッグ用。GUIでデバックする場合はこちらを選択する
    #options.binary_location = '/usr/bin/chromium-browser'
    driver = webdriver.Chrome(service=chrome_service, options=options)
    mouse = webdriver.ActionChains(driver)
    return driver , mouse

# トップページに接続し、セッションやCookieを取得する (selenium版)
def prepare_proc(cfg):
    """
    クローラーをセットアップする
    トップページからカードトラキングページに接続し、セッションやCookieを取得する
    """
    global http_req_num
    # クローラーをセットアップする
    ( driver, mouse ) = setup_driver(cfg)
    # クロール開始
    # 待機時間を設定する
    wait = WebDriverWait(driver, 10)
    # トップページにアクセスする
    driver.get(cfg['url']['top'])
    http_req_num += 1
    # 画面のタイトルを確認する
    assert 'ShipmentLink Shipping & Transport ' in driver.title
    # 検索ページがすべて表示されるまで待機する
    wait.until(EC.presence_of_all_elements_located)
    # ファイルに保存する
    _html = driver.page_source
    save_selenium_html(_html, 'top.html')
    return driver

# トップページに接続し、セッションやCookieを取得する (requests版)
def prepace_proc_requests(cfg):
    """トップページに接続し、セッションやCookieを取得する

    Args:
        cfg (_type_): _description_

    Returns:
        _type_: _description_
    """
    global http_req_num
    headers = {}
    headers['user-agent'] = cfg['chromedriver']['user-agent']
    with requests.Session() as ses:
        __html = ses.get(cfg['url']['top'], headers=headers)
        http_req_num += 1
        __cookies = ses.cookies
        return ses, __html, __cookies
    
# カーゴトラッキングページに接続する (selenium版)
def connect_cargo_tracking(cfg, driver):
    """
    カーゴトラッキングページに接続する
    """
    global http_req_num
    # 待機時間を設定する
    wait = WebDriverWait(driver, 10)
    # カーゴトラッキングページを表示する
    driver.get(cfg['url']['cargo_tracking'])
    http_req_num += 1
    # 画面のタイトルを確認する
    assert 'ShipmentLink - Cargo Tracking' in driver.title
    # 検索ページがすべて表示されるまで待機する
    wait.until(EC.presence_of_all_elements_located)
    # ファイルに保存する
    # _html = driver.page_source
    # save_selenium_html(_html, 'cargo.html')
    return driver

# カーゴトラッキングページに接続する　(requests版)
def connect_cargo_tracking_requests(cfg, ses):
    """カーゴトラッキングページに接続する

    Args:
        cfg (dict): 設定dict
        ses (obj): セッション

    Returns:
        res: カーゴトラッキングページのレスポンス
    """
    global http_req_num
    # リクエストヘッダーを作成する
    headers = {}
    headers['User-Agent'] = cfg['chromedriver']['user-agent']
    headers['Referer'] = cfg['url']['top']
    res = ses.post(cfg['url']['cargo_tracking'], headers=headers, cookies=ses.cookies)
    http_req_num += 1
    return ses, res

# カーゴトラッキングページを解析して、フォームデータを取得する
def Analystic_FormData_Cargo_Traking(res):
    """カーゴトラッキングページを解析して、フォームデータを取得する

    Args:
        res (obj): カーゴトラッキングページのレスポンス

    Returns:
        form_keys: POSTメソッド時のフォームデータのキーのリスト
    """
    form_keys = []
    soup = BeautifulSoup(res.text, features='html.parser')
    _form = soup.find('form')
    _form_input = _form.find_all('input', type='hidden')
    for _key in _form_input:
        form_keys.append(_key.attrs['name'])
    return form_keys

# カーゴトラッキングページにカーゴ番号を入力し、カーゴ情報ページを表示する (selenium版)
def get_cargo_basic_info(cfg, driver):
    """
    カーゴ番号を選択し、カーゴ番号を入力し、カーゴ情報ページを表示する
    """
    global http_req_num
    # BookingNoを取得する
    booking_no = cfg['cargo']
    # 待機時間を設定する
    wait = WebDriverWait(driver, 10)
    # ブラウザを操作して値を入力する
    # Bookingのラジオボタンをクリックする
    element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/center/table[2]/tbody/tr/td/form/div/div[2]/table/tbody/tr[1]/td/table/tbody/tr[1]/td[1]/table/tbody/tr/td[2]/div[3]/input')))
    element.click()
    # カーゴ番号を入力する
    element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/center/table[2]/tbody/tr/td/form/div/div[2]/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/table/tbody/tr/td/div[1]/input')))
    element.send_keys(cfg['cargo'])
    # Submitボタンをクリックする
    element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="nav-quick"]/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/table/tbody/tr/td/div[2]/input')))
    element.click()
    # ここでカーゴ情報ページに切り替わる、カーゴ情報が表示されている
    # 画面のタイトルを確認する
    assert 'ShipmentLink - Cargo Tracking' in driver.title
    # カーゴ情報ページがすべて表示されるまで待機する
    wait.until(EC.presence_of_all_elements_located)
    html = driver.page_source
    # ファイルに保存する
    save_selenium_html(html, 'cargo_info_' + booking_no + '.html')
    return driver, html

# カーゴトラッキングページにカーゴ番号を入力し、カーゴ情報ページを表示する (requests版)
def get_cargo_basic_info_requests(cfg, ses, form_keys):
    """カーゴトラッキングページにカーゴ番号を入力し、カーゴ情報ページを表示する

    Args:
        cfg (dict): 設定dict
        ses (obj): セッション

    Returns:
        res: カーゴ情報ページのレスポンス
    """
    global http_req_num
    # リクエストヘッダーを作成する
    headers = {}
    headers['User-Agent'] = cfg['chromedriver']['user-agent']
    headers['Referer'] = cfg['url']['cargo_tracking']
    headers['Origin'] = cfg['url']['top']
    # 空のリクエスト用フォームデータを作成する
    form_data = {}
    for key in form_keys:
        form_data[key] = ''
    # キーを追加する
    form_data['SEL'] = 's_bk'
    # 値を入れてリクエスト用のフォームデータを作成する
    form_data['NO'] = cfg['cargo']
    form_data['bkno'] = cfg['cargo']
    form_data['TYPE'] = 'BK'
    res = ses.post(cfg['url']['cargo_tracking'], headers=headers, data=form_data)
    http_req_num += 1
    # htmlファイルを保存する
    save_requests_html(res, './cargo_info_requests_' + cfg['cargo'] + '.html')
    return ( ses, res.text )

# カーゴ情報ページを解析し、各種のデータをdict形式で取得する
## Bill of Lading No用
def Analystic_FormData_Bill(driver, html):
    """
    カーゴ情報ページを解析し、各種のデータをdict形式で取得する
    """
    return None

## Container No用
def Analystic_FormData_Container(driver, html):
    """
    カーゴ情報ページを解析し、各種のデータをdict形式で取得する
    dict
    """
    return None

## Booking No用
## (selenium版)
#def Analystic_FormData_Booking(driver, html):
## (requests版)
def Analystic_FormData_Booking(cfg, ses, html):
    """
    カーゴ情報ページを解析し、各種のデータをdict形式で取得する
    dict
    """
    # 初期化する
    cargo_info_dict = {}
    _cai_list=[]
    _cai_data = {}
    _form_data = {}
    soup = BeautifulSoup(html, features='html.parser')
    _div = soup.find('div', class_="content_style")
    _table = _div.find_all('table', class_="globalpage")
    # B/L No.　と Vessel Voyage on B/L の値を取得する
    # _ec_table = _table[2].find_all('table', class_="ec-table ec-table-sm")
    # _ec_table = _table[2].find_all('td', class_="f12wrdb2")
    # seleniumと構造が違うため変更する
    _td = _table[2].find_all('td', class_="f12wrdb2")
    bl_no = _td[1].contents[0].string
    bl_vessel = _td[2].contents[0].string
    # Basic Information
    _ec_table = _div.find_all('table', class_="ec-table ec-table-sm")
    _tr = _ec_table[1].find_all('tr')
    # Place of Receipt
    _row_place_of_receipt = _tr[2].find_all('td')
    _place_of_receipt = _row_place_of_receipt[0].contents[0]
    cargo_info_dict['plase_of_receipt'] = unicodedata.normalize("NFKD", _place_of_receipt)
    # Port of Loading
    _row_port_of_loading = _tr[3].find_all('td')
    _port_of_loading = _row_port_of_loading[0].contents[0]
    cargo_info_dict['port_of_loading'] = unicodedata.normalize("NFKD", _port_of_loading)
    # Port of Discharge
    _row_port_of_discharge = _tr[4].find_all('td')
    _port_of_discharge = _row_port_of_discharge[0].contents[0]
    cargo_info_dict['port_of_discharge'] = unicodedata.normalize("NFKD", _port_of_discharge)
    # Place of Delivery
    _row_place_of_dellivery = _tr[5].find_all('td')
    _place_of_dellivery = _row_place_of_dellivery[0].contents[0]
    cargo_info_dict['place_of_dellivery'] = unicodedata.normalize("NFKD", _place_of_dellivery)
    # Exchange Rate
    _row_exchange_rate = _tr[6].find_all('td')
    _exchange_rate = _row_exchange_rate[0].contents[0]
    cargo_info_dict['exchange_rate'] = unicodedata.normalize("NFKD", _exchange_rate)
    # Stowage Code
    _stowage_code = _row_exchange_rate[1].contents[0]
    cargo_info_dict['stowage_code'] = unicodedata.normalize("NFKD", _stowage_code)
    # Booking Status
    _booking_status = _row_exchange_rate[2].contents[0]
    cargo_info_dict['booking_stastus'] = unicodedata.normalize("NFKD", _booking_status).strip()
    # Container Activity Infomation Table
    # requestsのPOSTメソッドで利用するフォームデータを作成する (requests版)
    _form = _div.find_all('form')
    for _input in _form[2].find_all('input'):
        _form_key = _input.attrs['name']
        if _input.has_attr('value'):
            _form_value = _input.attrs['value']
        else:
            _form_value = ''
        _form_data[str(_form_key)] = str(_form_value)
    # Container Row
    _ca_tr = _ec_table[3].find_all('tr')
    # コンテナ情報行の項目を取得する。2行目が取得する対象
    # for _index in _ca_tr[1].find_all('th').string:
    #     _cai_index.append(str(_index))
    # コンテナ情報行を取得する。3行目以降が対象となる
    for _row in _ca_tr[2:]:
        _cai = _row.find_all('td')
        # コンテナ情報を取得する
        _cai_data['no'] = _cai[0].find('a').string
        _cai_data['size'] = _cai[1].find('span').string
        _cai_data['service_type'] = _cai[2].string
        _cai_data['quantity'] = _cai[3].string
        _cai_data['measurement'] = _cai[4].string
        _cai_data['gross_weight'] = _cai[5].string
        _cai_data['tare_weight'] = _cai[6].contents
        _cai_data['method'] = _cai[7].string
        _cai_data['vgm'] = _cai[8].string
        _cai_data['pickup_date'] = _cai[9].string
        _cai_data['pickup_depot'] = _cai[10].string
        _cai_data['full_in_date'] = _cai[11].string
        _cai_data['full_return_to'] = _cai[12].contents
        _cai_data['href'] = _cai[0].find('a')
        # コンテナの移動情報を取得する (selenium版)
        #_container_move = Display_Container_Move(driver, _cai_data)
        # コンテナの移動情報を取得する (requests版)
        _container_move = Display_Container_Move_requests(cfg, ses, _form_data, _cai_data)
        _cai_list.append(_cai_data)
    # コンテナ情報をdictに保存する
    cargo_info_dict['cai']=_cai_list
    return cargo_info_dict

# 取得したカーゴ情報をBillとContainer、Booking用と個別にファイルに出力する
def Collect_CagoInfo():
    """
    取得したカーゴ情報をBillとContainer、Booking用と個別にファイルに出力する
    """
    return None

# コンテナ移動情報ページを表示する (selenium版)
def Display_Container_Move(driver, cai_data):
    """コンテナ移動ページを表示する

    Args:
        driver: WEBドライバー
        cai_data(dict): コンテナ移動情報
    Returns:
        driver: WEBドライバー
    """
    global http_req_num
    # 待機時間を設定する
    wait = WebDriverWait(driver, 10)
    # javasrciptのタイムアウトを設定する
    driver.set_script_timeout(10)
    # ページロードのタイムアウトを設定する
    driver.set_page_load_timeout(10)
    _href = str(cai_data['href']['href'])
    # javascriptを実行して、カーゴ移動情報ページを表示する
    driver.execute_script(_href)
    http_req_num += 1
    # カーゴ移動情報ページがすべて表示されるまで待機する
    wait.until(EC.presence_of_all_elements_located)
    # ウィンドウハンドルを取得する
    handle_array = driver.window_handles
    # 子ウィンドウに切り替える
    driver.switch_to.window(handle_array[-1])
    # うまく切り替わらないので1秒待機する
    sleep(1)
    # 画面のタイトルを確認する
    assert 'ShipmentLink - Cargo Tracking Container Move Detail' in driver.title
    _html = driver.page_source
    # ファイルに保存する
    save_selenium_html(_html, str('container_move_info_' + cai_data['no'] + '.html'))
    # 取得したコンテナ移動情報ページを分析する
    ( cai_data, _a_href ) = Analystic_FormData_Container_Move(_html, cai_data)
    # Close ボタンをクリックして、子Windowを閉じる
    driver.execute_script(str(_a_href))
    http_req_num += 1
    # 親ウィンドウに戻る
    driver.switch_to.window(handle_array[0])
    return ( driver )

# コンテナ移動情報ページを表示する (requests版)
def Display_Container_Move_requests(cfg, ses, form_data, cai_data):
    """_summary_

    Args:
        ses (_type_): _description_
        cai_data (_type_): _description_

    Returns:
        _type_: _description_
    """
    global http_req_num
    # リクエストヘッダーを作成する
    headers = {}
    headers['User-Agent'] = cfg['chromedriver']['user-agent']
    headers['Origin'] = cfg['url']['top']
    headers['Referer'] = cfg['url']['cargo_tracking']
    # フォームデータのコンテナ番号を書き換える
    form_data['cntr_no'] = cai_data['no']
    # カーゴ情報ページを表示した際のcookiesを設定する
    cookies = ses.cookies
    cookies['TDB1_Function_Type'] = 'quick'
    res = ses.post(cfg['url']['cargo_tracking'], headers=headers, cookies=cookies, data=form_data)
    http_req_num += 1
    # htmlファイルを保存する
    save_requests_html(res, './container_move_info_requests_' + cai_data['no'] + '.html')
    # 取得したコンテナ移動情報ページを分析する
    ( cai_data, _a_href ) = Analystic_FormData_Container_Move(res.text, cai_data)
    return ses, res

# 取得したコンテナ移動情報ページを分析する
def Analystic_FormData_Container_Move(html, cai_data):
    """
    取得したコンテナ移動情報を取得する
    """
    _mv_history = []
    _field_name = []
    soup = BeautifulSoup(html, features='html.parser')
    _table = soup.find('table', class_='ec-table ec-table-sm')
    # Closeボタンの値を取得する
    _a_href = soup.find('a')['href']
    # Containerの移動情報を取得する
    _tr = _table.find_all('tr')
    # Containerの移動情報の項目名を取得する
    _th_field_name = _tr[1].find_all('th')
    for _field in _th_field_name:
        _field_name.append(_field.string)
    # 移動データを取得する
    for _move_data in _tr[2:]:
        _mv = {}
        _mv_data = _move_data.find_all('td')
        n = 0
        for _name in _field_name:
            _mv[_name] = _mv_data[n].string
            n += 1
        _mv_history.append(_mv)
    cai_data['move_history'] = _mv_history
    return ( cai_data, _a_href )

# メインルーチン
def main():
    """
    メインルーチン
    """
    global http_req_num
    # 初期値
    cfg_file_name = "config_yuuki.json"
    # loggerをセットアップする
    logger = mylogger()
    # 設定ファイルを読み込む
    cfg = read_config(cfg_file_name)
    # データファイルを読み込む
    #cargo_data = read_data(cfg)
    # クローラーをセットアップし、トップページに接続して、cookieなどを取得する
    #driver = prepare_proc(cfg)
    ( ses, html, cookie ) = prepace_proc_requests(cfg)
    # カーゴ番号検索ページを表示する
    #driver = connect_cargo_tracking(cfg, driver)
    ( ses, res ) = connect_cargo_tracking_requests(cfg, ses)
     # カーゴ番号検索ページを分析し、フォームデータのキーを取得する
    form_keys = Analystic_FormData_Cargo_Traking(res)
    # カーゴ番号を入力し、カーゴ情報ページを表示する
    #( driver, cargo_info ) = get_cargo_basic_info(cfg, driver)
    ( ses, cargo_info ) = get_cargo_basic_info_requests(cfg, ses, form_keys)
    # カーゴ情報ページを解析し、dictに保存する
    #cargo_info_dict = Analystic_FormData_Booking(driver, cargo_info)
    cargo_info_dict = Analystic_FormData_Booking(cfg, ses, cargo_info)
    # カーゴ情報のdictを表示する
    pprint.pprint(cargo_info_dict)
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
