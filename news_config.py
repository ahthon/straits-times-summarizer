"""
User settings for news.
"""
import os

# Toggle today's news. Set to True if you only want to pull today's news.
todays_news = False

# Number of news articles (top headlines) you want to pull per category.
headline_count = 5

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

# Delete any old text file
folder = os.listdir()
for f in folder:
    if f.endswith(".txt"):
        os.remove(f)
