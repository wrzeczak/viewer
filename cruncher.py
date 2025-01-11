import os
from os import listdir
from os.path import isfile, join

import sys

import subprocess

if len(sys.argv) > 1:
    root_folder = sys.argv[1]
else: exit(-1)

files = [f for f in listdir(root_folder) if isfile(join(root_folder, f))]

os.mkdir(f"{root_folder}-compressed")

for f in files:
    if f.endswith(".mp4") or f.endswith(".gif") or f.endswith(".tag") or f.endswith(".html") or f == "TAGSET": continue
    subprocess.run(["convert", f"{root_folder}/{f}", "-resize", "500^x500", f"{root_folder}-compressed/{f}"])
