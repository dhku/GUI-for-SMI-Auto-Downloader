import requests
import json
from urllib.request import urlopen
from urllib.parse import unquote
from urllib.parse import urlparse

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


def requestAnimeWeekInfo(week):
    list = []

    try:
        response = requests.get("https://api.anissia.net/anime/schedule/" + str(week),timeout=3)
    except Exception as e:
        return None

    datas = json.loads(response.text)
    json_data = datas["data"]

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


def requestAnimeSubsInfo(anime):

    list = []

    response = requests.get("https://api.anissia.net/anime/caption/animeNo/" + str(anime.animeNo))

    datas = json.loads(response.text)
    json_data = datas["data"]

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

def requestAnimeInfo(animeNo):

    list = []

    response = requests.get("https://api.anissia.net/anime/animeNo/" + str(animeNo))

    datas = json.loads(response.text)
    json_data = datas["data"]

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

def requestSearchAnimeInfo(keyword):

    list = []

    response = requests.get("https://api.anissia.net/anime/list/0?q=" + str(keyword))
    datas = json.loads(response.text)
    json_data = datas["data"]

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
    return list

def requestSearchAnimeCorrect(keyword):

    list = []
    response = requests.get("https://api.anissia.net/anime/autocorrect?q=" + str(keyword))
    datas = json.loads(response.text)
    json_data = datas["data"]

    for k in json_data:
        list.append(k);

    return list

if __name__ == "__main__":
    list = requestAnimeWeekInfo(0);

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



