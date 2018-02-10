from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


def summarize(url, sent_count=10):
    """Automatic text summarizer
    https://pypi.python.org/pypi/sumy
    """
    lang = "english"
    parser = HtmlParser.from_url(url, Tokenizer(lang))
    stemmer = Stemmer(lang)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(lang)
    summary = [str(sent) for sent in summarizer(parser.document, sent_count)]
    return(summary)
