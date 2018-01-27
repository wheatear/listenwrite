# -*- coding: utf-8 -*-

import os
import sys
import pypinyin

class Chinese2Pinyin(object):
    def __init__(self, wordFile):
        self.wordFile = wordFile
        self.pinyinFile = '%s.pinyin' % self.wordFile

    def makePinyin(self):
        inFile = self.openFile(self.wordFile, 'r')
        outFile = self.openFile(self.pinyinFile, 'w')
        for line in inFile:
            words = line.strip()
            if len(words) == 0:
                outFile.write(line)
                continue
            if words[0] == '#':
                outFile.write(line)
                continue
            lWords = words.split(' ')
            sPinyin = ''
            for word in lWords:
                uword = word.decode('utf-8')
                pinyin = pypinyin.pinyin(uword)

                str = ''
                num = len(pinyin)
                for i in range(num):
                    py = pinyin[i][0].encode('utf-8')
                    str = '%s %s' % (str, py)
                # print(str)
                sPinyin = '%s    %s' % (sPinyin, str)
                sPinyin = sPinyin.strip()
            outFile.write('%s\r\n' % sPinyin)

        inFile.close()
        outFile.close()

    def openFile(self, file, mode):
        try:
            fp = open(file, mode)
        except IOError, e:
            print('Can not open file %s: %s' % (file, e))
            exit()
        return fp


# main there
if __name__ == '__main__':
    wordFile = sys.argv[1]
    pinyin = Chinese2Pinyin(wordFile)
    pinyin.makePinyin()
