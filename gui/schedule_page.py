from datetime import datetime
from functools import partial
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from kudong import *
from modules.font_config import fs, pt

animeWeeklist = []
animeWeekIdx = 0

# 1. Schedule Page
# //////////////////////////////////////////////////////////////////
class SchedulePage:

    def __init__(self, MainWindow, widgets):

        self.MainWindow = MainWindow
        self.widgets = widgets  

        self.widgets.pushButton_sun.clicked.connect(partial(self.clickWeekendButton,0))
        self.widgets.pushButton_mon.clicked.connect(partial(self.clickWeekendButton,1))
        self.widgets.pushButton_tue.clicked.connect(partial(self.clickWeekendButton,2))
        self.widgets.pushButton_wed.clicked.connect(partial(self.clickWeekendButton,3))
        self.widgets.pushButton_thu.clicked.connect(partial(self.clickWeekendButton,4))
        self.widgets.pushButton_fri.clicked.connect(partial(self.clickWeekendButton,5))
        self.widgets.pushButton_sat.clicked.connect(partial(self.clickWeekendButton,6))
        self.widgets.pushButton_extra.clicked.connect(partial(self.clickWeekendButton,7))
        self.widgets.pushButton_new.clicked.connect(partial(self.clickWeekendButton,8))

        # QTableWidget 편성표 테이블 설정
        widgets.anime_time_table.setSelectionBehavior(QTableWidget.SelectRows)
        widgets.anime_time_table.verticalHeader().setDefaultSectionSize(60)
        widgets.anime_time_table.verticalHeader().setVisible(False)
        widgets.anime_time_table.verticalHeader().setSectionsMovable(False)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        # widgets.anime_time_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Fixed)
        widgets.anime_time_table.horizontalHeader().resizeSection(1, 500)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(5,QHeaderView.ResizeToContents)
        widgets.anime_time_table.cellClicked.connect(self.on_cell_clicked)

        now = datetime.now()
        weekday_index = now.weekday()

        if weekday_index == 6:
            weekday_index = 0
        else:
            weekday_index += 1

        self.clickWeekendButton(weekday_index);

    # 해당 요일 클릭시 버튼 스타일을 적용합니다.
    def setWeekendButtonStyle(self, idx,sheet):
        if idx == 0:
            self.widgets.pushButton_sun.setStyleSheet(sheet);
        elif idx == 1:
            self.widgets.pushButton_mon.setStyleSheet(sheet);
        elif idx == 2:
            self.widgets.pushButton_tue.setStyleSheet(sheet);
        elif idx == 3:
            self.widgets.pushButton_wed.setStyleSheet(sheet);
        elif idx == 4:
            self.widgets.pushButton_thu.setStyleSheet(sheet);
        elif idx == 5:
            self.widgets.pushButton_fri.setStyleSheet(sheet);
        elif idx == 6:
            self.widgets.pushButton_sat.setStyleSheet(sheet);
        elif idx == 7:
            self.widgets.pushButton_extra.setStyleSheet(sheet);
        elif idx == 8:
            self.widgets.pushButton_new.setStyleSheet(sheet);

    # 특정 요일을 클릭했을 때 함수
    def clickWeekendButton(self, idx):
        global animeWeeklist,animeWeekIdx
        #print("idx 클릭 "+ str(idx))
        count = 0
        beforeSheet = "background-color: rgb(52, 59, 72); font-size: " + str(fs(32, 38)) + "px; font-weight: bold;"
        self.setWeekendButtonStyle(animeWeekIdx, beforeSheet)
        afterSheet = "background-color: rgb(156, 179, 199); font-size: " + str(fs(32, 38)) + "px; font-weight: bold; color: rgb(255, 255, 255);"
        self.setWeekendButtonStyle(idx, afterSheet)
        animeWeekIdx = idx

        self.widgets.anime_time_table.clearContents()
        animeWeeklist = requestAnimeWeekInfo(idx)

        if animeWeeklist is None:
            reply = QMessageBox.information(self.MainWindow,'SMI-DOWNLOADER','현재 애니시아 서버와 연결할수 없습니다!')
            return

        self.widgets.anime_time_table.setRowCount(len(animeWeeklist))
        self.widgets.anime_time_table.setColumnCount(7)
        self.widgets.anime_time_table.setFocusPolicy(Qt.NoFocus)

        font = QFont()
        font.setPointSize(pt(25, 40))
        font.setBold(QFont.Bold)

        for k in animeWeeklist:
            prefix = ""
            
            if idx < 7: #분기 애니메이션일 경우만
                date_str = datetime.now().strftime("%Y-%m-%d")
                currentDate = datetime.strptime(date_str, "%Y-%m-%d")

                startDate = None
                endDate = None

                if k.startDate != '':
                    startDate = datetime.strptime(k.startDate, '%Y-%m-%d')
                    #print("출력" + k.startDate)

                if k.endDate != '':
                    endDate = datetime.strptime(k.endDate, '%Y-%m-%d')
                    #print("출력" + k.endDate)

                if k.status == "OFF":
                    prefix = "[결방] "
                elif endDate is not None and currentDate > endDate:
                    prefix = "[完] "
                elif startDate is not None and currentDate <= startDate:
                    prefix = startDate.strftime("[%m-%d] ")

            item = QTableWidgetItem(k.time)
            item.setFont(font)

            self.widgets.anime_time_table.setItem(count,0,item);
            self.widgets.anime_time_table.setItem(count,1,QTableWidgetItem(prefix + k.subject));
            self.widgets.anime_time_table.setItem(count,2,QTableWidgetItem(str(k.animeNo)));
            self.widgets.anime_time_table.setItem(count,3,QTableWidgetItem(k.genres));
            
            self.widgets.anime_time_table.setItem(count,4,QTableWidgetItem(k.startDate));
            self.widgets.anime_time_table.setItem(count,5,QTableWidgetItem(str(k.captionCount)));
            self.widgets.anime_time_table.setItem(count,6,QTableWidgetItem(k.website));  
            count += 1     

        for row in range(self.widgets.anime_time_table.rowCount()):
            for column in range(self.widgets.anime_time_table.columnCount()):
                item = self.widgets.anime_time_table.item(row, column)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable) 

        self.widgets.anime_time_table.horizontalScrollBar().setValue(
                self.widgets.anime_time_table.horizontalScrollBar().minimum()
        )

    #편성표에서 클릭 했을때 
    def on_cell_clicked(self, row,column):
        #print(f"Row {row} {column}")

        item = self.widgets.anime_time_table.item(row, 1)
        if item is None:
            return

        anime = animeWeeklist[row]

        #if(selectedAnime_LeftBox is not anime):
        #    self.widgets.left_progressBar.hide()
        #    self.widgets.left_progressBar.setValue(0);

        common.show_anime_detail(self, anime, requestAnimeSubsInfo(anime))
