from datetime import datetime
from functools import partial
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from kudong import *
from modules.font_config import fs, pt

isRecentThreadRunning = False

# 5. RECENT PAGE
# ///////////////////////////////////////////////////////////////  
class RecentPage(QObject):
    def __init__(self, MainWindow, widgets):
        super().__init__()
        self.MainWindow = MainWindow
        self.widgets = widgets  
        self.page_info = None
        self.widgets.anime_recent_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.widgets.anime_recent_table.verticalHeader().setDefaultSectionSize(60)
        self.widgets.anime_recent_table.verticalHeader().setVisible(False)
        self.widgets.anime_recent_table.verticalHeader().setSectionsMovable(False)
        self.widgets.anime_recent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.widgets.anime_recent_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.widgets.anime_recent_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        self.widgets.anime_recent_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.Fixed)
        self.widgets.anime_recent_table.horizontalHeader().resizeSection(2, 610)
        self.widgets.anime_recent_table.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
        self.widgets.anime_recent_table.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)
        self.widgets.anime_recent_table.verticalScrollBar().valueChanged.connect(self.on_scroll_recent_table)
        self.widgets.anime_recent_table.cellClicked.connect(self.on_recent_cell_clicked)
        self.widgets.anime_recent_table.cellDoubleClicked.connect(self.on_double_click)

        self.widgets.anime_recent_table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.widgets.anime_recent_table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.widgets.anime_recent_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def on_double_click(self, row, column):
        item = self.widgets.anime_recent_table.item(row, 5)
        open_url(item.text())
        
    def async_update_recent_task(self):
        global isRecentThreadRunning
        if isRecentThreadRunning is False:
            isRecentThreadRunning = True
            self.recent_thread = AsyncRecentWorkerThread(self)
            self.recent_thread.setValue(self.update_recent_task)
            self.recent_thread.start()

    def on_scroll_recent_table(self):
        scroll_bar = self.widgets.anime_recent_table.verticalScrollBar()
        if scroll_bar.value() == scroll_bar.maximum():
            self.scroll_thread = AsyncRecentWorkerThread(self)
            self.scroll_thread.setValue(self.load_more_data)
            self.scroll_thread.start()
            
    def load_more_data(self):
        if self.page_info.pageNumber + 1 >= self.page_info.totalPages:
            return

        search_list, page_info = requestRecentAnimeInfo(self.page_info.pageNumber + 1);
        self.page_info = page_info

        font = QFont()
        font.setPointSize(pt(20, 40))
        font.setBold(QFont.Bold)

        start_row = self.widgets.anime_recent_table.rowCount();

        for k in search_list:
            
            item = QTableWidgetItem(self.calculateDateTime(k.updDt))
            item.setFont(font)

            row = self.widgets.anime_recent_table.rowCount()
            self.widgets.anime_recent_table.insertRow(row)

            self.widgets.anime_recent_table.setItem(row,0,item);
            self.widgets.anime_recent_table.setItem(row,1,QTableWidgetItem(k.episode +"화"));
            self.widgets.anime_recent_table.setItem(row,2,QTableWidgetItem(k.subject));
            self.widgets.anime_recent_table.setItem(row,3,QTableWidgetItem(k.name)); 
            self.widgets.anime_recent_table.setItem(row,4,QTableWidgetItem(str(k.animeNo))); 
            self.widgets.anime_recent_table.setItem(row,5,QTableWidgetItem(str(k.website))); 

        end_row = self.widgets.anime_recent_table.rowCount();

        for row in range(start_row,end_row):
            for column in range(self.widgets.anime_recent_table.columnCount()):
                item = self.widgets.anime_recent_table.item(row, column)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable) 


    def update_recent_task(self):
        global isRecentThreadRunning
        search_list, page_info = requestRecentAnimeInfo()
        self.page_info = page_info
        
        count = 0
        
        if search_list is None:
            reply = QMessageBox.information(self.MainWindow,'SMI-DOWNLOADER','현재 애니시아 서버와 연결할수 없습니다!')
            isRecentThreadRunning = False
            return
        
        self.widgets.anime_recent_table.clearContents()
        self.widgets.anime_recent_table.verticalScrollBar().setValue(0)

        self.widgets.label_recemt_total_elements.setText("<html><head/><body><p><span style='font-size:" + str(fs(12, 22)) + "pt;'>최근 90일 데이터 / 총 "+str(page_info.totalElements)+" 작품</span></p></body></html>");    

        self.widgets.anime_recent_table.setRowCount(len(search_list))
        self.widgets.anime_recent_table.setColumnCount(6)

        self.widgets.anime_recent_table.setFocusPolicy(Qt.NoFocus)

        font = QFont()
        font.setPointSize(pt(20, 40))
        font.setBold(QFont.Bold)

        for k in search_list:
            
            item = QTableWidgetItem(self.calculateDateTime(k.updDt))
            item.setFont(font)

            self.widgets.anime_recent_table.setItem(count,0,item);
            self.widgets.anime_recent_table.setItem(count,1,QTableWidgetItem(k.episode +"화"));
            self.widgets.anime_recent_table.setItem(count,2,QTableWidgetItem(k.subject));
            self.widgets.anime_recent_table.setItem(count,3,QTableWidgetItem(k.name)); 
            self.widgets.anime_recent_table.setItem(count,4,QTableWidgetItem(str(k.animeNo))); 
            self.widgets.anime_recent_table.setItem(count,5,QTableWidgetItem(str(k.website))); 
            count += 1

        for row in range(self.widgets.anime_recent_table.rowCount()):
            for column in range(self.widgets.anime_recent_table.columnCount()):
                item = self.widgets.anime_recent_table.item(row, column)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable) 

        self.widgets.anime_recent_table.horizontalScrollBar().setValue(
                self.widgets.anime_recent_table.horizontalScrollBar().minimum()
        )

        isRecentThreadRunning = False

    def calculateDateTime(self, value):
        updDtStr = value
        updDt = datetime.strptime(updDtStr, "%Y-%m-%dT%H:%M:%S")
        currentDt = datetime.now();

        time_diff = currentDt - updDt
        time_diff_str = ""
        #print("time_diff = " + time_diff)

        result = ""
        total_sec = time_diff.total_seconds();

        if total_sec < 60: # 60초 이내
            result = str(round(total_sec)).rjust(2) + "초 전"
        elif total_sec < 3600: # 60분 이내
            result = str(round(total_sec/60)).rjust(2) + "분 전"
        elif total_sec < 86400: # 24시간 이내
            result = str(round(total_sec/3600)).rjust(2) + "시간 전"
        else:
            result = str(round(total_sec/86400)).rjust(2) + "일 전"
        # elif total_sec < 2592000: #30일 이내
        #     result = str(round(total_sec/86400)).rjust(2) + "일 전"
        # else: 
        #     result = updDtStr[:updDtStr.rfind("T")]

        return result
    
    def on_recent_cell_clicked(self, row,column):
        #print(f"Row {row} {column}")
        item = self.widgets.anime_recent_table.item(row, 4) # AnimeNo 가 None이 아닌지 체크
        if item is None:
            return

        anime, subs = requestAnimeInfo(item.text());
        common.show_anime_detail(self, anime, subs)
    
class AsyncRecentWorkerThread(QThread):
    def __init__(self, search_page):
        super().__init__()

    def setValue(self, callback):
        self.callback = callback       

    def run(self):
        self.callback()