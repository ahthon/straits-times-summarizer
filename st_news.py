"""
STRAITS TIMES SUMMARIZER
Author: ahthon
Date created: 14 Oct 2017
Date last modified: 01 Sep 2018
"""

import re
import requests
import statistics
import time

from email_config import *
from news_config import *
from st_email import sendEmail
from st_summarizer import summarize

from bs4 import BeautifulSoup
from newspaper import fulltext
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import sent_tokenize
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


def articleHTML(url):
    """Returns html soup.
    """
    html = request.urlopen(url).read().decode("utf8")
    soup = BeautifulSoup(html, "html.parser")
    return(soup)


def articleURLs(soup, url_count):
    """Returns article urls of a certain news category.
    """
    st = "http://www.straitstimes.com"
    hrefs = str(soup.find_all(
        "span", class_="story-headline", limit=url_count))
    urls = re.findall('href=\"(.*?)\"', hrefs)
    urls = [st+url for url in urls if urls and "javascript" not in url]
    urls = [url for url in urls if "multimedia/" not in url]
    return(urls)


def urlCategory(url):
    """Returns an article's category from its url.
    """
    pattern = "straitstimes.com/(\w*)/"
    cat = re.search(pattern, url)
    if cat:
        cat = cat.group(1).title()
        return(cat)
    else:
        return(None)


def urlSubCategory(url):
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


def articleTitle(soup):
    """Returns news title.
    """
    title = soup.find("h1", class_="headline node-title")
    title = title.string
    return(title)


def articleByline(soup):
    """Returns news byline/author. Returns '--' if none is found.
    """
    author = soup.find("div", class_="author-field author-name")
    designation = soup.find("div", class_="author-designation author-field")

    if author and designation:
        author = str(author.string)
        designation = str(designation.string)                     
        return(author+" | "+designation)
    elif author:
        author = str(author.string)
        return(author)
    else:
        return("--")


def articleText(url):
    """Returns news text.
    """
    html = requests.get(url).text
    text = fulltext(html)
    return(text)


def articleJavaScript(soup):
    """Returns article's html (script tag).
    """
    script = str(soup.find_all("script"))
    return(script)


def articleID(js):
    """ Returns art ID.
    """
    target = '"articleid".*"(\d*)"'
    pub_id = re.search(target, js)
    if pub_id:
        return(pub_id.group(1))


def articleDateTime(js):
    """Returns publication date and time (yyyy:mm:dd hh:mm) of news.
    """
    target = '"pubdate":"(.*)"'
    pubdate = re.search(target, js)
    if pubdate:
        return(pubdate.group(1).split(" "))


def articleDate(pub_datetime):
    """Returns article's published datetime.
    """
    pubdate = pub_datetime[0]
    date = pubdate.split("-")

    year, month, day = date[0], date[1], date[2]

    months = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
        "09": "Oct", "10": "Sep", "11": "Nov", "12": "Dec"}

    month_name = months.get(month)
    pub_date = "{} {} {}".format(day, month_name, year)
    return(pub_date)


def articleTime(pub_datetime):
    """Returns article's published time.
    """
    pubtime = pub_datetime[1]
    pub_time = pubtime + " Hours"
    return(pub_time)


def articleKeywords(js):
    """Returns a list of news topics/tags.
    """
    target = '"keyword".*"(.*)"'
    keyword = re.search(target, js)
    if keyword:
        keywords = keyword.group(1).split(",")
    return(keywords)


def write(text, file, linebreak=True):
    """Prints to file some text.
    """
    print(text, file=file)

    # print new, empty line
    if linebreak is True:
        print("", file=file)


def writeDivider(file):
    """Prints fancy divider.
    """
    write("***", file)


def wordCount(text):
    """Returns word count.
    """
    tokenizer = RegexpTokenizer(r"\w(?:[-\w]*\w)?")
    count = len(tokenizer.tokenize(text))
    return(count)


def sentCount(text):
    """Returns sentence count.
    """
    count = len(sent_tokenize(text))
    return(count)


def Main(percent_reduce, todays_news, email_news):

    date_today = time.strftime("%d %b %Y")  # dd mmm yyyy
    print(st_summarizer)
    print("  Collecting news for {}.\n".format(date_today))

    # statistics and counters
    reduction = []
    summarized = 0
    articles_fetched = 0

    # news categories
    print("  Categories fetched: {}".format(len(st_categories)))
    for (cat, cat_url, filename) in st_categories:
        print("\t[{}]".format(cat))

    # urls of articles for each category
    st_cats_urls = []
    for (cat, cat_url, filename) in st_categories:
        urls = articleURLs(articleHTML(cat_url), headline_count)
        st_cats_urls.append((urls, cat, filename))
        articles_fetched += len(urls)
    print("\n  Articles fetched: {}\n".format(articles_fetched))

    st_articles = [urls for urls in st_cats_urls]

    with open("ST_News-Headlines.txt", "w", encoding="utf8") as email_file:
        print("  Summarizing articles...\n")
        write(
            "News headlines on {}\n".format(date_today),
            email_file)

        # look at each news category
        for (urls, cat, filename) in st_articles:
            print("  "+cat.upper())
            cat_title = "\n{}\n{}".format(cat.upper(), "="*len(cat))

            summary_filename = "s_"+filename
            news_filename = "o_"+filename

            with open(summary_filename, "w", encoding="utf8") as summ_file:
                with open(news_filename, "w", encoding="utf8") as news_file:
                    write(cat_title, summ_file)
                    write(cat_title, news_file)
                    write(cat_title, email_file, linebreak=False)

                    article_count = 0

                    for url in urls:

                        # word count
                        wordcount_summ = 0
                        wordcount_news = 0

                        # article data
                        html = articleHTML(url)
                        js = articleJavaScript(html)
                        pub_datetime = articleDateTime(js)
                        pub_date = articleDate(pub_datetime)
                        pub_time = articleTime(pub_datetime)

                        if todays_news is True and pub_date != date_today:
                            # skip to next article if it's not published today
                            continue
                        else:
                            article_count += 1
                            cat_in_url = urlCategory(url)
                            subcat_in_url = urlSubCategory(url)

                            # get news subcategory;
                            # otherwise, get main category
                            if subcat_in_url is None:
                                subcat_in_url = cat_in_url

                        pub_id = "#{}".format(articleID(js))
                        title = pub_id+" "+articleTitle(html)
                        byline = articleByline(html)
                        keywords = articleKeywords(js)
                        text = articleText(url)
                        wordcount_news += wordCount(text)

                        print(
                            "\t{:02d}.".format(article_count),
                            "[{}]{}".format(pub_date, title[len(pub_id):])
                        )

                        # output, news headlines
                        write("[{}] {}\n{}".format(
                            pub_date, title, url),
                            email_file
                        )

                        # output, news summary
                        write(title, summ_file)
                        write(url, summ_file)
                        write("By: "+byline, summ_file)
                        write(pub_date+", "+pub_time, summ_file)

                        # length of summary
                        sents_in_summary = int(
                            percent_reduce*sentCount(text)
                            )

                        # summarized text
                        summary = summarize(url, sents_in_summary)
                        news_lead = sent_tokenize(text)[0]
                        if news_lead not in summary[0:1]:  # includes lead
                            write(news_lead, summ_file)
                            wordcount_summ += wordCount(news_lead)
                        for sent in summary:
                            write(sent, summ_file)
                            wordcount_summ += wordCount(sent)

                        write(keywords, summ_file)
                        writeDivider(summ_file)
                        summarized += 1

                        # output, original news arts
                        write(title+" [{}]".format(subcat_in_url), news_file)
                        write(url, news_file)
                        write("By: "+byline, news_file)
                        write(pub_date+", "+pub_time, news_file)
                        write(text, news_file)
                        write(keywords, news_file)
                        writeDivider(news_file)

                        # reduction in words
                        reduction.append(
                            (wordcount_news-wordcount_summ)/wordcount_news
                            )
                    writeDivider(email_file)

                    if article_count == 0:  # no news for today
                        print(
                            "\t{:02d}.".format(article_count),
                            "[{}] [No Updates]".format(date_today)
                        )
                    print("")

    mean_reduction = statistics.mean(reduction)
    stdev_reduction = statistics.stdev(reduction)
    print("  Articles summarized: {}".format(summarized))
    print("  Avg. word reduction: {:.1f}%, SD: {:.2f}\n".format(
        (mean_reduction*100), stdev_reduction))

    if email_news is True:
        sendEmail(gmail_user, gmail_pwd, send_to)


if __name__ == "__main__":
    Main(percent_reduce, todays_news, email_news)
    
