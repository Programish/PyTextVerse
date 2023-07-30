import nltk
from nltk.corpus import stopwords
import re
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Set up Chrome options to run in headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensure GUI is off
chrome_options.binary_location = "/usr/bin/chrome_binary"  # Replace with the actual path

# Set path to the chromedriver executable
webdriver_path = "/home/programish/chromedriver"  # Replace with your actual path

# Load the web page
df = pd.read_excel("Input.xlsx")
master = pd.read_fwf("MasterDictionary/positive-words.txt", header=None, encoding='latin-1')
positive = list(master[0])
master = pd.read_fwf("MasterDictionary/negative-words.txt", header=None, encoding='latin-1')
negative = list(master[0])
path = '/home/StopWords'
dir_list = os.listdir(path)
my_stopwords = list()

def splitter(value):
    ls = str(value).split()
    return ls[0]

for i in dir_list: 
    f = os.path.join(path, i)
    words = pd.read_fwf(f, header=None, encoding='latin-1')
    words[0] = words[0].apply(splitter)
    my_stopwords.extend(words[0])

res_df = df
res_df['POSITIVE SCORE'] = int()
res_df['NEGATIVE SCORE'] = int()
res_df['POLARITY SCORE'] = float()
res_df['SUBJECTIVITY SCORE'] = float()
res_df['AVG SENTENCE LENGTH'] = float()
res_df['PERCENTAGE OF COMPLEX WORDS'] = float()
res_df['FOG INDEX'] = float()
res_df['AVG NUMBER OF WORDS PER SENTENCE'] = float()
res_df['COMPLEX WORD COUNT'] = int()
res_df['WORD COUNT'] = int()
res_df['SYLLABLE PER WORD'] = float()
res_df['PERSONAL PRONOUNS'] = int()
res_df['AVG WORD LENGTH'] = float()

stopwords = stopwords.words('english')

for link in df.URL:

# Create a new Chrome instance
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    driver.get(link)

# Wait for the page to fully load (you can increase the sleep time if needed)
    time.sleep(2)

# Extract the page source
    page_source = driver.page_source

# Close the browser
    driver.quit()

# Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    class1 = 0
# Extract the article title
    title_element = soup.find("h1", class_="entry-title")
    title = title_element.text.strip() if title_element else "Title not found"
    if title == "Title not found":
        class1 = 1
        title_element = soup.find("h1", class_="tdb-title-text")
        title = title_element.text.strip() if title_element else "Title not found"

# Extract the article text
    article_text = ""
    text_class = "td_block_wrap tdb_single_content tdi_130 td-pb-border-top td_block_template_1 td-post-content tagdiv-type" if class1 else "td-post-content tagdiv-type"
    content_element = soup.find("div", class_=text_class)
    if content_element:
        for paragraph in content_element.find_all(["p", 'li']):
            article_text += paragraph.text.strip() + "\n"
    else:
        article_text = "Article text not found"
    
    total_words = len(re.split(r"\n|' '", article_text))

# Calculating total number of sentences
    length = sum(1 for i in article_text if i == '.')

    article_text_ls = article_text.split()
    for i in range(len(article_text_ls)):
        if article_text_ls[i] != 'US':
            article_text_ls[i] = article_text_ls[i].lower()
    article_text = ' '.join(article_text_ls)    

    article_text = re.sub(r"[!\"#$%&\'()*+,-.:;<=>?@\[\\\]^_`{|}~]", "",article_text)    
    
    pronouns = 0
    for word in article_text_ls:
        if word in ('i', 'we', 'ours', 'us', 'my'):
            pronouns += 1

    msg = re.split(r"\n|' '", article_text)
    sentence = []
    for word in msg:
        if word not in my_stopwords:
            sentence.append(word)
    corpus = " ".join(sentence)

    res_text = corpus
    pos, neg = 0, 0
    for word in res_text.split():    
        if word in positive:
            pos += 1
        elif word in negative:
            neg += 1 

    complex_word = 0
    total_syllables = 0
    for word in res_text.split():
        syllable = 0
        if word[-2:] in ('es', 'ed'):
            word = word[:-2]
        for letter in word:
            if letter in ('a', 'e', 'i', 'o', 'u'):
                syllable += 1
                total_syllables += 1
        if syllable > 2:
            complex_word += 1
   
    sentence = list()
    for word in res_text.split():
        if word not in stopwords:
            sentence.append(word)

    total_char = len(res_text.replace(' ', ''))
        
    res_df.loc[res_df.URL==link, 'POSITIVE SCORE'] = pos
    res_df.loc[res_df.URL==link, 'NEGATIVE SCORE'] = neg
    res_df.loc[res_df.URL==link, 'POLARITY SCORE'] = round((pos-neg)/(pos+neg+0.000001), 2)
    res_df.loc[res_df.URL==link, 'SUBJECTIVITY SCORE'] = round((pos+neg)/(len(res_text.split())+0.000001), 2)
    res_df.loc[res_df.URL==link, 'AVG SENTENCE LENGTH'] = (0 if length == 0 else round(len(res_text.split())/length, 2))
    res_df.loc[res_df.URL==link, 'PERCENTAGE OF COMPLEX WORDS'] = round(complex_word/len(res_text.split()), 2)
    res_df.loc[res_df.URL==link, 'FOG INDEX'] = (0 if length == 0 else round( 0.4 * (len(res_text.split())/length + complex_word/len(res_text.split())), 2))
    res_df.loc[res_df.URL==link, 'AVG NUMBER OF WORDS PER SENTENCE'] = (0 if length == 0 else round(total_words/length, 2))
    res_df.loc[res_df.URL==link, 'COMPLEX WORD COUNT'] = complex_word
    res_df.loc[res_df.URL==link, 'WORD COUNT'] = len(sentence)
    res_df.loc[res_df.URL==link, 'SYLLABLE PER WORD'] = round(total_syllables/len(sentence), 2)
    res_df.loc[res_df.URL==link, 'PERSONAL PRONOUNS'] = pronouns
    res_df.loc[res_df.URL==link, 'AVG WORD LENGTH'] = round(total_char/len(sentence), 2)

res_df.to_csv('Output.csv')
