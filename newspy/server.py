from flask import Flask, render_template, redirect
from db.database import ArticleDB
from db.reader import Reader
from db.summarize import TextSummarizer

from datetime import datetime, timedelta

app = Flask(__name__)

DATABASE_PATH = './newspy/db/article_db.sqlite'

@app.route('/')
def index():
    db = ArticleDB(DATABASE_PATH)
    articles = db.fetch_articles()
    yesterday = datetime.today() - timedelta(days=1)
    for article in articles:
        published = datetime.strptime(article['published'], '%Y-%m-%d %H:%M:%S+00:00')
        if published <= yesterday:
            article['old'] = True
    db.close()

    return render_template('index.html', articles=articles)

@app.route('/clear')
def clear():
    db = ArticleDB(DATABASE_PATH)
    remove_old_articles(db, days_old=0)
    db.close()

    return redirect('/refresh')

@app.route('/refresh')
def refresh():
    db = ArticleDB(DATABASE_PATH)
    old_articles_removed = remove_old_articles(db, days_old=7)
    articles_added = fetch_new_articles(db)
    db.close()

    return render_template('refresh.html', added=articles_added, removed=old_articles_removed)

def remove_old_articles(db, days_old=7):
    removed = db.remove_old_articles(days_old)
    return removed

def fetch_new_articles(db):
    sources = db.get_sources()
    reader = Reader()
    for source in sources:
        reader.add_source(source)

    articles = reader.fetch_articles(db)
    summarizer = TextSummarizer()

    articles_added = 0
    for a in articles:
        if not db.article_exists(a.title, a.url):
            summary = summarizer.summarize(a.text)
            db.add_article(a.source_id, a.title, a.published, a.url, summary.summary, summary.score)
            articles_added += 1
    return articles_added

if __name__ == '__main__':
    app.run(debug=True)