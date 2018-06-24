import feedparser
import requests
import unidecode
import operator
import pytz

from bs4 import BeautifulSoup
from datetime import datetime

class Article():
    
    def __init__(self, title, url, published):
        self.title = title
        self.url = url
        self.published = published

    def fetch(self, text_match):
        session = requests.Session()
        req = session.get(self.url)
        soup = BeautifulSoup(req.text, 'lxml')

        paragraphs = soup.find_all(text_match['element'], {'class': text_match['class']})
        if len(paragraphs) == 0:
            paragraphs = soup.find_all(text_match['element'], {'class': text_match['class_fallback']})
        self.text = '\n'.join([unidecode.unidecode(p.get_text()) for p in paragraphs])
        return self.text

class ContentSource():
    
    def __init__(self, config):
        self.config = config
        self.name = config['name']
        self.link = config['link']

    def fetch_articles(self, db, max_articles = None):
        posts = feedparser.parse(self.config['rss'])

        articles = []
        for post in posts.entries[:max_articles]:
            published = datetime.strptime(post.published, self.config['date_format'])
            published = published.replace(tzinfo=pytz.UTC)

            article = Article(post.title, post.link, published)
            article.source_id = self.config['id']

            # don't fetch articles already in db
            if not db.article_exists(article.title, article.url):
                article.fetch(self.config['text'])
                articles.append(article)

        return articles

    def __str__(self):
        return str(self.paper)
            

class Reader():

    def __init__(self):
        self.sources = []

    def add_source(self, source_config):
        source = ContentSource(source_config)
        self.sources.append(source)
    
    def fetch_articles(self, db, max_articles = None):
        articles = []
        for source in self.sources:
            articles.extend(source.fetch_articles(db, max_articles))

        articles = sorted(articles, key=operator.attrgetter('published'), reverse=True)

        return articles[:max_articles]