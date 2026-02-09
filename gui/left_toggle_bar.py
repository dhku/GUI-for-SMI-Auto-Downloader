from datetime import datetime
from functools import partial
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from kudong import *

#leftToggleBar
class LeftToggleBar(QObject):

    def __init__(self, MainWindow, widgets):
        super().__init__() # QObject 상속시 반드시 필수
        self.MainWindow = MainWindow
        self.widgets = widgets   
        common.toggleBar_instance = self

        self.widgets.left_downloadButton.clicked.connect(self.directDownload)
        self.widgets.left_addQueue.clicked.connect(self.addQueue)
        self.widgets.left_more.clicked.connect(self.clickMore)
        self.widgets.left_website.clicked.connect(self.clickMore2)

        self.widgets.left_progressBar.setMinimum(0);
        self.widgets.left_progressBar.setMaximum(100);
        self.widgets.left_progressBar.setValue(0);
        #self.widgets.left_progressBar.hide()

        self.widgets.left_progressName.setText("현재 대기열에 작업이 없습니다.")
        self.widgets.left_progressName.setWordWrap(True)

        idle_text = "편성표에서 원하는 자막을 선택하세요"
        self.widgets.label.setText("<html><head/><body><p align='center'><span style=' font-size:20pt; font-weight:600;'>"+idle_text+"</span></p></body></html>");
        self.widgets.label.setWordWrap(True)

        self.widgets.label_date.hide()

    def addQueue(self):
        selectedAnime_LeftBox = common.selectedAnime_LeftBox

        if(selectedAnime_LeftBox is not None):
            idx = -1;
            isFindBlank = False;
            list = []

            for row in range(self.widgets.scheduler_table.rowCount()):
                id = self.widgets.scheduler_table.item(row, 0)
                if(id is None):
                    break
                list.append(id.text())

            #print("리스트 출력" + str(list))

            if(str(selectedAnime_LeftBox.animeNo) in list):
                QMessageBox.information(self.MainWindow, 'SMI-DOWNLOADER','즐겨찾기에 이미 존재하는 작품입니다!')
                return    
            
            for row in range(self.widgets.scheduler_table.rowCount()):
                id = self.widgets.scheduler_table.item(row, 0)
                if(id is None):
                    idx = row
                    isFindBlank = True
                    break

            if(isFindBlank is True): 
                self.widgets.scheduler_table.setItem(idx,0,QTableWidgetItem(str(selectedAnime_LeftBox.animeNo)));
                self.widgets.scheduler_table.setItem(idx,1,QTableWidgetItem(selectedAnime_LeftBox.subject.replace('"', '')));
            else:
                rowCount = self.widgets.scheduler_table.rowCount();
                self.widgets.scheduler_table.setRowCount(rowCount + 1)
                self.widgets.scheduler_table.setItem(rowCount,0,QTableWidgetItem(str(selectedAnime_LeftBox.animeNo)));
                self.widgets.scheduler_table.setItem(rowCount,1,QTableWidgetItem(selectedAnime_LeftBox.subject.replace('"', '')));                

            common.downloadPage_instance.onYmlsaveButtonClicked()
            QMessageBox.information(self.MainWindow,'SMI-DOWNLOADER','즐겨찾기에 추가되었습니다!')


    def directDownload(self):

        selectedAnime_LeftBox = common.selectedAnime_LeftBox

        if(selectedAnime_LeftBox is not None):
            #self.widgets.left_progressBar.show()

            if lock_Scheduler() == True:
                self.widgets.left_progressBar.setValue(0)
                common.download_thread = threading.Thread(target= lambda: requestAnimeSMI_3(selectedAnime_LeftBox,progress_callback))
                common.download_thread.start()
            else:
                QMessageBox.information( 
                self.MainWindow, 
                "SMI-DOWNLOADER", 
                "다른 작업이 먼저 수행중입니다....");
                return
            
            # 로그 콘솔 내용 초기화
            self.widgets.log_console.setPlainText("")
            self.widgets.log_console.verticalScrollBar().setValue(
                self.widgets.log_console.verticalScrollBar().maximum()
            )

            # 프로그레스 바 내용 설정
            self.widgets.left_progressName.setText("곧 다운로드가 시작됩니다...")
            self.widgets.left_progressName.setWordWrap(True)

    def clickMore(self):
        selectedAnime_LeftBox = common.selectedAnime_LeftBox
        if(selectedAnime_LeftBox is not None):
            open_url("https://anissia.net/anime?animeNo=" + str(selectedAnime_LeftBox.animeNo))

    def clickMore2(self):
        selectedAnime_LeftBox = common.selectedAnime_LeftBox
        if(selectedAnime_LeftBox is not None):
            open_url(selectedAnime_LeftBox.website)

    @Slot(int, int, str, bool) # Slot 가 선언되어있는 객체는 QObject를 무조건 상속받아야함
    def updateProgressBar(self,progress,count,output,isFinished):
        global isScheduler_button_clicked

        if count == 1 and progress == 0:
            self.widgets.left_progressBar.setValue(50);
        elif count == 0 and progress == 0: 
            self.widgets.left_progressBar.setValue(100);
        else:
            self.widgets.left_progressBar.setValue((progress / count) * 100);
    

        self.widgets.log_console.setPlainText(get_global_console_output())
        self.widgets.log_console.verticalScrollBar().setValue(
            self.widgets.log_console.verticalScrollBar().maximum()
        )

        if not output == "None":
            self.widgets.left_progressName.setText(output)
            self.widgets.left_progressName.setWordWrap(True)

        if isFinished == True and common.isScheduler_mode == False:
            beforeSheet = "background-color: rgb(52, 59, 72);"
            self.widgets.scheduler_button.setStyleSheet(beforeSheet)
            
            self.widgets.scheduler_button.setText("다운로드 시작")

            self.widgets.scheduler_checkBox.setEnabled(True)
            self.widgets.scheduler_comboBox.setEnabled(False)

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

            self.widgets.log_timestamp.clearContents()
            self.widgets.log_timestamp.setRowCount(len(log_file_list))
            self.widgets.log_timestamp.setColumnCount(3)

            count = 0
            for f in log_file_list:
                self.widgets.log_timestamp.setItem(count,0,QTableWidgetItem(f));
                self.widgets.log_timestamp.setItem(count,1,QTableWidgetItem("download_subtitle"));
                self.widgets.log_timestamp.setItem(count,2,QTableWidgetItem("다운로드 로그 데이터"));
                count += 1                 

            for row in range(self.widgets.log_timestamp.rowCount()):
                for column in range(self.widgets.log_timestamp.columnCount()):
                    item = self.widgets.log_timestamp.item(row, column)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
            
            self.widgets.log_timestamp.verticalScrollBar().setValue(
            self.widgets.log_timestamp.verticalScrollBar().maximum()
            )

        # print("===============================================")
        # print(">콜백함수 진행수 " + str(progress) + "/" + str(count))
        # print(">콜백함수 진행률 " + str((progress / count) + "%")
        # print("===============================================")




    