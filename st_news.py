"""
STRAITS TIMES NEWS SUMMARIZER
Author: Ahthon
Date created: 14 Oct 2017
Date last modified: 27 Dec 2017
"""

import re
import requests
import statistics
import time

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


def soup(url):
    """Returns html soup.
    """
    html = request.urlopen(url).read().decode("utf-8")
    html_soup = BeautifulSoup(html, "html.parser")
    return(html_soup)


def get_cat_urls(cat_soup, limit=10):
    """Returns urls of the headlines of a certain news category.
    """
    st_url = "http://www.straitstimes.com"
    headlines = str(cat_soup.find_all(
        "span", class_="story-headline", limit=limit))
    hrefs = re.findall('href=\"(.*?)\"', headlines)
    urls = [st_url+url for url in hrefs if hrefs and "javascript" not in url]
    return(urls)


def get_news_title(news_soup):
    """Returns news title.
    """
    title = news_soup.find("h1", class_="headline node-title")
    title = title.string
    return(title)


def get_news_byline(news_soup):
    """Returns news byline/author. Returns '--' if none is found.
    """
    author = news_soup.find(
        "div", class_="author-field author-name")
    designation = news_soup.find(
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


def get_news_text(news_url):
    """Returns news text
    """
    html = requests.get(news_url).text
    text = fulltext(html)
    return(text)


def get_article_js(news_soup):
    script = str(news_soup.find_all("script", limit=3)[-1])
    return(script)


def get_news_id(news_js):
    target = '"articleid".*"(\d*)"'
    article_id = re.search(target, news_js)
    if article_id:
        return(article_id.group(1))


def get_news_datetime(news_js):
    """Returns publication date and time (yyyy:mm:dd hh:mm) of news.
    """
    target = "(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2})"
    pubdate = re.search(target, news_js)
    if pubdate:
        return(pubdate.group(1).split(" "))


def get_news_date(news_datetime):
    """Returns news's datetime.
    """
    pubdate = news_datetime[0]
    date = pubdate.split(":")

    year = date[0]
    month = date[1]
    day = date[2]

    months = {
        "1": "Jan",
        "2": "Feb",
        "3": "Mar",
        "4": "Apr",
        "5": "May",
        "6": "Jun",
        "7": "Jul",
        "8": "Aug",
        "9": "Oct",
        "10": "Sep",
        "11": "Nov",
        "12": "Dec"
    }

    month_name = months.get(month)

    news_date = "{} {} {}".format(day, month_name, year)
    return(news_date)


def get_news_time(news_datetime):
    pubtime = news_datetime[1]
    news_time = pubtime + " Hours"
    return(news_time)


def get_news_keywords(news_js):
    """Returns a list of news topics/tags.
    """
    target = '"keyword".*"(.*)"'
    keyword = re.search(target, news_js)
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


def main(ori_news=True):

    # record percentage reduction of words in summary
    reduction = []

    # news categories
    print("Collecting categories.")
    sg = soup("http://www.straitstimes.com/singapore")
    asia = soup("http://www.straitstimes.com/asia")
    world = soup("http://www.straitstimes.com/world")
    politics = soup("http://www.straitstimes.com/politics")
    biz = soup("http://www.straitstimes.com/business")
    sci = soup("http://www.straitstimes.com/tags/science")

    # urls of articles for each category
    print("Building articles.")
    sg_headlines = get_cat_urls(sg)
    asia_headlines = get_cat_urls(asia)
    world_headlines = get_cat_urls(world)
    pol_headlines = get_cat_urls(politics)
    biz_headlines = get_cat_urls(biz)
    sci_headlines = get_cat_urls(sci)

    # urls of articles, category name, filename
    st_news = [
        (sg_headlines, "Singapore", "Singapore_News.txt"),
        (asia_headlines, "Asia", "Asia_News.txt"),
        (world_headlines, "World", "World_News.txt"),
        (pol_headlines, "Politics", "Politics_News.txt"),
        (biz_headlines, "Business", "Business_News.txt"),
        (sci_headlines, "Science", "Science_News.txt")
    ]

    # text file containing headlines for e-mail
    emailfile = open("ST_headlines.txt", mode="w", encoding="utf-8")
    date = time.strftime("%d %b %Y")
    print_tofile("News for {}".format(date), emailfile)

    print("Summarizing articles.\n")
    # look at each news category
    for (headlines, cat, fname) in st_news:
        print(cat)
        cat_title = cat+"\n"+"="*len(cat)

        # output, summary
        sumfname = "s_"+fname
        sumfile = open(sumfname, mode="w", encoding="utf-8")
        print_tofile(cat_title, sumfile)

        # output, original
        newsfname = "o_"+fname
        newsfile = open(newsfname, mode="w", encoding="utf-8")
        print_tofile(cat_title, newsfile)

        # output, e-mail file
        print_tofile(cat_title, emailfile, lbreak=False)

        # look at each news article
        for news_url in headlines:
            print("\t"+news_url[27:])

            # word count
            wcount_summ = 0
            wcount_news = 0

            # news article data
            news_html = soup(news_url)
            news_js = get_article_js(news_html)
            news_datetime = get_news_datetime(news_js)
            news_date = get_news_date(news_datetime)
            news_time = get_news_time(news_datetime)
            news_id = get_news_id(news_js)
            news_title = get_news_title(news_html)
            news_byline = get_news_byline(news_html)
            news_keywords = get_news_keywords(news_js)
            news_text = get_news_text(news_url)
            wcount_news += word_count(news_text)

            # output, e-mail headlines
            print_tofile("• "+news_title, emailfile, lbreak=False)
            print_tofile(news_keywords, emailfile, lbreak=False)
            print_tofile(news_url, emailfile)

            # output, summary
            print_tofile(news_title.upper(), sumfile)
            print_tofile(news_url, sumfile)
            print_tofile(news_byline, sumfile)
            print_tofile(news_date+", "+news_time, sumfile)

            # length of summary
            sents_in_summary = int(0.3*sent_count(news_text))

            # summary text
            news_summary = get_summary(news_url, sents_in_summary)
            news_lead = sent_tokenize(news_text)[0]
            if news_lead not in news_summary[0:1]:
                print_tofile(news_lead, sumfile)
                wcount_summ += word_count(news_lead)
            for sent in news_summary:
                print_tofile(sent, sumfile)
                wcount_summ += word_count(sent)

            print_tofile(news_keywords, sumfile)
            print_divider(sumfile)

            # output, original
            print_tofile(news_title.upper(), newsfile)
            print_tofile(news_url, newsfile)
            print_tofile(news_byline, newsfile)
            print_tofile(news_date+", "+news_time, newsfile)
            print_tofile(news_text, newsfile)
            print_tofile(news_keywords, newsfile)
            print_divider(newsfile)

            # reduction in words
            reduction.append((wcount_news-wcount_summ)/wcount_news)
        sumfile.close()
        newsfile.close()
    emailfile.close()

    mean_reduction = statistics.mean(reduction)
    stdev_reduction = statistics.stdev(reduction)
    print("\nMean reduction of words: {:.1f}%, SD: {:.2f}.".format(
        (mean_reduction*100), stdev_reduction))
    print("")


if __name__ == "__main__":
    print(st_summarizer)
    main()
    send_email()  # e-mail headlines and summaries
