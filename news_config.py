"""
User settings for news.
"""
import os

# Toggle today's news. Set to True if you only want to pull today's news.
# Default: False
todays_news = False


# Number of news articles (top headlines) you want to pull per category.
# Default: 5
headline_count = 5


# Set the length of summary text.
# Summary length is relative to original text.
# Default: 0.3 (number of sentences is reduced by 70%)
percent_reduce = 0.3


# Categories to pull top headlines from.
# Comment to exclude category; decomment to include it.
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

# Specific tags to pull latest news from.
# Comment to exclude category; decomment to include it.
# Included tags will be added to main categories.
st_tags = [
    ("Scientific Research", "http://www.straitstimes.com/tags/scientific-research", "ST_Scientific-Research.txt")
    # ("Science", "http://www.straitstimes.com/tags/science", "ST_Science.txt"),
    # ("US Politics", "http://www.straitstimes.com/tags/us-politics", "ST_US-Politics.txt")
]

for tag in st_tags:
    st_categories.append(tag)


# Deletes any old text file.
# Comment to disable.
folder = os.listdir()
for f in folder:
    if f.endswith(".txt"):
        os.remove(f)
