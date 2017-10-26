import sys, time, os, getopt
import logging
import numpy as np
from modules.colors import *
from modules.workreturn import *
from urllib.request import urlopen
from bs4 import BeautifulSoup

def urlGET(url, sType, toGet):
    parsableInfo = ["title", "group_id", "description", "media_id", "episode", "url", "img"]
    returnList = []

    if toGet not in parsableInfo:
        print(RED + "[ERRO]" + WHITE + "Can't parse '" + RED + toGet + WHITE + "'..")
        return None
    page = urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    for script in soup("script"):
        script.extract()


    if toGet == parsableInfo[0]:
        if sType == "serie":
            for span in soup.find_all("span", attrs={'class':'series-title block ellipsis', 'dir':'auto'}):
                if span.get_text() != None:
                    returnList.append(' '.join(span.get_text().split()).replace("’", "'"))
        elif sType == "media":
            for a in soup.find_all("a", attrs={'class':'portrait-element block-link titlefix episode'}):
                if a.get("title") != None:
                    try:
                        returnList.append(' '.join(a.get("title").split())[:a.get("title")].replace("’", "'"))
                    except:
                        returnList.append(' '.join(a.get("title").split()).replace("’", "'"))
                        pass
                else:
                    returnList.append("null")
    elif toGet == parsableInfo[1]:
        if sType == "serie":

            for li in soup.find_all("li"):
                if li.get("group_id") != None:
                    returnList.append(li.get("group_id"))
        elif sType == "media":

            for div in soup.find_all("div", attrs={'class':'episode-progress'}):
                if div.get("media_id") != None:
                    returnList.append(div.get("media_id"))
                else:
                    returnList.append("null")

    elif toGet == parsableInfo[2]:
        if sType == "serie":

            for meta in soup.find_all("meta", attrs={'property':'og:description'}):
                if meta.get("content") != None:
                    returnList.append(meta.get("content"))
                else:
                    returnList.append("null")

        elif sType == "media":

            for p in soup.find_all("p", attrs={'class':'short-desc', 'dir':'auto'}):
                if p.get_text() != None:
                    returnList.append(' '.join(p.get_text().split()))
                else:
                    returnList.append("null")

    elif toGet == parsableInfo[4]:
        if sType == "serie":

            for span in soup.find_all("span", attrs={'class':'series-data block ellipsis'}):
                if span.get_text() != None:
                    returnList.append(' '.join(span.get_text().split()).replace(" Videos", ""))
                else:
                    returnList.append('0')

        elif sType == "media":
            for span in soup.find_all("span", attrs={'class':'series-title block ellipsis', 'dir':'auto'}):
                if span.get_text() != None:
                    returnList.append(' '.join(span.get_text().split()).replace("Episode ", ""))
                else:
                    returnList.append("null")
    elif toGet == parsableInfo[5]:
        if sType == "serie":

            for a in soup.find_all("a", attrs={'token':'shows-portraits', 'itemprop':'url'}):
                if a.get("href") != None:
                    returnList.append("http://www.crunchyroll.com" + ' '.join(a.get("href").split()))
                else:
                    returnList.append('Unknown')

        elif sType == "media":

            for a in soup.find_all("a", attrs={'class':'portrait-element block-link titlefix episode'}):
                if a.get("href") != None:
                    returnList.append("http://www.crunchyroll.com" + ' '.join(a.get("href").split()))
                else:
                    returnList.append("null")

    elif toGet == parsableInfo[6]:
        if sType == "serie":

            for img in soup.find_all("img", attrs={'itemprop':'photo', 'class':'portrait'}):
                if img.get("src") != None:
                    returnList.append(' '.join(img.get("src").split()))

        elif sType == "media":

            for img in soup.find_all("img", attrs={'class':'landscape'}):
                if img.get("src") != None:
                    returnList.append(' '.join(img.get("src").split()))
                else:
                    returnList.append("null")

    else:
        print(RED + "[ERRO]" + WHITE + "Can't parse '" + RED + toGet + WHITE + "'..")
        return None
    return returnList
