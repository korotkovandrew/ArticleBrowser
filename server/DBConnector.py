import sqlite3
from sqlite3 import Error        

LIKE_SPLITTER = ';'

import DSS

DB_PATH = 'database/db.sqlite3'

class SQLiteConnector:
    def __createConnection(self):
        try:
            return sqlite3.connect(DB_PATH)
        except sqlite3.Error as e:
            # print(e)
            print('Failed to connect to database')
            exit(1)

    def getUserID(self, username: str) -> int:
        conn = self.__createConnection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        
        conn.close()
        return None if row is None else row[0]

    def getUser(self, userID: int) -> dict:
        conn = self.__createConnection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (userID,))
        row = cursor.fetchone()
        
        if row is not None and row[3] != '':
            print(row[3])
            likes = list(map(int, row[3].split(LIKE_SPLITTER)))
        else:
            likes = []
            
        conn.close()
        return None if row is None else {'id':       row[0], 
                                         'username': row[1], 
                                         'password': row[2], 
                                         'likes':    likes}

        
    def removeUser(self, userID: int) -> None:
        conn = self.__createConnection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE id = ?', (userID,))
        conn.commit()
        
        conn.close()


    def getUserLikes(self, username: str) -> list:
        conn = self.__createConnection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id_likes FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        
        likes = list(map(int , row[0].split(LIKE_SPLITTER))) if row and row[0] else []
        
        conn.close()
        return likes


    def isLiked(self, userID: int, articleID: int) -> bool:
        conn = self.__createConnection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id_likes FROM users WHERE id = ?', (userID,))
        row = cursor.fetchone()
        
        isLiked = str(articleID) in row[0].split(LIKE_SPLITTER) if row else False
        
        conn.close()
        return isLiked


    def setLiked(self, userID: int, articleID: int) -> None:
        conn = self.__createConnection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id_likes FROM users WHERE id = ?', (userID,))
        likes = cursor.fetchone()[0]
        if likes == '':
            likes = str(articleID)
        else:
            likes = likes.split(LIKE_SPLITTER)
            likes.append(str(articleID))
            likes = LIKE_SPLITTER.join(likes)
        cursor.execute('UPDATE users SET id_likes = ? WHERE id = ?', (likes, userID))
        cursor.execute('UPDATE articles SET likes = likes + 1 WHERE id = ?', (articleID,))
        conn.commit()
        
        conn.close()


    def addUser(self, username: str, password: str) -> int:
        conn = self.__createConnection()
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO users (username, password, id_likes) VALUES (?, ?, ?)', (username, password, ''))
        conn.commit()
        userID = cursor.lastrowid
        
        conn.close()
        return userID
        
        
    def getArticle(self, articleID: int) -> dict:
        conn = self.__createConnection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM articles WHERE id = ?', (articleID,))
        row = cursor.fetchone()
        
        conn.close()
        return None if row is None else {'id':      row[0], 
                                         'title':   row[2], 
                                         'author':  row[3], 
                                         'likes':   row[4], 
                                         'content': row[5]}

    def getRandomArticle(self) -> dict:
        conn = self.__createConnection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM articles ORDER BY RANDOM() LIMIT 1')
        row = cursor.fetchone()
        
        conn.close()
        return None if row is None else {'id':      row[0], 
                                         'title':   row[2], 
                                         'author':  row[3], 
                                         'likes':   row[4], 
                                         'content': row[5]}

    def getRecommendedArticles(self, userID: int, numberOfArticles: int) -> list:
        #! now it just returns random articles
        # TODO СППР
        articles = []
        for _ in range(numberOfArticles):
            article = self.getRandomArticle()
            if article:
                articles.append({'id':article['id'], 'title':article['title']})

        return articles
