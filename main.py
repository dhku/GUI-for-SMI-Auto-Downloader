# ///////////////////////////////////////////////////////////////
#
# BY: KUDONG
# PROJECT: GUI-FOR-SMI-AUTO-DOWNLOADER
# Version: 1.5.3
#
# ///////////////////////////////////////////////////////////////

import sys
import os
import webbrowser
import time
import ctypes

from modules import *
from widgets import *
from kudong import *
from gui import *

os.environ["QT_FONT_DPI"] = "96" # HiDPI 기본값 100%
widgets = None

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # 위젯 전역 설정
        # ///////////////////////////////////////////////////////////////
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        global widgets
        widgets = self.ui

        # 커스텀 제목 사용 | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # 타이틀 이름
        # ///////////////////////////////////////////////////////////////
        title = "SMI-AUTO-DOWNLOADER"
        description = "SMI-AUTO-DOWNLOADER - Automation of Subtitle Download for Anime Fans"
        self.setWindowTitle(title)
        widgets.titleRightInfo.setText(description)

        # 상단 셋팅 숨기기
        widgets.settingsTopBtn.hide()

        # 토글 메뉴
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # 내부 UI 셋팅
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # 트레이
        self.tray = Tray(self,widgets)
        # 다운로드 관리 페이지
        self.download_page = DownloadPage(self,widgets)
        # 좌측 토글 바
        self.left_toggle_bar = LeftToggleBar(self,widgets)
        # 편성표 페이지
        self.anime_schedule_page = SchedulePage(self,widgets)
        # 콘솔 로그 페이지
        self.console_page = ConsolePage(self,widgets)
        # 검색 페이지
        self.search_page = SearchPage(self,widgets)
        # 최근 자막 페이지
        self.recent_page = RecentPage(self,widgets)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # 좌측 메뉴 아이콘
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_download.clicked.connect(self.buttonClick)
        widgets.btn_log.clicked.connect(self.buttonClick)
        widgets.btn_exit.clicked.connect(self.buttonClick)
        widgets.btn_search.clicked.connect(self.buttonClick)
        widgets.btn_update.clicked.connect(self.buttonClick)

        # 좌측 사이드 바
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)

        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # 우측 바
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)

        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # 투명도 설정
        def onChangeValueOpacity(self):
            value = widgets.horizontalSlider_2.value()
            window.setWindowOpacity(value/100.0)

        widgets.horizontalSlider_2.setRange(10, 100)
        widgets.horizontalSlider_2.setValue(100)
        widgets.horizontalSlider_2.valueChanged.connect(onChangeValueOpacity)

        # 맨 앞으로 창 열기
        # ///////////////////////////////////////////////////////////////
        self.show()
        self.raise_()
        self.activateWindow()

        # 테마 설정
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = False
        themeFile = "themes\py_dracula_light.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.anime_schedule)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))


    # BUTTONS CLICK
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        global currentPage
        btn = self.sender()
        btnName = btn.objectName()

        # 편성표 이동 버튼
        if btnName == "btn_home":
            common.currentPage = "home"
            widgets.stackedWidget.setCurrentWidget(widgets.anime_schedule)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # 다운로드 관리 이동 버튼
        if btnName == "btn_download":
            common.currentPage = "download"
            widgets.stackedWidget.setCurrentWidget(widgets.download_page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # 로그 페이지 이동 버튼
        if btnName == "btn_log":
            common.currentPage = "log"
            widgets.stackedWidget.setCurrentWidget(widgets.log_page) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU

        # 검색 페이지 이동 버튼
        if btnName == "btn_search":
            common.currentPage = "search"
            widgets.stackedWidget.setCurrentWidget(widgets.search_page)
            self.search_page.async_update_search_keyword_task()
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # 최근 자막 페이지 이동 버튼
        if btnName == "btn_update":
            common.currentPage = "update"
            widgets.stackedWidget.setCurrentWidget(widgets.recent_page)
            self.recent_page.async_update_recent_task()
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        if btnName == "btn_exit":
            webbrowser.open("https://github.com/dhku/GUI-for-SMI-Auto-Downloader")

        # 버튼 디버깅
        # print(btn.styleSheet())
        # print(f'Button "{btnName}" pressed!')

    # 리사이징 이벤트
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # 마우스 클릭 이벤트
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        # if event.buttons() == Qt.LeftButton:
        #     print('Mouse click: LEFT CLICK')
        # if event.buttons() == Qt.RightButton:
        #     print('Mouse click: RIGHT CLICK')

    def openLeftBox(self):
        UIFunctions.openLeftBox(self, True)

# 윈도우 DPI를 계산합니다.
def get_windows_dpi():
    try:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        dpi = user32.GetDpiForSystem()
        return dpi
    except Exception as e:
        print("error :", e)
        return None
    
# 진입점
if __name__ == "__main__":

    autoDPI = False

    # 콘솔 로깅
    console_logger_init() # 배포시 활성화

    # HIDPI 값 불러오기
    with open('settings.yml', encoding='UTF8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        autoDPI = config['auto-dpi']
        # print("auto-dpi = "+ str(autoDPI))
        os.environ["QT_FONT_DPI"] = str(config['dpi'])

    start = time.time()

    if(autoDPI is True):
        dpi = get_windows_dpi()
        if dpi is not None:
            # print("DPI = "+ str(dpi) +" / SCALE_FACTOR = " + str((dpi / 96.0) * 100))
            os.environ["QT_FONT_DPI"] = str(dpi)
    # else:
    #     print("DPI = "+ os.environ["QT_FONT_DPI"])
        
    # UI 인스턴스화
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("WindowsVista"));

    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()

    end = time.time()
    # print(f"{end - start:.5f} sec")

    sys.exit(app.exec_())
