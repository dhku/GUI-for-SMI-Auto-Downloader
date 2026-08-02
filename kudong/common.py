import webbrowser
import html

from datetime import datetime
from functools import partial

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# gui 모듈에서 사용하는 공통 전역변수
# 다른 모듈에서 common.<전역변수>로 사용
isScheduler_mode = False; # 일반 OR 주기적으로 다운로드인지 체크
toggleBar_instance = None; # 진행도 스레드에서 사용
downloadPage_instance = None; # left_toggle_bar에서 Yml save 참조용
selectedAnime_LeftBox = None; # 선택한 애니메이션 객체
download_thread = None;
smiWorker = None; # 진행도 콜백에서 사용
currentPage = None;

# URL을 여는 함수
def open_url(url):
    webbrowser.open(url)

WEEK_KO = ["일", "월", "화", "수", "목", "금", "토"]

# modules 패키지가 main을 참조하므로 순환 참조를 피하기 위해 호출 시점에 import
def _fs(win_size, mac_size):
    from modules.font_config import fs
    return fs(win_size, mac_size)

def _parse_date(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except Exception:
        return None

def _format_air_time(value):
    time_obj = datetime.strptime(value, "%H:%M") # 2025-99-99 가 넘어오면 예외처리
    return time_obj.strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")

# 특별편/신작처럼 요일이 없는 경우에는 방영 주기를 표시하지 않음
def _weekly_line(week_Ko, time_value):
    if week_Ko is None:
        return None
    return "매주 (" + week_Ko + ") " + _format_air_time(time_value)

# 좌측 박스 날짜 라벨 HTML (line2가 있으면 두 줄)
def _date_html(line1, line2 = None):
    size = str(_fs(16, 24))
    if line2 is None:
        return ("<html><head/><body><p align='center'><span style=' font-size:" + size +
                "pt; '>" + line1 + "</span></p></body></html>")
    return ("<html><head/><body><p align='center' style='line-height:0.6;'><span style=' font-size:" + size +
            "pt; '>" + line1 + "</span></p><p align='center'><span style=' font-size:" + size +
            "pt;'>" + line2 + "</span></p></body></html>")

# 자막 갱신 시각을 ' (N분 전)' 형태로 변환
def format_sub_time_diff(updDtStr):
    updDt = datetime.strptime(updDtStr, "%Y-%m-%dT%H:%M:%S")
    total_sec = (datetime.now() - updDt).total_seconds()

    if total_sec < 60: # 60초 이내
        return " (" + str(round(total_sec)) + "초 전)"
    elif total_sec < 3600: # 60분 이내
        return " (" + str(round(total_sec/60)) + "분 전)"
    elif total_sec < 86400: # 24시간 이내
        return " (" + str(round(total_sec/3600)) + "시간 전)"
    elif total_sec < 2592000: # 30일 이내
        return " (" + str(round(total_sec/86400)) + "일 전)"
    return " (" + updDtStr[:updDtStr.rfind("T")] + ")"

# 좌측 박스 제목 라벨
def render_anime_title(widgets, anime):
    escaped_text = html.escape(anime.subject) # HTML 이스케이프 처리 <> 대응
    widgets.label.setText("<html><head/><body><p align='center'><span style=' font-size:" +
                          str(_fs(20, 34)) + "pt; font-weight:bold;'>" + escaped_text +
                          "</span></p></body></html>");
    widgets.label.setWordWrap(True)

# 좌측 박스 방영일자 라벨
def render_anime_date(widgets, anime):
    label = widgets.label_date

    def show(text):
        label.setText(text)
        label.setWordWrap(True)
        label.show()

    if anime.startDate == '':
        label.hide()
        return

    currentDate = datetime.now();
    startDate = _parse_date(anime.startDate)
    endDate = _parse_date(anime.endDate)
    week_Ko = WEEK_KO[anime.weekNo] if isinstance(anime.weekNo, int) and 0 <= anime.weekNo <= 6 else None

    # print("week_Ko: " + str(week_Ko))
    # print("anime.time: " + str(anime.time))
    # print("anime.startDate: " + str(anime.startDate))
    # print("anime.endDate: " + str(anime.endDate))
    # print("anime.status: " + str(anime.status))
    # print("anime.weekNo: " + str(anime.weekNo))
    # print("anime.subject: " + str(anime.subject))
    # print("anime.time: " + str(anime.time))
    # print("anime.startDate: " + str(anime.startDate))
    # print("anime.endDate: " + str(anime.endDate))

    if anime.status == 'ON':
        if startDate is not None and currentDate <= startDate:
            show(_date_html(startDate.strftime("%Y. %m. %d")))
        elif endDate is not None:
            if startDate == endDate:
                show(_date_html(startDate.strftime("%Y. %m. %d")))
            else:
                show(_date_html(startDate.strftime("%Y. %m. %d") + " ~ " + endDate.strftime("%Y. %m. %d"),
                                _weekly_line(week_Ko, anime.time)))
        else:
            try:
                if week_Ko is None:
                    show(_date_html(startDate.strftime("%Y. %m. %d")))
                else:
                    show(_date_html(startDate.strftime("%Y. %m. %d") + " ~ 방영중",
                                    _weekly_line(week_Ko, anime.time)))
            except Exception as e:
                label.hide()
    elif anime.status == 'END':
        try:
            if endDate is None:
                show(_date_html(startDate.strftime("%Y. %m. %d"), "완결"))
            else:
                show(_date_html(startDate.strftime("%Y. %m. %d") + " ~ " + endDate.strftime("%Y. %m. %d"), "완결"))
        except Exception as e:
            label.hide()
    else:
        show(_date_html(startDate.strftime("%Y. %m. %d ~ 방영중"), "결방"))

# 좌측 박스 자막 목록 버튼
def render_subs_buttons(widgets, subs):
    layout = widgets.extraCenter.layout()

    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    for k in subs:
        updDtStr = k.updDt

        if(k.website == ""):
            button = QPushButton("준비중 " + k.name + " " + updDtStr[:updDtStr.rfind("T")])
        else:
            button = QPushButton(k.episode + "화 " + k.name + format_sub_time_diff(updDtStr))
            button.clicked.connect(partial(open_url, k.website))

        button.setMinimumSize(0, 60)
        button.setStyleSheet("font-size: " + str(_fs(20, 20)) + "px; color: rgb(0, 0, 0);")
        layout.addWidget(button)

    layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
    widgets.extraCenter.setLayout(layout);

# 테이블에서 선택한 애니메이션을 좌측 박스에 표시
def show_anime_detail(page, anime, subs):
    global selectedAnime_LeftBox
    selectedAnime_LeftBox = anime

    render_anime_title(page.widgets, anime)
    render_anime_date(page.widgets, anime)
    render_subs_buttons(page.widgets, subs)

    #UIFunctions.openLeftBox(self, True) 이 로직은 상호 참조 이슈로 main에서 호출하는것으로 대체
    page.MainWindow.openLeftBox() # 대신 이거 사용

# 다운로드 진행도 콜백 함수
def progress_callback(progress, count, output = "None",isFinished = False):
    global smiWorker
    if smiWorker is not None:
        smiWorker.wait()
    smiWorker = WorkerThread()
    smiWorker.setValue(progress,count,output,isFinished)
    smiWorker.start()

# 진행도를 반영하는 스레드
class WorkerThread(QThread):
    def __init__(self):
        super().__init__()
        self.toggleBar_instance = toggleBar_instance

    def setValue(self,progress,count,output,isFinished):
        self.progress = progress
        self.count = count
        self.output = output
        self.isFinished = isFinished

    def run(self):
        QMetaObject.invokeMethod(self.toggleBar_instance, "updateProgressBar", Qt.QueuedConnection,Q_ARG(int,self.progress),Q_ARG(int,self.count),Q_ARG(str,self.output),Q_ARG(bool,self.isFinished))