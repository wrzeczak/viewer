from raylib import *
# from pyray import Color
import json
import argparse as ag
from os import listdir
from os.path import join, exists, getsize
from math import floor
from typing import List

#------------------------------------------------------------------------------
# argument parsing

parser = ag.ArgumentParser(prog="WRZ: Gallery 3", description="A basic image tagging system, v.3")
parser.add_argument("-d", "--print_debug_info", action="store_true", default=False)
parser.add_argument("source_folder")

args = parser.parse_args()
print_debug_info = args.print_debug_info
source_folder = args.source_folder

#------------------------------------------------------------------------------
# utility functions

# takes string of form #RRGGBB
def GetColorHex(hex : str):
	hex = hex[1:] # remove leading hashtag
	hex = "0x" + hex + "FF" # format the number in the way int() wants it
 	# print(hex)
	return GetColor(int(hex, 16))

# prints only if the -d option is passed
def debug_print(s : str):
	if print_debug_info: print(f"WRZ: DEBUG: {s}")

# shorthand for str.encode()
def byte(s : str) -> bytes:
	return str.encode(s)

#------------------------------------------------------------------------------
# global variables

WIDTH = 1200
HEIGHT = 900
JSON_PATH = join(source_folder, "store.json") # edit this filepath to point to an alternative data store
ACCEPTED_FILETYPES = [".png", ".jpg", ".gif", ".jpeg", ".bmp"] # edit this list to add files you think stb_image should be able to load

# styles - i wanted to use raygui's style but they proved troublesome with this python version
BACKGROUND_COLOR = GetColorHex("#22222A")
FLOOR_COLOR = GetColorHex("#1A1A22")
TAG_BOX_COLOR = GetColorHex("#1C1C24")
DIALOG_COLOR = GetColorHex("#33333B")

# colors for the image states when disabled
MUTED_DUPLICATE_COLOR = GetColorHex("#143E20")
MUTED_MARKED_COLOR = GetColorHex("#3A2442")

# as above, when enabled
DUPLICATE_COLOR = GetColorHex("#287B41")
MARKED_COLOR = GetColorHex("#6C427B")

INFO_FONT_SIZE = 20 # for the three image states on the left of the image
TAG_FONT_SIZE = 20 # for the tagging dialog in the floor
IMAGE_FONT_SIZE = 20 # for the image filename and size below the image
DIALOG_FONT_SIZE = 40 # for the text of the new tag
DELETING_FONT_SIZE = 60 # for the big text that says "DELETING TAG"

# text colors for the above pieces of info
TAG_ON_COLOR = WHITE
TAG_OFF_COLOR = GRAY
IMAGE_COLOR = WHITE

# note: all of these must be integers, raylib does not perform automatic typecasting
HEAD_HEIGHT = 600 # the top section, where the image and additional info are rendered
FLOOR_HEIGHT = HEIGHT - HEAD_HEIGHT # the bottom section, where the buttons are rendered
IMAGE_PADDING = 50 # padding from the top of the floor to the bottom of the image
IMAGE_HEIGHT = HEAD_HEIGHT - (2 * IMAGE_PADDING)

TAG_X_PADDING = 50 # offsets of the tag block - no horizontal padding
TAG_Y_PADDING = 50

TAG_WIDTH = floor((WIDTH - (2 * TAG_X_PADDING)) / 5)
TAG_HEIGHT = 2 * TAG_FONT_SIZE
TAG_SPACE = floor((FLOOR_HEIGHT - (2 * TAG_Y_PADDING) - (4 * TAG_HEIGHT)) / 4) 

#------------------------------------------------------------------------------
# keybinds

WK_ADVANCE_IMAGES = KEY_RIGHT
WK_RETREAT_IMAGES = KEY_LEFT  # isn't it nice how advance and retreat line up? <3
WK_MARK_DUPLICATE = KEY_SPACE
WK_MARK_MARKED = KEY_TAB
WK_TAG_KEYS = list("12345qwertasdfgzxcvb") # use lowercase version if changing these, also keep to 20 keys
WK_QUIT = KEY_ESCAPE
WK_NEW_TAG = KEY_ENTER
WK_DEL_TAG = KEY_BACKSPACE

if len(WK_TAG_KEYS) > 20: 
	print("Too many tag keys! Exiting!")
	exit(-4)

SetExitKey(WK_QUIT)

#------------------------------------------------------------------------------

# JSON format used by this program
# { "tag_list": [str] -> list of all image tags, 
#   "bad_files": [str] -> list of filenames that can't be loaded by raylib,
#   "duplicate_files": [str] -> list of filenames marked manually as duplicates,
#   "marked_files": [str] -> a list of files marked by the user for their own purposes; i use this to mark files i want to delete,
#   "tag": { "tag1": [str], "tag2": [str], ....} -> a structure containing every tag which keys a list of filenames }
#   so, to access the filenames attached to a tag, use ['tag']['tag_you_want_to_access']
#   this is done this way to prevent name conflicts with any of the above built-in data keys
def wrzLoadData() -> dict:
	data = {}

	if (not exists(JSON_PATH)) or (getsize(JSON_PATH) == 0):
		# create the json file if the file does not exist or is empty
		with open(JSON_PATH, "w") as j:
			data = { "tag_list": [], "bad_files": [], "duplicate_files": [], "marked_files": [], "tag": {} }
			j.write(json.dumps(data))
			print(f"No 'store.json' found in {source_folder}, automatically generating one. Edit JSON_PATH in tagger.py if you wish to use a different JSON data store.")

			return data
	else:
		# read the JSON file and return its contents
		with open(JSON_PATH, "r") as j:
			data = json.load(j)

		# data validation - if tag_list mismatches the rest of the store, json will throw KeyError
		try:
			tag_list = data['tag_list']

			for tag in tag_list:
				try:
					debug_print(f"{tag}: {data['tag'][tag]}")
				except KeyError:
					print(f"WRZ: KeyError: In {JSON_PATH}, 'tag_list' does not match the rest of the data store; remove extraneous entry '{tag}' in 'tag_list' and retry. Exiting...")
					exit(-2)

			# accessing data that does not exist throws KeyError
			_ = data['bad_files']
			_ = data['duplicate_files']
			_ = data['marked_files']

			# cleanup files that may have been deleted
			for f in data["bad_files"]:
				if not exists(join(source_folder, f)):
					data["bad_files"].remove(f)

			for f in data["duplicate_files"]:
				if not exists(join(source_folder, f)):
					data["duplicate_files"].remove(f)

			for f in data["marked_files"]:
				if not exists(join(source_folder, f)):
					data["marked_files"].remove(f)

		except KeyError:
				print(f"WRZ: KeyError: In {JSON_PATH}, at least one of the four required tags, 'tag_list,' 'bad_files,' 'duplicate_files,' and 'marked_files' is missing/malformed. Exiting...")
				exit(-1)	


	return data

#------------------------------------------------------------------------------

# takes in a Texture2D to be drawn, scaling and placing it appropriately
def wrzDrawImage(img):
	w = img.width
	h = img.height

	if (w * h) == 0:
		# bad image - draw error message
		m1 = b"Error loading image! Format likely unsupported by raylib, despite having a supported file extension."
		message_width = MeasureText(m1, 20)
		DrawText(m1, floor((WIDTH - message_width) / 2), floor(HEAD_HEIGHT / 2) + 10, 20, RED)
		return

	new_w = floor(IMAGE_HEIGHT * (w / h))

	scale = new_w / w

	x_offset = floor((WIDTH - new_w) / 2)
	y_offset = IMAGE_PADDING

	DrawTextureEx(img, (x_offset, y_offset), 0.0, scale, WHITE)

#------------------------------------------------------------------------------

def wrzDrawBaseUI():
	DrawRectangle(0, HEAD_HEIGHT, WIDTH, FLOOR_HEIGHT, FLOOR_COLOR)

#------------------------------------------------------------------------------

# returns is_image_bad, is_image_duplicate, is_image_marked
def wrzGetImageData(data, image_path, image_tex):
	is_image_bad = (image_tex.width * image_tex.height) == 0
	if is_image_bad and not (image_path in data["bad_files"]): # should already be there
		data["bad_files"].append(image_path)

	is_image_duplicate = image_path in data["duplicate_files"]
	is_image_marked = image_path in data["marked_files"]

	return is_image_bad, is_image_duplicate, is_image_marked

#------------------------------------------------------------------------------

def wrzDrawImageData(image_path, image_tex, is_image_duplicate, is_image_marked):
	# image metadata - filename and width
	DrawText(byte(f"{image_path} [{image_tex.width}, {image_tex.height}]"), 10, 10, IMAGE_FONT_SIZE, IMAGE_COLOR)

	DrawRectangle(0, IMAGE_PADDING + 90, WIDTH, 2 * INFO_FONT_SIZE, MUTED_DUPLICATE_COLOR)
	if is_image_duplicate: DrawRectangle(floor(WIDTH / 2), IMAGE_PADDING + 95, floor(WIDTH / 2), (2 * INFO_FONT_SIZE) - 10, DUPLICATE_COLOR)
	
	DrawRectangle(0, IMAGE_PADDING + 150, WIDTH, 2 * INFO_FONT_SIZE, MUTED_MARKED_COLOR)
	if is_image_marked: DrawRectangle(floor(WIDTH / 2), IMAGE_PADDING + 155, floor(WIDTH / 2), (2 * INFO_FONT_SIZE) - 10, MARKED_COLOR)

	# image data - duplicate and marked
	if is_image_duplicate:
		DrawText(b"DUPLICATE FILE", 10, IMAGE_PADDING + floor(INFO_FONT_SIZE / 2) + 90, INFO_FONT_SIZE, DUPLICATE_COLOR)

	if is_image_marked:
		DrawText(b"MARKED FILE", 10, IMAGE_PADDING + floor(INFO_FONT_SIZE / 2) + 150, INFO_FONT_SIZE, MARKED_COLOR)

#------------------------------------------------------------------------------

def wrzGetImageTags(data : dict, image_path : str) -> List[str]:
	tag_data = data['tag']
	tags = []

	for tag, files in tag_data.items():
		if image_path in files:
			tags.append(tag)

	return tags

#------------------------------------------------------------------------------

def wrzDrawImageTags(data : dict, image_path : str):
	tag_count = len(data["tag_list"])
	image_tags = wrzGetImageTags(data, image_path)

	for i, key in enumerate(WK_TAG_KEYS):
		x = i % 5
		y = (i - x) % 4

		vx = TAG_X_PADDING + (TAG_WIDTH * x)
		vy = HEAD_HEIGHT + TAG_Y_PADDING + ((TAG_HEIGHT + TAG_SPACE) * y)
		DrawRectangleLines(vx, vy, TAG_WIDTH, TAG_HEIGHT, TAG_BOX_COLOR)

		ty = floor((TAG_HEIGHT - TAG_FONT_SIZE) / 2)

		tx = 0
		if i < tag_count:
			tag = data['tag_list'][i]
			text = byte(f"[{key}] {tag}")
			tx = floor((TAG_WIDTH - MeasureText(text, TAG_FONT_SIZE)) / 2)
			DrawText(text, vx + tx, vy + ty, TAG_FONT_SIZE, TAG_ON_COLOR if tag in image_tags else TAG_OFF_COLOR)
		else:
			text = byte(f"[{key}]")
			tx = floor((TAG_WIDTH - MeasureText(text, TAG_FONT_SIZE)) / 2)
			DrawText(text, vx + tx, vy + ty, TAG_FONT_SIZE, TAG_OFF_COLOR)

#------------------------------------------------------------------------------

global __new_tag
__new_tag = ""

# NOTE: does not actually add a new tag, simply provides the dialog
# TODO: make this look better
def wrzAddNewTag(data):
	tag_count = len(data["tag_list"])
	if tag_count >= 20:
		print("WRZ: DEBUG: Too many tags! Cannot create new one.")
		return False, None

	global __new_tag
	DrawRectangle(0, 0, WIDTH, HEIGHT, Fade(FLOOR_COLOR, 0.5))

	wx = 150
	wy = 200
	wh = (2 * INFO_FONT_SIZE) + 40 + DIALOG_FONT_SIZE

	DrawRectangle(wx, wy, WIDTH - 300, wh, DIALOG_COLOR)
	DrawRectangle(wx, wy, WIDTH - 300, 2 * INFO_FONT_SIZE, Fade(FLOOR_COLOR, 0.5))
	DrawText(b"CREATE NEW TAG", wx + 10, wy + floor(INFO_FONT_SIZE / 2), INFO_FONT_SIZE, WHITE)

	key = GetCharPressed()
	if key > 0: 
		__new_tag = (__new_tag.strip()) + chr(key)

	if IsKeyPressed(KEY_BACKSPACE):
		__new_tag = __new_tag.strip()[:-1]

	if IsKeyPressed(KEY_DELETE):
		__new_tag = ""

	DrawText(byte(__new_tag), wx + 10, wy + (2 * INFO_FONT_SIZE) + 20, DIALOG_FONT_SIZE, WHITE)

	new_tag = str(__new_tag)
	return True, new_tag

#------------------------------------------------------------------------------

def main():
	#------------------------------------------------------------------------------

	InitWindow(WIDTH, HEIGHT, b"WRZ: Viewer 3")
	SetTargetFPS(GetMonitorRefreshRate(GetCurrentMonitor()))

	data = wrzLoadData()
	images = listdir(source_folder)
	images = [i for i in images if i[-4:] in ACCEPTED_FILETYPES] # filter out .webp, .mp4, store.json, etc.

	image_idx = 0
	image_path = images[image_idx]
	image_tex = LoadTexture(byte(join(source_folder, image_path)))
	image_tags = wrzGetImageTags(data, image_path)
	image_dims = (image_tex.width, image_tex.height)

	show_tag_dialog = False
	deleting_tag = False

	new_tag = None

	while not WindowShouldClose():
		#------------------------------------------------------------------------------

		if IsKeyPressed(WK_NEW_TAG):
			show_tag_dialog = not show_tag_dialog
			if show_tag_dialog == False:
				# do something with the new tag
				debug_print(f"New Tag: {new_tag}")
				data["tag_list"].append(new_tag)
				data["tag"][new_tag] = []

				new_tag = None
				__new_tag = ""

		if not show_tag_dialog and IsKeyPressed(WK_DEL_TAG):
				deleting_tag = not deleting_tag

		if (not show_tag_dialog) and (not deleting_tag):
			# unloading and reloading the texture every frame only barely stutters on images around 3000x3000
			if IsKeyPressed(WK_RETREAT_IMAGES):
				# unload old image, move through images[], load new one
				image_idx -= 1

				UnloadTexture(image_tex)
				image_idx %= len(images)
				image_path = images[image_idx]
				image_tex = LoadTexture(byte(join(source_folder, image_path)))
				image_tags = wrzGetImageTags(data, image_path)

			if IsKeyPressed(WK_ADVANCE_IMAGES):
				# unload old image, move through images[], load new one
				image_idx += 1

				UnloadTexture(image_tex)
				image_idx %= len(images)
				image_path = images[image_idx]
				image_tex = LoadTexture(byte(join(source_folder, image_path)))
				image_tags = wrzGetImageTags(data, image_path)

			is_image_bad, is_image_duplicate, is_image_marked = wrzGetImageData(data, image_path, image_tex)

			if IsKeyPressed(WK_MARK_MARKED):
				if is_image_marked:
					data["marked_files"].remove(image_path)
					is_image_marked = False
				else:
					data["marked_files"].append(image_path)
					is_image_marked = True

			if IsKeyPressed(WK_MARK_DUPLICATE):
				if is_image_duplicate:
					data["duplicate_files"].remove(image_path)
					is_image_duplicate = False
				else:
					data["duplicate_files"].append(image_path)
					is_image_duplicate = True

		if not show_tag_dialog:
			# do tag assignment keypresses, bypassing the exlucsion delete tag dialog above
			if not deleting_tag:
				key = chr(GetCharPressed())
				tags = data["tag_list"]

				if key in WK_TAG_KEYS:
					key_index = WK_TAG_KEYS.index(key)
					if key_index < len(tags): # the key pressed is associated with a tag
						tag = tags[key_index]
						filenames = data["tag"][tag]

						if image_path in filenames: # remove image from tag
							data["tag"][tag].remove(image_path)
						else:
							data["tag"][tag].append(image_path)
			else:
				key = chr(GetCharPressed())
				tags = data["tag_list"]

				if key in WK_TAG_KEYS:
					key_index = WK_TAG_KEYS.index(key)
					if key_index < len(tags): # the key pressed is associated with a tag
						tag = tags[key_index]
						# safety print so that the deleted data is saved in the console for recovery
						# if you accidentally deleted data, you can copy paste it from the terminal
						# and manually re-enter it into the JSON file
						# one note, JSON does not accept single-quotes for strings, but python prints
						# lists of strings with single-quotes. you will have to find-and-replace all
						# single quotes with double quotes in order for the parser to accept it
						print(f'WRZ: DEBUG: Deleted tag "{tag}": {data["tag"][tag]} .') 
						data["tag_list"].remove(tag) # remove tag from tag_list
						data["tag"].pop(tag)		 # and from the tag structure

					deleting_tag = False # exit the delete dialog


		#------------------------------------------------------------------------------

		BeginDrawing()

		ClearBackground(BACKGROUND_COLOR)
		wrzDrawBaseUI()

		wrzDrawImageData(image_path, image_tex, is_image_duplicate, is_image_marked)
		wrzDrawImage(image_tex)
		wrzDrawImageTags(data, image_path)

		# DrawFPS(10, 10)

		if show_tag_dialog:
			show_tag_dialog, new_tag = wrzAddNewTag(data)

		if deleting_tag:
			DrawRectangle(0, 0, WIDTH, HEAD_HEIGHT, Fade(FLOOR_COLOR, 0.5))
			text = b"!! IRREVERSIBLE DELETE TAG !!"
			tw = MeasureText(text, DELETING_FONT_SIZE)
			tx = floor((WIDTH - tw) / 2)
			ty = floor((HEAD_HEIGHT - DELETING_FONT_SIZE) / 2)
			DrawRectangle(tx - 20, ty - 20, tw + 40, DELETING_FONT_SIZE + 40, FLOOR_COLOR)

			DrawText(text, tx, ty, DELETING_FONT_SIZE, RED)


		EndDrawing()

		#------------------------------------------------------------------------------

	#------------------------------------------------------------------------------

	with open(JSON_PATH, "w") as j:
		j.write(json.dumps(data))

if __name__ == "__main__": main()