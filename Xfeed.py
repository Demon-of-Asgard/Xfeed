#!/home/manu/anaconda3/bin/python

import os 
import sys
import yaml
import getkey
import datetime 
import platform
import requests
import feedparser
import urllib.request
# import sqlite3
# from pylatexenc.latex2text import LatexNodes2Text

class Cmd:
    NEXT = "n"
    PREVIOUS = "p"
    ABSTRACT = "a"
    OPEN = "o"
    EXIT = "q"


class Os:
    TYPE = platform.system()
    OPEN = 'open' if TYPE == 'Darwin' else 'xdg-open'


class Paths:
    PDF = "./pdf"
    DB  = "./db"


class Feeds:
    def __init__(self, url:str, identifier:str)-> None:
        self.url = url
        self.identifier = identifier


def clear()-> None:
    os.system("clear")
    return None


def get_shell_text(text: str, color: str = "default", style: str = "default") -> str:
    """Create colorful custom shell texts. """

    shell_styles = {"default": 0, "bold": 1, "faded": 2,
                        "italic": 3, "uline": 4, "blink": 5, "bg": 7}

    shell_colors = {"default": 0, "blue": 30, "red": 31, "green": 32,
                    "yellow": 33, "salmon": 34, "purple": 35, "cyan": 36,  "grey": 37}

    return f'\033[{shell_styles[style]};{shell_colors[color]}m{text}\033[0m'


def read_cmd(hint:str)->list:
    return input(f"{hint}")


def render_feed(feeds:list,display_abs:list, start_index=0, identifier:str=None, comment="")->None:

    os.system("clear")
 
    # print("+" + "-"*(20 + len(identifier)) + "+")
    # print("|" + " "*10 + get_shell_text(text= identifier, color="green", style="bold")+ " "*10 + "|")
    # print("+" + "-"*(20 + len(identifier)) + "+")
    
    print(get_shell_text(text= identifier, color="green", style="bold"))

    for index, entry in enumerate(feeds):
        if display_abs[index]:
            print(f"[{index+start_index+1}] {get_shell_text(text = entry['title'], color='blue', style='bold')}")
            abstract_ = "\t\t" + "\n\t  ".join(entry['summary'].strip("<p>").strip("</p>").split("\n"))
            abstract = get_shell_text(text=abstract_, color="grey", style="italic")
            print(f"{abstract}", end = "\n\n")
        else:
            print(f"[{index+start_index+1}] {entry['title']}")

    if comment != None:
        print(comment)

    return None


def open_file(link:str)->None:
    print(get_shell_text(text="loading", color="green") + get_shell_text(text="...", color="green", style="blink"))

    if not os.path.exists(Paths.PDF):
        os.makedirs(Paths.PDF)

    pdf_path = os.path.join(Paths.PDF, link.split("/abs/")[-1] + ".pdf")

    if not os.path.exists(pdf_path):
        url_of_id = "/pdf/".join(link.split("/abs/")) + ".pdf"
        response = requests.get(url_of_id)
        with open(pdf_path, "wb") as f:
            f.write(response.content)
    os.system(f"{Os.OPEN} {pdf_path}")
    clear()
    return 


def pack_current_feeds(feeds:list, abs_index, current_item:int, slice_length:int)-> tuple:
    feeds_chunk = feeds[current_item:current_item+slice_length]
    display_abs = [index + current_item == abs_index for index, _ in enumerate(feeds_chunk)]
    return (feeds_chunk, display_abs)


def main_loop(feed_list:list, identifier:str)-> None:

    current_item = 0
    display_length = 20
    display_chunk = []
    display_abs = []
    abs_index = 0
    comment = None

    while True:

        display_chunk, display_abs = pack_current_feeds(feed_list, abs_index, current_item=current_item, slice_length=display_length)
        render_feed(display_chunk, display_abs, start_index=current_item, identifier=identifier, comment=comment)
        comment = None

        key_pressed = getkey.getkey()

        if (key_pressed == getkey.keys.ESC) or (key_pressed == "q"):
            clear()
            exit()

        elif key_pressed == getkey.keys.DOWN or key_pressed == "j":
            current_item += 1 if ((current_item + 1) < len(feed_list)) else 0
            abs_index += 1 if ((abs_index + 1) < len(feed_list)) else 0

        elif key_pressed == getkey.keys.UP or key_pressed == "k":
            current_item -= ((current_item - 1) >= 0)
            abs_index -= ((abs_index - 1) >= 0)

        elif key_pressed == "o":
            print(display_chunk[0]['link'])
            stat = open_file(link=display_chunk[0]['link'])
        else:
            # comment = get_shell_text(text="ERR: ", color="red", style="bold") + f"Unexpected Input <{cmd}>"
            continue


def main(url:str, identifier:str):

    print(get_shell_text(text="loading", color="green") + get_shell_text(text="...", color="green", style="blink"))
    
    today = datetime.datetime.now().date()

    if not os.path.exists(os.path.join(Paths.DB, identifier)):
        os.makedirs(os.path.join(Paths.DB, identifier))
    
    if not os.path.exists(os.path.join(Paths.DB, identifier, f"{today}.xml")):
        with open(os.path.join(Paths.DB, identifier, f"{today}.xml"), "wb") as f:
            response = urllib.request.urlopen(url).read()
            f.write(response)
    else:
        with open(os.path.join(Paths.DB, identifier, f"{today}.xml"), "rb") as f:
            response = f.read()
            
    response = urllib.request.urlopen(url).read()
    feed = feedparser.parse(response)
    feed_list = [entry for entry in feed.entries]
    clear()
    main_loop(feed_list=feed_list, identifier=identifier)


if __name__ == "__main__":
    prefix="./"
    pdfat = "./"
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--prefix":
            prefix = sys.argv[i+1]
        elif sys.argv[i] == "--pdf":
            Paths.PDF = sys.argv[i+1]
        elif sys.argv[i] == "--db":
            Paths.DB = sys.argv[i+1]
        else:
            pass
        
    feeds_info:dict = {}
    with open(os.path.join(prefix, "feeds.yaml"), "r") as f:
        feeds_info = yaml.load(f, Loader=yaml.FullLoader)
    
    available_feeds = [(feeds_info[key]) for key in feeds_info.keys()]

    comment = None
    while True:
        _ = os.system("clear")
        for i, elm in enumerate(available_feeds):
            print(f"[{i}] {elm['identifier']}")

        if comment != None:
            print(comment)

        cmd = input(f"ENTER OPTION> ")

        if(cmd == Cmd.EXIT):
            os.system("clear")
            exit()

        elif int(cmd) < len(available_feeds):
            main(available_feeds[int(cmd)]['url'], identifier=available_feeds[int(cmd)]['identifier'])
            comment = None
        else:
            comment = get_shell_text(text="ERR: ", color="red", style="bold") + f"Unexpected Input <{cmd}>"


# issue with openin file once chunk len < display_len 
