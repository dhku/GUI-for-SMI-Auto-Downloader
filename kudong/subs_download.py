import requests
import json
import sys
import re
import os
import io
import time
import yaml
import traceback
import threading
import natsort
import gdrive
from http import client
from urllib import request
from urllib.request import urlopen
from urllib.parse import unquote
from urllib.parse import quote
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup
from functools import partial


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
# Version: 1.2
# Url: https://github.com/dhku/SMI-Auto-Downloader
# =================================================

AnimeNO = -1
AnimeName = "None"
outpath = os.path.abspath('.') + "/"
smiDir = ""
isDownloadError = 0

download_progress_count = 0;
download_progress_length = 0;

console_output = ""
log_path = os.path.abspath('.') + "/log/"

p_extension = re.compile(r"^.*\.(zip|ass|smi|7z)$")
regrex1 = re.compile(r".*(naver).*")
regrex2 = re.compile(r".*(blogspot).*")
regrex3 = re.compile(r".*(tistory).*")

thread_lock = threading.Lock()
isRunning = False

quitSignal = False

def download(url, file_name = None):
    with open(file_name, "wb") as file:  
        response = requests.get(url)              
        file.write(response.content)      

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
    #다운로드 사이즈 체크
    download_progress_length = 0
    for k in json_data:

        name = k['name']
        episode = k['episode']
        updDt = k['updDt']
        website = unquote(k['website'])

        smiDir = AnimeName + "/" + episode + "화/" + name + "/"

        if os.path.isfile(outpath + smiDir + "finish.txt"):
            continue;
        if regrex1.match(website):
            download_progress_length += download_count_naver(website)
        elif regrex2.match(website):
            download_progress_length += download_count_blogspot(website)
        elif regrex3.match(website):
            download_progress_length += download_count_tistory(website)
        else:
            download_progress_length += 0
    return download_progress_length

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

def requestAnimeSMI(AnimeNo,callback):
    global smiDir,isDownloadError,download_progress_count,download_progress_length,console_output,isRunning

    print_log("다운경로: "+outpath)
    print_log("================================================================")

    # 콘솔 출력 결과물 초기화
    console_output = ""

    # 로그 파일 디렉토리가 존재하지 않을시 생성
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    new_filename = get_new_log_file()

    download_progress_count = 0;
    download_progress_length = 0;

    response = requests.get("https://api.anissia.net/anime/caption/animeNo/" + str(AnimeNo))

    #print_log(response.status_code)

    datas = json.loads(response.text)
    json_data = datas["data"]

    #다운로드 사이즈 체크

    print_log("다운로드 사이즈를 체크 하고 있습니다.....")
    download_progress_length = get_download_progress_length(json_data);
    print_log("================================================================")

    text_to_file(console_output, log_path + new_filename)
    callback(download_progress_count,download_progress_length, "다운로드에 필요한 데이터를 확인 하고 있습니다...")

    _requestAnimeSMI(AnimeNo,callback,new_filename,json_data)

    print_log("다운로드 진행상황 => "+str(download_progress_count)+"/"+str(download_progress_length))
    print_log("작업이 종료되었습니다")

    text_to_file(console_output, log_path + new_filename)

    callback(download_progress_count,download_progress_length,"다운로드가 완료되었습니다.",True)

    unlock_Scheduler()


def requestMultipleAnimeSMI(callback):
    global smiDir,isDownloadError,download_progress_count,download_progress_length,console_output, AnimeName,AnimeNO,isRunning

    with open('anime.yml', encoding='UTF8') as f:
        global outpath
        config = yaml.load(f, Loader=yaml.FullLoader)

        animelist = json.loads(config['anime_list'])

        print_log("다운경로: "+outpath)
        print_log("================================================================")

        # 콘솔 출력 결과물 초기화
        console_output = ""

        # 로그 파일 디렉토리가 존재하지 않을시 생성
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        new_filename = get_new_log_file()

        download_progress_count = 0;
        download_progress_length = 0;

        key1 = []
        key2 = []
        list = []

        print_log("다운로드 사이즈를 체크 하고 있습니다.....")
        
        for k in animelist:
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
            download_progress_length += get_download_progress_length(json_data);
            list.append(json_data)
            key1.append(AnimeName)
            key2.append(AnimeNO)

        print_log("================================================================")
        
        text_to_file(console_output, log_path + new_filename)    
        callback(download_progress_count,download_progress_length, "다운로드에 필요한 데이터를 확인 하고 있습니다...")

        count = 0
        for json_data in list:

            if quitSignal == True:
                break

            AnimeName = key1[count]
            AnimeNO = key2[count]
            _requestAnimeSMI(AnimeNO,callback,new_filename,json_data)
            count += 1


        print_log("다운로드 진행상황 => "+str(download_progress_count)+"/"+str(download_progress_length))
        print_log("작업이 종료되었습니다")

        text_to_file(console_output, log_path + new_filename)

        callback(download_progress_count,download_progress_length,"다운로드가 완료되었습니다.",True)

        unlock_Scheduler()

def _requestAnimeSMI(AnimeNo,callback,new_filename,json_data):
    global smiDir,isDownloadError,download_progress_count,download_progress_length,console_output

    for k in json_data:
        
        if quitSignal == True:
            break

        isDownloadError = 0;

        name = k['name']
        episode = k['episode']
        updDt = k['updDt']
        website = unquote(k['website'])

        smiDir = AnimeName + "/" + episode + "화/" + name + "/"

        callback(download_progress_count,download_progress_length,"<"+AnimeName+"> 다운로드중...")
        print_log("다운로드 진행상황 => "+str(download_progress_count)+"/"+str(download_progress_length))
        print_log("ANIME SMI AUTO DOWNLOADER - Target => <"+AnimeName+">")    
        print_log("================================================================")
        print_log("> 제작자: " + name)
        print_log("> 회차: " + episode+"화")
        print_log("> 업데이트: " + updDt)
        print_log("> 주소: " + website)

        if os.path.isfile(outpath + smiDir + "finish.txt"):
            print_log("[=] 이전에 생성된 finish.txt가 발견되어 과정이 스킵되었습니다.")
            print_log("================================================================")
            continue;

        if regrex1.match(website):
            print_log("[+] naver 검출.")
            download_naver(website,callback)
        elif regrex2.match(website):
            print_log("[+] blogspot 검출.")
            download_blogspot(website,callback)
        elif regrex3.match(website):
            print_log("[+] tistory 검출.")
            download_tistory(website,callback)
        else:
            print_log("[-] 해당 조건에 부합하는 링크가 존재하지 않습니다.")
            isDownloadError = 1;
        
        if isDownloadError == 0:
            text_to_file( json.dumps(k) , outpath + smiDir + "finish.txt");
            print_log("[+] finish.txt가 생성되었습니다.")
        else:
            print_log("[-] finish.txt가 생성되지 않았습니다.")

        print_log("================================================================")
        text_to_file(console_output, log_path + new_filename)


# 내부 로직 구현

def download_naver(url,callback):
    global isDownloadError,download_progress_count, download_progress_length
    #URL source를 긁어옵니다.
    url_source = get_url_source_naver(url);

    if url_source is None:
        isDownloadError = 1;
        return
    
    # find 't.static.blog.naver.net'
    if url_source.find("t.static.blog/mylog") == -1:
        print_log("\n[-] It is not a NAVER Blog")
        isDownloadError = 1;
        return 

    try:
        # find 'aPostFiles'
        #p_attached_file = re.compile(r"\s*.*aPostFiles\[1\] = \[(.*?)\]", re.IGNORECASE | re.DOTALL)
        p_attached_file = re.compile(r"\s*.*aPostFiles\[1\] = JSON.parse\(\'\[(.*?)\]", re.IGNORECASE | re.DOTALL)
        result = p_attached_file.match(url_source).group(1)
        if result:
            # convert to JSON style
            data = "[" + result.replace('\\\'', '\"') + "]"
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
                    download_progress_count += 1
                    callback(download_progress_count,download_progress_length)

                except Exception as e:
                    print_log("[-] Error : %s" % e)
                    isDownloadError = 1;
                    download_progress_count += 1
        else:
            soup = BeautifulSoup(url_source, 'html.parser')
            temps = soup.find('div',class_="se-main-container")    

            if(temps is None):
                temps = soup.find('div', {'class': 'se-main-container'})

            links = temps.find_all("a")
            file_found = 0;

            p_attach = re.compile(r"(.*(googleusercontent).*)")
            p_google = re.compile(r"(.*(https://drive.google.com/file/d/).*)")

            for a in links:
                if a.get('href') == None:
                    continue;
                each_file = a.attrs['href']
                # print_log("href = "+each_file)
                try:
                    each_file = each_file.replace('&amp;','&');

                    # 구글 드라이브 주소가 검출되었을때
                    if bool(p_google.match(each_file)):

                        start_index = each_file.find("/d/") + 3;
                        end_index =  each_file.rfind("/view");

                        key = each_file[start_index:end_index]
                        each_file = "https://drive.google.com/uc?id="+key

                        remotefile = urlopen(each_file)
                        fileName = remotefile.headers.get_filename();

                        if fileName is not None:
                            fileName = fileName.encode('ISO-8859-1').decode('UTF-8');
                        else:
                            parsed_url = urlparse(each_file)
                            fileName = os.path.basename(parsed_url.path)
                            fileName = unquote(fileName)

                        path = outpath + smiDir

                        if fileName == "uc":
                            fileName = gdrive.get_file_name(each_file)

                        if(not p_extension.match(fileName)):
                            download_progress_count += 1
                            callback(download_progress_count,download_progress_length)
                            continue;

                        print_log("[=] 다운로드 시작 => "+ fileName)

                        if not os.path.exists(path):
                            os.makedirs(path)

                        gdrive.download(each_file, path + fileName, quiet=False)
                        print_log("[+] 파일 다운로드가 완료 되었습니다. ")

                        file_found = 1;
                        download_progress_count += 1
                        callback(download_progress_count,download_progress_length)

                    # 일반 다운로드 주소가 검출되었을때
                    elif bool(p_attach.match(each_file)) == False:
                        print_log("  Link : %s" % each_file)
                        remotefile = urlopen(each_file)
                        fileName = remotefile.headers.get_filename();

                        if fileName is not None:
                            fileName = fileName.encode('ISO-8859-1').decode('UTF-8');
                        else:
                            parsed_url = urlparse(each_file)
                            fileName = os.path.basename(parsed_url.path)
                            fileName = unquote(fileName)

                        print_log("[=] 다운로드 시작 => "+fileName)

                        path = outpath + smiDir
                        if not os.path.exists(path):
                            os.makedirs(path)

                        download(each_file, path + fileName);
                        isDownloaded = 1;
                        file_found = 1;
                        print_log("[+] 파일 다운로드가 완료 되었습니다. ")
                        download_progress_count += 1
                        callback(download_progress_count,download_progress_length)
                    
                except Exception as e:
                    print_log("[-] Error : %s" % e)
                    download_progress_count += 1
                    isDownloadError = 1;
            
            if(file_found == 0):
                print_log("[-] Attached File not found !!")
                isDownloadError = 1;
    except Exception as e:
        print_log("[-] Error : %s" % e)
        isDownloadError = 1;

def download_count_naver(url):
    url_source = get_url_source_naver(url);
    if url_source is None:
        return 0;
    if url_source.find("t.static.blog/mylog") == -1:
        return 0;
    download_count = 0
    try:
        p_attached_file = re.compile(r"\s*.*aPostFiles\[1\] = JSON.parse\(\'\[(.*?)\]", re.IGNORECASE | re.DOTALL)
        result = p_attached_file.match(url_source).group(1)
        if result:
            data = "[" + result.replace('\\\'', '\"') + "]"
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
    global isDownloadError
    try:
        while url.find("PostView.naver") == -1 and url.find("PostList.naver") == -1:
            f = request.urlopen(url)
            url_info = f.info()
            url_charset = client.HTTPMessage.get_charsets(url_info)[0]
            url_source = f.read().decode(url_charset)

            # find 'NBlogWlwLayout.nhn'
            if url_source.find("NBlogWlwLayout.naver") == -1:
                print_log("\n[-] It is not a NAVER Blog")
                sys.exit(0)

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
        isDownloadError = 1;
        return None;

def download_tistory(url,callback):
    global isDownloadError,download_progress_count, download_progress_length
    url_source = get_url_source_tistory(url)

    if url_source is None:
        return

    # find 's1.daumcdn.net/cfs.tistory'
    if url_source.find("t1.daumcdn.net/tistory") == -1:
        print_log("[-] It is not a Tistory Blog")
        isDownloadError = 1;
        return;

    #text_to_file(get_url_source_tistory( "https://harnenim.github.io/WinPNG/Viewer.html?url=" + url), "hello.html");

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
                download_progress_count += 1
                callback(download_progress_count,download_progress_length)
        else:
            soup = BeautifulSoup(url_source, 'html.parser')
            temps = soup.find('div',class_="tt_article_useless_p_margin contents_style")    
        
            if(temps is None):
                temps = soup.find('div', {'class': 'contents_style'})

            links = temps.find_all("a")
            file_found = 0;

            p_attach = re.compile(r"(.*(googleusercontent).*)")
            p_google = re.compile(r"(.*(https://drive.google.com/file/d/).*)")

            for a in links:
                if a.get('href') == None:
                    continue;
                each_file = a.attrs['href']
                # print_log("href = "+each_file)
                try:
                    each_file = each_file.replace('&amp;','&');

                    # 구글 드라이브 주소가 검출되었을때
                    if bool(p_google.match(each_file)):

                        start_index = each_file.find("/d/") + 3;
                        end_index =  each_file.rfind("/view");

                        key = each_file[start_index:end_index]
                        each_file = "https://drive.google.com/uc?id="+key

                        remotefile = urlopen(each_file)
                        fileName = remotefile.headers.get_filename();

                        if fileName is not None:
                            fileName = fileName.encode('ISO-8859-1').decode('UTF-8');
                        else:
                            parsed_url = urlparse(each_file)
                            fileName = os.path.basename(parsed_url.path)
                            fileName = unquote(fileName)

                        path = outpath + smiDir

                        if fileName == "uc":
                            fileName = gdrive.get_file_name(each_file)
                    
                        if(not p_extension.match(fileName)):
                            download_progress_count += 1
                            callback(download_progress_count,download_progress_length)
                            continue;

                        print_log("[=] 다운로드 시작 => "+ fileName)

                        if not os.path.exists(path):
                            os.makedirs(path)

                        gdrive.download(each_file, path + fileName, quiet=False)
                        print_log("[+] 파일 다운로드가 완료 되었습니다. ")

                        file_found = 1;
                        download_progress_count += 1
                        callback(download_progress_count,download_progress_length)

                    # 일반 다운로드 주소가 검출되었을때
                    elif bool(p_attach.match(each_file)) == False:
                        print_log("  Link : %s" % each_file)
                        remotefile = urlopen(each_file)
                        fileName = remotefile.headers.get_filename();

                        if fileName is not None:
                            fileName = fileName.encode('ISO-8859-1').decode('UTF-8');
                        else:
                            parsed_url = urlparse(each_file)
                            fileName = os.path.basename(parsed_url.path)
                            fileName = unquote(fileName)

                        print_log("[=] 다운로드 시작 => "+fileName)

                        path = outpath + smiDir
                        if not os.path.exists(path):
                            os.makedirs(path)

                        download(each_file, path + fileName);
                        isDownloaded = 1;
                        file_found = 1;
                        print_log("[+] 파일 다운로드가 완료 되었습니다. ")
                        download_progress_count += 1
                        callback(download_progress_count,download_progress_length)
                    
                except Exception as e:
                    print_log("[-] Error : %s" % e)
                    print_log(traceback.format_exc())
                    download_progress_count += 1
                    isDownloadError = 1;
            
            if(file_found == 0):
                print_log("[-] Attached File not found !!")
                isDownloadError = 1;
    
    except Exception as e:
        print_log("[-] Error : %s" % e)
        print_log(traceback.format_exc())
        isDownloadError = 1;   

def download_count_tistory(url):
    url_source = get_url_source_tistory(url)

    if url_source is None:
        return 0
    
    if url_source.find("t1.daumcdn.net/tistory") == -1:
        return 0;

    download_count = 0

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
    global isDownloadError
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
        isDownloadError = 1;
        return None;

def download_blogspot(url,callback):
    global isDownloadError, download_progress_count, download_progress_length
    url_source = get_url_source_blogspot(url)

    if url_source is None:
        return

    # p_attach = re.compile(r"<div class=\'post-body.*?\'[^>]*>((?:(?:(?!<div[^>]*>|</div>).)+|<div[^>]*>([\s\S]*?)</div>)*)</div>", re.IGNORECASE | re.DOTALL)   
    # result = p_attach.findall(url_source)

    soup = BeautifulSoup(url_source, 'html.parser')
    temps = soup.find('div',class_="post-body")

    links = temps.find_all("a")

    p_attach = re.compile(r"(.*(googleusercontent).*)")
    p_google = re.compile(r"(.*(https://drive.google.com/file/d/).*)")
    p_google_2 = re.compile(r"(.*(https://docs.google.com/uc).*)")
    p_google_3 = re.compile(r"(.*(https://drive.usercontent.google.com/download).*)")

    isDownloaded = 0;

    for a in links:
        each_file = a.attrs['href']
        # print_log("href = "+each_file)
        try:
            each_file = each_file.replace('&amp;','&');

            if bool(p_google_2.match(each_file)):
                start_index = each_file.find("&id=") + 4;
                end_index =  each_file.rfind("&confirm");
                each_file = "https://drive.google.com/file/d/" + each_file[start_index:end_index] + "/view"
            
            if bool(p_google_3.match(each_file)):
                start_index = each_file.find("?id=") + 4;
                end_index =  each_file.rfind("&export");
                each_file = "https://drive.google.com/file/d/" + each_file[start_index:end_index] + "/view"

            # 구글 드라이브 주소가 검출되었을때
            if bool(p_google.match(each_file)):

                start_index = each_file.find("/d/") + 3;
                end_index =  each_file.rfind("/view");

                key = each_file[start_index:end_index]
                each_file = "https://drive.google.com/uc?id="+key

                remotefile = urlopen(each_file)
                fileName = remotefile.headers.get_filename();

                if fileName is not None:
                    fileName = fileName.encode('ISO-8859-1').decode('UTF-8');
                else:
                    parsed_url = urlparse(each_file)
                    fileName = os.path.basename(parsed_url.path)
                    fileName = unquote(fileName)

                path = outpath + smiDir

                if fileName == "uc":
                    fileName = gdrive.get_file_name(each_file)

                if(not p_extension.match(fileName)):
                    download_progress_count += 1
                    callback(download_progress_count,download_progress_length)
                    continue;

                print_log("[=] 다운로드 시작 => "+ fileName)

                if not os.path.exists(path):
                    os.makedirs(path)

                gdrive.download(each_file, path + fileName, quiet=False)
                print_log("[+] 파일 다운로드가 완료 되었습니다. ")
                    
                isDownloaded = 1;
                download_progress_count += 1
                callback(download_progress_count,download_progress_length)
            # 일반 다운로드 주소가 검출되었을때
            elif bool(p_attach.match(each_file)) == False:
                print_log("  Link : %s" % each_file)
                remotefile = urlopen(each_file)
                fileName = remotefile.headers.get_filename();

                if fileName is not None:
                    try:
                        fileName = fileName.encode('ISO-8859-1').decode('UTF-8');
                    except Exception as e:
                        fileName = fileName.encode('UTF-8').decode('ISO-8859-1');
                        fileName = fileName.encode('ISO-8859-1').decode('UTF-8');
                else:
                    parsed_url = urlparse(each_file)
                    fileName = os.path.basename(parsed_url.path)
                    fileName = unquote(fileName)

                if(not p_extension.match(fileName)):
                   download_progress_count += 1
                   callback(download_progress_count,download_progress_length)
                   continue;
                
                print_log("[=] 다운로드 시작 => "+fileName)

                path = outpath + smiDir
                if not os.path.exists(path):
                    os.makedirs(path)

                download(each_file, path + fileName);
                isDownloaded = 1;
                print_log("[+] 파일 다운로드가 완료 되었습니다. ")
                download_progress_count += 1
                callback(download_progress_count,download_progress_length)
            
        except Exception as e:
            print_log("[-] Error : %s" % e)
            print_log(traceback.format_exc())
            download_progress_count += 1
            isDownloadError = 1;

    if isDownloaded == 0:
        isDownloadError = 1;

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
    global isDownloadError
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
        isDownloadError = 1;
        return None;

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

