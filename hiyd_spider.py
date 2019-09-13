# 导入需要使用的工具
from selenium import webdriver
from lxml import etree
import re
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib import request
import csv
import os
import multiprocessing

# 1.获取数据的函数封装
def get_details():
    # 1.1selenium的初始化
    # 指定driver的路径
    driver_path = r"C:\Users\Administrator\Desktop\python\chromedriver.exe"
    # 返回一个driver对象
    driver = webdriver.Chrome(executable_path=driver_path)
    details = []
    # 1.2构建请求：获取数据
    for i in range(67,70):
        url = "https://www.hiyd.com/dongzuo/{}/".format(i)
        print(url)
        if url == "https://www.hiyd.com/dongzuo/1/":
            # 首页无需切换
            driver.get(url=url)
        else:
            # 切换至之前打开的空页面，进行页面的打开
            driver.switch_to.window(driver.window_handles[0])
            driver.get(url=url)
        # 1.3设置等待
        time.sleep(2)
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "jp_video_0")))
        # 1.4获取渲染后的网页源码
        content = driver.page_source
        # 1.5进行xpath的解析
        response = etree.HTML(content)
        # 1.6使用xpath获取数据
        name = response.xpath("//h1[@class='video-title']//text()")[0]
        type = response.xpath("//div[@class='info-main']//div[1]//p[1]//em//text()")[0]
        level = response.xpath("//div[@class='info-main']//div[1]//p[2]//em//text()")[0]
        infos = response.xpath("//div[@class='guide-text']//pre//text()")[0]
        info = re.sub(r"\s", "", infos)
        try:
            video = response.xpath("//video[@id='jp_video_0']//@src")[0]
        except:
            driver.execute_script("window.open()")
            driver.close()
            continue
        # 1.7整合存储的数据
        detail = {"name": name, "type": type, "level": level, "info": info, "video": video}
        print(detail)
        details.append(detail)
        driver.execute_script("window.open()")
        driver.close()
    driver.quit()
    return details


# 2.写入数据的函数封装
def write_detail(details):
    # 2.1定义表头
    headers = ["name","type","level","info","video"]
    # 2.2打开文件
    with open("hiyd.csv","w",encoding="utf-8") as f:
        # 2.3写入表头
        writer = csv.DictWriter(f,headers)
        # 2.4写入数据
        writer.writerows(details)

# 3.视频下载的函数封装
def video_download(detail):
    # 3.1定义存储的路径
    path = os.path.join(os.path.dirname(__file__))
    if not os.path.exists(path):
        os.mkdir(path)
    video = detail["video"]
    name = detail["name"]
    # 3.2组合类型
    type = detail["type"]
    type_path = os.path.join(path,type)
    if not os.path.exists(type_path):
        os.mkdir(type_path)
    request.urlretrieve(video, os.path.join(type_path,name))

def main():

    details = get_details()
    write_detail(details)
    po = multiprocessing.Pool(3)
    for detail in details:
        po.apply_async(video_download,(detail,))
    po.close()
    po.join()

# 主函数
if __name__ == '__main__':
    main()