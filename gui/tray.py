import platform

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from kudong import *

# Tray
# ///////////////////////////////////////////////////////////////
class Tray:
    def __init__(self, MainWindow, widgets):
        self.MainWindow = MainWindow
        self.widgets = widgets  

        # 트레이 설정
        self.MainWindow.setWindowIcon(QIcon("icon.ico"))

        self.MainWindow.tray_icon = QSystemTrayIcon(self.MainWindow)
        self.MainWindow.tray_icon.setIcon(QIcon("icon.ico"))
        tray_menu = QMenu(self.MainWindow)

        restore_action = QAction("열기", self.MainWindow)
        restore_action.triggered.connect(self.MainWindow.showNormal)
        tray_menu.addAction(restore_action)

        quit_action = QAction("종료", self.MainWindow)
        quit_action.triggered.connect(self.closeApp)
        tray_menu.addAction(quit_action)

        self.MainWindow.tray_icon.setContextMenu(tray_menu)
        self.MainWindow.tray_icon.show()

        # 커스텀 타이틀바의 닫기 버튼 연결 (Windows)
        # 초기화 시점(show 전)에는 isVisible()이 False일 수 있어 조건 없이 연결
        self.widgets.closeAppBtn.clicked.connect(self.minimize_to_tray)

        # macOS/Linux: 네이티브 닫기 버튼 클릭 시 트레이로 최소화
        self.MainWindow._tray = self
        self.MainWindow.closeEvent = self._close_event

        self.MainWindow.tray_icon.activated.connect(self.on_tray_icon_activated) 

        if platform.system() == 'Darwin':
            self._event_filter = self._DockClickEventFilter(self.MainWindow)
            QApplication.instance().installEventFilter(self._event_filter)

    class _DockClickEventFilter(QObject):
        def __init__(self, window):
            super().__init__()
            self._window = window

        def eventFilter(self, obj, event):
            if event.type() == QEvent.ApplicationActivate:
                self._window.show()
                self._window.raise_()
                self._window.activateWindow()
            return False

    def _close_event(self, event):
        event.ignore()
        self.minimize_to_tray()

    def minimize_to_tray(self):
        self.MainWindow.hide()
        self.MainWindow.tray_icon.showMessage(
            "SMI-AUTO-DOWNLOADER",
            "해당 어플리케이션은 시스템 트레이에 최소화 되었습니다.",
            QIcon("icon.ico"),
            2000
        )
        
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.MainWindow.isMinimized():
                self.MainWindow.showNormal()
            else:
                self.MainWindow.show()
            self.MainWindow.raise_()
            self.MainWindow.activateWindow()

    def closeApp(self):
        set_global_quitSignal(True)
        QApplication.instance().quit()