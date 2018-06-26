import argparse
import unidecode

from database import ArticleDB
from reader import Reader
from summarize import TextSummarizer

DATABASE_PATH = './article_db.sqlite'

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
    print('Added {} articles.'.format(articles_added))

def display_articles(db, limit):
    articles = db.fetch_articles(limit)
    for a in articles:
        string = '''
================================================================================
{title}
{published} - [{link}]
--------------------------------------------------------------------------------
{summary}
--------------------------------------------------------------------------------
{source} - {score}
================================================================================
        '''.format(
            title=a['title'],
            published=a['published'],
            link=a['link'],
            summary=a['summary'],
            source=a['source']['name'],
            score=a['summary_score'])

        string = unidecode.unidecode(string)
        print(string)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-d', '--display', type=int, default=0, help='Display most recently published articles')
    argparser.add_argument('-r', '--remove', type=int, default=7, help='Remove articles after this many days')
    argparser.add_argument('-nf', '--nofetch', default=False, action='store_true', help="Don't fetch new articles")
    args = argparser.parse_args()

    db = ArticleDB(DATABASE_PATH)
    # remove old articles
    old_articles_removed = remove_old_articles(db, days_old=args.remove)
    print('Removed {} old articles.'.format(old_articles_removed))
    # fetch new articles
    if not args.nofetch:
        fetch_new_articles(db)
    
    if args.display > 0:
        display_articles(db, args.display)

    db.close()