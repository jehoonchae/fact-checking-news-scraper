import json
import time
import requests
import re
import os
import sys

import csv
from bs4 import BeautifulSoup
from selenium import webdriver


def cleaner(text):
    text = re.sub("\s{2,}|\"|'|\`|\,|\…|\.|\n|\t|\r|▲|【|】|▶|©", "", text)
    return text


base_url = "https://factcheck.snu.ac.kr/v2/facts/{}"

url_list = [base_url.format(str(i + 1)) for i in range(2628)]

chrome_path = os.getcwd() + "/chromedriver"

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("window-size=1920x1080")
options.add_argument("disable-gpu")
# options.add_argument("--disable-gpu")

driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=options)

with open("data/snu_fact_checking.csv", "w", encoding="utf8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(
        [
            "url",
            "fc_source",
            "fc_date",
            "label_list",
            "target",
            "source_title",
            "source_url",
            "category1",
            "category2",
            "abstract",
        ]
    )
    for url in url_list:
        driver.get(url)
        driver.implicitly_wait(3)
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        if soup.find("p", class_="name") == None:
            continue
        try:
            for i in range(len(soup.find_all("div", class_="meter-label"))):
                target = cleaner(soup.find("p", class_="name").text)
                source_title = cleaner(
                    soup.find("div", class_="fcItem_detail_li_p").a.text
                )
                try:
                    source_url = soup.find("p", class_="source").a.get("href").strip()
                except AttributeError:
                    source_url = soup.find("p", class_="source").text.strip()
                category1 = cleaner(
                    soup.find("div", class_="fcItem_detail_bottom")
                    .find_all("li")[0]
                    .text
                )
                category2 = cleaner(
                    soup.find("div", class_="fcItem_detail_bottom")
                    .find_all("li")[1]
                    .text
                )
                abstract = cleaner(soup.find("p", class_="exp").text)
                label_list = cleaner(soup.find_all("div", class_="meter-label")[i].text)
                fc_date = soup.find_all("div", class_="reg_date")[i].i.text
                try:
                    fc_source = (
                        soup.find_all("div", class_="fcItem_vf_li_right")[i]
                        .find("p", class_="vf_article")
                        .a.get("href")
                        .strip()
                    )
                except AttributeError:
                    fc_source = url
                writer.writerow(
                    [
                        url,
                        fc_source,
                        fc_date,
                        label_list,
                        target,
                        source_title,
                        source_url,
                        category1,
                        category2,
                        abstract,
                    ]
                )
        except AttributeError:
            print(url)
