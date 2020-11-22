import re
import os
import csv
from bs4 import BeautifulSoup
from selenium import webdriver

# Simple string data cleaner
def cleaner(text):
    text = re.sub("\s{2,}|\"|'|\`|\,|\…|\.|\n|\t|\r|▲|【|】|▶|©", "", text)
    return text

# Generate the urls of snu fact-checking resrouces
base_url = "https://factcheck.snu.ac.kr/v2/facts/{}"
url_list = [base_url.format(str(i + 1)) for i in range(2628)]

# My chrome driver path
chrome_path = os.getcwd() + "/chromedriver"

# Use headless mode
options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("window-size=1920x1080")
options.add_argument("disable-gpu")
# options.add_argument("--disable-gpu")

# Open driver
driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=options)

# Save as .csv format
with open("data/snu_fact_checking.csv", "w", encoding="utf8", newline="") as f:

    # Make the .csv file and write a header
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

        # If the page is deleted, skip
        if soup.find("p", class_="name") == None:
            continue

        try:
            """
            Save each fact-checking news seperately even on the same issue and target.
            In other words, the format of data frame saved in the .csv file is long form.
            Each fact-chekcing news comprise a row.
            """
            for i in range(len(soup.find_all("div", class_="meter-label"))):

                # Target on which the fact-checking news verifying
                target = cleaner(soup.find("p", class_="name").text)

                # The title of the post
                source_title = cleaner(
                    soup.find("div", class_="fcItem_detail_li_p").a.text
                )

                # Url of the source where a suspicion was initially emerged
                try:
                    source_url = soup.find("p", class_="source").a.get("href").strip()
                except AttributeError:
                    source_url = soup.find("p", class_="source").text.strip()

                # Categories of the post classifed by the snu fact check
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

                # Brief introduction on the issue
                abstract = cleaner(soup.find("p", class_="exp").text)

                # Labeling meter in 5 scales
                label_list = cleaner(soup.find_all("div", class_="meter-label")[i].text)

                # Date when the fact-checekin news was written
                fc_date = soup.find_all("div", class_="reg_date")[i].i.text

                # Source url of the original fact-checking news
                try:
                    fc_source = (
                        soup.find_all("div", class_="fcItem_vf_li_right")[i]
                        .find("p", class_="vf_article")
                        .a.get("href")
                        .strip()
                    )
                except AttributeError:
                    fc_source = url

                # write a row to the .csv file
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
