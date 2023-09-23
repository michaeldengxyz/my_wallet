#Pyhton 3.x
# -*- coding: UTF-8 -*-
#rev 0.1
#zip or unzip

import sys, os, re, time, glob
import json
import traceback
import zlib
import numpy as np
from shutil import copyfile
from colorama import init
init(autoreset=True) #set this True to print color fonts in the console

def UZ_Check(folder="", filename="", fileExt = 'py', force2zip=False, force2unzip=False):
    if not folder:
        folder = re.sub(r'\\','/',os.path.abspath(os.path.dirname(__file__)))
        UT_Print2Log('white',"\nroot:", folder)

    filepathZip = folder + '/backup/' + filename + ".zlib"
    UT_FolderCreate(folder + '/backup')

    filepathOri = folder + '/' + filename + "." + fileExt

    if force2zip: #force to make a zip for backup
        UZ_ZIP(from_filepath = filepathOri,  to_filepath = filepathZip, fileExt = 'zlib')
        
    if force2unzip: #force to restore from a zip backup file
        UZ_ZIP(from_filepath = filepathZip, to_filepath = filepathOri, fileExt = fileExt)

    if not os.path.exists(filepathZip):
        UZ_ZIP(from_filepath = filepathOri,  to_filepath = filepathZip, fileExt = 'zlib')

    if not os.path.exists(filepathOri):
        UZ_ZIP(from_filepath = filepathZip, to_filepath = filepathOri, fileExt = fileExt)

def UZ_ZIP(from_filepath="", to_filepath="", fileExt = 'py'):
    UT_Print2Log('', sys._getframe().f_lineno, "\n\tFrom:", from_filepath, "\n\tTo", to_filepath)
    if not os.path.exists(from_filepath):  
        UT_Print2Log('red', sys._getframe().f_lineno, '!! The file not eixsting:', from_filepath)      
        return
    
    try:
        filedata    = ''    
        if re.match(r'.*\.zlib$', from_filepath, re.I):
            filedata = UT_FileOpen(from_filepath)
            if filedata:            
                filedata = zlib.decompress(filedata).decode(encoding='UTF-8',errors='ignore')
        else:
            filedata = UT_FileOpen(from_filepath, format='strings')
            filedata = zlib.compress(filedata.encode(encoding='UTF-8',errors='ignore'))   

        if filedata:
            if os.path.exists(to_filepath):
                try:
                    copyfile(to_filepath, to_filepath + '.bak' + time.strftime("%Y%m%dT%H%M%S",time.localtime(time.time())) + '.' + fileExt)
                except:
                    UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())             

            fileFormat  = 'string'
            if re.match(r'.*\.zlib$', to_filepath, re.I):
                fileFormat  = 'bytes'

            UT_FileSave(filedata, to_filepath, format= fileFormat)
        else:
            UT_Print2Log('red', sys._getframe().f_lineno, 'No file data!!') 
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())  

def UZ_CleanBackup(folder=""):
    if not folder:
        folder = re.sub(r'\\','/',os.path.abspath(os.path.dirname(__file__)))
        print("\033[0;37;40m'\nroot:", folder)

    if os.path.exists(folder + '/backup'): 
        #!!! when the file path is deep and every long, will get error and fail to get file size !!!!
        os.chdir(folder + '/backup')

        for f in sorted(glob.glob("*.zlib")): 
            if (f == '.') or (f == '..'):
                continue

            if re.match(r'.*\.zlib\.bak\d+\.zlib$',f,re.I):
                print("UZ_CleanBackup:", f)
                try:
                    fsize = os.path.getsize(f)   
                    ftime = os.path.getmtime(f)
                    if ftime < time.time() - 3600*24*15: #delete file older than 15 days
                        UT_Print2Log('red', sys._getframe().f_lineno, '... delete:', folder + '/backup/' + f)
                        os.unlink(f)
                except:
                    UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc()) 

def UT_PrintInColor(icolor="", text=""):
    pcolor = ''
    if icolor:
        if icolor=='black':
            pcolor = '\033[0;30;40m'
        elif icolor=='red':
            pcolor = '\033[0;31;40m'
        elif icolor=='green':
            pcolor = '\033[0;32;40m'
        elif icolor=='yellow':
            pcolor = '\033[0;33;40m'
        elif icolor=='blue':
            pcolor = '\033[0;34;40m'
        elif icolor=='carmine' or icolor=='#FF33CC':
            pcolor = '\033[0;35;40m'
        elif icolor=='#00CCFF':
            pcolor = '\033[0;36;40m'
        elif icolor=='white':
            pcolor = '\033[0;37;40m'
    else:
        icolor = "#606060"
        pcolor = '\033[0;37;40m'

    #显示方式: 0（默认\）、1（高亮）、22（非粗体）、4（下划线）、24（非下划线）、 5（闪烁）、25（非闪烁）、7（反显）、27（非反显）
    #前景色:   30（黑色）、31（红色）、32（绿色）、 33（黄色）、34（蓝色）、35（洋 红）、36（青色）、37（白色）
    #背景色:   40（黑色）、41（红色）、42（绿色）、 43（黄色）、44（蓝色）、45（洋 红）、46（青色）、47（白色）

    print(pcolor + text + '\033[0m')
    return icolor

def UT_Print2Log(*args):
    ss = []
    for i in range(1,len(args)):
        obj = args[i]
        if(type(obj) == np.ndarray) or type(obj) == tuple or type(obj) == list or type(obj) == dict:
            ss.append(json.dumps(str(obj)))
        else:
            ss.append(str(obj))

    icolor = UT_PrintInColor(icolor=args[0], text= '\t'.join(ss))

def UT_FileOpen(filepath, format='bytes'):    
    UT_Print2Log('', "\t.... Open file:",filepath, format)
    try:
        if os.path.exists(filepath):  
            if format == 'bytes': 
                buffer = b''   
                with open(filepath,'rb') as f:   
                    buffer = f.read()   
                    f.close()
                return buffer
            else:
                buffer = ''   
                with open(filepath,'r',encoding="utf-8") as f:   
                    buffer = f.read()   
                    f.close()
                return buffer
        else:
            UT_Print2Log('red', sys._getframe().f_lineno, "File path is not existing!!")
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())   

def UT_FileSave(data,filepath, format='bytes'):    
    UT_Print2Log('', "\t.... Save to file:",filepath, format)
    try:
        if os.path.exists(filepath):       
            os.unlink(filepath)

        if format == 'bytes':    
            with open(filepath,'wb+') as f:   
                f.write(data)
        else:
            with open(filepath,'w+',encoding="utf-8") as f:  
            #important to have encoding="utf-8", to prevent Window opens the file as encoding="gbk" or else encoding then cause error.
                f.write(str(data))            
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())  

def UT_FolderCreate(folder):
    if not folder:
        return False

    if not os.path.exists(folder):
        os.makedirs(folder)
        if not os.path.exists(folder):
            UT_Print2Log('red', sys._getframe().f_lineno, "Can not create the folder:\n\t" + folder)
            return False
    return True
#UZ_Check(folder=r"E:\OneDrive\Program", filename="mypyUtils", fileExt='py', force2unzip=True)