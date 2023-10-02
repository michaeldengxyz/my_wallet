#Pyhton 3.x
# -*- coding: UTF-8 -*-
#rev 0.1
#common subroutines for image processing functions

import sys, re, traceback
import base64
import time
import win32ui,win32gui,win32con

from io import BytesIO
from PIL import Image

from mypyUtils import UT_Print2Log, UT_UsedTime

def UTI_ImageFromBase64String(base64_str, image_path=None):
    #base64_to_image
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    if image_path:
        img.save(image_path)
    return img

def UTI_ScreenShotXY(width=0,height=0,xSrc=None,ySrc=None, debug=True):
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
