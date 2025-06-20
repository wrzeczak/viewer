import os
from os import listdir, rmdir, mkdir, remove    
from os.path import isfile, join, isdir, exists
import subprocess
from PIL import Image
import argparse as ag
from math import floor

#------------------------------------------------------------------------------

parser = ag.ArgumentParser()

parser.add_argument("source_folder")
args = parser.parse_args()

source_folder = args.source_folder
output_folder = f"{source_folder}-compressed"
images = os.listdir(source_folder)
ACCEPTED_FILETYPES = [".png", ".jpg", ".gif", ".jpeg", ".bmp"]
images = [i for i in images if f".{i.split(".")[-1]}" in ACCEPTED_FILETYPES]

if exists(output_folder):
    # delete previous compressed folder
    files = listdir(output_folder)
    files = [join(output_folder, i) for i in files]

    for f in files: remove(f)
    rmdir(output_folder)

mkdir(output_folder)

for p in images:
    output_file = join(output_folder, p)

    open(output_file, 'w').close()

#------------------------------------------------------------------------------

# resize image to have a maximum dimension of 500

for p in images:
    img = Image.open(join(source_folder, p))
    dim = list(img.size)

    max_dim = max(dim)
    if max_dim > 500:
        # resize all photos with a bigger max dim than 500
        idx = dim.index(max_dim)
        ratio = 500 / dim[idx]

        new_dim0 = floor(ratio * dim[0])
        new_dim1 = floor(ratio * dim[1])

        img = img.resize((new_dim0, new_dim1))

        if not exists(output_file): 
            print(output_file)
            listdir(output_folder)
        with open(output_file, "w") as f:
            img.save(f"{output_folder}/{p}", optimize=True, quality=85)