from datetime import datetime
from functools import partial
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from kudong import *
from modules.font_config import fs, pt

animeWeeklist = []
animeWeekIdx = 0

ON_AIR_DURATION = 30 # 방영 시간을 시작 후 30분으로 가정
ON_AIR_BG_COLOR = QColor(190, 40, 40)
ON_AIR_TEXT_COLOR = QColor(255, 255, 255)

# 오늘 요일을 편성표 인덱스(일요일 = 0)로 변환
def currentWeekIdx():
    weekday_index = datetime.now().weekday()

    if weekday_index == 6:
        return 0
    return weekday_index + 1

# hh:mm 문자열을 0시 기준 분으로 변환 (24:30 처럼 24시 이상 표기는 다음날로 환산)
def parseTimeToMinutes(time_str):
    try:
        hour, minute = str(time_str).split(":")
        return (int(hour) * 60 + int(minute)) % 1440
    except Exception:
        return None

# 아무곳이나 클릭하면 On-AIR 하이라이트를 해제하는 필터
class OnAirClickFilter(QObject):

    def __init__(self, page):
        super().__init__()
        self.page = page

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.page.clearOnAirHighlight()
        return False

# 방영 중인 행의 배경을 붉은색으로 그립니다.
# 스타일시트의 QTableWidget::item 규칙이 QTableWidgetItem 의 배경색을 덮어쓰므로 직접 그립니다.
class OnAirRowDelegate(QStyledItemDelegate):

    def __init__(self, page):
        super().__init__()
        self.page = page

    def paint(self, painter, option, index):
        if index.row() in self.page.onAirRows and not (option.state & QStyle.State_Selected):
            painter.save()
            painter.fillRect(option.rect, ON_AIR_BG_COLOR)
            painter.restore()
            option.palette.setColor(QPalette.Text, ON_AIR_TEXT_COLOR)
        super().paint(painter, option, index)

# 1. Schedule Page
# //////////////////////////////////////////////////////////////////
class SchedulePage:

    def __init__(self, MainWindow, widgets):

        self.MainWindow = MainWindow
        self.widgets = widgets  

        self.onAirRows = []
        self.onAirClickFilter = OnAirClickFilter(self)
        self.isOnAirFilterInstalled = False

        self.onAirDelegate = OnAirRowDelegate(self)
        widgets.anime_time_table.setItemDelegate(self.onAirDelegate)

        self.widgets.onAirButton.clicked.connect(self.clickOnAirButton)

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

        self.clickWeekendButton(currentWeekIdx());

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
        self.clearOnAirHighlight()
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

    # On-AIR 버튼 클릭시 오늘 요일 편성표에서 방영 중인 작품을 하이라이트 합니다.
    def clickOnAirButton(self):
        if self.widgets.stackedWidget.currentWidget() is not self.widgets.anime_schedule:
            self.widgets.btn_home.click() # 편성표 페이지로 이동

        self.clickWeekendButton(currentWeekIdx())

        if animeWeeklist is None:
            return

        self.setOnAirHighlight(self.getOnAirRows())

    # 현재 시각을 기준으로 방영 중인 행 번호를 구합니다.
    def getOnAirRows(self):
        now = datetime.now()
        nowMinutes = now.hour * 60 + now.minute

        startMinutes = {}
        for row, k in enumerate(animeWeeklist):
            minutes = parseTimeToMinutes(k.time)
            if minutes is not None:
                startMinutes[row] = minutes

        # 시작 후 ON_AIR_DURATION 분 이내인 작품 (겹치는 작품은 모두 포함)
        onAirRows = [row for row, minutes in startMinutes.items()
                     if minutes <= nowMinutes < minutes + ON_AIR_DURATION]

        if len(onAirRows) > 0:
            return onAirRows

        # 방영 중인 작품이 없다면 가장 가까운 다음 방영 작품
        nextMinutes = [minutes for minutes in startMinutes.values() if minutes > nowMinutes]

        if len(nextMinutes) == 0:
            return []

        return [row for row, minutes in startMinutes.items() if minutes == min(nextMinutes)]

    # 해당 행들을 붉은색으로 하이라이트 합니다.
    def setOnAirHighlight(self, rows):
        if len(rows) == 0:
            return

        table = self.widgets.anime_time_table
        table.clearSelection() # 선택 색상이 하이라이트를 덮지 않도록 해제

        self.onAirRows = list(rows)
        table.viewport().update()
        self.scrollToOnAirRow()

        if not self.isOnAirFilterInstalled:
            QApplication.instance().installEventFilter(self.onAirClickFilter)
            self.isOnAirFilterInstalled = True

    # 첫번째 하이라이트 행이 화면 중앙에 오도록 스크롤 합니다.
    def scrollToOnAirRow(self):
        if len(self.onAirRows) == 0:
            return

        table = self.widgets.anime_time_table
        row = min(self.onAirRows)

        if row >= table.rowCount() or table.item(row, 0) is None:
            return

        # 표를 새로 채운 직후에는 행 배치와 스크롤 범위 계산이 미뤄져서
        # 그대로 스크롤하면 엉뚱한 위치로 이동하므로 먼저 배치를 확정합니다.
        table.executeDelayedItemsLayout()
        table.scrollToItem(table.item(row, 0), QAbstractItemView.PositionAtCenter)

    # 하이라이트를 원래 색상으로 되돌립니다.
    def clearOnAirHighlight(self):
        if len(self.onAirRows) == 0:
            return

        self.onAirRows = []
        self.widgets.anime_time_table.viewport().update()

        if self.isOnAirFilterInstalled:
            QApplication.instance().removeEventFilter(self.onAirClickFilter)
            self.isOnAirFilterInstalled = False

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
