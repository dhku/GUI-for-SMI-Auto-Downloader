import html
import os
import platform
import re
import subprocess
import threading
from datetime import datetime
from functools import partial
from urllib.parse import unquote, urlparse

import requests
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from kudong import *
from .console_page import refresh_log_table
from kudong.ai_client import (
    AiClientError,
    TranslateCancelled,
    ensure_translate_ready,
    korean_output_path,
    translate_subtitle_file,
)
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
BUTTON_TRANSLATING_STYLE = (
    'QPushButton { background-color: rgb(214, 132, 36); color: rgb(255, 246, 230);'
    ' font-size: 20px; font-family: "Malgun Gothic"; outline: none;'
    " border: 2px solid rgb(214, 132, 36); border-radius: 5px; }"
    "QPushButton:hover { background-color: rgb(196, 78, 52); border: 2px solid rgb(214, 92, 64); }"
    "QPushButton:pressed { background-color: rgb(160, 60, 40); border: 2px solid rgb(160, 60, 40); }"
    "QPushButton:disabled { background-color: rgb(214, 132, 36); color: rgb(255, 246, 230);"
    " border: 2px solid rgb(214, 132, 36); }"
)
CANCELLED = "__cancelled__"
CANCEL_TIP = "번역 중입니다. 클릭하면 번역을 취소합니다."
AI_OUTPUT_FOLDER = "AI 자막"
COMPACT_CONTROL_STYLE = (
    'QPushButton, QComboBox { background-color: rgb(52, 59, 72); color: rgb(221, 221, 221);'
    ' font-size: 16px; font-family: "Malgun Gothic"; outline: none;'
    " border: 2px solid rgb(52, 59, 72); border-radius: 5px; padding: 0 10px; }"
    "QPushButton:hover, QComboBox:hover { background-color: rgb(57, 65, 80);"
    " border: 2px solid rgb(61, 70, 86); }"
    "QPushButton:pressed { background-color: rgb(35, 40, 49); border: 2px solid rgb(43, 50, 61); }"
    "QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right;"
    " width: 22px; border: none;"
    " background-image: url(:/icons/images/icons/cil-arrow-bottom.png);"
    " background-position: center; background-repeat: no-repeat; }"
    "QComboBox QAbstractItemView { background-color: rgb(33, 37, 43); color: rgb(221, 221, 221);"
    " selection-background-color: rgb(52, 59, 72); font-size: 16px;"
    ' font-family: "Malgun Gothic"; outline: none; }'
)


class _NoFocusDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        option.state = option.state & ~QStyle.State_HasFocus
        super().paint(painter, option, index)


class _InstantTooltipFilter(QObject):
    def __init__(self, page, table, parent=None):
        super().__init__(parent)
        self._page = page
        self._table = table
        self._watched = set()
        self._item_tip = None

    def watch(self, widget):
        if widget is None:
            return
        key = id(widget)
        if key in self._watched:
            return
        self._watched.add(key)
        widget.destroyed.connect(lambda *_args, k=key: self._watched.discard(k))
        widget.installEventFilter(self)
        widget.setAttribute(Qt.WA_Hover, True)
        widget.setMouseTracking(True)
        for child in widget.findChildren(QWidget):
            self.watch(child)

    def eventFilter(self, obj, event):
        kind = event.type()
        if kind == QEvent.ChildAdded:
            child = event.child()
            if isinstance(child, QWidget):
                self.watch(child)
            return False
        if not isinstance(obj, QWidget):
            return False
        if kind == QEvent.Enter:
            if obj is self._table.viewport() or obj is self._table.horizontalHeader():
                return False
            tip = obj.toolTip()
            if tip:
                QToolTip.showText(QCursor.pos(), tip, obj)
            return False
        if kind == QEvent.Leave:
            if obj is self._table.viewport() or obj is self._table.horizontalHeader():
                self._item_tip = None
            QToolTip.hideText()
            return False
        if kind == QEvent.ToolTip:
            return True
        if kind in (QEvent.HoverMove, QEvent.MouseMove):
            if obj is self._table.viewport():
                self._show_cell_tip(event, self._table.itemAt)
            elif obj is self._table.horizontalHeader():
                self._show_header_tip(event)
        return False

    def _event_pos(self, event):
        if hasattr(event, "position"):
            return event.position().toPoint()
        return event.pos()

    def _show_cell_tip(self, event, item_at):
        item = item_at(self._event_pos(event))
        tip = item.toolTip() if item is not None else ""
        if tip == self._item_tip:
            return
        self._item_tip = tip
        if tip:
            QToolTip.showText(QCursor.pos(), tip, self._table.viewport())
        else:
            QToolTip.hideText()

    def _show_header_tip(self, event):
        header = self._table.horizontalHeader()
        logical = header.logicalIndexAt(self._event_pos(event))
        item = self._table.horizontalHeaderItem(logical)
        tip = item.toolTip() if item is not None else ""
        if tip == self._item_tip:
            return
        self._item_tip = tip
        if tip:
            QToolTip.showText(QCursor.pos(), tip, header)
        else:
            QToolTip.hideText()


def _set_tooltip(widget, tip):
    widget.setToolTip(tip)
    if widget.underMouse():
        if tip:
            QToolTip.showText(QCursor.pos(), tip, widget)
        else:
            QToolTip.hideText()


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


def format_modified(value):
    text = str(value or "").strip()
    if text == "":
        return ""
    try:
        stamp = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    if stamp.tzinfo is not None:
        stamp = stamp.astimezone()
    return stamp.strftime("%Y-%m-%d %H:%M")


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
    result_ready = Signal(int, str, str, bool, str)
    status = Signal(int, str, str, str)

    def __init__(self, row, url, dest, mode, parent=None):
        super().__init__(parent)
        self.row = row
        self.url = url
        self.dest = dest
        self.mode = mode
        self.cancel_event = threading.Event()
        self.translating = False

    def cancel(self):
        self.cancel_event.set()

    def run(self):
        partial_path = self.dest + ".part"
        try:
            already = _output_ready(self.dest)
            if not (self.mode == "korean" and already):
                self._download(partial_path)

            if self.mode == "korean":
                if self.cancel_event.is_set():
                    raise TranslateCancelled()
                self.translating = True
                self.status.emit(self.row, self.url, self.mode, "번역 중")
                saved = translate_subtitle_file(
                    self.dest,
                    on_progress=lambda text: self.status.emit(self.row, self.url, self.mode, text),
                    cancel_event=self.cancel_event,
                )
                self.result_ready.emit(self.row, self.url, self.mode, True, saved)
            else:
                self.result_ready.emit(self.row, self.url, self.mode, True, self.dest)
        except TranslateCancelled:
            self.result_ready.emit(self.row, self.url, self.mode, False, CANCELLED)
        except Exception as error:
            if os.path.isfile(partial_path):
                try:
                    os.remove(partial_path)
                except OSError:
                    pass
            self.result_ready.emit(self.row, self.url, self.mode, False, str(error))

    def _download(self, partial_path):
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


def _output_ready(path):
    if os.path.isdir(path):
        try:
            return any(os.scandir(path))
        except OSError:
            return False
    try:
        return os.path.isfile(path) and os.path.getsize(path) > 0
    except OSError:
        return False


# AI 자막 페이지
# ///////////////////////////////////////////////////////////////
class AiPage(QObject):
    def __init__(self, MainWindow, widgets):
        super().__init__()
        self.MainWindow = MainWindow
        self.widgets = widgets
        self.workers = []
        self.active_workers = {}
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
            + "QTableWidget { outline: 0; padding: 0px; margin: 0px; border: none; }"
            + "QTableWidget::item:focus { outline: none; border: none; }"
        )
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setFocusPolicy(Qt.NoFocus)
        table.verticalHeader().setDefaultSectionSize(68)
        table.horizontalHeader().setVisible(True)
        table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self._tooltip_filter = _InstantTooltipFilter(self.widgets.ai_page, table, self)
        self._tooltip_filter.watch(self.widgets.ai_page)

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
        layout.setContentsMargins(9, 0, 9, 10)
        layout.setSpacing(8)

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

        layout.addWidget(self.ai_search_input, 1)
        layout.addWidget(self.ai_search_button)
        self.widgets.verticalLayout_29.insertWidget(1, search_row)

        action_row = QFrame(self.widgets.ai_page)
        action_row.setObjectName("ai_action_row")
        action_row.setFrameShape(QFrame.NoFrame)
        action_row.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(12, 0, 9, 0)
        action_layout.setSpacing(8)

        self.ai_selection_label = QLabel("0개 선택", action_row)
        self.ai_selection_label.setObjectName("ai_selection_label")
        self.ai_selection_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ai_selection_label.setStyleSheet(
            'color: rgb(180, 186, 196); font-size: 16px; font-family: "Malgun Gothic";'
            " background: transparent;"
        )

        self.ai_download_mode = QComboBox(action_row)
        self.ai_download_mode.setObjectName("ai_download_mode")
        self.ai_download_mode.setCursor(Qt.PointingHandCursor)
        self.ai_download_mode.setFocusPolicy(Qt.NoFocus)
        self.ai_download_mode.setFixedSize(QSize(118, 40))
        self.ai_download_mode.setStyleSheet(COMPACT_CONTROL_STYLE)
        self.ai_download_mode.addItem("한국어", "korean")
        self.ai_download_mode.addItem("일본어", "original")        
        _set_tooltip(
            self.ai_download_mode,
            "받을 자막 종류입니다. 일본어는 원본 파일만 받고, 한국어는 일본어를 번역해 저장합니다.",
        )
        self.ai_download_mode.currentIndexChanged.connect(self._on_download_mode_changed)

        self.ai_download_all_button = QPushButton("일괄 다운로드", action_row)
        self.ai_download_all_button.setObjectName("ai_download_all_button")
        self.ai_download_all_button.setCursor(Qt.PointingHandCursor)
        self.ai_download_all_button.setFocusPolicy(Qt.NoFocus)
        self.ai_download_all_button.setFixedSize(QSize(148, 40))
        self.ai_download_all_button.setStyleSheet(COMPACT_CONTROL_STYLE)
        self.ai_download_all_button.clicked.connect(self.on_download_all_clicked)
        self._update_bulk_tooltip()

        action_layout.addWidget(self.ai_download_mode, 0, Qt.AlignVCenter)
        action_layout.addWidget(self.ai_selection_label, 1)
        action_layout.addWidget(self.ai_download_all_button, 0, Qt.AlignVCenter)
        self.widgets.verticalLayout_29.setSpacing(0)
        self.widgets.ai_row_2.setFrameShape(QFrame.NoFrame)
        self.widgets.horizontalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.widgets.verticalLayout_29.insertWidget(2, action_row)

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
        header.resizeSection(3, 148)
        header_item = table.horizontalHeaderItem(0)
        if header_item is not None:
            header_item.setToolTip("클릭하면 전체를 선택하거나 해제합니다.")

        self._set_count_text(str(len(files)) + "개 파일")
        self._update_selection_count()

        for row, entry in enumerate(files):
            name = str(entry.get("name") or "")
            url = str(entry.get("url") or "")
            modified = str(entry.get("last_modified") or "")

            name_item = QTableWidgetItem(name)
            name_item.setData(URL_ROLE, url)
            name_item.setData(NAME_ROLE, name)
            name_item.setToolTip(format_modified(modified))
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)

            size_item = QTableWidgetItem(format_size(entry.get("size")))
            size_item.setTextAlignment(Qt.AlignCenter)
            size_item.setFlags(size_item.flags() & ~Qt.ItemIsEditable)

            table.setCellWidget(row, 0, self._make_checkbox())
            table.setItem(row, 1, name_item)
            table.setItem(row, 2, size_item)

            table.setCellWidget(row, 3, self._make_action_button(row, name, url))

    def _style_action_button(self, button, done=False, translating=False):
        button.setCursor(Qt.PointingHandCursor)
        button.setFocusPolicy(Qt.NoFocus)
        button.setMinimumHeight(48)
        if translating:
            style = BUTTON_TRANSLATING_STYLE
        elif done:
            style = BUTTON_DONE_STYLE
        else:
            style = DOWNLOAD_BUTTON_STYLE
        button.setStyleSheet(style)

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
        box.stateChanged.connect(self._update_selection_count)
        layout.addWidget(box)
        return wrap

    def _update_selection_count(self, state=0):
        table = self.widgets.ai_subtitle_table
        selected = 0
        for row in range(table.rowCount()):
            box = self._checkbox_at(row)
            if box is not None and box.isChecked():
                selected += 1
        self.ai_selection_label.setText(str(selected) + "개 선택")

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

    def _dest_for(self, name, url):
        base = get_global_outpath() or os.path.join(os.path.abspath("."), "downloads")
        return os.path.join(base, AI_OUTPUT_FOLDER, safe_filename(name, url))

    def _download_mode(self):
        mode = self.ai_download_mode.currentData()
        if mode in ("original", "korean"):
            return mode
        return "original"

    def _mode_text(self, mode):
        if mode == "korean":
            return "일본어 원문을 한국어로 번역해 저장합니다. 이미 받은 원본이 있으면 번역만 진행합니다."
        return "원본 자막 파일을 다운로드합니다."

    def _update_bulk_tooltip(self):
        _set_tooltip(self.ai_download_all_button, self._mode_text(self._download_mode()))

    def _on_download_mode_changed(self, index=0):
        self._update_bulk_tooltip()
        table = self.widgets.ai_subtitle_table
        for row in range(table.rowCount()):
            button = self._row_button(row)
            if isinstance(button, QPushButton) and not button.isEnabled():
                continue
            if self._row_worker(row) is not None:
                continue
            self._refresh_action_button(row)

    def _make_action_button(self, row, name, url):
        button = QPushButton("다운로드")
        button.setObjectName("ai_download_button")
        button.clicked.connect(partial(self.on_row_button_clicked, row))
        self._apply_action_button(button, name, url)
        if url in self.active_workers:
            self._set_row_busy(row, "번역 중" if self.active_workers[url].translating else "받는 중")
        return button

    def _row_worker(self, row):
        item = self.widgets.ai_subtitle_table.item(row, 1)
        if item is None:
            return None
        return self.active_workers.get(item.data(URL_ROLE))

    def on_row_button_clicked(self, row, checked=False):
        worker = self._row_worker(row)
        if worker is None:
            self.on_download_clicked(row)
            return
        if worker.mode != "korean" or not worker.translating or worker.cancel_event.is_set():
            return
        worker.cancel()
        button = self._row_button(row)
        if isinstance(button, QPushButton):
            button.setEnabled(False)
            button.setText("취소 중")
            _set_tooltip(button, "번역을 취소하고 있습니다.")

    def _row_button(self, row):
        widget = self.widgets.ai_subtitle_table.cellWidget(row, 3)
        if isinstance(widget, QPushButton):
            return widget
        if widget is None:
            return None
        button = widget.findChild(QPushButton, "ai_download_button")
        if isinstance(button, QPushButton):
            return button
        return None

    def _saved_path(self, name, url, mode):
        dest = self._dest_for(name, url)
        if mode == "korean":
            return korean_output_path(dest)
        return dest

    def _apply_action_button(self, button, name, url, saved_path=""):
        mode = self._download_mode()
        path = self._saved_path(name, url, mode)
        ready = _output_ready(path)
        button.setEnabled(True)
        button.setText("완료" if ready else "다운로드")
        tip = self._mode_text(mode)
        if ready:
            tip = "클릭하면 저장 폴더를 엽니다."
        _set_tooltip(button, tip)
        self._style_action_button(button, done=ready)

    def _set_row_busy(self, row, text):
        button = self._row_button(row)
        if not isinstance(button, QPushButton):
            return
        translating = str(text).startswith("번역")
        button.setEnabled(translating)
        button.setText(text)
        if translating:
            _set_tooltip(button, CANCEL_TIP)
        self._style_action_button(button, translating=translating)

    def _refresh_action_button(self, row, saved_path=""):
        item = self.widgets.ai_subtitle_table.item(row, 1)
        button = self._row_button(row)
        if item is None or not isinstance(button, QPushButton):
            return
        name = item.data(NAME_ROLE) or item.text()
        url = item.data(URL_ROLE)
        self._apply_action_button(button, name, url, saved_path)

    def _ensure_korean_ready(self):
        try:
            ensure_translate_ready()
        except AiClientError as error:
            QMessageBox.warning(self.MainWindow, "SMI-DOWNLOADER", str(error))
            return False
        return True

    def on_download_all_clicked(self, checked=False):
        table = self.widgets.ai_subtitle_table
        rows = []
        for row in range(table.rowCount()):
            box = self._checkbox_at(row)
            if box is not None and box.isChecked():
                rows.append(row)
        if not rows:
            QMessageBox.information(self.MainWindow, "SMI-DOWNLOADER", "다운로드할 파일을 선택해주세요.")
            return
        pending = [row for row in rows if not self._row_output_ready(row)]
        if not pending:
            QMessageBox.information(self.MainWindow, "SMI-DOWNLOADER", "선택한 파일은 이미 받아 두었습니다.")
            return
        if self._download_mode() == "korean" and not self._ensure_korean_ready():
            return
        for row in pending:
            self.on_download_clicked(row, ready=True)

    def on_download_clicked(self, row, checked=False, ready=False):
        table = self.widgets.ai_subtitle_table
        item = table.item(row, 1)
        button = self._row_button(row)
        if item is None or not isinstance(button, QPushButton) or not button.isEnabled():
            return

        url = item.data(URL_ROLE)
        name = item.data(NAME_ROLE) or item.text()
        if not url:
            QMessageBox.warning(self.MainWindow, "SMI-DOWNLOADER", "다운로드 주소가 없습니다.")
            return
        if url in self.active_workers:
            return
        mode = self._download_mode()
        saved = self._saved_path(name, url, mode)
        if _output_ready(saved):
            self._open_saved_folder(saved)
            return
        if mode == "korean" and not ready and not self._ensure_korean_ready():
            return

        dest = self._dest_for(name, url)
        skip_download = mode == "korean" and _output_ready(dest)
        self._set_row_busy(row, "번역 중" if skip_download else "받는 중")

        worker = AiDownloadWorker(row, url, dest, mode, self)
        worker.translating = skip_download
        worker.result_ready.connect(self.on_download_finished)
        worker.status.connect(self.on_download_status)
        worker.finished.connect(self._drop_worker)
        self.workers.append(worker)
        self.active_workers[url] = worker
        worker.start()

    def _row_for_url(self, url):
        table = self.widgets.ai_subtitle_table
        for row in range(table.rowCount()):
            item = table.item(row, 1)
            if item is not None and item.data(URL_ROLE) == url:
                return row
        return -1

    def _show_translate_log(self):
        self.widgets.log_console.setPlainText(get_global_console_output())
        bar = self.widgets.log_console.verticalScrollBar()
        bar.setValue(bar.maximum())

    def on_download_status(self, row, url, mode, text):
        if mode == "korean":
            self._show_translate_log()
        worker = self.active_workers.get(url)
        if worker is not None:
            if worker.cancel_event.is_set():
                return
            if str(text).startswith("번역"):
                worker.translating = True
        found = self._row_for_url(url)
        if found < 0:
            return
        self._set_row_busy(found, text)

    def on_download_finished(self, row, url, mode, ok, message):
        if mode == "korean":
            self._show_translate_log()
            refresh_log_table(self.widgets.log_timestamp)
        found = self._row_for_url(url)
        if found >= 0:
            saved = message if ok and mode == "korean" and self._download_mode() == "korean" else ""
            self._refresh_action_button(found, saved)

        if ok or message == CANCELLED:
            return

        detail = message if len(message) <= 800 else message[:800] + "..."
        if mode == "korean":
            text = "한국어 자막을 만들지 못했습니다.\n" + detail
        else:
            text = "자막 파일을 받지 못했습니다.\n" + detail
        QMessageBox.warning(self.MainWindow, "SMI-DOWNLOADER", text)

    def _row_output_ready(self, row):
        item = self.widgets.ai_subtitle_table.item(row, 1)
        if item is None:
            return False
        name = item.data(NAME_ROLE) or item.text()
        url = item.data(URL_ROLE)
        if not url:
            return False
        return _output_ready(self._saved_path(name, url, self._download_mode()))

    def _open_saved_folder(self, path):
        if os.path.isdir(path):
            folder = path
        else:
            folder = os.path.dirname(path)
        if not os.path.isdir(folder):
            QMessageBox.warning(self.MainWindow, "SMI-DOWNLOADER", "저장 폴더를 찾지 못했습니다.")
            return
        system = platform.system()
        if system == "Windows":
            os.startfile(folder)
        elif system == "Darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def _drop_worker(self):
        worker = self.sender()
        if worker in self.workers:
            self.workers.remove(worker)
        url = getattr(worker, "url", None)
        if url is not None and self.active_workers.get(url) is worker:
            self.active_workers.pop(url, None)
