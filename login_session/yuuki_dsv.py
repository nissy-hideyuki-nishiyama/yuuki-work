from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
# import pyautogui
import os
# import pandas as pd
# WebDriverのパスを指定してインスタンスを作成する
# ループする値のリストを定義
# element.send_keys('237300139244')
df = pd.read_csv("/Users/yuuki/Desktop/" + 'ever.csv'  ,encoding="shift-jis")
df['EVERGREEN'] = df['EVERGREEN'].astype("str")
column_data = df['EVERGREEN'].tolist()
column_data = ['0' + item if len(item) == 11 else item for item in column_data]
for loop_value in column_data:
    driver = webdriver.Chrome('/path/to/chromedriver')
    driver.get('https://ct.shipmentlink.com/servlet/TDB1_CargoTracking.do')
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/center/table[2]/tbody/tr/td/form/div/div[2]/table/tbody/tr[1]/td/table/tbody/tr[1]/td[1]/table/tbody/tr/td[2]/div[3]/input')))
    element.click()
    element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/center/table[2]/tbody/tr/td/form/div/div[2]/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/table/tbody/tr/td/div[1]/input')))
    element.send_keys(loop_value)
    element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="nav-quick"]/table/tbody/tr[1]/td/table/tbody/tr[1]/td[2]/table/tbody/tr/td/div[2]/input')))
    element.click()
    html_content = driver.page_source
    # BeautifulSoupを使用してHTMLを解析
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find_all('table', class_='ec-table ec-table-sm')[3]
    elements = table.find_all(class_="#f12rown1 ec-fs-16")
    if elements:
        first_a_element = elements[0].find('a')
        if first_a_element:
            href_value = first_a_element['href']
            print(href_value)
        else:
            print("No <a> element found.")
    else:
        print("No matching elements found.")
    new_href_value = href_value[11:]
    final_href = "return " + new_href_value + ";"
    wait = WebDriverWait(driver, 3)
    result = driver.execute_script(final_href)
    print(result)
    screenshot = pyautogui.screenshot()
    # スクリーンショットを保存
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    screenshot_path = os.path.join(desktop_path, "screenshot.png")
    screenshot.save(screenshot_path)