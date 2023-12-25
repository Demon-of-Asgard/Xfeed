#!/home/manu/anaconda3/bin/python

import os 
import sys
import yaml
import platform
import requests
import feedparser
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

    shell_colors = {"default": 0, "black": 30, "red": 31, "green": 32,
                    "yellow": 33, "blue": 34, "magenta": 35, "cyan": 36,  "white": 37.}

    return f"\033[{shell_styles[style]};{shell_colors[color]}m{text}\033[{shell_colors['default']}m"


def read_cmd(hint:str)->list:
    return input(f"{hint}")


def render_feed(feeds:list,isabs:list, start_index=0, identifier:str=None, comment="")->None:

    os.system("clear")
 
    print("+" + "-"*(20 + len(identifier)) + "+")
    print("|" + " "*10 + get_shell_text(text= identifier, color="green", style="bold")+ " "*10 + "|")
    print("+" + "-"*(20 + len(identifier)) + "+")

    for index, entry in enumerate(feeds):
        # print(f"[{index+start_index}] {LatexNodes2Text().latex_to_text(entry['title'])}")
        if isabs[index]:
            print(f"[{index+start_index}] {get_shell_text(text = entry['title'], color='red', style='italic')}")
            abstract_ = "\t\t" + "\n\t  ".join(entry['summary'].strip("<p>").strip("</p>").split("\n"))
            abstract = get_shell_text(text=abstract_, color="default", style="italic")
            print(f"{abstract}", end = "\n\n")
            # print(f"{LatexNodes2Text().latex_to_text(current_abstract)}")
        else:
            print(f"[{index+start_index}] {entry['title']}")

    if comment != None:
        print(comment)

    return None


def open_file(display_chunk:list,  id:int=None):
    print(get_shell_text(text="loading", color="green") + get_shell_text(text="...", color="green", style="blink"))

    if not os.path.exists(Paths.PDF):
        os.makedirs(Paths.PDF)

    pdf_path = os.path.join(Paths.PDF, display_chunk[id]["link"].split("/abs/")[-1] + ".pdf")

    if not os.path.exists(pdf_path):
        url_of_id = "/pdf/".join(display_chunk[id]["link"].split("/abs/")) + ".pdf"
        response = requests.get(url_of_id)
        with open(pdf_path, "wb") as f:
            f.write(response.content)
    os.system(f"{Os.OPEN} {pdf_path}")
    clear()
    return 


def pack_current_feeds(feeds:list, abs_index, current_item:int, slice_length:int)-> tuple:
    feeds_chunk = feeds[current_item:current_item+slice_length]
    isabs = [index + current_item == abs_index for index, _ in enumerate(feeds_chunk)]
    return (feeds_chunk, isabs)


def main_loop(feed_list:list, identifier:str)-> None:
    current_item = 0
    display_length = 10
    display_chunk = []
    isabs = []
    abs_index = -1
    comment = None
    while True:
        display_chunk, isabs = pack_current_feeds(feed_list, abs_index, current_item=current_item, slice_length=display_length)
        render_feed(display_chunk, isabs, start_index=current_item, identifier=identifier, comment=comment)
        comment = None
        cmd = read_cmd("> ")
        
        if cmd.lower() == Cmd.EXIT:
            clear()
            return 
        
        elif cmd.lower() == Cmd.NEXT:
            current_item += display_length * ((current_item + display_length) < len(feed_list))

        elif cmd.lower() == Cmd.PREVIOUS:
            current_item -= display_length * ((current_item - display_length) >= 0)

        elif len(cmd.split(" ")) == 2:
            cmdlist = cmd.split(" ")
            if cmdlist[0].lower() == Cmd.ABSTRACT and int(cmdlist[1]) < len(feed_list):
                abs_index = int(cmdlist[1])
            elif cmdlist[0].lower() == Cmd.OPEN and int(cmdlist[1]) < len(feed_list):
                stat = open_file(display_chunk=display_chunk,  id=int(cmdlist[1]) - current_item)
            else:
                comment = get_shell_text(text="ERR: ", color="red", style="bold") + f"Unexpected Input <{cmd}>"
        else:
            comment = get_shell_text(text="ERR: ", color="red", style="bold") + f"Unexpected Input <{cmd}>"
            continue


def main(url:str, identifier:str):
    print(get_shell_text(text="loading", color="green") + get_shell_text(text="...", color="green", style="blink"))
    Feed = Feeds(url=url, identifier=identifier)
    feed = feedparser.parse(Feed.url)
    feed_list = [entry for entry in feed.entries]
    clear()
    main_loop(feed_list=feed_list, identifier=Feed.identifier)


if __name__ == "__main__":
    prefix="./"
    pdfat = "./"
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--prefix":
            prefix = sys.argv[i+1]
        elif sys.argv[i] == "--pdf":
            pdfat = sys.argv[i+1]
            Paths.PDF = pdfat
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

        cmd = input(f"> ")

        cmdtype="str"
        try:
            cmd = int(cmd)
            cmdtype = "int"
        except:
            cmdtype = "str"

        if cmdtype =="str":
            if(cmd == Cmd.EXIT):
                os.system("clear")
                exit()
            else:
                comment = get_shell_text(text="ERR: ", color="red", style="bold") + f"Unexpected Input <{cmd}>"

        else:
            if cmd < len(available_feeds):
                main(available_feeds[int(cmd)]['url'], identifier=available_feeds[int(cmd)]['identifier'])
                comment = None
            else:
                comment = get_shell_text(text="ERR: ", color="red", style="bold") + f"Unexpected Input <{cmd}>"


