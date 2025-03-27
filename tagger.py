from raylib import *
# import sys
# import os
from os import listdir
from os.path import isfile, join
from typing import List
import argparse
from time import perf_counter
from math import floor
# import ctypes

#------------------------------------------------------------------------------

source_folder = "ERRNO"
exclude_tagged_files = False

parser = argparse.ArgumentParser(prog="WRZ: Gallery Tagger")
parser.add_argument("source_folder")
parser.add_argument("-e", "--exclude_tagged_files", action="store_true", default=False) # exclude images which are already tagged
parser.add_argument("-d", "--print_debug_information", action="store_true", default=False) # print timing information, mostly

args = parser.parse_args()

source_folder = args.source_folder
exclude_tagged_files = args.exclude_tagged_files
print_debug_information = args.print_debug_information

def debug_print(str):
    if print_debug_information: print("WRZ: DEBUG:", str)

#------------------------------------------------------------------------------

tic = perf_counter()

included_image_filetypes = [".jpg", ".jpeg", ".gif", ".png", ".bmp"]

filenames = [f for f in listdir(source_folder) if isfile(join(source_folder, f)) and any(f.endswith(e) for e in included_image_filetypes)]

tag_files = [f for f in listdir(source_folder) if isfile(join(source_folder, f)) and f.endswith(".tag")]
tags = [t[:-4] for t in tag_files]

if exclude_tagged_files:
    tagged_files = []

    for _t in tag_files:
        with open(join(source_folder, _t), "r", encoding="utf", errors="ignore") as t:
            lines = t.readlines()
            for l in lines:
                tagged_files.append(l.strip())

    filenames = [f for f in filenames if f not in tagged_files]

    if len(filenames) == 0:
        print(f"WRZ: ERROR: Flag -e was passed, but there are no untagged files in \"{source_folder}!\"\nWRZ: Exiting, no harm done.")
        exit(1)

filenames_full = [join(source_folder, f) for f in filenames]

# else: show all files
toc = perf_counter()

debug_print(f"Initial file loading took {toc - tic} seconds!")

#------------------------------------------------------------------------------

tic = perf_counter()

debug_print(tags)
debug_print(f"FILENAMES: {filenames}")

# tagged without ".tag" suffix i.e. according to 'tags,' not 'tag_files'
tag_dict = {}

for t in tag_files:
    debug_print(f"TAG FILEPATH: {t}")
    with open(join(source_folder, t), "r", encoding="utf8", errors="ignore") as f:
        files = [l.strip() for l in f.readlines()]
        debug_print(f"FILES ASSOC. WITH TAG {t}: {files}")
        tag_dict[t[:-4]] = files
        # debug_print(tag_dict[t[:4]])

image_dict = {}

for f in filenames:
    image_dict[f] = []
    for t in tags:
        if f in tag_dict[t]:
            image_dict[f].append(t)

debug_print(image_dict)

# exit(0)

toc = perf_counter()

debug_print(f"File tag association took {toc - tic} seconds!")

#------------------------------------------------------------------------------

_button_labels = list("12345QWERTASDFGZXCVB")

button_dict = {}

if len(tags) > len(_button_labels):
    print("Too many tags! Fix this! Email me! wrzeczak@protonmail.com")
    exit(1)

i = 0
for t in tags:
    button_dict[_button_labels[i]] = t
    i += 1

button_labels = _button_labels[:i]

button_column_count = len(button_labels) % 5 # width of the last column of buttons
button_row_count = 1 + floor((len(button_labels) - button_column_count) / 4)

debug_print(button_dict)
debug_print(button_row_count)
debug_print(button_column_count)

#------------------------------------------------------------------------------

WIDTH = 1
HEIGHT = 1
IMAGE_HEIGHT = 1
UI_HEIGHT = 1

if not print_debug_information: SetTraceLogLevel(LOG_FATAL)

InitWindow(810, 650, b"WRZ: Image Tagger")


WIDTH = floor(GetMonitorWidth(GetCurrentMonitor()) / 2)
HEIGHT = floor(GetMonitorHeight(GetCurrentMonitor()) / 2)

SetWindowSize(WIDTH, HEIGHT)
SetWindowPosition(floor(WIDTH / 2), floor(HEIGHT / 2))

IMAGE_HEIGHT = floor(0.7 * HEIGHT)
LABEL_HEIGHT = 40
UI_HEIGHT = HEIGHT - IMAGE_HEIGHT - LABEL_HEIGHT

BUTTON_HEIGHT = floor(UI_HEIGHT / (2 + button_row_count))
BUTTON_WIDTH = floor(WIDTH / 6)
BUTTON_X_OFFSET = floor(BUTTON_WIDTH / 2)
BUTTON_Y_OFFSET = LABEL_HEIGHT + IMAGE_HEIGHT + floor((UI_HEIGHT - (BUTTON_HEIGHT * button_row_count)) / 2)

SetTargetFPS(GetMonitorRefreshRate(GetCurrentMonitor()))

SetExitKey(KEY_NULL)
exit_dialog = False # once set true, will show a dialog asking the user if they want to save changes
save_changes = True

new_tag_dialog = False
text_input = ffi.new("char*", b"\0")

#------------------------------------------------------------------------------

image_idx = 0

debug_print(len(filenames))

image = filenames[image_idx]
tex = LoadTexture(str.encode(filenames_full[image_idx]))
image_tags = image_dict[image]

texture_load_error = False

SetWindowTitle(str.encode(f"WRZ: Image Tagger - \"{image}\""))


#------------------------------------------------------------------------------

while not WindowShouldClose():

    #------------------------------------------------------------------------------
    
    reload_picture = False

    GuiSetStyle(DEFAULT, TEXT_SIZE, 20)

    if IsKeyPressed(KEY_RIGHT) and not exit_dialog:
        reload_picture = True
        image_idx = (image_idx + 1) % len(filenames)        
    
    if IsKeyPressed(KEY_LEFT) and not exit_dialog:
        reload_picture = True
        image_idx = (image_idx - 1) % len(filenames)
    
    if reload_picture:
        tic = perf_counter()

        UnloadTexture(tex)
        image = filenames[image_idx]
        tex = LoadTexture(str.encode(filenames_full[image_idx]))

        image_tags = image_dict[image]

        toc = perf_counter()

        debug_print(f"Image reloading took {toc - tic} seconds! Loaded @ {tex.width}x{tex.height} with tags {image_tags}")

        if (tex.height * tex.width) == 0:
            texture_load_error = True
            debug_print(f"Texture Load Error! tex.width * tex.height == {tex.width * tex.height}")
        else:
            texture_load_error = False
        
        SetWindowTitle(str.encode(f"WRZ: Image Tagger - \"{image}\""))
    
    if IsKeyPressed(KEY_ESCAPE):
        if IsKeyDown(KEY_LEFT_SHIFT):
            save_changes = True
            break

        if new_tag_dialog: new_tag_dialog = False
        else: exit_dialog = not exit_dialog

    if IsKeyPressed(KEY_N):
        new_tag_dialog = True
    
    key = chr(GetKeyPressed())

    if key != chr(0) and not new_tag_dialog: 
        debug_print(f"{key} [{ord(key)}]")

        if key in button_labels:
            tag = button_dict[key]

            if tag in image_tags:
                image_tags.remove(tag)
                debug_print(f"{image} - {image_tags}")
            else:
                image_tags.append(tag)
                debug_print(f"{image} - {image_tags}")

    #------------------------------------------------------------------------------
    
    BeginDrawing()

    ClearBackground(BLACK)

    DrawRectangle(0, IMAGE_HEIGHT + LABEL_HEIGHT, WIDTH, UI_HEIGHT, DARKGRAY)

    DrawText(str.encode(str(image_tags)), 10, IMAGE_HEIGHT + 8, 30, WHITE)

    if texture_load_error == False:
        h = IMAGE_HEIGHT - 20
        # h/y = w/x -> h * x / y = w
        w = floor((h * tex.width) / tex.height)

        DrawRectangle(floor((WIDTH - w - 30) / 2), 5, floor(w + 10), h + 10, WHITE)
        DrawTexturePro(tex, [ 0, 0, tex.width, tex.height ], [ 0, 0, w, h ], [ -1 * ((WIDTH - w - 20) / 2), -10 ], 0, WHITE)
    else:
        m1 = str.encode(f"Error Loading File!!! w = {tex.width}, h = {tex.height}")
        m2 = str.encode(image)

        font_size = 30
        w1 = MeasureText(m1, font_size)
        w2 = MeasureText(m2, font_size)

        DrawText(m1, floor((WIDTH - w1) / 2), floor((IMAGE_HEIGHT / 2) - font_size), font_size, WHITE)
        DrawText(m2, floor((WIDTH - w2) / 2), floor(IMAGE_HEIGHT / 2), font_size, WHITE)

    GuiSetStyle(DEFAULT, TEXT_SIZE, 20)

    i = 0

    for l in button_labels:
        x = i % 5
        y = floor((i - x) / 4)

        GuiButton([(x * BUTTON_WIDTH) + BUTTON_X_OFFSET, (y * BUTTON_HEIGHT) + BUTTON_Y_OFFSET, BUTTON_WIDTH, BUTTON_HEIGHT ], str.encode(f"{l} - {button_dict[l]}"))
        i += 1

    GuiSetStyle(DEFAULT, TEXT_SIZE, 20)

    if exit_dialog:
        DrawRectangle(0, 0, WIDTH, HEIGHT, Fade(WHITE, 0.7))
        exit_dialog_result = GuiMessageBox([floor(WIDTH / 4), floor(HEIGHT / 4), floor(WIDTH / 2), floor(HEIGHT / 2)], GuiIconText(ICON_EXIT, str.encode("Close Window")), str.encode("Do you want to exit and save changes?"), str.encode("Exit With Changes;Exit Without Saving;Cancel"))
        
        match(exit_dialog_result):
            case 0: # close window button
                debug_print("User Cancelled Exit Dialog (X)")
                exit_dialog = False
            case 1:
                debug_print("User Exited (Save Changes)")
                save_changes = True
                break;
            case 2:
                debug_print("User Exited (Do Not Save Changes)")
                save_changes = False
                break;
            case 3:
                debug_print("User Cancelled Exit Dialog (Cancel)")
                exit_dialog = False
    
    if new_tag_dialog:
        DrawRectangle(0, 0, WIDTH, HEIGHT, Fade(WHITE, 0.7))

        result = GuiTextInputBox([floor(WIDTH / 4), floor(HEIGHT / 4), floor(WIDTH / 2), floor(HEIGHT / 2)], str.encode("Create New Tag"), str.encode("Type new tag name - must result in a valid filename!"), str.encode("Ok;Cancel"), text_input, 24, ffi.new("bool*", True))

        if result == 1: # "Ok"
            new_tag = ffi.string(text_input).decode("utf-8").strip()

            if new_tag not in tags:
                debug_print(new_tag)
                debug_print(tags)
                debug_print(tag_files)

                if len(tags) < len(_button_labels):
                    button_dict[_button_labels[len(button_labels)]] = new_tag
                    tags.append(new_tag)
                    tag_files.append(join(new_tag, ".tag"))
                    open(f"{source_folder}\\{new_tag}.tag", "w").close() # touch the new tag file
                
                debug_print(tags)
                debug_print(tag_files)

            exit(2)
        elif result == 0 or result == 2:
            new_tag_dialog = False
            text_input = ffi.new("char*", b"\0")

    EndDrawing()

#------------------------------------------------------------------------------

if save_changes:
    debug_print("Saving changes...")

    debug_print("Old tag dictionary:")
    debug_print(tag_dict)

    new_tag_dict = {}

    for t in tags:
        new_tag_dict[t] = []

    for n in filenames:
        s = image_dict[n]

        for t in tags:
            if t in s:
                new_tag_dict[t].append(f"{n}\n")    
    
    debug_print("New tag dictionary:")
    debug_print(new_tag_dict)

    for t in tags:
        debug_print(f"Writing {len(new_tag_dict[t])} files to {t}.tag...")

        if not exclude_tagged_files: # open with "w"
            with open(f"{source_folder}\\{t}.tag", "w") as f:
                f.writelines(new_tag_dict[t])
        else:
            with open(f"{source_folder}\\{t}.tag", "a") as f:
                f.writelines(new_tag_dict[t])