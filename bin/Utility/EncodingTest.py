# coding=utf-8

import multiprocessing
#import numpy as np

utf16heading = b'\xff\xfe'
utf8heading = b'\xef\xbb\xbf'

utf8str = 'utf8'
utf8sig = 'utf-8-sig'
utf16str = 'utf16'
big5str = 'big5'  # 'cp950'
gbstr = 'gb2312'  # 'cp936'
utf_type = [utf8str, utf8sig, utf16str, big5str, gbstr]

def EncodingTestStr(ret_value, bytestr):
    import numpy as np

    thrhold = 0.95
    defaultfmt = utf8str

    def LeadingCodeCheck(bytestr):
        blen = len(bytestr)
        if blen >= 2 and bytestr[:2] == utf16heading:
            return utf16str
        if blen >= 3 and bytestr[:3] == utf8heading:
            return utf8sig
        return None
    def bLikeUtf16(bytestr):
        wlen = len(bytestr) // 2
        wstr = np.frombuffer(bytestr, dtype=np.uint16, count=wlen)
        validcnt = np.sum((((wstr >= 0x4e00) & (wstr < 0x9fff)) | (wstr < 256)).astype(int))
        if validcnt > wlen * thrhold:
            return True
        return False
    def bLikeUtf8(bytestr):
        bstr = np.frombuffer(bytestr, dtype=np.uint8)
        blen = len(bstr)
        i = 0
        asc = 0
        err = 0
        ch = 0
        while i < blen:
            extno = 0 if not bstr[i] & 0x80 else (1 if not bstr[i] & 0x20 else (2 if not bstr[i] & 0x10 else 3))
            i += 1
            if i + extno > blen:
                err += 1
            else:
                if extno == 0:
                    asc += 1
                else:
                    if sum((bstr[i:i + extno] & 0xc0 == 0xc0).astype(int)) < extno:
                        err += 1
                    else:
                        ch += 1
            i += extno
        return ch > (ch + err) * thrhold
    def GB1stRange(b):
        return (b >= 0xa0) and (b <= 0xfe)
    def GB2ndRange(b):
        return (b >= 0xa0) and (b <= 0xfe)
    def Big51stRange(b):
        return (b >= 0x81) and (b <= 0xfe)
    def Big52ndRange(b):
        return ((b >= 0x40) and (b <= 0x7e)) or ((b >= 0xa1) and (b <= 0xfe))
    def bLikeMultiByte(bytestr, range1st, range2nd):
        blen = len(bytestr)
        barr = np.frombuffer(bytestr, dtype=np.uint8, count=blen)
        i = 0
        asc = 0
        err = 0
        ch = 0
        while i < blen-1:
            if barr[i] < 0x80:
                asc += 1
            else:
                if not range1st(barr[i]):
                    err += 1
                else:
                    i += 1
                    if range2nd(barr[i]):
                        ch += 1
                    else:
                        err += 1
            i += 1
        return ch > (ch + err) * thrhold
    def bLikeBig5(bytestr):
        return bLikeMultiByte(bytestr, Big51stRange, Big52ndRange)
    def bLikeGB(bytestr):
        return bLikeMultiByte(bytestr, GB1stRange, GB2ndRange)

    ret_value.value = utf_type.index(defaultfmt)
    Leadcode = LeadingCodeCheck(bytestr)
    #utf_type = [utf16heading, utf8heading, utf8str, utf8sig, utf16str, big5str, gbstr]
    if Leadcode != None:
        ret_value.value = utf_type.index(Leadcode)
        #return Leadcode
    elif bLikeUtf8(bytestr):
        ret_value.value = utf_type.index(utf8str)
        #return utf8str
    elif bLikeUtf16(bytestr):
        ret_value.value = utf_type.index(utf16str)
        #return utf16str
    elif bLikeGB(bytestr):
        ret_value.value = utf_type.index(gbstr)
        #return gbstr
    elif bLikeBig5(bytestr):
        ret_value.value = utf_type.index(big5str)
        #return big5str
    #ret_value.value = defaultfmt
    #return defaultfmt

def FileEncodingTest(fname):
    import numpy as np
    testsize = 2048
    defaultfmt = utf8str
    try:
        filesize = os.stat(fname).st_size
        f = open(fname, mode='rb')
    except:
        return utf_type.index(defaultfmt)  # None
    readsize = min(testsize, filesize)
    data = f.read(readsize)
    f.close()
    ret_value = multiprocessing.Value("i", 0, lock=False)
    #reader_process = multiprocessing.Process(target=EncodingTestStr, args=[ret_value, data])
    # reader_process.start()
    # reader_process.join()
    # return ret_value.value
    EncodingTestStr(ret_value, data)
    return ret_value.value

def OpenFile(fname, mode, encoding='utf8'):
    if mode == 'w':
        return open(fname, mode, encoding=encoding)
    try:
        if not encoding:
            encoding_str = utf_type[ FileEncodingTest(fname) ]
            return open(fname, mode, encoding=encoding_str)
        return open(fname, mode, encoding=encoding)
    except FileNotFoundError as e:
        raise e

'''
==================================================
Lines below are for test only
==================================================
'''
import os
def selftest():
    def GetFnameList(rootdir):
        nlist = []
        for e in os.walk(rootdir):
            addlist = [e[0] + '/' + s for s in e[2] if s[0] != '.']
            nlist += addlist
#            for t in addlist:
#                print(t)
#         print(len(nlist), ' Files')
        return nlist
    #rootdir = '/Shieh_Data/RawText/DonSun/'
    #rootdir = '/Shieh_Data/RawText/eBook/'
    #rootdir = '/Shieh_Data/RawText/eBook/總裁/'
    rootdir = '/Shieh_Data/860txt/'
#   rootdir = '/Shieh_Python/'

    fnames = GetFnameList(rootdir) #['t.txt', 't-w.txt', 'readdict.py', '/Shieh_Data/860txt/鹿鼎記.txt']

    for fn in fnames:
        fmt = FileEncodingTest(fn)
        print(fmt, fn)
    str='自台的好朋友今天是好1234'
    ustr = str.encode(encoding='utf16')
    ty=EncodingTestStr(ustr)
    # print(ty,ustr)
    ustr = str.encode(encoding='utf8')
    ty=EncodingTestStr(ustr)
    # print(ty,ustr)
    ustr = str.encode(encoding='utf-8-sig')
    ty=EncodingTestStr(ustr)
    # print(ty,ustr)
    ustr = str.encode(encoding='big5') #cp950')
    ty=EncodingTestStr(ustr)
    # print(ty,ustr)
    ustr = str.encode(encoding='gb2312') #encoding='cp936')
    ty=EncodingTestStr(ustr)
    # print(ty,ustr)

# selftest()
