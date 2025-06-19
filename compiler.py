import json
import argparse as ag
from os import listdir
from os.path import join, exists, getsize, isfile
from math import floor

#------------------------------------------------------------------------------
# argument parsing

parser = ag.ArgumentParser(prog="WRZ: Gallery 3")
parser.add_argument("source_folder")
parser.add_argument("-o", "--output_file", nargs='?', type=ag.FileType('w'))
parser.add_argument("-c", "--compress", action="store_true")
parser.add_argument("-t", "--tagged", action="store_true")
parser.add_argument("-n", "--column_count", type=int, default=4)
parser.add_argument("-d", "--print_debug", action="store_true", default=True)

args = parser.parse_args()

source_folder = args.source_folder
compress = args.compress
tagged = args.tagged
output_file_path = args.output_file.name
column_count = args.column_count

#------------------------------------------------------------------------------
# utility functions

def gen_n_columns(files, n):
    output = [[] for _ in range(n)]
    for i in range(len(files)):
        output[i % n].append(files[i])
    
    return output

def wrzLoadData() -> dict:
	data = {}

	if (not exists(JSON_PATH)) or (getsize(JSON_PATH) == 0):
		print(f"WRZ: ERROR: File '{JSON_PATH}' does not exist or is empty; run tagger.py to generate this file first!")
		exit(-2)

	else:
		# read the JSON file and return its contents
		with open(JSON_PATH, "r") as j:
			data = json.load(j)

		# data validation - if tag_list mismatches the rest of the store, json will throw KeyError
		try:
			tag_list = data['tag_list']

			for tag in tag_list:
				try:
					_ = data['tag'][tag]
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
# global variables

JSON_PATH = join(source_folder, "store.json") # edit this filepath to point to an alternative data store
ACCEPTED_FILETYPES = [".png", ".jpg", ".gif", ".jpeg", ".bmp"] # edit this list to add files you think stb_image should be able to load

images = listdir(source_folder)
images = [i for i in images if i[-4:] in ACCEPTED_FILETYPES] # filter out .webp, .mp4, store.json, etc.

data = wrzLoadData()

#------------------------------------------------------------------------------
# compress files if -c flag is passed

if compress == True:
    if os.path.isdir(f"{source_folder}-compressed/"): # remove all previously compressed files (easier than checking which ones are already)
        subprocess.call(["rm", "-rf", f"{source_folder}-compressed"])
    subprocess.call(["python3", "cruncher.py", source_folder]) # call the compressor script TODO: make this an imported module?
    files = [f for f in listdir(f"{source_folder}-compressed") if isfile(join(f"{source_folder}-compressed", f))]
else:
    files = [f for f in listdir(source_folder) if isfile(join(source_folder, f))]

#------------------------------------------------------------------------------

# TODO: detect this automatically - is it useful to ignore tags in a tagged setup?
if tagged:
	tags = data["tag_list"]
	if len(tags) == 0:
		print("WRZ: ERROR: tag_list is empty! Either run this without -t, or fix malformed JSON.")
		exit(-5)

	print(f"Writing tags for {source_folder}...")

	for t in tags:
		tag_images = data["tag"][t]

		with open(join(source_folder, f"{t}.html"), "w") as h:
			def printf(s):
				print(s, file=h)

			print(f"Writing {h.name}, {len(tag_images)} images.")

			image_columns = gen_n_columns(tag_images, column_count)

			printf("<!DOCTYPE html>")
			printf("<html lang=\"en\">\n<head>")
			printf("<link rel=\"stylesheet\" href=\"../styles.css\">")    
			printf(f"<title>Image View [{t}]</title>")
			printf("</head>")
			printf("<body>")
			printf("<p>")
			printf("<!----------- auto generated data begins here ----------------->")
			printf("<div id=\"gallery-row\">")

			for l in image_columns:
				printf("\t<div id=\"gallery-column\">")

				for f in l:
					printf(f"\t\t<a href=\"{f}\"><img src=\"{f}\" alt=\"{f}\"></a>")
				printf("\t</div>")

			printf("</div>\n</p>\n</body>\n</html>")

#------------------------------------------------------------------------------


image_columns = gen_n_columns(images, column_count)

with open(output_file_path, "w") as o:
	def printf(s):
		print(s, file=o)

	printf("<!DOCTYPE html>")
	printf("<html lang=\"en\">\n<head>")
	printf("<link rel=\"stylesheet\" href=\"styles.css\">")    
	printf(f"<title>Global Image View</title>")
	printf("</head>")
	printf("<body>")
	printf("<p>")

	if tagged:
		print("<div id=\"tag-display\"><b>TAGS &mdash;</b>&nbsp;", end="", file=o)

		tags = data["tag_list"]

		for t in tags:
			print(f"<a href=\"{source_folder}/{t}.html\">{t}</a>,&nbsp;", end="", file=o)

		printf("</div>\n<br/>\n")

	printf("<div id=\"gallery-row\">")

	print(f"Writing main gallery view to {output_file_path}...")

	for l in image_columns:
		printf("\t<div id=\"gallery-column\">")

		for f in l:
			if compress and not f.endswith(".gif") and not f.endswith(".mp4"):
				printf(f"\t\t<a href=\"{source_folder}/{f}\"><img src=\"{source_folder}-compressed/{f}\" alt=\"{source_folder}/{f}\"></a>")
			else:
				printf(f"\t\t<a href=\"{source_folder}/{f}\"><img src=\"{source_folder}/{f}\" alt=\"{source_folder}/{f}\"></a>")

		printf("\t</div>")

	printf("</div>")
	printf("</p>")
	printf("</body></html>")

#------------------------------------------------------------------------------

print("\n-----------------------------------------------\n")
print("Copy and paste the CSS code below into your site's CSS file; #gallery-column needs to be redefined to have a certain width!\n")
print("#gallery-column {")

width_percent = floor((1 / column_count) * 100)

print(f"\tflex: {width_percent}%;")
print(f"\twidth: {width_percent}%;")
print("\tpadding: 0 0px;\n}")
print("\n-----------------------------------------------\n")