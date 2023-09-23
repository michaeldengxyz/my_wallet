#Pyhton 3.x
# -*- coding: UTF-8 -*-
#rev 0.1
#common subroutines for logical functions

import sys, os, re
import numpy as np
import json
import traceback
import getpass
from numpyencoder import NumpyEncoder
import time
import win32gui, win32con, win32api
import win32clipboard
from win32api import GetMonitorInfo, MonitorFromPoint
import win32ui
import pynput
from pynput import mouse
import ctypes
from pynput import keyboard as keyboardX
import psutil
from screeninfo import get_monitors
import pygetwindow


import zlib
import base64
import hashlib
from Crypto.Cipher import AES
import random
import difflib
from io import BytesIO
from PIL import Image

from colorama import init
init(autoreset=True) #set this True to print color fonts in the console

WinUtils = {}
WinUtils['win_logs'] = []
WinUtils['has_content_in_clipboard'] = 1

def UT_XYminMax(mm,xy):
    try:
        if not mm.__contains__('xmin'):
            mm['xmin'] = xy[0]
        if not mm.__contains__('ymin'):
            mm['ymin'] = xy[1]
        if not mm.__contains__('xmax'):     
            mm['xmax'] = xy[0]
        if not mm.__contains__('ymax'):
            mm['ymax'] = xy[1]
        
        while len(xy) >0:
             x = xy.pop(0)
             y = xy.pop(0)
             
             if(x > mm['xmax']):
                 mm['xmax'] = x
    
             if(x < mm['xmin']):
                 mm['xmin'] = x
        
             if(y > mm['ymax']):
                 mm['ymax'] = y
    
             if(y < mm['ymin']):
                 mm['ymin'] = y  
    except:        
        UT_Print2Log('red', sys._getframe().f_lineno, "XYminMax error:\n" + traceback.format_exc()) 

def UT_ProcessNew(cmd):
    #cmd = "C:/ProgramData/Anaconda3/envs/tensorflow_gpu/python.exe " + re.sub(r'\\','/',sys.path[0]) + "/image_make_thumbnail2.py " + str(id) + " " + str(num) + " " + str(locknum) 
    UT_Print2Log('', sys._getframe().f_lineno, "ProcessNew:\n\t", cmd)
    try:
        os.system(cmd)
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

def UT_UsedTime(stime, t=0):
    if not t:
        t = time.time() - stime
    tt={'h':'00','m':'00','s':'00'}
    
    if t >= 3600:
        h = int(t/3600)
        tt['h'] = "{:0>2d}".format(h)
        t = t - h*3600
       
    if t >= 60:
        m = int(t/60)
        tt['m'] = "{:0>2d}".format(m)
        t = t - m*60

    if t > 0:
        tt['s'] = "{:0>6.3f}".format(t)

    return tt['h'] + ':' + tt['m'] + ':' + tt['s'] 

def UT_ImageFromBase64String(base64_str, image_path=None):
    #base64_to_image
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    if image_path:
        img.save(image_path)
    return img

def UT_ScreenShotXY(width=0,height=0,xSrc=None,ySrc=None, debug=True):
    #ScreenShotXY
    stime = time.time()
    im_PIL = None  
    err = None
    try:
        if width == 0: 
            return im_PIL,'width can not be 0!'
        if height== 0:
            return im_PIL,'height can not be 0!'

        if xSrc == None:
            return im_PIL,'x0 can not be None!'
        if ySrc == None:
            return im_PIL,'y0 can not be None!'
        
        hWnd = 0
        hWndDC = win32gui.GetWindowDC(hWnd)   #0 - desktop
        #创建设备描述表
        mfcDC = win32ui.CreateDCFromHandle(hWndDC)
        #创建内存设备描述表
        saveDC = mfcDC.CreateCompatibleDC()
        #创建位图对象准备保存图片
        saveBitMap = win32ui.CreateBitmap()
        #为bitmap开辟存储空间
        #UT_Print2Log('', width,height,xSrc,ySrc,';',hWndDC,';',mfcDC) #-1920 1080 1920 1080 ; 889263399 ; object 'PyCDC' - assoc is 000001F1B3EC5998, vi=<None>
        saveBitMap.CreateCompatibleBitmap(mfcDC,width,height)
        #将截图保存到saveBitMap中
        saveDC.SelectObject(saveBitMap)
        #保存bitmap到内存设备描述表
        saveDC.BitBlt((0,0), (width,height), mfcDC, (xSrc, ySrc), win32con.SRCCOPY)  
        #BOOLBitBlt((int x,int y),(int nWidth,int nHeight),CDC*pSrcDC,(int xSrc,int ySrc),DWORDdwRop);
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        ###生成图像
        im_PIL = Image.frombuffer('RGB',(bmpinfo['bmWidth'],bmpinfo['bmHeight']),bmpstr,'raw','BGRX',0,1)
        #UT_Print2Log('', im_PIL)
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hWnd,hWndDC)
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, 'UT_ScreenShotXY [width, height, x0, y0]=',[width, height, xSrc, ySrc], traceback.format_exc())
    #'''
    if debug:
        UT_Print2Log('blue',"UT_ScreenShotXY - used time:", UT_UsedTime(stime)) 

        if isinstance(im_PIL, Image.Image):
            UT_Print2Log('blue',"UT_ScreenShotXY - Image size: %s, mode: %s" % (im_PIL.size, im_PIL.mode))                    
        else:
            UT_Print2Log('red', sys._getframe().f_lineno, "Failed to get screenshot!")
        #'''
    return im_PIL,err

def UT_GetColors(istart=16711680, n=10):
    colors = []
    a = np.linspace(istart,255,n)
    #UT_Print2Log('', sys._getframe().f_lineno, a)
    for i in a:
        c = int(i)
        colors.append('#%06x'%c)
    #UT_Print2Log('', sys._getframe().f_lineno, colors)
    return colors

def UT_HandlerAdaptor(fun,**kwds):
    """
    #let button click event carry parameters
    #sample: 
    canvas.bind('<Button-1>',func=UN_HandlerAdaptor(MeetingUIClosed,tl=tl))
    def MeetingUIClosed(event=None, tl=None):
        try:
            tl.destroy()
        except:
            pass
    """
    return lambda event,fun=fun,kwds=kwds:fun(event,**kwds) 

def UT_isRectanglesInterSection(boxa, boxb, display=False):
    isInteract = True
    try:
        min_x = max(boxa[0], boxb[0])
        min_y = max(boxa[1], boxb[1])
        max_x = min(boxa[2], boxb[2])
        max_y = min(boxa[3], boxb[3])

        if min_x > max_x or min_y > max_y:
            isInteract = False
        if display:
            UT_Print2Log('', "\n---- Is interacted: ", isInteract, boxa, boxb)
    except:
        pass

    '''
    minx = min(boxa[0], boxb[0])
    miny = min(boxa[1], boxb[1])
    maxx = max(boxa[2], boxb[2])
    maxy = max(boxa[3], boxb[3])

    tl = Toplevel()
    canvas=Canvas(tl,
        width = maxx - minx  + 100,
        height= maxy - miny  + 100,
        bg="white",
        relief=FLAT,
        bd = 0,
        )
    canvas.pack(side=TOP, fill=BOTH, expand=1)

    rect = canvas.create_rectangle(
        boxa[0] - minx + 20,
        boxa[1] - miny + 20,
        boxa[2] - minx + 20,
        boxa[3] - miny + 20,
        outline = 'red',
        width= 1
        )

    rect2 = canvas.create_rectangle(
        boxb[0] - minx + 20,
        boxb[1] - miny + 20,
        boxb[2] - minx + 20,
        boxb[3] - miny + 20,
        outline = 'blue',
        width= 1,
    )      

    canvas.create_text(
        10,
        10,
        font = ('Arial', 10, 'normal'),
        text = str(isInteract),
        fill = 'black',
        anchor = W,
        justify = LEFT) 
    '''
    return isInteract

def UT_IsTrue(obj):
    #UT_Print2Log('', type(obj),obj)
    if(type(obj) == np.ndarray and obj.any()):
        return True
    elif(type(obj) == tuple and len(obj)):
        return True
    elif(type(obj) == list and len(obj)):
        return True
    elif(type(obj) == dict and len(obj.keys())):
        return True
    elif obj:
        return True    
    else: 
        return False
    
def UT_IsStrMatched(s1,s2,confidence=0.95):
    s1 = re.sub(r'\s+','',s1)
    s2 = re.sub(r'\s+','',s2)
    ratio = difflib.SequenceMatcher(None, str(s1).upper(), str(s2).upper()).quick_ratio()
    if  ratio > confidence:
        if ratio != 1:
            UT_Print2Log('#FF33CC', '\t---- difflib.SequenceMatcher:',s1,s2,ratio)
        return True
    else:
        return False
    
def UT_GetMD5(instring):
    #GetMD5 
    return str(hashlib.md5(instring.encode(encoding='UTF-8',errors='strict')).hexdigest()).upper()

def UT_RandomKey(n=1):
    #RandomKey
    keys = ''
    for x in range(n):
        keyx = ''
        for i in range(32):
            keyx += chr(random.randint(32,126))     
        keys += str(hashlib.md5(keyx.encode(encoding='UTF-8',errors='strict')).hexdigest()).upper()
    m = 0
    j = len(keys)
    key = ''
    for c in keys:
        m += 1
        key += c
        if (m % 4 == 0) & (m < j):
            key += '-'  
    return key

def UT_CryptMe(instring,key=None,isEncript=True):    
    #CryptMe    
    #fdata['string'] = 'ILOVEU'
    #fdata['key']    = 'DF11-FB15-B7B2-15AB-47B7-7AC4-C6F9-5EFE'
    if not len(str(instring)):
        if isEncript:
            return b''
        else:
            return ''

    fdata = {}
    unit = "characters"
    fdata['string'] = instring
    fdata['size'] = len(fdata['string'])
    fdata['sizeZ']= 0
    fdata['rateC']= 'NA'
    fdata['key'] = key
    fdata['data'] = ''
    try:
        if isEncript:
            #UT_Print2Log('', "\n\t.. Encrypt ..."); 
            fdata['data'] = zlib.compress(fdata['string'].encode(encoding='UTF-8',errors='ignore'))       
            if(fdata['data']):         
                ckey = re.sub(r'-','',fdata['key']); 
                #UT_Print2Log('', "\t\tEncrypted:\n\t\t-- KEY: "+ fdata['key']) 

                cryptor = AES.new(ckey.encode('utf-8'),AES.MODE_CBC,str(ckey[0:16]).encode('utf-8'))                       
                fdata['data'] = base64.b64encode(cryptor.encrypt(UT_PadText(fdata['data']))); 
                
                #UT_Print2Log('', "\t\t-- KEYSIZE: "+str(len(ckey))+"\n\t\t-- BLOCKSIZE: "+str(AES.block_size)+"\n\t\t-- IV: "+ckey[0:16])
            
                fdata['sizeZ']= len(fdata['data'])
                if(fdata['sizeZ']):
                    fdata['rateC'] = "{:0.2f}".format(fdata['size']/fdata['sizeZ'])
            else:
                UT_Print2Log('red', sys._getframe().f_lineno, "\t.. Failed to compress!\n")        
            
            #UT_Print2Log('', "\t.. Compressed: before size="+str(fdata['size'])+" "+unit+", after size="+str(fdata['sizeZ'])+", compressed rate "+str(fdata['rateC'])+"\n") dhkaads
        else:
            #UT_Print2Log('', "\n\t.. Decrypt ..."); 
            ckey = re.sub(r'-','',fdata['key']); 
            cryptor = AES.new(ckey.encode('utf-8'),AES.MODE_CBC,str(ckey[0:16]).encode('utf-8'))  
            fdata['data'] = cryptor.decrypt(base64.b64decode(fdata['string'])); 
            fdata['data'] = zlib.decompress(fdata['data']).decode(encoding='UTF-8',errors='ignore') 
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc()) 

    #UT_Print2Log('', 'In: ',instring,'\nout: ',fdata['data'],'\n')
    return fdata['data']

def UT_PadText(s):
    '''Pad an input string according to PKCS#7''' #
    BS = AES.block_size
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS).encode("utf-8")

def UT_ReplaceFunction(matched):
    #repl_func
    if matched:
        text = matched.group(1)
        return "\\" + text + "+"
    
def UT_WindowCloseViaAltF4(ititle):
    #Wind_CloseViaAltF4
    imouse = mouse.Controller()
    ftext = re.sub(r'\s+',"\\\\s+",re.sub(r'([^a-zA-Z0-9\s])+',UT_ReplaceFunction,ititle))
    for title in pygetwindow.getAllTitles():        
        if title and re.match(r'.*({})'.format(ftext), title, re.I):
            whnd = win32gui.FindWindow(None,title)
            print("\nWind_CloseViaAltF4:", whnd,title)            
            win32gui.SetForegroundWindow(whnd)
            ibox = UT_WindowRectGet(whnd)  #left, top, right, bottom
            imouse.position = (int((ibox[0] + ibox[2])/2), int((ibox[1] + ibox[3])/2))
            imouse.click(mouse.Button.left, 1)
            ctr = pynput.keyboard.Controller()
            with ctr.pressed(
                pynput.keyboard.Key.alt,
                pynput.keyboard.Key.f4):
                pass

def UT_WindowResize(winTitle='', sizeWH=[500, 500], resize='resizeTo'):
    #Wind_Resize
    try:
        win = pygetwindow.getWindowsWithTitle(winTitle)[0]
        if resize == 'resizeTo':
            win.resizeTo(sizeWH[0], sizeWH[1])
        elif resize == 'resize':
            win.resize(sizeWH[0], sizeWH[1])
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, "\nWind_Resize:\n", traceback.format_exc())   

def UT_WindowInputSubmit(todo,hwnd,offsetXY,imouse,keyboard,str_in,hit_enter=False,sleepAfter=5, winScale =1):
    #Wind_Input_Submit
    UT_Print2Log('', "\n" + todo, hwnd,offsetXY,imouse,keyboard,str_in)
    rect = UT_WindowRectGet(hwnd)  #left, top, right, bottom
    UT_Print2Log('', hwnd, win32gui.GetWindowText(hwnd), rect)
    win32gui.SetForegroundWindow(hwnd)

    x = rect[0] + offsetXY[0]
    y = rect[1] + offsetXY[1]
    UT_Print2Log('', "Click on this text point (",x, y,"), offset=(", offsetXY[0],offsetXY[1],")")
    imouse.position = (int(x/winScale), int(y/winScale))
    time.sleep(1)
    imouse.click(mouse.Button.left, 1)
    UT_ClipboardPaste(str_in,delstr=True)
    time.sleep(1)

    x = rect[0] + offsetXY[2]
    y = rect[1] + offsetXY[3]
    imouse.position = (int(x/winScale), int(y/winScale))
    time.sleep(1)

    if hit_enter:
        UT_Print2Log('', "keyboard.press(keyboardX.Key.enter)")
        keyboard.press(keyboardX.Key.enter)
        keyboard.release(keyboardX.Key.enter)
    else:
        UT_Print2Log('', "Click on this button point (",x, y,"), offset=(", offsetXY[2],offsetXY[3],")")
        imouse.click(mouse.Button.left, 1)

    time.sleep(sleepAfter)
    return win32gui.GetForegroundWindow()

def UT_Window2LeftMousePress(todo='',hwnd=None,offsetXY=[0,0],imouse=None,sleepAfter=5):
    #Wind2LeftMousePress
    try:
        rect = [0, 0]
        title = 'N/A'
        if hwnd:
            rect = UT_WindowRectGet(hwnd)  #left, top, right, bottom
            title= win32gui.GetWindowText(hwnd)
        UT_Print2Log('', "\n" + todo, hwnd, title, rect)

        y = rect[1] + offsetXY[1]
        x = rect[0] + offsetXY[0]

        if UT_IsMouseOnRightPosition([x,y]):
            time.sleep(0.5)

            imouse.position = (x + 50, y + 50)
            time.sleep(0.2)
            imouse.move(-50, -50)
            imouse.press(mouse.Button.left)

            time.sleep(sleepAfter)
        else:
            UT_Print2Log('red', sys._getframe().f_lineno, "Failed to click on this button/point (",x, y,"), offset=(", offsetXY[0],offsetXY[1],")!!!!")
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, "\n" + todo, traceback.format_exc())   

def UT_Window2ClickButton(todo,hwnd,offsetXY,imouse,hit_enter=False,keyboard=None,sleepAfter=5):
    #Wind2ClickButton
    try:
        rect = [0, 0]
        title = 'N/A'
        if hwnd:
            rect = UT_WindowRectGet(hwnd)  #left, top, right, bottom 
            title= win32gui.GetWindowText(hwnd)
        UT_Print2Log('', "\n" + todo, hwnd, title, rect)

        y = rect[1] + offsetXY[1]
        x = rect[0] + offsetXY[0]

        if UT_IsMouseOnRightPosition([x,y]):
            time.sleep(0.5)

            if hit_enter and keyboard:
                UT_Print2Log('', "keyboard.press(keyboardX.Key.enter)")
                keyboard.press(keyboardX.Key.enter)
                keyboard.release(keyboardX.Key.enter)
            else:        
                UT_Print2Log('', "Click on this button point (",x, y,"), offset=(", offsetXY[0],offsetXY[1],")")
                imouse.click(mouse.Button.left, 1)

            time.sleep(sleepAfter)
        else:
            UT_Print2Log('red', sys._getframe().f_lineno, "Failed to click on this button/point (",x, y,"), offset=(", offsetXY[0],offsetXY[1],")!!!!")

        return win32gui.GetForegroundWindow()
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, "\n" + todo, traceback.format_exc())   

def UT_FindChildWinds(wxs, hwnd, xhwndChild= None,wantedClass= None, wantedText= None):
    #FindChildWinds
    if not wxs.__contains__(hwnd):
        wxs[str(hwnd)] = {}

    c = 0
    checkedChilds = {}
    while True:
        UT_Print2Log('', c, hwnd, xhwndChild, wantedClass, wantedText)
        hwndChild = win32gui.FindWindowEx(hwnd, xhwndChild, wantedClass, wantedText)
        if hwndChild:
            if not wxs[str(hwnd)].__contains__(str(hwndChild)):
                UT_Print2Log('', "\t",hwnd, hwndChild, 'Class:[' + str(win32gui.GetClassName(hwndChild)) + ']  Text:['+  str(win32gui.GetWindowText(hwndChild)) + ']',"\n")
                wxs[str(hwnd)][str(hwndChild)] = {}
                checkedChilds[hwndChild] = 0
                c=0
            else:
                c +=1

        if c > 8:
            xhwndChild = None
            for xch in checkedChilds:
                if checkedChilds[xch] == 0:
                    xhwndChild = xch
                    checkedChilds[xch] = 1

            if not xhwndChild:
                break

    #for hwndChild in wxs[str(hwnd)]:
    #    UT_FindChildWinds(wxs[str(hwnd)][hwndChild], hwndChild, None, wantedClass, wantedText)

def UT_WindowsAlign(scale=1, findWinTitle=""):  
    curDisplay = None
    UT_Print2Log('', "Windows Align for:", findWinTitle)

    for m in get_monitors():
        curDisplay = m

        wins = []
        winhandles = []
        #for title in pygetwindow.getAllTitles():
        for winx in pygetwindow.getAllWindows():
            #<Win32Window left="-7", top="-7", width="2575", height="1407", title="tmp6.py - Visual Studio Code [Administrator]">
            if winx.title:
                UT_Print2Log('','\t', winx)
                if re.match(r'.*({})'.format(findWinTitle), winx.title, re.I):  
                    try:       
                        for win in pygetwindow.getWindowsWithTitle(winx.title):
                            if not win in winhandles:
                                winhandles.append(win)
                                UT_Print2Log('','\t  ----', winx.left >= curDisplay.x and winx.left <= curDisplay.x + curDisplay.width, "\n")
                                if winx.left >= curDisplay.x and winx.left <= curDisplay.x + curDisplay.width:
                                    wins.append([win, winx.title])
                                break
                    except:
                        UT_Print2Log('red', "\nUT_WindowsAlign:\n", traceback.format_exc())

        if len(wins):
            UT_Print2Log('',"\nTo align:", wins)
            UT_Print2Log('',curDisplay)
            dwidth  = 500
            dheight = 500
            dx = int(80*scale)
            dy = int(30*scale)
            x0 = 100
            y0 = 50

            taskbarHeight = 0
            try:
                monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))
                monitor_area = monitor_info.get("Monitor")
                work_area = monitor_info.get("Work")
                taskbarHeight = monitor_area[3] - work_area[3]
                UT_Print2Log('',"\nThe taskbar height is {}.".format(taskbarHeight))

            except:
                pass

            try:
                dwidth  = curDisplay.width  - x0*2 - (len(wins) - 1)*dx
                dheight = curDisplay.height - y0*2 - (len(wins) - 1)*dy - taskbarHeight
                y0 = 50 + (len(wins) - 1)*dy
                for win in wins:
                    UT_Print2Log('','\t'+ str(win) +' move to:',(x0 + curDisplay.x, y0 + curDisplay.y) , "resize to",(dwidth, dheight),win[1])
                    win[0].moveTo(x0 + curDisplay.x, y0 + curDisplay.y)
                    win[0].resizeTo(dwidth, dheight)
                    x0 += dx
                    y0 -= dy
            except:
                UT_Print2Log('red',"\nUT_WindowsAlign:\n", traceback.format_exc()) 

            UT_Print2Log('','') 

def UT_ProcessInfo(processName):
    pids = psutil.pids()
    res = False
    for pid in pids:
        # UT_Print2Log('', pid)
        p = psutil.Process(pid)
        try:
            #UT_Print2Log('', p.name())
            if str(p.name()).upper() == str(processName).upper():
                UT_Print2Log('red', sys._getframe().f_lineno, '--- killing pid ', pid)
                UT_Print2Log('', os.popen('taskkill.exe /pid '+str(pid)))
                res = True  # 如果找到该进程则打印它的PID，返回true
                break
        except:
            pass

    return res  # 没有找到该进程，返回false


def UT_IsMouseOnRightPosition(mouseSetPoint=[], winScale= 1):
    good = 1
    try:
        if len(mouseSetPoint):
            imouse = mouse.Controller()
            x1 = int(mouseSetPoint[0]/winScale)
            y1 = int(mouseSetPoint[1]/winScale)
            imouse.position = (x1, y1)    #fit to a 100% of Display Scale, and place the mouse at a correct point

            n = 0
            while True:
                n +=1 
                try:           
                    posx = win32api.GetCursorPos()
                    if x1 != posx[0] or y1 != posx[1]:       
                        if n < 5:                     
                            e = win32api.SetCursorPos((x1,y1))
                            time.sleep(0.1)
                        else:
                            good = 0
                            break
                    else:
                        break
                except:
                    good = 0
                    UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())
                    break
    except:
        good = 0
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

    return good

def UT_WindowRectGet(hwnd):
    try:
        f = ctypes.windll.dwmapi.DwmGetWindowAttribute
    except:
        f = None
    if f:
        try:
            rect = ctypes.wintypes.RECT()
            DWMWA_EXTENDED_FRAME_BOUNDS = 9
            f(ctypes.wintypes.HWND(hwnd),
            ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
            ctypes.byref(rect),
            ctypes.sizeof(rect)
            )
            return rect.left, rect.top, rect.right, rect.bottom
        except:
            UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())
    
def UT_WinFocusOn(hwnd=None):    
    try:           
        l, t, r, b = UT_WindowRectGet(hwnd)
        UT_Print2Log('', sys._getframe().f_lineno, ".... SetForegroundWindow:",hwnd, l, t, r, b)                    
        win32gui.SetForegroundWindow(hwnd)

        x = l + 2
        y = t + 2
        #win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(x/SCREEN_WIDTH*65535.0), int(y/SCREEN_HEIGHT*65535.0))
        win32api.SetCursorPos((x,y))
        UT_Print2Log('', sys._getframe().f_lineno)
        #------ This will lock the mouse sometimes
        #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        #win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0) 
        #------ This will lock the mouse sometimes
        imouse = mouse.Controller()   
        imouse.click(mouse.Button.left, 1)
        UT_Print2Log('', sys._getframe().f_lineno)       
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

def UT_ClipboardPaste(text, delstr=False, mouseSetPoint=[]):
    good = 1
    if len(mouseSetPoint):
        good = UT_IsMouseOnRightPosition(mouseSetPoint)

    if not good:
        return False

    try:
        UT_ClipboardInertText(text)
        ctr = keyboardX.Controller()
        if delstr:
            with ctr.pressed(keyboardX.Key.ctrl,"a"):
                pass
            with ctr.pressed(keyboardX.Key.delete):
                pass

        #UT_Print2Log('', ".. paste text from clipboard:", win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)) dengmmeDDY#$JABIL22xSHANGHAI218.107.14.4
        with ctr.pressed(keyboardX.Key.ctrl,"v"):            
            pass
        WinUtils['has_content_in_clipboard'] = 1  
        return True 
    except:
        win32clipboard.CloseClipboard()
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())
        return False
    
def UT_ClipboardInertText(text=""):
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()
    except:
        win32clipboard.CloseClipboard()
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())    

def UT_ClipboardEmpty():
    if WinUtils['has_content_in_clipboard']:
        UT_Print2Log('blue', sys._getframe().f_lineno, "clean up clipboard!!")
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.CloseClipboard()
        WinUtils['has_content_in_clipboard'] = 0

def UT_HideConsoleWindow(myfile=""):
    try:
        myfile = re.sub(r'.*(\\|\/)','', myfile)
        UT_Print2Log("\n", sys._getframe().f_lineno, "main file: ",myfile,"\n")
        if re.match(r'.*\.py$',myfile,re.I):
            return
            
        whnd = win32gui.FindWindowEx(0,0,'ConsoleWindowClass',None)
        title  = win32gui.GetWindowText(whnd)
        UT_Print2Log(whnd,title)
        if title.endswith(myfile) or re.match(r'.*'+ title +'',myfile,re.I):
            win32gui.ShowWindow(whnd, win32con.SW_HIDE)
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

def UT_GetInfoAppRoot():
    root_folder = re.sub(r'\\','/',os.path.abspath(os.path.dirname(__file__)))
    print("\033[0;37;40m'\nroot:", root_folder)  
    sys.path.append(root_folder)  
    os.chdir(root_folder)    

    pcName = os.environ['COMPUTERNAME']
    curUser= getpass.getuser()
    print("getcwd:",os.getcwd() + "\nDevice Name:", pcName)
    print("Current Login User:", getpass.getuser())

    return root_folder, pcName, curUser

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
    WinUtils['win_logs'].append([time.time(), args, icolor])

def UT_LogSave2HTML(logFile=''):
    if not len(WinUtils['win_logs']) or not logFile:
        return

    logsX = {}
    for log in WinUtils['win_logs']:
        ss = []
        for i in range(1,len(log[1])):
            obj = log[1][i]
            if(type(obj) == np.ndarray) or type(obj) == tuple or type(obj) == list or type(obj) == dict:
                ss.append(json.dumps(str(obj)))
            else:
                ss.append(str(obj))

        t = time.strftime("%Y-%m-%d %H:%M",time.localtime(log[0]))
        if not logsX.__contains__(t):
            logsX[t] = []

        textList = []
        for s in re.split(r'\n', "\t".join(ss)):
            s1 = re.sub(r'^\t','    ',s)
            s2 = re.sub(r'^\s+','', s1)
            pleft = 2
            if len(s2) < len(s1):
                pleft += 15 * (len(s1) - len(s2))
            if not s2:
                s2 = "<br />"
            textList.append("<div style='padding-left:"+str(pleft)+"px' >" + s2 + "</div>")        
        logsX[t].append("<div class='time "+ t +"' style='color:"+log[2]+";padding-left:20px' title='" + time.strftime("%Y-%m-%d %H:%M:%S %z",time.localtime(log[0])) + "' >" +
                             "\n".join(textList) +\
                        "</div>")

    logs = []
    for t in sorted(logsX.keys()):
        logs.append("<p>\n<div class='times' style='font-weight:bold;background:#E0E0E0;padding:8px'>"+ t +"</div>\n" + "\n".join(logsX[t]) + '\n</p>')
    
    if len(logs): 
        folder = os.path.dirname(logFile)
        #UT_Print2Log('red', sys._getframe().f_lineno,folder)
        UT_FolderCreate(folder)      
        UT_FileSave("\n\n".join(logs), logFile, format='string')

def UT_JsonFileRead(filepath= ""):
    try:
        if filepath:
            return json.loads(UT_FileOpen(filepath, format='string'))
        else:
            UT_Print2Log('red', sys._getframe().f_lineno, "File path is invalid!!")
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())
    
    return None

def UT_JsonFileSave(filepath= "", fdata=None):
    try:       
        UT_FileSave(json.dumps(fdata, cls=NumpyEncoder),filepath, format='string')
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

def UT_FileOpen(filepath, format='bytes'):    
    UT_Print2Log('', "\t.... Open file:",filepath)
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
    UT_Print2Log('', "\t.... Save to file:",filepath)
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

def UT_PrintStruct(struc, indent=0):
    if isinstance(struc, dict):
        UT_Print2Log('', '  '*indent+'{')
        for key,val in struc.items():
            if isinstance(val, (dict, list, tuple)):
              print ('  '*(indent+1) + str(key) + '=> ')
              UT_PrintStruct(val, indent+2)
            else:
              UT_Print2Log('', '  '*(indent+1) + str(key) + '=> ' + str(val))
        UT_Print2Log('', '  '*indent+'}')
        
    elif isinstance(struc, list):
        UT_Print2Log('', '  '*indent + '[')
        for item in struc:
            UT_PrintStruct(item, indent+1)
        UT_Print2Log('', '  '*indent + ']')
      
    elif isinstance(struc, tuple):
        UT_Print2Log('', '  '*indent + '(')
        for item in struc:
          UT_PrintStruct(item, indent+1)
        UT_Print2Log('', '  '*indent + ')')
        
    else: 
        print ('  '*indent + str(struc))

