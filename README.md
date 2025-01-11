# WRZ: Viewer

An image tagging system with the ability to generate a webpage for easy viewing online.

### Example

Open `example.html` to see the final product of the system. The process began with the folder `example/`, containing nine images. Then, the file `TAGSET` was created, which tells the program which tags to use[^1] Then, `py tagger.py example` opened the tagger, a program which tags the files. After tagging the files, the program was exited (`ESC` or hitting the X). Then, `py compiler.py -o example.html -t example` compiled the webpage `example.html` and tag pages `dole.html`, `flag.html`, and `kemp.html`. The `-t` option tells the compiler that the folder is tagged, and is optional. The `-o` option is required and tells the program the output file[^2].

### Full Featureset

`py tagger.py [-e] [folder_path]`

`-e` will exclude any files with tags already attached to them. This is useful if you are adding a few files to a large dataset and want to avoid scrolling through files you don't intend to modify the tags of.

`py compiler.py [-o output_file] [-c] [-t] folder_path`

`folder_path` is the folder containing all the images; `output_file` is the root HTML file that is created.

`-c` will create a compressed version of the folder; this is intended to save bandwidth if you are displaying high-resolution images. The compressed images are displayed on the root pages[^3], and when the images are clicked, the full-resolution image is loaded.

`-t` will indicate to the compiler that the tag pages should be compiled. The program will not automatically do this.

---

[^1]: The tagger program itself should probably only be run with ten tags in the `TAGSET` file at a time. Tags not included in the `TAGSET` will not be modified, but the program will display them under the images.

[^2]: As of now, the output location of the tag files is not modifiable at runtime.

[^3]: As of now, tag pages do not display the compressed files.