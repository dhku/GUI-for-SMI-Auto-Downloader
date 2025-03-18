import webbrowser

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

# URL을 여는 함수
def open_url(url):
    webbrowser.open(url)

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