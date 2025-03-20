from datetime import datetime
from functools import partial
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from kudong import *

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
        beforeSheet = "background-color: rgb(52, 59, 72); font-size: 32px; font-weight: bold;"
        self.setWeekendButtonStyle(animeWeekIdx, beforeSheet)
        afterSheet = "background-color: rgb(156, 179, 199); font-size: 32px; font-weight: bold; color: rgb(255, 255, 255);"
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
        font.setPointSize(25)
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
        if item is not None:
            anime = animeWeeklist[row]

            #if(selectedAnime_LeftBox is not anime):
            #    self.widgets.left_progressBar.hide()
            #    self.widgets.left_progressBar.setValue(0);
                
            selectedAnime_LeftBox = anime # local
            common.selectedAnime_LeftBox = anime # global

            # print("Item data:", common.selectedAnime_LeftBox.subject)

            self.widgets.label.setText("<html><head/><body><p align='center'><span style=' font-size:20pt; font-weight:bold;'>"+anime.subject+"</span></p></body></html>");
            self.widgets.label.setWordWrap(True)

            startDate = None;
            endDate = None;
            currentDate = datetime.now();

            if anime.startDate != '':

                try:
                    startDate = datetime.strptime(anime.startDate, '%Y-%m-%d')
                except Exception as e:  
                    startDate = None;

                try:
                    endDate = datetime.strptime(anime.endDate, '%Y-%m-%d')
                except Exception as e:  
                    endDate = None;  
                
                week_Ko = None;

                if anime.weekNo == 0:
                    week_Ko = "일"
                elif anime.weekNo == 1:  
                    week_Ko = "월"
                elif anime.weekNo == 2:  
                    week_Ko = "화"
                elif anime.weekNo == 3:  
                    week_Ko = "수"
                elif anime.weekNo == 4:  
                    week_Ko = "목"
                elif anime.weekNo == 5:  
                    week_Ko = "금"
                elif anime.weekNo == 6:  
                    week_Ko = "토"

                if anime.status == 'ON':
                    if startDate is not None and currentDate <= startDate :
                        self.widgets.label_date.setText("<html><head/><body><p align='center'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+"</span></p></body></html>");
                        self.widgets.label_date.setWordWrap(True)
                        self.widgets.label_date.show()
                    else:
                        if endDate is not None:
                            if startDate == endDate:
                                self.widgets.label_date.setText("<html><head/><body><p align='center'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+"</span></p></body></html>");
                                self.widgets.label_date.setWordWrap(True)
                                self.widgets.label_date.show()
                            else:
                                time_obj = datetime.strptime(anime.time, "%H:%M")
                                formatted_time = time_obj.strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
                                self.widgets.label_date.setText("<html><head/><body><p align='center' style='line-height:0.6;'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+" ~ "+endDate.strftime("%Y. %m. %d.")+"</span></p><p align='center'><span style=' font-size:16pt;'>"+"매주 ("+week_Ko +") "+formatted_time+"</span></p></body></html>");
                                self.widgets.label_date.setWordWrap(True)
                                self.widgets.label_date.show()
                        else:
                            try:
                                time_obj = datetime.strptime(anime.time, "%H:%M") # 2025-99-99 가 넘어오면 예외처리
                                formatted_time = time_obj.strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
                                self.widgets.label_date.setText("<html><head/><body><p align='center' style='line-height:0.6;'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d. ~ 방영중")+"</span></p><p align='center'><span style=' font-size:16pt;'>"+"매주 ("+week_Ko +") "+formatted_time+"</span></p></body></html>");
                                self.widgets.label_date.setWordWrap(True)
                                self.widgets.label_date.show()
                            except Exception as e:  
                                try:
                                    self.widgets.label_date.setText("<html><head/><body><p align='center'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+"</span></p></body></html>");
                                    self.widgets.label_date.setWordWrap(True)
                                    self.widgets.label_date.show()
                                except Exception as e2: 
                                    self.widgets.label_date.hide()
                elif anime.status == 'END':
                    self.widgets.label_date.setText("<html><head/><body><p align='center' style='line-height:0.6;'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+" ~ "+endDate.strftime("%Y. %m. %d.")+"</span></p><p align='center'><span style=' font-size:16pt;'>완결</span></p></body></html>");
                    self.widgets.label_date.setWordWrap(True)
                    self.widgets.label_date.show()           
                else:
                    self.widgets.label_date.setText("<html><head/><body><p align='center' style='line-height:0.6;'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d. ~ 방영중")+"</span></p><p align='center'><span style=' font-size:16pt;'>결방</span></p></body></html>");
                    self.widgets.label_date.setWordWrap(True)
                    self.widgets.label_date.show()
            else:
                self.widgets.label_date.hide() 

            subs = requestAnimeSubsInfo(anime)

            spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

            layout = self.widgets.extraCenter.layout()

            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

            for k in subs:
                name = k.name
                episode = k.episode
                website = k.website
                updDtStr = k.updDt

                updDt = datetime.strptime(updDtStr, "%Y-%m-%dT%H:%M:%S")
                currentDt = datetime.now();

                time_diff = currentDt - updDt
                time_diff_str = ""
                #print("time_diff = " + time_diff)

                time_diff_prefix = " ("
                total_sec = time_diff.total_seconds();

                if total_sec < 60: # 60초 이내
                    time_diff_str = time_diff_prefix + str(round(total_sec)) + "초 전)"
                elif total_sec < 3600: # 60분 이내
                    time_diff_str = time_diff_prefix + str(round(total_sec/60)) + "분 전)"
                elif total_sec < 86400: # 24시간 이내
                    time_diff_str = time_diff_prefix + str(round(total_sec/3600)) + "시간 전)"
                elif total_sec < 2592000: #30일 이내
                    time_diff_str = time_diff_prefix + str(round(total_sec/86400)) + "일 전)"
                else: 
                    time_diff_str = time_diff_prefix + updDtStr[:updDtStr.rfind("T")] +")"

                if(website == ""):
                    button = QPushButton("준비중 "+name+ " "+updDtStr[:updDtStr.rfind("T")])
                else:
                    button = QPushButton(episode+"화 "+name + time_diff_str)
                    button.clicked.connect(partial(open_url,website))

                button.setMinimumSize(0, 60)
                button.setStyleSheet("font-size: 20px; color: rgb(0, 0, 0);")
                layout.addWidget(button)

            layout.addItem(spacer)
            self.widgets.extraCenter.setLayout(layout);
            self.MainWindow.openLeftBox()
