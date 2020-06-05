import zipfile
import shutil
import rarfile
from os.path import split, exists, join
from os import listdir, mkdir, walk, getcwd, makedirs
from fnmatch import fnmatch
import py7zr
import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QApplication, QLineEdit, QFileDialog, QMessageBox, QCheckBox
from multiprocessing import Process
from os.path import splitext


class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.edit_arhive = QLineEdit('/sysroot/home/user/PycharmProjects/Arshiv', self)
        self.edit_arhive.setGeometry(10, 10, 470, 30)
        self.edit_mask = QLineEdit('/sysroot/home/user/PycharmProjects/Arshiv/maks1.txt', self)
        self.edit_mask.setGeometry(10, 50, 470, 30)
        self.edit_string = QLineEdit('/sysroot/home/user/PycharmProjects/Arshiv/string.txt', self)
        self.edit_string.setGeometry(10, 90, 470, 30)
        self.btn_open = QPushButton('Открыть', self)
        self.btn_open.move(490, 10)
        self.btn_open.clicked.connect(self.buttonClicked)
        self.btn_graf = QPushButton('Откр. Mask', self)
        self.btn_graf.move(490, 50)
        self.btn_graf.clicked.connect(self.button1Clicked)
        self.btn_graf1 = QPushButton('Открыть Str', self)
        self.btn_graf1.move(490, 90)
        self.btn_graf1.clicked.connect(self.button2Clicked)
        self.btn_graf2 = QPushButton('Сортировать', self)
        self.btn_graf2.move(490, 130)
        self.btn_graf2.clicked.connect(self.button3Clicked)
        self.check = QCheckBox('Переносить', self)
        self.check.toggle()
        self.check.move(10, 130)
        self.check.clicked.connect(self.check_cl)
        self.check_st = QCheckBox('Статистика', self)
        self.check_st.toggle()
        self.check_st.move(10, 150)
        # self.check.clicked.connect(self.check_st)
        self.btn_close = QPushButton('Close', self)
        self.btn_close.move(10, 250)
        self.btn_close.clicked.connect(self.close)
        self.setGeometry(300, 300, 600, 300)
        self.setWindowTitle('Event sender')
        self.status = self.statusBar()
        self.show()

    def check_cl(self, state):
        if state:
            self.check.setText('Переместить')
        else:
            self.check.setText('Скопировать')

    def buttonClicked(self):
        text = QFileDialog.getOpenFileName(self, 'Open file', getcwd())
        name = split(text[0])[0]
        self.edit_arhive.clear()
        self.edit_arhive.insert(name)
        self.status.showMessage(f'File: {name}')

    def button1Clicked(self):
        text = QFileDialog.getOpenFileName(self, 'Open file', self.edit_arhive.text())
        self.edit_mask.clear()
        self.edit_mask.insert(text[0])
        self.status.showMessage(f'File: {text[0]}')

    def button2Clicked(self):
        text = QFileDialog.getOpenFileName(self, 'Open file', self.edit_mask.text())
        self.edit_string.clear()
        self.edit_string.insert(text[0])
        self.status.showMessage(f'File: {text[0]}')

    def button3Clicked(self):
        start_path = self.edit_arhive.text()
        mask_file = self.edit_mask.text()
        string_file = self.edit_string.text()
        first = Inspector(string_file, mask_file, start_path, stat=self.check.checkState(),
                          stat_st=self.check_st.checkState())
        first.run()
        if self.check.checkState() and exists(join(start_path, 'temp')):
            shutil.rmtree(f'{start_path}/temp')
        QMessageBox.information(self, 'Sort', 'Done', QMessageBox.Ok)


class ZipExtract(Process):
    def __init__(self, arhiv, masks, strings, start_path, stats, sts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.masks = masks
        self.strings = strings
        self.start_path = start_path
        self.arhiv = arhiv
        self.cur_path = getcwd()
        self.stat = stats
        self.st = sts

    def run(self):
        print(getcwd())
        file = zipfile.ZipFile(f'{self.start_path}/{self.arhiv}')
        print(f'Взял архив: {self.arhiv}')
        for mask in self.masks:
            for name in file.namelist():
                if fnmatch(name, mask):
                    name_path = split(name)
                    file.extract(name, path=f'{self.start_path}/temp/{splitext(self.arhiv)[0]}')
                    print(f'Файл {name} сюда {self.start_path}/temp')
                    with open(f'{self.start_path}/temp/{splitext(self.arhiv)[0]}/{name}',
                              mode='r', encoding='utf8') as source:
                        data = source.read()
                    for string in self.strings:
                        count_string = data.count(string)
                        if count_string:
                            if not exists(f'{self.start_path}/{string}'):
                                mkdir(f'{self.start_path}/{string}')
                            if self.st:
                                with open(f'{self.start_path}/{string}/text.txt', mode='a', encoding='utf8') as out:
                                    out.write(
                                        f'{self.arhiv}   -   {name_path[1]}    - {string} - {count_string} совпадения\n')
                                    print(f'Add record {self.start_path}/{string}/text.txt')
                            makedirs(f'{self.start_path}/{string}/{splitext(self.arhiv)[0]}/{name_path[0]}',
                                     exist_ok=True)
                            shutil.copy(f'{self.start_path}/temp/{splitext(self.arhiv)[0]}/{name}',
                                        f'{self.start_path}/{string}/{splitext(self.arhiv)[0]}/{name_path[0]}')
                            print(f'Copy {self.start_path}/{string}/{name}')


class Extract7z(Process):
    def __init__(self, arhiv, masks, strings, start_path, stats, sts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.masks = masks
        self.strings = strings
        self.start_path = start_path
        self.arhiv = arhiv
        self.cur_path = getcwd()
        self.st = sts
        self.stats = stats

    def run(self):
        file = py7zr.SevenZipFile(f'{self.start_path}/{self.arhiv}')
        print(f'Take file: {self.start_path}/{self.arhiv}')
        file.extractall(f'{self.start_path}/temp/{splitext(self.arhiv)[0]}')
        print(f'Extract to {self.start_path}/temp/{splitext(self.arhiv)[0]}')
        ind = len(self.start_path.split('/'))
        for folder, dirs, files in walk(f'{self.start_path}/temp/{splitext(self.arhiv)[0]}'):
            print(folder, dirs, files)
            for mask in self.masks:
                for name in [x for x in files if fnmatch(x, mask)]:
                    with open(f'{folder}/{name}', mode='r', encoding='utf8') as source:
                        data = source.read()
                        for string in self.strings:
                            count_string = data.count(string)
                            if count_string:
                                place = '/'.join(folder.split('/')[ind+2:])
                                makedirs(f'{self.start_path}/{string}/{splitext(self.arhiv)[0]}/{place}/', exist_ok=True)
                                shutil.copy(f'{folder}/{name}', f'{self.start_path}/{string}/{splitext(self.arhiv)[0]}/{place}')
                                if self.st:
                                    with open(f'{self.start_path}/{string}/text.txt', mode='a', encoding='utf8') as out:
                                        out.write(
                                            f'{self.arhiv}   -   {place}/{name}    - {string} - {count_string} совпадения\n')
                                    print(f'Write to file {self.start_path}/{string}/text.txt')


class RarExtract(Process):
    def __init__(self, arhiv, masks, strings, start_path, stats, sts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.masks = masks
        self.strings = strings
        self.start_path = start_path
        self.arhiv = arhiv
        self.st = sts
        self.static = stats

    def run(self):
        rarfile.UNRAR_TOOL = 'UnRAR.exe'
        print(f'Take file: {self.start_path}/{self.arhiv}')
        file = rarfile.RarFile(join(self.start_path, self.arhiv))
        print(f'Take file: {self.start_path}/{self.arhiv}')
        file.extractall(f'{self.start_path}/temp/{splitext(self.arhiv)[0]}')
        print(f'Extract to {self.start_path}/temp/{splitext(self.arhiv)[0]}')
        ind = len(self.start_path.split('/'))
        for folder, dirs, files in walk(f'{self.start_path}/temp/{splitext(self.arhiv)[0]}'):
            print(folder, dirs, files)
            for mask in self.masks:
                for name in [x for x in files if fnmatch(x, mask)]:
                    with open(f'{folder}/{name}', mode='r', encoding='utf8') as source:
                        data = source.read()
                        for string in self.strings:
                            count_string = data.count(string)
                            if count_string:
                                place = '/'.join(folder.split('/')[ind + 2:])
                                makedirs(f'{self.start_path}/{string}/{splitext(self.arhiv)[0]}/{place}/',
                                         exist_ok=True)
                                shutil.copy(f'{folder}/{name}',
                                            f'{self.start_path}/{string}/{splitext(self.arhiv)[0]}/{place}')
                                if self.st:
                                    with open(f'{self.start_path}/{string}/text.txt', mode='a', encoding='utf8') as out:
                                        out.write(
                                            f'{self.arhiv}   -   {place}/{name}    - {string} - {count_string} совпадения\n')
                                    print(f'Write to file {self.start_path}/{string}/text.txt')


class Inspector(Process):
    def __init__(self, string_file, mask_file, start_path, stat, stat_st, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.string_file = string_file
        self.mask_file = mask_file
        self.start_path = start_path
        self.masks = []
        self.strings = []
        self.stat = stat
        self.st = stat_st

    def run(self):
        self.prepare()

        # works = [RarExtract(archiv, self.masks, self.strings, self.start_path, stats=self.stat, sts=self.st)
        #          for archiv in listdir(self.start_path) if archiv.endswith('.rar')]
        # works = [ZipExtract(archiv, self.masks, self.strings, self.start_path, stats=self.stat, sts=self.st)
        #          for archiv in listdir(self.start_path) if archiv.endswith('.zip')]
        # z7_list = [Extract7z(archiv, self.masks, self.strings, self.start_path, stats=self.stat, sts=self.st)
        #            for archiv in listdir(self.start_path) if archiv.endswith('.7z')]
        # if z7_list:
        #     works.extend(z7_list)
        works = [Extract7z(archiv, self.masks, self.strings, self.start_path, stats=self.stat, sts=self.st)
                 for archiv in listdir(self.start_path) if archiv.endswith('.7z')]
        works.extend([ZipExtract(archiv, self.masks, self.strings, self.start_path, stats=self.stat, sts=self.st)
                      for archiv in listdir(self.start_path) if archiv.endswith('.zip')])
        works.extend([RarExtract(archiv, self.masks, self.strings, self.start_path, stats=self.stat, sts=self.st)
                      for archiv in listdir(self.start_path) if archiv.endswith('.rar')])
        print(works)
        for work in works:
            work.start()
        for work in works:
            work.join()
        # for arhiv in listdir(self.start_path):
        #     if arhiv.endswith('.zip'):
        #         second = ZipExtract(arhiv, self.masks, self.strings, self.start_path, stats=self.stat, sts=self.st)
        #         second.start()
        #         second.join()
        # elif arhiv.endswith('.7z'):
        #     third = Extract7z(arhiv, self.masks, self.strings, self.start_path, sts=self.st)
        #     third.start()
        #     third.join()
        # elif arhiv.endswith('.rar'):
        #     first = RarExtract(arhiv, self.masks, self.strings, self.start_path, sts=self.st)
        #     first.run()

    def prepare(self):
        with open(self.mask_file, mode='r', encoding='utf8') as mask:
            for line in mask:
                line = '*' + line.strip()
                self.masks.append(line)

        with open(self.string_file, mode='r', encoding='utf8') as string:
            for line in string:
                line = line.strip()
                self.strings.append(line)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
