
from datetime import datetime
from functools import partial
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from kudong import *

isSearchThreadRunning = False

# 4. SEARCH
# ///////////////////////////////////////////////////////////////  
class SearchPage(QObject):
    def __init__(self, MainWindow, widgets):
        super().__init__()
        self.MainWindow = MainWindow
        self.widgets = widgets  
        self.page_info = None

        self.widgets.anime_search_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.widgets.anime_search_table.verticalHeader().setDefaultSectionSize(60)
        self.widgets.anime_search_table.verticalHeader().setVisible(False)
        self.widgets.anime_search_table.verticalHeader().setSectionsMovable(False)
        self.widgets.anime_search_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.widgets.anime_search_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.widgets.anime_search_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Fixed)
        self.widgets.anime_search_table.horizontalHeader().resizeSection(1, 620)
        self.widgets.anime_search_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        self.widgets.anime_search_table.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
        self.widgets.anime_search_table.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)
        self.widgets.anime_search_table.horizontalHeader().setSectionResizeMode(5,QHeaderView.ResizeToContents)
        self.widgets.anime_search_table.verticalScrollBar().valueChanged.connect(self.on_scroll_search_table)
        self.widgets.anime_search_table.cellClicked.connect(self.on_search_cell_clicked)
        self.widgets.search_button.clicked.connect(self.async_update_search_keyword_task)
        self.widgets.search_input.textChanged.connect(self.update_search_correct_task)
        self.widgets.search_input.returnPressed.connect(self.widgets.search_button.click)
        self.search_thread = SearchCorrectWorkerThread(self)

    def on_scroll_search_table(self):
        scroll_bar = self.widgets.anime_search_table.verticalScrollBar()
        if scroll_bar.value() == scroll_bar.maximum():
            self.scroll_thread = AsyncSearchWorkerThread(self)
            self.scroll_thread.setValue(self.load_more_data)
            self.scroll_thread.start()
            
    def load_more_data(self):
        if self.page_info.pageNumber + 1 >= self.page_info.totalPages:
            return

        search_list, page_info = requestSearchAnimeInfo(self.page_info.keyword, self.page_info.pageNumber + 1);   
        self.page_info = page_info

        font = QFont()
        font.setPointSize(25)
        font.setBold(QFont.Bold)

        start_row = self.widgets.anime_search_table.rowCount();

        for k in search_list:
            
            item = QTableWidgetItem(k.time)
            item.setFont(font)

            row = self.widgets.anime_search_table.rowCount()
            self.widgets.anime_search_table.insertRow(row)

            self.widgets.anime_search_table.setItem(row,0,item);
            self.widgets.anime_search_table.setItem(row,1,QTableWidgetItem(k.subject));
            self.widgets.anime_search_table.setItem(row,2,QTableWidgetItem(str(k.animeNo)));
            self.widgets.anime_search_table.setItem(row,3,QTableWidgetItem(k.genres));
            
            self.widgets.anime_search_table.setItem(row,4,QTableWidgetItem(k.startDate));
            self.widgets.anime_search_table.setItem(row,5,QTableWidgetItem(str(k.captionCount)));
            self.widgets.anime_search_table.setItem(row,6,QTableWidgetItem(k.website));  

        end_row = self.widgets.anime_search_table.rowCount();

        for row in range(start_row,end_row):
            for column in range(self.widgets.anime_search_table.columnCount()):
                item = self.widgets.anime_search_table.item(row, column)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable) 

    def async_update_search_keyword_task(self):
        global isSearchThreadRunning
        if isSearchThreadRunning is False:
            isSearchThreadRunning = True
            self.search_keyword_thread = AsyncSearchWorkerThread(self)
            self.search_keyword_thread.setValue(self.on_search_button_clicked)
            self.search_keyword_thread.start()

    def update_search_correct_task(self):
        current_text = self.widgets.search_input.text()
        self.search_thread.setValue(current_text)
        self.search_thread.start()

    def on_search_button_clicked(self):
            global isSearchThreadRunning
            keyword = self.widgets.search_input.text()

            if keyword == "/도움말":
                open_url("https://anissia.net/notice?topicNo=141")
                isSearchThreadRunning = False
                return

            search_list, page_info = requestSearchAnimeInfo(keyword);
            self.page_info = page_info

            count = 0
            
            if search_list is None:
                reply = QMessageBox.information(self.MainWindow,'SMI-DOWNLOADER','현재 애니시아 서버와 연결할수 없습니다!')
                isSearchThreadRunning = False
                return
            
            self.widgets.anime_search_table.clearContents()
            self.widgets.anime_search_table.verticalScrollBar().setValue(0)

            self.widgets.label_total_elements.setText("<html><head/><body><p><span style='font-size:12pt;'>총 "+str(page_info.totalElements)+"개의 작품이 검색되었습니다.</span></p></body></html>");    

            self.widgets.anime_search_table.setRowCount(len(search_list))
            self.widgets.anime_search_table.setColumnCount(7)

            self.widgets.anime_search_table.setFocusPolicy(Qt.NoFocus)

            font = QFont()
            font.setPointSize(25)
            font.setBold(QFont.Bold)

            for k in search_list:
                
                item = QTableWidgetItem(k.time)
                item.setFont(font)

                self.widgets.anime_search_table.setItem(count,0,item);
                self.widgets.anime_search_table.setItem(count,1,QTableWidgetItem(k.subject));
                self.widgets.anime_search_table.setItem(count,2,QTableWidgetItem(str(k.animeNo)));
                self.widgets.anime_search_table.setItem(count,3,QTableWidgetItem(k.genres));
                
                self.widgets.anime_search_table.setItem(count,4,QTableWidgetItem(k.startDate));
                self.widgets.anime_search_table.setItem(count,5,QTableWidgetItem(str(k.captionCount)));
                self.widgets.anime_search_table.setItem(count,6,QTableWidgetItem(k.website));  
                count += 1     

            for row in range(self.widgets.anime_search_table.rowCount()):
                for column in range(self.widgets.anime_search_table.columnCount()):
                    item = self.widgets.anime_search_table.item(row, column)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable) 

            self.widgets.anime_search_table.horizontalScrollBar().setValue(
                    self.widgets.anime_search_table.horizontalScrollBar().minimum()
            )

            isSearchThreadRunning = False


    def on_search_cell_clicked(self, row,column):
                #print(f"Row {row} {column}")
                item = self.widgets.anime_search_table.item(row, 2) # AnimeNo 가 None이 아닌지 체크

                if item is not None:
                    anime, subs = requestAnimeInfo(item.text());

                    selectedAnime_LeftBox = anime # local
                    common.selectedAnime_LeftBox = anime # global

                    #print("Item data:", anime.subject)

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

    @Slot(str)
    def update_search_correct(self, correct_keyword):
        self.widgets.search_input.setToolTip(correct_keyword)


class AsyncSearchWorkerThread(QThread):
    def __init__(self, search_page):
        super().__init__()

    def setValue(self, callback):
        self.callback = callback       

    def run(self):
        self.callback()

class SearchCorrectWorkerThread(QThread):
    def __init__(self, search_page):
        super().__init__()
        self.search_page = search_page

    def setValue(self,keyword):
        self.keyword = keyword

    def run(self):
        list = requestSearchAnimeCorrect(self.keyword)
        if list is not None:
            correct_keyword = "\n".join(list)
            # print(correct_keyword)
            QMetaObject.invokeMethod(self.search_page, "update_search_correct", Qt.QueuedConnection,Q_ARG(str,correct_keyword))