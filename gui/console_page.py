
import os
import natsort
from datetime import datetime
from functools import partial
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from kudong import *

# 3. Console
# ///////////////////////////////////////////////////////////////
class ConsolePage:
    def __init__(self, MainWindow, widgets):
        self.MainWindow = MainWindow
        self.widgets = widgets  

        log_file_list = natsort.natsorted(os.listdir(os.path.abspath('.') + "/log"))
        log_file_list.remove("error.log")

        #로그 30개 이상시 이전 로그 제거
        log_size = len(log_file_list)
        if(log_size > 30):
            for i in range(0,log_size - 30):
                file_p = os.path.abspath('.') + "/log/"+log_file_list[i]
                if os.path.isfile(file_p):
                    os.remove(file_p)

        self.widgets.log_timestamp.clearContents()
        self.widgets.log_timestamp.setRowCount(len(log_file_list))
        self.widgets.log_timestamp.setColumnCount(3)

        count = 0
        for f in log_file_list:
            self.widgets.log_timestamp.setItem(count,0,QTableWidgetItem(f));
            self.widgets.log_timestamp.setItem(count,1,QTableWidgetItem("download_subtitle"));
            self.widgets.log_timestamp.setItem(count,2,QTableWidgetItem("다운로드 로그 데이터"));
            count += 1                 

        for row in range(self.widgets.log_timestamp.rowCount()):
            for column in range(self.widgets.log_timestamp.columnCount()):
                item = self.widgets.log_timestamp.item(row, column)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable) 

        self.widgets.log_timestamp.setSelectionBehavior(QTableWidget.SelectRows)
        self.widgets.log_timestamp.verticalHeader().setDefaultSectionSize(40)
        self.widgets.log_timestamp.verticalHeader().setVisible(False)
        self.widgets.log_timestamp.verticalHeader().setSectionsMovable(False)
        self.widgets.log_timestamp.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.widgets.log_timestamp.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.widgets.log_timestamp.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        self.widgets.log_timestamp.cellClicked.connect(self.on_cell_clicked_console)
        self.widgets.log_timestamp.setFocusPolicy(Qt.NoFocus)
        
        self.widgets.log_timestamp.verticalScrollBar().setValue(
            self.widgets.log_timestamp.verticalScrollBar().maximum()
        )

        self.widgets.log_console.setReadOnly(True)

    #로그 클릭시
    def on_cell_clicked_console(self, row,column):
        item = self.widgets.log_timestamp.item(row, 0)
        if item is not None:
            file_name = item.text()
            with open(os.path.abspath('.') + "/log/" + file_name, 'r', encoding='utf-8') as file:
                text = file.read()
                self.widgets.log_console.setPlainText(text)
                self.widgets.log_console.verticalScrollBar().setValue(
                    self.widgets.log_console.verticalScrollBar().minimum()
                )