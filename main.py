import sys, time, os, getopt
import logging
import tqdm
import numpy as np
import subprocess
import glob
from progressbar import *
import progressbar
from modules.colors import *
from modules.workreturn import *
from modules.parse import *
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import json
import base64
import datetime

login_data = {
    'name': 'user',
    'password': 'password',
    'formname': 'RpcApiUser_Login' # Dont change this
}


dumpVariablesOnExit = False
verbose = True
if os.path.isfile("verbose.txt"):
    os.remove("verbose.txt")
outFolder = "dump"
toFolder = False
extract = "None"
pURL = ""
stringD = ""
# General Strings
validExtracts = ["title:serie", "title:all:serie", "title:media", "title:all:media",  "id:serie", "id:all:serie", "id:media", "id:all:media", "url:serie", "url:all:serie", "url:media", "url:all:media", "img:serie", "img:all:serie", "img:media", "img:all:media", "description:serie", "description:all:serie", "description:media", "description:all:media"]

# Specific Strings
validExtracts.extend(["episode:serie", "episode:all:serie", "episode:media", "episode:all:media"])
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
def setup_debug(name, log_file, level=logging.DEBUG):
    """Function setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
def main(argv):
    global extract, outFolder, toFolder, validExtracts, stringD, pURL
    helpObjects = ["-e", "--extract", "-d", "--dump", "--dump-folder", "-h", "--help", "-s", "--string", "--key", "--password", "--pass", "-k", "--user", "-u"]
    helpText = dict.fromkeys(['-e', '--extract'], "Extracts specified parsed information. To get a list of available information try: 'main.py -e list' ")
    helpText.update(dict.fromkeys(['-d', '--dump'], "Dumps parsed series and episode info to individual files in dump folder, or a folder specified with 'main.py -d --dump-folder <folder>'"))
    helpText.update(dict.fromkeys(['--dump-folder', '--df'], "Set dump folder for argument 'main.py --dump'"))
    helpText.update(dict.fromkeys(['-s', '--string'], "Required parameter for certain ('--extract')'s. Hard to explain. Look at examples."))
    helpText.update(dict.fromkeys(['-p', '--parse'], "Set a CrunchyRoll serie site for parsing"))
    helpText.update(dict.fromkeys(['-u', '--user'], "Set a CrunchyRoll username to login. This is optional and lets the program get info on content that is usually blocked to guests"))
    helpText.update(dict.fromkeys(['-k', '--pass', '--password', '--key'], "Set a CrunchyRoll password to login. This is optional and lets the program get info on content that is usually blocked to guests"))
    # print(helpText['-d'])
    try:
        opts, args = getopt.getopt(argv,"dh:e:o:p:u:k",["help=", "extract=", "output=", "string=", "parse=", "dump-folder=", "user=", "pass=", "key=", "password="])
    except getopt.GetoptError:
        print ("'main.py -h' for information on arguments")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            if arg in helpObjects:
                print(helpText[arg])
            elif "-" + arg in helpObjects:
                print(helpText["-" + arg])
            elif "--" + arg.replace(" ", "-") in helpObjects:
                print(helpText["--" + arg.replace(" ", "-")])
            else:
                print ('main.py -e <extract information> -d (dumps parsed information to individual files) --dump-folder (set folder to dump files to)')
            sys.exit()
        elif opt in ("-e", "--extract"):
            if arg == "list":
                print("Valid extract strings: ")
                prev = ""
                for c in validExtracts:
                    if c.split(":")[0] != prev:
                        prev = c.split(":")[0]
                        print("~~ " + prev + " ~~")
                    print("  >> " + c)
                sys.exit(0)
            else:
                if arg in validExtracts:
                    print("valid")
                    extract = arg
                else:
                    print("invalid parameter - do 'main.py --help extract' for more information")
                    sys.exit(2)
        elif opt in ("-s", "--string"):
            stringD = arg
        elif opt in ("-p", "--parse"):
            pURL = arg
        elif opt in ("-d", "--dump"):
            toFolder = True
        elif opt in ("-o", "--outputfolder", "--output", "--outfolder", "--ofolder", "--odir", "--outdir", "--dump-folder"):
            outFolder = arg
        elif opt in ('-u', '--user'):
            login_data['name'] = arg
        elif opt in ('-k', '--pass', '--password', '--key'):
            login_data['password'] = arg
    if extract != "None":
        if len(extract.split(":")) >= 3 and extract.split(":")[1] == "all":
            print("Request all %s's from '%s'." % (extract.split(":")[0], extract.split(":")[2]))
        else:
            if stringD == "":
                print("Sorry, but to run this task, '-s or --string' must be set.")
                sys.exit(2)
    # print('toFolder = " ' + str(toFolder))
    # print('outFolder = " ' + outFolder)
    # print('extract = " ' + extract)
    # if stringD != "":
    #     print('stringD = " ' + stringD)
if __name__ == "__main__":
   main(sys.argv[1:])

def verbose_write(text):
    # print(text)
    text = str(text)
    with open("verbose.txt", 'a', encoding='UTF-8') as f:
        f.write(datetime.datetime.now().strftime("%d-%m-%y %H:%M:%S - ") + text + "\n")
    return


def list_duplicates_of(seq,item):
    start_at = -1
    locs = []
    while True:
        try:
            loc = seq.index(item,start_at+1)
        except ValueError:
            break
        else:
            locs.append(loc)
            start_at = loc
    return locs
def clean_title(val, filename = False):
    val = str(val)
    if not filename:
        return val.replace("\"", "'").replace("/", "_").replace("\\", "").replace("\'", "\\'").encode('utf-8')
    else:
        return val.replace(":","_").replace("?", "").replace("*", "").replace("\"", "'").replace("/", "_").replace("\\", "")
def getReturn(noColor=False):
    if noColor:
        st = "* %s %s" % (work.returnCode, work.returnMessage)
    else:
        st = WHITE + "%s* %s %s%s" % (work.returnCodeColor, work.returnCode, work.returnMessageColor, work.returnMessage)
    return st
def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""
    if verbose:
        verbose_write("* INFO Logger set up! ({}:{}:{})".format(name, log_file, level))
    else:
        print(">> Logger set up! ({}:{}:{})".format(name, log_file, level))
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

print(CYAN + "* INFO " + WHITE + "Initializing loggers", end='')
verbose_write("* INFO Initializing loggers! ")

try:
    debug = setup_debug('main_debug', 'main.log')
    print(".. ")
    work.returnCode = "SUCC"
    work.returnMessage = "Loggers initialized"
    work.returnCodeColor = work.Success
except Exception as e:
    print(e.args)
if verbose:
    verbose_write(getReturn(True))
else:
    print(getReturn(True))
print()
if extract == "None" and not toFolder:
    work.returnCode = "INPUT"
    work.returnMessage = "Before we begin. Do you want to export all information to individual files? (Y): "
    work.returnCodeColor = work.InputC
    if not toFolder:
        print(getReturn())
        if input(">>>> ").upper() == "Y":
            toFolder = True
if verbose:
    verbose_write("* INFO Updating list of series..")
else:
    print("* INFO Updating list of series..")
# print(CYAN + "* INFO " + WHITE + "Updating list of series..")
wiki = "http://www.crunchyroll.com/videos/anime/all?group=all"
debug.debug('Open URL: ' + wiki)
if verbose:
    verbose_write("* INFO Opening page '{}' for parsing..".format(wiki))
else:
    print(">> * INFO Opening page '{}' for parsing..".format(wiki))
# print(">> " + CYAN + "* INFO " + WHITE + "Opening page '%s' for parsing.." % wiki)
opened = False
values = {}
valueList = []
show_group_ids = []
show_titles = []
show_video_count = []
show_urls = []
show_imgs = []
show_descriptions = []
try:
    with requests.Session() as s:
        if login_data['name'] != "user":
            if verbose:
                verbose_write("* INFO Trying to login as '{}' for parsing..".format(login_data['name']))
            else:
                print(">> * INFO Trying to login as '{}' for parsing..".format(login_data['name']))
            # print(">> " + CYAN + "* INFO " + WHITE + "Trying to login as '%s' for parsing.." % login_data['name'])
            s.post('https://www.crunchyroll.com/?a=formhandler', data=login_data)
            page = s.get(wiki)
            page = str(page.text)
            opened = True
        else:
            try:
                if verbose:
                    verbose_write("* INFO Trying to open page as guest for parsing..")
                else:
                    print(">> * INFO Trying to open page as guest for parsing..")
                # print(">> " + CYAN + "* INFO " + WHITE + "Trying to open page as guest for parsing..")
                page = urlopen(wiki)
                opened = True
            except Exception as e:
                if verbose:
                    verbose_write("[WARN] Unable to converse with CrunchyRoll\n> " + str(e.args))
                else:
                    print("[WARN] Unable to converse with CrunchyRoll")
                opened = False
                debug.debug('URL open')
except:
    try:
        print(">> " + CYAN + "* INFO " + WHITE + "Trying to open page as guest for parsing.." % login_data['name'])
        page = urlopen(wiki)
        opened = True
    except Exception as e:
        if verbose:
            verbose_write("[WARN] Unable to converse with CrunchyRoll\n> " + str(e.args))
        else:
            print("[WARN] Unable to converse with CrunchyRoll")
        opened = False
        debug.debug('URL open')
if opened:
    soup = BeautifulSoup(page, "html.parser")
    debug.debug('URL - Parsing..')
    for script in soup("script"):
        script.extract()
        debug.debug('URL - Extract Scripts..')
    if verbose:
        verbose_write("* INFO Start Parsing..")
    else:
        print(CYAN + "* INFO " + WHITE + "Start Parsing..")
    for li in soup.find_all("li"):
        if li.get("group_id") != None:
            show_group_ids.append(li.get("group_id"))
    debug.debug('GET - group_id..')
    for span in soup.find_all("span", attrs={'class':'series-data block ellipsis'}):
        if span.get_text() != None:
            show_video_count.append(' '.join(span.get_text().split()).replace(" Videos", ""))
        else:
            show_video_count.append('0')
    debug.debug('GET - video_count..')
        # print(' '.join(span.get_text().split()))
    for a in soup.find_all("a", attrs={'token':'shows-portraits', 'itemprop':'url'}):
        if a.get("href") != None:
            show_urls.append("http://www.crunchyroll.com" + ' '.join(a.get("href").split()))
        else:
            show_video_count.append('Unknown')
    debug.debug('GET - show_URL..')
        # print(' '.join(span.get_text().split()))
    for span in soup.find_all("span", attrs={'class':'series-title block ellipsis', 'dir':'auto'}):
        if span.get_text() != None:
            show_titles.append(' '.join(span.get_text().split()).replace("’", "'"))
    debug.debug('GET - show_title..')
    for img in soup.find_all("img", attrs={'itemprop':'photo', 'class':'portrait'}):
        if img.get("src") != None:
            show_imgs.append(' '.join(img.get("src").split()))
    debug.debug('GET - image..')
    showsA = list(zip(show_group_ids, show_titles, show_video_count, show_urls, show_imgs))

    dups = len(show_group_ids)*[None]
    dupes = []
    for i, e in enumerate(show_group_ids):
        # print(i,e)
        if e not in dups:
            dups[i] = e
        else:
            dups[i] = e
            dupes.append(i)
    show_titles = show_titles[:-5]
    if len(show_group_ids) > len(show_titles):
        show_group_ids = show_group_ids[:-(len(show_group_ids) - len(show_titles))]
    if len(show_imgs) > len(show_titles):
        show_imgs = show_imgs[:-(len(show_imgs) - len(show_titles))]
    if len(show_video_count) > len(show_titles):
        show_video_count = show_video_count[:-(len(show_video_count) - len(show_titles))]
    if len(show_urls) > len(show_titles):
        show_urls = show_urls[:-(len(show_urls) - len(show_titles))]
    # if len(dupes) > 0:
    #     print(len(dups), len(dupes))
    # print("Title: %s\r\n>> ID: %s\r\n>> Episodes: %s\r\n>> URL: %s\r\n>> IMG: %s" % (len(show_titles), len(show_group_ids), len(show_video_count), len(show_urls), len(show_imgs)))
    #     print("Duplicate entries found: ")
    x=0
    while x != len(show_group_ids):
        # print("Title: %s\r\n>> ID: %s\r\n>> Episodes: %s\r\n>> URL: %s\r\n>> IMG: %s" % (show_titles[x], show_group_ids[x], show_video_count[x], show_urls[x], show_imgs[x]))
        # debug.info("Title: %s\r\n>> ID: %s\r\n>> Episodes: %s\r\n>> URL: %s\r\n>> IMG: %s" % (show_titles[x], show_group_ids[x], show_video_count[x], show_urls[x], show_imgs[x]))
        x += 1
    # print("Items in lists: \r\nTitle: %s\r\n>> ID: %s\r\n>> Episodes: %s\r\n>> URL: %s\r\n>> IMG: %s" % (len(show_titles), len(show_group_ids), len(show_video_count), len(show_urls), len(show_imgs)))
    # debug.info("Title: %s\r\n>> ID: %s\r\n>> Episodes: %s\r\n>> URL: %s\r\n>> IMG: %s" % (len(show_titles), len(show_group_ids), len(show_video_count), len(show_urls), len(show_imgs)))

    errors = 0
    errorEncountered = False
    if extract != "None":
        if (len(extract.split(":")) >= 3):
            thang = extract.split(":")[2]
            thang2 = extract.split(":")[0]
            if thang == "serie":
                if thang2 == "id":
                    toExtract = show_group_ids
                elif thang2 == "title":
                    toExtract = show_titles
                elif thang2 == "url":
                    toExtract = show_urls
                elif thang2 == "img":
                    toExtract = show_imgs
                elif thang2 == "description":
                    toExtract = show_descriptions
                elif thang2 == "episode":
                    toExtract = show_video_count
                f = open("parser.out", 'w', encoding="utf-8")
                f.write(extract + ": \r\n" + str(toExtract) + "\r\n")
                f.close()  # you can omit in most cases as the destructor will call it
                if dumpVariablesOnExit:
                    f = open("variableDump.txt", 'w', encoding="utf-8")
                    f.write(str(list(zip(show_group_ids, show_titles, show_video_count, show_urls, show_imgs))) + "\r\n")
                    f.close()  # you can omit in most cases as the destructor will call it
                sys.exit(0);
        else:
            if extract != "None" and stringD == "":
                print("No string was specified. Please do so using: 'main.py -e %s -s or --string <string>'" % extract)
                errors += 1
                errorEncountered = True
                if dumpVariablesOnExit:
                    f = open("variableDump.txt", 'w', encoding="utf-8")
                    f.write(str(list(zip(show_group_ids, show_titles, show_video_count, show_urls, show_imgs))) + "\r\n")
                    f.close()  # you can omit in most cases as the destructor will call it
                sys.exit(2)
            else:
                i = stringD
                extractIndexes = []
                toExtract = []
                if extract.split(":")[0] == "id":
                    if extract.split(":")[1] == "serie":
                        if i in show_titles:
                            values = np.array(show_titles)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_descriptions:
                            values = np.array(show_descriptions)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_video_count:
                            values = np.array(show_video_count)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_urls:
                            values = np.array(show_urls)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_imgs:
                            values = np.array(show_imgs)
                            extractIndexes = np.where(values == i)[0]
                        else:
                            print(RED + "[ERRO] " + WHITE + "Couldn't find a match with current parameters, [%s:%s] (%s) - (%s)" % (extract.split(":")[0], extract.split(":")[1], i, extractIndexes))
                            errors += 1
                            errorEncountered = True
                        for ex in extractIndexes:
                            toExtract.append(show_group_ids[ex])
                elif extract.split(":")[0] == "title":
                    if extract.split(":")[1] == "serie":
                        if i in show_group_ids:
                            values = np.array(show_group_ids)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_descriptions:
                            values = np.array(show_descriptions)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_video_count:
                            values = np.array(show_video_count)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_urls:
                            values = np.array(show_urls)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_imgs:
                            values = np.array(show_imgs)
                            extractIndexes = np.where(values == i)[0]
                        else:
                            print(RED + "[ERRO] " + WHITE + "Couldn't find a match with current parameters, [%s:%s] (%s) - (%s)" % (extract.split(":")[0], extract.split(":")[1], i, extractIndexes))
                            errors += 1
                            errorEncountered = True
                        for ex in extractIndexes:
                            toExtract.append(show_titles[ex])
                elif extract.split(":")[0] == "url":
                    if extract.split(":")[1] == "serie":
                        if i in show_group_ids:
                            values = np.array(show_group_ids)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_descriptions:
                            values = np.array(show_descriptions)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_video_count:
                            values = np.array(show_video_count)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_titles:
                            values = np.array(show_titles)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_imgs:
                            values = np.array(show_imgs)
                            extractIndexes = np.where(values == i)[0]
                        else:
                            print(RED + "[ERRO] " + WHITE + "Couldn't find a match with current parameters, [%s:%s] (%s) - (%s)" % (extract.split(":")[0], extract.split(":")[1], i, extractIndexes))
                            errors += 1
                            errorEncountered = True
                        for ex in extractIndexes:
                            toExtract.append(show_urls[ex])
                elif extract.split(":")[0] == "img":
                    if extract.split(":")[1] == "serie":
                        if i in show_group_ids:
                            values = np.array(show_group_ids)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_descriptions:
                            values = np.array(show_descriptions)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_video_count:
                            values = np.array(show_video_count)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_titles:
                            values = np.array(show_titles)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_urls:
                            values = np.array(show_urls)
                            extractIndexes = np.where(values == i)[0]
                        else:
                            print(RED + "[ERRO] " + WHITE + "Couldn't find a match with current parameters, [%s:%s] (%s) - (%s)" % (extract.split(":")[0], extract.split(":")[1], i, extractIndexes))
                            errors += 1
                            errorEncountered = True
                        for ex in extractIndexes:
                            toExtract.append(show_imgs[ex])

                elif extract.split(":")[0] == "description":
                    if extract.split(":")[1] == "serie":
                        if i in show_group_ids:
                            values = np.array(show_group_ids)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_imgs:
                            values = np.array(show_imgs)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_video_count:
                            values = np.array(show_video_count)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_titles:
                            values = np.array(show_titles)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_urls:
                            values = np.array(show_urls)
                            extractIndexes = np.where(values == i)[0]
                        else:
                            print(RED + "[ERRO] " + WHITE + "Couldn't find a match with current parameters, [%s:%s] (%s) - (%s)" % (extract.split(":")[0], extract.split(":")[1], i, extractIndexes))
                            errors += 1
                            errorEncountered = True
                        for ex in extractIndexes:
                            to = urlGET(show_urls[ex], "serie", "description")
                            # print(to)
                            toExtract.append(str(to).replace("['", "").replace("[\"", "").replace("']", "").replace("\"]", ""))
                elif extract.split(":")[0] == "episode":
                    if extract.split(":")[1] == "serie":
                        if i in show_group_ids:
                            values = np.array(show_group_ids)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_imgs:
                            values = np.array(show_imgs)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_descriptions:
                            values = np.array(show_descriptions)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_titles:
                            values = np.array(show_titles)
                            extractIndexes = np.where(values == i)[0]
                        elif i in show_urls:
                            values = np.array(show_urls)
                            extractIndexes = np.where(values == i)[0]
                        else:
                            print(RED + "[ERRO] " + WHITE + "Couldn't find a match with current parameters, [%s:%s] (%s) - (%s)" % (extract.split(":")[0], extract.split(":")[1], i, extractIndexes))
                            errors += 1
                            errorEncountered = True
                        for ex in extractIndexes:
                            toExtract.append(show_video_count[ex])
                if not errorEncountered and errors == 0:
                    print(GREEN + "[SUCC]" + WHITE + " Search-item found!\r\nResult:\r\n")
                    print(extract + ": \r\n" + str(toExtract) + "\r\n")
                else:
                    print(GREEN + "[ERRO]" + WHITE + " " + str(errors) + " Errors encounterd!\r\nResult:\r\n")
                    print(extract + ": \r\n" + str(toExtract) + "\r\n")
                f = open("parser.out", 'w', encoding="utf-8")
                f.write(extract + ": \r\n" + str(toExtract) + "\r\n")
                f.close()  # you can omit in most cases as the destructor will call it
                print(MAGENTA + "EXIT" + WHITE + " Task Complete.")
                if dumpVariablesOnExit:
                    f = open("variableDump.txt", 'w', encoding="utf-8")
                    f.write(str(list(zip(show_group_ids, show_titles, show_video_count, show_urls, show_imgs))) + "\r\n")
                    f.close()  # you can omit in most cases as the destructor will call it
                sys.exit(0);
    # for key in showsA:
    work.returnCode = "SUCC"
    work.returnCodeColor = work.Success
    work.returnMessage = "Parsing Complete. Applying update.."
    verbose_write(getReturn(True))
time.sleep(2)
descCount = 0
show_descriptions = []
def get_change(current, previous):
    if current == previous:
        return 999.9
    try:
       return ((abs(current - previous))/current)*100
    except ZeroDivisionError:
        return 100.0
date = time.strftime("%d.%m.%Y")
if not os.path.isfile("parsed/all_group=all - %s.crdl" % date):
    if not os.path.exists("parsed"):
        os.makedirs("parsed")
    print("Do you want to download all show information? This only needs to be done once in a while to collect information on new series and descriptions.  \r\n This process might take some time, as it loops through all show sites to get information. \r\n If you skip this process, you will not be able to see show descriptions in 'all_group=all' files.\r\n  You will also have to parse CrunchyRoll's main site each time this applications is used.")
    it = input("(Y): ")
    if it.upper() == "Y":
        pbar = tqdm.tqdm(show_urls)
        pbar.unit = "URLs"
        # pbar.mininterval = 2
        pbar.ncols = 75
        # pbar.dynamic_ncols = True
        pbar.bar_format = "{desc} {percentage:3.2f}% |{bar}{r_bar}"
        pbar.desc = "Connected"
        opened = False
        for utd in pbar:
            if verbose:
                verbose_write("* INFO Scanning '{}'..".format(utd))
            descCount += 1
            # print("{0:.2f}".format(100-get_change(len(show_urls), descCount)) + "% [%-20s]...      "% '='*descCount, end="\r", flush=True)
            # pbar.update(len(show_urls)/10)
            # pbar.set_description("Processing %s" % utd)

            try:
                page = urlopen(utd)
                opened = True
                pbar.desc = "Connected"
            except Exception as e:
                opened = False
                pbar.desc = "No internet connection"
                if verbose:
                    verbose_write("* WARN : " + str(e.args))
            if opened:
                soup = BeautifulSoup(page, "html.parser")
                for script in soup("script"):
                    script.extract()
                for meta in soup.find_all("meta", attrs={'property':'og:description'}):
                    if meta.get("content") != None:
                        show_descriptions.append(meta.get("content"))
                    else:
                        show_descriptions.append("null")
else:
    list_of_files = glob.glob('parsed/*') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    if verbose:
        verbose_write("* WARN Already scanned main page")
        verbose_write("* INFO Loading from '{}'..".format(latest_file))
    with open(latest_file, encoding="utf8") as f:
        content = json.load(f)
    # you may also want to remove whitespace characters like `\n` at the end of each line
    # content = [x.strip() for x in list(filter(None, content))]
    # show_dict_list = list(filter(None, content)) # fastest
    # show_dict_list_tmp = []
    # for y in show_dict_list:
    #     show_dict_list_tmp.append(y.replace("},", "}").replace("[{'", "{'"))
    # show_dict_list = show_dict_list_tmp
    # del show_dict_list_tmp
    # for c in show_dict_list:
    #     lisP = eval(c)
        # print("Group ID: %s\r\nTitle: %s\r\nEpisodes: %s\r\nDescription: %s\r\nImage: %s\r\nURL: %s\r\n##################################################" % (lisP['group_id'], lisP['title'], lisP['video_count'], lisP['description'], lisP['img'], lisP['url']))
        # input("")
    for c in content:
        show_descriptions.append(content[c]['description'])
allvalues = {}
widgets = [FormatLabel('Parsing Data'), ' ', Percentage(), ' ', Bar('#'), ' ', RotatingMarker()]
files = []
counter = 0
with progressbar.ProgressBar(widgets=widgets, max_value=len(show_group_ids)) as bar:
    for c in show_group_ids:
        values = {}
        values['group_id'] = c
        values['title'] = show_titles[show_group_ids.index(c)]
        values['video_count'] = show_video_count[show_group_ids.index(c)]
        try:
            values['description'] = show_descriptions[show_group_ids.index(c)]
        except Exception as e:
            if verbose:
                verbose_write("* WARN " + str(e.args))
        values['url'] = show_urls[show_group_ids.index(c)]
        values['img'] = show_imgs[show_group_ids.index(c)]
        allvalues[values['title']] = values
        # value = {values['title']:values}
        valueList.append(values)
        mysqllog.info('Sending information to mySql database')
        # pr = (">>  Adding '%s'") % show_titles[show_group_ids.index(c)]
        # pr = (CYAN + ">> " + WHITE + " Adding '" + RED + "%s") % show_titles[show_group_ids.index(c)]
        indent = 75
        count = 0
        spaces=""
        while count != indent-len(show_titles[show_group_ids.index(c)]):
            if indent-len(show_titles[show_group_ids.index(c)]) < 0:
                break
            spaces+=" "
            count+=1
        counter += 1
        # time.sleep(.000000000000000000000000000000001)
        # widgets[0] = FormatLabel('{0}'.format(show_titles[show_group_ids.index(c)]))
        bar.update(counter)
print(YELLOW + "* INFO" + WHITE + " Done\n")
    # print("Sending data took %s seconds" % bar.)
# print(valueList)
#def printf(msg, color):
#    sys.stdout.write(color)
#    print "
date = time.strftime("%d.%m.%Y")
if not os.path.isfile("parsed/all_group=all - %s.crdl" % date):
    if not os.path.exists("parsed"):
        os.makedirs("parsed")
    f = open("parsed/all_group=all - %s.crdl" % date, 'w', encoding="utf-8")
    # f.write(json.dumps(valueList, indent=4, sort_keys=True))
    # f.write(json.dumps(allvalues))
    f.write(json.dumps(allvalues, indent=4, sort_keys=True))
    # f.write(json.dumps(str(valueList).replace("}, {", "}, \n{").replace("“", "\"").replace("”", "\"").replace("’", "'").replace("_","_").replace("'", "\'"), indent=4, sort_keys=True))
    f.close()  # you can omit in most cases as the destructor will call it

urlsToParse = show_urls
if pURL != "":
    show_urls.append(pURL)
    # print(show_urls[-1:])
    urlsToParse = show_urls[-1:]
    # print(urlsToParse)
counter = 0
totalUrls = len(show_urls)

isMulti = True
try:
    if extract.split(":")[1] == "media" or extract.split(":")[2] == "media" or extract == "":
        isMulti = True
except:
    isMulti = True

if isMulti:
    if verbose:
        verbose_write(("\n* INFO Parsing individual series."))
    else:
        print("\n" + YELLOW + "* INFO" + WHITE + " Parsing individual series.")
    pbar = tqdm.tqdm(urlsToParse)
    pbar.unit = "URLs"
    # pbar.mininterval = 2
    pbar.ncols = 75
    # pbar.dynamic_ncols = True
    pbar.bar_format = "{desc} {percentage:3.2f}% |{bar}{r_bar}"
    pbar.desc = "Parsing.. "

    for url in pbar:
        if verbose:
            verbose_write("* INFO Parsing '{}'..".format(url))

        counter += 1
        # print("%s[GET] %sInfo: %sParsing: (%s/%s) %s %s                                                                    " % (RED, CYAN, WHITE, counter, totalUrls, RED, show_titles[show_urls.index(url)]), end="\r", flush=True)
        debug.debug('Open URL: ' + url)
        page = urlopen(url)
        debug.debug('URL open')
        soup = BeautifulSoup(page, "html.parser")
        debug.debug('URL - Parsing..')
        debug.debug('URL - Extract Scripts..')
        for script in soup("script"):
            script.extract()
        show_descriptions = []
        media_values = {}
        media_values_list = []
        media_ids = []
        media_links = []
        media_titles = []
        media_episodes = []
        media_imgs = []
        media_descriptions = []
    ##################################################################################
        for meta in soup.find_all("meta", attrs={'property':'og:description'}):
            if meta.get("content") != None:
                show_descriptions.append(meta.get("content"))
            else:
                show_descriptions.append("null")
        debug.debug('GET show_description')
    ##################################################################################
        for a in soup.find_all("a", attrs={'class':'portrait-element block-link titlefix episode'}):
            if a.get("href") != None:
                media_links.append("http://www.crunchyroll.com" + ' '.join(a.get("href").split()))
            else:
                media_links.append("null")

            if a.get("title") != None:
                try:
                    media_titles.append(' '.join(a.get("title").split())[:a.get("title")].replace("’", "'"))
                except:
                    media_titles.append(' '.join(a.get("title").split()).replace("’", "'"))
                    pass
            else:
                media_titles.append("null")
        debug.debug('GET media_link')
        debug.debug('GET media_title')
    ##################################################################################
        for img in soup.find_all("img", attrs={'class':'landscape'}):
            if img.get("src") != None:
                media_imgs.append(' '.join(img.get("src").split()))
            else:
                media_imgs.append("null")
        debug.debug('GET media_img')
    ##################################################################################
        for div in soup.find_all("div", attrs={'class':'episode-progress'}):
            if div.get("media_id") != None:
                media_ids.append(div.get("media_id"))
            else:
                media_ids.append("null")
        debug.debug('GET media_id')
    ##################################################################################
        for span in soup.find_all("span", attrs={'class':'series-title block ellipsis', 'dir':'auto'}):
            if span.get_text() != None:
                media_episodes.append(' '.join(span.get_text().split()).replace("Episode ", ""))
            else:
                media_episodes.append("null")
        debug.debug('GET media_episode')
    ##################################################################################
        for p in soup.find_all("p", attrs={'class':'short-desc', 'dir':'auto'}):
            if p.get_text() != None:
                media_descriptions.append(' '.join(p.get_text().split()))
            else:
                media_descriptions.append("null")
        debug.debug('media_description')
    ##################################################################################
        # msgh = "Gathered information: %s" % list(zip(media_ids, media_titles, media_episodes, media_descriptions, media_links, media_imgs))
        # msgh = msgh.encode('UTF-8')
        # debug.info(msgh)
        showsB = zip(media_ids, media_links, clean_title(media_titles), media_episodes, media_imgs, clean_title(media_descriptions))
        if extract == "":
            if verbose:
                verbose_write("[PARSER] Sending to database.. ")
            else:
                print(YELLOW + "[PARSER]" + CYAN + " Sending to database.. ", end='')
        for c in media_ids:
            media_values = {}
            media_values['media_id'] = c
            media_values['media_title'] = media_titles[media_ids.index(c)]
            media_values['media_episode'] = media_episodes[media_ids.index(c)]
            media_values['media_description'] = media_descriptions[media_ids.index(c)]
            media_values['media_url'] = media_links[media_ids.index(c)]
            media_values['media_img'] = media_imgs[media_ids.index(c)]
            media_values_list.append(media_values)


        indent = 50
        count = 0
        spaces=""
        while count != (indent-len(show_titles[show_urls.index(url)])-len(str(counter))+1):
            if indent-len(show_titles[show_urls.index(url)]) < 0 or len(spaces) > indent:
                break
            spaces+=" "
            count+=1
        if toFolder:
            # print(WHITE + spaces + " | " + GREEN + "Parse done.." + OFF)

            # print(YELLOW + "[PARSER]" + CYAN + " Writing to file: "+ RED +" %s                                                                              " % show_titles[show_urls.index(url)], end="\r", flush=True)
            if not os.path.exists(outFolder):
                os.makedirs(outFolder)
            f = open(outFolder + "/%s.crdl" % clean_title(show_titles[show_urls.index(url)], True), 'w', encoding="utf-8")
            f.write(str(valueList[show_urls.index(url)]) + "\r\n")
            for p in media_links:
                # print(len(media_values_list))
                f.write(str(media_values_list[media_links.index(p)]) + "\r\n")
            f.close()  # you can omit in most cases as the destructor will call it
        indent = 53
        count = 0
        spaces=""
        while count != (indent-len(show_titles[show_urls.index(url)])):
            if indent-len(show_titles[show_urls.index(url)]) < 0 or len(spaces) > indent:
                break
            spaces+=" "
            count+=1
        # if toFolder:
            # print(WHITE + spaces + " | " + GREEN + "Write done.." + OFF)
if extract != "None":
    if True:
        if len(extract.split(":")) >= 3:
            toExtract = []
            debug.info("extract: " + extract.split(":")[0])
            if extract.split(":")[0] == "id":
                if extract.split(":")[2] == "media":
                    toExtract = media_ids
            elif extract.split(":")[0] == "title":
                if extract.split(":")[2] == "media":
                    toExtract = media_titles
            elif extract.split(":")[0] == "url":
                if extract.split(":")[2] == "media":
                    toExtract = media_urls
            elif extract.split(":")[0] == "img":
                if extract.split(":")[2] == "media":
                    toExtract = media_imgs
            elif extract.split(":")[0] == "description":
                if extract.split(":")[2] == "media":
                    toExtract = media_descriptions
            elif extract.split(":")[0] == "episode":
                if extract.split(":")[2] == "media":
                    toExtract = media_episodes
            f = open("parser.out", 'w', encoding="utf-8")
            f.write(str(toExtract) + "\r\n")
            f.close()  # you can omit in most cases as the destructor will call it
        else:
            if extract != "None" and stringD == "":
                print("No string was specified. Please do so using: 'main.py -e %s -s or --string <string>'" % extract)
                if dumpVariablesOnExit:
                    f = open("variableDump.txt", 'w', encoding="utf-8")
                    f.write(str(list(zip(show_group_ids, show_titles, show_video_count, show_urls, show_imgs))) + "\r\n")
                    f.close()  # you can omit in most cases as the destructor will call it
                sys.exit(2)
            else:
                i = stringD
                extractIndexes = []
                toExtract = []
                if extract.split(":")[0] == "id":
                    if extract.split(":")[1] == "media":
                        if i in media_titles:
                            values = np.array(media_titles)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_descriptions:
                            values = np.array(media_descriptions)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_episodes:
                            values = np.array(media_episodes)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_links:
                            values = np.array(media_links)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_imgs:
                            values = np.array(media_imgs)
                            extractIndexes = np.where(values == i)[0]
                        else:
                            print(RED + "[ERRO] " + WHITE + "Couldn't find a match with current parameters, [%s:%s] (%s) - (%s)" % (extract.split(":")[0], extract.split(":")[1], i, extractIndexes))
                            errors += 1
                            errorEncountered = True
                        for ex in extractIndexes:
                            toExtract.append(media_ids[ex])
                elif extract.split(":")[0] == "title":
                    if extract.split(":")[1] == "media":
                        if i in media_ids:
                            values = np.array(media_ids)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_descriptions:
                            values = np.array(media_descriptions)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_episodes:
                            values = np.array(media_episodes)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_links:
                            values = np.array(media_links)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_imgs:
                            values = np.array(media_imgs)
                            extractIndexes = np.where(values == i)[0]
                        else:
                            print(RED + "[ERRO] " + WHITE + "Couldn't find a match with current parameters, [%s:%s] (%s) - (%s)" % (extract.split(":")[0], extract.split(":")[1], i, extractIndexes))
                            errors += 1
                            errorEncountered = True
                    for ex in extractIndexes:
                        toExtract.append(media_titles[ex])

                elif extract.split(":")[0] == "url":
                    if extract.split(":")[1] == "media":
                        if i in media_ids:
                            values = np.array(media_ids)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_descriptions:
                            values = np.array(media_descriptions)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_episodes:
                            values = np.array(media_episodes)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_titles:
                            values = np.array(media_titles)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_imgs:
                            values = np.array(media_imgs)
                            extractIndexes = np.where(values == i)[0]
                        else:
                            print(RED + "[ERRO] " + WHITE + "Couldn't find a match with current parameters, [%s:%s] (%s) - (%s)" % (extract.split(":")[0], extract.split(":")[1], i, extractIndexes))
                            errors += 1
                            errorEncountered = True
                        for ex in extractIndexes:
                            toExtract.append(media_links[ex])

                elif extract.split(":")[0] == "img":
                    if extract.split(":")[1] == "media":

                        if i in media_ids:
                            values = np.array(media_ids)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_descriptions:
                            values = np.array(media_descriptions)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_episodes:
                            values = np.array(media_episodes)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_titles:
                            values = np.array(media_titles)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_links:
                            values = np.array(media_imgs)
                            extractIndexes = np.where(values == i)[0]
                        else:
                            print(RED + "[ERRO] " + WHITE + "Couldn't find a match with current parameters, [%s:%s] (%s) - (%s)" % (extract.split(":")[0], extract.split(":")[1], i, extractIndexes))
                            errors += 1
                            errorEncountered = True
                        for ex in extractIndexes:
                            toExtract.append(media_imgs[ex])

                elif extract.split(":")[0] == "description":
                    if extract.split(":")[1] == "media":
                        if i in media_ids:
                            values = np.array(media_ids)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_imgs:
                            values = np.array(media_imgs)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_episodes:
                            values = np.array(media_episodes)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_titles:
                            values = np.array(media_titles)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_links:
                            values = np.array(media_imgs)
                            extractIndexes = np.where(values == i)[0]
                        else:
                            print(RED + "[ERRO] " + WHITE + "Couldn't find a match with current parameters, [%s:%s] (%s) - (%s)" % (extract.split(":")[0], extract.split(":")[1], i, extractIndexes))
                            errors += 1
                            errorEncountered = True
                        for ex in extractIndexes:
                            toExtract.append(media_descriptions[ex])

                elif extract.split(":")[0] == "episode":
                    if extract.split(":")[1] == "media":
                        if i in media_ids:
                            values = np.array(media_ids)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_imgs:
                            values = np.array(media_imgs)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_episodes:
                            values = np.array(media_descriptions)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_titles:
                            values = np.array(media_titles)
                            extractIndexes = np.where(values == i)[0]
                        elif i in media_links:
                            values = np.array(media_imgs)
                            extractIndexes = np.where(values == i)[0]
                        else:
                            print(RED + "[ERRO] " + WHITE + "Couldn't find a match with current parameters, [%s:%s] (%s) - (%s)" % (extract.split(":")[0], extract.split(":")[1], i, extractIndexes))
                            errors += 1
                            errorEncountered = True
                        for ex in extractIndexes:
                            toExtract.append(media_episodes[ex])


                f = open("parser.out", 'w', encoding="utf-8")
                f.write(str(toExtract) + "\r\n")
                f.close()  # you can omit in most cases as the destructor will call it

                # indent = 50
                # count = 0
                # spaces=""
                # while count != indent-len(show_titles[show_urls.index(url)]):
                #     if indent-len(show_titles[show_urls.index(url)]) < 0:
                #         break
                #     spaces+=" "
                #     count+=1
                # if toFolder:
                #     print(GREEN + spaces + "Done.." + OFF)
if verbose:
    verbose_write("* INFO Number of series parsed: " + str(counter))
print(CYAN + "* INFO " + WHITE + "Number of series parsed: " + RED + "%s" % counter)
