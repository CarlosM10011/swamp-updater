Swamp Updater
================================================================================

This tool automates the process of updating a blind-person friendly FPS called
swamp by downloading and unzipping the latest patch. It also allows you to
exclude certain files from being replaced by adding them to a text file that is
created when first launching it. This repository includes two versions of the
utility: one updates the stable version, and the other updates the latest beta.
Note that because of the way the zip files are packaged currently, you must
download the swamp zip file because the patched zips do not have all the files,
including the games assets.

How to Build
================================================================================

In order to build, you need python 3.7. Pyinstaller is also required if you wish
to build a self-packaged binary. Note that the default pyinstaller bootloaders
get flagged by MS Defender, so you may have to build your own bootloaders if
that happens to you. Building the pyinstaller bootloaders requires either MinGW
or Visual Studio on Windows, so it may be easier for you to use the precompiled
binaries located under the dist directory.

Installation / Usage
================================================================================
To use, simply copy over the swamp-updater.exe and swamp-updater-beta.exe
binaries under the dist directory to your swamp directory. When ever you wish to
update, simply run the executable from Windows Explorer. Edit the
excluded_files.txt file if you wish to exclude files from being replaced.

Bugs
================================================================================

Any improvements are greatly appreciated (feature requests, bug reports, pull
requests, etc). I literally coded this thing up over night because I got
aggravated with the file download stalling when downloading the updates, so it
by all means is not perfect.
