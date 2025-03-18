
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
        self.MainWindow.tray_icon.setIcon(QIcon("icon.ico"))  # 트레이 아이콘으로 사용할 이미지 파일의 경로
        tray_menu = QMenu(self.MainWindow)

        restore_action = QAction("열기", self.MainWindow)
        restore_action.triggered.connect(self.MainWindow.showNormal)
        tray_menu.addAction(restore_action)

        quit_action = QAction("종료", self.MainWindow)
        quit_action.triggered.connect(self.closeApp)
        tray_menu.addAction(quit_action)

        self.MainWindow.tray_icon.setContextMenu(tray_menu)
        self.MainWindow.tray_icon.show()


        self.widgets.closeAppBtn.clicked.connect(self.minimize_to_tray)
        self.MainWindow.tray_icon.activated.connect(self.on_tray_icon_activated) 

    # 어플리케이션 종료시
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
            self.MainWindow.showNormal()

    def closeApp(self):
        set_global_quitSignal(True)
        QApplication.instance().quit()