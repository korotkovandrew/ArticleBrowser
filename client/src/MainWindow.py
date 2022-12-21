from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QScrollArea, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

from functools import partial

from src.ClientSocket.Sender import Sender
from src.Requests import *
from src.RecommendationArea import RecommendationArea

class MainWindow(Sender, QMainWindow):
    def __init__(self, 
                 serverIP: str, 
                 serverPort: int, 
                 currentUser: str):
        
        Sender.__init__(self, serverIP, serverPort)
        QMainWindow.__init__(self)
        
        self.initUI(currentUser)
        self.initSignals()
        self.loadArticle()
        

    def initAlertWindow(self):
        self.alertWindow = QDialog()
        uic.loadUi('src/ui/Alert.ui', self.alertWindow)
        self.alertWindow.message.setText('...')


    def initUI(self, username: str):
        self.initAlertWindow()
        
        uic.loadUi('src/ui/MainWindow.ui', self)
        self.setWindowTitle('Article Browser')
        self.setWindowIcon(QIcon('./src/ui/ico/Ab_icon.ico'))
        
        self.articleTitleLabel.setWordWrap(True)
        self.articleTitleLabel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        
        self.nicknameLabel.setText(username)
        
            
    def initSignals(self):
        self.randomArticleButton.clicked.connect(self.loadArticle)
        self.likeButton.clicked.connect(self.likeSignal)
    
    
    def showLiked(self, liked: bool = True):
        self.likeButton.setEnabled(not liked)
        if liked:
            self.likeButton.setStyleSheet("background-color: #E74C3C;")
        else:
            self.likeButton.setStyleSheet('QPushButton { background-color: #303134; border-radius: 10px; min-height: 34px; } QPushButton:hover { background-color: #1E1F20; } QPushButton:onclick { background-color: #1A1B1C;}')

    def loadArticle(self, articleID: int = 0):
        if self.nicknameLabel.text() == '':
            self.alert(True, 'You are not logged in')
            return
        response = self.send(GET(self.nicknameLabel.text(), articleID))
        if response['code']:
            self.alert(True, response['code'])
            return
        
        self.currentArticleID = response['articleID']
        self.articleTitleLabel.setText(response['articleData']['title'])
        self.articleText.setText(response['articleData']['content'])
        self.showLiked(response['liked'])
     
        
    def likeSignal(self):
        if self.nicknameLabel.text() == '':
            self.alert(True, 'You are not logged in')
            return
        if self.currentArticleID == 0:
            self.alert(True, 'You have not opened any article')
            return
        
        response = self.send(LIKE(self.nicknameLabel.text(), 
                                  self.currentArticleID))
        if response['code'] == '':
            self.showLiked(True)
    
        articles = []
        for articleID in response['data']:
            articles.append((articleID, response['data'][articleID]['title']))
        
        self.updateRecomendations(articles)

    def updateRecomendations(self, recomendations: list):
        self.recommendationsLabel.setText('For you')
        self.recommendationsWidgets = RecommendationArea(recomendations)
        
        self.userLayout.addWidget(self.recommendationsWidgets, 4, 0, 1, 2)
        for widget in self.recommendationsWidgets.widgets:
            widget.button.clicked.connect(partial(self.loadArticle, widget.articleID))
            widget.button.clicked.connect(partial(self.recommendationsWidgets.removeWidget, widget.articleID))
            
            
    def alert(self, critical: bool, message: str):
        self.setEnabled(False)
        self.alertWindow.message.setText(message)
        if critical:
            self.alertWindow.setWindowIcon(QIcon('src/ui/ico/critical.ico'))
        else:
            self.alertWindow.setWindowIcon(QIcon('src/ui/ico/info.ico'))
        self.alertWindow.exec_()
        self.setEnabled(True)
            