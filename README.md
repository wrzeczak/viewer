# WRZ: Viewer

An image tagging system with the ability to generate a webpage for easy viewing online.

### Example

Open `example.html` to see the final product of the system. The process began with the folder `example/`, containing nine images. Then, `py tagger.py example` opened the tagger, a program which tags the files. After tagging the files, the program was exited (`ESC` or hitting the X). Then, `py compiler.py -o example.html -t example` compiled the webpage `example.html` and tag pages `dole.html`, `flag.html`, and `kemp.html`. The `-t` option tells the compiler that the folder is tagged, and is optional. The `-o` option is required and tells the program the output file[^2].

### Full CLI Featureset

`py tagger.py [-d] [-e] folder_path`

`-e` will exclude any files with tags already attached to them. This is useful if you are adding a few files to a large dataset and want to avoid scrolling through files you don't intend to modify the tags of.

`py compiler.py [-o output_file] [-c] [-t] folder_path`

`folder_path` is the folder containing all the images; `output_file` is the root HTML file that is created.

`-c` will create a compressed version of the folder; this is intended to save bandwidth if you are displaying high-resolution images. The compressed images are displayed on the root pages[^3], and when the images are clicked, the full-resolution image is loaded. **This only works on Linux using imagemagick**. (The idea being that your web server is probably running Linux, and you only need to store compressed files on the web server)

`-t` will indicate to the compiler that the tag pages should be compiled. The program will not automatically do this.

### Tagger Usage

Run the tagger on a folder full of images. The system will create/read any files with the `.tag` extension. It supports 20 tags in one folder (this would be pretty easy to extend) and will bind the right-hand side of the keyboard. Press on a key to toggle a tag on a given image (clicking the buttons doesn't actually work; this is meant to be as mouse-free as possible). Press `n` to create a new tag, and use the left and right arrow keys to cycle through the folder. Hit `ESC` to exit (prompts you with a menu), or `SHIFT + ESC` to exit and save (no prompt). Running `tagger.py` with the `-d` option will print debug information - this is really only meant for development and can be safely ignored by users. Passing `-e` will exclude all images that already have tags.

---

[^2]: As of now, the output location of the tag files is not modifiable at runtime.

[^3]: As of now, tag pages do not display the compressed files.
