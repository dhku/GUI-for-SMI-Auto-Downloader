import html
import os
import re
from functools import partial
from urllib.parse import unquote, urlparse

import requests
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from kudong import *
from modules.font_config import fs

URL_ROLE = Qt.UserRole
NAME_ROLE = Qt.UserRole + 1
BUTTON_STYLE = "background-color: rgb(52, 59, 72);\nfont-size: 20px;\noutline: none;"
DOWNLOAD_BUTTON_STYLE = BUTTON_STYLE + '\nfont-family: "Malgun Gothic";'
BUTTON_DONE_STYLE = (
    'QPushButton { background-color: rgb(45, 106, 79); font-size: 20px; font-family: "Malgun Gothic";'
    " outline: none; border: 2px solid rgb(45, 106, 79); border-radius: 5px; }"
    "QPushButton:hover { background-color: rgb(54, 124, 92); border: 2px solid rgb(62, 140, 104); }"
    "QPushButton:pressed { background-color: rgb(36, 86, 64); border: 2px solid rgb(36, 86, 64); }"
)


class _NoFocusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.state = option.state & ~QStyle.State_HasFocus
        super().paint(painter, option, index)


def format_size(size):
    try:
        value = int(size)
    except (TypeError, ValueError):
        return "-"
    if value < 1024:
        return str(value) + " B"
    if value < 1024 * 1024:
        return f"{value / 1024:.1f} KB"
    return f"{value / (1024 * 1024):.1f} MB"


def safe_filename(name, url):
    raw = name or os.path.basename(unquote(urlparse(url).path)) or "subtitle"
    raw = unquote(str(raw))
    raw = os.path.basename(raw.replace("\\", "/"))
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", raw).strip(" .")
    return cleaned or "subtitle"


class AiSearchWorker(QThread):
    result_ready = Signal(int, object)

    def __init__(self, token, keyword, parent=None):
        super().__init__(parent)
        self.token = token
        self.keyword = keyword

    def run(self):
        self.result_ready.emit(self.token, requestJimakuFiles(self.keyword))


class AiDownloadWorker(QThread):
    result_ready = Signal(int, str, bool, str)

    def __init__(self, row, url, dest, parent=None):
        super().__init__(parent)
        self.row = row
        self.url = url
        self.dest = dest

    def run(self):
        partial_path = self.dest + ".part"
        try:
            os.makedirs(os.path.dirname(self.dest), exist_ok=True)
            with requests.get(
                self.url,
                stream=True,
                timeout=60,
                headers={"User-Agent": "SMI-Auto-Downloader"},
            ) as response:
                response.raise_for_status()
                with open(partial_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=512 * 1024):
                        if chunk:
                            file.write(chunk)
            os.replace(partial_path, self.dest)
            self.result_ready.emit(self.row, self.url, True, self.dest)
        except Exception as error:
            if os.path.isfile(partial_path):
                try:
                    os.remove(partial_path)
                except OSError:
                    pass
            self.result_ready.emit(self.row, self.url, False, str(error))


# AI 자막 페이지
# ///////////////////////////////////////////////////////////////
class AiPage(QObject):
    def __init__(self, MainWindow, widgets):
        super().__init__()
        self.MainWindow = MainWindow
        self.widgets = widgets
        self.workers = []
        self.search_workers = []
        self._load_token = 0
        self.japanese_name = ""
        self.english_name = ""

        self._setup_header()

        table = self.widgets.ai_subtitle_table
        self._adjusting_selection = False
        table.setSelectionBehavior(QAbstractItemView.SelectItems)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        table.itemSelectionChanged.connect(self._limit_row_selection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setFocusPolicy(Qt.NoFocus)
        table.setItemDelegate(_NoFocusDelegate(table))
        table.setStyleSheet(
            table.styleSheet()
            + "QTableWidget { outline: 0; }"
            + "QTableWidget::item:focus { outline: none; border: none; }"
        )
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setFocusPolicy(Qt.NoFocus)
        table.verticalHeader().setDefaultSectionSize(68)
        table.horizontalHeader().setVisible(True)
        table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.set_files([])

    def _setup_header(self):
        title_row = self.widgets.ai_row_1
        title_row.setMaximumSize(QSize(16777215, 56))
        title_row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.widgets.label_ai_title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        count = self.widgets.label_ai_count
        count.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        count.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.widgets.ai_row_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        search_row = QFrame(self.widgets.ai_page)
        search_row.setObjectName("ai_search_row")
        search_row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QHBoxLayout(search_row)
        layout.setContentsMargins(9, 0, 9, 0)

        field_style = "background-color: rgb(33, 37, 43);\nfont-size: 20px;"
        button_style = BUTTON_STYLE

        self.ai_search_input = QLineEdit(search_row)
        self.ai_search_input.setObjectName("ai_search_input")
        self.ai_search_input.setPlaceholderText("일본어 원제 또는 영어 제목")
        self.ai_search_input.setMinimumSize(QSize(160, 60))
        self.ai_search_input.setStyleSheet(field_style)
        self.ai_search_input.returnPressed.connect(self.on_search_clicked)

        self.ai_search_button = QPushButton("검색", search_row)
        self.ai_search_button.setObjectName("ai_search_button")
        self.ai_search_button.setCursor(Qt.PointingHandCursor)
        self.ai_search_button.setMinimumSize(QSize(110, 60))
        self.ai_search_button.setStyleSheet(button_style)
        self.ai_search_button.clicked.connect(self.on_search_clicked)

        self.ai_download_all_button = QPushButton("일괄 다운로드", search_row)
        self.ai_download_all_button.setObjectName("ai_download_all_button")
        self.ai_download_all_button.setCursor(Qt.PointingHandCursor)
        self.ai_download_all_button.setMinimumSize(QSize(160, 60))
        self.ai_download_all_button.setStyleSheet(button_style)
        self.ai_download_all_button.clicked.connect(self.on_download_all_clicked)

        layout.addWidget(self.ai_search_input, 1)
        layout.addWidget(self.ai_search_button)
        layout.addWidget(self.ai_download_all_button)
        self.widgets.verticalLayout_29.insertWidget(1, search_row)

    def load_selected_anime(self):
        anime = common.selectedAnime_LeftBox
        keyword = ""
        if anime is not None:
            keyword = str(anime.originalSubject or "").strip()

        self.ai_search_input.setText(keyword)
        if keyword == "":
            self.set_files([])
            return
        self._search(keyword)

    def on_search_clicked(self):
        keyword = self.ai_search_input.text().strip()
        if keyword == "":
            QMessageBox.information(self.MainWindow, "SMI-DOWNLOADER", "검색어를 입력해주세요.")
            return
        self._search(keyword)

    def _search(self, keyword):
        self.japanese_name = ""
        self.english_name = ""
        self.set_files([])
        self._load_token += 1
        token = self._load_token
        self._set_count_text("불러오는 중")

        worker = AiSearchWorker(token, keyword, self)
        worker.result_ready.connect(self._on_jimaku_files)
        worker.finished.connect(self._drop_search_worker)
        self.search_workers.append(worker)
        worker.start()

    def _on_jimaku_files(self, token, result):
        if token != self._load_token:
            return
        if not isinstance(result, dict):
            self.japanese_name = ""
            self.english_name = ""
            self.set_files([])
            QMessageBox.warning(
                self.MainWindow,
                "SMI-DOWNLOADER",
                "jimaku.cc에서 자막 목록을 가져오지 못했습니다.",
            )
            return
        self.japanese_name = str(result.get("japanese_name") or "")
        self.english_name = str(result.get("english_name") or "")
        self.set_files(result.get("files") or [])

    def _drop_search_worker(self):
        worker = self.sender()
        if worker in self.search_workers:
            self.search_workers.remove(worker)

    def _set_count_text(self, text):
        name = html.escape(self.japanese_name)
        if name:
            body = name + " · " + text
        else:
            body = text
        self.widgets.label_ai_count.setToolTip(self.english_name)
        self.widgets.label_ai_count.setText(
            "<html><head/><body><p align='right'><span style='font-size:"
            + str(fs(12, 22))
            + "pt;'>"
            + body
            + "</span></p></body></html>"
        )

    def set_files(self, files):
        table = self.widgets.ai_subtitle_table
        files = files or []
        table.setRowCount(0)
        table.setColumnCount(4)
        table.setRowCount(len(files))
        table.setHorizontalHeaderLabels(["선택", "제목", "크기", ""])
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.resizeSection(0, 70)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.resizeSection(3, 150)
        header_item = table.horizontalHeaderItem(0)
        if header_item is not None:
            header_item.setToolTip("클릭하면 전체를 선택하거나 해제합니다.")

        self._set_count_text(str(len(files)) + "개 파일")

        for row, entry in enumerate(files):
            name = str(entry.get("name") or "")
            url = str(entry.get("url") or "")
            modified = str(entry.get("last_modified") or "")

            name_item = QTableWidgetItem(name)
            name_item.setData(URL_ROLE, url)
            name_item.setData(NAME_ROLE, name)
            name_item.setToolTip(modified)
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)

            size_item = QTableWidgetItem(format_size(entry.get("size")))
            size_item.setTextAlignment(Qt.AlignCenter)
            size_item.setFlags(size_item.flags() & ~Qt.ItemIsEditable)

            table.setCellWidget(row, 0, self._make_checkbox())
            table.setItem(row, 1, name_item)
            table.setItem(row, 2, size_item)

            button = QPushButton("다운로드")
            self._style_action_button(button)
            button.clicked.connect(partial(self.on_download_clicked, row))
            table.setCellWidget(row, 3, button)

    def _style_action_button(self, button, done=False):
        button.setCursor(Qt.PointingHandCursor)
        button.setFocusPolicy(Qt.NoFocus)
        button.setMinimumHeight(48)
        button.setStyleSheet(BUTTON_DONE_STYLE if done else DOWNLOAD_BUTTON_STYLE)

    def _make_checkbox(self):
        wrap = QWidget()
        wrap.setFocusPolicy(Qt.NoFocus)
        wrap.setStyleSheet("background-color: transparent;")
        layout = QHBoxLayout(wrap)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        box = QCheckBox(wrap)
        box.setFocusPolicy(Qt.NoFocus)
        box.setCursor(Qt.PointingHandCursor)
        layout.addWidget(box)
        return wrap

    def _checkbox_at(self, row):
        wrap = self.widgets.ai_subtitle_table.cellWidget(row, 0)
        if isinstance(wrap, QCheckBox):
            return wrap
        if wrap is None:
            return None
        return wrap.findChild(QCheckBox)

    def _on_header_clicked(self, index):
        if index != 0:
            return
        table = self.widgets.ai_subtitle_table
        boxes = [self._checkbox_at(row) for row in range(table.rowCount())]
        boxes = [box for box in boxes if box is not None]
        if not boxes:
            return
        checked = not all(box.isChecked() for box in boxes)
        for box in boxes:
            box.setChecked(checked)

    def _limit_row_selection(self):
        if self._adjusting_selection:
            return

        table = self.widgets.ai_subtitle_table
        selected = [index for index in table.selectedIndexes() if index.column() not in (0, 3)]
        self._adjusting_selection = True
        table.clearSelection()
        if selected:
            row = selected[-1].row()
            for column in (1, 2):
                item = table.item(row, column)
                if item is not None:
                    item.setSelected(True)
        self._adjusting_selection = False

    def on_download_all_clicked(self):
        table = self.widgets.ai_subtitle_table
        rows = []
        for row in range(table.rowCount()):
            box = self._checkbox_at(row)
            if box is not None and box.isChecked():
                rows.append(row)
        if not rows:
            QMessageBox.information(self.MainWindow, "SMI-DOWNLOADER", "다운로드할 파일을 선택해주세요.")
            return
        for row in rows:
            self.on_download_clicked(row)

    def on_download_clicked(self, row, checked=False):
        table = self.widgets.ai_subtitle_table
        item = table.item(row, 1)
        button = table.cellWidget(row, 3)
        if item is None or not isinstance(button, QPushButton) or not button.isEnabled():
            return

        url = item.data(URL_ROLE)
        name = item.data(NAME_ROLE) or item.text()
        if not url:
            QMessageBox.warning(self.MainWindow, "SMI-DOWNLOADER", "다운로드 주소가 없습니다.")
            return

        base = get_global_outpath() or os.path.join(os.path.abspath("."), "downloads")
        dest = os.path.join(base, "ai", safe_filename(name, url))

        button.setEnabled(False)
        button.setText("받는 중")

        worker = AiDownloadWorker(row, url, dest, self)
        worker.result_ready.connect(self.on_download_finished)
        worker.finished.connect(self._drop_worker)
        self.workers.append(worker)
        worker.start()

    def on_download_finished(self, row, url, ok, message):
        table = self.widgets.ai_subtitle_table
        item = table.item(row, 1)
        button = table.cellWidget(row, 3)
        same_row = item is not None and item.data(URL_ROLE) == url
        if same_row and isinstance(button, QPushButton):
            button.setEnabled(True)
            button.setText("완료" if ok else "다운로드")
            self._style_action_button(button, done=ok)

        if ok:
            return

        QMessageBox.warning(
            self.MainWindow,
            "SMI-DOWNLOADER",
            "자막 파일을 받지 못했습니다.\n" + message,
        )

    def _drop_worker(self):
        worker = self.sender()
        if worker in self.workers:
            self.workers.remove(worker)
