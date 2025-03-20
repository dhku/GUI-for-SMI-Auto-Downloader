# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainopYNhU.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QCheckBox,
    QComboBox, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QMainWindow,
    QPlainTextEdit, QProgressBar, QPushButton, QScrollArea,
    QSizePolicy, QSlider, QSpacerItem, QStackedWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)
from . resources_rc import *

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1529, 741)
        MainWindow.setMinimumSize(QSize(940, 560))
        self.styleSheet = QWidget(MainWindow)
        self.styleSheet.setObjectName(u"styleSheet")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        self.styleSheet.setFont(font)
        self.styleSheet.setStyleSheet(u"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"\n"
"SET APP STYLESHEET - FULL STYLES HERE\n"
"DARK THEME - DRACULA COLOR BASED\n"
"\n"
"///////////////////////////////////////////////////////////////////////////////////////////////// */\n"
"\n"
"QWidget{\n"
"	color: rgb(221, 221, 221);\n"
"	font: 10pt \"Segoe UI\";\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"Tooltip */\n"
"QToolTip {\n"
"	color: #ffffff;\n"
"	background-color: rgba(33, 37, 43, 180);\n"
"	border: 1px solid rgb(44, 49, 58);\n"
"	background-image: none;\n"
"	background-position: left center;\n"
"    background-repeat: no-repeat;\n"
"	border: none;\n"
"	border-left: 2px solid rgb(255, 121, 198);\n"
"	text-align: left;\n"
"	padding-left: 8px;\n"
"	margin: 0px;\n"
"}\n"
"\n"
"#extraTopMenu #label {\n"
"    font-family: \"Malgun Gothic\";\n"
"}\n"
"\n"
"#pushButton_week .QPushButton {\n"
" 	font-family: \"Malgun Gothic"
                        "\";\n"
"}\n"
"\n"
"#anime_time_table {\n"
" 	font-family: \"Malgun Gothic\";\n"
"}\n"
"\n"
"#anime_search_table {\n"
" 	font-family: \"Malgun Gothic\";\n"
"}\n"
"\n"
"#anime_recent_table {\n"
" 	font-family: \"Malgun Gothic\";\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"Bg App */\n"
"#bgApp {	\n"
"	background-color: rgb(40, 44, 52);\n"
"	border: 1px solid rgb(44, 49, 58);\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"Left Menu */\n"
"#leftMenuBg {	\n"
"	background-color: rgb(33, 37, 43);\n"
"}\n"
"#topLogo {\n"
"	background-color: rgb(33, 37, 43);\n"
"	/*background-image: url(:/images/images/images/logo.png);*/\n"
"	border-image: url(:/images/images/images/logo.png) ;\n"
"	background-position: center center;\n"
"	background-repeat: no-repeat;\n"
"}\n"
"#titleLeftApp { font: 63 12pt \"Segoe UI Semibold\"; }\n"
"#titleLeftDescription { font: 8pt \"Segoe UI\"; color"
                        ": rgb(189, 147, 249); }\n"
"\n"
"/* MENUS */\n"
"#topMenu .QPushButton {	\n"
"	background-position: left center;\n"
"    background-repeat: no-repeat;\n"
"	border: none;\n"
"	border-left: 22px solid transparent;\n"
"	background-color: transparent;\n"
"	text-align: left;\n"
"	padding-left: 44px;\n"
"}\n"
"#topMenu .QPushButton:hover {\n"
"	background-color: rgb(40, 44, 52);\n"
"}\n"
"#topMenu .QPushButton:pressed {	\n"
"	background-color: rgb(189, 147, 249);\n"
"	color: rgb(255, 255, 255);\n"
"}\n"
"#bottomMenu .QPushButton {	\n"
"	background-position: left center;\n"
"    background-repeat: no-repeat;\n"
"	border: none;\n"
"	border-left: 20px solid transparent;\n"
"	background-color:transparent;\n"
"	text-align: left;\n"
"	padding-left: 44px;\n"
"}\n"
"#bottomMenu .QPushButton:hover {\n"
"	background-color: rgb(40, 44, 52);\n"
"}\n"
"#bottomMenu .QPushButton:pressed {	\n"
"	background-color: rgb(189, 147, 249);\n"
"	color: rgb(255, 255, 255);\n"
"}\n"
"#leftMenuFrame{\n"
"	border-top: 3px solid rgb(44, 49, 58)"
                        ";\n"
"}\n"
"\n"
"/* Toggle Button */\n"
"#toggleButton {\n"
"	background-position: left center;\n"
"    background-repeat: no-repeat;\n"
"	border: none;\n"
"	border-left: 20px solid transparent;\n"
"	background-color: rgb(37, 41, 48);\n"
"	text-align: left;\n"
"	padding-left: 44px;\n"
"	color: rgb(113, 126, 149);\n"
"}\n"
"#toggleButton:hover {\n"
"	background-color: rgb(40, 44, 52);\n"
"}\n"
"#toggleButton:pressed {\n"
"	background-color: rgb(189, 147, 249);\n"
"}\n"
"\n"
"/* Title Menu */\n"
"#titleRightInfo { padding-left: 10px; }\n"
"\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"Extra Tab */\n"
"#extraLeftBox {	\n"
"	background-color: rgb(44, 49, 58);\n"
"}\n"
"#extraTopBg{	\n"
"	background-color: rgb(189, 147, 249)\n"
"}\n"
"\n"
"/* Icon */\n"
"#extraIcon {\n"
"	background-position: center;\n"
"	background-repeat: no-repeat;\n"
"	background-image: url(:/icons/images/icons/icon_settings.png);\n"
"}\n"
"\n"
"/* Label */\n"
"#extraLabel { c"
                        "olor: rgb(255, 255, 255); }\n"
"\n"
"/* Btn Close */\n"
"#extraCloseColumnBtn { background-color: rgba(255, 255, 255, 0); border: none;  border-radius: 5px; }\n"
"#extraCloseColumnBtn:hover { background-color: rgb(196, 161, 249); border-style: solid; border-radius: 4px; }\n"
"#extraCloseColumnBtn:pressed { background-color: rgb(180, 141, 238); border-style: solid; border-radius: 4px; }\n"
"\n"
"/* Extra Content */\n"
"#extraContent{\n"
"	border-top: 3px solid rgb(40, 44, 52);\n"
"}\n"
"\n"
"/* Extra Top Menus */\n"
"#extraTopMenu .QPushButton {\n"
"background-position: left center;\n"
"    background-repeat: no-repeat;\n"
"	border: none;\n"
"	border-left: 22px solid transparent;\n"
"	background-color:transparent;\n"
"	text-align: left;\n"
"	padding-left: 44px;\n"
"}\n"
"#extraTopMenu .QPushButton:hover {\n"
"	background-color: rgb(40, 44, 52);\n"
"}\n"
"#extraTopMenu .QPushButton:pressed {	\n"
"	background-color: rgb(189, 147, 249);\n"
"	color: rgb(255, 255, 255);\n"
"}\n"
"\n"
"/* ////////////////////////////"
                        "/////////////////////////////////////////////////////////////////////\n"
"Content App */\n"
"#contentTopBg{	\n"
"	background-color: rgb(33, 37, 43);\n"
"}\n"
"#contentBottom{\n"
"	border-top: 3px solid rgb(44, 49, 58);\n"
"}\n"
"\n"
"/* Top Buttons */\n"
"#rightButtons .QPushButton { background-color: rgba(255, 255, 255, 0); border: none;  border-radius: 5px; }\n"
"#rightButtons .QPushButton:hover { background-color: rgb(44, 49, 57); border-style: solid; border-radius: 4px; }\n"
"#rightButtons .QPushButton:pressed { background-color: rgb(23, 26, 30); border-style: solid; border-radius: 4px; }\n"
"\n"
"/* Theme Settings */\n"
"#extraRightBox { background-color: rgb(44, 49, 58); }\n"
"#themeSettingsTopDetail { background-color: rgb(189, 147, 249); }\n"
"\n"
"/* Bottom Bar */\n"
"#bottomBar { background-color: rgb(44, 49, 58); }\n"
"#bottomBar QLabel { font-size: 11px; color: rgb(113, 126, 149); padding-left: 10px; padding-right: 10px; padding-bottom: 2px; }\n"
"\n"
"/* CONTENT SETTINGS */\n"
"/* MENUS */\n"
"#co"
                        "ntentSettings .QPushButton {	\n"
"	background-position: left center;\n"
"    background-repeat: no-repeat;\n"
"	border: none;\n"
"	border-left: 22px solid transparent;\n"
"	background-color:transparent;\n"
"	text-align: left;\n"
"	padding-left: 44px;\n"
"}\n"
"#contentSettings .QPushButton:hover {\n"
"	background-color: rgb(40, 44, 52);\n"
"}\n"
"#contentSettings .QPushButton:pressed {	\n"
"	background-color: rgb(189, 147, 249);\n"
"	color: rgb(255, 255, 255);\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"QTableWidget */\n"
"QTableWidget {	\n"
"	background-color: transparent;\n"
"	padding: 10px;\n"
"	border-radius: 5px;\n"
"	gridline-color: rgb(44, 49, 58);\n"
"	border-bottom: 1px solid rgb(44, 49, 60);\n"
"}\n"
"QTableWidget::item{\n"
"	border-color: rgb(44, 49, 60);\n"
"	padding-left: 5px;\n"
"	padding-right: 5px;\n"
"	gridline-color: rgb(44, 49, 60);\n"
"}\n"
"QTableWidget::item:selected{\n"
"	background-color: rgb(189, 147, 249);\n"
""
                        "}\n"
"QHeaderView::section{\n"
"	background-color: rgb(33, 37, 43);\n"
"	max-width: 30px;\n"
"	border: 1px solid rgb(44, 49, 58);\n"
"	border-style: none;\n"
"    border-bottom: 1px solid rgb(44, 49, 60);\n"
"    border-right: 1px solid rgb(44, 49, 60);\n"
"}\n"
"QTableWidget::horizontalHeader {	\n"
"	background-color: rgb(33, 37, 43);\n"
"}\n"
"QHeaderView::section:horizontal\n"
"{\n"
"    border: 1px solid rgb(33, 37, 43);\n"
"	background-color: rgb(33, 37, 43);\n"
"	padding: 3px;\n"
"	border-top-left-radius: 7px;\n"
"    border-top-right-radius: 7px;\n"
"}\n"
"QHeaderView::section:vertical\n"
"{\n"
"    border: 1px solid rgb(44, 49, 60);\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"LineEdit */\n"
"QLineEdit {\n"
"	background-color: rgb(33, 37, 43);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(33, 37, 43);\n"
"	padding-left: 10px;\n"
"	selection-color: rgb(255, 255, 255);\n"
"	selection-background-color: rgb(255, 121, 198);\n"
""
                        "}\n"
"QLineEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QLineEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"PlainTextEdit */\n"
"QPlainTextEdit {\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	padding: 10px;\n"
"	selection-color: rgb(255, 255, 255);\n"
"	selection-background-color: rgb(255, 121, 198);\n"
"}\n"
"QPlainTextEdit  QScrollBar:vertical {\n"
"    width: 8px;\n"
" }\n"
"QPlainTextEdit  QScrollBar:horizontal {\n"
"    height: 8px;\n"
" }\n"
"QPlainTextEdit:hover {\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QPlainTextEdit:focus {\n"
"	border: 2px solid rgb(91, 101, 124);\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"ScrollBars */\n"
"QScrollBar:horizontal {\n"
"    border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    height: 8px;\n"
"    margin: 0px 21"
                        "px 0 21px;\n"
"	border-radius: 0px;\n"
"}\n"
"QScrollBar::handle:horizontal {\n"
"    background: rgb(189, 147, 249);\n"
"    min-width: 25px;\n"
"	border-radius: 4px\n"
"}\n"
"QScrollBar::add-line:horizontal {\n"
"    border: none;\n"
"    background: rgb(55, 63, 77);\n"
"    width: 20px;\n"
"	border-top-right-radius: 4px;\n"
"    border-bottom-right-radius: 4px;\n"
"    subcontrol-position: right;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::sub-line:horizontal {\n"
"    border: none;\n"
"    background: rgb(55, 63, 77);\n"
"    width: 20px;\n"
"	border-top-left-radius: 4px;\n"
"    border-bottom-left-radius: 4px;\n"
"    subcontrol-position: left;\n"
"    subcontrol-origin: margin;\n"
"}\n"
"QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal\n"
"{\n"
"     background: none;\n"
"}\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal\n"
"{\n"
"     background: none;\n"
"}\n"
" QScrollBar:vertical {\n"
"	border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    widt"
                        "h: 8px;\n"
"    margin: 21px 0 21px 0;\n"
"	border-radius: 0px;\n"
" }\n"
" QScrollBar::handle:vertical {	\n"
"	background: rgb(189, 147, 249);\n"
"    min-height: 25px;\n"
"	border-radius: 4px\n"
" }\n"
" QScrollBar::add-line:vertical {\n"
"     border: none;\n"
"    background: rgb(55, 63, 77);\n"
"     height: 20px;\n"
"	border-bottom-left-radius: 4px;\n"
"    border-bottom-right-radius: 4px;\n"
"     subcontrol-position: bottom;\n"
"     subcontrol-origin: margin;\n"
" }\n"
" QScrollBar::sub-line:vertical {\n"
"	border: none;\n"
"    background: rgb(55, 63, 77);\n"
"     height: 20px;\n"
"	border-top-left-radius: 4px;\n"
"    border-top-right-radius: 4px;\n"
"     subcontrol-position: top;\n"
"     subcontrol-origin: margin;\n"
" }\n"
" QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {\n"
"     background: none;\n"
" }\n"
"\n"
" QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"     background: none;\n"
" }\n"
"\n"
"/* ////////////////////////////////////////////////////////"
                        "/////////////////////////////////////////\n"
"CheckBox */\n"
"QCheckBox::indicator {\n"
"    border: 3px solid rgb(52, 59, 72);\n"
"	width: 15px;\n"
"	height: 15px;\n"
"	border-radius: 10px;\n"
"    background: rgb(44, 49, 60);\n"
"}\n"
"QCheckBox::indicator:hover {\n"
"    border: 3px solid rgb(58, 66, 81);\n"
"}\n"
"QCheckBox::indicator:checked {\n"
"    background: 3px solid rgb(52, 59, 72);\n"
"	border: 3px solid rgb(52, 59, 72);	\n"
"	background-image: url(:/icons/images/icons/cil-check-alt.png);\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"RadioButton */\n"
"QRadioButton::indicator {\n"
"    border: 3px solid rgb(52, 59, 72);\n"
"	width: 15px;\n"
"	height: 15px;\n"
"	border-radius: 10px;\n"
"    background: rgb(44, 49, 60);\n"
"}\n"
"QRadioButton::indicator:hover {\n"
"    border: 3px solid rgb(58, 66, 81);\n"
"}\n"
"QRadioButton::indicator:checked {\n"
"    background: 3px solid rgb(94, 106, 130);\n"
"	border: 3px solid rgb(52, 5"
                        "9, 72);	\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"ComboBox */\n"
"QComboBox{\n"
"	background-color: rgb(27, 29, 35);\n"
"	border-radius: 5px;\n"
"	border: 2px solid rgb(33, 37, 43);\n"
"	padding: 5px;\n"
"	padding-left: 10px;\n"
"}\n"
"QComboBox:hover{\n"
"	border: 2px solid rgb(64, 71, 88);\n"
"}\n"
"QComboBox::drop-down {\n"
"	subcontrol-origin: padding;\n"
"	subcontrol-position: top right;\n"
"	width: 25px; \n"
"	border-left-width: 3px;\n"
"	border-left-color: rgba(39, 44, 54, 150);\n"
"	border-left-style: solid;\n"
"	border-top-right-radius: 3px;\n"
"	border-bottom-right-radius: 3px;	\n"
"	background-image: url(:/icons/images/icons/cil-arrow-bottom.png);\n"
"	background-position: center;\n"
"	background-repeat: no-reperat;\n"
" }\n"
"QComboBox QAbstractItemView {\n"
"	color: rgb(255, 121, 198);	\n"
"	background-color: rgb(33, 37, 43);\n"
"	padding: 10px;\n"
"	selection-background-color: rgb(39, 44, 54);\n"
"}\n"
"\n"
"/* ///////"
                        "//////////////////////////////////////////////////////////////////////////////////////////\n"
"Sliders */\n"
"QSlider::groove:horizontal {\n"
"    border-radius: 5px;\n"
"    height: 10px;\n"
"	margin: 0px;\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QSlider::groove:horizontal:hover {\n"
"	background-color: rgb(55, 62, 76);\n"
"}\n"
"QSlider::handle:horizontal {\n"
"    background-color: rgb(189, 147, 249);\n"
"    border: none;\n"
"    height: 10px;\n"
"    width: 10px;\n"
"    margin: 0px;\n"
"	border-radius: 5px;\n"
"}\n"
"QSlider::handle:horizontal:hover {\n"
"    background-color: rgb(195, 155, 255);\n"
"}\n"
"QSlider::handle:horizontal:pressed {\n"
"    background-color: rgb(255, 121, 198);\n"
"}\n"
"\n"
"QSlider::groove:vertical {\n"
"    border-radius: 5px;\n"
"    width: 10px;\n"
"    margin: 0px;\n"
"	background-color: rgb(52, 59, 72);\n"
"}\n"
"QSlider::groove:vertical:hover {\n"
"	background-color: rgb(55, 62, 76);\n"
"}\n"
"QSlider::handle:vertical {\n"
"    background-color: rgb(189, 147, 2"
                        "49);\n"
"	border: none;\n"
"    height: 10px;\n"
"    width: 10px;\n"
"    margin: 0px;\n"
"	border-radius: 5px;\n"
"}\n"
"QSlider::handle:vertical:hover {\n"
"    background-color: rgb(195, 155, 255);\n"
"}\n"
"QSlider::handle:vertical:pressed {\n"
"    background-color: rgb(255, 121, 198);\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"CommandLinkButton */\n"
"QCommandLinkButton {	\n"
"	color: rgb(255, 121, 198);\n"
"	border-radius: 5px;\n"
"	padding: 5px;\n"
"	color: rgb(255, 170, 255);\n"
"}\n"
"QCommandLinkButton:hover {	\n"
"	color: rgb(255, 170, 255);\n"
"	background-color: rgb(44, 49, 60);\n"
"}\n"
"QCommandLinkButton:pressed {	\n"
"	color: rgb(189, 147, 249);\n"
"	background-color: rgb(52, 58, 71);\n"
"}\n"
"\n"
"/* /////////////////////////////////////////////////////////////////////////////////////////////////\n"
"Button */\n"
"#pagesContainer QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	"
                        "background-color: rgb(52, 59, 72);\n"
"}\n"
"#pagesContainer QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"#pagesContainer QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}\n"
"\n"
"")
        self.verticalLayout_25 = QVBoxLayout(self.styleSheet)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.verticalLayout_25.setContentsMargins(10, 10, 10, 10)
        self.bgApp = QFrame(self.styleSheet)
        self.bgApp.setObjectName(u"bgApp")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bgApp.sizePolicy().hasHeightForWidth())
        self.bgApp.setSizePolicy(sizePolicy)
        self.bgApp.setMinimumSize(QSize(0, 0))
        self.bgApp.setStyleSheet(u"")
        self.bgApp.setFrameShape(QFrame.NoFrame)
        self.bgApp.setFrameShadow(QFrame.Raised)
        self.bgApp.setLineWidth(1)
        self.appLayout = QHBoxLayout(self.bgApp)
        self.appLayout.setSpacing(0)
        self.appLayout.setObjectName(u"appLayout")
        self.appLayout.setContentsMargins(0, 0, 0, 0)
        self.leftMenuBg = QFrame(self.bgApp)
        self.leftMenuBg.setObjectName(u"leftMenuBg")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(1)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.leftMenuBg.sizePolicy().hasHeightForWidth())
        self.leftMenuBg.setSizePolicy(sizePolicy1)
        self.leftMenuBg.setMinimumSize(QSize(60, 0))
        self.leftMenuBg.setMaximumSize(QSize(60, 16777215))
        self.leftMenuBg.setFrameShape(QFrame.NoFrame)
        self.leftMenuBg.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.leftMenuBg)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.topLogoInfo = QFrame(self.leftMenuBg)
        self.topLogoInfo.setObjectName(u"topLogoInfo")
        self.topLogoInfo.setMinimumSize(QSize(0, 50))
        self.topLogoInfo.setMaximumSize(QSize(16777215, 50))
        self.topLogoInfo.setFrameShape(QFrame.NoFrame)
        self.topLogoInfo.setFrameShadow(QFrame.Raised)
        self.topLogo = QFrame(self.topLogoInfo)
        self.topLogo.setObjectName(u"topLogo")
        self.topLogo.setGeometry(QRect(10, 5, 42, 42))
        self.topLogo.setMinimumSize(QSize(42, 42))
        self.topLogo.setMaximumSize(QSize(42, 42))
        self.topLogo.setFrameShape(QFrame.NoFrame)
        self.topLogo.setFrameShadow(QFrame.Raised)
        self.titleLeftApp = QLabel(self.topLogoInfo)
        self.titleLeftApp.setObjectName(u"titleLeftApp")
        self.titleLeftApp.setGeometry(QRect(70, 8, 160, 20))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI Semibold"])
        font1.setBold(False)
        font1.setItalic(False)
        self.titleLeftApp.setFont(font1)
        self.titleLeftApp.setStyleSheet(u"font-size: 13px;")
        self.titleLeftApp.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.titleLeftDescription = QLabel(self.topLogoInfo)
        self.titleLeftDescription.setObjectName(u"titleLeftDescription")
        self.titleLeftDescription.setGeometry(QRect(70, 27, 160, 16))
        self.titleLeftDescription.setMaximumSize(QSize(16777215, 16))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(8)
        font2.setBold(False)
        font2.setItalic(False)
        self.titleLeftDescription.setFont(font2)
        self.titleLeftDescription.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.verticalLayout_3.addWidget(self.topLogoInfo)

        self.leftMenuFrame = QFrame(self.leftMenuBg)
        self.leftMenuFrame.setObjectName(u"leftMenuFrame")
        sizePolicy.setHeightForWidth(self.leftMenuFrame.sizePolicy().hasHeightForWidth())
        self.leftMenuFrame.setSizePolicy(sizePolicy)
        self.leftMenuFrame.setMinimumSize(QSize(0, 0))
        self.leftMenuFrame.setSizeIncrement(QSize(0, 0))
        self.leftMenuFrame.setFont(font)
        self.leftMenuFrame.setFrameShape(QFrame.NoFrame)
        self.leftMenuFrame.setFrameShadow(QFrame.Raised)
        self.verticalMenuLayout = QVBoxLayout(self.leftMenuFrame)
        self.verticalMenuLayout.setSpacing(0)
        self.verticalMenuLayout.setObjectName(u"verticalMenuLayout")
        self.verticalMenuLayout.setContentsMargins(0, 0, 0, 0)
        self.toggleBox = QFrame(self.leftMenuFrame)
        self.toggleBox.setObjectName(u"toggleBox")
        self.toggleBox.setMaximumSize(QSize(16777215, 45))
        self.toggleBox.setFrameShape(QFrame.NoFrame)
        self.toggleBox.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.toggleBox)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.toggleButton = QPushButton(self.toggleBox)
        self.toggleButton.setObjectName(u"toggleButton")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.toggleButton.sizePolicy().hasHeightForWidth())
        self.toggleButton.setSizePolicy(sizePolicy2)
        self.toggleButton.setMinimumSize(QSize(0, 45))
        self.toggleButton.setFont(font)
        self.toggleButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggleButton.setLayoutDirection(Qt.LeftToRight)
        self.toggleButton.setStyleSheet(u"background-image: url(:/icons/images/icons/icon_menu.png);")

        self.verticalLayout_4.addWidget(self.toggleButton)


        self.verticalMenuLayout.addWidget(self.toggleBox)

        self.topMenu = QFrame(self.leftMenuFrame)
        self.topMenu.setObjectName(u"topMenu")
        sizePolicy.setHeightForWidth(self.topMenu.sizePolicy().hasHeightForWidth())
        self.topMenu.setSizePolicy(sizePolicy)
        self.topMenu.setMaximumSize(QSize(16777215, 16777215))
        self.topMenu.setFrameShape(QFrame.NoFrame)
        self.topMenu.setFrameShadow(QFrame.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.topMenu)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.btn_home = QPushButton(self.topMenu)
        self.btn_home.setObjectName(u"btn_home")
        sizePolicy2.setHeightForWidth(self.btn_home.sizePolicy().hasHeightForWidth())
        self.btn_home.setSizePolicy(sizePolicy2)
        self.btn_home.setMinimumSize(QSize(0, 45))
        self.btn_home.setFont(font)
        self.btn_home.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_home.setLayoutDirection(Qt.LeftToRight)
        self.btn_home.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-home.png);")

        self.verticalLayout_8.addWidget(self.btn_home)

        self.btn_download = QPushButton(self.topMenu)
        self.btn_download.setObjectName(u"btn_download")
        sizePolicy2.setHeightForWidth(self.btn_download.sizePolicy().hasHeightForWidth())
        self.btn_download.setSizePolicy(sizePolicy2)
        self.btn_download.setMinimumSize(QSize(0, 45))
        self.btn_download.setFont(font)
        self.btn_download.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_download.setLayoutDirection(Qt.LeftToRight)
        self.btn_download.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-star.png);")

        self.verticalLayout_8.addWidget(self.btn_download)

        self.btn_search = QPushButton(self.topMenu)
        self.btn_search.setObjectName(u"btn_search")
        sizePolicy2.setHeightForWidth(self.btn_search.sizePolicy().hasHeightForWidth())
        self.btn_search.setSizePolicy(sizePolicy2)
        self.btn_search.setMinimumSize(QSize(0, 45))
        self.btn_search.setFont(font)
        self.btn_search.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_search.setLayoutDirection(Qt.LeftToRight)
        self.btn_search.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-find-in-page.png);")

        self.verticalLayout_8.addWidget(self.btn_search)

        self.btn_update = QPushButton(self.topMenu)
        self.btn_update.setObjectName(u"btn_update")
        sizePolicy2.setHeightForWidth(self.btn_update.sizePolicy().hasHeightForWidth())
        self.btn_update.setSizePolicy(sizePolicy2)
        self.btn_update.setMinimumSize(QSize(0, 45))
        self.btn_update.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_update.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-history.png);")

        self.verticalLayout_8.addWidget(self.btn_update)

        self.btn_log = QPushButton(self.topMenu)
        self.btn_log.setObjectName(u"btn_log")
        sizePolicy2.setHeightForWidth(self.btn_log.sizePolicy().hasHeightForWidth())
        self.btn_log.setSizePolicy(sizePolicy2)
        self.btn_log.setMinimumSize(QSize(0, 45))
        self.btn_log.setFont(font)
        self.btn_log.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_log.setLayoutDirection(Qt.LeftToRight)
        self.btn_log.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-terminal.png);")

        self.verticalLayout_8.addWidget(self.btn_log)

        self.btn_log.raise_()
        self.btn_download.raise_()
        self.btn_home.raise_()
        self.btn_search.raise_()
        self.btn_update.raise_()

        self.verticalMenuLayout.addWidget(self.topMenu, 0, Qt.AlignTop)

        self.bottomMenu = QFrame(self.leftMenuFrame)
        self.bottomMenu.setObjectName(u"bottomMenu")
        self.bottomMenu.setFrameShape(QFrame.NoFrame)
        self.bottomMenu.setFrameShadow(QFrame.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.bottomMenu)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.btn_exit = QPushButton(self.bottomMenu)
        self.btn_exit.setObjectName(u"btn_exit")
        self.btn_exit.setMinimumSize(QSize(0, 45))
        self.btn_exit.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-external-link.png);")

        self.verticalLayout_9.addWidget(self.btn_exit)

        self.toggleLeftBox = QPushButton(self.bottomMenu)
        self.toggleLeftBox.setObjectName(u"toggleLeftBox")
        sizePolicy2.setHeightForWidth(self.toggleLeftBox.sizePolicy().hasHeightForWidth())
        self.toggleLeftBox.setSizePolicy(sizePolicy2)
        self.toggleLeftBox.setMinimumSize(QSize(0, 45))
        self.toggleLeftBox.setFont(font)
        self.toggleLeftBox.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggleLeftBox.setLayoutDirection(Qt.LeftToRight)
        self.toggleLeftBox.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-zoom-in.png);")
        self.toggleLeftBox.setIconSize(QSize(20, 20))

        self.verticalLayout_9.addWidget(self.toggleLeftBox)


        self.verticalMenuLayout.addWidget(self.bottomMenu, 0, Qt.AlignBottom)


        self.verticalLayout_3.addWidget(self.leftMenuFrame)


        self.appLayout.addWidget(self.leftMenuBg)

        self.extraLeftBox = QFrame(self.bgApp)
        self.extraLeftBox.setObjectName(u"extraLeftBox")
        sizePolicy1.setHeightForWidth(self.extraLeftBox.sizePolicy().hasHeightForWidth())
        self.extraLeftBox.setSizePolicy(sizePolicy1)
        self.extraLeftBox.setMinimumSize(QSize(0, 0))
        self.extraLeftBox.setMaximumSize(QSize(0, 16777215))
        self.extraLeftBox.setFrameShape(QFrame.NoFrame)
        self.extraLeftBox.setFrameShadow(QFrame.Raised)
        self.extraColumLayout = QVBoxLayout(self.extraLeftBox)
        self.extraColumLayout.setSpacing(0)
        self.extraColumLayout.setObjectName(u"extraColumLayout")
        self.extraColumLayout.setContentsMargins(0, 0, 0, 0)
        self.extraTopBg = QFrame(self.extraLeftBox)
        self.extraTopBg.setObjectName(u"extraTopBg")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.extraTopBg.sizePolicy().hasHeightForWidth())
        self.extraTopBg.setSizePolicy(sizePolicy3)
        self.extraTopBg.setMinimumSize(QSize(0, 50))
        self.extraTopBg.setMaximumSize(QSize(16777215, 50))
        self.extraTopBg.setStyleSheet(u"background-color: rgb(89, 135, 182);")
        self.extraTopBg.setFrameShape(QFrame.NoFrame)
        self.extraTopBg.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.extraTopBg)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.extraTopLayout = QGridLayout()
        self.extraTopLayout.setObjectName(u"extraTopLayout")
        self.extraTopLayout.setHorizontalSpacing(10)
        self.extraTopLayout.setVerticalSpacing(0)
        self.extraTopLayout.setContentsMargins(10, -1, 10, -1)
        self.extraIcon = QFrame(self.extraTopBg)
        self.extraIcon.setObjectName(u"extraIcon")
        self.extraIcon.setMinimumSize(QSize(20, 0))
        self.extraIcon.setMaximumSize(QSize(20, 20))
        self.extraIcon.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-zoom-in.png);")
        self.extraIcon.setFrameShape(QFrame.NoFrame)
        self.extraIcon.setFrameShadow(QFrame.Raised)

        self.extraTopLayout.addWidget(self.extraIcon, 0, 0, 1, 1)

        self.extraLabel = QLabel(self.extraTopBg)
        self.extraLabel.setObjectName(u"extraLabel")
        self.extraLabel.setMinimumSize(QSize(150, 0))

        self.extraTopLayout.addWidget(self.extraLabel, 0, 1, 1, 1)

        self.extraCloseColumnBtn = QPushButton(self.extraTopBg)
        self.extraCloseColumnBtn.setObjectName(u"extraCloseColumnBtn")
        self.extraCloseColumnBtn.setMinimumSize(QSize(28, 28))
        self.extraCloseColumnBtn.setMaximumSize(QSize(28, 28))
        self.extraCloseColumnBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon = QIcon()
        icon.addFile(u":/icons/images/icons/icon_close.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.extraCloseColumnBtn.setIcon(icon)
        self.extraCloseColumnBtn.setIconSize(QSize(20, 20))

        self.extraTopLayout.addWidget(self.extraCloseColumnBtn, 0, 2, 1, 1)


        self.verticalLayout_5.addLayout(self.extraTopLayout)


        self.extraColumLayout.addWidget(self.extraTopBg)

        self.extraContent = QFrame(self.extraLeftBox)
        self.extraContent.setObjectName(u"extraContent")
        sizePolicy.setHeightForWidth(self.extraContent.sizePolicy().hasHeightForWidth())
        self.extraContent.setSizePolicy(sizePolicy)
        self.extraContent.setFrameShape(QFrame.NoFrame)
        self.extraContent.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.extraContent)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.extraTopMenu = QFrame(self.extraContent)
        self.extraTopMenu.setObjectName(u"extraTopMenu")
        sizePolicy.setHeightForWidth(self.extraTopMenu.sizePolicy().hasHeightForWidth())
        self.extraTopMenu.setSizePolicy(sizePolicy)
        self.extraTopMenu.setFrameShape(QFrame.NoFrame)
        self.extraTopMenu.setFrameShadow(QFrame.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.extraTopMenu)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.extraTopMenu)
        self.label.setObjectName(u"label")
        sizePolicy2.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy2)
        self.label.setScaledContents(False)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setMargin(10)

        self.verticalLayout_11.addWidget(self.label)

        self.label_date = QLabel(self.extraTopMenu)
        self.label_date.setObjectName(u"label_date")
        self.label_date.setStyleSheet(u"")

        self.verticalLayout_11.addWidget(self.label_date)

        self.left_downloadButton = QPushButton(self.extraTopMenu)
        self.left_downloadButton.setObjectName(u"left_downloadButton")
        sizePolicy2.setHeightForWidth(self.left_downloadButton.sizePolicy().hasHeightForWidth())
        self.left_downloadButton.setSizePolicy(sizePolicy2)
        self.left_downloadButton.setMinimumSize(QSize(0, 45))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(15)
        font3.setBold(False)
        font3.setItalic(False)
        self.left_downloadButton.setFont(font3)
        self.left_downloadButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.left_downloadButton.setLayoutDirection(Qt.LeftToRight)
        self.left_downloadButton.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-share-boxed.png);\n"
"font-size:15pt;")
        self.left_downloadButton.setIconSize(QSize(20, 20))

        self.verticalLayout_11.addWidget(self.left_downloadButton)

        self.left_addQueue = QPushButton(self.extraTopMenu)
        self.left_addQueue.setObjectName(u"left_addQueue")
        sizePolicy2.setHeightForWidth(self.left_addQueue.sizePolicy().hasHeightForWidth())
        self.left_addQueue.setSizePolicy(sizePolicy2)
        self.left_addQueue.setMinimumSize(QSize(0, 45))
        self.left_addQueue.setFont(font3)
        self.left_addQueue.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.left_addQueue.setLayoutDirection(Qt.LeftToRight)
        self.left_addQueue.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-star.png); \n"
"font-size:15pt;")

        self.verticalLayout_11.addWidget(self.left_addQueue)

        self.left_website = QPushButton(self.extraTopMenu)
        self.left_website.setObjectName(u"left_website")
        sizePolicy2.setHeightForWidth(self.left_website.sizePolicy().hasHeightForWidth())
        self.left_website.setSizePolicy(sizePolicy2)
        self.left_website.setMinimumSize(QSize(0, 45))
        self.left_website.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-paperclip.png);\n"
"font-size:15pt;")

        self.verticalLayout_11.addWidget(self.left_website)

        self.left_more = QPushButton(self.extraTopMenu)
        self.left_more.setObjectName(u"left_more")
        sizePolicy2.setHeightForWidth(self.left_more.sizePolicy().hasHeightForWidth())
        self.left_more.setSizePolicy(sizePolicy2)
        self.left_more.setMinimumSize(QSize(0, 45))
        self.left_more.setFont(font3)
        self.left_more.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.left_more.setLayoutDirection(Qt.LeftToRight)
        self.left_more.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-layers.png);\n"
"font-size:15pt;")

        self.verticalLayout_11.addWidget(self.left_more)


        self.verticalLayout_12.addWidget(self.extraTopMenu, 0, Qt.AlignTop)

        self.extraCenter = QFrame(self.extraContent)
        self.extraCenter.setObjectName(u"extraCenter")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.extraCenter.sizePolicy().hasHeightForWidth())
        self.extraCenter.setSizePolicy(sizePolicy4)
        self.extraCenter.setFrameShape(QFrame.NoFrame)
        self.extraCenter.setFrameShadow(QFrame.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.extraCenter)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 10, 0, 0)

        self.verticalLayout_12.addWidget(self.extraCenter)

        self.extraBottom = QFrame(self.extraContent)
        self.extraBottom.setObjectName(u"extraBottom")
        self.extraBottom.setFrameShape(QFrame.StyledPanel)
        self.extraBottom.setFrameShadow(QFrame.Raised)
        self.verticalLayout_26 = QVBoxLayout(self.extraBottom)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.left_progressName = QLabel(self.extraBottom)
        self.left_progressName.setObjectName(u"left_progressName")

        self.verticalLayout_26.addWidget(self.left_progressName)

        self.left_progressBar = QProgressBar(self.extraBottom)
        self.left_progressBar.setObjectName(u"left_progressBar")
        self.left_progressBar.setStyleSheet(u"QProgressBar {\n"
"	color: black;\n"
"}")
        self.left_progressBar.setValue(24)
        self.left_progressBar.setAlignment(Qt.AlignCenter)
        self.left_progressBar.setTextVisible(True)
        self.left_progressBar.setOrientation(Qt.Horizontal)
        self.left_progressBar.setInvertedAppearance(False)
        self.left_progressBar.setTextDirection(QProgressBar.TopToBottom)

        self.verticalLayout_26.addWidget(self.left_progressBar)


        self.verticalLayout_12.addWidget(self.extraBottom)


        self.extraColumLayout.addWidget(self.extraContent)


        self.appLayout.addWidget(self.extraLeftBox)

        self.contentBox = QFrame(self.bgApp)
        self.contentBox.setObjectName(u"contentBox")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy5.setHorizontalStretch(10)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.contentBox.sizePolicy().hasHeightForWidth())
        self.contentBox.setSizePolicy(sizePolicy5)
        self.contentBox.setMinimumSize(QSize(0, 0))
        self.contentBox.setFrameShape(QFrame.NoFrame)
        self.contentBox.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.contentBox)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.contentTopBg = QFrame(self.contentBox)
        self.contentTopBg.setObjectName(u"contentTopBg")
        self.contentTopBg.setMinimumSize(QSize(0, 50))
        self.contentTopBg.setMaximumSize(QSize(16777215, 50))
        self.contentTopBg.setFrameShape(QFrame.NoFrame)
        self.contentTopBg.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.contentTopBg)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 10, 0)
        self.leftBox = QFrame(self.contentTopBg)
        self.leftBox.setObjectName(u"leftBox")
        sizePolicy3.setHeightForWidth(self.leftBox.sizePolicy().hasHeightForWidth())
        self.leftBox.setSizePolicy(sizePolicy3)
        self.leftBox.setMinimumSize(QSize(0, 0))
        self.leftBox.setFrameShape(QFrame.NoFrame)
        self.leftBox.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.leftBox)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.titleRightInfo = QLabel(self.leftBox)
        self.titleRightInfo.setObjectName(u"titleRightInfo")
        sizePolicy4.setHeightForWidth(self.titleRightInfo.sizePolicy().hasHeightForWidth())
        self.titleRightInfo.setSizePolicy(sizePolicy4)
        self.titleRightInfo.setMaximumSize(QSize(16777215, 45))
        self.titleRightInfo.setFont(font)
        self.titleRightInfo.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_3.addWidget(self.titleRightInfo)


        self.horizontalLayout.addWidget(self.leftBox)

        self.rightButtons = QFrame(self.contentTopBg)
        self.rightButtons.setObjectName(u"rightButtons")
        self.rightButtons.setMinimumSize(QSize(0, 28))
        self.rightButtons.setFrameShape(QFrame.NoFrame)
        self.rightButtons.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.rightButtons)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalSlider_2 = QSlider(self.rightButtons)
        self.horizontalSlider_2.setObjectName(u"horizontalSlider_2")
        self.horizontalSlider_2.setOrientation(Qt.Horizontal)

        self.horizontalLayout_2.addWidget(self.horizontalSlider_2)

        self.settingsTopBtn = QPushButton(self.rightButtons)
        self.settingsTopBtn.setObjectName(u"settingsTopBtn")
        self.settingsTopBtn.setMinimumSize(QSize(28, 28))
        self.settingsTopBtn.setMaximumSize(QSize(28, 28))
        self.settingsTopBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon1 = QIcon()
        icon1.addFile(u":/icons/images/icons/icon_settings.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.settingsTopBtn.setIcon(icon1)
        self.settingsTopBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.settingsTopBtn)

        self.minimizeAppBtn = QPushButton(self.rightButtons)
        self.minimizeAppBtn.setObjectName(u"minimizeAppBtn")
        self.minimizeAppBtn.setMinimumSize(QSize(28, 28))
        self.minimizeAppBtn.setMaximumSize(QSize(28, 28))
        self.minimizeAppBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.minimizeAppBtn.setToolTipDuration(-1)
        icon2 = QIcon()
        icon2.addFile(u":/icons/images/icons/icon_minimize.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.minimizeAppBtn.setIcon(icon2)
        self.minimizeAppBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.minimizeAppBtn)

        self.maximizeRestoreAppBtn = QPushButton(self.rightButtons)
        self.maximizeRestoreAppBtn.setObjectName(u"maximizeRestoreAppBtn")
        self.maximizeRestoreAppBtn.setMinimumSize(QSize(28, 28))
        self.maximizeRestoreAppBtn.setMaximumSize(QSize(28, 28))
        font4 = QFont()
        font4.setFamilies([u"Segoe UI"])
        font4.setPointSize(10)
        font4.setBold(False)
        font4.setItalic(False)
        font4.setStyleStrategy(QFont.PreferDefault)
        self.maximizeRestoreAppBtn.setFont(font4)
        self.maximizeRestoreAppBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        icon3 = QIcon()
        icon3.addFile(u":/icons/images/icons/icon_maximize.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.maximizeRestoreAppBtn.setIcon(icon3)
        self.maximizeRestoreAppBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.maximizeRestoreAppBtn)

        self.closeAppBtn = QPushButton(self.rightButtons)
        self.closeAppBtn.setObjectName(u"closeAppBtn")
        self.closeAppBtn.setMinimumSize(QSize(28, 28))
        self.closeAppBtn.setMaximumSize(QSize(28, 28))
        self.closeAppBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.closeAppBtn.setIcon(icon)
        self.closeAppBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.closeAppBtn)


        self.horizontalLayout.addWidget(self.rightButtons, 0, Qt.AlignRight)


        self.verticalLayout_2.addWidget(self.contentTopBg)

        self.contentBottom = QFrame(self.contentBox)
        self.contentBottom.setObjectName(u"contentBottom")
        self.contentBottom.setFrameShape(QFrame.NoFrame)
        self.contentBottom.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.contentBottom)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.content = QFrame(self.contentBottom)
        self.content.setObjectName(u"content")
        self.content.setFrameShape(QFrame.NoFrame)
        self.content.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.content)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.pagesContainer = QFrame(self.content)
        self.pagesContainer.setObjectName(u"pagesContainer")
        self.pagesContainer.setStyleSheet(u"")
        self.pagesContainer.setFrameShape(QFrame.NoFrame)
        self.pagesContainer.setFrameShadow(QFrame.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.pagesContainer)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.stackedWidget = QStackedWidget(self.pagesContainer)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setStyleSheet(u"background: transparent;")
        self.anime_schedule = QWidget()
        self.anime_schedule.setObjectName(u"anime_schedule")
        self.verticalLayout_20 = QVBoxLayout(self.anime_schedule)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.pushButton_week = QFrame(self.anime_schedule)
        self.pushButton_week.setObjectName(u"pushButton_week")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(1)
        sizePolicy6.setHeightForWidth(self.pushButton_week.sizePolicy().hasHeightForWidth())
        self.pushButton_week.setSizePolicy(sizePolicy6)
        self.pushButton_week.setFrameShape(QFrame.StyledPanel)
        self.pushButton_week.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.pushButton_week)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 5)
        self.pushButton_sun = QPushButton(self.pushButton_week)
        self.pushButton_sun.setObjectName(u"pushButton_sun")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.pushButton_sun.sizePolicy().hasHeightForWidth())
        self.pushButton_sun.setSizePolicy(sizePolicy7)
        font5 = QFont()
        font5.setFamilies([u"Malgun Gothic"])
        font5.setBold(True)
        font5.setItalic(False)
        self.pushButton_sun.setFont(font5)
        self.pushButton_sun.setStyleSheet(u"background-color: rgb(52, 59, 72);\n"
"font-size: 32px; font-weight: bold;\n"
"")

        self.horizontalLayout_6.addWidget(self.pushButton_sun)

        self.pushButton_mon = QPushButton(self.pushButton_week)
        self.pushButton_mon.setObjectName(u"pushButton_mon")
        sizePolicy7.setHeightForWidth(self.pushButton_mon.sizePolicy().hasHeightForWidth())
        self.pushButton_mon.setSizePolicy(sizePolicy7)
        self.pushButton_mon.setFont(font5)
        self.pushButton_mon.setStyleSheet(u"background-color: rgb(52, 59, 72);\n"
"font-size: 32px; font-weight: bold;")

        self.horizontalLayout_6.addWidget(self.pushButton_mon)

        self.pushButton_tue = QPushButton(self.pushButton_week)
        self.pushButton_tue.setObjectName(u"pushButton_tue")
        sizePolicy7.setHeightForWidth(self.pushButton_tue.sizePolicy().hasHeightForWidth())
        self.pushButton_tue.setSizePolicy(sizePolicy7)
        self.pushButton_tue.setFont(font5)
        self.pushButton_tue.setStyleSheet(u"background-color: rgb(52, 59, 72);\n"
"font-size: 32px; font-weight: bold;")

        self.horizontalLayout_6.addWidget(self.pushButton_tue)

        self.pushButton_wed = QPushButton(self.pushButton_week)
        self.pushButton_wed.setObjectName(u"pushButton_wed")
        sizePolicy7.setHeightForWidth(self.pushButton_wed.sizePolicy().hasHeightForWidth())
        self.pushButton_wed.setSizePolicy(sizePolicy7)
        self.pushButton_wed.setFont(font5)
        self.pushButton_wed.setStyleSheet(u"background-color: rgb(52, 59, 72);\n"
"font-size: 32px; font-weight: bold;")

        self.horizontalLayout_6.addWidget(self.pushButton_wed)

        self.pushButton_thu = QPushButton(self.pushButton_week)
        self.pushButton_thu.setObjectName(u"pushButton_thu")
        sizePolicy7.setHeightForWidth(self.pushButton_thu.sizePolicy().hasHeightForWidth())
        self.pushButton_thu.setSizePolicy(sizePolicy7)
        self.pushButton_thu.setFont(font5)
        self.pushButton_thu.setStyleSheet(u"background-color: rgb(52, 59, 72);\n"
"font-size: 32px; font-weight: bold;")

        self.horizontalLayout_6.addWidget(self.pushButton_thu)

        self.pushButton_fri = QPushButton(self.pushButton_week)
        self.pushButton_fri.setObjectName(u"pushButton_fri")
        sizePolicy7.setHeightForWidth(self.pushButton_fri.sizePolicy().hasHeightForWidth())
        self.pushButton_fri.setSizePolicy(sizePolicy7)
        self.pushButton_fri.setFont(font5)
        self.pushButton_fri.setStyleSheet(u"background-color: rgb(52, 59, 72);\n"
"font-size: 32px; font-weight: bold;")

        self.horizontalLayout_6.addWidget(self.pushButton_fri)

        self.pushButton_sat = QPushButton(self.pushButton_week)
        self.pushButton_sat.setObjectName(u"pushButton_sat")
        sizePolicy7.setHeightForWidth(self.pushButton_sat.sizePolicy().hasHeightForWidth())
        self.pushButton_sat.setSizePolicy(sizePolicy7)
        self.pushButton_sat.setFont(font5)
        self.pushButton_sat.setStyleSheet(u"background-color: rgb(52, 59, 72);\n"
"font-size: 32px; font-weight: bold;")

        self.horizontalLayout_6.addWidget(self.pushButton_sat)

        self.pushButton_extra = QPushButton(self.pushButton_week)
        self.pushButton_extra.setObjectName(u"pushButton_extra")
        sizePolicy7.setHeightForWidth(self.pushButton_extra.sizePolicy().hasHeightForWidth())
        self.pushButton_extra.setSizePolicy(sizePolicy7)
        self.pushButton_extra.setFont(font5)
        self.pushButton_extra.setStyleSheet(u"background-color: rgb(52, 59, 72);\n"
"font-size: 32px; font-weight: bold;")

        self.horizontalLayout_6.addWidget(self.pushButton_extra)

        self.pushButton_new = QPushButton(self.pushButton_week)
        self.pushButton_new.setObjectName(u"pushButton_new")
        sizePolicy7.setHeightForWidth(self.pushButton_new.sizePolicy().hasHeightForWidth())
        self.pushButton_new.setSizePolicy(sizePolicy7)
        self.pushButton_new.setFont(font5)
        self.pushButton_new.setStyleSheet(u"background-color: rgb(52, 59, 72);\n"
"font-size: 32px; font-weight: bold;")

        self.horizontalLayout_6.addWidget(self.pushButton_new)


        self.verticalLayout_20.addWidget(self.pushButton_week)

        self.anime_time = QFrame(self.anime_schedule)
        self.anime_time.setObjectName(u"anime_time")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(5)
        sizePolicy8.setHeightForWidth(self.anime_time.sizePolicy().hasHeightForWidth())
        self.anime_time.setSizePolicy(sizePolicy8)
        self.anime_time.setMinimumSize(QSize(0, 0))
        self.anime_time.setStyleSheet(u"")
        self.anime_time.setFrameShape(QFrame.StyledPanel)
        self.anime_time.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.anime_time)
        self.horizontalLayout_7.setSpacing(3)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(3, 3, 3, 3)
        self.anime_time_table = QTableWidget(self.anime_time)
        if (self.anime_time_table.columnCount() < 7):
            self.anime_time_table.setColumnCount(7)
        __qtablewidgetitem = QTableWidgetItem()
        self.anime_time_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.anime_time_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.anime_time_table.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.anime_time_table.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.anime_time_table.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.anime_time_table.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        __qtablewidgetitem6 = QTableWidgetItem()
        self.anime_time_table.setHorizontalHeaderItem(6, __qtablewidgetitem6)
        self.anime_time_table.setObjectName(u"anime_time_table")
        self.anime_time_table.setStyleSheet(u"font-size: 20px; \n"
"")
        self.anime_time_table.setFrameShape(QFrame.StyledPanel)
        self.anime_time_table.setFrameShadow(QFrame.Sunken)
        self.anime_time_table.setDragEnabled(False)
        self.anime_time_table.horizontalHeader().setHighlightSections(True)
        self.anime_time_table.horizontalHeader().setProperty("showSortIndicator", False)

        self.horizontalLayout_7.addWidget(self.anime_time_table)


        self.verticalLayout_20.addWidget(self.anime_time)

        self.stackedWidget.addWidget(self.anime_schedule)
        self.download_page = QWidget()
        self.download_page.setObjectName(u"download_page")
        self.download_page.setStyleSheet(u"b")
        self.verticalLayout = QVBoxLayout(self.download_page)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.row_1 = QFrame(self.download_page)
        self.row_1.setObjectName(u"row_1")
        sizePolicy.setHeightForWidth(self.row_1.sizePolicy().hasHeightForWidth())
        self.row_1.setSizePolicy(sizePolicy)
        self.row_1.setFrameShape(QFrame.StyledPanel)
        self.row_1.setFrameShadow(QFrame.Raised)
        self.verticalLayout_16 = QVBoxLayout(self.row_1)
        self.verticalLayout_16.setSpacing(0)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.frame_div_content_1 = QFrame(self.row_1)
        self.frame_div_content_1.setObjectName(u"frame_div_content_1")
        self.frame_div_content_1.setMinimumSize(QSize(0, 110))
        self.frame_div_content_1.setMaximumSize(QSize(16777215, 110))
        self.frame_div_content_1.setFrameShape(QFrame.NoFrame)
        self.frame_div_content_1.setFrameShadow(QFrame.Raised)
        self.verticalLayout_17 = QVBoxLayout(self.frame_div_content_1)
        self.verticalLayout_17.setSpacing(0)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.frame_title_wid_1 = QFrame(self.frame_div_content_1)
        self.frame_title_wid_1.setObjectName(u"frame_title_wid_1")
        sizePolicy.setHeightForWidth(self.frame_title_wid_1.sizePolicy().hasHeightForWidth())
        self.frame_title_wid_1.setSizePolicy(sizePolicy)
        self.frame_title_wid_1.setMaximumSize(QSize(16777215, 35))
        self.frame_title_wid_1.setFrameShape(QFrame.StyledPanel)
        self.frame_title_wid_1.setFrameShadow(QFrame.Raised)
        self.verticalLayout_18 = QVBoxLayout(self.frame_title_wid_1)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(11, 0, 0, 0)
        self.labelBoxBlenderInstalation = QLabel(self.frame_title_wid_1)
        self.labelBoxBlenderInstalation.setObjectName(u"labelBoxBlenderInstalation")
        sizePolicy9 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy9.setHorizontalStretch(0)
        sizePolicy9.setVerticalStretch(0)
        sizePolicy9.setHeightForWidth(self.labelBoxBlenderInstalation.sizePolicy().hasHeightForWidth())
        self.labelBoxBlenderInstalation.setSizePolicy(sizePolicy9)
        self.labelBoxBlenderInstalation.setMinimumSize(QSize(0, 50))
        self.labelBoxBlenderInstalation.setFont(font)
        self.labelBoxBlenderInstalation.setStyleSheet(u"")

        self.verticalLayout_18.addWidget(self.labelBoxBlenderInstalation)


        self.verticalLayout_17.addWidget(self.frame_title_wid_1)

        self.frame_content_wid_1 = QFrame(self.frame_div_content_1)
        self.frame_content_wid_1.setObjectName(u"frame_content_wid_1")
        sizePolicy.setHeightForWidth(self.frame_content_wid_1.sizePolicy().hasHeightForWidth())
        self.frame_content_wid_1.setSizePolicy(sizePolicy)
        self.frame_content_wid_1.setFrameShape(QFrame.NoFrame)
        self.frame_content_wid_1.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.frame_content_wid_1)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, -1, -1, 0)
        self.labelVersion_3 = QLabel(self.frame_content_wid_1)
        self.labelVersion_3.setObjectName(u"labelVersion_3")
        self.labelVersion_3.setStyleSheet(u"color: rgb(113, 126, 149);")
        self.labelVersion_3.setLineWidth(1)
        self.labelVersion_3.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.labelVersion_3, 2, 0, 1, 4)

        self.yml_downloadPath = QLineEdit(self.frame_content_wid_1)
        self.yml_downloadPath.setObjectName(u"yml_downloadPath")
        self.yml_downloadPath.setMinimumSize(QSize(0, 30))
        self.yml_downloadPath.setStyleSheet(u"background-color: rgb(33, 37, 43);")

        self.gridLayout.addWidget(self.yml_downloadPath, 1, 0, 1, 1)

        self.scheduler_folder = QPushButton(self.frame_content_wid_1)
        self.scheduler_folder.setObjectName(u"scheduler_folder")
        self.scheduler_folder.setMinimumSize(QSize(150, 30))
        self.scheduler_folder.setStyleSheet(u"background-color: rgb(52, 59, 72);")
        icon4 = QIcon()
        icon4.addFile(u":/icons/images/icons/cil-folder-open.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.scheduler_folder.setIcon(icon4)

        self.gridLayout.addWidget(self.scheduler_folder, 1, 2, 1, 1)

        self.ym_openfileButton = QPushButton(self.frame_content_wid_1)
        self.ym_openfileButton.setObjectName(u"ym_openfileButton")
        self.ym_openfileButton.setMinimumSize(QSize(150, 30))
        self.ym_openfileButton.setFont(font)
        self.ym_openfileButton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.ym_openfileButton.setStyleSheet(u"background-color: rgb(52, 59, 72);")
        self.ym_openfileButton.setIcon(icon4)

        self.gridLayout.addWidget(self.ym_openfileButton, 1, 1, 1, 1)


        self.horizontalLayout_9.addLayout(self.gridLayout)


        self.verticalLayout_17.addWidget(self.frame_content_wid_1)


        self.verticalLayout_16.addWidget(self.frame_div_content_1)


        self.verticalLayout.addWidget(self.row_1)

        self.row_2 = QFrame(self.download_page)
        self.row_2.setObjectName(u"row_2")
        sizePolicy.setHeightForWidth(self.row_2.sizePolicy().hasHeightForWidth())
        self.row_2.setSizePolicy(sizePolicy)
        self.row_2.setMinimumSize(QSize(0, 200))
        self.row_2.setFrameShape(QFrame.StyledPanel)
        self.row_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_19 = QVBoxLayout(self.row_2)
        self.verticalLayout_19.setSpacing(3)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.label_3 = QLabel(self.row_2)
        self.label_3.setObjectName(u"label_3")
        sizePolicy3.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy3)
        self.label_3.setMinimumSize(QSize(0, 0))

        self.verticalLayout_19.addWidget(self.label_3)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.scheduler_checkBox = QCheckBox(self.row_2)
        self.scheduler_checkBox.setObjectName(u"scheduler_checkBox")
        self.scheduler_checkBox.setStyleSheet(u"")

        self.gridLayout_2.addWidget(self.scheduler_checkBox, 1, 0, 3, 1)

        self.scheduler_comboBox = QComboBox(self.row_2)
        self.scheduler_comboBox.addItem("")
        self.scheduler_comboBox.addItem("")
        self.scheduler_comboBox.addItem("")
        self.scheduler_comboBox.addItem("")
        self.scheduler_comboBox.addItem("")
        self.scheduler_comboBox.addItem("")
        self.scheduler_comboBox.addItem("")
        self.scheduler_comboBox.addItem("")
        self.scheduler_comboBox.setObjectName(u"scheduler_comboBox")

        self.gridLayout_2.addWidget(self.scheduler_comboBox, 4, 0, 1, 1)

        self.yml_save_button = QPushButton(self.row_2)
        self.yml_save_button.setObjectName(u"yml_save_button")
        sizePolicy10 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy10.setHorizontalStretch(0)
        sizePolicy10.setVerticalStretch(0)
        sizePolicy10.setHeightForWidth(self.yml_save_button.sizePolicy().hasHeightForWidth())
        self.yml_save_button.setSizePolicy(sizePolicy10)
        self.yml_save_button.setMinimumSize(QSize(90, 0))
        self.yml_save_button.setStyleSheet(u"background-color: rgb(52, 59, 72);")

        self.gridLayout_2.addWidget(self.yml_save_button, 1, 9, 1, 1)

        self.yml_remove_row = QPushButton(self.row_2)
        self.yml_remove_row.setObjectName(u"yml_remove_row")
        self.yml_remove_row.setMinimumSize(QSize(90, 0))
        self.yml_remove_row.setStyleSheet(u"background-color: rgb(52, 59, 72);")

        self.gridLayout_2.addWidget(self.yml_remove_row, 1, 6, 1, 1)

        self.label_2 = QLabel(self.row_2)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 2, 1, 1)

        self.yml_open_button = QPushButton(self.row_2)
        self.yml_open_button.setObjectName(u"yml_open_button")
        self.yml_open_button.setMinimumSize(QSize(90, 0))
        self.yml_open_button.setStyleSheet(u"background-color: rgb(52, 59, 72);")

        self.gridLayout_2.addWidget(self.yml_open_button, 1, 7, 1, 1)

        self.scrollArea = QScrollArea(self.row_2)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setStyleSheet(u" QScrollBar:vertical {\n"
"    background: rgb(52, 59, 72);\n"
" }\n"
" QScrollBar:horizontal {\n"
"    background: rgb(52, 59, 72);\n"
" }")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 210, 210))
        self.scrollAreaWidgetContents.setStyleSheet(u" QScrollBar:vertical {\n"
"	border: none;\n"
"    background: rgb(52, 59, 72);\n"
"    width: 14px;\n"
"    margin: 21px 0 21px 0;\n"
"	border-radius: 0px;\n"
" }")
        self.horizontalLayout_11 = QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(5, 5, 5, 5)
        self.yml_content = QPlainTextEdit(self.scrollAreaWidgetContents)
        self.yml_content.setObjectName(u"yml_content")
        self.yml_content.setMinimumSize(QSize(200, 200))
        self.yml_content.setStyleSheet(u"background-color: rgb(33, 37, 43);")

        self.horizontalLayout_11.addWidget(self.yml_content)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_2.addWidget(self.scrollArea, 3, 2, 5, 8)

        self.yml_reset_button = QPushButton(self.row_2)
        self.yml_reset_button.setObjectName(u"yml_reset_button")
        self.yml_reset_button.setMinimumSize(QSize(90, 0))
        self.yml_reset_button.setStyleSheet(u"background-color: rgb(52, 59, 72);")

        self.gridLayout_2.addWidget(self.yml_reset_button, 1, 5, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 1, 3, 1, 1)

        self.scheduler_button = QPushButton(self.row_2)
        self.scheduler_button.setObjectName(u"scheduler_button")
        sizePolicy2.setHeightForWidth(self.scheduler_button.sizePolicy().hasHeightForWidth())
        self.scheduler_button.setSizePolicy(sizePolicy2)
        self.scheduler_button.setMinimumSize(QSize(0, 40))
        self.scheduler_button.setStyleSheet(u"background-color: rgb(52, 59, 72);")

        self.gridLayout_2.addWidget(self.scheduler_button, 5, 0, 3, 1)

        self.yml_reload_button = QPushButton(self.row_2)
        self.yml_reload_button.setObjectName(u"yml_reload_button")
        self.yml_reload_button.setMinimumSize(QSize(90, 0))
        self.yml_reload_button.setStyleSheet(u"background-color: rgb(52, 59, 72);")

        self.gridLayout_2.addWidget(self.yml_reload_button, 1, 8, 1, 1)


        self.verticalLayout_19.addLayout(self.gridLayout_2)


        self.verticalLayout.addWidget(self.row_2)

        self.row_3 = QFrame(self.download_page)
        self.row_3.setObjectName(u"row_3")
        sizePolicy.setHeightForWidth(self.row_3.sizePolicy().hasHeightForWidth())
        self.row_3.setSizePolicy(sizePolicy)
        self.row_3.setMinimumSize(QSize(0, 150))
        self.row_3.setFrameShape(QFrame.StyledPanel)
        self.row_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_24 = QVBoxLayout(self.row_3)
        self.verticalLayout_24.setSpacing(3)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(2, 0, 2, 0)
        self.scheduler_table = QTableWidget(self.row_3)
        if (self.scheduler_table.columnCount() < 2):
            self.scheduler_table.setColumnCount(2)
        __qtablewidgetitem7 = QTableWidgetItem()
        self.scheduler_table.setHorizontalHeaderItem(0, __qtablewidgetitem7)
        __qtablewidgetitem8 = QTableWidgetItem()
        self.scheduler_table.setHorizontalHeaderItem(1, __qtablewidgetitem8)
        if (self.scheduler_table.rowCount() < 16):
            self.scheduler_table.setRowCount(16)
        font6 = QFont()
        font6.setFamilies([u"Segoe UI"])
        __qtablewidgetitem9 = QTableWidgetItem()
        __qtablewidgetitem9.setFont(font6);
        self.scheduler_table.setVerticalHeaderItem(0, __qtablewidgetitem9)
        __qtablewidgetitem10 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(1, __qtablewidgetitem10)
        __qtablewidgetitem11 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(2, __qtablewidgetitem11)
        __qtablewidgetitem12 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(3, __qtablewidgetitem12)
        __qtablewidgetitem13 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(4, __qtablewidgetitem13)
        __qtablewidgetitem14 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(5, __qtablewidgetitem14)
        __qtablewidgetitem15 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(6, __qtablewidgetitem15)
        __qtablewidgetitem16 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(7, __qtablewidgetitem16)
        __qtablewidgetitem17 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(8, __qtablewidgetitem17)
        __qtablewidgetitem18 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(9, __qtablewidgetitem18)
        __qtablewidgetitem19 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(10, __qtablewidgetitem19)
        __qtablewidgetitem20 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(11, __qtablewidgetitem20)
        __qtablewidgetitem21 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(12, __qtablewidgetitem21)
        __qtablewidgetitem22 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(13, __qtablewidgetitem22)
        __qtablewidgetitem23 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(14, __qtablewidgetitem23)
        __qtablewidgetitem24 = QTableWidgetItem()
        self.scheduler_table.setVerticalHeaderItem(15, __qtablewidgetitem24)
        self.scheduler_table.setObjectName(u"scheduler_table")
        sizePolicy9.setHeightForWidth(self.scheduler_table.sizePolicy().hasHeightForWidth())
        self.scheduler_table.setSizePolicy(sizePolicy9)
        palette = QPalette()
        brush = QBrush(QColor(221, 221, 221, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(0, 0, 0, 0))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        brush2 = QBrush(QColor(0, 0, 0, 255))
        brush2.setStyle(Qt.NoBrush)
        palette.setBrush(QPalette.Active, QPalette.Base, brush2)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        brush3 = QBrush(QColor(0, 0, 0, 255))
        brush3.setStyle(Qt.NoBrush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush)
        brush4 = QBrush(QColor(0, 0, 0, 255))
        brush4.setStyle(Qt.NoBrush)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush4)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)
        self.scheduler_table.setPalette(palette)
        self.scheduler_table.setFrameShape(QFrame.NoFrame)
        self.scheduler_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scheduler_table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.scheduler_table.setEditTriggers(QAbstractItemView.AnyKeyPressed|QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.scheduler_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.scheduler_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.scheduler_table.setShowGrid(True)
        self.scheduler_table.setGridStyle(Qt.SolidLine)
        self.scheduler_table.setSortingEnabled(False)
        self.scheduler_table.horizontalHeader().setVisible(False)
        self.scheduler_table.horizontalHeader().setCascadingSectionResizes(True)
        self.scheduler_table.horizontalHeader().setDefaultSectionSize(200)
        self.scheduler_table.horizontalHeader().setStretchLastSection(True)
        self.scheduler_table.verticalHeader().setVisible(False)
        self.scheduler_table.verticalHeader().setCascadingSectionResizes(False)
        self.scheduler_table.verticalHeader().setHighlightSections(False)
        self.scheduler_table.verticalHeader().setStretchLastSection(True)

        self.verticalLayout_24.addWidget(self.scheduler_table)


        self.verticalLayout.addWidget(self.row_3)

        self.stackedWidget.addWidget(self.download_page)
        self.search_page = QWidget()
        self.search_page.setObjectName(u"search_page")
        self.verticalLayout_28 = QVBoxLayout(self.search_page)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.search_row_1 = QFrame(self.search_page)
        self.search_row_1.setObjectName(u"search_row_1")
        self.search_row_1.setMaximumSize(QSize(16777215, 35))
        self.search_row_1.setFrameShape(QFrame.StyledPanel)
        self.search_row_1.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.search_row_1)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(-1, 0, 11, 0)
        self.labelBoxBlenderInstalation_2 = QLabel(self.search_row_1)
        self.labelBoxBlenderInstalation_2.setObjectName(u"labelBoxBlenderInstalation_2")
        sizePolicy9.setHeightForWidth(self.labelBoxBlenderInstalation_2.sizePolicy().hasHeightForWidth())
        self.labelBoxBlenderInstalation_2.setSizePolicy(sizePolicy9)
        self.labelBoxBlenderInstalation_2.setMinimumSize(QSize(0, 50))
        self.labelBoxBlenderInstalation_2.setFont(font)
        self.labelBoxBlenderInstalation_2.setStyleSheet(u"")

        self.horizontalLayout_8.addWidget(self.labelBoxBlenderInstalation_2)

        self.label_total_elements = QLabel(self.search_row_1)
        self.label_total_elements.setObjectName(u"label_total_elements")
        sizePolicy.setHeightForWidth(self.label_total_elements.sizePolicy().hasHeightForWidth())
        self.label_total_elements.setSizePolicy(sizePolicy)
        self.label_total_elements.setMinimumSize(QSize(0, 50))

        self.horizontalLayout_8.addWidget(self.label_total_elements)


        self.verticalLayout_28.addWidget(self.search_row_1)

        self.search_row_2 = QFrame(self.search_page)
        self.search_row_2.setObjectName(u"search_row_2")
        self.search_row_2.setFrameShape(QFrame.StyledPanel)
        self.search_row_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.search_row_2)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.search_input = QLineEdit(self.search_row_2)
        self.search_input.setObjectName(u"search_input")
        self.search_input.setMinimumSize(QSize(0, 60))
        self.search_input.setStyleSheet(u"background-color: rgb(33, 37, 43);\n"
"font-size: 20px;")

        self.horizontalLayout_10.addWidget(self.search_input)

        self.search_button = QPushButton(self.search_row_2)
        self.search_button.setObjectName(u"search_button")
        self.search_button.setMinimumSize(QSize(150, 60))
        font7 = QFont()
        font7.setFamilies([u"Segoe UI"])
        font7.setBold(False)
        font7.setItalic(False)
        self.search_button.setFont(font7)
        self.search_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.search_button.setStyleSheet(u"background-color: rgb(52, 59, 72);\n"
"font-size: 20px;")
        icon5 = QIcon()
        iconThemeName = u"None"
        if QIcon.hasThemeIcon(iconThemeName):
            icon5 = QIcon.fromTheme(iconThemeName)
        else:
            icon5.addFile(u".", QSize(), QIcon.Mode.Normal, QIcon.State.Off)

        self.search_button.setIcon(icon5)

        self.horizontalLayout_10.addWidget(self.search_button)


        self.verticalLayout_28.addWidget(self.search_row_2)

        self.search_row_3 = QFrame(self.search_page)
        self.search_row_3.setObjectName(u"search_row_3")
        self.search_row_3.setFrameShape(QFrame.StyledPanel)
        self.search_row_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_12 = QHBoxLayout(self.search_row_3)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(7, -1, 7, -1)
        self.anime_search_table = QTableWidget(self.search_row_3)
        if (self.anime_search_table.columnCount() < 7):
            self.anime_search_table.setColumnCount(7)
        __qtablewidgetitem25 = QTableWidgetItem()
        self.anime_search_table.setHorizontalHeaderItem(0, __qtablewidgetitem25)
        __qtablewidgetitem26 = QTableWidgetItem()
        self.anime_search_table.setHorizontalHeaderItem(1, __qtablewidgetitem26)
        __qtablewidgetitem27 = QTableWidgetItem()
        self.anime_search_table.setHorizontalHeaderItem(2, __qtablewidgetitem27)
        __qtablewidgetitem28 = QTableWidgetItem()
        self.anime_search_table.setHorizontalHeaderItem(3, __qtablewidgetitem28)
        __qtablewidgetitem29 = QTableWidgetItem()
        self.anime_search_table.setHorizontalHeaderItem(4, __qtablewidgetitem29)
        __qtablewidgetitem30 = QTableWidgetItem()
        self.anime_search_table.setHorizontalHeaderItem(5, __qtablewidgetitem30)
        __qtablewidgetitem31 = QTableWidgetItem()
        self.anime_search_table.setHorizontalHeaderItem(6, __qtablewidgetitem31)
        self.anime_search_table.setObjectName(u"anime_search_table")
        self.anime_search_table.setStyleSheet(u"font-size: 20px; \n"
"")
        self.anime_search_table.setFrameShape(QFrame.StyledPanel)
        self.anime_search_table.setFrameShadow(QFrame.Sunken)
        self.anime_search_table.setDragEnabled(False)
        self.anime_search_table.horizontalHeader().setHighlightSections(True)
        self.anime_search_table.horizontalHeader().setProperty("showSortIndicator", False)

        self.horizontalLayout_12.addWidget(self.anime_search_table)


        self.verticalLayout_28.addWidget(self.search_row_3)

        self.stackedWidget.addWidget(self.search_page)
        self.recent_page = QWidget()
        self.recent_page.setObjectName(u"recent_page")
        self.verticalLayout_27 = QVBoxLayout(self.recent_page)
        self.verticalLayout_27.setObjectName(u"verticalLayout_27")
        self.recent_row_1 = QFrame(self.recent_page)
        self.recent_row_1.setObjectName(u"recent_row_1")
        self.recent_row_1.setMaximumSize(QSize(16777215, 36))
        self.recent_row_1.setFrameShape(QFrame.StyledPanel)
        self.recent_row_1.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_13 = QHBoxLayout(self.recent_row_1)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(-1, 0, -1, 0)
        self.labal_recent_title = QLabel(self.recent_row_1)
        self.labal_recent_title.setObjectName(u"labal_recent_title")
        sizePolicy9.setHeightForWidth(self.labal_recent_title.sizePolicy().hasHeightForWidth())
        self.labal_recent_title.setSizePolicy(sizePolicy9)
        self.labal_recent_title.setMinimumSize(QSize(0, 50))
        self.labal_recent_title.setFont(font)
        self.labal_recent_title.setStyleSheet(u"")

        self.horizontalLayout_13.addWidget(self.labal_recent_title)

        self.label_recemt_total_elements = QLabel(self.recent_row_1)
        self.label_recemt_total_elements.setObjectName(u"label_recemt_total_elements")
        sizePolicy.setHeightForWidth(self.label_recemt_total_elements.sizePolicy().hasHeightForWidth())
        self.label_recemt_total_elements.setSizePolicy(sizePolicy)
        self.label_recemt_total_elements.setMinimumSize(QSize(0, 50))

        self.horizontalLayout_13.addWidget(self.label_recemt_total_elements)


        self.verticalLayout_27.addWidget(self.recent_row_1)

        self.recent_row_2 = QFrame(self.recent_page)
        self.recent_row_2.setObjectName(u"recent_row_2")
        self.recent_row_2.setFrameShape(QFrame.StyledPanel)
        self.recent_row_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_14 = QHBoxLayout(self.recent_row_2)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(7, -1, 7, -1)
        self.anime_recent_table = QTableWidget(self.recent_row_2)
        if (self.anime_recent_table.columnCount() < 6):
            self.anime_recent_table.setColumnCount(6)
        __qtablewidgetitem32 = QTableWidgetItem()
        self.anime_recent_table.setHorizontalHeaderItem(0, __qtablewidgetitem32)
        __qtablewidgetitem33 = QTableWidgetItem()
        self.anime_recent_table.setHorizontalHeaderItem(1, __qtablewidgetitem33)
        __qtablewidgetitem34 = QTableWidgetItem()
        self.anime_recent_table.setHorizontalHeaderItem(2, __qtablewidgetitem34)
        __qtablewidgetitem35 = QTableWidgetItem()
        self.anime_recent_table.setHorizontalHeaderItem(3, __qtablewidgetitem35)
        __qtablewidgetitem36 = QTableWidgetItem()
        self.anime_recent_table.setHorizontalHeaderItem(4, __qtablewidgetitem36)
        __qtablewidgetitem37 = QTableWidgetItem()
        self.anime_recent_table.setHorizontalHeaderItem(5, __qtablewidgetitem37)
        self.anime_recent_table.setObjectName(u"anime_recent_table")
        self.anime_recent_table.setStyleSheet(u"font-size: 20px; \n"
"")
        self.anime_recent_table.setFrameShape(QFrame.StyledPanel)
        self.anime_recent_table.setFrameShadow(QFrame.Sunken)
        self.anime_recent_table.setDragEnabled(False)
        self.anime_recent_table.horizontalHeader().setHighlightSections(True)
        self.anime_recent_table.horizontalHeader().setProperty("showSortIndicator", False)

        self.horizontalLayout_14.addWidget(self.anime_recent_table)


        self.verticalLayout_27.addWidget(self.recent_row_2)

        self.stackedWidget.addWidget(self.recent_page)
        self.log_page = QWidget()
        self.log_page.setObjectName(u"log_page")
        sizePolicy3.setHeightForWidth(self.log_page.sizePolicy().hasHeightForWidth())
        self.log_page.setSizePolicy(sizePolicy3)
        self.verticalLayout_21 = QVBoxLayout(self.log_page)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.frame_2 = QFrame(self.log_page)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy6.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy6)
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.verticalLayout_23 = QVBoxLayout(self.frame_2)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.log_timestamp = QTableWidget(self.frame_2)
        if (self.log_timestamp.columnCount() < 3):
            self.log_timestamp.setColumnCount(3)
        __qtablewidgetitem38 = QTableWidgetItem()
        self.log_timestamp.setHorizontalHeaderItem(0, __qtablewidgetitem38)
        __qtablewidgetitem39 = QTableWidgetItem()
        self.log_timestamp.setHorizontalHeaderItem(1, __qtablewidgetitem39)
        __qtablewidgetitem40 = QTableWidgetItem()
        self.log_timestamp.setHorizontalHeaderItem(2, __qtablewidgetitem40)
        self.log_timestamp.setObjectName(u"log_timestamp")

        self.verticalLayout_23.addWidget(self.log_timestamp)


        self.verticalLayout_21.addWidget(self.frame_2)

        self.frame = QFrame(self.log_page)
        self.frame.setObjectName(u"frame")
        sizePolicy6.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy6)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_22 = QVBoxLayout(self.frame)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.log_console = QPlainTextEdit(self.frame)
        self.log_console.setObjectName(u"log_console")

        self.verticalLayout_22.addWidget(self.log_console)


        self.verticalLayout_21.addWidget(self.frame)

        self.stackedWidget.addWidget(self.log_page)

        self.verticalLayout_15.addWidget(self.stackedWidget)


        self.horizontalLayout_4.addWidget(self.pagesContainer)

        self.extraRightBox = QFrame(self.content)
        self.extraRightBox.setObjectName(u"extraRightBox")
        self.extraRightBox.setMinimumSize(QSize(0, 0))
        self.extraRightBox.setMaximumSize(QSize(0, 16777215))
        self.extraRightBox.setFrameShape(QFrame.NoFrame)
        self.extraRightBox.setFrameShadow(QFrame.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.extraRightBox)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.themeSettingsTopDetail = QFrame(self.extraRightBox)
        self.themeSettingsTopDetail.setObjectName(u"themeSettingsTopDetail")
        self.themeSettingsTopDetail.setMaximumSize(QSize(16777215, 3))
        self.themeSettingsTopDetail.setFrameShape(QFrame.NoFrame)
        self.themeSettingsTopDetail.setFrameShadow(QFrame.Raised)

        self.verticalLayout_7.addWidget(self.themeSettingsTopDetail)

        self.contentSettings = QFrame(self.extraRightBox)
        self.contentSettings.setObjectName(u"contentSettings")
        self.contentSettings.setFrameShape(QFrame.NoFrame)
        self.contentSettings.setFrameShadow(QFrame.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.contentSettings)
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.topMenus = QFrame(self.contentSettings)
        self.topMenus.setObjectName(u"topMenus")
        self.topMenus.setFrameShape(QFrame.NoFrame)
        self.topMenus.setFrameShadow(QFrame.Raised)
        self.verticalLayout_14 = QVBoxLayout(self.topMenus)
        self.verticalLayout_14.setSpacing(0)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.btn_message = QPushButton(self.topMenus)
        self.btn_message.setObjectName(u"btn_message")
        sizePolicy2.setHeightForWidth(self.btn_message.sizePolicy().hasHeightForWidth())
        self.btn_message.setSizePolicy(sizePolicy2)
        self.btn_message.setMinimumSize(QSize(0, 45))
        self.btn_message.setFont(font)
        self.btn_message.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_message.setLayoutDirection(Qt.LeftToRight)
        self.btn_message.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-envelope-open.png);")

        self.verticalLayout_14.addWidget(self.btn_message)

        self.btn_print = QPushButton(self.topMenus)
        self.btn_print.setObjectName(u"btn_print")
        sizePolicy2.setHeightForWidth(self.btn_print.sizePolicy().hasHeightForWidth())
        self.btn_print.setSizePolicy(sizePolicy2)
        self.btn_print.setMinimumSize(QSize(0, 45))
        self.btn_print.setFont(font)
        self.btn_print.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_print.setLayoutDirection(Qt.LeftToRight)
        self.btn_print.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-print.png);")

        self.verticalLayout_14.addWidget(self.btn_print)

        self.btn_logout = QPushButton(self.topMenus)
        self.btn_logout.setObjectName(u"btn_logout")
        sizePolicy2.setHeightForWidth(self.btn_logout.sizePolicy().hasHeightForWidth())
        self.btn_logout.setSizePolicy(sizePolicy2)
        self.btn_logout.setMinimumSize(QSize(0, 45))
        self.btn_logout.setFont(font)
        self.btn_logout.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_logout.setLayoutDirection(Qt.LeftToRight)
        self.btn_logout.setStyleSheet(u"background-image: url(:/icons/images/icons/cil-account-logout.png);")

        self.verticalLayout_14.addWidget(self.btn_logout)


        self.verticalLayout_13.addWidget(self.topMenus, 0, Qt.AlignTop)


        self.verticalLayout_7.addWidget(self.contentSettings)


        self.horizontalLayout_4.addWidget(self.extraRightBox)


        self.verticalLayout_6.addWidget(self.content)

        self.bottomBar = QFrame(self.contentBottom)
        self.bottomBar.setObjectName(u"bottomBar")
        self.bottomBar.setMinimumSize(QSize(0, 22))
        self.bottomBar.setMaximumSize(QSize(16777215, 22))
        self.bottomBar.setFrameShape(QFrame.NoFrame)
        self.bottomBar.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.bottomBar)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.creditsLabel = QLabel(self.bottomBar)
        self.creditsLabel.setObjectName(u"creditsLabel")
        self.creditsLabel.setMaximumSize(QSize(16777215, 16))
        self.creditsLabel.setFont(font7)
        self.creditsLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.creditsLabel)

        self.version = QLabel(self.bottomBar)
        self.version.setObjectName(u"version")
        self.version.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.version)

        self.frame_size_grip = QFrame(self.bottomBar)
        self.frame_size_grip.setObjectName(u"frame_size_grip")
        self.frame_size_grip.setMinimumSize(QSize(20, 0))
        self.frame_size_grip.setMaximumSize(QSize(20, 16777215))
        self.frame_size_grip.setFrameShape(QFrame.NoFrame)
        self.frame_size_grip.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_5.addWidget(self.frame_size_grip)


        self.verticalLayout_6.addWidget(self.bottomBar)


        self.verticalLayout_2.addWidget(self.contentBottom)


        self.appLayout.addWidget(self.contentBox)


        self.verticalLayout_25.addWidget(self.bgApp)

        MainWindow.setCentralWidget(self.styleSheet)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.titleLeftApp.setText(QCoreApplication.translate("MainWindow", u"SMI-AUTO-DOWNLOADER", None))
        self.titleLeftDescription.setText(QCoreApplication.translate("MainWindow", u"GUI Edition By KUDONG", None))
        self.toggleButton.setText(QCoreApplication.translate("MainWindow", u"\uc228\uae30\uae30", None))
        self.btn_home.setText(QCoreApplication.translate("MainWindow", u"\uc560\ub2c8 \ud3b8\uc131\ud45c", None))
        self.btn_download.setText(QCoreApplication.translate("MainWindow", u"\ub2e4\uc6b4\ub85c\ub4dc \uad00\ub9ac", None))
        self.btn_search.setText(QCoreApplication.translate("MainWindow", u"\uc791\ud488 \uac80\uc0c9", None))
        self.btn_update.setText(QCoreApplication.translate("MainWindow", u"\ucd5c\uc2e0 \uc790\ub9c9", None))
        self.btn_log.setText(QCoreApplication.translate("MainWindow", u"\ub85c\uadf8", None))
        self.btn_exit.setText(QCoreApplication.translate("MainWindow", u"\uae43\ud5c8\ube0c", None))
        self.toggleLeftBox.setText(QCoreApplication.translate("MainWindow", u"\uc790\ub9c9 \uc815\ubcf4", None))
        self.extraLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt;\">\uc790\ub9c9 \uc815\ubcf4</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.extraCloseColumnBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Close left box", None))
#endif // QT_CONFIG(tooltip)
        self.extraCloseColumnBtn.setText("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:28pt; font-weight:600;\">\uc790\ub9c9</span></p></body></html>", None))
        self.label_date.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\" style=\"line-height:0.6;\"><span style=\" font-size:16pt; \">2024. 10. 02. ~ \ubc29\uc601\uc911</span></p>\n"
"<p align=\"center\"><span style=\" font-size:16pt;\">\ub9e4\uc8fc (\uc218) \uc624\uc804 00:00</span>\n"
"</p></body></html>", None))
        self.left_downloadButton.setText(QCoreApplication.translate("MainWindow", u"\uc989\uc2dc \uc790\ub9c9 \ub2e4\uc6b4\ub85c\ub4dc", None))
        self.left_addQueue.setText(QCoreApplication.translate("MainWindow", u"\uc791\ud488 \uc990\uaca8\ucc3e\uae30\uc5d0 \ucd94\uac00", None))
        self.left_website.setText(QCoreApplication.translate("MainWindow", u"\uc560\ub2c8 \uc6f9\uc0ac\uc774\ud2b8", None))
        self.left_more.setText(QCoreApplication.translate("MainWindow", u"\ub354 \ubcf4\uae30", None))
        self.left_progressName.setText(QCoreApplication.translate("MainWindow", u"<\uc560\ub2c8\uba54\uc774\uc158> \ub2e4\uc6b4\ub85c\ub4dc\uc911...", None))
        self.titleRightInfo.setText(QCoreApplication.translate("MainWindow", u"Temp Title", None))
#if QT_CONFIG(tooltip)
        self.horizontalSlider_2.setToolTip(QCoreApplication.translate("MainWindow", u"\ubc1d\uae30 \uc870\uc808", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.settingsTopBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Settings", None))
#endif // QT_CONFIG(tooltip)
        self.settingsTopBtn.setText("")
#if QT_CONFIG(tooltip)
        self.minimizeAppBtn.setToolTip(QCoreApplication.translate("MainWindow", u"\ucd5c\uc18c\ud654", None))
#endif // QT_CONFIG(tooltip)
        self.minimizeAppBtn.setText("")
#if QT_CONFIG(tooltip)
        self.maximizeRestoreAppBtn.setToolTip(QCoreApplication.translate("MainWindow", u"\ucd5c\ub300\ud654", None))
#endif // QT_CONFIG(tooltip)
        self.maximizeRestoreAppBtn.setText("")
#if QT_CONFIG(tooltip)
        self.closeAppBtn.setToolTip(QCoreApplication.translate("MainWindow", u"\ucc3d \ub2eb\uae30", None))
#endif // QT_CONFIG(tooltip)
        self.closeAppBtn.setText("")
        self.pushButton_sun.setText(QCoreApplication.translate("MainWindow", u"\u65e5", None))
        self.pushButton_mon.setText(QCoreApplication.translate("MainWindow", u"\u6708", None))
        self.pushButton_tue.setText(QCoreApplication.translate("MainWindow", u"\u706b", None))
        self.pushButton_wed.setText(QCoreApplication.translate("MainWindow", u"\u6c34", None))
        self.pushButton_thu.setText(QCoreApplication.translate("MainWindow", u"\u6728", None))
        self.pushButton_fri.setText(QCoreApplication.translate("MainWindow", u"\uf90a", None))
        self.pushButton_sat.setText(QCoreApplication.translate("MainWindow", u"\u571f", None))
        self.pushButton_extra.setText(QCoreApplication.translate("MainWindow", u"\u5916", None))
        self.pushButton_new.setText(QCoreApplication.translate("MainWindow", u"\u65b0", None))
        ___qtablewidgetitem = self.anime_time_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"\uc2dc\uac04", None));
        ___qtablewidgetitem1 = self.anime_time_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"\uc81c\ubaa9", None));
        ___qtablewidgetitem2 = self.anime_time_table.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"ID", None));
        ___qtablewidgetitem3 = self.anime_time_table.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"\uc7a5\ub974", None));
        ___qtablewidgetitem4 = self.anime_time_table.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"\uc2dc\uc791\uc77c", None));
        ___qtablewidgetitem5 = self.anime_time_table.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"\uc790\ub9c9\ub7ec", None));
        ___qtablewidgetitem6 = self.anime_time_table.horizontalHeaderItem(6)
        ___qtablewidgetitem6.setText(QCoreApplication.translate("MainWindow", u"\uacf5\uc2dd\uc0ac\uc774\ud2b8", None));
        self.labelBoxBlenderInstalation.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt;\">\uc790\ub9c9 \ub2e4\uc6b4\ub85c\ub4dc \uacbd\ub85c</span></p></body></html>", None))
        self.labelVersion_3.setText(QCoreApplication.translate("MainWindow", u"\ud574\ub2f9 \uacbd\ub85c\ub97c \ud1b5\ud574 \uc790\ub9c9\uc774 \ub2e4\uc6b4\ub85c\ub4dc \ub429\ub2c8\ub2e4.", None))
        self.yml_downloadPath.setText("")
        self.yml_downloadPath.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Type here", None))
        self.scheduler_folder.setText(QCoreApplication.translate("MainWindow", u"\ub2e4\uc6b4 \ud3f4\ub354 \uc5f4\uae30", None))
        self.ym_openfileButton.setText(QCoreApplication.translate("MainWindow", u"\uacbd\ub85c \ubcc0\uacbd", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt;\">\uc791\ud488 \uc990\uaca8\ucc3e\uae30 \uad00\ub9ac</span></p></body></html>", None))
        self.scheduler_checkBox.setText(QCoreApplication.translate("MainWindow", u"\uc8fc\uae30\uc801\uc73c\ub85c \ubc18\ubcf5 \uc2e4\ud589", None))
        self.scheduler_comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"10\ubd84 \ub9c8\ub2e4", None))
        self.scheduler_comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"30\ubd84 \ub9c8\ub2e4", None))
        self.scheduler_comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"1\uc2dc\uac04 \ub9c8\ub2e4", None))
        self.scheduler_comboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"3\uc2dc\uac04 \ub9c8\ub2e4", None))
        self.scheduler_comboBox.setItemText(4, QCoreApplication.translate("MainWindow", u"6\uc2dc\uac04 \ub9c8\ub2e4", None))
        self.scheduler_comboBox.setItemText(5, QCoreApplication.translate("MainWindow", u"12\uc2dc\uac04 \ub9c8\ub2e4", None))
        self.scheduler_comboBox.setItemText(6, QCoreApplication.translate("MainWindow", u"24\uc2dc\uac04 \ub9c8\ub2e4", None))
        self.scheduler_comboBox.setItemText(7, QCoreApplication.translate("MainWindow", u"\ubc18\ubcf5 \uc5c6\uc74c", None))

        self.yml_save_button.setText(QCoreApplication.translate("MainWindow", u"\uc800\uc7a5 \ud558\uae30", None))
        self.yml_remove_row.setText(QCoreApplication.translate("MainWindow", u"\uc120\ud0dd\ud589\uc0ad\uc81c", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"  Anime.yml", None))
        self.yml_open_button.setText(QCoreApplication.translate("MainWindow", u"yml \uc5f4\uae30", None))
        self.yml_reset_button.setText(QCoreApplication.translate("MainWindow", u"\ubaa8\ub4e0\ud589\uc0ad\uc81c", None))
        self.scheduler_button.setText(QCoreApplication.translate("MainWindow", u"\ub2e4\uc6b4\ub85c\ub4dc \uc2dc\uc791", None))
        self.yml_reload_button.setText(QCoreApplication.translate("MainWindow", u"\ub9ac\ub85c\ub4dc", None))
        ___qtablewidgetitem7 = self.scheduler_table.horizontalHeaderItem(0)
        ___qtablewidgetitem7.setText(QCoreApplication.translate("MainWindow", u"ID", None));
        ___qtablewidgetitem8 = self.scheduler_table.horizontalHeaderItem(1)
        ___qtablewidgetitem8.setText(QCoreApplication.translate("MainWindow", u"\uc81c\ubaa9(\ud3f4\ub354\uc774\ub984)", None));
        ___qtablewidgetitem9 = self.scheduler_table.verticalHeaderItem(0)
        ___qtablewidgetitem9.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem10 = self.scheduler_table.verticalHeaderItem(1)
        ___qtablewidgetitem10.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem11 = self.scheduler_table.verticalHeaderItem(2)
        ___qtablewidgetitem11.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem12 = self.scheduler_table.verticalHeaderItem(3)
        ___qtablewidgetitem12.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem13 = self.scheduler_table.verticalHeaderItem(4)
        ___qtablewidgetitem13.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem14 = self.scheduler_table.verticalHeaderItem(5)
        ___qtablewidgetitem14.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem15 = self.scheduler_table.verticalHeaderItem(6)
        ___qtablewidgetitem15.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem16 = self.scheduler_table.verticalHeaderItem(7)
        ___qtablewidgetitem16.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem17 = self.scheduler_table.verticalHeaderItem(8)
        ___qtablewidgetitem17.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem18 = self.scheduler_table.verticalHeaderItem(9)
        ___qtablewidgetitem18.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem19 = self.scheduler_table.verticalHeaderItem(10)
        ___qtablewidgetitem19.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem20 = self.scheduler_table.verticalHeaderItem(11)
        ___qtablewidgetitem20.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem21 = self.scheduler_table.verticalHeaderItem(12)
        ___qtablewidgetitem21.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem22 = self.scheduler_table.verticalHeaderItem(13)
        ___qtablewidgetitem22.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem23 = self.scheduler_table.verticalHeaderItem(14)
        ___qtablewidgetitem23.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        ___qtablewidgetitem24 = self.scheduler_table.verticalHeaderItem(15)
        ___qtablewidgetitem24.setText(QCoreApplication.translate("MainWindow", u"New Row", None));
        self.labelBoxBlenderInstalation_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt;\">\uc560\ub2c8\uba54\uc774\uc158 \uc791\ud488 \uac80\uc0c9</span></p></body></html>", None))
        self.label_total_elements.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p></p></body></html>", None))
        self.search_input.setText("")
        self.search_input.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\uc560\ub2c8\uac80\uc0c9 #\uc7a5\ub974 @\uc81c\uc791\uc790 /\uc644\uacb0 /\ub3c4\uc6c0\ub9d0", None))
        self.search_button.setText(QCoreApplication.translate("MainWindow", u"\uac80\uc0c9", None))
        ___qtablewidgetitem25 = self.anime_search_table.horizontalHeaderItem(0)
        ___qtablewidgetitem25.setText(QCoreApplication.translate("MainWindow", u"\uc2dc\uac04", None));
        ___qtablewidgetitem26 = self.anime_search_table.horizontalHeaderItem(1)
        ___qtablewidgetitem26.setText(QCoreApplication.translate("MainWindow", u"\uc81c\ubaa9", None));
        ___qtablewidgetitem27 = self.anime_search_table.horizontalHeaderItem(2)
        ___qtablewidgetitem27.setText(QCoreApplication.translate("MainWindow", u"ID", None));
        ___qtablewidgetitem28 = self.anime_search_table.horizontalHeaderItem(3)
        ___qtablewidgetitem28.setText(QCoreApplication.translate("MainWindow", u"\uc7a5\ub974", None));
        ___qtablewidgetitem29 = self.anime_search_table.horizontalHeaderItem(4)
        ___qtablewidgetitem29.setText(QCoreApplication.translate("MainWindow", u"\uc2dc\uc791\uc77c", None));
        ___qtablewidgetitem30 = self.anime_search_table.horizontalHeaderItem(5)
        ___qtablewidgetitem30.setText(QCoreApplication.translate("MainWindow", u"\uc790\ub9c9\ub7ec", None));
        ___qtablewidgetitem31 = self.anime_search_table.horizontalHeaderItem(6)
        ___qtablewidgetitem31.setText(QCoreApplication.translate("MainWindow", u"\uacf5\uc2dd\uc0ac\uc774\ud2b8", None));
        self.labal_recent_title.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt;\">\uc560\ub2c8\uba54\uc774\uc158 \ucd5c\uc2e0 \uc790\ub9c9</span></p></body></html>", None))
        self.label_recemt_total_elements.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><br/></p></body></html>", None))
        ___qtablewidgetitem32 = self.anime_recent_table.horizontalHeaderItem(0)
        ___qtablewidgetitem32.setText(QCoreApplication.translate("MainWindow", u"\uc2dc\uac04", None));
        ___qtablewidgetitem33 = self.anime_recent_table.horizontalHeaderItem(1)
        ___qtablewidgetitem33.setText(QCoreApplication.translate("MainWindow", u"\ud68c\ucc28", None));
        ___qtablewidgetitem34 = self.anime_recent_table.horizontalHeaderItem(2)
        ___qtablewidgetitem34.setText(QCoreApplication.translate("MainWindow", u"\uc81c\ubaa9", None));
        ___qtablewidgetitem35 = self.anime_recent_table.horizontalHeaderItem(3)
        ___qtablewidgetitem35.setText(QCoreApplication.translate("MainWindow", u"\uc81c\uc791\uc790", None));
        ___qtablewidgetitem36 = self.anime_recent_table.horizontalHeaderItem(4)
        ___qtablewidgetitem36.setText(QCoreApplication.translate("MainWindow", u"ID", None));
        ___qtablewidgetitem37 = self.anime_recent_table.horizontalHeaderItem(5)
        ___qtablewidgetitem37.setText(QCoreApplication.translate("MainWindow", u"\ub9c1\ud06c", None));
        ___qtablewidgetitem38 = self.log_timestamp.horizontalHeaderItem(0)
        ___qtablewidgetitem38.setText(QCoreApplication.translate("MainWindow", u"TimeStamp", None));
        ___qtablewidgetitem39 = self.log_timestamp.horizontalHeaderItem(1)
        ___qtablewidgetitem39.setText(QCoreApplication.translate("MainWindow", u"Category", None));
        ___qtablewidgetitem40 = self.log_timestamp.horizontalHeaderItem(2)
        ___qtablewidgetitem40.setText(QCoreApplication.translate("MainWindow", u"Message", None));
        self.btn_message.setText(QCoreApplication.translate("MainWindow", u"Message", None))
        self.btn_print.setText(QCoreApplication.translate("MainWindow", u"Print", None))
        self.btn_logout.setText(QCoreApplication.translate("MainWindow", u"Logout", None))
        self.creditsLabel.setText(QCoreApplication.translate("MainWindow", u"KUDONG", None))
        self.version.setText(QCoreApplication.translate("MainWindow", u"v1.5.2", None))
    # retranslateUi

