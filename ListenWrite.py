
# import win32api, win32gui
# ct = win32api.GetConsoleTitle()
# hd = win32gui.FindWindow(0,ct)
# win32gui.ShowWindow(hd,0)

# import ctypes
# whnd = ctypes.windll.kernel32.GetConsoleWindow()
# if whnd != 0:
#     ctypes.windll.user32.ShowWindow(whnd, 0)
#     ctypes.windll.kernel32.CloseHandle(whnd)

from aip import AipSpeech
import mp3play, time
import datetime
import os
import re
import sqlite3
# from tkinter import *
# import tkinter.messagebox
# import tkinter.font
# import tkinter.ttk
import pypinyin
import threading
import wx
import listenwritewin


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


class ListenWord(object):
    def __init__(self, word, voiceSet, aipClient):
        self.word = word
        self.voiceSet = voiceSet
        self.pinyin = None
        self.wordNum = len(word)
        self.voiceFile = None
        self.aipClient = aipClient
        # self.sleepSeconds = len(word) / 3 * 2
        self.sleepSeconds = len(word) * 2
        self.testResult = 0
        # self.wordKey = word.decode('utf-8').encode('unicode_escape').replace('\\u','')
        self.wordKey = word.encode('unicode_escape').replace(b'\\u',b'').decode()
        self.makePinyin()

    def prepareVoice(self):
        self.voiceFile = 'voice/%s_%d%d%d%d.mp3' % (self.wordKey, self.voiceSet['per'], self.voiceSet['pit'], self.voiceSet['spd'], self.voiceSet['vol'])
        if os.path.isfile(self.voiceFile):
            return self.voiceFile
        voice = self.aipClient.getVoice(self.word, self.voiceSet)
        if voice is None:
            print(('can not make voice of "%s"' % self.word))
            self.voiceFile = None
            return None
        with open(self.voiceFile, 'wb') as f:
            f.write(voice)
        f.close()
        return self.voiceFile

    def makePinyin(self):
        # uword = self.word.decode('utf-8')
        uword = self.word
        self.pinyin = pypinyin.pinyin(uword)
        self.wordNum = len(self.pinyin)
        self.sleepSeconds = self.wordNum * 2


class Player(object):
    def __init__(self, app):
        # threading.Thread.__init__(self)
        self.app = app
        self.volume = 90
        self.nextOne = 0
        self.pause = 0
        self.playStart = 0
        self.repeatNum = 1
        self.playing = 0

    def playAll(self):
        self.playStart = 0
        self.pause = 0
        self.playing = 0
        self.repeatNum = 1
        self.playOne(self.app.listenWriter.builder.prdGroup[0])
        if self.playGroup():
            self.playOne(self.app.listenWriter.builder.prdGroup[1])
            return True
        return False

    def playContinue(self):
        self.pause = 0
        if self.playGroup():
            self.playOne(self.app.listenWriter.builder.prdGroup[1])
            return True
        return False

    def playGroup(self):
        if self.playing == 1:
            return
        self.playing = 1
        startNum = self.playStart
        listenGrp = self.app.listenWriter.wordsGroup
        aPlayNums = range(len(listenGrp))[startNum:]
        for i in aPlayNums:
            listenWord = listenGrp[i]
            if self.repeatNum > 0:
                wordPinyin = listenWord.pinyin
                # wx.CallAfter(self.app.displayPinyin,wordPinyin)
                self.app.displayPinyin(wordPinyin)
            else:
                self.repeatNum = 1
            clip = None
            for k in range(2):
                clip = self.playOne(listenWord, clip)
                for slp in range(listenWord.sleepSeconds):
                    if self.nextOne == 1 or self.pause == 1:
                        break
                    time.sleep(1)
                if self.nextOne == 1 or self.pause == 1:
                    break
            # print('repeat num: %d' % k)
            if self.nextOne == 1:
                self.nextOne = 0
                continue
            if  self.pause == 1:
                if k == 1:
                    self.playStart = i + 1
                else:
                    self.playStart = i
                self.repeatNum = k
                self.playing = 0
                return False
        self.playing  = 0
        return True

    def playOne(self, listenWord, clip=None):
        if clip is None:
            clip = mp3play.load(listenWord.voiceFile)
        clipSeconds = clip.seconds() + 1
        # sleepSeconds = listenWord.addSeconds + clipSeconds

        clip.volume(self.volume)
        clip.play()
        # time.sleep(clip.seconds())
        time.sleep(clipSeconds)
        clip.stop()
        return clip


class Builder(object):
    def __init__(self, lstwrt):
        self.listenWriter = lstwrt
        self.dataSource = lstwrt.dataSource
        self.aipClient = lstwrt.client
        # self.person = aipClient.voiceCfg['per']
        self.lisnGroup = []
        self.prdGroup = []

    def loadWordes(self):
        self.loadPrdWordes()
        self.openDs()
        for line in self.fp:
            line = line.strip()
            if len(line) == 0: continue
            if line[0] == '#': continue
            lWords = line.split()
            for word in lWords:
                lsnWord = ListenWord(word, self.listenWriter.listenSet, self.aipClient)
                self.lisnGroup.append(lsnWord)
        self.fp.close()
        return self.lisnGroup

    def loadPrdWordes(self):
        for word in self.listenWriter.presenteWords:
            prdWord = ListenWord(word, self.listenWriter.presenterSet, self.aipClient)
            self.prdGroup.append(prdWord)
        return self.prdGroup

    def openDs(self):
        try:
            self.fp = open(self.dataSource, 'r')
        except IOError as e:
            print(('Can not open file %s: %s' % (self.dataSource, e)))
            exit()
        return self.fp

    def makeAllVoice(self):
        self.makeVoice(self.prdGroup)
        self.makeVoice(self.lisnGroup)

    def makeVoice(self, wordGrp):
        for word in wordGrp:
            voicefile = word.prepareVoice()
            if not voicefile:
                print('cant make voice for %s' % word.word)


class DbBuilder(Builder):
    dSql = {}
    dSql['SearchPress'] = 'select pressid from lw_press where pname = ?'
    dSql['InsertPress'] = 'insert into ls_press(pname) values(?)'
    dSql['SearchBook'] = 'select bookid from lw_book where pressid=? and bookname=? and grade=?'
    dSql['InsertBook'] = 'insert into lw_book(pressid,bookname,grade) values(?,?,?)'
    dSql['SearchUnit'] = 'select unitid from lw_unit where bookid=? and unitname=?'
    dSql['InsertUnit'] = 'insert into lw_unit(bookid,unitname) values(?,?)'
    dSql['SearchLesson'] = 'select lessonid from lw_lesson where unitid=? and lessoncode=? and lessonname=?'
    dSql['InsertLesson'] = 'insert into lw_lesson(unitid,lessoncode,lessonname) values(?,?,?)'
    dSql['SearchWord'] = 'select word from lw_word where lessonid=? and word=?'
    dSql['InsertWord'] = 'insert into lw_word(lessonid,word) values(?,?)'

    dSql['SearchSelected'] = 'select choicename,choicevalue from lw_choiceselected'
    dSql['SaveSelected'] = "update lw_choiceselected set choicevalue=? where choicename=?"

    dSql['ChoicePress'] = 'select pressid,pname from lw_press'
    dSql['ChoiceBook'] = 'select bookid,bookname,grade from lw_book where pressid=?'
    dSql['ChoiceUnit'] = 'select unitid,unitname from lw_unit where bookid=?'
    dSql['ChoiceLesson'] = 'select lessonid,lessoncode,lessonname from lw_lesson where unitid=?'
    dSql['ChoiceTest'] = "select testname,strftime('%Y%m%d%H%M%S',testtime),testid,pressid,bookid,unitid,lessonid from lw_test where "
    dSql['TestWords'] = "select distinct word from lw_testwords where result=1 and"
    # testid in (?) and

    dSql['SearchTest'] = 'select testid from lw_test where testtime=? and testname=? and type=? and pressid=?'
    # and bookid =? and unitid =? and lessonid =?
    dSql['InsertTest'] = "insert into lw_test(testtime,testname,type,pressid,bookid,unitid,lessonid) values(?,?,?,?,?,?,?)"
    dSql['SearchTestWord'] = "select result from lw_testwords where testid=? and word=?"
    dSql['InsertTestWord'] = "insert into lw_testwords(result,testid,word) values(?,?,?)"
    dSql['UpdateTestWord'] = "update lw_testwords set result=? where testid=? and word=?"
    dSql['TestWord'] = "select word from lw_testwords where testid=? and result=?"

    dSql['LessonWords'] = 'select word from lw_word where lessonId=?'

    def __init__(self, lstwrt):
        super(self.__class__, self).__init__(lstwrt)
        self.db = DbConn(self.dataSource)
        self.conn = None
        self.openDs()

    def openDs(self):
        try:
            self.conn = self.db.connectServer()
        except Exception as e:
            print(('Can not open sqlite %s: %s' % (self.dataSource, e)))
            exit()
        return self.conn

    def importWords(self, file):
        self.openDs()
        fp = self.openFile(file)
        pressId = None
        bookId = None
        unitId = None
        lessonId = None
        p = re.compile(r'^#+')
        for line in fp:
            line = line.strip()
            if len(line) == 0: continue
            if line[0] == '#':
                line = p.sub('', line)
                aItem = line.split()
                if len(aItem) < 2:
                    continue
                section = aItem[0].upper()
                if section == 'PRESS':
                    pressId = self.importPress(aItem)
                elif  section == 'BOOK':
                    bookId = self.importBook(aItem, pressId)
                elif section == 'UNIT':
                    unitId = self.importUnit(aItem, bookId)
                elif  section == 'LESSON':
                    lessonId = self.importLesson(aItem, unitId)
            else:
                self.importWord(line, lessonId)
        fp.close()

    def insertResult(self, testId, word, result):
        sqlSearch = self.dSql['SearchTestWord']
        sqlSave = self.dSql['InsertTestWord']
        curSearch = self.db.prepareSql(sqlSearch)
        self.db.executeCur(curSearch, sqlSearch, (testId, word))
        row = self.db.fetchone(curSearch)
        if row:
            if row[0] == result:
                return
            else:
                sqlSave = self.dSql['UpdateTestWord']

        curSave = self.db.prepareSql(sqlSave)
        self.db.executeCur(curSave, sqlSave, (result, testId, word ))
        curSave.connection.commit()

    def addTest(self, dChoice, wordType):
        # dTest = {}
        testTime = datetime.datetime.now()
        testName = 'test'
        pressId = None
        bookId = None
        unitId = None
        lessonId = None
        if dChoice['ChoiceSelected']['book']:
            bookName = dChoice['ChoiceSelected']['book']
            testName = bookName
            bookId = dChoice['ChoiceBook'][bookName]
            if dChoice['ChoiceSelected']['lesson']:
                lessonName = dChoice['ChoiceSelected']['lesson']
                testName = '%s %s' % (testName,lessonName)
                lessonId = dChoice['ChoiceLesson'][lessonName]
            if dChoice['ChoiceSelected']['unit']:
                unitName = dChoice['ChoiceSelected']['unit']
                unitId = dChoice['ChoiceUnit'][unitName]
                testName = '%s %s' % (testName, unitName)
        if dChoice['ChoiceSelected']['press']:
            pressName = dChoice['ChoiceSelected']['press']
            pressId = dChoice['ChoicePress'][pressName]
        aParam = (testTime, testName, wordType, pressId, bookId, unitId, lessonId)
        sqlInsert = self.dSql['InsertTest']
        # self.openDs()

        # wx.MessageBox('add test sql: %s  param: %s' % (sqlInsert,aParam))
        curInsert = self.db.prepareSql(sqlInsert)
        self.db.executeCur(curInsert, sqlInsert, aParam)
        curInsert.connection.commit()

        sqlSearch = self.dSql['SearchTest']
        # and bookid =? and unitid =? and lessonid =?
        if aParam[4]:
            sqlSearch = '%s and bookid=?' % sqlSearch
        else:
            sqlSearch = '%s and bookid is null'  % sqlSearch
        if aParam[5]:
            sqlSearch = '%s and unitid=?' % sqlSearch
        else:
            sqlSearch = '%s and unitid is null' % sqlSearch
        if aParam[6]:
            sqlSearch = '%s and lessonid=?' % sqlSearch
        else:
            sqlSearch = '%s and lessonid is null' % sqlSearch
        lParam = list(aParam)
        for i,pa in enumerate(lParam):
            if not pa:
                lParam.pop(i)
        tParam = tuple(lParam)
        curSearchTest = self.db.prepareSql(sqlSearch)
        # wx.MessageBox('search test sql: %s  param: %s' % (sqlSearch, tParam))
        self.db.executeCur(curSearchTest, sqlSearch, tParam)
        row = self.db.fetchone(curSearchTest)
        if row:
            # dTest[row[0]] = aParam
            [row[0]].extend(tParam)
            return row
        else:
            return None

    def importPress(self, aInfo):
        # pressName = ' '.join(aInfo[1:])
        pressName = aInfo[1]
        dPress = {'PNAME': pressName}
        aPress = (pressName, )
        searchKey = 'SearchPress'
        insertKey = 'InsertPress'
        return self.importCommon(searchKey, insertKey, aPress)

    def importBook(self, aInfo, parentId):
        bookName = aInfo[1]
        grade = None
        if len(aInfo) > 2:
            grade = aInfo[2]
        dict = {}
        dict['BOOKNAME'] = bookName
        dict['GRADE'] = grade
        dict['PRESSID'] = parentId
        aBook = (parentId, bookName, grade)
        searchKey = 'SearchBook'
        insertKey = 'InsertBook'
        return self.importCommon(searchKey, insertKey, aBook)

    def importUnit(self, aInfo, parentId):
        unitName = aInfo[1]
        dict = {}
        dict['UNITNAME'] = unitName
        dict['BOOKID'] = parentId
        aUnit = (parentId, unitName)
        searchKey = 'SearchUnit'
        insertKey = 'InsertUnit'
        return self.importCommon(searchKey, insertKey, aUnit)

    def importLesson(self, aInfo, parentId):
        lessonCode = aInfo[1]
        lessonName = None
        if len(aInfo) > 2:
            lessonName = aInfo[2]
        dict = {}
        dict['LESSONCODE'] = lessonCode
        dict['LESSONNAME'] = lessonName
        dict['UNITID'] = parentId
        aLesson = (parentId, lessonCode, lessonName)
        searchKey = 'SearchLesson'
        insertKey = 'InsertLesson'
        return self.importCommon(searchKey, insertKey, aLesson)

    def importWord(self, line, parentId):
        searchKey = 'SearchWord'
        insertKey = 'InsertWord'
        aInfo = line.split()
        for word in aInfo:
            # dict = {}
            # dict['WORD'] = word
            # dict['LESSONID'] = parentId
            aWord = (parentId, word)
            self.importCommon(searchKey, insertKey, aWord)
        return

    def importCommon(self, searchKey, insertKey, dicVal):
        sqlSearch = self.dSql[searchKey]
        curSearch = self.db.prepareSql(sqlSearch)
        self.db.executeCur(curSearch, sqlSearch, dicVal)
        row = self.db.fetchone(curSearch)
        if row:
            return row[0]
        sqlInsert = self.dSql[insertKey]
        curInsert = self.db.prepareSql(sqlInsert)
        self.db.executeCur(curInsert, sqlInsert, dicVal)
        curInsert.connection.commit()

        self.db.executeCur(curSearch, sqlSearch, dicVal)
        row = self.db.fetchone(curSearch)
        if row:
            return row[0]
        else:
            return None

    def openFile(self, file):
        try:
            fp = open(file, 'r')
        except IOError as e:
            print(('Can not open file %s: %s' % (file, e)))
            exit()
        return fp

    def loadTestWords(self, aTestId):
        self.prdGroup = []
        self.loadPrdWordes()
        self.lisnGroup = []
        sql = self.dSql['TestWords']
        sTestIds = ','.join(aTestId)
        sql = '%s testid in (%s)' % (sql, sTestIds)
        # wx.MessageBox("loadTestWords: %s  %s\n" % (sql, sTestIds))
        cur = self.db.executeSql(sql)
        rows = self.db.fetchall(cur)
        cur.close()
        # wx.MessageBox("loadTestWords: %s\n" % rows)
        aWords = []
        for row in rows:
            word = row[0]
            # aWords.append(word)
            lsnWord = ListenWord(word, self.listenWriter.listenSet, self.aipClient)
            self.lisnGroup.append(lsnWord)
        return self.lisnGroup

    def saveSelected(self, dSelected):
        sql = self.dSql['SaveSelected']

        aPara = []
        for key in dSelected:
            para = (dSelected[key], key)
            aPara.append(para)
        cur = self.db.executeManySql(sql, aPara)
        cur.connection.commit()
        cur.close

    def loadSelected(self):
        dSelected = {}
        sql = self.dSql['SearchSelected']
        cur = self.db.executeSql(sql)
        rows = self.db.fetchall(cur)
        cur.close()
        for row in rows:
            dSelected[row[0]] = row[1]
        # print(dSelected)
        return dSelected

    def loadTest(self, fieldName, fieldValue):
        dict = {}
        # dict[''] = None
        sql = self.dSql['ChoiceTest']
        sqlTest = '%s%s=?' % (sql, fieldName)
        # print(sqlTest)
        # print(fieldValue)
        cur = self.db.executeSql(sqlTest, (fieldValue,))
        # cur = self.db.prepareSql(sqlTest)
        # cur = self.db.executeCur(cur, sqlTest, (fieldValue,))
        rows = self.db.fetchall(cur)
        cur.close()
        for row in rows:
            # print(row)
            key = '%s %s' % (row[0], row[1])
            dict[key] = row[2:]
        return dict

    def loadChoiceCommon(self, choiceKey, itemId):
        dict = {}
        dict[''] = None
        if not itemId and choiceKey != 'ChoicePress' :
            return dict
        # self.openDs()
        sql = self.dSql[choiceKey]
        # cur = self.db.prepareSql(sql)
        # conn = self.db.connectServer()
        cur = self.conn.cursor()
        if itemId:
            self.db.executeCur(cur, sql, (itemId,))
        else:
            self.db.executeCur(cur, sql)
        rows = self.db.fetchall(cur)
        cur.close()
        # conn.close()

        for row in rows:
            key = ' '.join(row[1:])
            dict[key] = row[0]
        return dict

    def loadLessonWords(self, lessonId):
        self.prdGroup = []
        self.loadPrdWordes()
        self.lisnGroup = []
        sql = self.dSql['LessonWords']
        # cur = self.db.prepareSql(sql)
        # conn = self.db.connectServer()
        cur = self.conn.cursor()
        self.db.executeCur(cur, sql, (lessonId,))
        rows = self.db.fetchall(cur)
        cur.close()
        # self.conn.close()
        aWords = []
        for row in rows:
            word = row[0]
            # aWords.append(word)
            lsnWord = ListenWord(word, self.listenWriter.listenSet, self.aipClient)
            self.lisnGroup.append(lsnWord)
        return self.lisnGroup


class DbConn(object):
    def __init__(self, dbInfo):
        self.dbInfo = dbInfo
        self.conn = None
        self.dCur = {}
        # self.connectServer()

    def connectServer(self):
        # if self.conn: return self.conn
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.dbInfo)
        except Exception as e:
            # logging.fatal('could not connect to oracle(%s:%s/%s), %s', self.cfg.dbinfo['dbhost'], self.cfg.dbinfo['dbusr'], self.cfg.dbinfo['dbsid'], e)
            raise Exception(e)
            # exit()
        return self.conn

    def getCursor(self):
        return self.conn.cursor()

    def prepareSql(self, sql):
        # logging.info('prepare sql: %s', sql)
        if sql in self.dCur:
            return self.dCur[sql]
        cur = self.conn.cursor()
        # try:
        #     cur.prepare(sql)
        # except sqlite3.DatabaseError as e:
        #     # logging.error('prepare sql err: %s', sql)
        #     raise sqlite3.DatabaseError(e)
        #     return None
        self.dCur[sql] = cur
        return cur

    def executemanyCur(self, cur, sql, params):
        # logging.info('execute cur %s : %s', cur.statement, params)
        try:
            cur.executemany(sql, params)
        except sqlite3.DatabaseError as e:
            # logging.error('execute sql err %s:%s ', e, cur.statement)
            raise sqlite3.DatabaseError(e)
            return None
        return cur

    def fetchmany(self, cur):
        # logging.debug('fetch %d rows from %s', cur.arraysize, cur.statement)
        try:
            rows = cur.fetchmany()
        except sqlite3.DatabaseError as e:
            # logging.error('fetch sql err %s:%s ', e, cur.statement)
            raise sqlite3.DatabaseError(e)
            return None
        return rows

    def fetchone(self, cur):
        # logging.debug('fethone from %s', cur.statement)
        try:
            row = cur.fetchone()
        except sqlite3.DatabaseError as e:
            # logging.error('execute sql err %s:%s ', e, cur.statement)
            raise sqlite3.DatabaseError(e)
            return None
        return row

    def fetchall(self, cur):
        # logging.debug('fethone from %s', cur.statement)
        try:
            rows = cur.fetchall()
        except sqlite3.DatabaseError as e:
            # logging.error('execute sql err %s:%s ', e, cur.statement)
            raise sqlite3.DatabaseError(e)
            return None
        return rows

    def executeCur(self, cur, sql, params=None):
        # logging.info('execute cur %s', cur.statement)
        # try:
        # print('sql: %s . para: %s' % (sql, params))
        if params is None:
                cur.execute(sql)
        else:
                cur.execute(sql, params)
        # except sqlite3.DatabaseError as e:
        #     # logging.error('execute sql err %s:%s ', e, cur.statement)
        #     raise sqlite3.DatabaseError(e)
        #     return None
        return cur

    def executeSql(self, sql, params=None):
        cur = self.conn.cursor()
        # wx.MessageBox("sql: %s param: %s\n" % (sql, params))
        try:
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
        except sqlite3.DatabaseError as e:
            # logging.error('execute sql err %s:%s ', e, cur.statement)
            # raise sqlite3.DatabaseError(e)
            wx.MessageBox("dberror: %s on sql: %s\n" % (e, sql))
            return None
        return cur

    def executeManySql(self, sql, aParams=None):
        cur = self.conn.cursor()
        try:
            if aParams:
                cur.executemany(sql, aParams)
            else:
                cur.execute(sql)
        except sqlite3.DatabaseError as e:
            # logging.error('execute sql err %s:%s ', e, cur.statement)
            wx.MessageBox("dberror: %s on sql: %s  param: %s\n" % (e, sql, aParams))
            # raise sqlite3.DatabaseError(e)
            return None
        return cur


class ListenWrite(object):
    APP_ID = '10568246'
    API_KEY = '6cFFqOMdPr3EIYx4uEpYsD4s'
    SECRET_KEY = '6e2c9e550e3358d1e6fd85030115ae36'

    def __init__(self, app):
        self.app = app
        self.wordsGroup = []
        self.prdGroup = []
        self.presenteWords = []
        self.client = AipClient(ListenWrite.APP_ID, ListenWrite.API_KEY, ListenWrite.SECRET_KEY)
        self.listenSet = {}
        self.presenterSet = {}
        self.vioceSet()
        # self.voiceCfg = {'vol': 8, 'spd': 0, }
        # self.dataSource = 'listenwords.txt'
        self.dataSource = 'lessonwords.db'
        # self.client.setVoiceCfg()
        self.builder = DbBuilder(self)
        self.player = Player(app)
        self.dInitSet = {}
        self.wordType = 'new'
        self.test = None

    def loadWords(self):
        # self.listenGroup = self.builder.makeGroup()
        self.presenteWords = ['开始听写', '听写完毕']
        self.wordsGroup = self.builder.loadWordes()
        t = threading.Thread(target=self.makeVoice)
        t.setDaemon(True)
        t.start()

    def vioceSet(self):
        # presenterSet
        self.presenterSet['spd'] = 5  # 语速，取值0-9，默认为5中语速
        self.presenterSet['pit'] = 5  # 音调，取值0-9，默认为5中语调
        self.presenterSet['vol'] = 12  # 音量，取值0-15，默认为5中音量
        self.presenterSet['per'] = 3  # 发音人选择, 0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女
        # listenSet
        self.listenSet['spd'] = 2  # 语速，取值0-9，默认为5中语速
        self.listenSet['pit'] = 5  # 音调，取值0-9，默认为5中语调
        self.listenSet['vol'] = 12  # 音量，取值0-15，默认为5中音量
        self.listenSet['per'] = 0  # 发音人选择, 0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女

    def makeVoice(self):
        self.builder.makeAllVoice()

    def playWordes(self):
        if self.player.playAll():
            self.app.m_button11.Enable(True)
            self.app.m_button12.Enable(True)
            self.app.m_button15.Enable(True)

    def playContinue(self):
        if self.player.playContinue():
            self.app.m_button11.Enable(True)
            self.app.m_button12.Enable(True)
            self.app.m_button15.Enable(True)

    def pause(self):
        self.player.pause = 1

    def addTest(self):
        self.test = self.builder.addTest(self.dInitSet, self.wordType)
        # wx.MessageBox('test: %s' % self.test)

    def saveTest(self, aWrongWores):
        testId = self.test[0]
        for wd in self.wordsGroup:
            word = wd.word
            result = 0
            if word in aWrongWores:
                result = 1
            self.builder.insertResult(testId, word, result)

    def importWords(self, file):
        self.builder.importWords(file)
        self.app.m_button11.Enable(False)

    def loadInit(self):
        dInitSet = {}
        dChoiceSelected = self.builder.loadSelected()
        # dChoiceSelected = {'press':'人民教育出版社'}
        # dChoiceSelected['book'] = '语文 四年级下'
        # dChoiceSelected['unit'] = '五单元'
        # dChoiceSelected['lesson'] = '19 花的勇气'
        dInitSet['ChoiceSelected'] = dChoiceSelected

        dChoicePress = self.builder.loadChoiceCommon('ChoicePress', None)
        dInitSet['ChoicePress'] = dChoicePress

        if dChoiceSelected['press']:
            pressId = dChoicePress[dChoiceSelected['press']]
        else:
            pressId = None
        dChoiceBook = self.builder.loadChoiceCommon('ChoiceBook', pressId)
        dInitSet['ChoiceBook'] = dChoiceBook
        dInitSet['ChoiceTest'] = self.loadTest('pressid', pressId)

        if dChoiceSelected['book']:
            bookId = dChoiceBook[dChoiceSelected['book']]
        else:
            bookId = None
        dChoiceUnit = self.builder.loadChoiceCommon('ChoiceUnit', bookId)
        dInitSet['ChoiceUnit'] = dChoiceUnit
        dInitSet['ChoiceTest'] = self.loadTest('bookid', bookId)

        if dChoiceSelected['unit']:
            unitId = dChoiceUnit[dChoiceSelected['unit']]
        else:
            unitId = None
        dChoiceLesson = self.builder.loadChoiceCommon('ChoiceLesson', unitId)
        dInitSet['ChoiceLesson'] = dChoiceLesson
        dInitSet['ChoiceTest'] = self.loadTest('unitid', unitId)

        if dChoiceSelected['lesson']:
            lessonId = dChoiceLesson[dChoiceSelected['lesson']]
        else:
            lessonId = None
        self.lessonId = lessonId
        # self.loadWordsByLesson(lessonId)
        dInitSet['ChoiceTest'] = self.loadTest('lessonid', lessonId)
        self.dInitSet = dInitSet

        self.loadTime()
        # testBy = ''
        # byId = ''
        # # self.loadTest(testBy, byId)
        # dChoiceTest = {'全部': 'all'}
        # self.dInitSet['ChoiceTest'] = dChoiceTest
        # self.dInitSet['ChoiceSelected']['Test'] = None
        self.loadWordScope()

    def saveSelected(self):
        self.builder.saveSelected(self.dInitSet['ChoiceSelected'])

    def loadTime(self):
        dChoiceTime = {'上次测试':'last', '当天测试':'1day', '一周内测试':'1week', '一月内测试':'1month', '六月内测试':'6months', '一年内测试':'1year', '全部测试':'all'}
        self.dInitSet['ChoiceTime'] = dChoiceTime
        # self.dInitSet['ChoiceSelected']['Time'] = '上次测试'
        return dChoiceTime

    def loadTest(self, fieldName, fieldValue):
        # dChoiceTest = {'全部':'all'}
        if fieldValue is None:
            return {}
        dChoiceTest = self.builder.loadTest(fieldName, fieldValue)
        self.dInitSet['ChoiceTest'] = dChoiceTest
        # self.dInitSet['ChoiceSelected']['Test'] = None
        return dChoiceTest

    def loadWordScope(self):
        dChoiceWordScope = {'全部':'all', '20':20, '50':50, '100':100}
        self.dInitSet['ChoiceWordScope'] = dChoiceWordScope
        # self.dInitSet['ChoiceSelected']['WordScope'] = '全部'
        return dChoiceWordScope

    def loadBook(self, pressId):
        dChoiceBook = self.builder.loadChoiceCommon('ChoiceBook', pressId)
        self.dInitSet['ChoiceBook'] = dChoiceBook
        self.dInitSet['ChoiceSelected']['book'] = None
        return dChoiceBook

    def loadUnit(self, bookId):
        dChoiceUnit = self.builder.loadChoiceCommon('ChoiceUnit', bookId)
        self.dInitSet['ChoiceUnit'] = dChoiceUnit
        self.dInitSet['ChoiceSelected']['unit'] = None
        return dChoiceUnit

    def loadLesson(self, unitId):
        dChoiceLesson = self.builder.loadChoiceCommon('ChoiceLesson', unitId)
        self.dInitSet['ChoiceLesson'] = dChoiceLesson
        self.dInitSet['ChoiceSelected']['lesson'] = None
        return dChoiceLesson

    def loadWordsByLesson(self, lessonId):
        self.presenteWords = ['开始听写', '听写完毕']
        self.wordsGroup = self.builder.loadLessonWords(lessonId)
        t = threading.Thread(target=self.makeVoice)
        t.setDaemon(True)
        t.start()

    def loadWordsByTest(self, aTestId):
        self.presenteWords = ['开始听写', '听写完毕']
        self.wordsGroup = self.builder.loadTestWords(aTestId)
        t = threading.Thread(target=self.makeVoice)
        t.setDaemon(True)
        t.start()

# class Application(Frame):
#     def __init__(self, master=None):
#         Frame.__init__(self, master)
#         self.pack()
#         self.createWidgets()
#         self.columnNum = 6
#         self.wordCount = 0
#         self.columnCount = 0
#         self.rowCount = 0
#         # self.listenGroup = []
#         self.ft30 = tkinter.font.Font(size=30)
#         self.ft25 = tkinter.font.Font(size=25)
#         self.nextOne = 0
#         self.loaded = 0
#
#     def createWidgets(self):
#
#         # self.helpbutton.pack(side='right')
#         # self.nameInput = Entry(self)
#         # self.nameInput.pack()
#         ft30 = tkinter.font.Font(size=30)
#         self.loadButton = Button(self, text='加载词语', command=self.load)
#         self.loadButton.grid(row=10,column=0,padx=3,sticky=W)
#         self.startButton = Button(self, text='开始听写', command=self.start)
#         self.startButton.grid(row=10,column=1,sticky=W)
#         self.startButton = Button(self, text='下一个', command=self.nextWord)
#         self.startButton.grid(row=10, column=2)
#         self.helpbutton = Button(self, text='帮助', command=self.help)
#         self.helpbutton.grid(row=10, column=5, sticky=E, padx=3)
#         self.pinyinLable = Label(self,text='拼音', font=ft30)
#         self.pinyinLable.grid(row=9,column=1, columnspan=2, sticky=E+W)
#         self.pinyinLable['font'] = ft30
#         self.wordLable = Label(self, text='词语', font=ft30)
#         self.wordLable.grid(row=9,column=4, columnspan=2, sticky=E+W)
#
#         self.scrollBar = Scrollbar(self)
#         self.scrollBar.grid(row=1,sticky=E)
#         self.tree = tkinter.ttk.Treeview(self,
#                                  columns=('c1', 'c2', 'c3', 'c4', 'c5', 'c6'),
#                                  yscrollcommand=self.scrollBar.set,show='headings')
#         self.tree.column('c1', width=150, anchor='center')
#         self.tree.column('c2', width=150, anchor='center')
#         self.tree.column('c3', width=150, anchor='center')
#         self.tree.column('c4', width=150, anchor='center')
#         self.tree.column('c5', width=150, anchor='center')
#         self.tree.column('c6', width=150, anchor='center')
#
#         self.tree.grid(row=1,columnspan=5)
#         self.scrollBar.config(command=self.tree.yview)
#
#         self.tree.bind("<Button-1>", self.markError)
#
#     def markError(self,event):
#
#         word = self.tree.identify_element(event.x,event.y)
#         word = '%s %s %s' % (self.tree.identify_row(event.y), self.tree.identify_column(event.x), word)
#         self.pinyinLable['text'] = word
#
#     def load(self):
#         self.listenWriter = ListenWrite(self)
#         self.listenWriter.setDaemon(True)
#         self.listenWriter.loadWords()
#         self.loaded = 1
#
#         # wordNum = self.listenWriter.listenGroup.size
#         # j = 0
#         # wordRow = []
#         # for i in range(wordNum):
#         #     if i >= wordNum: break
#         #     j += 1
#         #     if j == 7:
#         #         # self.tree.insert('','end',values=['test'] * 6)
#         #         witem = self.tree.insert('', 'end', values=wordRow)
#         #         # print(witem.tags)
#         #         wordRow = []
#         #         j = 0
#         #     wordRow.append(self.listenWriter.listenGroup.listListenWords[i].pinyin)
#         # if len(wordRow) > 0:
#         #     self.tree.insert('', 'end', values=wordRow)
#         # print('font: %s' % self.tree['font'])
#
#     def displayPinyin(self, pinyin):
#         str = ''
#         num = len(pinyin)
#         for i in range(num):
#             py = pinyin[i][0].encode('utf-8')
#             str = '%s %s' % (str,py)
#         # print(str)
#         self.pinyinLable['text'] = str
#         # ft = tkFont.Font(size=30)
#         # self.pinyinLable['font'] = ft
#         # print('font: %s' % self.pinyinLable['font'])
#         self.wordCount += 1
#         self.columnCount += 1
#         if self.columnCount >= self.columnNum:
#             self.columnCount = 0
#             self.rowCount += 1
#             self.currentItem = self.tree.insert('', 'end')
#         self.tree.set(self.currentItem, self.columnCount, value=str)
#         # self.master.update_idletasks()
#
#     def start(self):
#         # name = self.nameInput.get() or 'world'
#         # tkMessageBox.showinfo('Message', 'Hello, %s' % name)
#         if self.loaded == 0:
#             self.load()
#         self.wordCount = 0
#         self.columnCount = -1
#         self.currentItem = self.tree.insert('', 'end')
#         # self.listenWords()
#         self.listenWriter.start()
#
#     def listenWords(self):
#         self.listenGroup = self.listenWriter.listenGroup
#         self.client = self.listenWriter.client
#         player = self.listenWriter.player
#
#         player.preparePlay(self.client, player.begionWord, player.begionFile)
#         player.preparePlay(self.client, player.endword, player.endFile)
#         player.playOne(player.begionFile, 1)
#
#         for i in range(self.listenGroup.size):
#             listenWord = self.listenGroup.listListenWords[i]
#             wordPinyin = listenWord.pinyin
#             # textPinyin = []
#             # for i in range(len(wordPinyin)):
#             #     textPinyin[i] = wordPinyin[i].encode('utf-8')
#             self.displayPinyin(wordPinyin)
#
#             clip = player.playOne(listenWord.voiceFile, listenWord.sleepSeconds)
#             if self.nextOne == 1:
#                 continue
#             player.playOne(listenWord.voiceFile, listenWord.sleepSeconds, clip)
#         player.playOne(player.endFile, 1)
#
#     def nextWord(self):
#         # self.listenWriter.player.nextOne = 1
#         self.nextOne = 1
#
#     def help(self):
#         msg = '''生词听写工具使用方法：
# 1.把要听写的词语写入文件listenwords.txt中，词语之间用空格隔开。
# 2.行首是#的为注释行，不听写。
# 3.程序运行时，会把listenwords.txt文件中所有非#开头的行，读入内存。按空格分隔拆出各个词语，通过语音合成得到读音，依次播放，每个词播放两遍。
# 4.当加入新的词语时，需要联网得到读音，请保证网络畅通。
#
#                                                                  作者：王新田
#                                                                    13520498010'''
#         tkinter.messagebox.showinfo('Help', msg)

class WordChoice(listenwritewin.MyDialog1):
    def __init__(self, parent, wordtype):
        super(self.__class__, self).__init__(parent)
        self.wordType = wordtype
        self.listenWriter = parent.listenWriter
        self.pressChoice = {}
        self.bookChoice = {}
        self.unitChoice = {}
        self.lessonChoice = {}
        self.choiceSelected = {}
        self.choiceTime = {}
        self.choiceTest = {}
        self.choiceWordScope = {}
        self.pressId = None
        self.bookId = None
        self.unitId = None
        self.lessonId = None
        self.aTestId = []

    def setInit(self, dInitSet):
        try:
            self.choiceSelected = dInitSet['ChoiceSelected']
            self.pressChoice = dInitSet['ChoicePress']
            self.bookChoice = dInitSet['ChoiceBook']
            self.unitChoice = dInitSet['ChoiceUnit']
            self.lessonChoice = dInitSet['ChoiceLesson']
            self.choiceTime = dInitSet['ChoiceTime']
            self.choiceTest = dInitSet['ChoiceTest']
            self.choiceWordScope = dInitSet['ChoiceWordScope']
        except Exception as e:
            msg = '%s: %s' % (e.__class__, str(e))
            wx.MessageBox(msg, '异常', wx.OK | wx.ICON_INFORMATION)

        aPressChoice = dInitSet['ChoicePress'].keys()
        self.setChoiceItem(self.m_choice5, aPressChoice, self.choiceSelected['press'])
        # for i,item in enumerate(aPressChoice):
        #     self.m_choice5.Append(item)
        #     if item == self.choiceSelected['press']:
        #         self.m_choice5.SetSelection(i)

        aBookChoice = dInitSet['ChoiceBook'].keys()
        self.setChoiceItem(self.m_choice6, aBookChoice, self.choiceSelected['book'])
        # for i,item in enumerate(aBookChoice):
        #     self.m_choice6.Append(item)
        #     if item == self.choiceSelected['book']:
        #         self.m_choice6.SetSelection(i)

        aUnitChoice = dInitSet['ChoiceUnit'].keys()
        self.setChoiceItem(self.m_choice7, aUnitChoice, self.choiceSelected['unit'])
        # for i,item in enumerate(aUnitChoice):
        #     self.m_choice7.Append(item)
        #     if item == self.choiceSelected['unit']:
        #         self.m_choice7.SetSelection(i)

        aLessonChoice = dInitSet['ChoiceLesson'].keys()
        self.setChoiceItem(self.m_choice8, aLessonChoice, self.choiceSelected['lesson'])
        # for i,item in enumerate(aLessonChoice):
        #     self.m_choice8.Append(item)
        #     if item == self.choiceSelected['lesson']:
        #         self.m_choice8.SetSelection(i)
        if self.wordType == 'new':
            if self.choiceSelected['lesson']:
                self.lessonId = self.lessonChoice[self.choiceSelected['lesson']]
                self.listenWriter.loadWordsByLesson(self.lessonId)
            return

        aChoiceTime = dInitSet['ChoiceTime'].keys()
        self.setChoiceItem(self.m_choice71, aChoiceTime, self.choiceSelected['Time'])
        # for i, item in enumerate(aChoiceTime):
        #     self.m_choice71.Append(item)
        #     if item == self.choiceSelected['Time']:
        #         self.m_choice71.SetSelection(i)
        aChoiceTest = dInitSet['ChoiceTest'].keys()
        self.setChoiceItem(self.m_choice81, aChoiceTest, self.choiceSelected['Test'])
        # for i, item in enumerate(aChoiceTest):
        #     self.m_choice81.Append(item)
        #     if item == self.choiceSelected['Test']:
        #         self.m_choice81.SetSelection(i)
        aChoiceWordScope = dInitSet['ChoiceWordScope'].keys()
        self.setChoiceItem(self.m_choice9, aChoiceWordScope, self.choiceSelected['WordScope'])
        # for i, item in enumerate(aChoiceWordScope):
        #     self.m_choice9.Append(item)
        #     if item == self.choiceSelected['WordScope']:
        #         self.m_choice9.SetSelection(i)

    def pressSelect(self, event):
        press = self.m_choice5.GetStringSelection()
        self.choiceSelected['press'] = press
        pressId = self.pressChoice[press]
        self.bookChoice = self.listenWriter.loadBook(pressId)
        self.choiceSelected['book'] = None
        self.setChoiceItem(self.m_choice6, self.bookChoice.keys())
        self.unitChoice = {}
        self.choiceSelected['unit'] = None
        self.m_choice7.Clear()
        self.lessonChoice = {}
        self.choiceSelected['lesson'] = None
        self.m_choice8.Clear()
        if self.wordType == 'wrong':
            self.loadTest('pressid', pressId)

    def setChoiceItem(self, choice, aItem, selected=None):
        choice.Clear()
        for i, item in enumerate(aItem):
            choice.Append(item)
            if selected is None:
                continue
            if item == selected:
                choice.SetSelection(i)
        # choice.Au

    def bookSelect(self, event):
        book = self.m_choice6.GetStringSelection()
        # if book == self.choiceSelected['book']:
        #     return
        self.choiceSelected['book'] = book
        bookId = self.bookChoice[book]
        self.unitChoice = self.listenWriter.loadUnit(bookId)
        self.choiceSelected['unit'] = None
        self.setChoiceItem(self.m_choice7, self.unitChoice.keys())
        # self.m_choice7.Clear()
        # for item in self.unitChoice.keys():
        #     self.m_choice7.Append(item)
        self.lessonChoice = {}
        self.choiceSelected['lesson'] = None
        self.m_choice8.Clear()
        if self.wordType == 'wrong':
            self.loadTest('bookid', bookId)

    def unitSelect(self, event):
        unit = self.m_choice7.GetStringSelection()
        # if unit == self.choiceSelected['unit']:
        #     return
        self.choiceSelected['unit'] = unit
        unitId = self.unitChoice[unit]
        self.lessonChoice = self.listenWriter.loadLesson(unitId)
        self.choiceSelected['lesson'] = None
        self.setChoiceItem(self.m_choice8, self.lessonChoice.keys())
        # self.m_choice8.Clear()
        # for item in self.lessonChoice.keys():
        #     self.m_choice8.Append(item)
        if self.wordType == 'wrong':
            self.loadTest('unitid', unitId)

    def lessonSelect(self, event):
        lesson = self.m_choice8.GetStringSelection()

        self.choiceSelected['lesson'] = lesson
        self.lessonId = self.lessonChoice[lesson]
        # print('lessonid: %s' % self.lessonId)
        if self.wordType == 'wrong':
            self.loadTest('lessonid', self.lessonId)

    def loadTest(self, fieldName, fieldValue):
        self.choiceTest = self.listenWriter.loadTest(fieldName, fieldValue)
        self.choiceSelected['Test'] = None
        self.setChoiceItem(self.m_choice81, self.choiceTest.keys())
        self.aTestId = []
        for key in self.choiceTest.keys():
            testId = str(self.choiceTest[key][0])
            self.aTestId.append(testId)

    def testSelect(self, event):
        test = self.m_choice81.GetStringSelection()
        # if test == self.choiceSelected['Test']:
        #     return
        self.choiceSelected['Test'] = test
        self.aTestId = [str(self.choiceTest[test][0])]

    def DoOk(self, event):
        self.listenWriter.dInitSet['ChoiceSelected'] = self.choiceSelected
        self.listenWriter.dInitSet['ChoicePress'] = self.pressChoice
        self.listenWriter.dInitSet['ChoiceBook'] = self.bookChoice
        self.listenWriter.dInitSet['ChoiceUnit'] = self.unitChoice
        self.listenWriter.dInitSet['ChoiceLesson'] = self.lessonChoice
        self.listenWriter.dInitSet['ChoiceTime'] = self.choiceTime
        self.listenWriter.dInitSet['ChoiceTest'] = self.choiceTest
        self.listenWriter.dInitSet['ChoiceWordScope'] = self.choiceWordScope
        self.listenWriter.wordType = self.wordType
        if self.wordType == 'new':
            self.listenWriter.loadWordsByLesson(self.lessonId)
        elif self.wordType == 'wrong':
            if len(self.aTestId) > 0:
                self.listenWriter.loadWordsByTest(self.aTestId)
            else:
                wx.MessageBox("No test was selected.")
        self.EndModal(0)


class LisWriFram(listenwritewin.MyFrame1):
    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)
        self.listenWriter = ListenWrite(self)
        self.aListenWords = []
        self.wordCount = 0
        self.loaded = 0
        self.loadInitSet()
        # self.nextOne = 0
        self.remarking = 0

    def loadInitSet(self):
        self.listenWriter.loadInit()

    def closeApp(self, event):
        self.listenWriter.saveSelected()
        event.Skip()

    def loadWords(self, event):
        self.loaded = 1
        self.listenWriter.loadWords()
        self.loaded = 9
        # t.join()
        # self.loaded = 9

    def startListen(self, event):
        # name = self.nameInput.get() or 'world'
        # tkMessageBox.showinfo('Message', 'Hello, %s' % name)
        # if self.loaded == 0:
        #     self.loadWords(None)
        self.m_button11.Enable(False)
        self.m_button12.Enable(False)
        self.m_button15.Enable(False)
        self.m_button14.Enable(True)
        self.refreshCount()
        self.listenWriter.addTest()
        t = threading.Thread(target=self.listenWriter.playWordes)
        t.setDaemon(True)
        t.start()

    # def addTest(self):
    #     pass

    def nextWord(self, event):
        # self.listenWriter.player.nextOne = 1
        self.listenWriter.player.nextOne = 1

    def pause(self,event):
        self.m_button11.Enable(False)
        self.m_button12.Enable(True)
        self.m_button15.Enable(True)
        self.listenWriter.pause()

    def playContinue(self, event):
        self.m_button11.Enable(False)
        self.m_button12.Enable(False)
        self.m_button15.Enable(False)
        self.m_button14.Enable(True)
        t = threading.Thread(target=self.listenWriter.playContinue)
        t.setDaemon(True)
        t.start()

    def importWords(self, event):
        wildcard = "Text Files (*.txt)|*.txt"
        dlg = wx.FileDialog(self, "选择词语文件", os.getcwd(), "", wildcard, wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
            self.listenWriter.importWords(file)
        #     f = open(dlg.GetPath(), 'r')
        #     with f:
        #         data = f.read()
        #         self.text.SetValue(data)
        dlg.Destroy()

    def listenNew(self, event):
        selectForm = WordChoice(self, 'new')
        selectForm.setInit(self.listenWriter.dInitSet)
        selectForm.m_staticText81.Enable(False)
        selectForm.m_staticText101.Enable(False)
        selectForm.m_staticText11.Enable(False)
        selectForm.m_choice71.Enable(False)
        selectForm.m_choice81.Enable(False)
        selectForm.m_choice9.Enable(False)
        selectForm.ShowModal()
        self.m_button11.Enable(True)
        # try:
        #     selectForm = WordChoice(self, 'new')
        #     selectForm.setInit(self.listenWriter.dInitSet)
        #     selectForm.m_staticText81.Enable(False)
        #     selectForm.m_staticText101.Enable(False)
        #     selectForm.m_staticText11.Enable(False)
        #     selectForm.m_choice71.Enable(False)
        #     selectForm.m_choice81.Enable(False)
        #     selectForm.m_choice9.Enable(False)
        #     selectForm.ShowModal()
        #     self.m_button11.Enable(True)
        # except Exception as e:
        #     msg = '%s: %s' % (e.__class__, str(e))
        #     wx.MessageBox(msg, 'exception', wx.OK | wx.ICON_INFORMATION)

    def listenWrong(self, event):
        try:
            selectForm = WordChoice(self, 'wrong')
            selectForm.setInit(self.listenWriter.dInitSet)

            selectForm.ShowModal()
            self.m_button11.Enable(True)
        except Exception as e:
            msg = '%s: %s' % (e.__class__, str(e))
            wx.MessageBox(msg, 'exception', wx.OK | wx.ICON_INFORMATION)

    def errorListen(self, event):
        wx.MessageBox("听写错词。。。", '听写', wx.OK | wx.ICON_INFORMATION)

    def displayWords(self, event):
        # self.wordCount = 0
        self.refreshCount()
        aWords = self.listenWriter.wordsGroup
        for i,word in enumerate(aWords):
            row = i // 6
            col = i % 6
            self.m_grid2.SetCellValue(row, col, word.word)

    def refreshCount(self):
        # if self.wordCount == 0:
        #     return
        self.m_grid2.ClearGrid()
        self.wordCount = 0
        # row = self.wordCount // 6
        # self.wordCount = (row + 1) * 6

    def displayPinyin(self, pinyin):
        str = ''
        num = len(pinyin)
        for i in range(num):
            py = pinyin[i][0]
            str = '%s %s' % (str,py)
        if len(str) > 0:
            str = str[1:]
        self.m_staticText8.LabelText = str
        row = self.wordCount // 6
        col = self.wordCount % 6
        self.m_grid2.SetCellValue(row, col, str)
        self.wordCount += 1

    def remarkError(self, event):
        wx.MessageBox(str(dir(event)), '选择词语', wx.OK | wx.ICON_INFORMATION)
        self.remarking = 1
        self.defaultColour = self.m_grid2.GetDefaultCellBackgroundColour()
        self.errColore = self.m_grid2.SelectC

    def saveTest( self, event ):
        # aWrongPosi = 'Selected %s' % self.m_grid2.GetSelectedCells()
        # wx.MessageBox("RangeSelectCell: %s \n" % aWrongPosi)
        aSelectedCells = self.m_grid2.GetSelectedCells()
        aWrongWords = []
        msg = ''
        for cell in aSelectedCells:
            aWrongWords.append(self.m_grid2.GetCellValue(cell.Row, cell.Col))
        wx.MessageBox("wrong words: %s \n" % aWrongWords)
        self.listenWriter.saveTest(aWrongWords)

    def saveError(self, event):
        self.remarking = 0
        event.Skip()

    def selectCell( self, event ):
        # if self.remarking == 0:
        #     return
        pass
        # if event.Selecting():
        #     self.m_grid2.SelectCells(event.GetRow, event.GetCol)
        #     msg = 'Selected %s' % self.m_grid2.SelectCells
        # else:
        #     msg = 'Deselected'
        # wx.MessageBox("OnSelectCell: %s (%d,%d) %s\n" %
        #                (msg, event.GetRow(), event.GetCol(), event.GetPosition()))
        #
        # # Another way to stay in a cell that has a bad value...
        # row = self.m_grid2.GetGridCursorRow()
        # col = self.m_grid2.GetGridCursorCol()
        #
        # # event.GetString()
        # # wx.MessageBox(event.GetString(), '选择词语', wx.OK | wx.ICON_INFORMATION)

    def onRangeSelect(self, evt):
        pass
        # if evt.Selecting():
        #     msg = 'Selected %s' % self.m_grid2.GetSelectedCells()
        #     # self.m_grid2.GetSelectedCells()
        # else:
        #     msg = 'Deselected'
        # wx.MessageBox("OnRangeSelectCell: %s top_left %s bottom_right %s\n" %
        #                (msg, evt.GetTopLeftCoords(), evt.GetBottomRightCoords()))


# start
if __name__ == '__main__':
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
    # frame.loadWords(None)
    # app.
    app.MainLoop()

