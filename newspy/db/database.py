import sqlite3

from datetime import datetime, timedelta

class ArticleDB():
    
    def __init__(self, path='./article_db.sqlite'):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def _source_to_json(self, row):
        # ID, Name, Link, RSS, Text_Element, Text_Class, Text_Class_Fallback, Date_Format
        source = {
            "id": row[0],
            "name": row[1],
            "link": row[2],
            "rss": row[3],
            "text": { "element": row[4], "class": row[5], "class_fallback": row[6] },
            "date_format": row[7]
        }
        return source

    def _article_to_json(self, row):
        # Article.Source, Title, Published, Article.Link, Summary, Summary_Score, Name, Source.Link
        article = {
            "title": row[1],
            "published": row[2],
            "link": row[3],
            "summary": row[4],
            "summary_score": row[5],
            "source": {
                "id": row[0],
                "name": row[6],
                "link": row[7]
            }
        }
        return article

    def get_sources(self):
        query = '''
        SELECT * FROM Sources
        '''

        self.cursor.execute(query)
        source_rows = self.cursor.fetchall()
        sources = [self._source_to_json(row) for row in source_rows]

        return sources

    def article_exists(self, title, link):
        query = '''
        SELECT * FROM Articles
        WHERE Title = ?
        AND Link = ?
        '''
        binding = (title, link)

        self.cursor.execute(query, binding)
        title = self.cursor.fetchone()
        if title:
            return True
        else:
            return False


    def add_article(self, source_id, title, published, link, summary, summary_score):
        query = '''
        INSERT INTO Articles (Source, Title, Published, Link, Summary, Summary_Score)
        VALUES (?, ?, ?, ?, ?, ?)
        '''
        binding = (source_id, title, published, link, summary, summary_score)

        self.cursor.execute(query, binding)
        self.conn.commit()

    def fetch_articles(self, limit=None):
        query = '''
        SELECT A.*, S.Name, S.Link FROM Articles A
        JOIN Sources S ON S.ID = A.Source
        ORDER BY A.Published DESC
        {lim}
        '''.format(lim='' if limit is None else 'LIMIT ' + limit)

        self.cursor.execute(query)
        article_rows = self.cursor.fetchall()
        articles = [self._article_to_json(row) for row in article_rows]

        return articles

    def remove_old_articles(self, days_old):
        date = datetime.today() - timedelta(days=days_old)
        query = '''
        DELETE FROM Articles
        WHERE Published < "{pub}"
        '''.format(pub=date)
        
        self.cursor.execute(query)
        self.conn.commit()

        return self.cursor.rowcount