import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
import time

gmail_user = "user@gmail.com"  # user gmail address
gmail_pwd = "userpassword"  # user gmail password


def email(to, subject, text, attach):

    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = to
    msg["Subject"] = subject

    # email text
    textfile = open(text, mode="r", encoding="utf8")
    body = textfile.read()
    msg.attach(MIMEText(body, "plain"))

    # email attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(open(attach, mode="rb").read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        "attachment; filename='%s'" % os.path.basename(attach))
    msg.attach(part)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(gmail_user, gmail_pwd)
    server.sendmail(gmail_user, to, msg.as_string())
    server.quit()


def send_email():
    date = time.strftime("%d %b %Y")

    email_content = {
        "0_headlines": (
            "The Straits Times, {}".format(date),
            "ST_headlines.txt",
            "ST_headlines.txt"),

        "1_sg": (
            "ST: Singapore News, {}".format(date),
            "s_Singapore_News.txt",
            "o_Singapore_News.txt"),

        "2_asia": (
            "ST: Asia News, {}".format(date),
            "s_Asia_News.txt",
            "o_Asia_News.txt"),

        "3_world": (
            "ST: World News, {}".format(date),
            "s_World_News.txt",
            "o_World_News.txt"),

        "4_pol": (
            "ST: Political News, {}".format(date),
            "s_Politics_News.txt",
            "o_Politics_News.txt"),

        "5_biz": (
            "ST: Business News, {}".format(date),
            "s_Business_News.txt",
            "o_Business_News.txt"),

        "6_sci": (
            "ST: Science News, {}".format(date),
            "s_Science_News.txt",
            "o_Science_News.txt")
    }

    # recipient e-mails
    send_to = ["recipient1@gmail.com", "recipient2@gmail.com"]

    print("Sending news summaries via e-mail.\n")
    print("E-mail recipients:")
    for to in send_to:
        print("\t{}".format(to))
    print("")

    for to in send_to:
        print("Sending e-mails to <{}>...".format(to))
        for (cat, content) in sorted(email_content.items())[::-1]:
            (subject, text, attach) = content
            email(to, subject, text, attach)
            print("\t'{}' sent to <{}>.".format(subject, to))
    print("")

    print("All e-mails sent.")
