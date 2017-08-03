import sys, time, os, getopt
import logging
import numpy as np
import pymysql
from modules.colors import *
from modules.workreturn import *
from modules.parse import *
from urllib.request import urlopen
from bs4 import BeautifulSoup
enableMySQL = False
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
    helpObjects = ["-e", "--extract", "-d", "--dump", "--dump-folder", "-h", "--help", "-s", "--string"]
    helpText = dict.fromkeys(['-e', '--extract'], "Extracts specified parsed information. To get a list of available information try: 'main.py -e list' ")
    helpText.update(dict.fromkeys(['-d', '--dump'], "Dumps parsed series and episode info to individual files in dump folder, or a folder specified with 'main.py -d --dump-folder <folder>'"))
    helpText.update(dict.fromkeys(['--dump-folder', '--df'], "Set dump folder for argument 'main.py --dump'"))
    helpText.update(dict.fromkeys(['-s', '--string'], "Required parameter for certain ('--extract')'s. Hard to explain. Look at examples."))
    helpText.update(dict.fromkeys(['-p', '--parse'], "Set a CrunchyRoll serie site for parsing"))
    # print(helpText['-d'])
    try:
        opts, args = getopt.getopt(argv,"dh:e:o:p:",["help=", "extract=", "output=", "string=", "parse=", "dump-folder="])
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
        return val.replace("\"", "'").replace("/", "_").replace("\\", "").replace("\'", "\\'")
    else:
        return val.replace(":","_").replace("?", "").replace("*", "").replace("\"", "'").replace("/", "_").replace("\\", "")
def getReturn():
    st = WHITE + ">> %s[%s] %s%s" % (work.returnCodeColor, work.returnCode, work.returnMessageColor, work.returnMessage)
    return st
def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

print(CYAN + "[INFO] " + WHITE + "Initializing loggers", end='')
debug = setup_debug('main_debug', 'main.log')
mysqllog = setup_logger('mySql', 'mySql.log')
if enableMySQL:
    tables = ['series', 'episode_information', 'episode_info_more']
    print(" and configure connection to mySql database.. ")
    try:
        connection = pymysql.connect(host='', user='', passwd='', db='')
        work.returnCode = "SUCCESS"
        work.returnMessage = "Connection configured"
        work.returnCodeColor = work.Success
        connection.commit()
    except Exception:
        work.returnCode = "ERROR"
        work.returnMessage = "Couldn't configure to database"
        work.returnCodeColor = work.Error
else:
    print(".. ")
    work.returnCode = "SUCCESS"
    work.returnMessage = "Loggers initialized"
    work.returnCodeColor = work.Success
print(getReturn())

truncate = False
truncateMessage = ""
truncateCount = 0
noun = "a"
totalEntries = 0
if enableMySQL:
    print(CYAN + "[INFO] " + WHITE + "Establish connection to mySql database..")
    try:
        acon = connection.cursor()
        mysqllog.info('Connection established')
        work.returnCode = "SUCCESS"
        work.returnMessage = "Connection established"
        work.returnCodeColor = GREEN
    except:
        mysqllog.warn('Connection to mySql has failed. Writing to files instead..')
        work.returnCode = "ERROR"
        work.returnMessage = "Couldn't connect to database"
        work.returnCodeColor = RED
    print(getReturn())
    for table in tables:
        sql = "SELECT count(*) as tot FROM %s;" % table
        sql = sql.encode('UTF-8')
        mysqllog.info('SEND: ' + str(sql))
        acon.execute(sql)
        data=acon.fetchone()
        mysqllog.info('RESPONSE: ' + str(data))
        if int(str(data).replace("(","").replace(",)", "")) > 0:
            debug.warn("Found '%s' entries in table '%s'!" % (int(str(data).replace("(","").replace(",)", "")), table))
            totalEntries += int(str(data).replace("(","").replace(",)", ""))
            truncateCount += 1
            truncateMessage += "There are entries in 'series' (%s) as opposed to what's recommended (0)\r\n" % data
    if truncateCount > 0:
        if truncateCount == 1:
            noun = "a table"
        else:
            noun = "multiple tables"
        print("WARNING: There are entries in %s." % noun)
        debug.warn("Found entries in %s" % table)
        print(truncateMessage)
        print("Do you want to truncate? (Y to truncate): ")

        if input("").upper() == "Y":
            for table in tables:
                debug.info("Truncating: %s" % table)
                print(CYAN + "Truncating: " + RED + "%s" % table)
                sql = "truncate %s;" % table
                sql = sql.encode('UTF-8')
                mysqllog.info('SEND: ' + str(sql))
                acon.execute(sql)

                data=acon.fetchone()
                mysqllog.info('RESPONSE: ' + str(data))
if extract == "None" and not toFolder:
    work.returnCode = "INPUT"
    work.returnMessage = "Before we begin. Do you want to export all information to individual files? (Y): "
    work.returnCodeColor = work.InputC
    if not toFolder:
        print(getReturn())
        if input(">>>> ").upper() == "Y":
            toFolder = True

print(CYAN + "[INFO] " + WHITE + "Updating list of series..")
wiki = "http://www.crunchyroll.com/videos/anime/all?group=all"
debug.debug('Open URL: ' + wiki)
print(">> " + CYAN + "[INFO] " + WHITE + "Opening page '%s' for parsing.." % wiki)
page = urlopen(wiki)
debug.debug('URL open')
soup = BeautifulSoup(page, "html.parser")
debug.debug('URL - Parsing..')
for script in soup("script"):
    script.extract()
debug.debug('URL - Extract Scripts..')
values = {}
valueList = []
show_group_ids = []
show_titles = []
show_video_count = []
show_urls = []
show_imgs = []
show_descriptions = []
print(CYAN + "[INFO] " + WHITE + "Start Parsing..")
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
            sys.exit(0);
    else:
        if extract != "None" and stringD == "":
            print("No string was specified. Please do so using: 'main.py -e %s -s or --string <string>'" % extract)
            errors += 1
            errorEncountered = True
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
            sys.exit(0);
# for key in showsA:
work.returnCode = "SUCCESS"
work.returnCodeColor = work.Success
work.returnMessage = "Parsing Complete. Applying update.."
print(getReturn())
time.sleep(2)
for c in show_group_ids:
    values = {}
    values['group_id'] = c
    values['title'] = show_titles[show_group_ids.index(c)]
    values['video_count'] = show_video_count[show_group_ids.index(c)]
    values['url'] = show_urls[show_group_ids.index(c)]
    values['img'] = show_imgs[show_group_ids.index(c)]
    valueList.append(values)
    mysqllog.info('Sending information to mySql database')
    pr = (CYAN + ">> " + WHITE + " Adding '" + RED + "%s") % show_titles[show_group_ids.index(c)]
    indent = 75
    count = 0
    spaces=""
    while count != indent-len(show_titles[show_group_ids.index(c)]):
        if indent-len(show_titles[show_group_ids.index(c)]) < 0:
            break
        spaces+=" "
        count+=1
    if enableMySQL:
        print(pr + WHITE + "'" + spaces + "to the database.." + OFF)
        try:
            sql = "INSERT INTO series(serie_name, serie_link, episodes, serie_release, date_entered, serie_id) VALUES(\'%s\', \'%s\', \'%s\', \'%s\',  NOW(), NULL);" % (clean_title(show_titles[show_group_ids.index(c)]), show_urls[show_group_ids.index(c)], show_video_count[show_group_ids.index(c)], "0000")
            sql = sql.encode('utf-8')
            mysqllog.info('SEND: ' + str(sql))
            acon.execute(sql)

            data=acon.fetchall()
            mysqllog.info('RESPONSE: ' + str(data))
        except:
            mysqllog.error('Send, failed')

# print(valueList)
#def printf(msg, color):
#    sys.stdout.write(color)
#    print "


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
    for url in urlsToParse:
        counter += 1
        print("%s[GET] %sInfo: %sParsing: (%s/%s) %s %s" % (RED, CYAN, WHITE, counter, totalUrls, RED, show_titles[show_urls.index(url)]), end='')
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
        msgh = "Gathered information: %s" % list(zip(media_ids, media_titles, media_episodes, media_descriptions, media_links, media_imgs))
        msgh = msgh.encode('UTF-8')
        debug.info(msgh)
        showsB = zip(media_ids, media_links, clean_title(media_titles), media_episodes, media_imgs, clean_title(media_descriptions))
        if extract == "":
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

            if enableMySQL:
                try:
                    mysqllog.info('Sending information to mySql database')
                    sql = "INSERT INTO episode_information(serie_name, episode_name, episode_link, episode, media_id, serie_id) VALUES(\'%s\', \'%s\', \'%s\', \'%s\', %s, (SELECT serie_id FROM series WHERE serie_name = \'%s\' LIMIT 1 ));" % (clean_title(show_titles[show_urls.index(url)]), clean_title(media_titles[media_ids.index(c)]), media_links[media_ids.index(c)], media_episodes[media_ids.index(c)], c, clean_title(show_titles[show_urls.index(url)]))
                    sql = sql.encode('UTF-8')
                    mysqllog.info('SEND: ' + str(sql))
                    acon.execute(sql)
                    data=acon.fetchall()
                    mysqllog.info('RESPONSE: ' + str(data))
                    sql = "INSERT INTO episode_info_more(serie_name, media_id, episode_description, episode_thumbnail, serie_id) VALUES(\'%s\', %s, \'%s\', \'%s\', (SELECT serie_id FROM series WHERE serie_name = \'%s\' LIMIT 1 ));" % (clean_title(show_titles[show_urls.index(url)]), c, clean_title(media_descriptions[media_ids.index(c)]), media_imgs[media_ids.index(c)], clean_title(show_titles[show_urls.index(url)]))
                    sql = sql.encode('UTF-8')
                    mysqllog.info('SEND: ' + str(sql))
                    acon.execute(sql)

                    data=acon.fetchall()
                    mysqllog.info('RESPONSE: ' + str(data))
                except:
                    mysqllog.error('Send, failed')
                    print(RED + " Send Failed")
        indent = 50
        count = 0
        spaces=""
        while count != (indent-len(show_titles[show_urls.index(url)])-len(str(counter))):
            if indent-len(show_titles[show_urls.index(url)]) < 0:
                break
            spaces+=" "
            count+=1
        if toFolder:
            print(WHITE + spaces + " | " + GREEN + "Parse done.." + OFF)
        if not connection.open or toFolder:
            if toFolder:
                print(YELLOW + "[PARSER]" + CYAN + " Writing to file: "+ RED +" %s" % show_titles[show_urls.index(url)], end='')
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
        while count != (indent-len(show_titles[show_urls.index(url)])-len(str(counter))+1):
            if indent-len(show_titles[show_urls.index(url)]) < 0:
                break
            spaces+=" "
            count+=1
        if toFolder:
            print(WHITE + spaces + " | " + GREEN + "Write done.." + OFF)
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
                        print(ex, len(media_titles))
                        exit()
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
print(CYAN + "[INFO] " + WHITE + "Number of series parsed: " + RED + "%s" % counter)
