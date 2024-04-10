from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import datetime
import time
import csv
import pandas as pd
import os

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=chrome_options)

# Navigate to the target website
driver.get("https://www.teamblind.com/topics/Layoffs")

# Arrange the posts according to post time
ac1 = driver.find_element(By.XPATH, '//*[@id="container"]/div/div/div[1]/div/div[2]/div/span/span/span[2]/a')
ActionChains(driver).move_to_element(ac1).click(ac1).perform()
time.sleep(3)

ac2 = driver.find_element(By.XPATH, '//*[@id="container"]/div/div/div[1]/div/div[2]/div/span/span/span[1]/span/div[1]/ol/li[2]/a/span')
ActionChains(driver).move_to_element(ac2).click(ac2).perform()
time.sleep(3)

# Scroll down the webpage to load more content
js = "return action = document.body.scrollHeight"
height = 0
new_height = driver.execute_script(js)
count = 0
while height < new_height:
    for i in range(height, new_height, 100):
        driver.execute_script('window.scrollTo(0,{})'.format(i))
        time.sleep(0.5)
    height = new_height
    time.sleep(7)
    new_height = driver.execute_script(js)
    count += 1
    if count > 600:  # modify!!! (post number roughly equals to 70 + 20 * count)
        break

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'lxml')
driver.quit()

# Find all post elements on the page
posts = soup.find_all("li")

# Initialize empty lists to store the data
title_list = []
href_list = []
views = []
likes = []
num_comment = []
times = []

# For compositing new urls
base_url = "https://www.teamblind.com"

# Extract information from each post element
for post in posts:
    view_tag = post.find("a", class_="view")
    like_tag = post.find("a", class_="like")
    comment_tag = post.find("a", class_="comment")
    time_tag = post.find("a", class_="time")
    href_tag = []
    title_tag = []
    t = post.find("a", href=True, title=True)
    if t:
        href_tag = t['href']
        title_tag = t['title']

    view = view_tag.get_text(strip=True) if view_tag else None
    like = like_tag.get_text(strip=True) if like_tag else None
    comment = comment_tag.get_text(strip=True) if comment_tag else None
    post_time = time_tag.get_text(strip=True) if time_tag else None

    if title_tag and href_tag and view and like and comment and post_time:
        title_list.append(title_tag)
        href_list.append(base_url+href_tag)
        views.append(view)
        likes.append(like)
        num_comment.append(comment)
        times.append(post_time)

# Process the time information to match the format
month_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
month_dates = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
year = datetime.datetime.now().year
if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
    month_dates[1] = 29

for i in range(0,len(times)):
    month = month_list[datetime.datetime.now().month - 1]
    date = datetime.datetime.now().day

    if times[i] == "Yesterday":
        date = date - 1
        if date <= 0 and month != "Jan":
            month = month_list[datetime.datetime.now().month - 2]
            date = month_dates[datetime.datetime.now().month - 2] + date
        elif date <= 0 and month == "Jan":
            month = "Dec"
            date = 31 + date
        times[i] = month + " " + str(date)
    elif times[i][len(times[i]) - 1] == 'm' or times[i][len(times[i]) - 1] == 'h': # actually today
        times[i] = month + " " + str(date)
    elif times[i][len(times[i]) - 1] == 'd':  # max 7d
        date = date - int(times[i][0])
        if date <= 0 and month != "Jan":
            month = month_list[datetime.datetime.now().month - 2]
            date = month_dates[datetime.datetime.now().month - 2] + date
        elif date <= 0 and month == "Jan":
            month = "Dec"
            date = 31 + date
        times[i] = month + " " + str(date)

print(len(href_list))  #get a number

# Write the extracted URLs to 'link.txt'
href_file = open("link.txt", "a", encoding='utf-8')
for i in range(len(href_list)):
    href_file.write(href_list[i] + '\n')
href_file.close()

# Write the extracted data to 'output.csv'
with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile)
    # Write header (optional)
    csv_writer.writerow(['title', 'href', 'views', 'likes', "comment","time"])
    # Write data
    for row in zip(title_list, href_list, views, likes, num_comment, times):
        csv_writer.writerow(row)
