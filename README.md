# Python-Crunchyroll-Scraper
This is a generic, massively overcoded python [CrunchyRoll](http://www.crunchyroll.com "Crunchyroll Website")(R) scraper with the sole purpose of gathering data directly from the [CrunchyRoll](http://www.crunchyroll.com "Crunchyroll Website")(R) website.

## Requirements:
Required: numpy

Required: BeautifulSoup (bs4)

Optional: PyMySQL

## Usage:
You can launch the program without arguments and get information on all series currently available, or launch with arguments and get various information specific to certain series or episodes.

### Arguments:
* **'-e', '--extract'** - Extracts specified parsed information. 
E.g **'python main.py -e title:all:serie'**
* **'-p', '--parse'**
** - Specify page to collect information from. 
E.g **'python main.py -e id:all:media --parse http://www.crunchyroll.com/bleach'** - This will get all episode media_id's of Bleach. If you also want all the information on each episode you can additionally use the **'-d', '--dump'** to write this information to file. On default, the file will be created in a folder called "dump" and have a '.crdl' extension. You can change the outfolder with **'--dump-folder'** and the extension in the source script.
* **'-s', '--string'** - Searchstring for use of gathering specific information. 
E.g **'python main.py -e description:serie --string "Bleach"'** - Response: *['BLEACH follows the story of Ichigo Kurosaki. When Ichigo meets Rukia he finds his life is changed forever.']*
* **'-d', '--dump', ('--dump-folder', '--df')** - Dumps collected information to serie specific files in the dumpfolder *(default dumpfolder is just called 'dump' You can specify your own dumpfolder if you wish)* . 


### Extractable information:
#### Important to note:
Any **'-e', '--extract'** arguments using *':all:'* will NOT be compatible with **'-s', '--string'** 

*:all:* will get ALL information from given urls. Unless you specify a certain url with **'-p', '--parse'** the program will collect from ALL series on [CrunchyRoll](http://www.crunchyroll.com "Crunchyroll Website")(R).

**Serie:**
* ***title:serie*** - Allows you to search for the title linked to a searchstring you specify using **'-s'** or **'--string'** E.g **'python main.py -e title:serie --string 42854'** will give the following result:
***Result:
title:serie:
['Bleach']***

* ***title:all:serie*** - Will collect ALL titles of ALL series on [CrunchyRoll](http://www.crunchyroll.com "Crunchyroll Website")(R).
* ***id:serie*** - Allows you to search for the title linked to a searchstring you specify using **'-s'** or **'--string'** E.g **'python main.py -e title:serie --string Bleach'** will give the following result:
***Result:
id:serie:
['42854']***

* ***id:all:serie*** - Will collect ALL group_id's of ALL series on [CrunchyRoll](http://www.crunchyroll.com "Crunchyroll Website")(R).
* ***url:serie*** - Allows you to search for the title linked to a searchstring you specify using **'-s'** or **'--string'** E.g **'python main.py -e url:serie --string Bleach'** will give the following result:
***Result:
url:serie:
['http://www.crunchyroll.com/bleach']***
* ***url:all:serie*** - Will collect ALL urls of ALL series on [CrunchyRoll](http://www.crunchyroll.com "Crunchyroll Website")(R).
* ***img:serie*** - Allows you to search for the title linked to a searchstring you specify using **'-s'** or **'--string'** E.g **'python main.py -e img:serie --string Bleach'** will give the following result:
***Result:
img:serie:
[['http://img1.ak.crunchyroll.com/i/spire2/52edb7a843abacb4ff0f642c8eda14401325114125_thumb.jpg']](http://img1.ak.crunchyroll.com/i/spire2/52edb7a843abacb4ff0f642c8eda14401325114125_thumb.jpg "Bleach Cover Image")***
* ***img:all:serie*** - Will collect ALL images of ALL series on [CrunchyRoll](http://www.crunchyroll.com "Crunchyroll Website")(R).
* ***description:serie*** - Allows you to search for the title linked to a searchstring you specify using **'-s'** or **'--string'** E.g **'python main.py -e description:serie --string Bleach'** will give the following result:
***Result:
description:serie:
['BLEACH follows the story of Ichigo Kurosaki. When Ichigo meets Rukia he finds his life is changed forever.']***
* **description:all:serie** - Will collect ALL descriptions of ALL series on [CrunchyRoll](http://www.crunchyroll.com "Crunchyroll Website")(R).
* ***episode:serie*** - Allows you to search for the title linked to a searchstring you specify using **'-s'** or **'--string'** E.g **'python main.py -e episode:serie --string Bleach'** will give the following result:
***Result:
episode:serie:
['366']***
* ***episode:all:serie*** - Will collect episode count of ALL series on [CrunchyRoll](http://www.crunchyroll.com "Crunchyroll Website")(R).


***I'm too lazy to add descriptions to the rest. But you probably get it by now anyways.***

**Media:**
* ***title:media***
* ***title:all:media***
* ***id:media***
* ***id:all:media***
* ***url:media***
* ***url:all:media***
* ***img:media***
* ***img:all:media***
* ***description:media***
* ***description:all:media***
* ***episode:media***
* ***episode:all:media***

## A plead of help
Please, if you are an experienced python coder I would LOVE for you to help me clean this code up. It's a massive f***-fest of uselessness:/ 

It's not really efficient, but heyy! Atleast it works. (Sorta, any '*:media' doesn't..)
