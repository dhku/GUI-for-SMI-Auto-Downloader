import requests
import json
import sys
import re
import os
import yaml
import traceback
import threading
import natsort
import gdrive
import urllib.error
from http import client
from urllib import request
from urllib.request import urlopen
from urllib.parse import unquote
from urllib.parse import quote
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup
from .winpng import *

#pip install gdown
#pip install requests
#pip install PyYAML
#pip install beautifulsoup4

#시놀로지(헤놀로지)
# wget https://bootstrap.pypa.io/get-pip.py
# python3 get-pip.py
# python3 -m pip install {package name}
# python3 -m pip install 'urllib3<2.0'
# python3 -m pip install gdown

# =================================================
# Title: SMI AUTO DOWNLOADER
# Author: KUDONG
# Version: 1.5.9
# Url: https://github.com/dhku/SMI-Auto-Downloader
# =================================================

AnimeNO = -1
AnimeName = "None"
outpath = ""
smiDir = ""

console_output = ""
log_path = ""

p_extension = re.compile(r"^.*\.(zip|ass|smi|7z)$", re.IGNORECASE)
regrex1 = re.compile(r".*(naver).*")
regrex2 = re.compile(r".*(blogspot).*")
regrex3 = re.compile(r".*(tistory).*")

p_google = re.compile(r"(.*(https://drive.google.com/file/d/).*)")
p_google_2_1 = re.compile(r"(.*(https://docs.google.com/uc).*)")
p_google_2_2 = re.compile(r"(.*(https://drive.google.com/uc).*)")
p_google_3 = re.compile(r"(.*(https://drive.usercontent.google.com/download).*)")

p_harne = re.compile(r"(.*(https://harne1.tistory.com).*)")

thread_lock = threading.Lock()
isRunning = False
quitSignal = False

class DownloadProgress:
    """한 번의 다운로드에서 '몇 개 중 몇 개'와 GUI 갱신을 맡긴다.

    done은 처리한 파일 수, total은 예상 전체 파일 수다.
    자막 한 건의 성공 여부는 여기 두지 않고, 다운로드 함수의 반환값으로 올린다.
    """

    def __init__(self, on_update):
        self.done = 0
        self.total = 0
        self._on_update = on_update

    def status(self, message):
        self._notify(message, False)

    def step(self):
        self.done += 1
        self._notify(None, False)

    def finish(self, message):
        self._notify(message, True)

    def _notify(self, message, finished):
        text = "None" if message is None else message
        self._on_update(self.done, self.total, text, finished)

def init_paths(autoPath):
    global outpath, log_path
    log_path = os.path.abspath('.') + "/log/"

    with open('anime.yml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    if(data['download_path'] != ""):
        outpath = data['download_path']
    else:
        outpath = os.path.abspath('.') + "/downloads/"

    if(autoPath is True):
        outpath = os.path.abspath('.') + "/downloads/"        

    if not os.path.exists(outpath):
        os.makedirs(outpath)

    data['download_path'] = outpath
    with open('anime.yml', 'w', encoding='utf-8') as file:
        yaml.safe_dump(data, file, allow_unicode=True)

def _remove_partial(file_name):
    if file_name and os.path.isfile(file_name):
        try:
            os.remove(file_name)
        except OSError:
            pass

def download(url, file_name = None):
    sess = requests.Session()
    gdrive.track_session(sess)
    try:
        if quitSignal == True:
            raise gdrive.exceptions.DownloadCancelled()
        res = sess.get(url, stream=True)
        sess._active_response = res
        with open(file_name, "wb") as file:
            for chunk in res.iter_content(chunk_size=512 * 1024):
                if quitSignal == True:
                    break
                if chunk:
                    file.write(chunk)
        if quitSignal == True:
            _remove_partial(file_name)
            raise gdrive.exceptions.DownloadCancelled()
    except Exception:
        if quitSignal == True:
            _remove_partial(file_name)
            raise gdrive.exceptions.DownloadCancelled()
        raise
    finally:
        gdrive.untrack_session(sess)
        try:
            sess.close()
        except Exception:
            pass

def text_to_file(txt, file_name):
    f = open(file_name, 'w',encoding="UTF-8")
    f.write(txt)
    f.close()

def set_global_outpath(path):
    global outpath
    outpath = path + "/"

def set_global_quitSignal(signal):
    global quitSignal
    quitSignal = signal
    if signal == True:
        try:
            gdrive.abort_download()
        except Exception:
            pass

def get_global_outpath():
    return outpath

def get_global_console_output():
    global console_output
    return console_output

def get_new_log_file():
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d")
    new_filename = ""
    log_file_list = natsort.natsorted(os.listdir(os.path.abspath('.') + "/log"))
    log_file_list.remove("error.log")

    if(len(log_file_list) != 0):
        latest_file = log_file_list[len(log_file_list) - 1]
        pattern = r"(\d{4}-\d{2}-\d{2})-(\d+)\.log"
        match = re.match(pattern, latest_file)
        if match and match.group(1) == formatted_date:
            date = match.group(1)
            counter = int(match.group(2)) + 1
            temp = f"{date}-{counter}.log"
            if not os.path.exists(log_path + temp):
                new_filename = temp
        else:
            counter = 1
            while True:
                temp = f"{formatted_date}-{counter}.log"
                if not os.path.exists(log_path + temp):
                    new_filename = temp
                    break
                counter += 1
    else:
        counter = 1
        while True:
            temp = f"{formatted_date}-{counter}.log"
            if not os.path.exists(log_path + temp):
                new_filename = temp
                break
            counter += 1
    return new_filename

def get_download_progress_length(json_data):
    global AnimeName
    #다운로드 사이즈 체크
    total = 0
    for k in json_data:

        name = k['name']
        episode = k['episode']
        updDt = k['updDt']
        website = unquote(k['website'])

        folder_name = AnimeName
        folder_name = folder_name.replace(":","")
        folder_name = folder_name.replace("/","")
        folder_name = folder_name.replace("?","")
        folder_name = folder_name.replace("<","")
        folder_name = folder_name.replace(">","")
        folder_name = folder_name.replace("*","")
        folder_name = folder_name.replace("|","")
        smiDir = folder_name + "/" + episode + "화/" + name + "/"

        if os.path.isfile(outpath + smiDir + "finish.txt"):
            continue;
        if regrex1.match(website):
            total += download_count_naver(website)
        elif regrex2.match(website):
            total += download_count_blogspot(website)
        elif regrex3.match(website):
            total += download_count_tistory(website)
        elif website == "":
            continue;
        else:
            total += download_count_website(website)
    return total

def lock_Scheduler():
    global isRunning
    thread_lock.acquire()
    if isRunning == False:
        isRunning = True
        thread_lock.release()
        return True
    else:
        thread_lock.release()
        return False

def unlock_Scheduler():
    global isRunning
    thread_lock.acquire()
    isRunning = False
    thread_lock.release()

def print_log(log):
    global console_output
    console_output += log + "\n"

# 요청함수

def requestAnimeSMI_3(anime,callback):
    requestAnimeSMI_2(anime.animeNo,anime.subject,callback);

def requestAnimeSMI_2(AnimeNo,name,callback):
    global AnimeName
    AnimeName = name
    requestAnimeSMI(AnimeNo,callback)

def _close_job(progress, new_filename):
    print_log("다운로드 진행상황 => " + str(progress.done) + "/" + str(progress.total))
    if quitSignal == True:
        print_log("작업이 중지되었습니다")
        done_message = "다운로드가 중지되었습니다."
    else:
        print_log("작업이 종료되었습니다")
        done_message = "다운로드가 완료되었습니다."

    text_to_file(console_output, log_path + new_filename)
    progress.finish(done_message)
    unlock_Scheduler()

def requestAnimeSMI(AnimeNo, callback):
    global smiDir, console_output

    # 콘솔 출력 결과물 초기화
    console_output = ""

    print_log("다운경로: "+outpath)
    print_log("================================================================")

    # 로그 파일 디렉토리가 존재하지 않을시 생성
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    new_filename = get_new_log_file()
    progress = DownloadProgress(callback)

    response = requests.get("https://api.anissia.net/anime/caption/animeNo/" + str(AnimeNo))

    #print_log(response.status_code)

    datas = json.loads(response.text)
    json_data = datas["data"]

    #다운로드 사이즈 체크

    print_log("다운로드 사이즈를 체크 하고 있습니다.....")
    progress.total = get_download_progress_length(json_data)
    print_log("================================================================")

    text_to_file(console_output, log_path + new_filename)
    progress.status("다운로드에 필요한 데이터를 확인 하고 있습니다...")

    try:
        _requestAnimeSMI(AnimeNo, progress, new_filename, json_data)
    except gdrive.exceptions.DownloadCancelled:
        print_log("[=] 사용자 중지로 다운로드가 중단되었습니다.")

    _close_job(progress, new_filename)


def requestMultipleAnimeSMI(callback):
    global smiDir, console_output, AnimeName, AnimeNO

    with open('anime.yml', encoding='UTF8') as f:
        global outpath
        config = yaml.load(f, Loader=yaml.FullLoader)

        animelist = json.loads(config['anime_list'])

        # 콘솔 출력 결과물 초기화
        console_output = ""

        print_log("다운경로: "+outpath)
        print_log("================================================================")

        # 로그 파일 디렉토리가 존재하지 않을시 생성
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        new_filename = get_new_log_file()
        progress = DownloadProgress(callback)

        key1 = []
        key2 = []
        list = []

        print_log("다운로드 사이즈를 체크 하고 있습니다.....")
        
        for k in animelist:
            if quitSignal == True:
                break

            AnimeName = k['Anime']
            AnimeNO = k['AnimeNo']

            try:
                response = requests.get("https://api.anissia.net/anime/caption/animeNo/" + str(AnimeNO))
            except Exception as e:
                print_log("[-] 현재 애니시아 서버와 연결할수 없습니다..... :-(")
                break

            #print_log(response.status_code)
            datas = json.loads(response.text)
            json_data = datas["data"]
            
            #다운로드 사이즈 체크
            progress.total += get_download_progress_length(json_data)
            list.append(json_data)
            key1.append(AnimeName)
            key2.append(AnimeNO)

        print_log("================================================================")
        
        text_to_file(console_output, log_path + new_filename)
        progress.status("다운로드에 필요한 데이터를 확인 하고 있습니다...")

        count = 0
        try:
            for json_data in list:

                if quitSignal == True:
                    break

                AnimeName = key1[count]
                AnimeNO = key2[count]
                _requestAnimeSMI(AnimeNO, progress, new_filename, json_data)
                count += 1
        except gdrive.exceptions.DownloadCancelled:
            print_log("[=] 사용자 중지로 다운로드가 중단되었습니다.")

        _close_job(progress, new_filename)

def _requestAnimeSMI(AnimeNo, progress, new_filename, json_data):
    global AnimeName, smiDir, console_output

    for k in json_data:
        
        if quitSignal == True:
            break

        name = k['name']
        episode = k['episode']
        updDt = k['updDt']
        website = unquote(k['website'])

        progress.status("<" + AnimeName + "> 다운로드중...")
        print_log("다운로드 진행상황 => " + str(progress.done) + "/" + str(progress.total))
        print_log("ANIME SMI AUTO DOWNLOADER - Target => <"+AnimeName+">")    
        print_log("================================================================")
        print_log("> 제작자: " + name)
        print_log("> 회차: " + episode+"화")
        print_log("> 업데이트: " + updDt)
        print_log("> 주소: " + website)

        folder_name = AnimeName
        folder_name = folder_name.replace(":","")
        folder_name = folder_name.replace("/","")
        folder_name = folder_name.replace("?","")
        folder_name = folder_name.replace("<","")
        folder_name = folder_name.replace(">","")
        folder_name = folder_name.replace("*","")
        folder_name = folder_name.replace("|","")
        
        smiDir = folder_name + "/" + episode + "화/" + name + "/"

        if os.path.isfile(outpath + smiDir + "finish.txt"):
            print_log("[=] 이전에 생성된 finish.txt가 발견되어 과정이 스킵되었습니다.")
            print_log("================================================================")
            continue;

        if regrex1.match(website):
            print_log("[+] naver 검출.")
            succeeded = download_naver(website, progress)
        elif regrex2.match(website):
            print_log("[+] blogspot 검출.")
            succeeded = download_blogspot(website, progress)
        elif regrex3.match(website):
            print_log("[+] tistory 검출.")
            succeeded = download_tistory(website, progress)
        elif website == "":
            print_log("[=] 자막 사이트가 검출되지 않았습니다.")
            succeeded = False
        else:
            print_log("[+] 일반 웹사이트 검출.")
            succeeded = download_website(website, progress)
        
        if quitSignal == True:
            print_log("[=] 사용자 중지로 남은 다운로드를 건너뜁니다.")
            break

        if succeeded:
            text_to_file( json.dumps(k) , outpath + smiDir + "finish.txt");
            print_log("[+] finish.txt가 생성되었습니다.")
        else:
            print_log("[-] finish.txt가 생성되지 않았습니다.")

        print_log("================================================================")
        text_to_file(console_output, log_path + new_filename)


# 내부 로직 구현

def _to_drive_view(url, drive_uc=False):
    """여러 형태의 구글 드라이브 링크를 /file/d/.../view 로 맞춘다."""
    if p_google_2_1.match(url):
        start_index = url.find("&id=") + 4
        end_index = url.rfind("&confirm")
        url = "https://drive.google.com/file/d/" + url[start_index:end_index] + "/view"
    if drive_uc and p_google_2_2.match(url):
        start_index = url.find("&id=") + 4
        end_index = len(url)
        url = "https://drive.google.com/file/d/" + url[start_index:end_index] + "/view"
    if p_google_3.match(url):
        start_index = url.find("?id=") + 4
        end_index = url.rfind("&export")
        url = "https://drive.google.com/file/d/" + url[start_index:end_index] + "/view"
    return url

def _download_drive_view(view_url, progress):
    """https://drive.google.com/file/d/.../view 하나를 저장한다.

    확장자가 자막/압축이 아니면 진행만 올리고 False.
    저장했으면 True. 실패는 예외를 그대로 올린다.
    """
    start_index = view_url.find("/d/") + 3
    end_index = view_url.rfind("/view")
    key = view_url[start_index:end_index]
    uc_url = "https://drive.google.com/uc?id=" + key

    remotefile = urlopen(uc_url)
    file_name = remotefile.headers.get_filename()

    if file_name is not None:
        file_name = file_name.encode('ISO-8859-1').decode('UTF-8')
    else:
        parsed_url = urlparse(uc_url)
        file_name = unquote(os.path.basename(parsed_url.path))

    if file_name == "uc":
        file_name = gdrive.get_file_name(uc_url)

    if not p_extension.match(file_name):
        progress.step()
        return False

    print_log("[=] 다운로드 시작 => " + file_name)

    path = outpath + smiDir
    if not os.path.exists(path):
        os.makedirs(path)

    gdrive.download(uc_url, path + file_name, quiet=False)
    print_log("[+] 파일 다운로드가 완료 되었습니다. ")
    progress.step()
    return True

def _header_filename(url, response):
    file_name = response.headers.get_filename()
    if file_name is not None:
        return file_name.encode('ISO-8859-1').decode('UTF-8')
    return unquote(os.path.basename(urlparse(url).path))

def download_naver(url, progress):
    #URL source를 긁어옵니다.
    url_source = get_url_source_naver(url)

    if url_source is None:
        return False
    
    # find 't.static.blog.naver.net'
    if url_source.find("t.static.blog/mylog") == -1:
        print_log("\n[-] It is not a NAVER Blog")
        return False

    failed = False
    try:
        # find 'aPostFiles'
        # 캡쳐 그룹 \[ \] 사이 - 따로 [ ] 감싸줘야함
        # p_attached_file = re.compile(r"\s*.*aPostFiles\[1\] = JSON.parse\(\'\[(.*?)\]", re.IGNORECASE | re.DOTALL)
        # 캡쳐 그룹 ( ) 사이 - 따로 [ ] 안해도됨
        p_attached_file = re.compile(r"\s*.*aPostFiles\[1\]\s*=\s*JSON\.parse\('(\[.*?\])'\s*\.replace", re.IGNORECASE | re.DOTALL)
        result = p_attached_file.match(url_source).group(1)
        if result != '[]':
            # convert to JSON style
            # data = "[" + result.replace('\\\'', '\"') + "]"
            data = result.replace('\\\'', '\"')
            json_data = json.loads(data)

            for each_file in json_data:       
                try:
                    print_log("* File : %s, Size : %s Bytes" % (each_file["encodedAttachFileName"], each_file["attachFileSize"]))
                    print_log("  Link : %s" % each_file["encodedAttachFileUrl"])
                    # File Download
                    print_log("[=] 다운로드 시작 => "+each_file["encodedAttachFileName"])

                    path = outpath + smiDir
                    if not os.path.exists(path):
                        os.makedirs(path)

                    download(each_file["encodedAttachFileUrl"], path + each_file["encodedAttachFileName"])
                    print_log("[+] 파일 다운로드가 완료 되었습니다. ")
                    progress.step()

                except Exception as e:
                    print_log("[-] Error : %s" % e)
                    failed = True
                    progress.step()
        else:
            soup = BeautifulSoup(url_source, 'html.parser')
            temps = soup.find('div',class_="se-main-container")    

            if(temps is None):
                temps = soup.find('div', {'class': 'se-main-container'})

            links = temps.find_all("a")
            file_found = 0

            p_attach = re.compile(r"(.*(googleusercontent).*)")

            for a in links:
                if a.get('href') == None:
                    continue
                each_file = a.attrs['href']
                # print_log("href = "+each_file)
                try:
                    each_file = each_file.replace('&amp;','&')

                    # 구글 드라이브 주소가 검출되었을때
                    if p_google.match(each_file):
                        if _download_drive_view(each_file, progress):
                            file_found = 1

                    # 일반 다운로드 주소가 검출되었을때
                    elif p_attach.match(each_file) is None:
                        print_log("  Link : %s" % each_file)
                        remotefile = urlopen(each_file)
                        fileName = _header_filename(each_file, remotefile)

                        print_log("[=] 다운로드 시작 => "+fileName)

                        path = outpath + smiDir
                        if not os.path.exists(path):
                            os.makedirs(path)

                        download(each_file, path + fileName)
                        file_found = 1
                        print_log("[+] 파일 다운로드가 완료 되었습니다. ")
                        progress.step()

                except urllib.error.HTTPError as e:
                    print_log("[=] 해당 URL은 스킵되었습니다. : %s" % e)
                    progress.step()
                except Exception as e:
                    print_log("[-] Error : %s" % e)
                    progress.step()
            
            if file_found == 0:
                print_log("[-] Attached File not found !!")
                failed = True
    except Exception as e:
        print_log("[-] Error : %s" % e)
        failed = True
    return not failed

def download_count_naver(url):
    url_source = get_url_source_naver(url);
    if url_source is None:
        return 0;
    if url_source.find("t.static.blog/mylog") == -1:
        return 0;
    download_count = 0
    try:
        p_attached_file = re.compile(r"\s*.*aPostFiles\[1\]\s*=\s*JSON\.parse\('(\[.*?\])'\s*\.replace", re.IGNORECASE | re.DOTALL)
        result = p_attached_file.match(url_source).group(1)
        if result != '[]':
            # data = "[" + result.replace('\\\'', '\"') + "]"
            data = result.replace('\\\'', '\"')
            json_data = json.loads(data)
            
            for each_file in json_data:  
                download_count += 1

            return download_count
        else:
            soup = BeautifulSoup(url_source, 'html.parser')
            temps = soup.find('div',class_="se-main-container")    
            
            if(temps is None):
                temps = soup.find('div', {'class': 'se-main-container'})

            links = temps.find_all("a")

            p_attach = re.compile(r"(.*(googleusercontent).*)")
            p_google = re.compile(r"(.*(https://drive.google.com/file/d/).*)")

            for a in links:
                if a.get('href') == None:
                    continue;
                each_file = a.attrs['href']
                try:
                    each_file = each_file.replace('&amp;','&');
                    # 구글 드라이브 주소가 검출되었을때
                    if bool(p_google.match(each_file)):
                        download_count += 1

                    # 일반 다운로드 주소가 검출되었을때
                    elif bool(p_attach.match(each_file)) == False:
                        download_count += 1

                except Exception as e:
                    download_count += 0 
    except Exception as e:
        return download_count
    return download_count

def get_url_source_naver(url):
    try:
        while url.find("PostView.naver") == -1 and url.find("PostList.naver") == -1:
            f = request.urlopen(url)
            url_info = f.info()
            url_charset = client.HTTPMessage.get_charsets(url_info)[0]
            url_source = f.read().decode(url_charset)

            # get frame src
            p_frame = re.compile(r"\s*.*?<iframe.*?mainFrame.*?(.*)", re.IGNORECASE | re.DOTALL)
            p_src_url = re.compile(r"\s*.*?src=[\'\"](.+?)[\'\"]", re.IGNORECASE | re.DOTALL)
            src_url = p_src_url.match(p_frame.match(url_source).group(1)).group(1)
            url = src_url

        if url.find("http://blog.naver.com") == -1:
            last_url = "http://blog.naver.com" + url
        else:
            last_url = url

        print_log("   => Last URL : %s\n" % last_url)
        f = request.urlopen(last_url)
        url_info = f.info()
        url_charset = client.HTTPMessage.get_charsets(url_info)[0]
        url_source = f.read().decode(url_charset)

        return url_source

    except Exception as e:
        print_log("[-] Error : %s" % e)
        return None

def download_tistory(url, progress):
    url_source = get_url_source_tistory(url)

    if url_source is None:
        return False

    # find 's1.daumcdn.net/cfs.tistory'
    if url_source.find("t1.daumcdn.net/tistory") == -1:
        print_log("[-] It is not a Tistory Blog")
        return False

    if p_harne.match(url):
        path = outpath + smiDir
        winpng(url, path, True, True)
        progress.step()
        return True

    failed = False
    try:
        # find all 'attach file link'
        p_attach = re.compile(r"href=[\'\"](\S+?/attachment/.*?)[\'\"]\s*.*?/> (.*?)</", re.IGNORECASE | re.DOTALL)
        result = p_attach.findall(url_source)

        if result:
            
            for each_file in result:
                file_url = each_file[0]
                if each_file[1] == "":
                    file_name = file_url[file_url.rfind('/') + 1:]
                else:
                    file_name = each_file[1]
                print_log("* File : %s" % file_name)
                print_log("  Link : %s" % file_url)
                print_log("[=] 다운로드 시작 => "+file_name)

                path = outpath + smiDir
                if not os.path.exists(path):
                    os.makedirs(path)

                download(file_url, path + file_name)
                print_log("[+] 파일 다운로드가 완료 되었습니다. ")
                progress.step()
        else:
            soup = BeautifulSoup(url_source, 'html.parser')
            temps = soup.find('div',class_="tt_article_useless_p_margin contents_style")    
        
            if(temps is None):
                temps = soup.find('div', {'class': 'contents_style'})

            links = temps.find_all("a")
            file_found = 0

            p_attach = re.compile(r"(.*(googleusercontent).*)")

            for a in links:
                if a.get('href') == None:
                    continue
                each_file = a.attrs['href']
                # print_log("href = "+each_file)
                try:
                    each_file = each_file.replace('&amp;','&')

                    # 구글 드라이브 주소가 검출되었을때
                    if p_google.match(each_file):
                        if _download_drive_view(each_file, progress):
                            file_found = 1

                    # 일반 다운로드 주소가 검출되었을때
                    elif p_attach.match(each_file) is None:
                        print_log("  Link : %s" % each_file)
                        remotefile = urlopen(each_file)
                        fileName = _header_filename(each_file, remotefile)

                        print_log("[=] 다운로드 시작 => "+fileName)

                        path = outpath + smiDir
                        if not os.path.exists(path):
                            os.makedirs(path)

                        download(each_file, path + fileName)
                        file_found = 1
                        print_log("[+] 파일 다운로드가 완료 되었습니다. ")
                        progress.step()

                except urllib.error.HTTPError as e:
                    print_log("[=] 해당 URL은 스킵되었습니다. : %s" % e)
                    progress.step()
                except Exception as e:
                    print_log("[-] Error : %s" % e)
                    print_log(traceback.format_exc())
                    progress.step()
            
            if file_found == 0:
                print_log("[-] Attached File not found !!")
                failed = True
    
    except Exception as e:
        print_log("[-] Error : %s" % e)
        print_log(traceback.format_exc())
        failed = True
    return not failed   

def download_count_tistory(url):
    url_source = get_url_source_tistory(url)

    if url_source is None:
        return 0
    
    if url_source.find("t1.daumcdn.net/tistory") == -1:
        return 0;

    download_count = 0

    if bool(p_harne.match(url)):
        return 1;

    try:
        p_attach = re.compile(r"href=[\'\"](\S+?/attachment/.*?)[\'\"]\s*.*?/> (.*?)</", re.IGNORECASE | re.DOTALL)
        result = p_attach.findall(url_source)

        if result:
            return result.len()
        else:
            soup = BeautifulSoup(url_source, 'html.parser')
            temps = soup.find('div',class_="tt_article_useless_p_margin contents_style")    
            
            if(temps is None):
                temps = soup.find('div', {'class': 'contents_style'})

            links = temps.find_all("a")

            p_attach = re.compile(r"(.*(googleusercontent).*)")
            p_google = re.compile(r"(.*(https://drive.google.com/file/d/).*)")

            for a in links:
                if a.get('href') == None:
                    continue;
                each_file = a.attrs['href']
                try:
                    each_file = each_file.replace('&amp;','&');
                    # 구글 드라이브 주소가 검출되었을때
                    if bool(p_google.match(each_file)):
                        download_count += 1

                    # 일반 다운로드 주소가 검출되었을때
                    elif bool(p_attach.match(each_file)) == False:
                        download_count += 1

                except Exception as e:
                    download_count += 0

    except Exception as e:
        download_count += 0   
    
    return download_count

def get_url_source_tistory(url):
    try:
        try:
            f = request.urlopen(url)
        except Exception as e:
            # 한글 URL 검출시 quote로 감싸야됨
            # 'ascii' codec can't encode characters in position 11-13: ordinal not in range(128) 방지
            last_slash_index = url.rfind('/')
            body = url[:last_slash_index]
            query = quote(url[last_slash_index:])
            #print_log("출력=> "+body + query)
            f = request.urlopen(body + query)

        url_info = f.info()
        url_charset = client.HTTPMessage.get_charsets(url_info)[0]
        url_source = f.read().decode(url_charset)
        return url_source
    except Exception as e:
        print_log("[-] Error : %s" % e)
        print_log(traceback.format_exc())
        return None

def download_blogspot(url, progress):
    url_source = get_url_source_blogspot(url)

    if url_source is None:
        return False

    # p_attach = re.compile(r"<div class=\'post-body.*?\'[^>]*>((?:(?:(?!<div[^>]*>|</div>).)+|<div[^>]*>([\s\S]*?)</div>)*)</div>", re.IGNORECASE | re.DOTALL)   
    # result = p_attach.findall(url_source)

    soup = BeautifulSoup(url_source, 'html.parser')
    temps = soup.find('div',class_="post-body")

    links = temps.find_all("a")

    p_attach = re.compile(r"(.*(googleusercontent).*)")
    saved_any = False

    for a in links:
        each_file = a.attrs['href']
        #print_log("href = "+each_file)
        try:
            each_file = each_file.replace('&amp;','&')
            each_file = _to_drive_view(each_file)

            # 구글 드라이브 주소가 검출되었을때
            if p_google.match(each_file):
                if _download_drive_view(each_file, progress):
                    saved_any = True
            # 일반 다운로드 주소가 검출되었을때
            elif p_attach.match(each_file) is None:
                print_log("  Link : %s" % each_file)
                remotefile = urlopen(each_file)
                fileName = remotefile.headers.get_filename()

                if fileName is not None:
                    try:
                        fileName = fileName.encode('ISO-8859-1').decode('UTF-8')
                    except Exception as e:
                        fileName = fileName.encode('UTF-8').decode('ISO-8859-1')
                        fileName = fileName.encode('ISO-8859-1').decode('UTF-8')
                else:
                    parsed_url = urlparse(each_file)
                    fileName = os.path.basename(parsed_url.path)
                    fileName = unquote(fileName)

                if not p_extension.match(fileName):
                    progress.step()
                    continue
                
                print_log("[=] 다운로드 시작 => "+fileName)

                path = outpath + smiDir
                if not os.path.exists(path):
                    os.makedirs(path)

                download(each_file, path + fileName)
                saved_any = True
                print_log("[+] 파일 다운로드가 완료 되었습니다. ")
                progress.step()

        except urllib.error.HTTPError as e:
            print_log("[=] 해당 URL은 스킵되었습니다. : %s" % e)
            progress.step()
        except Exception as e:
            print_log("[-] Error : %s" % e)
            print_log(traceback.format_exc())
            progress.step()

    return saved_any

def download_count_blogspot(url):

    url_source = get_url_source_blogspot(url)

    if url_source is None:
        return 0

    soup = BeautifulSoup(url_source, 'html.parser')
    temps = soup.find('div',class_="post-body")

    links = temps.find_all("a")

    p_attach = re.compile(r"(.*(googleusercontent).*)")
    p_google = re.compile(r"(.*(https://drive.google.com/file/d/).*)")

    download_count = 0;

    for a in links:
        each_file = a.attrs['href']

        try:
            each_file = each_file.replace('&amp;','&');
            # 구글 드라이브 주소가 검출되었을때
            if bool(p_google.match(each_file)):
                print_log("[+] 구글 드라이브 주소가 검출되었습니다.")
                download_count += 1
            # 일반 다운로드 주소가 검출되었을때
            elif bool(p_attach.match(each_file)) == False:
                print_log("[+] 일반 다운로드 주소가 검출되었습니다.")
                download_count += 1
        except Exception as e:
            download_count += 0
    return download_count    

def get_url_source_blogspot(url):
    try:
        try:
            f = request.urlopen(url)
        except Exception as e:
            # 한글 URL 검출시 quote로 감싸야됨
            # 'ascii' codec can't encode characters in position 11-13: ordinal not in range(128) 방지
            last_slash_index = url.rfind('/')
            body = url[:last_slash_index]
            query = quote(url[last_slash_index:])
            #print_log("출력=> "+body + query)
            f = request.urlopen(body + query)
        url_info = f.info()
        url_charset = client.HTTPMessage.get_charsets(url_info)[0]
        url_source = f.read().decode(url_charset)
        return url_source
    except Exception as e:
        print_log("[-] Error : %s" % e)
        return None

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

def extract_csrf_token(html, url_source=None):
    match = re.search(r'<meta\s+name="csrf-token"\s+content="([^"]+)"', html)
    return match.group(1) if match else None

def download_website(url, progress):
    url_source = get_url_source_website(url)

    if url_source is None:
        return False

    soup = BeautifulSoup(url_source, 'html.parser')
    temps = soup.find('div')
    return find_blog_standard(temps, progress)

def find_blog_standard(temps, progress):
    links = temps.find_all("a")

    for a in links:
        each_file = a.attrs['href']
        #print_log("href = "+each_file)

        try:
            each_file = each_file.replace('&amp;','&')
            each_file = _to_drive_view(each_file, drive_uc=True)

            if p_google.match(each_file):
                if _download_drive_view(each_file, progress):
                    return True
        except urllib.error.HTTPError as e:
            print_log("[=] 해당 URL은 스킵되었습니다. : %s" % e)
            progress.step()
            return False
        except Exception as e:
            print_log("[-] Error : %s" % e)
            print_log(traceback.format_exc())
            progress.step()
            return False
    return False

# Cloudflare Turnstile 인증으로 Deprecated 
def find_blog_1(temps, url, progress):
    blog_1_url = re.compile(r"(.*(https://erulabo.com/file).*)")
    links = temps.find_all("button", attrs={"data-file-url": True})

    for a in links:
        each_file = "https://erulabo.com" + a.attrs['data-file-url']
        #print("data-file-url = "+each_file)

        try:
            each_file = each_file.replace('&amp;','&')

            if blog_1_url.match(each_file):

                # Step 1: 게시글 접근 → 쿠키 + CSRF 토큰
                session = requests.Session()
                session.headers.update(HEADERS)

                resp = session.get(url, timeout=15)
                resp.raise_for_status()
                csrf_token = extract_csrf_token(resp.text)

                token_url = each_file + "/token"
                token_resp = session.post(
                    token_url,
                    json={},  # Content-Length: 2 (빈 JSON body)
                    headers={
                        "Accept": "*/*",
                        "Content-Type": "application/json",
                        "X-CSRF-TOKEN": csrf_token,
                        "X-Requested-With": "XMLHttpRequest",
                        "Referer": url,
                        "Origin": "https://erulabo.com",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                    },
                    timeout=15,
                )

                # Step 2: POST /file/{uuid}/token 으로 다운로드 URL 획득
                data = token_resp.json()
                download_url = data.get("download_url", "")

                if download_url:
                    dl_resp = session.get(download_url, allow_redirects=False, timeout=15)

                    if dl_resp.status_code in (301, 302, 303, 307, 308): # Google Drive URL
                        each_file = dl_resp.headers.get("Location", "")
                        print_log("Google Drive URL: " + each_file)
                    else: # 리다이렉트 없음
                        each_file = download_url

            each_file = _to_drive_view(each_file, drive_uc=True)

            if p_google.match(each_file):
                if _download_drive_view(each_file, progress):
                    return True
    
        except urllib.error.HTTPError as e:
            print_log("[=] 해당 URL은 스킵되었습니다. : %s" % e)
            progress.step()
            return False
        except Exception as e:
            print_log("[-] Error : %s" % e)
            print_log(traceback.format_exc())
            progress.step()
            return False
    return False

def download_count_website(url):

    url_source = get_url_source_website(url)

    if url_source is None:
        return 0

    soup = BeautifulSoup(url_source, 'html.parser')
    temps = soup.find('div')

    links = temps.find_all("a")

    download_count = 0;

    for a in links:
        each_file = a.attrs['href']

        try:
            each_file = each_file.replace('&amp;','&');
            # 구글 드라이브 주소가 검출되었을때
            if bool(p_google.match(each_file)):
                print_log("[+] 구글 드라이브 주소가 검출되었습니다.")
                download_count += 1
        except Exception as e:
            download_count = 0

    return download_count    

def get_url_source_website(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        try:
            req = request.Request(url, headers=headers)
            f = request.urlopen(req)
        except Exception as e:
            # 한글 URL 검출시 quote로 감싸야됨
            # 'ascii' codec can't encode characters in position 11-13: ordinal not in range(128) 방지
            last_slash_index = url.rfind('/')
            body = url[:last_slash_index]
            query = quote(url[last_slash_index:])
            #print_log("출력=> "+body + query)
            f = request.urlopen(body + query)
        url_info = f.info()
        url_charset = client.HTTPMessage.get_charsets(url_info)[0]
        url_source = f.read().decode(url_charset)
        return url_source
    except Exception as e:
        print_log("[-] Error : %s" % e)
        return None

def run_scheduler(callback):
    with open('anime.yml', encoding='UTF8') as f:
        global outpath
        config = yaml.load(f, Loader=yaml.FullLoader)

        if config['download_path'] != "":
            outpath = config['download_path'] + "/"

        print_log("다운경로: "+outpath)

        animelist = json.loads(config['anime_list'])

        print_log("================================================================")

        for k in animelist:
            global AnimeName,AnimeNO
            AnimeName = k['Anime']
            AnimeNO = k['AnimeNo']
            requestAnimeSMI(AnimeNO,callback);

if __name__ == "__main__":
    print_log("hello")
    #run_scheduler()

