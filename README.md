# straits-times-summarizer

![PyPI](https://img.shields.io/pypi/pyversions/Django.svg)

       ______           _ __        _______
      / __/ /________ _(_) /____   /_  __(_)_ _  ___ ___
     _\ \/ __/ __/ _ `/ / __(_-<    / / / /  ' \/ -_|_-<
    /___/\__/_/  \_,_/_/\__/___/   /_/ /_/_/_/_/\__/___/
       _  __                 ____                          _
      / |/ /__ _    _____   / __/_ ____ _  __ _  ___ _____(_)__ ___ ____
     /    / -_) |/|/ (_-<  _\ \/ // /  ' \/  ' \/ _ `/ __/ /_ // -_) __/
    /_/|_/\__/|__,__/___/ /___/\_,_/_/_/_/_/_/_/\_,_/_/ /_//__/\__/_/

A set of scripts to scrape for news from The Straits Times and summarize the news articles. An added function is to e-mail the summaries and send the original articles as an e-mail attachment.

## Features

Main script: `st_news.py`
- Summaries of news articles (TexRank summarization).
- Includes article's tags, author, and the date/time it was published.
- Outputs summaries, original texts, and news headlines as .txt files.

![st_news](https://user-images.githubusercontent.com/32814703/34471824-89a95b10-ef8d-11e7-8b11-8c55aaf1276c.gif)


`summarizer.py`
- Handles text summary.

`st_email.py`
- Option to e-mail articles through Gmail.
- Summarized text is in html format.
- Original news text is sent as an attachment.

![st1](https://user-images.githubusercontent.com/32814703/34471794-73e9bd16-ef8c-11e7-930e-292b96ffa6f7.png)

![st2](https://user-images.githubusercontent.com/32814703/34471793-73646396-ef8c-11e7-89fc-7f61ae9f25ca.png)

## Configuration

Configure your settings in news_config.py and email_config.py.

#### News settings `news_config.py`

1. Toggle to search for only today's news. Set to True if you only want to pull news articles that were published today. 
```
todays_news = False
```

2. Set the number of news articles (top headlines) you want to pull per category.
```
headline_count = 5
```

3. Set categories. Comment to exclude category; decomment to include it.
```
st_categories = [
    ("Singapore", "http://www.straitstimes.com/singapore", "ST_Singapore.txt"),
    ("Politics", "http://www.straitstimes.com/politics", "ST_Politics.txt"),
    ("Asia", "http://www.straitstimes.com/asia", "ST_Asia.txt"),
    ("World", "http://www.straitstimes.com/world", "ST_World.txt"),
    # ("Lifestyle", "http://www.straitstimes.com/lifestyle", "ST_Lifestyle.txt"),
    # ("Food", "http://www.straitstimes.com/lifestyle/food", "ST_Food.txt"),
    # ("Sport", "http://www.straitstimes.com/sport", "ST_Sport.txt"),
    # ("Tech", "http://www.straitstimes.com/tech", "ST_Tech.txt")
]
```

Set any other specific 'Tags' to pull news from. These tags would be appended to the main categories. Again, comment to exclude category; decomment to include it.
```
st_tags = [
    ("Scientific Research", "http://www.straitstimes.com/tags/scientific-research", "ST_Scientific-Research.txt")
    # ("Science", "http://www.straitstimes.com/tags/science", "ST_Science.txt"),
    # ("US Politics", "http://www.straitstimes.com/tags/us-politics", "ST_US-Politics.txt")
]
```

#### E-mail/Gmail settings `email_config.py`

Gmail is used in st_email.py. Ensure that ["Allow less secure apps" is turned on](https://support.google.com/accounts/answer/6010255?hl=en) for the gmail account.

1. Toggle send e-mail function. Set to True to enable; False to disable.
```
email_news = False
```

2. User's gmail details.
```
gmail_user = "user@gmail.com"       # user gmail address
gmail_pwd = "userpwd"               # user gmail password
```

3. E-mail addresses of reciepients.
```
send_to = [
    "recipient1@gmail.com",
    "recipient2@gmail.com"
]
```

## Author

* [**ahthon**](https://github.com/ahthon)

Feel free to contact me if you run into issues or have suggests for improvement.
