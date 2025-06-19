import os
from os import listdir
from os.path import isfile, join

import sys

import subprocess

# TODO: make this use argparse? 
if len(sys.argv) > 1:
    root_folder = sys.argv[1]
else: exit(-1)

files = [f for f in listdir(root_folder) if isfile(join(root_folder, f))]

os.mkdir(f"{root_folder}-compressed")
ACCEPTED_FILETYPES = [".png", ".jpg", ".jpeg", ".bmp"] # remove gif

# TODO: make this work on more than just Linux
for f in files:
    if f[-4:] in ACCEPTED_FILETYPES:
        subprocess.run(["convert", f"{root_folder}/{f}", "-resize", "500^x500", f"{root_folder}-compressed/{f}"])