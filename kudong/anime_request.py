import requests
import json

from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.parse import unquote
from urllib.parse import quote

class AnimeInfo:

    def __init__(self,
                 animeNo,
                 status,
                 time,
                 subject,
                 genres,
                 startDate,
                 endDate,
                 captionCount,
                 website,
                 weekNo
                 ):
        self.animeNo = animeNo
        self.status = status
        self.time = time
        self.subject = subject
        self.genres = genres
        self.startDate = startDate
        self.endDate = endDate
        self.captionCount = captionCount
        self.website = website
        self.weekNo = weekNo

class SubsInfo:

    def __init__(self,
                 name,
                 episode,
                 updDt,
                 website):
        self.name = name
        self.episode = episode
        self.updDt = updDt
        self.website = website

class PageInfo:

    def __init__(self,
                 keyword,
                 pageNumber,
                 numberOfElements,
                 totalPages,
                 totalElements):
        self.keyword = keyword # 키워드
        self.pageNumber = pageNumber # 현재 페이지 번호 
        self.numberOfElements = numberOfElements # 해당 페이지의 요소 수
        self.totalPages = totalPages # 총 페이지 수
        self.totalElements = totalElements # 총 작품 수

class RecentInfo:

    def __init__(self,
                 animeNo,
                 subject,
                 episode,
                 updDt,
                 website,
                 name):
        self.animeNo = animeNo
        self.subject = subject
        self.episode = episode
        self.updDt = updDt
        self.website = website
        self.name = name

# 해당 요일의 분기 애니메이션 정보들를 가져옵니다.
def requestAnimeWeekInfo(week):
    list = []

    datas = None
    json_data = None

    try:
        response = requests.get("https://api.anissia.net/anime/schedule/" + str(week),timeout=3)
        datas = json.loads(response.text)
        json_data = datas["data"]
    except Exception as e:
        return None

    for k in json_data:

        animeNo = k['animeNo']
        status = k['status']
        time = k['time']
        subject = k['subject']
        genres = k['genres']
        startDate = k['startDate']
        endDate = k['endDate']
        captionCount = k['captionCount']
        website = unquote(k['website'])
        weekNo = week

        # print("ANIME SMI AUTO DOWNLOADER - Target => <"+subject+">")    
        # print("================================================================")
        # print("> animeNo: " + str(animeNo))
        # print("> status: " + status)
        # print("> time: " + time)
        # print("> subject: " + subject)
        # print("> genres: " + genres)
        # print("> startDate: " + startDate)
        # print("> endDate: " + endDate)
        # print("> captionCount: " + str(captionCount))
        # print("> website: " + website)
        # print("================================================================")

        list.append(AnimeInfo(animeNo,
                    status,
                    time,
                    subject,
                    genres,
                    startDate,
                    endDate,
                    captionCount,
                    website,
                    weekNo
                    ));
    return list

# 해당 애니메이션의 자막 정보를 가져옵니다.
def requestAnimeSubsInfo(anime):

    list = []

    datas = None
    json_data = None

    try:
        response = requests.get("https://api.anissia.net/anime/caption/animeNo/" + str(anime.animeNo))
        datas = json.loads(response.text)
        json_data = datas["data"]
    except Exception as e:
        return None

    for k in json_data:

        name = k['name']
        episode = k['episode']
        updDt = k['updDt']
        website = unquote(k['website'])

        list.append(SubsInfo(name,episode,updDt,website))

        # print("================================================================")
        # print("> 제작자: " + name)
        # print("> 회차: " + episode+"화")
        # print("> 업데이트: " + updDt)
        # print("> 주소: " + website)

    return list

# 해당 애니메이션의 정보와 자막정보를 가져옵니다.
def requestAnimeInfo(animeNo):

    list = []

    datas = None
    json_data = None

    try:
        response = requests.get("https://api.anissia.net/anime/animeNo/" + str(animeNo))
        datas = json.loads(response.text)
        json_data = datas["data"]
    except Exception as e:
        return None, None

    animeNo = json_data['animeNo']
    status = json_data['status']
    time = json_data['time']
    subject = json_data['subject']
    genres = json_data['genres']
    startDate = json_data['startDate']
    endDate = json_data['endDate']
    captionCount = json_data['captionCount']
    website = unquote(json_data['website'])
    weekNo = int(json_data['week'])

    info = AnimeInfo(animeNo,
                    status,
                    time,
                    subject,
                    genres,
                    startDate,
                    endDate,
                    captionCount,
                    website,
                    weekNo
                    );

    for k in json_data['captions']:

        name = k['name']
        episode = k['episode']
        updDt = k['updDt']
        website = unquote(k['website'])

        list.append(SubsInfo(name,episode,updDt,website))

        # print("================================================================")
        # print("> 제작자: " + name)
        # print("> 회차: " + episode+"화")
        # print("> 업데이트: " + updDt)
        # print("> 주소: " + website)

    return info, list

# 제목 검색시 나온 애니메이션 목록을 가져옵니다. 
def requestSearchAnimeInfo(keyword, page = 0):

    list = []

    datas = None
    json_data = None

    try:
        response = requests.get("https://api.anissia.net/anime/list/"+str(page)+"?q=" + quote(str(keyword)))
        datas = json.loads(response.text)
        json_data = datas["data"]
    except Exception as e:
        return None
    

    pageNumber = int(json_data["number"]) # 현재 페이지 번호 
    numberOfElements = int(json_data["numberOfElements"]) # 해당 페이지의 요소 수
    totalPages = int(json_data["totalPages"]) # 총 페이지 수
    totalElements = int(json_data["totalElements"]) # 총 작품 수

    pageInfo = PageInfo(
        keyword,
        pageNumber,
        numberOfElements,
        totalPages,
        totalElements
    );

    for k in json_data["content"]:

        animeNo = k['animeNo']
        status = k['status']
        time = k['time']
        subject = k['subject']
        genres = k['genres']
        startDate = k['startDate']
        endDate = k['endDate']
        captionCount = k['captionCount']
        website = unquote(k['website'])
        weekNo = int(k['week'])

        list.append(AnimeInfo(animeNo,
                    status,
                    time,
                    subject,
                    genres,
                    startDate,
                    endDate,
                    captionCount,
                    website,
                    weekNo
                    ));
    return list, pageInfo

# 키워드 자동완성에서 검색된 작품을 가져옵니다.
def requestSearchAnimeCorrect(keyword):

    list = []

    datas = None
    json_data = None

    try:
        response = requests.get("https://api.anissia.net/anime/autocorrect?q=" + quote(str(keyword)))
        datas = json.loads(response.text)
        json_data = datas["data"]
    except Exception as e:
        return None
    
    for k in json_data:
        list.append(k);

    return list

# 최근 업로드된 자막정보를 가져옵니다. 
def requestRecentAnimeInfo(page = 0):

    list = []

    datas = None
    json_data = None

    try:
        response = requests.get("https://api.anissia.net/anime/caption/recent/"+str(page))
        datas = json.loads(response.text)
        json_data = datas["data"]
    except Exception as e:
        return None
    
    pageNumber = int(json_data["number"]) # 현재 페이지 번호 
    numberOfElements = int(json_data["numberOfElements"]) # 해당 페이지의 요소 수
    totalPages = int(json_data["totalPages"]) # 총 페이지 수
    totalElements = int(json_data["totalElements"]) # 총 작품 수

    pageInfo = PageInfo(
        "",
        pageNumber,
        numberOfElements,
        totalPages,
        totalElements
    );

    for k in json_data["content"]:

        animeNo = k['animeNo']
        subject = k['subject']
        episode = k['episode']
        updDt = k['updDt']
        website = unquote(k['website'])
        name = k['name']

        list.append(RecentInfo(animeNo,
                    subject,
                    episode,
                    updDt,
                    website,
                    name
                    ));
    
    return list, pageInfo

if __name__ == "__main__":
    # list = requestAnimeWeekInfo(0);

    list, pageInfo = requestSearchAnimeInfo("",106);

    print("> keyword: " + str(pageInfo.keyword))
    print("> pageNumber: " + str(pageInfo.pageNumber))
    print("> numberOfElements: " + str(pageInfo.numberOfElements))
    print("> totalPages: " + str(pageInfo.totalPages))
    print("> totalElements: " + str(pageInfo.totalElements))

    for k in list:
        print("ANIME SMI AUTO DOWNLOADER - Target => <"+k.subject+">")    
        print("================================================================")
        print("> animeNo: " + str(k.animeNo))
        print("> status: " + k.status)
        print("> time: " + k.time)
        print("> subject: " + k.subject)
        print("> genres: " + k.genres)
        print("> startDate: " + k.startDate)
        print("> endDate: " + k.endDate)
        print("> captionCount: " + str(k.captionCount))
        print("> website: " + k.website)



