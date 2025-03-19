
from datetime import datetime
from functools import partial
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from kudong import *

clickedRemoveRow = -1;
isScheduler_button_clicked = False;
 
# 2. Download_Page
# ///////////////////////////////////////////////////////////////
class DownloadPage:

    def __init__(self, MainWindow, widgets):
        self.MainWindow = MainWindow
        self.widgets = widgets    

        self.widgets.scheduler_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Fixed)
        self.widgets.scheduler_table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        self.widgets.scheduler_table.setColumnWidth(0, 200)
        self.widgets.scheduler_table.setColumnWidth(1, 400)
        self.widgets.scheduler_table.verticalHeader().setSectionsMovable(False)
        self.widgets.scheduler_table.cellClicked.connect(self.on_scheduler_cell_clicked)
        self.widgets.scheduler_table.setFocusPolicy(Qt.NoFocus)

        self.widgets.yml_save_button.clicked.connect(self.onYmlsaveButtonClicked)
        self.widgets.yml_reset_button.clicked.connect(self.onYmlresetButtonClicked)
        self.widgets.yml_open_button.clicked.connect(self.onYmlopenButtonClicked)
        self.widgets.yml_reload_button.clicked.connect(self.onYmlreloadButtonClicked)
        self.widgets.yml_reset_button.clicked.connect(self.onYmlresetButtonClicked)
        self.widgets.yml_remove_row.clicked.connect(self.onYmlremoveRowButtonClicked)

        common.downloadPage_instance = self # left_toggle_bar에서 Yml save 참조용

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
        self.widgets.yml_downloadPath.setText(outpath)
        self.widgets.yml_downloadPath.setReadOnly(True)
        self.widgets.ym_openfileButton.clicked.connect(self.on_openfile_clicked)

        self.widgets.yml_content.setPlainText(
            "anime_list: '" + data['anime_list'] + "'\n"  + 
            "download_path: '" + data['download_path'] + "'"
        );
        self.widgets.yml_content.setReadOnly(True)

        animelist = json.loads(data['anime_list'])

        count = 0
        for k in animelist:
            self.widgets.scheduler_table.setItem(count,0,QTableWidgetItem(str(k['AnimeNo'])));
            self.widgets.scheduler_table.setItem(count,1,QTableWidgetItem(k['Anime']));
            count += 1

        self.widgets.scheduler_table.horizontalHeader().setVisible(True)
        self.widgets.scheduler_table.verticalHeader().setSectionsMovable(False)

        self.widgets.scheduler_folder.clicked.connect(self.onDownloadFolderButtonClicked)
        self.widgets.scheduler_table.cellClicked.connect(self.onYmlremoveRowClicked)

        self.widgets.scheduler_comboBox.setEnabled(False)
        self.widgets.scheduler_comboBox.setCurrentIndex(7);
        # self.widgets.scheduler_comboBox.setStyleSheet("""
        #     QComboBox:disabled {
        #         background-color: lightgray;
        #         color: gray;
        #     }
        # """)

        self.widgets.scheduler_checkBox.stateChanged.connect(self.scheduler_checkbox_changed)
        self.widgets.scheduler_button.clicked.connect(self.scheduler_button_clicked)

        self.timer = QTimer(self.MainWindow)
        self.timer.timeout.connect(self.scheduler_update)

    #테이블을 클릭했을떄
    def on_scheduler_cell_clicked(self, row, column):
        #print(f"Row {row} {column}")
        item = self.widgets.scheduler_table.item(row, 0) # AnimeNo 가 None이 아닌지 체크
        if item is not None and item.text() != "":
            anime, subs = requestAnimeInfo(item.text());

            selectedAnime_LeftBox = anime # local
            common.selectedAnime_LeftBox = anime # global

            #print("Item data:", anime.subject)

            self.widgets.label.setText("<html><head/><body><p align='center'><span style=' font-size:20pt; font-weight:bold;'>"+anime.subject+"</span></p></body></html>");
            self.widgets.label.setWordWrap(True)

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
                        self.widgets.label_date.setText("<html><head/><body><p align='center'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+"</span></p></body></html>");
                        self.widgets.label_date.setWordWrap(True)
                        self.widgets.label_date.show()
                    else:
                        if endDate is not None:
                            if startDate == endDate:
                                self.widgets.label_date.setText("<html><head/><body><p align='center'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+"</span></p></body></html>");
                                self.widgets.label_date.setWordWrap(True)
                                self.widgets.label_date.show()
                            else:
                                time_obj = datetime.strptime(anime.time, "%H:%M")
                                formatted_time = time_obj.strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
                                self.widgets.label_date.setText("<html><head/><body><p align='center' style='line-height:0.6;'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+" ~ "+endDate.strftime("%Y. %m. %d.")+"</span></p><p align='center'><span style=' font-size:16pt;'>"+"매주 ("+week_Ko +") "+formatted_time+"</span></p></body></html>");
                                self.widgets.label_date.setWordWrap(True)
                                self.widgets.label_date.show()
                        else:
                            try:
                                time_obj = datetime.strptime(anime.time, "%H:%M") # 2025-99-99 가 넘어오면 예외처리
                                formatted_time = time_obj.strftime("%p %I:%M").replace("AM", "오전").replace("PM", "오후")
                                self.widgets.label_date.setText("<html><head/><body><p align='center' style='line-height:0.6;'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d. ~ 방영중")+"</span></p><p align='center'><span style=' font-size:16pt;'>"+"매주 ("+week_Ko +") "+formatted_time+"</span></p></body></html>");
                                self.widgets.label_date.setWordWrap(True)
                                self.widgets.label_date.show()
                            except Exception as e:  
                                try:
                                    self.widgets.label_date.setText("<html><head/><body><p align='center'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+"</span></p></body></html>");
                                    self.widgets.label_date.setWordWrap(True)
                                    self.widgets.label_date.show()
                                except Exception as e2: 
                                    self.widgets.label_date.hide()
                elif anime.status == 'END':
                    self.widgets.label_date.setText("<html><head/><body><p align='center' style='line-height:0.6;'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d.")+" ~ "+endDate.strftime("%Y. %m. %d.")+"</span></p><p align='center'><span style=' font-size:16pt;'>완결</span></p></body></html>");
                    self.widgets.label_date.setWordWrap(True)
                    self.widgets.label_date.show()                              
                else:
                    self.widgets.label_date.setText("<html><head/><body><p align='center' style='line-height:0.6;'><span style=' font-size:16pt; '>"+startDate.strftime("%Y. %m. %d. ~ 방영중")+"</span></p><p align='center'><span style=' font-size:16pt;'>결방</span></p></body></html>");
                    self.widgets.label_date.setWordWrap(True)
                    self.widgets.label_date.show()
            else:
                self.widgets.label_date.hide() 

            spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

            layout = self.widgets.extraCenter.layout()

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
            self.widgets.extraCenter.setLayout(layout);
    
            #UIFunctions.openLeftBox(self, True) 이 로직은 상호 참조 이슈로 main에서 호출하는것으로 대체
            self.MainWindow.openLeftBox() # 대신 이거 사용

    # 다운로드 경로 선택시
    def on_openfile_clicked(self):
        #fileDir = QFileDialog.getOpenFileName(self);
        #self.widgets.yml_downloadPath.setText(outpath)
        fileDir = QFileDialog.getExistingDirectory(self.MainWindow,'폴더선택','')
        if(fileDir != ""):
            self.widgets.yml_downloadPath.setText(fileDir)
            set_global_outpath(fileDir)

            with open('anime.yml', 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)

                #print(data)

                data['download_path'] = fileDir

            with open('anime.yml', 'w', encoding='utf-8') as file:
                yaml.safe_dump(data, file, allow_unicode=True)

            self.widgets.yml_content.setPlainText(
                "anime_list: '" + data['anime_list'] + "'\n"  + 
                "download_path: '" + data['download_path'] + "'"
            );
    
    # Anime.yml에 내용을 저장합니다.
    def onYmlsaveButtonClicked(self):
        temp = ""

        save_dict = {}

        for row in range(self.widgets.scheduler_table.rowCount()):
            id = self.widgets.scheduler_table.item(row, 0)
            anime = self.widgets.scheduler_table.item(row, 1)
            if(id is None or anime is None):
                continue;
            save_dict[id.text()] = anime.text();

        for key,value in save_dict.items():
            id = key
            anime = value
            #print(str(row) + " " + str(self.widgets.scheduler_table.rowCount()))
            temp += "{ \"Anime\":\""+anime+"\", \"AnimeNo\":\""+str(id)+"\" }"
            temp += ",\n"

        temp = temp[:-2] +"\n"
        temp = '[\n' +temp + ']'

        with open('anime.yml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            data['anime_list'] = temp

        with open('anime.yml', 'w', encoding='utf-8') as file:
            yaml.safe_dump(data, file, allow_unicode=True)

        self.widgets.yml_content.setPlainText(
            "anime_list: '" + data['anime_list'] + "'\n"  + 
            "download_path: '" + data['download_path'] + "'"
        );
    
        self.onYmlreloadButtonClicked() # 세이브 후 테이블 리로드

    def onYmlresetButtonClicked(self):
        for row in range(self.widgets.scheduler_table.rowCount()):
            for column in range(self.widgets.scheduler_table.columnCount()):
                item = self.widgets.scheduler_table.item(row, column)

    def onYmlopenButtonClicked(self):
        webbrowser.open(os.path.abspath('.') + "/anime.yml")             

    def onYmlremoveRowClicked(self, row,column):
        global clickedRemoveRow
        clickedRemoveRow = row

    def onYmlremoveRowButtonClicked(self):
        self.widgets.scheduler_table.removeRow(clickedRemoveRow)
        rowCount = self.widgets.scheduler_table.rowCount()
        self.widgets.scheduler_table.insertRow(rowCount)

    def onYmlreloadButtonClicked(self):

        with open('anime.yml', 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

        self.widgets.yml_content.setPlainText(
            "anime_list: '" + data['anime_list'] + "'\n"  + 
            "download_path: '" + data['download_path'] + "'"
        );

        self.widgets.yml_downloadPath.setText(data['download_path'])
        set_global_outpath(data['download_path'])

        #테이블 모든 데이터 삭제
        self.widgets.scheduler_table.clearContents()

        animelist = json.loads(data['anime_list'])

        count = 0
        for k in animelist:
            self.widgets.scheduler_table.setItem(count,0,QTableWidgetItem(str(k['AnimeNo'])));
            self.widgets.scheduler_table.setItem(count,1,QTableWidgetItem(k['Anime']));
            count += 1

    def onYmlresetButtonClicked(self):
        self.widgets.scheduler_table.clearContents()
        # self.widgets.yml_content.setPlainText(
        #     "anime_list: '[\n\n]'\n"  + 
        #     "download_path: '" + os.path.abspath('.') + "'"
        # );

    def onDownloadFolderButtonClicked(self):
        webbrowser.open(get_global_outpath())

    # 스케줄러 체크박스 클릭시
    def scheduler_checkbox_changed(self,state):
        if state == 2: #checked
            self.widgets.scheduler_comboBox.setEnabled(True)
            self.widgets.scheduler_comboBox.setCurrentIndex(0);
            self.widgets.scheduler_button.setText("스케줄러 시작")
        else:
            self.widgets.scheduler_comboBox.setEnabled(False)
            self.widgets.scheduler_comboBox.setCurrentIndex(7);
            self.widgets.scheduler_button.setText("다운로드 시작")

    # 스케줄러 시작 버튼 클릭시
    def scheduler_button_clicked(self):
        global isScheduler_button_clicked
        if isScheduler_button_clicked == False: # 시작 로직

            idx = self.widgets.scheduler_comboBox.currentIndex()

            #"반복 없음"이 스케쥴러 모드에서 버튼 클릭 되었을때 처리
            if self.widgets.scheduler_checkBox.isChecked() and idx == 7: 
                QMessageBox.information( 
                self.MainWindow, 
                "SMI-DOWNLOADER", 
                "반복 없음은 선택할수 없습니다!");
                return

            if self.widgets.scheduler_checkBox.isChecked():
                self.widgets.left_progressName.setText("곧 스케쥴러가 시작됩니다...")
                self.widgets.left_progressName.setWordWrap(True)
            else:
                self.widgets.left_progressName.setText("곧 다운로드가 시작됩니다...")
                self.widgets.left_progressName.setWordWrap(True)

            if lock_Scheduler() == True:
                thread = threading.Thread(target= lambda: requestMultipleAnimeSMI(progress_callback))
                thread.start()
            else:
                QMessageBox.information( 
                self.MainWindow, 
                "SMI-DOWNLOADER", 
                "다른 작업이 먼저 수행중입니다....");
                return
            
            afterSheet = "background-color: rgb(156, 179, 199); color: rgb(255, 255, 255);"
            self.widgets.scheduler_button.setStyleSheet(afterSheet)

            self.widgets.scheduler_checkBox.setEnabled(False)

            if self.widgets.scheduler_comboBox.isEnabled():
                self.widgets.scheduler_button.setText("스케줄러 중지")
                common.isScheduler_mode = True;
            else:
                self.widgets.scheduler_button.setText("다운로드 중지")
                common.isScheduler_mode = False;
            
            self.widgets.scheduler_comboBox.setEnabled(False)
            isScheduler_button_clicked = True

            if self.widgets.scheduler_checkBox.isChecked(): # 반복 옵션이 체크 되어있었다면

                min = 1000 * 60
                hour = min * 60
                day = hour * 24

                if idx == 0: #10분마다
                    self.timer.start(10 * min)
                elif idx == 1: #30분마다
                    self.timer.start(30 * min)
                elif idx == 2: #1시간마다
                    self.timer.start(hour)
                elif idx == 3: #3시간마다
                    self.timer.start(3 * hour)
                elif idx == 4: #6시간마다
                    self.timer.start(6 * hour)
                elif idx == 5: #12시간마다
                    self.timer.start(12 * hour)
                elif idx == 6: #24시간마다
                    self.timer.start(day)
                    
        else: # 중지 로직
            beforeSheet = "background-color: rgb(52, 59, 72);"
            self.widgets.scheduler_button.setStyleSheet(beforeSheet)
            
            self.widgets.scheduler_checkBox.setEnabled(True)

            if common.isScheduler_mode == True:
                self.widgets.scheduler_button.setText("스케줄러 시작") 
                self.widgets.scheduler_comboBox.setEnabled(True)
                self.timer.stop()
            else:
                self.widgets.scheduler_button.setText("다운로드 시작")
                self.widgets.scheduler_comboBox.setEnabled(False)

            isScheduler_button_clicked = False
            
    # 타이머
    def scheduler_update(self):
        self.widgets.left_progressName.setText("곧 스케쥴러가 시작됩니다...")
        self.widgets.left_progressName.setWordWrap(True)
        if lock_Scheduler() == True:
            thread = threading.Thread(target= lambda: requestMultipleAnimeSMI(progress_callback))
            thread.start()


