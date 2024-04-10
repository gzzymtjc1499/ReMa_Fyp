from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time
import csv
import pandas as pd
import os
import requests
import datetime
from datetime import date
import random
import json
import selenium.webdriver.support.ui as ui

# Transform time
month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
month_dates = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
year = datetime.datetime.now().year
if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
    month_dates[1] = 29


def trans_time(time):
    month = month_list[datetime.datetime.now().month - 1]
    date = datetime.datetime.now().day
    if time == "Yesterday":
        date = date - 1
        if date <= 0 and month != "Jan":
            month = month_list[datetime.datetime.now().month - 2]
            date = month_dates[datetime.datetime.now().month - 2] + date
        elif date <= 0 and month == "Jan":
            month = "Dec"
            date = 31 + date
        time = month + " " + str(date)
    elif time[len(time) - 1] == 'm' or time[len(time) - 1] == 'h':  # actually today
        time = month + " " + str(date)
    elif time[len(time) - 1] == 'd':  # max 7d
        date = date - int(time[0])
        if date <= 0 and month != "Jan":
            month = month_list[datetime.datetime.now().month - 2]
            date = month_dates[datetime.datetime.now().month - 2] + date
        elif date <= 0 and month == "Jan":
            month = "Dec"
            date = 31 + date
        time = month + " " + str(date)
    return time


# Read and store cleaned post links from 'link.txt'
url_list = []
with open("link.txt", "r", encoding='utf-8') as f:
    for line in f.readlines():
        line = line.strip('\n')
        url_list.append(line)

url_list = url_list[5815:]  # for continue running  13+2211+5+1086+113+1045+238+1017+56+537 =

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=chrome_options)

# Navigate to the login page and wait for manual login
driver.get('https://www.teamblind.com/')
time.sleep(3)
driver.find_element(By.XPATH, '//*[@id="wrap"]/header/div/div/div[2]/div[2]/button[1]').click()
time.sleep(3)
driver.find_element(By.XPATH,
                    '//*[@id="app"]/div[3]/div[1]/div/div[2]/div/div/div[2]/div[1]/ul/li[1]/div/input').send_keys(
    '(insert your user name here)')
time.sleep(3)
driver.find_element(By.XPATH,
                    '//*[@id="app"]/div[3]/div[1]/div/div[2]/div/div/div[2]/div[1]/ul/li[2]/div/input').send_keys(
    'insert your password here')
time.sleep(3)
driver.find_element(By.XPATH,
                    '//*[@id="app"]/div[3]/div[1]/div/div[2]/div/div/div[2]/div[1]/div[1]/button/strong').click()
time.sleep(10)

count_post = 0

# Iterate through the URLs and scrape data
for idx, url in enumerate(url_list):
    try:
        driver.get(url)
        count_post += 1
        print("Post No: " + str(count_post) + str(url))
    except:
        print("no this url:" + str(url))
    sleep_time = random.uniform(2, 3)
    print(sleep_time)
    time.sleep(sleep_time)

    # Click and extend the post until the end
    while True:
        # this should be changed according to industry or main topics
        # the last button each page is "see more in xxx industry"
        if driver.current_url == 'https://www.teamblind.com/topics/Layoffs':
            break
        else:
            soup = BeautifulSoup(driver.page_source, 'lxml')  # record the contents each time before click
            try:
                ac = driver.find_element(By.CLASS_NAME, 'btn_more')
                ActionChains(driver).move_to_element(ac).click(ac).perform()
                sleep_time = random.uniform(2, 3)
                print(sleep_time)
                time.sleep(sleep_time)
            except:
                break

    try:  # Find the relevant tags from the page source
        title_tag = soup.body.find("h1", class_="word-break")
        # company_tag = soup.body.find("a", href=True, class_="tag")
        company_tags = soup.body.find_all("div", class_="writer")
        time_tags = soup.body.find_all("span", class_="date")
        like_tags = soup.body.find_all("a", class_="like")

        # Extract the text content from the tags, if they exist
        time_all_level = []
        like_all_level = []
        company_all_level = []

        for each in time_tags:
            if each.get_text(strip=True):
                time_all_level.append(trans_time(each.get_text(strip=True)))
            else:
                time_all_level.append(float("nan"))
        main_time = time_all_level[0]
        time_all_level = time_all_level[1:len(time_all_level)]

        for each in like_tags:
            if each.get_text(strip=True):
                like_all_level.append(each.get_text(strip=True))
            else:
                like_all_level.append(float("nan"))
        main_like = like_all_level[0]
        like_all_level = like_all_level[1:len(like_all_level)]

        for each in company_tags:
            company = each.find("a", href=True, class_="tag")
            if company:
                company_all_level.append(company.get_text(strip=True))
            else:
                company_all_level.append(float("nan"))
        main_company = company_all_level[0]
        company_all_level = company_all_level[1:len(like_all_level) + 1]  # there are some residual company names

        # Get the level-one and level-two replies
        res_all_level = []
        contents_all = soup.body.find_all("div", class_='detail')
        for content in contents_all:
            res_all_level.append(content.get_text(strip=True))
        main_content = res_all_level[0]  # content of the post
        res_all_level = res_all_level[1:len(res_all_level)]

        # Get the level-two-only replies
        res_level_two = []
        temp = soup.body.find_all("div", class_='reply')
        for each in temp:
            elements = each.find_all("div", class_='detail')
            for element in elements:
                res_level_two.append(element.get_text(strip=True))

        # Get the level-one-only replies
        res_level_one = [i for i in res_all_level if i not in res_level_two]
        # print(res_level_one)  # just print

        # Save all data
        reply_one_list = []
        reply_one = {}
        reply_two_list = []

        for i in range(len(res_all_level) + 1):  # iterate through all replies
            if i == len(res_all_level):  # comes to the end
                reply_one['replies'] = reply_two_list
                reply_one_list.append(reply_one)
                break

            if res_all_level[i] in res_level_one:
                if i != 0:  # clear the previous replies
                    reply_one['replies'] = reply_two_list
                    reply_two_list = []
                    reply_one_list.append(reply_one)
                    reply_one = {}
                # generate a new reply-1 dictionary
                reply_one['time'] = time_all_level[i]
                reply_one['like'] = like_all_level[i]
                reply_one['company'] = company_all_level[i]
                reply_one['content'] = res_all_level[i]
            else:  # generate a new reply-2 dictionary
                reply_two = {}
                reply_two['time'] = time_all_level[i]
                reply_two['like'] = like_all_level[i]
                reply_two['company'] = company_all_level[i]
                reply_two['content'] = res_all_level[i]
                reply_two_list.append(reply_two)

        post = {}
        post['time'] = main_time
        post['like'] = main_like
        post['company'] = main_company
        post['content'] = main_content
        post['url'] = url
        post['replies'] = reply_one_list

        with open('results.json', 'a+', encoding='utf-8') as f:
            f.write(json.dumps(post) + '\n')
    except:
        print("Error with this post: " + str(url))
        continue

# Close the WebDriver
driver.quit()

print(count_post)
