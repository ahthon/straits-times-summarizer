# straits-times-summarizer

A set of scripts to scrape for news from The Straits Times and summarize the news articles. An added function is to e-mail the summaries and send the original articles as an e-mai attachment.

## Features

**st_news.py**
- Summaries of news articles (TexRank summarization).
- Article's tags, author, and the date/time it was published.
- Outputs summaries, original texts, and news headlines as .txt files.

**summarizer.py**
- Handles text summary.

**st_email.py**
- Option to e-mail articles through g-mail.

## Prerequisites

This project makes use of the following libraries:

- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [newspaper](https://github.com/codelucas/newspaper/)
- [nltk](http://www.nltk.org/)
- [sumy](https://github.com/miso-belica/sumy)

## Usage

After configuring your e-mail settings in st_email.py, simply run the main script, st_news.py.

E-mail function is optional. Comment out sent_email() in the main script to disable it.

```
if __name__ == "__main__":
    print(st_summarizer)
    main()
    send_email()  # e-mail headlines and summaries
```


## Configuring gmail

Gmail is used in st_email.py. Ensure that ["Allow less secure apps" is turned on](https://support.google.com/accounts/answer/6010255?hl=en) for the gmail account.

Edit gmail address and password.

```
gmail_user = "mygmail@gmail.com"    # user gmail address
gmail_pwd = "mygmailpassword"       # user gmail password
```

Edit recipient e-mail address.

```
(...)
    # recipient e-mails
    send_to = ["recipient1@gmail.com", "recipient2@gmail.com"]
(...)
```

## Author

[**ahthon**](https://github.com/ahthon)

Feel free to contact me if you run into issues or have suggests for improvement.
