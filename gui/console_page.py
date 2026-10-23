
import os
import natsort
from datetime import datetime
from functools import partial
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from kudong import *


def _log_labels(path):
    kind = "download_subtitle"
    detail = "다운로드 로그 데이터"
    try:
        with open(path, "r", encoding="utf-8") as file:
            first = file.readline().strip()
            if first == "AI 자막 번역":
                kind = "ai_translate"
                detail = "AI 번역 로그"
            elif first == "SMI AUTO DOWNLOADER":
                kind = "welcome"
                detail = "처음 실행 안내"
    except OSError:
        pass
    return kind, detail


def refresh_log_table(table):
    folder = os.path.abspath(".") + "/log"
    try:
        names = [name for name in os.listdir(folder) if name != "error.log"]
    except OSError:
        names = []
    names = natsort.natsorted(names)

    overflow = len(names) - 30
    if overflow > 0:
        for name in names[:overflow]:
            path = os.path.join(folder, name)
            if os.path.isfile(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
        names = names[overflow:]

    table.clearContents()
    table.setColumnCount(3)
    table.setRowCount(len(names))
    for row, name in enumerate(names):
        kind, detail = _log_labels(os.path.join(folder, name))
        for column, text in enumerate((name, kind, detail)):
            item = QTableWidgetItem(text)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row, column, item)
    table.verticalScrollBar().setValue(table.verticalScrollBar().maximum())


# 3. Console
# ///////////////////////////////////////////////////////////////
class ConsolePage:
    def __init__(self, MainWindow, widgets):
        self.MainWindow = MainWindow
        self.widgets = widgets

        self.widgets.log_timestamp.setSelectionBehavior(QTableWidget.SelectRows)
        self.widgets.log_timestamp.verticalHeader().setDefaultSectionSize(40)
        self.widgets.log_timestamp.verticalHeader().setVisible(False)
        self.widgets.log_timestamp.verticalHeader().setSectionsMovable(False)
        self.widgets.log_timestamp.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.widgets.log_timestamp.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        self.widgets.log_timestamp.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        self.widgets.log_timestamp.cellClicked.connect(self.on_cell_clicked_console)
        self.widgets.log_timestamp.setFocusPolicy(Qt.NoFocus)
        refresh_log_table(self.widgets.log_timestamp)

        self.widgets.log_console.setReadOnly(True)
        self._select_latest_log()

    def _select_latest_log(self):
        table = self.widgets.log_timestamp
        row = table.rowCount() - 1
        if row < 0:
            return
        table.selectRow(row)
        self._show_log_row(row)

    #로그 클릭시
    def on_cell_clicked_console(self, row,column):
        self._show_log_row(row)

    def _show_log_row(self, row):
        item = self.widgets.log_timestamp.item(row, 0)
        if item is not None:
            file_name = item.text()
            with open(os.path.abspath('.') + "/log/" + file_name, 'r', encoding='utf-8') as file:
                text = file.read()
                self.widgets.log_console.setPlainText(text)
                self.widgets.log_console.verticalScrollBar().setValue(
                    self.widgets.log_console.verticalScrollBar().minimum()
                )