"""
STRAITS TIMES SUMMARIZER
Author: ahthon
Date created: 14 Oct 2017
Date last modified: 7 Jan 2018
"""

import re
import requests
import statistics
import sys
import time

from email_config import *
from news_config import *
from st_email import send_email
from st_summarizer import get_summary

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


def html_soup(url):
    """Returns html soup.
    """
    html = request.urlopen(url).read().decode("utf8")
    html_soup = BeautifulSoup(html, "html.parser")
    return(html_soup)


def get_urls_of_cat(cat_soup, url_count):
    """Returns article urls of a certain news category.
    """
    st_url = "http://www.straitstimes.com"
    art_urls = str(cat_soup.find_all(
        "span", class_="story-headline", limit=url_count))
    hrefs = re.findall('href=\"(.*?)\"', art_urls)
    urls = [st_url+url for url in hrefs if hrefs and "javascript" not in url]
    return(urls)


def get_cat_in_url(url):
    """Returns an art's category from its url.
    """
    pattern = "straitstimes.com/(\w*)/"
    cat = re.search(pattern, url)
    if cat:
        cat = cat.group(1).title()
        return(cat)
    else:
        return(None)


def get_subcat_in_url(url):
    """Returns an art's subcategory from its url.
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


def get_art_title(art_soup):
    """Returns news title.
    """
    title = art_soup.find("h1", class_="headline node-title")
    title = title.string
    return(title)


def get_art_byline(art_soup):
    """Returns news byline/author. Returns '--' if none is found.
    """
    author = art_soup.find(
        "div", class_="author-field author-name")
    designation = art_soup.find(
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


def get_art_text(art_url):
    """Returns news text
    """
    html = requests.get(art_url).text
    text = fulltext(html)
    return(text)


def get_art_js(art_soup):
    """Returns art's html (script tag)
    """
    script = str(art_soup.find_all("script", limit=3)[-1])
    return(script)


def get_art_id(art_js):
    """ Returns art ID.
    """
    target = '"articleid".*"(\d*)"'
    art_id = re.search(target, art_js)
    if art_id:
        return(art_id.group(1))


def get_art_datetime(art_js):
    """Returns publication date and time (yyyy:mm:dd hh:mm) of news.
    """
    target = "(\d{4}:\d{2}:\d{2}\s\d{2}:\d{2})"
    pubdate = re.search(target, art_js)
    if pubdate:
        return(pubdate.group(1).split(" "))


def get_art_date(art_datetime):
    """Returns art's published datetime.
    """
    pubdate = art_datetime[0]
    date = pubdate.split(":")

    year = date[0]
    month = date[1]
    day = date[2]

    months = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
        "09": "Oct", "10": "Sep", "11": "Nov", "12": "Dec"}

    month_name = months.get(month)
    art_date = "{} {} {}".format(day, month_name, year)
    return(art_date)


def get_art_time(art_datetime):
    """Returns art's published time.
    """
    pubtime = art_datetime[1]
    art_time = pubtime + " Hours"
    return(art_time)


def get_art_keywords(art_js):
    """Returns a list of news topics/tags.
    """
    target = '"keyword".*"(.*)"'
    keyword = re.search(target, art_js)
    if keyword:
        keywords = keyword.group(1).split(",")
    return(keywords)


def print_to_file(text, file, lbreak=True):
    """Prints to file some text.
    """
    print(text, file=file)

    # print new, empty line
    if lbreak is True:
        print("", file=file)


def print_divider(file):
    """Prints fancy divider.
    """
    print_to_file("***", file)


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


def main(percent_reduce, todays_news, email_news):

    # today's date
    date_today = time.strftime("%d %b %Y")
    print(st_summarizer)
    print("  Collecting news for {}.\n".format(date_today))

    # statistics and counters
    reduction = []
    summarized = 0
    arts_fetched = 0

    # news categories
    print("  Categories fetched: {}".format(len(st_categories)))
    for (cat, cat_url, filename) in st_categories:
        print("\t[{}]".format(cat))

    # urls of articles for each category
    st_cats_urls = []
    for (cat, cat_url, filename) in st_categories:
        art_urls = get_urls_of_cat(html_soup(cat_url), headline_count)
        st_cats_urls.append((art_urls, cat, filename))
        arts_fetched += len(art_urls)
    print("\n  Articles fetched: {}\n".format(arts_fetched))

    st_arts = [cat for cat in st_cats_urls]
    with open("ST_News-Headlines.txt", "w", encoding="utf8") as email_file:
        print("  Summarizing articles...\n")
        print_to_file(
            "News headlines on {}\n".format(date_today),
            email_file)

        # look at each news category
        for (art_urls, cat, filename) in st_arts:
            print("  "+cat.upper())
            cat_title = "\n{}\n{}".format(cat.upper(), "="*len(cat))

            summary_filename = "s_"+filename
            news_filename = "o_"+filename

            with open(summary_filename, "w", encoding="utf8") as summ_file:
                with open(news_filename, "w", encoding="utf8") as news_file:
                    print_to_file(cat_title, summ_file)
                    print_to_file(cat_title, news_file)
                    print_to_file(cat_title, email_file, lbreak=False)

                    art_count = 0  # number of arts fetched

                    for art_url in art_urls:

                        # word count
                        word_count_summ = 0
                        word_count_news = 0

                        # article data
                        art_html = html_soup(art_url)
                        art_js = get_art_js(art_html)
                        art_datetime = get_art_datetime(art_js)
                        art_date = get_art_date(art_datetime)
                        art_time = get_art_time(art_datetime)

                        if todays_news is True and art_date != date_today:
                            # skip to next article if it's not published today
                            continue
                        else:
                            art_count += 1
                            cat_in_url = get_cat_in_url(art_url)
                            subcat_in_url = get_subcat_in_url(art_url)

                            # get news subcategory;
                            # otherwise, get main category
                            if subcat_in_url is None:
                                subcat_in_url = cat_in_url

                        art_id = "#{}".format(get_art_id(art_js))
                        art_title = art_id+" "+get_art_title(art_html)
                        art_byline = get_art_byline(art_html)
                        art_keywords = get_art_keywords(art_js)
                        art_text = get_art_text(art_url)
                        word_count_news += word_count(art_text)

                        print(
                            "\t{0:02d}.".format(art_count),
                            "[{}]{}".format(art_date, art_title[len(art_id):])
                        )

                        # output, news headlines
                        print_to_file("[{}] {}\n{}".format(
                            art_date, art_title, art_url),
                            email_file
                        )

                        # output, news summary
                        print_to_file(art_title, summ_file)
                        print_to_file(art_url, summ_file)
                        print_to_file("By: "+art_byline, summ_file)
                        print_to_file(art_date+", "+art_time, summ_file)

                        # length of summary
                        sents_in_summary = int(
                            percent_reduce*sent_count(art_text)
                            )

                        # summarized text
                        art_summary = get_summary(art_url, sents_in_summary)
                        art_lead = sent_tokenize(art_text)[0]
                        if art_lead not in art_summary[0:1]:  # includes lead
                            print_to_file(art_lead, summ_file)
                            word_count_summ += word_count(art_lead)
                        for sent in art_summary:
                            print_to_file(sent, summ_file)
                            word_count_summ += word_count(sent)

                        print_to_file(art_keywords, summ_file)
                        print_divider(summ_file)
                        summarized += 1

                        # output, original news arts
                        print_to_file(art_title+" [{}]".format(
                            subcat_in_url), news_file)
                        print_to_file(art_url, news_file)
                        print_to_file("By: "+art_byline, news_file)
                        print_to_file(art_date+", "+art_time, news_file)
                        print_to_file(art_text, news_file)
                        print_to_file(art_keywords, news_file)
                        print_divider(news_file)

                        # reduction in words
                        reduction.append(
                            (word_count_news-word_count_summ)/word_count_news
                            )
                    print_divider(email_file)

                    if art_count == 0:  # no news for today
                        print(
                            "\t{0:02d}.".format(art_count),
                            "[{}] [No Updates]".format(date_today)
                        )
                    print("")

    mean_reduction = statistics.mean(reduction)
    stdev_reduction = statistics.stdev(reduction)
    print("  Articles summarized: {}".format(summarized))
    print("  Avg. word reduction: {:.1f}%, SD: {:.2f}\n".format(
        (mean_reduction*100), stdev_reduction))

    if email_news is True:
        send_email(gmail_user, gmail_pwd, send_to)


if __name__ == "__main__":
    main(percent_reduce, todays_news, email_news)
