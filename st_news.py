"""
STRAITS TIMES SUMMARIZER
Author: ahthon
Date created: 14 Oct 2017
Date last modified: 2 Jan 2018
"""

import re
import requests
import statistics
import sys
import time

from news_config import *
from email_config import *

from bs4 import BeautifulSoup
from newspaper import fulltext
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import sent_tokenize
from st_email import send_email
from summarizer import get_summary
from urllib import request

st_summarizer = """
       ______           _ __        _______
      / __/ /________ _(_) /____   /_  __(_)_ _  ___ ___
     _\ \/ __/ __/ _ `/ / __(_-<    / / / /  ' \/ -_|_-<
    /___/\__/_/  \_,_/_/\__/___/   /_/ /_/_/_/_/\__/___/
       _  __                 ____                          _
      / |/ /__ _    _____   / __/_ ____ _  __ _  ___ _____(_)__ ___ ____
     /    / -_) |/|/ (_-<  _\ \/ // /  ' \/  ' \/ _ `/ __/ /_ // -_) __/
    /_/|_/\__/|__,__/___/ /___/\_,_/_/_/_/_/_/_/\_,_/_/ /_//__/\__/_/

"""


def html_soup(url):
    """Returns html soup.
    """
    html = request.urlopen(url).read().decode("utf8")
    html_soup = BeautifulSoup(html, "html.parser")
    return(html_soup)


def get_urls_of_cat(cat_soup, headline_count):
    """Returns urls of the headlines of a certain news category.
    """
    st_url = "http://www.straitstimes.com"
    headlines = str(cat_soup.find_all(
        "span", class_="story-headline", limit=headline_count))
    hrefs = re.findall('href=\"(.*?)\"', headlines)
    urls = [st_url+url for url in hrefs if hrefs and "javascript" not in url]
    return(urls)


def get_cat_in_url(url):
    """Returns an article's category from its url.
    """
    pattern = "straitstimes.com/(\w*)/"
    cat = re.search(pattern, url)
    if cat:
        cat = cat.group(1).title()
        return(cat)
    else:
        return(None)


def get_subcat_in_url(url):
    """Returns an article's subcategory from its url.
    """
    pattern = "straitstimes.com/\w*/([a-z-].*)/"
    subcat = re.search(pattern, url)
    if subcat:
        subcat = subcat.group(1).title()
        if subcat == "Australianz":
            subcat = "Australia-NZ"
        elif subcat == "Se-Asia":
            subcat = "SE-Asia"
        return(subcat)
    else:
        return(None)


def get_article_title(article_soup):
    """Returns news title.
    """
    title = article_soup.find("h1", class_="headline node-title")
    title = title.string
    return(title)


def get_article_byline(article_soup):
    """Returns news byline/author. Returns '--' if none is found.
    """
    author = article_soup.find(
        "div", class_="author-field author-name")
    designation = article_soup.find(
        "div", class_="author-designation author-field")

    if author and designation:
        author = author.string
        designation = designation.string
        return(str(author+" | "+designation))
    elif author:
        author = author.string
        return(author)
    else:
        return("--")


def get_article_text(article_url):
    """Returns news text
    """
    html = requests.get(article_url).text
    text = fulltext(html)
    return(text)


def get_article_js(article_soup):
    """Returns article's html (script tag)
    """
    script = str(article_soup.find_all("script", limit=3)[-1])
    return(script)


def get_article_id(article_js):
    """ Returns article ID.
    """
    target = '"articleid".*"(\d*)"'
    article_id = re.search(target, article_js)
    if article_id:
        return(article_id.group(1))


def get_article_datetime(article_js):
    """Returns publication date and time (yyyy:mm:dd hh:mm) of news.
    """
    target = "(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2})"
    pubdate = re.search(target, article_js)
    if pubdate:
        return(pubdate.group(1).split(" "))


def get_article_date(article_datetime):
    """Returns article's published datetime.
    """
    pubdate = article_datetime[0]
    date = pubdate.split(":")

    year = date[0]
    month = date[1]
    day = date[2]

    months = {
        "01": "Jan",
        "02": "Feb",
        "03": "Mar",
        "04": "Apr",
        "05": "May",
        "06": "Jun",
        "07": "Jul",
        "08": "Aug",
        "09": "Oct",
        "10": "Sep",
        "11": "Nov",
        "12": "Dec"
    }

    month_name = months.get(month)

    article_date = "{} {} {}".format(day, month_name, year)
    return(article_date)


def get_article_time(article_datetime):
    """Returns article's published time.
    """
    pubtime = article_datetime[1]
    article_time = pubtime + " Hours"
    return(article_time)


def get_article_keywords(article_js):
    """Returns a list of news topics/tags.
    """
    target = '"keyword".*"(.*)"'
    keyword = re.search(target, article_js)
    if keyword:
        keywords = keyword.group(1).split(",")
    return(keywords)


def print_tofile(text, file, lbreak=True):
    """Prints to file some text.
    """
    print(text, file=file)

    # print new, empty line
    if lbreak is True:
        print("", file=file)


def print_divider(file):
    """Prints fancy divider.
    """
    print_tofile("***", file)


def word_count(text):
    """Returns word count.
    """
    tokenizer = RegexpTokenizer(r"\w(?:[-\w]*\w)?")
    count = len(tokenizer.tokenize(text))
    return(count)


def sent_count(text):
    """Returns sentence count.
    """
    count = len(sent_tokenize(text))
    return(count)


def main(todays_news, email_news):

    # today's date
    date_now = time.strftime("%d %b %Y")
    print(st_summarizer)
    print("  Collecting news for {}.\n".format(date_now))

    # statistics and counters
    reduction = []
    summarized = 0
    articles_fetched = 0

    # news categories' html soup
    print("  Fetching categories...")
    for (cat, cat_url, fname) in st_categories:
        print("\t[{}]".format(cat))
    print("  Categories fetched: {}\n".format(len(st_categories)))

    # urls of articles for each category
    print("  Fetching articles...")
    st_cats = []
    for (cat, cat_url, fname) in st_categories:
        cat_html = html_soup(cat_url)
        headlines = get_urls_of_cat(cat_html, headline_count)
        st_cats.append((headlines, cat, fname))
        articles_fetched += len(headlines)
    print("  Articles fetched: {}\n".format(articles_fetched))

    st_articles = [cat for cat in st_cats]

    # text file containing headlines for e-mail
    emailfile = open("ST_News-Headlines.txt", mode="w", encoding="utf8")
    date = time.strftime("%d %b %Y")
    print_tofile("News headlines on {}".format(date), emailfile)

    print("  Summarizing articles...\n")
    # look at each news category
    for (headlines, cat, fname) in st_articles:
        print("  "+cat.upper())
        cat_title = "\n"+cat.upper()+"\n"+"="*len(cat)

        # output, summary
        sumfname = "s_"+fname
        sumfile = open(sumfname, mode="w", encoding="utf8")
        print_tofile(cat_title, sumfile)

        # output, original
        newsfname = "o_"+fname
        newsfile = open(newsfname, mode="w", encoding="utf8")
        print_tofile(cat_title, newsfile)

        # output, news headlines
        print_tofile(cat_title, emailfile, lbreak=False)

        # article count
        article_count = 0

        # look at each news article
        for article_url in headlines:

            # word count
            wcount_summ = 0
            wcount_news = 0

            # news article data
            article_html = html_soup(article_url)
            article_js = get_article_js(article_html)
            article_datetime = get_article_datetime(article_js)
            article_date = get_article_date(article_datetime)
            article_time = get_article_time(article_datetime)

            if todays_news is True and article_date != date_now:
                # skip to next article if it's not published today
                continue
            else:
                article_count += 1
                cat_in_url = get_cat_in_url(article_url)
                subcat_in_url = get_subcat_in_url(article_url)

                # get news subcategory; otherwise, get main category
                if subcat_in_url is None:
                    subcat_in_url = cat_in_url

            article_id = "#{}".format(get_article_id(article_js))
            article_title = article_id+" "+get_article_title(article_html)
            article_byline = get_article_byline(article_html)
            article_keywords = get_article_keywords(article_js)
            article_text = get_article_text(article_url)
            wcount_news += word_count(article_text)

            print(
                "\t{0:02d}.".format(article_count),
                "[{}]{}".format(article_date, article_title[len(article_id):])
            )

            # output, news headlines
            print_tofile("[{}] {}\n{}".format(
                article_date, article_title, article_url),
                emailfile
            )

            # output, news summary
            print_tofile(article_title, sumfile)
            print_tofile(article_url, sumfile)
            print_tofile("By: "+article_byline, sumfile)
            print_tofile(article_date+", "+article_time, sumfile)

            # length of summary
            sents_in_summary = int(0.3*sent_count(article_text))

            # summarized text
            article_summary = get_summary(article_url, sents_in_summary)
            article_lead = sent_tokenize(article_text)[0]
            if article_lead not in article_summary[0:1]:  # includes lead
                print_tofile(article_lead, sumfile)
                wcount_summ += word_count(article_lead)
            for sent in article_summary:
                print_tofile(sent, sumfile)
                wcount_summ += word_count(sent)

            print_tofile(article_keywords, sumfile)
            print_divider(sumfile)
            summarized += 1

            # output, original news articles
            print_tofile(article_title+" [{}]".format(subcat_in_url), newsfile)
            print_tofile(article_url, newsfile)
            print_tofile("By: "+article_byline, newsfile)
            print_tofile(article_date+", "+article_time, newsfile)
            print_tofile(article_text, newsfile)
            print_tofile(article_keywords, newsfile)
            print_divider(newsfile)

            # reduction in words
            reduction.append((wcount_news-wcount_summ)/wcount_news)

        print_divider(emailfile)
        sumfile.close()
        newsfile.close()

        if article_count == 0:  # no news for today
            print(
                "\t{0:02d}.".format(article_count),
                "[{}] [No Updates]".format(date_now)
            )
        print("")

    mean_reduction = statistics.mean(reduction)
    stdev_reduction = statistics.stdev(reduction)
    print("  Articles summarized: {}".format(summarized))
    print("  Mean reduction of words: {:.1f}%, SD: {:.2f}\n".format(
        (mean_reduction*100), stdev_reduction))

    emailfile.close()
    if email_news is True:
        send_email(gmail_user, gmail_pwd, send_to)


if __name__ == "__main__":
    main(todays_news, email_news)
