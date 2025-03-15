# ///////////////////////////////////////////////////////////////
#
# BY: KUDONG
# PROJECT: SMI-AUTO-DOWNLOADER
# Version: 1.4.0
#
# ///////////////////////////////////////////////////////////////

# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////

import sys
import os
import webbrowser
import threading
import natsort
from datetime import datetime
from functools import partial

from modules import *
from widgets import *
from kudong import *
os.environ["QT_FONT_DPI"] = "96" # HiDPI 기본값 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////

widgets = None

animeWeeklist = []
animeWeekIdx = 0
selectedAnime_LeftBox = None

clickedRemoveRow = -1;
isScheduler_button_clicked = False;
isScheduler_mode = False; 
download_thread = None

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

        # 트레이 설정
        self.setWindowIcon(QIcon("icon.ico"))

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.ico"))  # 트레이 아이콘으로 사용할 이미지 파일의 경로
        tray_menu = QMenu(self)

        restore_action = QAction("열기", self)
        restore_action.triggered.connect(self.showNormal)
        tray_menu.addAction(restore_action)

        def closeApp():
            set_global_quitSignal(True)
            QApplication.instance().quit()

        quit_action = QAction("종료", self)
        quit_action.triggered.connect(closeApp)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        # 어플리케이션 종료시
        def minimize_to_tray():
            window.hide()
            window.tray_icon.showMessage(
                "SMI-AUTO-DOWNLOADER",
                "해당 어플리케이션은 시스템 트레이에 최소화 되었습니다.",
                QIcon("icon.ico"),
                2000
        )
            
        def on_tray_icon_activated(reason):
            if reason == QSystemTrayIcon.Trigger:
                self.showNormal()
        
        widgets.closeAppBtn.clicked.connect(minimize_to_tray)
        self.tray_icon.activated.connect(on_tray_icon_activated) 

        # 토글 메뉴
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # 내부 UI 셋팅
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        self.smiWorker = None

        # 1. Schedule Page
        # //////////////////////////////////////////////////////////////////

        def setWeekendButtonStyle(idx,sheet):
            if idx == 0:
                widgets.pushButton_sun.setStyleSheet(sheet);
            elif idx == 1:
                widgets.pushButton_mon.setStyleSheet(sheet);
            elif idx == 2:
                widgets.pushButton_tue.setStyleSheet(sheet);
            elif idx == 3:
                widgets.pushButton_wed.setStyleSheet(sheet);
            elif idx == 4:
                widgets.pushButton_thu.setStyleSheet(sheet);
            elif idx == 5:
                widgets.pushButton_fri.setStyleSheet(sheet);
            elif idx == 6:
                widgets.pushButton_sat.setStyleSheet(sheet);
            elif idx == 7:
                widgets.pushButton_extra.setStyleSheet(sheet);
            elif idx == 8:
                widgets.pushButton_new.setStyleSheet(sheet);


        def clickWeekendButton(idx):
            global animeWeeklist,animeWeekIdx
            #print("idx 클릭 "+ str(idx))
            count = 0
            beforeSheet = "background-color: rgb(52, 59, 72); font-size: 32px; font-weight: bold;"
            setWeekendButtonStyle(animeWeekIdx, beforeSheet)
            afterSheet = "background-color: rgb(156, 179, 199); font-size: 32px; font-weight: bold; color: rgb(255, 255, 255);"
            setWeekendButtonStyle(idx, afterSheet)
            animeWeekIdx = idx

            widgets.anime_time_table.clearContents()
            animeWeeklist = requestAnimeWeekInfo(idx)

            if animeWeeklist is None:
                reply = QMessageBox.information(self,'SMI-DOWNLOADER','현재 애니시아 서버와 연결할수 없습니다!')
                return

            widgets.anime_time_table.setRowCount(len(animeWeeklist))
            widgets.anime_time_table.setColumnCount(7)

            widgets.anime_time_table.setFocusPolicy(Qt.NoFocus)

            font = QFont()
            font.setPointSize(25)
            font.setBold(QFont.Bold)

            for k in animeWeeklist:
                prefix = ""
                
                if idx < 7:
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

                widgets.anime_time_table.setItem(count,0,item);
                widgets.anime_time_table.setItem(count,1,QTableWidgetItem(prefix + k.subject));
                widgets.anime_time_table.setItem(count,2,QTableWidgetItem(str(k.animeNo)));
                widgets.anime_time_table.setItem(count,3,QTableWidgetItem(k.genres));
                
                widgets.anime_time_table.setItem(count,4,QTableWidgetItem(k.startDate));
                widgets.anime_time_table.setItem(count,5,QTableWidgetItem(str(k.captionCount)));
                widgets.anime_time_table.setItem(count,6,QTableWidgetItem(k.website));  
                count += 1     

            for row in range(widgets.anime_time_table.rowCount()):
                for column in range(widgets.anime_time_table.columnCount()):
                    item = widgets.anime_time_table.item(row, column)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable) 

            widgets.anime_time_table.horizontalScrollBar().setValue(
                    widgets.log_console.horizontalScrollBar().minimum()
            )

        widgets.pushButton_sun.clicked.connect(partial(clickWeekendButton,0))
        widgets.pushButton_mon.clicked.connect(partial(clickWeekendButton,1))
        widgets.pushButton_tue.clicked.connect(partial(clickWeekendButton,2))
        widgets.pushButton_wed.clicked.connect(partial(clickWeekendButton,3))
        widgets.pushButton_thu.clicked.connect(partial(clickWeekendButton,4))
        widgets.pushButton_fri.clicked.connect(partial(clickWeekendButton,5))
        widgets.pushButton_sat.clicked.connect(partial(clickWeekendButton,6))
        widgets.pushButton_extra.clicked.connect(partial(clickWeekendButton,7))
        widgets.pushButton_new.clicked.connect(partial(clickWeekendButton,8))

        def open_url(url):
            webbrowser.open(url)

        #편성표에서 클릭 했을때 
        def on_cell_clicked(row,column):
            global selectedAnime_LeftBox
            #print(f"Row {row} {column}")

            item = widgets.anime_time_table.item(row, 1)
            if item is not None:
                anime = animeWeeklist[row]

                #if(selectedAnime_LeftBox is not anime):
                #    widgets.left_progressBar.hide()
                #    widgets.left_progressBar.setValue(0);
                    
                selectedAnime_LeftBox = anime

                #print("Item data:", anime.subject)

                widgets.label.setText("<html><head/><body><p align='center'><span style=' font-size:20pt; font-weight:bold;'>"+anime.subject+"</span></p></body></html>");
                widgets.label.setWordWrap(True)

                startDate = None;
                endDate = None;
                currentDate = datetime.now();

                if anime.startDate != '':

                    try:
                        startDate = datetime.strptime(anime.startDate, '%Y-%m-%d')
                    except Exception as e:  
                        startDate = None;

                    try:
                        endDate = datetime.strptime(anime.endDate, '%Y-%m-%d')
                    except Exception as e:  
                        endDate = None;  
                    
                    week_Ko = None;

                    if anime.weekNo == 0:
                        week_Ko = "일"
                    elif anime.weekNo == 1:  
                        week_Ko = "월"
                    elif anime.weekNo == 2:  
                        week_Ko = "화"
                    elif anime.weekNo == 3:  
                        week_Ko = "수"
                    elif anime.weekNo == 4:  
                        week_Ko = "목"
                    elif anime.weekNo == 5:  
                        week_Ko = "금"
                    elif anime.weekNo == 6:  
                        week_Ko = "토"

                    if anime.status == 'ON':
                        if startDate is not None and currentDate <= startDate :
                            widgets.label_date.setText("<html><head/><body><p align='center'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+"</span></p></body></html>");
                            widgets.label_date.setWordWrap(True)
                            widgets.label_date.show()
                        else:
                            if endDate is not None:
                                if startDate == endDate:
                                    widgets.label_date.setText("<html><head/><body><p align='center'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+"</span></p></body></html>");
                                    widgets.label_date.setWordWrap(True)
                                    widgets.label_date.show()
                                else:
                                    time_obj = datetime.strptime(anime.time, "%H:%M")
                                    formatted_time = time_obj.strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
                                    widgets.label_date.setText("<html><head/><body><p align='center' style='line-height:0.6;'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+" ~ "+endDate.strftime("%Y. %m. %d.")+"</span></p><p align='center'><span style=' font-size:16pt;'>"+"매주 ("+week_Ko +") "+formatted_time+"</span></p></body></html>");
                                    widgets.label_date.setWordWrap(True)
                                    widgets.label_date.show()
                            else:
                                try:
                                    time_obj = datetime.strptime(anime.time, "%H:%M") # 2025-99-99 가 넘어오면 예외처리
                                    formatted_time = time_obj.strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
                                    widgets.label_date.setText("<html><head/><body><p align='center' style='line-height:0.6;'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d. ~ 방영중")+"</span></p><p align='center'><span style=' font-size:16pt;'>"+"매주 ("+week_Ko +") "+formatted_time+"</span></p></body></html>");
                                    widgets.label_date.setWordWrap(True)
                                    widgets.label_date.show()
                                except Exception as e:  
                                    try:
                                        widgets.label_date.setText("<html><head/><body><p align='center'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+"</span></p></body></html>");
                                        widgets.label_date.setWordWrap(True)
                                        widgets.label_date.show()
                                    except Exception as e2: 
                                        widgets.label_date.hide()        
                    else:
                        widgets.label_date.setText("<html><head/><body><p align='center' style='line-height:0.6;'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d. ~ 방영중")+"</span></p><p align='center'><span style=' font-size:16pt;'>결방</span></p></body></html>");
                        widgets.label_date.setWordWrap(True)
                        widgets.label_date.show()
                else:
                    widgets.label_date.hide() 

                subs = requestAnimeSubsInfo(anime)

                spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

                layout = widgets.extraCenter.layout()

                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()

                for k in subs:
                    name = k.name
                    episode = k.episode
                    website = k.website
                    updDtStr = k.updDt

                    updDt = datetime.strptime(updDtStr, "%Y-%m-%dT%H:%M:%S")
                    currentDt = datetime.now();

                    time_diff = currentDt - updDt
                    time_diff_str = ""
                    #print("time_diff = " + time_diff)

                    time_diff_prefix = " ("
                    total_sec = time_diff.total_seconds();

                    if total_sec < 60: # 60초 이내
                        time_diff_str = time_diff_prefix + str(total_sec) + "초 전)"
                    elif total_sec < 3600: # 60분 이내
                        time_diff_str = time_diff_prefix + str(round(total_sec/60)) + "분 전)"
                    elif total_sec < 86400: # 24시간 이내
                        time_diff_str = time_diff_prefix + str(round(total_sec/3600)) + "시간 전)"
                    elif total_sec < 2592000: #30일 이내
                        time_diff_str = time_diff_prefix + str(round(total_sec/86400)) + "일 전)"
                    else: 
                        time_diff_str = time_diff_prefix + updDtStr[:updDtStr.rfind("T")] +")"

                    if(website == ""):
                        button = QPushButton("준비중 "+name+ " "+updDtStr[:updDtStr.rfind("T")])
                    else:
                        button = QPushButton(episode+"화 "+name + time_diff_str)
                        button.clicked.connect(partial(open_url,website))

                    button.setMinimumSize(0, 60)
                    button.setStyleSheet("font-size: 20px; color: rgb(0, 0, 0);")
                    layout.addWidget(button)

                layout.addItem(spacer)
                widgets.extraCenter.setLayout(layout);
                UIFunctions.openLeftBox(self, True)

        #leftToggleButton

        def addQueue():
            if(selectedAnime_LeftBox is not None):
                idx = -1;

                list = []

                for row in range(widgets.scheduler_table.rowCount()):
                    id = widgets.scheduler_table.item(row, 0)
                    if(id is None):
                       break
                    list.append(id.text())

                #print("리스트 출력" + str(list))

                if(str(selectedAnime_LeftBox.animeNo) in list):
                    QMessageBox.information(self,'SMI-DOWNLOADER','이미 다운로드 대기열에 존재하는 작품입니다!')
                    return     
                
                for row in range(widgets.scheduler_table.rowCount()):
                    id = widgets.scheduler_table.item(row, 0)
                    if(id is None):
                        idx = row
                        break

                widgets.scheduler_table.setItem(idx,0,QTableWidgetItem(str(selectedAnime_LeftBox.animeNo)));
                widgets.scheduler_table.setItem(idx,1,QTableWidgetItem(selectedAnime_LeftBox.subject));  

                #onYmlsaveButtonClicked()

        def callback_test(progress,count,output = "None",isFinished = False):
            if self.smiWorker is not None:
                self.smiWorker.wait()
            self.smiWorker = WorkerThread(self)
            self.smiWorker.setValue(progress,count,output,isFinished)
            self.smiWorker.start()

        def directDownload():
            global download_thread
            if(selectedAnime_LeftBox is not None):
                #widgets.left_progressBar.show()

                widgets.log_console.setPlainText("")
                widgets.log_console.verticalScrollBar().setValue(
                    widgets.log_console.verticalScrollBar().maximum()
                )

                widgets.left_progressName.setText("곧 다운로드가 시작됩니다...")
                widgets.left_progressName.setWordWrap(True)
                
                if lock_Scheduler() == True:
                    widgets.left_progressBar.setValue(0)
                    download_thread = threading.Thread(target= lambda: requestAnimeSMI_3(selectedAnime_LeftBox,callback_test))
                    download_thread.start()
                else:
                    QMessageBox.information( 
                    window, 
                    "SMI-DOWNLOADER", 
                    "다른 작업이 먼저 수행중입니다....");
                    return

        def clickMore():
            if(selectedAnime_LeftBox is not None):
                open_url("https://anissia.net/anime?animeNo=" + str(selectedAnime_LeftBox.animeNo))

        def clickMore2():
            if(selectedAnime_LeftBox is not None):
                open_url(selectedAnime_LeftBox.website)

        widgets.left_downloadButton.clicked.connect(directDownload)
        widgets.left_addQueue.clicked.connect(addQueue)
        widgets.left_more.clicked.connect(clickMore)
        widgets.left_website.clicked.connect(clickMore2)

        widgets.left_progressBar.setMinimum(0);
        widgets.left_progressBar.setMaximum(100);
        widgets.left_progressBar.setValue(0);
        #widgets.left_progressBar.hide()

        widgets.left_progressName.setText("현재 대기열에 작업이 없습니다.")
        widgets.left_progressName.setWordWrap(True)

        idle_text = "편성표에서 원하는 자막을 선택하세요"
        widgets.label.setText("<html><head/><body><p align='center'><span style=' font-size:20pt; font-weight:600;'>"+idle_text+"</span></p></body></html>");
        widgets.label.setWordWrap(True)

        widgets.label_date.hide()
        
        # QTableWidget 편성표 테이블 설정

        widgets.anime_time_table.setSelectionBehavior(QTableWidget.SelectRows)
        widgets.anime_time_table.verticalHeader().setDefaultSectionSize(60)
        widgets.anime_time_table.verticalHeader().setVisible(False)
        widgets.anime_time_table.verticalHeader().setSectionsMovable(False)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(3,QHeaderView.ResizeToContents)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(4,QHeaderView.ResizeToContents)
        widgets.anime_time_table.horizontalHeader().setSectionResizeMode(5,QHeaderView.ResizeToContents)
        widgets.anime_time_table.cellClicked.connect(on_cell_clicked)

        now = datetime.now()
        weekday_index = now.weekday()

        if weekday_index == 6:
            weekday_index = 0
        else:
            weekday_index += 1

        clickWeekendButton(weekday_index);

        # 2. Download_Page
        # ///////////////////////////////////////////////////////////////
        widgets.scheduler_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # 다운로드 경로 선택시
        def on_openfile_clicked():
            #fileDir = QFileDialog.getOpenFileName(self);
            #widgets.yml_downloadPath.setText(outpath)
            fileDir = QFileDialog.getExistingDirectory(self,'폴더선택','')
            if(fileDir != ""):
                widgets.yml_downloadPath.setText(fileDir)
                set_global_outpath(fileDir)

                with open('anime.yml', 'r', encoding='utf-8') as file:
                    data = yaml.safe_load(file)

                    #print(data)

                    data['download_path'] = fileDir

                with open('anime.yml', 'w', encoding='utf-8') as file:
                    yaml.safe_dump(data, file, allow_unicode=True)

                widgets.yml_content.setPlainText(
                    "anime_list: '" + data['anime_list'] + "'\n"  + 
                    "download_path: '" + data['download_path'] + "'"
                );
        
        #outpath

        with open('anime.yml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

        outpath = os.path.abspath('.') + "/downloads"

        if not os.path.exists(outpath):
            os.makedirs(outpath)

        if(data['download_path'] != ""):
            outpath = data['download_path']
        else:
            data['download_path'] = outpath
            with open('anime.yml', 'w', encoding='utf-8') as file:
                yaml.safe_dump(data, file, allow_unicode=True)

        set_global_outpath(outpath)   
        widgets.yml_downloadPath.setText(outpath)
        widgets.ym_openfileButton.clicked.connect(on_openfile_clicked)

        widgets.yml_content.setPlainText(
            "anime_list: '" + data['anime_list'] + "'\n"  + 
            "download_path: '" + data['download_path'] + "'"
        );
        widgets.yml_content.setReadOnly(True)

        animelist = json.loads(data['anime_list'])

        count = 0
        for k in animelist:
            widgets.scheduler_table.setItem(count,0,QTableWidgetItem(str(k['AnimeNo'])));
            widgets.scheduler_table.setItem(count,1,QTableWidgetItem(k['Anime']));
            count += 1

        widgets.scheduler_table.horizontalHeader().setVisible(True)
        widgets.scheduler_table.verticalHeader().setSectionsMovable(False)

        def onYmlsaveButtonClicked():
            temp = ""

            save_dict = {}

            for row in range(widgets.scheduler_table.rowCount()):
                id = widgets.scheduler_table.item(row, 0)
                anime = widgets.scheduler_table.item(row, 1)
                if(id is None):
                    continue;
                save_dict[id.text()] = anime.text();

            for key,value in save_dict.items():
                id = key
                anime = value
                #print(str(row) + " " + str(widgets.scheduler_table.rowCount()))
                temp += "{ \"Anime\":\""+anime+"\", \"AnimeNo\":\""+str(id)+"\" }"
                temp += ",\n"

            temp = temp[:-2] +"\n"
            temp = '[\n' +temp + ']'

            with open('anime.yml', 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                data['anime_list'] = temp

            with open('anime.yml', 'w', encoding='utf-8') as file:
                yaml.safe_dump(data, file, allow_unicode=True)

            widgets.yml_content.setPlainText(
                "anime_list: '" + data['anime_list'] + "'\n"  + 
                "download_path: '" + data['download_path'] + "'"
            );

        def onYmlresetButtonClicked():
            for row in range(widgets.scheduler_table.rowCount()):
                for column in range(widgets.scheduler_table.columnCount()):
                    item = widgets.scheduler_table.item(row, column)

        def onYmlopenButtonClicked():
            webbrowser.open(os.path.abspath('.') + "/anime.yml")             

        def onYmlremoveRowClicked(row,column):
            global clickedRemoveRow
            clickedRemoveRow = row

        def onYmlremoveRowButtonClicked():
            widgets.scheduler_table.removeRow(clickedRemoveRow)
            rowCount = widgets.scheduler_table.rowCount()
            widgets.scheduler_table.insertRow(rowCount)

        def onYmlreloadButtonClicked():

            with open('anime.yml', 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)

            widgets.yml_content.setPlainText(
                "anime_list: '" + data['anime_list'] + "'\n"  + 
                "download_path: '" + data['download_path'] + "'"
            );

            widgets.yml_downloadPath.setText(data['download_path'])
            set_global_outpath(data['download_path'])

            #테이블 모든 데이터 삭제
            widgets.scheduler_table.clearContents()

            animelist = json.loads(data['anime_list'])

            count = 0
            for k in animelist:
                widgets.scheduler_table.setItem(count,0,QTableWidgetItem(str(k['AnimeNo'])));
                widgets.scheduler_table.setItem(count,1,QTableWidgetItem(k['Anime']));
                count += 1

        def onYmlresetButtonClicked():
            widgets.scheduler_table.clearContents()
            # widgets.yml_content.setPlainText(
            #     "anime_list: '[\n\n]'\n"  + 
            #     "download_path: '" + os.path.abspath('.') + "'"
            # );

        def onDownloadFolderButtonClicked():
            webbrowser.open(get_global_outpath())

        widgets.yml_save_button.clicked.connect(onYmlsaveButtonClicked)
        widgets.yml_reset_button.clicked.connect(onYmlresetButtonClicked)
        widgets.yml_open_button.clicked.connect(onYmlopenButtonClicked)
        widgets.yml_reload_button.clicked.connect(onYmlreloadButtonClicked)
        widgets.yml_reset_button.clicked.connect(onYmlresetButtonClicked)
        widgets.yml_remove_row.clicked.connect(onYmlremoveRowButtonClicked)

        widgets.scheduler_folder.clicked.connect(onDownloadFolderButtonClicked)
        widgets.scheduler_table.cellClicked.connect(onYmlremoveRowClicked)
        
        # 스케줄러 체크박스 클릭시
        def scheduler_checkbox_changed(state):
            if state == 2: #checked
                widgets.scheduler_comboBox.setEnabled(True)
                widgets.scheduler_button.setText("스케줄러 시작")
            else:
                widgets.scheduler_comboBox.setEnabled(False)
                widgets.scheduler_button.setText("다운로드 시작")

        # 스케줄러 시작 버튼 클릭시
        def scheduler_button_clicked():
            global isScheduler_button_clicked, isScheduler_mode
            if isScheduler_button_clicked == False: # 시작 로직

                if widgets.scheduler_checkBox.isChecked():
                    widgets.left_progressName.setText("곧 스케쥴러가 시작됩니다...")
                    widgets.left_progressName.setWordWrap(True)
                else:
                    widgets.left_progressName.setText("곧 다운로드가 시작됩니다...")
                    widgets.left_progressName.setWordWrap(True)

                if lock_Scheduler() == True:
                    thread = threading.Thread(target= lambda: requestMultipleAnimeSMI(callback_test))
                    thread.start()
                else:
                    QMessageBox.information( 
                    window, 
                    "SMI-DOWNLOADER", 
                    "다른 작업이 먼저 수행중입니다....");
                    return

                afterSheet = "background-color: rgb(156, 179, 199); color: rgb(255, 255, 255);"
                widgets.scheduler_button.setStyleSheet(afterSheet)

                widgets.scheduler_checkBox.setEnabled(False)

                if widgets.scheduler_comboBox.isEnabled():
                    widgets.scheduler_button.setText("스케줄러 중지")
                    isScheduler_mode = True;
                else:
                    widgets.scheduler_button.setText("다운로드 중지")
                    isScheduler_mode = False;
                
                widgets.scheduler_comboBox.setEnabled(False)
                isScheduler_button_clicked = True

                if widgets.scheduler_checkBox.isChecked(): # 반복 옵션이 체크 되어있었다면
                    idx = widgets.scheduler_comboBox.currentIndex()

                    min = 1000 * 60
                    hour = min * 60
                    day = hour * 24

                    if idx == 0: #10분마다
                        self.timer.start(10 * min)
                    elif idx == 1: #30분마다
                        self.timer.start(30 * min)
                    elif idx == 2: #1시간마다
                        self.timer.start(hour)
                    elif idx == 2: #3시간마다
                        self.timer.start(3 * hour)
                    elif idx == 2: #6시간마다
                        self.timer.start(6 * hour)
                    elif idx == 2: #12시간마다
                        self.timer.start(12 * hour)
                    elif idx == 2: #24시간마다
                        self.timer.start(day)
                        
            else: # 중지 로직
                beforeSheet = "background-color: rgb(52, 59, 72);"
                widgets.scheduler_button.setStyleSheet(beforeSheet)
                
                widgets.scheduler_checkBox.setEnabled(True)

                if isScheduler_mode == True:
                    widgets.scheduler_button.setText("스케줄러 시작") 
                    widgets.scheduler_comboBox.setEnabled(True)
                    self.timer.stop()
                else:
                    widgets.scheduler_button.setText("다운로드 시작")
                    widgets.scheduler_comboBox.setEnabled(False)

                isScheduler_button_clicked = False
                
        widgets.scheduler_comboBox.setEnabled(False)
        widgets.scheduler_comboBox.setStyleSheet("""
            QComboBox:disabled {
                background-color: lightgray;
                color: gray;
            }
        """)

        widgets.scheduler_checkBox.stateChanged.connect(scheduler_checkbox_changed)
        widgets.scheduler_button.clicked.connect(scheduler_button_clicked)

        # 타이머
        def scheduler_update():
            widgets.left_progressName.setText("곧 스케쥴러가 시작됩니다...")
            widgets.left_progressName.setWordWrap(True)
            if lock_Scheduler() == True:
                thread = threading.Thread(target= lambda: requestMultipleAnimeSMI(callback_test))
                thread.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(scheduler_update)

        # 3. Console
        # ///////////////////////////////////////////////////////////////

        #로그 클릭시
        def on_cell_clicked_console(row,column):
            item = widgets.log_timestamp.item(row, 0)
            if item is not None:
                file_name = item.text()
                with open(os.path.abspath('.') + "/log/" + file_name, 'r', encoding='utf-8') as file:
                    text = file.read()
                    widgets.log_console.setPlainText(text)
                    widgets.log_console.verticalScrollBar().setValue(
                        widgets.log_console.verticalScrollBar().minimum()
                    )

        log_file_list = natsort.natsorted(os.listdir(os.path.abspath('.') + "/log"))
        log_file_list.remove("error.log")

        log_size = len(log_file_list)
        if(log_size > 30):
            for i in range(0,log_size - 30):
                file_p = os.path.abspath('.') + "/log/"+log_file_list[i]
                if os.path.isfile(file_p):
                    os.remove(file_p)

        widgets.log_timestamp.clearContents()
        widgets.log_timestamp.setRowCount(len(log_file_list))
        widgets.log_timestamp.setColumnCount(3)

        count = 0
        for f in log_file_list:
            widgets.log_timestamp.setItem(count,0,QTableWidgetItem(f));
            widgets.log_timestamp.setItem(count,1,QTableWidgetItem("download_subtitle"));
            widgets.log_timestamp.setItem(count,2,QTableWidgetItem("다운로드 로그 데이터"));
            count += 1                 

        for row in range(widgets.log_timestamp.rowCount()):
            for column in range(widgets.log_timestamp.columnCount()):
                item = widgets.log_timestamp.item(row, column)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable) 

        widgets.log_timestamp.setSelectionBehavior(QTableWidget.SelectRows)
        widgets.log_timestamp.verticalHeader().setDefaultSectionSize(40)
        widgets.log_timestamp.verticalHeader().setVisible(False)
        widgets.log_timestamp.verticalHeader().setSectionsMovable(False)
        widgets.log_timestamp.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        widgets.log_timestamp.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
        widgets.log_timestamp.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
        widgets.log_timestamp.cellClicked.connect(on_cell_clicked_console)

        widgets.log_timestamp.verticalScrollBar().setValue(
            widgets.log_timestamp.verticalScrollBar().maximum()
        )

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_download.clicked.connect(self.buttonClick)
        widgets.btn_log.clicked.connect(self.buttonClick)
        widgets.btn_exit.clicked.connect(self.buttonClick)

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)

        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)

        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        def onChangeValueOpacity(self):
            value = widgets.horizontalSlider_2.value()
            window.setWindowOpacity(value/100.0)
            #print(value)

        widgets.horizontalSlider_2.setRange(10, 100)
        widgets.horizontalSlider_2.setValue(100)
        widgets.horizontalSlider_2.valueChanged.connect(onChangeValueOpacity)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
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

    @Slot(int, int, str, bool)
    def updateProgressBar(self,progress,count,output,isFinished):
        global isScheduler_button_clicked

        if count == 1 and progress == 0:
            widgets.left_progressBar.setValue(50);
        elif count == 0 and progress == 0: 
            widgets.left_progressBar.setValue(100);
        else:
            widgets.left_progressBar.setValue((progress / count) * 100);
    

        widgets.log_console.setPlainText(get_global_console_output())
        widgets.log_console.verticalScrollBar().setValue(
            widgets.log_console.verticalScrollBar().maximum()
        )

        if not output == "None":
            widgets.left_progressName.setText(output)
            widgets.left_progressName.setWordWrap(True)

        if isFinished == True and isScheduler_mode == False:
            beforeSheet = "background-color: rgb(52, 59, 72);"
            widgets.scheduler_button.setStyleSheet(beforeSheet)
            
            widgets.scheduler_button.setText("다운로드 시작")

            widgets.scheduler_checkBox.setEnabled(True)
            widgets.scheduler_comboBox.setEnabled(False)

            isScheduler_button_clicked = False

        if isFinished == True:
            log_file_list = natsort.natsorted(os.listdir(os.path.abspath('.') + "/log"))
            log_file_list.remove("error.log")

            log_size = len(log_file_list)
            if(log_size > 30):
                for i in range(0,log_size - 30):
                    file_p = os.path.abspath('.') + "/log/"+log_file_list[i]
                    if os.path.isfile(file_p):
                        os.remove(file_p)

            widgets.log_timestamp.clearContents()
            widgets.log_timestamp.setRowCount(len(log_file_list))
            widgets.log_timestamp.setColumnCount(3)

            count = 0
            for f in log_file_list:
                widgets.log_timestamp.setItem(count,0,QTableWidgetItem(f));
                widgets.log_timestamp.setItem(count,1,QTableWidgetItem("download_subtitle"));
                widgets.log_timestamp.setItem(count,2,QTableWidgetItem("다운로드 로그 데이터"));
                count += 1                 

            for row in range(widgets.log_timestamp.rowCount()):
                for column in range(widgets.log_timestamp.columnCount()):
                    item = widgets.log_timestamp.item(row, column)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
            
            widgets.log_timestamp.verticalScrollBar().setValue(
            widgets.log_timestamp.verticalScrollBar().maximum()
            )

        # print("===============================================")
        # print(">콜백함수 진행수 " + str(progress) + "/" + str(count))
        # print(">콜백함수 진행률 " + str((progress / count) + "%")
        # print("===============================================")

    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.anime_schedule)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # 다운로드 설정창
        if btnName == "btn_download":
            widgets.stackedWidget.setCurrentWidget(widgets.download_page)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # 로그 확인 버튼
        if btnName == "btn_log":
            widgets.stackedWidget.setCurrentWidget(widgets.log_page) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU

        if btnName == "btn_exit":
            webbrowser.open("https://github.com/dhku/GUI-for-SMI-Auto-Downloader")

        # 버튼 디버깅
        #print(btn.styleSheet())
        #print(f'Button "{btnName}" pressed!')

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

class WorkerThread(QThread):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def setValue(self,progress,count,output,isFinished):
        self.progress = progress
        self.count = count
        self.output = output
        self.isFinished = isFinished

    def run(self):
        QMetaObject.invokeMethod(self.main_window, "updateProgressBar", Qt.QueuedConnection,Q_ARG(int,self.progress),Q_ARG(int,self.count),Q_ARG(str,self.output),Q_ARG(bool,self.isFinished))


# 진입점
if __name__ == "__main__":

    # HIDPI 값 불러오기
    with open('settings.yml', encoding='UTF8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        os.environ["QT_FONT_DPI"] = str(config['resolution'])

    # 콘솔 로깅
    console_logger_init() # 배포시 활성화

    # UI 인스턴스화
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("WindowsVista"));

    app.setWindowIcon(QIcon("icon.ico"))
    window = MainWindow()
    sys.exit(app.exec_())
