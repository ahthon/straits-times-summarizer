import smtplib

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os
import re
import time


def htmlfy_b(text):
    """Returns html bold text.
    """
    b = "<b>{}</b>".format(text)
    return(b)


def htmlfy_i(text):
    """Returns html italic text.
    """
    i = "<i>{}</i>".format(text)
    return(i)


def htmlfy_a(text, url):
    """Returns html hyperlink.
    """
    a = '<a href="{}">{}</a>'.format(url, text)
    return(a)


def htmlfy_p(text):
    """Returns html paragraph.
    """
    p = "<p>{}</p>".format(text)
    return(p)


def htmlfy_h3(text):
    """Returns html heading 3.
    """
    h3 = "<h3>{}</h3>".format(text)
    return(h3)


def htmlfy_h4(text):
    """Returns html heading 4.
    """
    h3 = "<h4>{}</h4>".format(text)
    return(h3)


def htmlfy_br(text):
    """Returns html breakline.
    """
    br = "<br>{}</br>".format(text)
    return(br)


def htmlfy_li(textlist):
    """Returns html unordered list.
    """
    u_list_items = ['<li style="margin-top: 0.5em">{}</li>'.format(item) for item in textlist]
    u_list = ['<ul style="list-style-type: square; margin-left: 1em">']
    for item in u_list_items:
        u_list.append(item)
    u_list.append("</ul>")
    list_html = ""
    for item in u_list:
        list_html += item
    return(list_html)


def htmlfy_table(rowslist):
    """Returns html table.
    """
    table = ['<table style="margin-left: 1em">']
    for rows in rowslist:
        table.append(rows)
    table.append('</table>')
    return(table)


def format_to_html():
    """Formats text files for html output.
    """

    hr_line = '<p>&nbsp;</p><hr width="5%"><p>&nbsp;</p>'

    # format summary files
    folder = os.listdir()
    summary_files = [f for f in folder if f.startswith("s_")]
    for f in summary_files:
        with open(f, mode="r", encoding="utf8") as text_f:
            with open("email_{}".format(f), mode="w", encoding="utf8") as email_f:
                lines = text_f.read().splitlines()
                lines = [line for line in lines if line != ""]
                category = lines.pop(0)
                headlines = [line[line.find(" ")+1:] for line in lines if line.startswith("#")]
                urls = [line for line in lines if line.startswith("http")]

                print(htmlfy_h3(category), file=email_f)
                print(htmlfy_li(headlines), file=email_f)
                print(htmlfy_br(""), file=email_f)

                for line in lines:
                    if line.startswith("#"):
                        line = line[line.find(" ")+1:]
                        line = htmlfy_h4(htmlfy_a(line.upper(), urls.pop(0)))
                        print(line, file=email_f)
                    elif line.startswith("http") or line.startswith("=="):
                        continue
                    elif line == "***":
                        print(hr_line, file=email_f)
                    else:
                        line = htmlfy_p(line)
                        print(line, file=email_f)

    # format report file
    f = "ST_News-Headlines.txt"
    with open(f, mode="r", encoding="utf8") as text_f:
        with open("email_{}".format(f), mode="w", encoding="utf8") as email_f:
            lines = text_f.read().splitlines()
            lines = [line for line in lines if line != ""]
            urls = [line for line in lines if line.startswith("http")]
            date = lines.pop(0)
            print(htmlfy_h3(date), file=email_f)

            table_data = []
            for line in lines:
                if line.isupper():
                    line = htmlfy_b(line)
                    line = '<th align="left">{}</th>'.format(line)
                    table_data.append(line)
                elif line.startswith("["):
                    line = re.search("\[(.*)\].[#]\d*.(.*)", line)
                    if line:
                        url = urls.pop(0)
                        date = line.group(1)
                        headline = htmlfy_a(htmlfy_i(line.group(2)), url)
                        line = '<td valign="top">{}</td><td  valign="top" style="margin-left: 3em">{}</td>'.format(date, headline)
                        table_data.append(line)
                elif line == "***":
                    table_data.append("<td>&nbsp;</td><td>&nbsp;</td>")

            table_rows = ["<tr>{}</tr>".format(td) for td in table_data]
            table = htmlfy_table(table_rows)
            for t in table:
                print(t, file=email_f)


def email(gmail_user, gmail_pwd, to, subject, text, attach):
    """Build email.
    """

    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = to
    msg["Subject"] = subject

    # email text
    textfile = open(text, mode="r", encoding="utf8")
    body = textfile.read()
    msg.attach(MIMEText(body, "html"))  # text is in html format

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


def send_email(gmail_user, gmail_pwd, send_to):
    """Sends email.
    """

    # format relevant file's content to html
    print("  Formatting e-mails...")
    format_to_html()
    print("  E-mails formatted.")

    # date today
    date = time.strftime("%d %b %Y")

    email_content = {
        "0_headlines": (
                    "The Straits Times, {}".format(date),
                    "email_ST_News-Headlines.txt",
                    "email_ST_News-Headlines.txt")
    }

    folder = os.listdir()
    email_count = 1
    for f in folder:
        if f.startswith("email_s"):
            summary_file = f
            original_file = summary_file.replace("email_s", "o")
            cat = summary_file[11:summary_file.find(".")].replace("-", " ")
            email_content.update({
                    "{}_{}".format(email_count, cat): (
                        "ST: {} Top Stories, {}".format(cat, date),
                        summary_file,
                        original_file)}
            )
            email_count += 1

    print("  Sending e-mails.\n")
    print("  E-mail recipients:")
    for to in send_to:
        print(f"\t{to}")
    print("")

    for to in send_to:
        print(f"  Sending e-mails to <{to}>...")
        for (cat, content) in sorted(email_content.items())[::-1]:
            (subject, text, attach) = content
            email(gmail_user, gmail_pwd, to, subject, text, attach)
            print(f"\t'{subject}' sent to <{to}>.")
    print("")

    print("  All e-mails sent.")
    del_email_files()
