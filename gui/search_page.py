
from datetime import datetime
from functools import partial
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from kudong import *
from modules.font_config import fs, pt

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
        font.setPointSize(pt(25, 40))
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

            self.widgets.label_total_elements.setText("<html><head/><body><p><span style='font-size:" + str(fs(12, 22)) + "pt;'>총 "+str(page_info.totalElements)+"개의 작품이 검색되었습니다.</span></p></body></html>");    

            self.widgets.anime_search_table.setRowCount(len(search_list))
            self.widgets.anime_search_table.setColumnCount(7)

            self.widgets.anime_search_table.setFocusPolicy(Qt.NoFocus)

            font = QFont()
            font.setPointSize(pt(25, 40))
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
        if item is None:
            return

        anime, subs = requestAnimeInfo(item.text());
        common.show_anime_detail(self, anime, subs)

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