# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 18:38:34 2023

@author: junob
"""

import sys

from Chatbot import chatbot


from PyQt5.QtCore import QAbstractListModel, QMargins, QPoint, QEvent, Qt, QRect
from PyQt5.QtGui import QColor, QTextDocument, QTextOption, QFontDatabase, QFont, QPixmap, QIcon

# from PyQt5.QtGui import
from PyQt5.QtWidgets import (
    QApplication,
    QTextEdit,
    QListView,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QStyledItemDelegate,
    #QLabel
)

USER_ME = 0
USER_THEM = 1

BUBBLE_COLORS = {USER_ME: "#90caf9", USER_THEM: "#FFCCFF"}

BUBBLE_PADDING = QMargins(15, 5, 55, 5)
TEXT_PADDING = QMargins(25, 15, 45, 15)

USER_TRANSLATE = {USER_ME: QPoint(35, 0), USER_THEM: QPoint(45, 0)}

class MessageDelegate(QStyledItemDelegate):

    def paint(self, painter, option, index):
        painter.save()
        # Retrieve the user,message uple from our model.data method.
        user, text = index.model().data(index, Qt.DisplayRole)

        trans = USER_TRANSLATE[user]
        painter.translate(trans)

        # option.rect contains our item dimensions. We need to pad it a bit
        # to give us space from the edge to draw our shape.
        bubblerect = option.rect.marginsRemoved(BUBBLE_PADDING)
        textrect = option.rect.marginsRemoved(TEXT_PADDING)

        # draw the bubble, changing color + arrow position depending on who
        # sent the message. the bubble is a rounded rect, with a triangle in
        # the edge.
        painter.setPen(Qt.NoPen)
        color = QColor(BUBBLE_COLORS[user])
        painter.setBrush(color)
        painter.drawRoundedRect(bubblerect, 9, 9)

        # draw the triangle bubble-pointer, starting from the top left/right.
        if user == USER_ME:
            p1 = bubblerect.topRight()
        else:
            p1 = bubblerect.topLeft()
            profile_rect = QRect(p1.x()-55, p1.y()-5, 37, 37)
            painter.drawRoundedRect(profile_rect, 11, 11)
            style = QApplication.style()
            # Ensure the cover is rendered over any selection rect
            profile = QPixmap('./profile.png')
            profile = profile.scaled(37, 37, Qt.KeepAspectRatio, Qt.SmoothTransformation)#, Qt.KeepAspectRatio, Qt.FastTransformation)
            style.drawItemPixmap(painter, profile_rect, Qt.AlignHCenter, profile)
            
        painter.drawPolygon(p1 + QPoint(-20, 0), p1 + QPoint(20, 0), p1 + QPoint(0, 15))

        toption = QTextOption()
        toption.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        # draw the text
        doc = QTextDocument(text)
        doc.setTextWidth(textrect.width())
        doc.setDefaultTextOption(toption)
        doc.setDocumentMargin(0)

        painter.translate(textrect.topLeft())
        doc.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        _, text = index.model().data(index, Qt.DisplayRole)
        textrect = option.rect.marginsRemoved(TEXT_PADDING)

        toption = QTextOption()
        toption.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)

        doc = QTextDocument(text)
        doc.setTextWidth(textrect.width())
        doc.setDefaultTextOption(toption)
        doc.setDocumentMargin(0)

        textrect.setHeight(doc.size().height())
        textrect = textrect.marginsAdded(TEXT_PADDING)
        return textrect.size()


class MessageModel(QAbstractListModel):
    def __init__(self, *args, **kwargs):
        super(MessageModel, self).__init__(*args, **kwargs)
        self.messages = []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # Here we pass the delegate the user, message tuple.
            return self.messages[index.row()]

    def setData(self, index, role, value):
        self._size[index.row()]

    def rowCount(self, index):
        return len(self.messages)

    def add_message(self, who, text):
        """
        Add an message to our message list, getting the text from the QLineEdit
        """
        if text:  # Don't add empty strings.
            # Access the list via the model.
            self.messages.append((who, text))
            # Trigger refresh.
            self.layoutChanged.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        with open('./brain.txt', 'rt', encoding='UTF8') as f:
            self.prompt = f.read()
        self.result = ''
        self.question = ''

        super(MainWindow, self).__init__()

        self.setWindowTitle('Chat_KoGPT')
        self.setWindowIcon(QIcon('./profile.png'))
        # Layout the UI
        l = QVBoxLayout()

        self.message_input = QTextEdit("")
        self.message_input.installEventFilter(self)
        #self.message_input.returnPressed.connect(self.message_to())
        
        # Buttons for from/to messages.
        self.btn1 = QPushButton("전송")
        #self.btn2 = QPushButton(">")

        self.messages = QListView()
        # Use our delegate to draw items in this view.
        self.messages.setItemDelegate(MessageDelegate())

        self.model = MessageModel()
        self.messages.setModel(self.model)
        #self.messages.setStyleSheet("Background: #CCCCCC;")

        self.btn1.pressed.connect(self.message_to)
        #self.btn2.pressed.connect(self.message_from)

        l.addWidget(self.messages)
        l.addWidget(self.message_input)
        l.addWidget(self.btn1)
        #l.addWidget(self.btn2)
        
        self.message_input.setFixedHeight(80)

        self.w = QWidget()
        self.w.setLayout(l)
        self.setCentralWidget(self.w)
        
    def resizeEvent(self, e):
        self.model.layoutChanged.emit()
        
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and obj is self.message_input:
            if event.key() == Qt.Key_Return and self.message_input.hasFocus():
                self.message_to()
                #print('Enter pressed')
                return True
        return False
        
    def message_to(self):
        self.model.add_message(USER_ME, self.message_input.toPlainText())
        self.question = self.message_input.toPlainText()
        self.message_input.clear()
        self.message_from()

    def message_from(self):
        self.prompt += self.result + '\nQ:' + self.question + '\nA:'
        #print(self.prompt)
        self.result = chatbot(self.prompt)
        self.model.add_message(USER_THEM, self.result)
        
        vbar = self.messages.verticalScrollBar()
        vbar.setValue(vbar.maximum())
        

app = QApplication(sys.argv)

fontDB = QFontDatabase()
fontDB.addApplicationFont('./font.ttf')
app.setFont(QFont('font.ttf', 9))
window = MainWindow()
window.show()
app.exec_()