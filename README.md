### Introduction of the project

This is the first year paper project of my research master. This project applies web scrapping technique and NLP method to model the topics of layoffs posts in an anonymous professional community.
We scrapped the post contents on TeamBlind, a large online job discussing platform in north America. We got all the post contents from late 2022 to July 2023, when there were mass layoff in north America. We then applied NLP method to all the posts to analyze the main topics and keywords about layoff.

### How to use the code
1. Run `1_get_links.py` to get the posts from TeamBlind with your own account. This code will generate a link.txt file with all the links of the main posts.
2. Run `2_get_post_content.py` to get all the contents, and other information of the posts. The code will generate a results.json file to store a structured version of the posts.
3. Run `3_analyze_post_content.py` to analyze the topics and keywords of the posts
Note 1: the code of step 1 & 2 may not be valid anymore because of the change of the website.
Note12: the link.txt and results.zip contains the data I got in July 2023.
