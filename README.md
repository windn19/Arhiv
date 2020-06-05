# Checking the availability of files in the archive and checking the contents
The program checks the archive for the presence of text files with a name specified by the mask for the presence of words specified in another file in them and writes the number of matches to the file.
## Installation
The program is written in Python 3.7 and it is expected that it is already installed
In case of conflict with Python2, use pip3. Install the necessary modules:

pip install -r requirements.txt

## Use
At startup, a graphical form appears, in the first field of which the path to the file is indicated, it can also be selected using the "Open" button (the path is indicated absolute). The next field indicates the path to the file with file name masks (the characters *,? And others used in Windows are allowed). Next is the path to the file with the words to search.
The program checks the folder in which it is located for the presence of archives - zip, 7z, rar - and opens them and checks for the presence of files. If they are found, they will be copied to the working folder along the path: search_word / source_ archive_name / path to the file in the archive / file name.
After processing of all archives is completed, an information window appears with the words "Done"
If there is a checkmark in the first checkbox, the program leaves the initial data for unpacking the archive in the temp folder. For zip - a copy of the resulting structure, for 7z, rar - full unpacking of the archive.
The second checkmark is responsible for maintaining statistics in the text.txt file; accordingly, if there is a file, it is created and marks on the search words are made in it, otherwise only copies of the files are created.
