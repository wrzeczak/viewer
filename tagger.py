from raylib import *
import sys
import os
from os import listdir
from os.path import isfile, join
from typing import List
import argparse

#------------------------------------------------------------------------------

source_folder = "ERRNO"
exclude_tagged_files = False

parser = argparse.ArgumentParser(prog="WRZ: Gallery Tagger")
parser.add_argument("source_folder")
parser.add_argument("-e", "--exclude_tagged_files", action="store_true")

args = parser.parse_args()

source_folder = args.source_folder
exclude_tagged_files = args.exclude_tagged_files

#------------------------------------------------------------------------------

files = [f for f in listdir(source_folder) if isfile(join(source_folder, f)) 
         and f != "TAGSET"
         and not f.endswith(".mp4") and not f.endswith(".tag")
         and not f.endswith(".css") and not f.endswith(".html")]

folder_is_tagged = False

for f in listdir(source_folder):
    if f.endswith(".tag"):
        folder_is_tagged = True

tag_files = []

for f in listdir(source_folder):
    if isfile(f"{source_folder}/{f}") and f.endswith(".tag"):
        tag_files.append(f)

#------------------------------------------------------------------------------

if exclude_tagged_files:
    tagged_files = []

    for t in tag_files:
        with open(f"{source_folder}/{t}", "r", encoding="utf8", errors="ignore") as f:
            lines = f.readlines()
            for l in lines:
                tagged_files.append(l.strip())

    files = [f for f in files if f not in tagged_files]

dicts = [None] * len(files)

for i in range(len(files)):
    dicts[i] = {
        "filename": files[i],
        "tags": []
    }

if folder_is_tagged:
    for t in tag_files:
        with open(f"{source_folder}/{t}", "r", encoding="utf8", errors="ignore") as f:
            lines = f.readlines()
            for l in lines:
                for d in dicts:
                    if d["filename"] == l.strip():
                        d["tags"].append(t[:-4])
image_idx = 0

exit_without_saving = True

#------------------------------------------------------------------------------

tags = []

with open(f"{source_folder}/TAGSET", "r") as f:
    lines = f.readlines()
    tags = [s.strip() for s in lines]

#------------------------------------------------------------------------------

def wrz_append(d: dict, s: str):
    if s not in d["tags"]:
        d["tags"].append(s)
    else:
        d["tags"].remove(s)

def __wrz_button(i: int, h: int, d: List[dict], s: str):
    if GuiButton( [ 600, 10 + (h * 50), 200, 50 ], str.encode(s)):
        wrz_append(d[i], s)
        exit_without_saving = False

def wrz_button(h: int, s: str):
    __wrz_button(image_idx % len(files), h, dicts, s)

def wrz_buttons(tags: List[str]):
    for i in range(len(tags)):
        wrz_button(i, tags[i])

def wrz_tags(i: int, d: List[dict]) -> str:
    return ", ".join(d[image_idx % len(files)]["tags"])

#------------------------------------------------------------------------------

InitWindow(810, 650, b"WRZ: Image Tagger")

SetTargetFPS(GetMonitorRefreshRate(GetCurrentMonitor()))

image = LoadTexture(str.encode(f"{source_folder}/{files[image_idx % len(files)]}"))

# source_rect = ffi.new("Rectangle", [ 0, 0, image.width, image.height ])
# dest_rect = ffi.new("Rectangle", [ 0, 0, 500, 500 ])
# origin_vector = ffi.new("Vector2", 0, 0 )

while not WindowShouldClose():

    if IsKeyPressed(KEY_LEFT):
        UnloadTexture(image)
        image_idx -= 1
        image = LoadTexture(str.encode(f"{source_folder}/{files[image_idx % len(files)]}"))

    if IsKeyPressed(KEY_RIGHT):
        UnloadTexture(image)
        image_idx += 1
        image = LoadTexture(str.encode(f"{source_folder}/{files[image_idx % len(files)]}"))

    for i in range(0, 10):
        if IsKeyPressed(KEY_ONE + i):
            try:
                wrz_append(dicts[image_idx % len(files)], tags[i])
            except: continue
            exit_without_saving = False

    BeginDrawing()

    ClearBackground(BLACK)

    # DrawTexture(image, 10, 10, WHITE)

    DrawRectangle(70, 10, 520, 520, GRAY)
    DrawTexturePro(image, [ 0, 0, image.width, image.height ], [ 0, 0, 500, 500 ], [ -80, -20 ], 0, WHITE)

    for i in range(len(tags)):
        GuiButton([10, 10 + (i * 50), 50, 50], str.encode(str(i)))

    if not exit_without_saving:
        if GuiButton([70, 570, 520, 50], b"#152# EXIT WITHOUT SAVING"):
            exit_without_saving = True
            CloseWindow()

    wrz_buttons(tags)

    DrawText(str.encode(wrz_tags(image_idx, dicts)), 70, 540, 20, WHITE)

    EndDrawing()

if not exit_without_saving:
    print(f"Exiting... Writing {len(tags)} tag(s)...")
    for t in tags:
        print(f"Writing {t}.tag... ", end='')
        with open(f"{source_folder}/{t}.tag", "a") as f:
            counter = 0
            for d in dicts:
                if t in d["tags"]:
                    f.write(f"{d["filename"]}\n")
                    counter += 1

        unduplicated_lines = []

        with open(f"{source_folder}/{t}.tag", "r") as f:
            lines = f.readlines()
            unduplicated_lines = list(set(lines))

        with open(f"{source_folder}/{t}.tag", "w") as f:
            f.writelines(unduplicated_lines)
            
        print(f"wrote {counter} filename(s).")