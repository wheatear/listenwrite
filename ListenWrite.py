
import win32api, win32gui
ct = win32api.GetConsoleTitle()
hd = win32gui.FindWindow(0,ct)
win32gui.ShowWindow(hd,0)

# import ctypes
# whnd = ctypes.windll.kernel32.GetConsoleWindow()
# if whnd != 0:
#     ctypes.windll.user32.ShowWindow(whnd, 0)
#     ctypes.windll.kernel32.CloseHandle(whnd)

from aip import AipSpeech
import mp3play, time
import os
import sqlite3
from tkinter import *
import tkinter.messagebox
import tkinter.font
import tkinter.ttk
import pypinyin
import threading
import wx
import listenwritewin


class ListenWord(object):
    def __init__(self, word, aipClient):
        self.word = word
        self.pinyin = None
        self.wordNum = 0
        self.aipClient = aipClient
        self.person = aipClient.voiceCfg['per']
        self.spd = aipClient.voiceCfg['spd']
        # self.sleepSeconds = len(word) / 3 * 2
        self.sleepSeconds = len(word)
        # self.wordKey = word.decode('utf-8').encode('unicode_escape').replace('\\u','')
        self.wordKey = word.encode('unicode_escape').replace(b'\\u',b'').decode()
        self.makePinyin()

    def prepareVoice(self):
        self.voiceFile = 'voice/%s_%d_%d.mp3' % (self.wordKey, self.person, self.spd)
        if os.path.isfile(self.voiceFile):
            return
        voice = self.aipClient.getVoice(self.word)
        if voice is None:
            print(('can not make voice of "%s"' % self.word))
            self.voiceFile = None
            return
        with open(self.voiceFile, 'wb') as f:
            f.write(voice)
        f.close()

    def makePinyin(self):
        # uword = self.word.decode('utf-8')
        uword = self.word
        self.pinyin = pypinyin.pinyin(uword)
        self.wordNum = len(self.pinyin)
        self.sleepSeconds = self.wordNum * 2


class ListenGroup(object):
    def __init__(self):
        self.listListenWords = []
        self.size = len(self.listListenWords)

    def appendWord(self, listenWord):
        listenWord.prepareVoice()
        self.listListenWords.append(listenWord)
        self.size = len(self.listListenWords)


class Builder(object):
    def __init__(self, wordFile, aipClient):
        self.file = wordFile
        self.aipClient = aipClient
        self.person = aipClient.voiceCfg['per']
        self.lisnGroup = ListenGroup()

    def makeGroup(self):
        self.lisnGroup.listListenWords = []
        self.openFile()
        for line in self.fp:
            line = line.strip()
            if len(line) == 0: continue
            if line[0] == '#': continue
            lWords = line.split(' ')
            for word in lWords:
                lsnWord = ListenWord(word, self.aipClient)
                self.lisnGroup.appendWord(lsnWord)
        self.fp.close()
        return self.lisnGroup

    def openFile(self):
        try:
            self.fp = open(self.file, 'r')
        except IOError as e:
            print(('Can not open file %s: %s' % (self.file, e)))
            exit()
        return self.fp



class Player(object):
    def __init__(self, app):
        self.app = app
        self.begionFile = 'voice/begion.mp3'
        self.begionWord = '开始听写'
        self.endFile = 'voice/end.mp3'
        self.endword = '听写完毕'
        self.voiceCfg = {}
        self.voiceCfg['spd'] = 5  # 语速，取值0-9，默认为5中语速
        self.voiceCfg['pit'] = 5  # 音调，取值0-9，默认为5中语调
        self.voiceCfg['vol'] = 12  # 音量，取值0-15，默认为5中音量
        self.voiceCfg['per'] = 3  # 发音人选择, 0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女
        self.nextOne = 0
        self.isContinue = 0

    def setWordGrp(self, listWords):
        self.grpWords = listWords

    def playGroup(self, aipClient):
        self.preparePlay(aipClient, self.begionWord, self.begionFile)
        self.preparePlay(aipClient, self.endword, self.endFile)
        self.playOne(self.begionFile,1)

        for i in range(self.grpWords.size):
            listenWord = self.grpWords.listListenWords[i]
            wordPinyin = listenWord.pinyin
            # textPinyin = []
            # for i in range(len(wordPinyin)):
            #     textPinyin[i] = wordPinyin[i].encode('utf-8')
            self.app.displayPinyin(wordPinyin)
            clip = None
            for k in range(2):
                clip = self.playOne(listenWord.voiceFile, listenWord.sleepSeconds, clip)
                for slp in range(listenWord.sleepSeconds):
                    if self.app.nextOne == 1:
                        # print{'next one'}
                        self.app.nextOne = 0
                        self.isContinue = 1
                        break
                    time.sleep(1)
                if self.isContinue == 1:
                    break
            if self.isContinue == 1:
                self.isContinue = 0
                continue
            # self.playOne(listenWord.voiceFile, listenWord.sleepSeconds, clip)
        self.playOne(self.endFile, 1)

    def preparePlay(self, aipClient, tex, voiceFile):
        if os.path.isfile(voiceFile):
            return voiceFile
        voice = aipClient.getVoice(tex, self.voiceCfg)
        if voice is None:
            print(('can not make voice of "%s"' % tex))
            return None
        with open(voiceFile, 'wb') as f:
            f.write(voice)
        f.close()

    def playOne(self, voiceFile, addSeconds, clip=None):
        if clip is None:
            clip = mp3play.load(voiceFile)
        clipSeconds = clip.seconds() + 1
        sleepSeconds = addSeconds + clipSeconds

        clip.volume(90)
        clip.play()
        # time.sleep(clip.seconds())
        time.sleep(clipSeconds)
        clip.stop()
        return clip


class AipClient(object):
    def __init__(self,appId,apiKey,secretKey):
        self.appId = appId
        self.apiKey = apiKey
        self.secretKey = secretKey
        self.lang = 'zh' #语言选择,填写zh
        self.ctp = 1 #客户端类型选择，web端填写1
        self.voiceCfg = {}
        self.client = AipSpeech(appId, apiKey, secretKey)
        self.setVoiceCfg()

    def setVoiceCfg(self, voiceSet=None):
        if voiceSet == None:
            self.voiceCfg['spd'] = 2 # 语速，取值0-9，默认为5中语速
            self.voiceCfg['pit'] = 5 # 音调，取值0-9，默认为5中语调
            self.voiceCfg['vol'] = 12 # 音量，取值0-15，默认为5中音量
            self.voiceCfg['per'] = 0 # 发音人选择, 0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女
        else:
            self.voiceCfg = voiceSet

    def getVoice(self, tex, voiceCfg=None):
        if voiceCfg == None:
            voiceCfg = self.voiceCfg
        voice = self.client.synthesis(tex, self.lang, self.ctp, voiceCfg)
        if not isinstance(voice, dict):
            return voice
        else:
            print(('make voice error:%s' % voice['err_msg']))
            return None


class ListenWrite(threading.Thread):
    APP_ID = '10568246'
    API_KEY = '6cFFqOMdPr3EIYx4uEpYsD4s'
    SECRET_KEY = '6e2c9e550e3358d1e6fd85030115ae36'

    def __init__(self, app):
        threading.Thread.__init__( self)
        self.app = app
        self.client = AipClient(ListenWrite.APP_ID, ListenWrite.API_KEY, ListenWrite.SECRET_KEY)
        self.voiceCfg = {'vol': 8, 'spd': 0, }
        self.inFile = 'listenwords.txt'
        self.client.setVoiceCfg()
        self.builder = Builder(self.inFile, self.client)
        self.player = Player(app)

    def loadWords(self):
        self.listenGroup = self.builder.makeGroup()
        self.player.setWordGrp(self.listenGroup)

    # def start(self):
    #     self.player.playGroup(self.client)
    def run(self):
        self.player.playGroup(self.client)


class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        self.columnNum = 6
        self.wordCount = 0
        self.columnCount = 0
        self.rowCount = 0
        # self.listenGroup = []
        self.ft30 = tkinter.font.Font(size=30)
        self.ft25 = tkinter.font.Font(size=25)
        self.nextOne = 0
        self.loaded = 0

    def createWidgets(self):

        # self.helpbutton.pack(side='right')
        # self.nameInput = Entry(self)
        # self.nameInput.pack()
        ft30 = tkinter.font.Font(size=30)
        self.loadButton = Button(self, text='加载词语', command=self.load)
        self.loadButton.grid(row=10,column=0,padx=3,sticky=W)
        self.startButton = Button(self, text='开始听写', command=self.start)
        self.startButton.grid(row=10,column=1,sticky=W)
        self.startButton = Button(self, text='下一个', command=self.nextWord)
        self.startButton.grid(row=10, column=2)
        self.helpbutton = Button(self, text='帮助', command=self.help)
        self.helpbutton.grid(row=10, column=5, sticky=E, padx=3)
        self.pinyinLable = Label(self,text='拼音', font=ft30)
        self.pinyinLable.grid(row=9,column=1, columnspan=2, sticky=E+W)
        self.pinyinLable['font'] = ft30
        self.wordLable = Label(self, text='词语', font=ft30)
        self.wordLable.grid(row=9,column=4, columnspan=2, sticky=E+W)

        self.scrollBar = Scrollbar(self)
        self.scrollBar.grid(row=1,sticky=E)
        self.tree = tkinter.ttk.Treeview(self,
                                 columns=('c1', 'c2', 'c3', 'c4', 'c5', 'c6'),
                                 yscrollcommand=self.scrollBar.set,show='headings')
        self.tree.column('c1', width=150, anchor='center')
        self.tree.column('c2', width=150, anchor='center')
        self.tree.column('c3', width=150, anchor='center')
        self.tree.column('c4', width=150, anchor='center')
        self.tree.column('c5', width=150, anchor='center')
        self.tree.column('c6', width=150, anchor='center')

        self.tree.grid(row=1,columnspan=5)
        self.scrollBar.config(command=self.tree.yview)

        self.tree.bind("<Button-1>", self.markError)

    def markError(self,event):

        word = self.tree.identify_element(event.x,event.y)
        word = '%s %s %s' % (self.tree.identify_row(event.y), self.tree.identify_column(event.x), word)
        self.pinyinLable['text'] = word

    def load(self):
        self.listenWriter = ListenWrite(self)
        self.listenWriter.setDaemon(True)
        self.listenWriter.loadWords()
        self.loaded = 1

        # wordNum = self.listenWriter.listenGroup.size
        # j = 0
        # wordRow = []
        # for i in range(wordNum):
        #     if i >= wordNum: break
        #     j += 1
        #     if j == 7:
        #         # self.tree.insert('','end',values=['test'] * 6)
        #         witem = self.tree.insert('', 'end', values=wordRow)
        #         # print(witem.tags)
        #         wordRow = []
        #         j = 0
        #     wordRow.append(self.listenWriter.listenGroup.listListenWords[i].pinyin)
        # if len(wordRow) > 0:
        #     self.tree.insert('', 'end', values=wordRow)
        # print('font: %s' % self.tree['font'])

    def displayPinyin(self, pinyin):
        str = ''
        num = len(pinyin)
        for i in range(num):
            py = pinyin[i][0].encode('utf-8')
            str = '%s %s' % (str,py)
        # print(str)
        self.pinyinLable['text'] = str
        # ft = tkFont.Font(size=30)
        # self.pinyinLable['font'] = ft
        # print('font: %s' % self.pinyinLable['font'])
        self.wordCount += 1
        self.columnCount += 1
        if self.columnCount >= self.columnNum:
            self.columnCount = 0
            self.rowCount += 1
            self.currentItem = self.tree.insert('', 'end')
        self.tree.set(self.currentItem, self.columnCount, value=str)
        # self.master.update_idletasks()

    def start(self):
        # name = self.nameInput.get() or 'world'
        # tkMessageBox.showinfo('Message', 'Hello, %s' % name)
        if self.loaded == 0:
            self.load()
        self.wordCount = 0
        self.columnCount = -1
        self.currentItem = self.tree.insert('', 'end')
        # self.listenWords()
        self.listenWriter.start()

    def listenWords(self):
        self.listenGroup = self.listenWriter.listenGroup
        self.client = self.listenWriter.client
        player = self.listenWriter.player

        player.preparePlay(self.client, player.begionWord, player.begionFile)
        player.preparePlay(self.client, player.endword, player.endFile)
        player.playOne(player.begionFile, 1)

        for i in range(self.listenGroup.size):
            listenWord = self.listenGroup.listListenWords[i]
            wordPinyin = listenWord.pinyin
            # textPinyin = []
            # for i in range(len(wordPinyin)):
            #     textPinyin[i] = wordPinyin[i].encode('utf-8')
            self.displayPinyin(wordPinyin)

            clip = player.playOne(listenWord.voiceFile, listenWord.sleepSeconds)
            if self.nextOne == 1:
                continue
            player.playOne(listenWord.voiceFile, listenWord.sleepSeconds, clip)
        player.playOne(player.endFile, 1)

    def nextWord(self):
        # self.listenWriter.player.nextOne = 1
        self.nextOne = 1

    def help(self):
        msg = '''生词听写工具使用方法：
1.把要听写的词语写入文件listenwords.txt中，词语之间用空格隔开。
2.行首是#的为注释行，不听写。
3.程序运行时，会把listenwords.txt文件中所有非#开头的行，读入内存。按空格分隔拆出各个词语，通过语音合成得到读音，依次播放，每个词播放两遍。
4.当加入新的词语时，需要联网得到读音，请保证网络畅通。

                                                                 作者：王新田
                                                                   13520498010'''
        tkinter.messagebox.showinfo('Help', msg)

class LisWriFram(listenwritewin.MyFrame1):
    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)
        self.wordCount = 0

    def loadWords(self, event):
        self.listenWriter = ListenWrite(self)
        self.listenWriter.setDaemon(True)
        self.listenWriter.loadWords()
        self.loaded = 1

    def start(self, event):
        # name = self.nameInput.get() or 'world'
        # tkMessageBox.showinfo('Message', 'Hello, %s' % name)
        if self.loaded == 0:
            self.load()
        self.wordCount = 0
        # self.columnCount = -1
        # self.currentItem = self.tree.insert('', 'end')
        # self.listenWords()
        self.listenWriter.start()

    def nextWord(self, event):
        # self.listenWriter.player.nextOne = 1
        self.nextOne = 1

    def displayPinyin(self, pinyin):
        str = ''
        num = len(pinyin)
        for i in range(num):
            py = pinyin[i][0].encode('utf-8')
            str = '%s %s' % (str,py)
        # print(str)
        self.m_staticText8.label = str
        # self.pinyinLable['text'] = str
        # ft = tkFont.Font(size=30)
        # self.pinyinLable['font'] = ft
        # print('font: %s' % self.pinyinLable['font'])

        self.wordCount += 1
        row = self.wordCount // 6
        col = self.wordCount % 6
        self.m_grid2.SetCellValue(row, col, str)
        # self.columnCount += 1
        # if self.columnCount >= self.columnNum:
        #     self.columnCount = 0
        #     self.rowCount += 1
        #     self.currentItem = self.tree.insert('', 'end')
        # self.tree.set(self.currentItem, self.columnCount, value=str)


# start
if __name__ == '__main__':
    # main = ListenWrite()
    # main.loadWords()
    # main.start()

    # # tkinter
    # app = Application()
    # # 设置窗口标题:
    # app.master.title('词语听写工具')
    # # 主消息循环:
    # app.mainloop()
    # # app.load()

    # wx
    app = wx.App(False)
    frame = LisWriFram(None)
    frame.Show(True)
    app.MainLoop()

    # top = Tk()
    # label = Label(top,text='lister write')
    # label.pack()
    #
    #
    # main = ListenWrite()
    # btStart = Button(top, text='开始', command=main.start)
    # btStart.pack()
    # mainloop()


