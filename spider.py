#!/usr/bin/env python3
# Project: arachnida
# Student: Biktor Garcia
# Module: spider.py
# Expected cmdline: spider.py [-rlpS] URL
#
# NOTE 1: If running this script in MacOS, you'll need the requests module. If you don't have administrator
# privileges, you can install it in a venv with:
# python3 -m venv [/path/to/venv] && source [/path/to/venv]/bin/activate && pip3 install requests

# NOTE 2: Instructions are unclear regarding option '-S', so I added it and repurposed it
# to allow for only strict scraping of the current host and avoid leaking into 3rd party sites

# Subject:
# El programa spider permitirá extraer todas las imágenes de un sitio web, de manera
# recursiva, proporcionando una url como parámetro. Gestionarás las siguientes opciones
# del programa:
# ./spider [-rlpS] URL
# • Opción -r : descarga de forma recursiva las imágenes en una URL recibida como
# parámetro.
# • Opción -r -l [N] : indica el nivel profundidad máximo de la descarga recursiva.
# En caso de no indicarse, será 5.
# • Opción -p [PATH] : indica la ruta donde se guardarán los archivos descargados.
# En caso de no indicarse, se utilizará ./data/.
# El programa descargará por defecto las siguientes extensiones:
# ◦ .jpg/jpeg
# ◦ .png
# ◦ .gif
# ◦ .bmp


# Handle options
import getopt
# Sys to parse arguments
import sys
# OS utilities (to handle directories and files)
import os
# HTTP requests
import requests
# HTML parsing
from html.parser import HTMLParser
# JSON module to keep a file with everything that was found
# and wether it was processed or not
import json
# Handle signals from the OS
import signal
import random
import string
# Globals
recursive = False
strict = True # Continue scraping the child only if it's in the same host
nesting_level = 5
output_path = "./data"
verbose = False
is_local = False
url = "" # either http[s]://url or file://path/to
initial_fn = "" #... initial scanned path
last_host = ""
task_queue = []
# Add any other extension here
supported_file_formats = ["jpg", "jpeg",
                          "png", "gif",
                          "bmp", "docx",
                          "pdf"]

# task queue is an array of Tasks
class Task:
    type = "" # img || link
    path = "" # path to resource
    processed = False # state
    parent = "" # parent object
    nesting_level = 0 #  level of recursion
    childs = [] # childs (if any)

#
#   Using HTMLParser library to iterate through the html response body
#   I'm specifically looking for <a> and <img> elements, and whenever
#   one of them is found is added to a queue for processing
class MyParser(HTMLParser):
    nesting_level = 0
    parent = "" # path to its parent
    def set_nesting_level(self, level):
        MyParser.nesting_level = level
    def set_parent(self, parent_node):
        MyParser.parent = parent_node

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            for x in attrs:
                if x[0] == "src" and x[1] != "":
                    if verbose:
                        print("Image found: ", x[1])
                    add_to_parse_list({"type":"img","path":x[1], "childs":[], "processed": False, "parent": MyParser.parent, "nesting_level": MyParser.nesting_level})
        elif tag == "a":
            for x in attrs:
                if x[0] == "href" and x[1] != "" and x[1].__contains__('mailto:') != True:
                    if verbose:
                        print("Link found: ", x[1])
                    add_to_parse_list({"type":"link","path":x[1], "childs":[], "processed": False, "parent": MyParser.parent, "nesting_level": MyParser.nesting_level})

#
# Function to dump the task queue to disk
#
def dump_tasks_to_file():
    global task_queue
    # Serializing json
    json_object = json.dumps(task_queue, indent=4)
    try:
        with open("site_data.json", "w") as outfile:
            outfile.write(json_object)
    except:
        print("ERROR: Couldn't backup the tasklist")

#
# Returns True if the URL is an absolute path or relative
#
def is_path_absolute(this_url):
    if this_url.__contains__('http://') or this_url.__contains__('https://'):
        return True
    return False
#
# Task handling: Looks for a specific path through a list (wether the task_queue or one of its childs)
#
def check_tasklist(items, item):
    already_in = False
    if not items:
        return already_in
    for task in items:
        if task["path"] == item["path"]:
            # Already exists
            already_in = True
        if already_in == False:
            already_in = check_tasklist(task["childs"], item)
    
    return already_in

#
# Same as above, but adds a child given a parent
#
def find_parent_and_add(items, item):
    already_in = False
    for task in items:
        if task["path"] == item["parent"]:
            # Already exists
            task["childs"].append(item)
            already_in = True
        if already_in == False:
            already_in = find_parent_and_add(task["childs"], item)
    
    return already_in

#
# Triggers a search and append through the task_queue to add new items
# to the queue
def add_to_parse_list(item):
    global task_queue
    already_in = check_tasklist(task_queue, item)
    if already_in == False:
        if verbose:
            print("Adding ", item["path"], "to the task queue")
        if item["parent"] == "":
            task_queue.append(item)
        else:
            find_parent_and_add(task_queue, item)
    else:
        if verbose:
            print("Item", item["path"], "is already in the list")
    
    dump_tasks_to_file()

#
# Show help
#
def show_help():
    print("spider: Utility to scrape and download files from a specified URL")
    print("USAGE:\n",
          "./spider.py [-rlpS] URL\n"
          "./spider.py --recursive --level 3 --path dump/ https://www.google.es\n"
          "\t -r --recursive: Scan other URLs recursively\n"
          "\t -l --level: Recursive level (implies -r)\n"
          "\t -p --path: Output path (default will be './data')\n"
          "\t -S --non-strict: Allow the spider to retrieve from urls outside the initial host \n"
          "\t -v --verbose: Show debugging messages\n"
          "\t -h --help: Show help\n")
    quit()

#
# Check if file extension matches (when downloading images)
#
def is_file_type_allowed(filename):
    global supported_file_formats
    extension = filename.rsplit('.', 1)[-1]
    for format in supported_file_formats:
        if extension.lower() == format:
            if verbose:
                print(filename, ": Extension match ", extension, '->', format)
            return True
    return False

#
# Abstract https / filesystem access requests
# 
def get_resource(path):
    global url
    class RequestClass:
        url = ""
        content = ""
        text = ""
        status_code = 0
    ret = RequestClass()
    this_url = ""
    if verbose:
        print("Get Resource: ", path)

    if is_local == False:
        if verbose:
            print("Remote access ")
        if is_path_absolute(path):
            this_url = path
        elif last_host != "" and last_host != url:
            this_url = last_host + path
        else:
            this_url = url +  path

        if strict == True and this_url.__contains__(url) != True:
            print(" --> Strict mode: skipping!")
            ret.status_code = 1010
            return ret
        try:
            return requests.get(this_url, allow_redirects=True)
        except:
            ret.status_code = 404
            return ret
    
    else:
        # Handle local file access
        if verbose:
            print("Local access")
        try:
            this_url = (url).replace("file://", "./") + '/' + path
            print("Opening ", this_url)
            fp = open(this_url, "rb")
            ret.content = fp.read()
            ret.text = ret.content.decode()
            fp.close()
            ret.status_code = 200
        except:
            print("Error opening file")
            ret.status_code = 409

    return ret

#
# Get image
#
def get_image(this_path, current_nesting_level):
    global output_path
    print('|-', '-' * current_nesting_level, "> ", current_nesting_level, '/', nesting_level, " Getting image with path: ", this_path, sep="")
    req = get_resource(this_path)
    if req.status_code == 200:
        if verbose:
            print(" Image retrieved!")
        filename = output_path + '/' + ''.join(random.choice((string.ascii_lowercase)) for i in range(8)) + '_' + this_path.rsplit('/', 1)[-1]
        if verbose:
            print("**** Path in disk", filename, end="")
        if is_file_type_allowed(filename) == True:
            if verbose:
                print("Saving as ", filename)
            fp = open(filename, "wb")
            fp.write(req.content)
            fp.close()
        if verbose:
            print("... Saved!")
        else:
            if verbose:
                print("WARN: File type not allowed!")
    elif req.status_code == 1010:
        if verbose:
            print("Not retrieving this file as it is outside the base URL")
    else:
        print("... Error retrieving", this_path, "Err code ", req.status_code)


#
#   scrape_child: Given a [task], scrape the path, and if that works, loop through its childs
#   to scrape them too (if below max recursion)
#
def scrape_child(task, current_nesting_level):
    global url
    global nesting_level
    global last_host
    print('|-', '-' * current_nesting_level, "> ", current_nesting_level, "/", nesting_level, " Scraping child with path: ", task["path"], sep="", end="")
    parser = MyParser()
    parser.set_nesting_level(current_nesting_level+1)
    parser.set_parent(task["path"])
    
    if (task["processed"] == True):
        print("WARN: Already Processed!")
        return
    if current_nesting_level > nesting_level:
        print("Nesting level exceeded, not continuing")
        return
    try:
        req = get_resource(task["path"])
        if req.url != "" and req.url.__contains__(url) != True:
            last_host = req.url.split('/', -1)[:3]
            last_host = last_host[0] + '//' + last_host[2]
            print("Warning! We jumped hosts", req.url, req.status_code, "new host: ", last_host)
        if req.status_code != 200 and req.status_code != 1010:
            print("Failed to get the requested file/url: ", req.status_code)
            return
        else:
            print("")

        parser.feed(req.text)
        for child in task["childs"]:
            if child["type"] == "link" and (current_nesting_level+1) < nesting_level:
                scrape_child(child, current_nesting_level+1)
            elif child["type"] == "img":
                get_image(child["path"], current_nesting_level)
    except:
        print("Failed to retrieve URL")
    task["processed"] = True

#
# First fetch of a URL / path
#
def scrape_init():
    global initial_fn
    global give_up_requested
    print("|-> Scrape init for initial URL ", url)
    if os.path.exists(output_path) != True:
        print("|-> Output directory", output_path, "doesn't exist, creating it...")
        try:
            os.makedirs(output_path)
        except:
            quit("Error while trying to make the output directory, bailing out...")
    else:
        print("WARNING: Output directory already exists! Will append/overwrite anything inside")       
    if verbose:
        print("|-> Recursive:", "yes" if recursive else "no")
        if recursive:
            print("|-> Nesting limit:", nesting_level)
        print("|-> Output path: ", output_path)
        print("|-> URL: ", url)
    # Get the first page, then loop through its data
    if is_local == False:
        x = requests.get(url, allow_redirects=True)
    else:
        x = get_resource(initial_fn)

    parser = MyParser() # initialize it
    parser.feed(x.text)
    print("|-> Finished feeding initial url")
    for task in task_queue:
        if recursive == True and (task["type"] == "link"):
            scrape_child(task, 0)
        elif task["type"] == "img":
            get_image(task["path"], 0)
        
    if x.status_code == 404:
        quit("The page doesn't seem to exist!")

def main():
    global recursive
    global nesting_level
    global output_path
    global verbose
    global strict
    global is_local
    global url
    global initial_fn
    try:
        opts, args = getopt.getopt(sys.argv[1:], "rl:p:vSho:", ["recursive", "level=", "path=","verbose","strict", "output="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        show_help()
    for o, a in opts:
        if o in ("-r", "--recursive"):
            recursive = True
        elif o in ("-l", "--level"):
            recursive = True
            nesting_level = int(a)
        elif o in ("-p", "--path"):
            output_path = a
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-S", "--strict"):
            strict = False
        elif o in ("-h", "--help"):
            show_help()
        elif o in ("-o", "--output"):
            output = a
        else:
            print("ERROR: unknown option: ", o)
            quit()

    url = sys.argv[len(sys.argv) -1]
    if verbose:
        print("Selected options:")
        print("\tRecursive:", "yes" if recursive else "no")
        if recursive:
            print("\tNesting level:", nesting_level)
        print("\tOutput path: ", output_path)
        print("\tURL: ", url)

    if url.__contains__('http://') or \
       url.__contains__('https://'):
        initial_fn = '/' + '/'.join(url.rsplit('/', -1)[3:])
        url = url.split('/', -1)[:3]
        url = url[0] + '//' + url[2]
        scrape_init()
    elif url.__contains__('file://'):
        is_local = True
        url = url.rsplit('/', 1)[0]
        scrape_init()  
    else:
        print("ERROR: Use either http[s]:// or file:// to scrape a local html file", url)
        quit()

if __name__ == "__main__":
    main()