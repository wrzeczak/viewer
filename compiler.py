from os import listdir
from os.path import isfile, join

import os
import subprocess
import sys

import argparse

##-----------------------------------------------------------------------------

mypath = "ERRNO"
convert = False
is_tagged = False

##-----------------------------------------------------------------------------

parser = argparse.ArgumentParser(prog="WRZ: Gallery")
parser.add_argument("folder_name")
parser.add_argument("-o", "--output_file", nargs='?', type=argparse.FileType('w'))
parser.add_argument("-c", "--compress", action="store_true")
parser.add_argument("-t", "--tagged", action="store_true")

args = parser.parse_args()

mypath = args.folder_name
convert = args.compress
is_tagged = args.tagged
output_file = args.output_file.name

##-----------------------------------------------------------------------------

#TODO: make this gen_n_columns(files, n)
def gen_four_columns(files):
    left_pics = files[:len(files)//2]
    right_pics = files[len(files)//2:]

    q1 = left_pics[:len(left_pics)//2]
    q2 = left_pics[len(left_pics)//2:]

    q3 = right_pics[:len(left_pics)//2]
    q4 = right_pics[len(left_pics)//2:]

    # q2 and q4 tend to accumulate the most images, so put them in the middle
    return [ q1, q2, q4, q3 ]

##-----------------------------------------------------------------------------

# compress files if -c flag is passed
if convert == True:
    if os.path.isdir(f"{mypath}-compressed/"): # remove all previously compressed files (easier than checking which ones are already)
        subprocess.call(["rm", "-rf", f"{mypath}-compressed"])
    subprocess.call(["python3", "cruncher.py", mypath]) # call the compressor script TODO: make this an imported module?
    files = [f for f in listdir(f"{mypath}-compressed") if isfile(join(f"{mypath}-compressed", f))]
else:
    files = [f for f in listdir(mypath) if isfile(join(mypath, f))]

files = [f for f in files if not f.endswith(".tag") and f != "TAGSET" and not f.endswith(".html") and not f.endswith(".css")]

##-----------------------------------------------------------------------------

# TODO: detect this automatically - is it useful to ignore tags in a tagged setup?
if is_tagged == True:
    tag_files = []

    for f in listdir(mypath): # get all the tag files
        if isfile(f"{mypath}/{f}") and f.endswith(".tag"):
            tag_files.append(f)

    print(f"Writing tags for {mypath}")   

    for t in tag_files:
        with open(f"{mypath}/{t}", "r", encoding="utf8", errors="ignore") as f:
            with open(f"{mypath}/{t[:-4]}.html", "w") as h:
                images = f.readlines()
                images = [i.strip() for i in images]
                print(f"Writing {t[:-4]}.html, {len(images)} files.")
                image_columns = gen_four_columns(images) # TODO: replace this with gen_n_columns()
                
                print("<!DOCTYPE html>", file=h)
                print("<html lang=\"en\"><head>", file=h)
                print("<link rel=\"stylesheet\" href=\"../styles.css\">", file=h)    
                print(f"<title>Image View <{t[:-4]}></title>", file=h)
                print("</head>", file=h)
                print("<body>", file=h)
                print("<p>", file=h)

                print("<div id=\"gallery-row\">", file=h)

                for l in image_columns:
                    print("\t<div id=\"gallery-column\">", file=h)
                    for f in l: 
                        print(f"\t\t<a href=\"{f}\"><img src=\"{f}\" alt=\"{f}\"></a>", file=h)
                    print("\t</div>", file=h)

                print("</div>", file=h)
                print("</p>", file=h)
                print("</body></html>", file=h)

##-----------------------------------------------------------------------------

columns = gen_four_columns(files) # TODO: replace this gen_n_columns

##-----------------------------------------------------------------------------

with open(output_file, "w") as o:
    print("<!DOCTYPE html>", file=o)
    print("<html lang=\"en\"><head>", file=o)
    print("<link rel=\"stylesheet\" href=\"styles.css\">", file=o)    
    print(f"<title>Image View</title>", file=o)
    print("</head>", file=o)
    print("<body>", file=o)
    print("<p>", file=o)

    if is_tagged:
        print("<div id=\"tag-display\"><b>TAGS &mdash;</b>&nbsp;", end="", file=o)
        tag_files = []

        for f in listdir(mypath):
            if isfile(f"{mypath}/{f}") and f.endswith(".html"):
                tag_files.append(f)
        
        print(f"Writing {len(tag_files)} tags.html to {mypath}...")

        for t in tag_files:
            print(f"<a href=\"{mypath}/{t}\">{t[:-5]}</a>,&nbsp;", end="", file=o)
        
        print("</div>\n<br/>\n", file=o)

    print("<div id=\"gallery-row\">", file=o)

    print(f"Writing main gallery view to {output_file}...")

    for l in columns:
        print("\t<div id=\"gallery-column\">", file=o)
        for f in l: 
            if convert and not f.endswith(".gif") and not f.endswith(".mp4"):
                print(f"\t\t<a href=\"{mypath}/{f}\"><img src=\"{mypath}-compressed/{f}\" alt=\"{mypath}/{f}\"></a>", file=o)
            else:
                print(f"\t\t<a href=\"{mypath}/{f}\"><img src=\"{mypath}/{f}\" alt=\"{mypath}/{f}\"></a>", file=o)
        print("\t</div>", file=o)

    print("</div>", file=o)
    print("</p>", file=o)
    print("</body></html>", file=o)
