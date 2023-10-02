#Pyhton 3.x
# -*- coding: UTF-8 -*-
#rev 0.1
#common subroutines for/on UI

import time, sys, re
import traceback
from tkinter import Label, Toplevel, Canvas, Frame, Button, filedialog
from tkinter import CENTER,FLAT,E,W,N,S,TOP,LEFT,X,BOTH,RIGHT,Y,ARC
import tkinter.font as tf

from ttkwidgets.frames import Balloon, Tooltip
import ctypes
from screeninfo import get_monitors
from mypyUtils import UT_Print2Log, UT_GetColors, UT_XYminMax
from mypyUtilsImage import UTI_ScreenShotXY
import win32gui,win32con,win32api
import threading

WinUtilsUI = {}
WinUtilsUI['display_scale'] = []
WinUtilsUI['display_sizes'] = []
WinUtilsUI['Win_last_geometry'] = ""
WinUtilsUI['WinDefaultFont_configure'] = None
WinUtilsUI['WinDefaultFont_last_fontsize'] = 0
WinUtilsUI['WinDefaultFont_original_fontsize'] = 0
WinUtilsUI['Toplevel_WinResize'] = []
WinUtilsUI['toplevel_lines'] = []
WinUtilsUI['toplevel_Rect'] = []
WinUtilsUI['toplevel_ClassToplevelMessage'] = None

def UI_SetFolder(self_folder):
    return filedialog.askdirectory(initialdir = self_folder)

def UI_CapLockStatus(event,e=None):
    #UT_Print2Log('', event,':',e)   
    if win32api.GetKeyState(win32con.VK_CAPITAL) == 1:
        #UT_Print2Log('',"CAPS Lock is on.") 
        if e:
            e.configure(background='#FFFF66')
        
    elif win32api.GetKeyState(win32con.VK_CAPITAL) == 0:
        #UT_Print2Log('',"CAPS Lock is off.")
        if e:
            e.configure(background='#FFFFFF')

def UI_WinWidgetRemove(wid=None, act=1):
    try:
        for item in wid.winfo_children():
            #print('', "-"*act,item)
            if item.winfo_children():
                UI_WinWidgetRemove(wid=item,act=act+1)
            try:
                item.destroy()
            except:
                pass
    except:
        pass
    
def UI_WidgetEntryShow(event,e=None,ishow=''):
    e.config(show=ishow)

def UI_WinGeometry(mainWin=None, p='+0+0',fromx=''):
    #relocate main window
    try:
        #UT_Print2Log('', sys._getframe().f_lineno, 'WmainWin geometry:', p, fromx)
        mainWin.geometry(p)
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

def UI_WidgetBalloon(wid, msg, title=""):
    if title:
        return Tooltip(wid, title, msg)
    else:
        return Tooltip(wid, "Tip", msg)

def UI_DeviceDisplayInfoGet(checkScale=True):
    mm={}

    info = {
        'display_scale': [],
        'display_sizes': [],
        'FullScreen':[],
        'FullScreenSize':[]
    }
    i = 0

    for m in get_monitors(): 
        #m   Monitor(x=0, y=0, width=2560, height=1440, width_mm=700, height_mm=390, name='\\\\.\\DISPLAY1') 
        try:
            i +=1
            UT_XYminMax(mm,[m.x,m.y, m.x + m.width, m.y + m.height])
            if checkScale:                        
                tl = Toplevel()
                tl.wm_attributes('-topmost',1) 
                tl.geometry('+'+ str(m.x) +'+' + str(m.y))
                label = Label(tl, text="get DPI ...", justify=LEFT, relief=FLAT,pady=3,padx=3, anchor='w')
                label.pack(side=TOP, fill=X)
                tl.update()
                time.sleep(1)
                # Set process DPI awareness
                try:
                    ctypes.windll.shcore.SetProcessDpiAwareness(1)
                except:
                    ctypes.windll.user32.SetProcessDPIAware()
                # Create a tkinter window
                # Get the reported DPI from the window's HWND
                dpi = ctypes.windll.user32.GetDpiForWindow(tl.winfo_id())
                # Print the DPI
                iscale = int(dpi/96*1000)/1000
                UT_Print2Log('', ".. monitors",i,m,dpi,iscale)        
                info['display_scale'].append([m.x, m.x + m.width, iscale, re.sub(r'\\*\.*\\*','',str(m.name)), m.width, m.height])
                info['display_sizes'].append(m)
                tl.destroy()
        except:
            UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

    if checkScale:
        WinUtilsUI['display_scale'] = info['display_scale']
        WinUtilsUI['display_sizes'] = info['display_sizes']

    
    if i > 0:
        info['FullScreen'] = [
            mm['xmax'] - mm['xmin'],
            mm['ymax'] - mm['ymin'],
            mm['xmin'],
            mm['ymin']
        ]
        print("..",'FullScreen',info['FullScreen'])

        info['FullScreenSize'] = [
            mm['xmax'] - mm['xmin'],
            mm['ymax'] - mm['ymin'],
            mm['xmin'],
            mm['ymin']
        ]    
        print("..",'FullScreenSize',info['FullScreenSize'])

    return info

def UI_DeviceDisplayScale(x=0, y=0, needScaled=False):
    scale = 1
    
    if needScaled and len(WinUtilsUI['display_scale']):
        m = ''
        UT_Print2Log('', '\nMonitorScale x=', x, '\ndisplay_scale=', WinUtilsUI['display_scale'])
        for dp in WinUtilsUI['display_scale']:
            try:
                if x >= dp[0] and x < dp[1]:
                    scale = dp[2]
                    m = str(dp[3])
                    break
            except:
                pass
        UT_Print2Log('', sys._getframe().f_lineno, m +' Scale=',scale, "\n")

    return scale

def UI_WinFontSet(force=False, mainWin=None):
    if not force and (WinUtilsUI['Win_last_geometry'] == mainWin.geometry()):
        return

    WinUtilsUI['Win_last_geometry'] = mainWin.geometry()
    ges = re.split(r'\+|x', mainWin.geometry())
    UT_Print2Log('','\nmain.geometry()=' + WinUtilsUI['Win_last_geometry'], ges)
    scale = UI_DeviceDisplayScale(x=int(ges[2]), needScaled=True)

    # Creating a Font object of "TkDefaultFont"
    defaultFont = tf.nametofont("TkDefaultFont")
    f = defaultFont.configure()
    WinUtilsUI['WinDefaultFont_configure'] = f
    UT_Print2Log('','Win Scale=' + str(scale), "\nCurrent WinDefaultFont=",f) #{'family': 'Segoe UI', 'size': 9, 'weight': 'normal', 'slant': 'roman', 'underline': 0, 'overstrike': 0} 9
    
    if not WinUtilsUI['WinDefaultFont_last_fontsize']:
        WinUtilsUI['WinDefaultFont_last_fontsize'] = f['size']

    if not WinUtilsUI['WinDefaultFont_original_fontsize']:
        WinUtilsUI['WinDefaultFont_original_fontsize'] = f['size']

    fsize = WinUtilsUI['WinDefaultFont_original_fontsize']
    if scale > 1:
        #UT_Print2Log('', tf.families())
        fsize = int(WinUtilsUI['WinDefaultFont_original_fontsize']*scale + 0.5)

    UT_Print2Log('', 'To set Font.size=', fsize, ', last_fontsize=', WinUtilsUI['WinDefaultFont_last_fontsize'])
    if not (WinUtilsUI['WinDefaultFont_last_fontsize'] == fsize):
        UT_Print2Log('', 'Set defaultFont.size=', fsize)
        defaultFont.configure(size= fsize)
        fontType = tf.Font(size= fsize)
        UI_WidgetFontSet(wid=mainWin, fontType=fontType)
        WinUtilsUI['WinDefaultFont_last_fontsize'] = fsize

        defaultFont = tf.nametofont("TkDefaultFont")
        f = defaultFont.configure()
        WinUtilsUI['WinDefaultFont_configure'] = f

    elif force:
        fontType = tf.Font(size= fsize)
        UI_WidgetFontSet(wid=mainWin, fontType=fontType)

def UI_WidgetFontSetAtPoint(wid=None, widName="entry", point=[]):
    try:
        scale = UI_DeviceDisplayScale(x=point[0], needScaled=True)
        fsize = int(WinUtilsUI['WinDefaultFont_original_fontsize']*scale + 0.5)
        fontType = tf.Font(size= fsize)
        UT_Print2Log('blue', 'WidgetFontSetAtPoint:',wid, widName, point, fsize, scale)
        UI_WidgetFontSet(wid=wid, fontType=fontType, widName=widName)   
    except:
         UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

def UI_WidgetFontSet(wid=None, fontType=None, widName="entry", act=1):
    if not (wid and widName):
        return
    try:
        for item in wid.winfo_children():
            #UT_Print2Log('', "-"*act,item)
            try:
                if widName == 'all':
                    item.configure(font=fontType)
                elif re.match(r'.*\!{}\d*$'.format(widName),str(item),re.I):                
                    item.configure(font=fontType)
                    #UT_Print2Log('', "+"*act,item, fontType)
            except:
                pass
            
            if item.winfo_children():
                UI_WidgetFontSet(wid=item, fontType=fontType, widName=widName, act=act+1)
    except:
        pass

def UI_WinWidgetState(wid=None, state="normal", widName="entry", act=1):
    if not (wid and widName):
        return
    try:
        for item in wid.winfo_children():
            #UT_Print2Log('', "-"*act,item)
            if re.match(r'.*\!{}\d*$'.format(widName),str(item),re.I):
                item.configure(state=state)

            if item.winfo_children():
                UI_WinWidgetState(wid=item, state=state, widName=widName, act=act+1)
    except:
        pass

def UI_WinResizeRequire(sizes=[], xys=[], fgcolor='red', msg='', bgColor= 'yellow'):
    UI_WinResizeRequireDEL()

    try:
        x1 = xys[0] - 1 
        y1 = xys[1] - 1
        x2 = xys[0] + sizes[0] + 1
        y2 = xys[1] + sizes[1] + 1

        try:                                                #x,y,width,height,color,notAppend=False  
            WinUtilsUI['Toplevel_WinResize'].append(UI_ToplevelLine(x1,y1,sizes[0]+2,1,fgcolor, notAppend=True))  #0 top
            WinUtilsUI['Toplevel_WinResize'].append(UI_ToplevelLine(x1,y2,sizes[0]+2,1,fgcolor, notAppend=True))  #1 bottom
            WinUtilsUI['Toplevel_WinResize'].append(UI_ToplevelLine(x1,y1,1,sizes[1]+2,fgcolor, notAppend=True))  #2 left
            WinUtilsUI['Toplevel_WinResize'].append(UI_ToplevelLine(x2,y1,1,sizes[1]+2,fgcolor, notAppend=True))  #3 right

            tl = Toplevel()
            tl.geometry('+'+ str(x1) +'+' + str(int(y1 + sizes[1]/2 - 22*3)))
            
            font_type = None 
            try:
                font_type = tf.Font(family="Lucida Grande", size=20)
            except:
                pass
            
            frm = Frame(tl)
            frm.pack(side=TOP, fill=X)

            label = Label(frm, text=msg, 
                            justify=LEFT, relief=FLAT,pady=3,padx=3, anchor='w', bg=bgColor, fg=fgcolor, font=font_type)
            label.pack(side=LEFT, fill=X)
            
            UI_ClassButtonPack(options={
                'frame':frm,
                'side':RIGHT,
                'fill':Y,
                'fg': "#FFFFFF",
                'bg':'#000000',
                'expand':True,
                'anchor':'center',
                'justify':CENTER,
                'text':"Click me\nif OK",                  
                'width':10,
                'command': UI_WinResizeRequireDEL
            })

            tl.wm_attributes('-topmost',1)
            tl.overrideredirect(1)
            WinUtilsUI['Toplevel_WinResize'].append([tl,])
        except:
            UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

def UI_WinResizeRequireDEL():
    try:
        #UT_Print2Log('', WinUtilsUI['Toplevel_WinResize'])
        if len(WinUtilsUI['Toplevel_WinResize']):
            for tl in WinUtilsUI['Toplevel_WinResize']:
                tl[0].destroy()

        WinUtilsUI['Toplevel_WinResize'] = []
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

def UI_ToplevelLine(x,y,width,height,color,notAppend=False):
    tl = Toplevel()    
    tl.wm_attributes('-topmost',1)

    canvas = Canvas(tl,
            width = width,
            height= height,
            bg= color,
            relief=FLAT,
            bd = 0,
            )
    canvas.configure(highlightthickness = 0)
    canvas.pack()

    tl.geometry('+'+ str(x) +'+' + str(y))
    tl.overrideredirect(1)

    if notAppend:
        return [tl,canvas]
    else:
        WinUtilsUI['toplevel_lines'].append([tl,canvas])   

def UI_ToplevelLineDEL():
    if len(WinUtilsUI['toplevel_lines']):
        for tl in WinUtilsUI['toplevel_lines']:
            try:
                tl[0].destroy()
            except:
                pass
    WinUtilsUI['toplevel_lines'] = []

def UI_ToplevelRect(sizes, xys, icolor='red', isClosed=False):
    try:
        x1 = int(xys[0] - 1)
        y1 = int(xys[1] - 1)
        x2 = int(xys[0] + sizes[0] + 1)
        y2 = int(xys[1] + sizes[1] + 1)

        if len(WinUtilsUI['toplevel_Rect']):
            UI_ToplevelRectShow(isShow=True, xy=[x1,y1,x2,y2],sizes=sizes, icolor=icolor)
            return

        try:
            UI_ToplevelRectDEL()
                                                       #x,y,width,height,color,notAppend=False  
            WinUtilsUI['toplevel_Rect'].append(UI_ToplevelLine(x1,y1,sizes[0]+2,1,icolor, notAppend=True))  #0 top
            WinUtilsUI['toplevel_Rect'].append(UI_ToplevelLine(x1,y2,sizes[0]+2,1,icolor, notAppend=True))  #1 bottom

            WinUtilsUI['toplevel_Rect'].append(UI_ToplevelLine(x1,y1,1,sizes[1]+2,icolor, notAppend=True))  #2 left
            WinUtilsUI['toplevel_Rect'].append(UI_ToplevelLine(x2,y1,1,sizes[1]+2,icolor, notAppend=True))  #3 right
        except:
            UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

def UI_ToplevelRectHide():
    UI_ToplevelRectShow(isShow=False)

def UI_ToplevelRectShow(isShow=True, xy=[],sizes=[],icolor='red'):
    if len(WinUtilsUI['toplevel_Rect']):
        if isShow:
            WinUtilsUI['toplevel_Rect'][0][1].configure(width= sizes[0]+2, bg=icolor)   #canvas
            WinUtilsUI['toplevel_Rect'][0][0].geometry('+'+ str(xy[0]) +'+' + str(xy[1])) #toplevel
            WinUtilsUI['toplevel_Rect'][0][0].deiconify() #toplevel

            WinUtilsUI['toplevel_Rect'][1][1].configure(width= sizes[0]+2, bg=icolor)   #canvas
            WinUtilsUI['toplevel_Rect'][1][0].geometry('+'+ str(xy[0]) +'+' + str(xy[3])) #toplevel
            WinUtilsUI['toplevel_Rect'][1][0].deiconify() #toplevel

            WinUtilsUI['toplevel_Rect'][2][1].configure(height= sizes[1]+2, bg=icolor)   #canvas
            WinUtilsUI['toplevel_Rect'][2][0].geometry('+'+ str(xy[0]) +'+' + str(xy[1])) #toplevel
            WinUtilsUI['toplevel_Rect'][2][0].deiconify() #toplevel

            WinUtilsUI['toplevel_Rect'][3][1].configure(height= sizes[1]+2, bg=icolor)   #canvas
            WinUtilsUI['toplevel_Rect'][3][0].geometry('+'+ str(xy[2]) +'+' + str(xy[1])) #toplevel
            WinUtilsUI['toplevel_Rect'][3][0].deiconify() #toplevel
        else:
            for tl in WinUtilsUI['toplevel_Rect']:
                tl[0].withdraw()

def UI_ToplevelRectDEL():
    if len(WinUtilsUI['toplevel_Rect']):
        for tl in WinUtilsUI['toplevel_Rect']:
            tl[0].destroy()
    WinUtilsUI['toplevel_Rect'] = []

def UI_WidgetRectGET(widget=None):
    rect = []
    if widget:        
        try:
            rect = win32gui.GetWindowRect(widget.winfo_id())
            #left top right bottom (18, 78, 522, 382)
        except:
            print(traceback.format_exc())

    return rect

class UI_ClassSnapshotMask():
    def __init__(self,):  
        self.displays_info = UI_DeviceDisplayInfoGet(checkScale=False)        
        self.MaskInit()

    def Reset(self):
        self.mouse_start_points = []
        self.mouse_selected_box = []
        self.Toplevel_SnapShotMasks = []
        self.snapshot_start = False
        self.tl_mask = None

    def MaskInit(self):
        self.Reset()        
        self.MaskClose()

        x0 = self.displays_info['FullScreenSize'][2]
        y0 = self.displays_info['FullScreenSize'][3]
        x1 = 100
        y1 = 100
        x2 = 105
        y2 = 105
        x3 = x0 + self.displays_info['FullScreenSize'][0]
        y3 = y0 + self.displays_info['FullScreenSize'][1]

        self.MaskReconfig(x0,y0,x1,y1,x2,y2,x3,y3)
        self.snapshot_start = True
        self.mouse_selected_box = []

    def MaskReconfig(self, x0,y0,x1,y1,x2,y2,x3,y3):
        if x1 > x2:
            xx = x1
            x1 = x2
            x2 = xx
        if y1 > y2:
            yy = y1
            y1 = y2
            y2 = yy

        mask_boxes = [
            [[x1, y1, x2, y2], 0.05],
            [[x0, y0, x3, y1], 0.5],
            [[x0, y1, x1, y2], 0.5],
            [[x2, y1, x3, y2], 0.5],
            [[x0, y2, x3, y3], 0.5]
        ]

        self.mouse_selected_box = [x1, y1, x2, y2]
        #print(self.mouse_selected_box)
        lenx = len(self.Toplevel_SnapShotMasks)
        i = 0
        for bb in mask_boxes:        
            b = bb[0]
            width = b[2] - b[0]
            height= b[3] - b[1]
            left  = b[0]
            top   = b[1]

            #if width and height:
            geo = str(width) + 'x' + str(height) + '+' + str(left) + '+' + str(top)

            if not lenx:
                tl = Toplevel(bg='#E0E0E0')   
                tl.title("Snap Shot Mask") 
                tl.wm_attributes('-topmost',1)
                tl.attributes('-alpha', bb[1])
                UI_WinGeometry(mainWin=tl, p=geo,fromx='')
                tl.overrideredirect(1)
                tl.configure(cursor='tcross')  #arrow
                self.Toplevel_SnapShotMasks.append([tl, bb])
            else:                
                if not bb[1] == self.Toplevel_SnapShotMasks[i][1]:
                    UI_WinGeometry(mainWin= self.Toplevel_SnapShotMasks[i][0], p=geo,fromx='')

            i +=1

    def MaskClose(self):
        try:
            for tl in self.Toplevel_SnapShotMasks:
                try:
                    tl[0].configure(cursor='arrow')
                    tl[0].destroy()
                except:
                    pass
            self.Toplevel_SnapShotMasks = []
            self.snapshot_start = False
        except:
            pass
    
    def OnMouseClick(self, x, y, button, pressed):
        #print("OnMouseClick", x, y, button, pressed, ", if-", self.snapshot_start and re.match(r'.*left',str(button),re.I), ', self.snapshot_start=', self.snapshot_start)
        if self.snapshot_start and re.match(r'.*left',str(button),re.I):
            if pressed:
                #print("OnMouseClick - mouse_start_points", x, y, button, pressed)
                if not len(self.mouse_start_points):  #mouse down to first point
                    self.mouse_start_points = [x,y]
                #print(self.mouse_start_points)
        else:
            self.mouse_start_points = []

        if not pressed:            
            self.mouse_start_points = []    
            if re.match(r'.*left',str(button),re.I):
                self.Snapshot()  

    def OnMouseMove(self, x, y, button, pressed):
        #print("OnMouseMove", x, y, button, pressed, self.mouse_start_points)
        if self.snapshot_start and len(self.mouse_start_points) and re.match(r'.*left',str(button),re.I) and pressed:
            dx = abs(x - self.mouse_start_points[0])
            dy = abs(y - self.mouse_start_points[1])
            #print("\tdx, dy=", dx, dy)
            if dx or dy:
                x0 = self.displays_info['FullScreenSize'][2]
                y0 = self.displays_info['FullScreenSize'][3]
                x1 = self.mouse_start_points[0]
                y1 = self.mouse_start_points[1]
                x2 = x
                y2 = y
                x3 = x0 + self.displays_info['FullScreenSize'][0]
                y3 = y0 + self.displays_info['FullScreenSize'][1] 

                self.MaskReconfig(x0,y0,x1,y1,x2,y2,x3,y3)


    def Snapshot(self):
        if len(self.mouse_selected_box):
            #print('self.mouse_selected_box=', self.mouse_selected_box)
            self.MaskClose()
            time.sleep(0.1)
            self.im_PIL,self.im_err = UTI_ScreenShotXY(
                width = self.mouse_selected_box[2] - self.mouse_selected_box[0],
                height= self.mouse_selected_box[3] - self.mouse_selected_box[1],
                xSrc  = self.mouse_selected_box[0],
                ySrc  = self.mouse_selected_box[1]
            )
            self.Reset()
            self.im_PIL.show()

class UI_ClassSnapshotMaskFullscreen():
    def __init__(self, CallbackAtEnd=None):  
        self.CallbackAtEnd = CallbackAtEnd
        self.displays_info = UI_DeviceDisplayInfoGet(checkScale=False)        
        self.MaskInit()

    def Reset(self):
        self.mouse_start_points = []
        self.mouse_selected_box = []
        self.snapshot_start = False
        self.snapshot_end   = False
        self.tl_mask = None

    def MaskInit(self):
        self.Reset()
        self.snapshot_start = True
        self.MaskClose()
        
        x0 = self.displays_info['FullScreenSize'][2]
        y0 = self.displays_info['FullScreenSize'][3]
        x3 = x0 + self.displays_info['FullScreenSize'][0]
        y3 = y0 + self.displays_info['FullScreenSize'][1]

        self.x0 = x0
        self.y0 = y0

        geo = str(x3 - x0) + 'x' + str(y3-y0) + '+' + str(x0) + '+' + str(y0)
        tl = Toplevel(bg='#E0E0E0')   
        tl.title("Snap Shot Mask") 
        tl.wm_attributes('-topmost',1)
        tl.attributes('-alpha', 0.05)
        UI_WinGeometry(mainWin=tl, p=geo,fromx='')
        tl.overrideredirect(1)
        tl.configure(cursor='tcross')

        tl.bind("<ButtonRelease-1>",self.MouseUpLeft)
        tl.bind("<Button-1>",self.MouseDownLeft)
        tl.bind("<B1-Motion>",self.MouseMoveLeft)

        self.tl_mask = tl

    def MouseUpLeft(self, event):
        self.OnMouseClick(event.x + self.x0, event.y + self.y0, 'button.left', False)

    def MouseDownLeft(self, event):
        self.OnMouseClick(event.x + self.x0, event.y + self.y0, 'button.left', True)

    def MouseMoveLeft(self, event):
        self.OnMouseMove(event.x + self.x0, event.y + self.y0, 'button.left', True)

    def MaskClose(self):        
        UI_ToplevelRectHide()
        try:
            if self.tl_mask:
                self.tl_mask.configure(cursor='arrow')
                self.tl_mask.destroy()
                self.tl_mask = None
        except:
            pass
    
    def OnMouseClick(self, x, y, button, pressed):
        if self.snapshot_start and re.match(r'.*left',str(button),re.I):
            if pressed:
                if not len(self.mouse_start_points):  #mouse down to first point
                    self.mouse_start_points = [x,y]
        else:
            self.mouse_start_points = []

        if not pressed:            
            self.mouse_start_points = []    
            if re.match(r'.*left',str(button),re.I):
                self.Snapshot()  

    def OnMouseMove(self, x, y, button, pressed):
        if self.snapshot_start and len(self.mouse_start_points) and re.match(r'.*left',str(button),re.I) and pressed:
            x0 = x
            x1 = x
            if self.mouse_start_points[0] < x:
                x0 = self.mouse_start_points[0]
            else:
                x1 = self.mouse_start_points[0]
            y0 = y
            y1 = y
            if self.mouse_start_points[1] < y:
                y0 = self.mouse_start_points[1]
            else:
                y1 = self.mouse_start_points[1]

            self.mouse_selected_box = [x0, y0, x1, y1]

            UI_ToplevelRect(
                [abs(x - self.mouse_start_points[0]), abs(y - self.mouse_start_points[1])], 
                [x0 , y0]
            )

    def Snapshot(self):
        if len(self.mouse_selected_box):
            self.MaskClose()
            self.snapshot_end   = True
            self.CallbackAtEnd()
            
            """
            time.sleep(0.1)
            self.im_PIL,self.im_err = UTI_ScreenShotXY(
                width = self.mouse_selected_box[2] - self.mouse_selected_box[0],
                height= self.mouse_selected_box[3] - self.mouse_selected_box[1],
                xSrc  = self.mouse_selected_box[0],
                ySrc  = self.mouse_selected_box[1]
            )
            self.Reset()
            self.im_PIL.show()
            """

class UI_ClassToplevelMessage():
    def __init__(self, msg="", bgColor="yellow", fgColor="red", pos=[], tshow=3, withCursor=True):
        if tshow:              
            font_type = None 
            scale = 1
            self.tl = None
            dy = 0
            if withCursor:
                dy = 20
                if WinUtilsUI['toplevel_ClassToplevelMessage']:
                    try:
                        WinUtilsUI['toplevel_ClassToplevelMessage'].destroy()
                    except:
                        pass
            try:
                if len(pos):
                    scale = UI_DeviceDisplayScale(x=pos[0], needScaled=True)             
                font_type = tf.Font(family="Lucida Grande", size=int(10*scale))
            except:
                UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

            try:
                self.tl = Toplevel()
                WinUtilsUI['toplevel_ClassToplevelMessage'] = self.tl

                if not len(pos):
                    pos = win32api.GetCursorPos()
                self.tl.geometry('+'+ str(pos[0]) +'+' + str(pos[1] + dy))

                label = Label(self.tl, text=msg, justify=LEFT, relief=FLAT,pady=3,padx=3, anchor='w', bg=bgColor, fg=fgColor, font=font_type)
                label.pack(side=TOP, fill=X)

                self.tl.wm_attributes('-topmost',1)
                self.tl.overrideredirect(1)
                self.tl.update()
            except:
                UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

            if self.tl:
                p = threading.Timer(tshow, self.Close)
                p.start()

    def Close(self):
        try:
            self.tl.destroy()
        except:
            pass


class UI_ClassSeparatorGrid:
    def __init__(self,frm,row=0,col=0,txt='|',fg='#FFFFFF',bg='#E0E0E0',p=[CENTER,FLAT,0,0]):
        self.label = Label(frm, 
                            text=txt, 
                            justify=p[0], 
                            relief=p[1],
                            pady=p[2],
                            padx=p[3],
                            fg=fg,
                            bg=bg
                            )
        self.label.grid(
                    row=row,
                    column=col,
                    sticky=E+W+N+S,
                    pady=0,
                    padx=0,
                        )

class UI_ClassButtonPack:
    def __init__(self,options={}):
        self.opts = options
        self.options={
            'frame':None,
            'side':LEFT,
            'fill':X,
            'expand':False,
            'anchor':'n',
            'padx':3,
            'pady':3,


            'text':"",
            'fg': "blue",
            'bg':'#E0E0E0',
            'relief':FLAT,
            'justify':LEFT,
            'textpadx':3,
            'textpady':3,                    
            'activebackground':'#FFFF66',
            'highlightbackground':'#FFFF99',
            'width':0,
            'height':0,
            'command': None
        }

        for s in self.opts:
            if self.options.__contains__(s):
                self.options[s] = self.opts[s]

        self.b = Button(
                    self.options['frame'], 
                    text=self.options['text'], 
                    fg=self.options['fg'],
                    bg=self.options['bg'],
                    justify=self.options['justify'], 
                    relief=self.options['relief'],
                    padx=self.options['textpadx'],
                    pady=self.options['textpady'],                    
                    activebackground=self.options['activebackground'],
                    highlightbackground=self.options['highlightbackground'],
                    width=self.options['width'],
                    height=self.options['height'],
                    command=self.options['command']
                    )
        self.b.pack(
                side=self.options['side'],
                pady=self.options['pady'],
                padx=self.options['padx'],
                fill=self.options['fill'],
                expand = self.options['expand'],
                anchor  = self.options['anchor']
        )

        self.b.bind('<Motion>',self.iMotion)
        self.b.bind('<Leave>',self.iLeave)
        self.bg = self.options['bg']
        self.txt= self.options['text']             
        
    def iMotion(self,event):
        self.b.config(bg = '#FFFFF0')

    def iLeave(self,event):
        self.b.config(bg = self.bg)

class UI_ClassButtonGrid:
    def __init__(self,frm,row=0,col=0,cmd=None,txt='?',fg='blue',bg='#E0E0E0',
                    colspan=1, width = 0, msg=None, TexAnchor = CENTER,
                    p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',0,E+W+N+S,0,0]):

        if width:
            p[6] = width

        self.b = Button( frm, 
                    text=txt, 
                    fg=fg,
                    bg=bg,
                    justify=p[0], 
                    anchor= TexAnchor,
                    relief=p[1],
                    padx=p[2],
                    pady=p[3],                    
                    activebackground=p[4],
                    highlightbackground=p[5],
                    width=p[6],
                    command=cmd
                    )
        self.b.grid( row=row,
                column=col,
                sticky=p[7],
                pady=p[8],
                padx=p[9],
                columnspan=colspan
                )

        self.b.bind('<Motion>',self.iMotion)
        self.b.bind('<Leave>',self.iLeave)
        self.bg = bg 
        self.txt= txt
        self.row = row           
        
        if msg:                
            self.message = msg
            UI_WidgetBalloon(self.b,  msg)
        else:
            self.message = ""

    def iMotion(self,event):
        self.b.config(bg = '#FFFFF0')

    def iLeave(self,event):
        self.b.config(bg = self.bg)

class UI_ClassToplevelAlertOnFullScreen():
    def __init__(self, mainWin=None, mainWin_start=1, e_display=None, alert="", interval=15):
        UT_Print2Log('blue', 'UI_ClassToplevelAlertOnFullScreen initiating ...')

        self.alert_text=alert
        self.alert_interval = interval #minutes
        self.mainWin = mainWin
        self.mainWin_start = mainWin_start
        self.mainWin_display_status=e_display  #widget to display countdown time on main-window
        self.tl = None

        self.mainWin_default_fontfamily= "Microsoft YaHei UI Light"
        if WinUtilsUI['WinDefaultFont_configure']:
            self.mainWin_default_fontfamily = WinUtilsUI['WinDefaultFont_configure']['family']

    def run(self):
        UT_Print2Log('blue', 'UI_ClassToplevelAlertOnFullScreen running ...')

        lastcheck_old = ""
        tl = None
        label1 = None
        sleep_2next = 0
        lastPopTime = ""
        interval_refresh = 1 #seconds

        while True:
            if not self.mainWin:
                break

            myLocalm = time.localtime()        
            if sleep_2next > 0 and not ((myLocalm.tm_min == 59 and myLocalm.tm_sec == 59) or (myLocalm.tm_min == 0 and myLocalm.tm_sec == 0)) :
                sleep_2next -= interval_refresh
                try:
                    if self.mainWin_display_status:
                        self.mainWin_display_status.config(text= str(sleep_2next))
                    label1.configure(text=lastPopTime + ", refresh after " + str(sleep_2next) + ' seconds')
                    tl.update()
                except:
                    pass
            elif self.mainWin_start and not ((myLocalm.tm_min == 59 and myLocalm.tm_sec == 59) or (myLocalm.tm_min == 0 and myLocalm.tm_sec == 0)):                
                sleep_2next = (60-myLocalm.tm_min)*60 - myLocalm.tm_sec
            else:
                try:
                    lastPopTime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))             
                    sleep_2next = (60-myLocalm.tm_min)*60 - myLocalm.tm_sec
                    #UT_Print2Log('', myLocalm) #time.struct_time(tm_year=2021, tm_mon=6, tm_mday=29, tm_hour=9, tm_min=38, tm_sec=50, tm_wday=1, tm_yday=180, tm_isdst=0)
                    lastcheck = str(myLocalm.tm_year) + "_" + str(myLocalm.tm_mon) + "_" + str(myLocalm.tm_mday) + "_" + str(myLocalm.tm_wday) + "_" + str(myLocalm.tm_hour)
                    if (lastcheck != lastcheck_old):
                        lastcheck_old = lastcheck
                        if tl:
                            tl.destroy()

                        tl = Toplevel(bg='black')
                        tl.title("Time to get rest!")
                        tl.wm_attributes('-topmost',1) 
                        self.tl = tl       

                        tl.geometry('+0+0')
                        hwnd = win32gui.FindWindow(None, "Time to get rest!")
                        win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)
                        tl.overrideredirect(1)

                        font_type  = tf.Font(size=64, family='Microsoft YaHei UI Light')
                        font_type2 = tf.Font(size=20, family='Microsoft YaHei UI Light')

                        label1 = Label(tl, text= lastPopTime + ", refresh after " + str(sleep_2next) + ' seconds', justify=CENTER, relief=FLAT,pady=10,padx=10, bg='black', fg='white', font=font_type2)
                        label1.pack(side=TOP, fill=X)

                        label = Label(tl, text= self.alert_text, justify=CENTER, relief=FLAT,pady=10,padx=10, bg='black', fg='white', font=font_type)
                        label.pack(side=TOP, fill=BOTH, expand=True)
                        
                        wh = int(self.mainWin.winfo_screenheight()/3)  #200
                        canvas = Canvas(tl,
                                    width=wh,
                                    height=wh,
                                    bg="black",
                                    relief=FLAT,
                                    bd = 0,
                                    )
                        canvas.configure(highlightthickness = 0)
                        canvas.pack(side=TOP) 
                        canvas.bind('<Button-1>', self.Closed) 
                        UI_WidgetBalloon(canvas,  'Click to close this window!')
                        t1 = threading.Timer(1,self.Closed_delay, args=[canvas, wh])
                        t1.start()
                except:
                    pass
            #UT_Print2Log('', "ReminderCheckMeeting sleep", interval_refresh, " seconds")
            time.sleep(interval_refresh)

    def Closed_delay(self, canvas, wh):
        try:
            delay_sec   = 60*self.alert_interval
            delay_sec_o = delay_sec
            width = 5
            arc = canvas.create_arc(width,width,wh - width,wh - width,start=0,extent=360,outline='white',style=ARC,width=width)
            arc2= canvas.create_arc(width*2,width*2,wh - width*2,wh - width*2,start=0,extent=0,outline='green',style=ARC,width=width)
            txt = canvas.create_text(int(wh/2), int(wh/2), text=str(delay_sec), font=(self.mainWin_default_fontfamily, 20), fill='white')
            ts  = 0
            lastAngle2 = 0
            colors = UT_GetColors(n=300)
            n = 0
            while delay_sec > 0:                    
                angle=int(delay_sec/delay_sec_o*3600)/10
                angle2 = int(ts*360)/10
                if ts > 10:
                    ts = 0
                    lastAngle2 = 0
                try:
                    canvas.itemconfig(arc,extent=angle)
                    canvas.itemconfig(arc2,start=lastAngle2,extent=angle2, outline= colors[n])
                    canvas.itemconfig(txt,text=str(int(delay_sec)), fill=colors[n])
                    self.tl.update()
                    n+=1
                    if n >= len(colors):
                        n = 0
                except:
                    #UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())
                    break
                lastAngle2 = angle2
                time.sleep(0.2)
                delay_sec -= 0.2
                ts += 0.2
        except:
            #UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())
            pass

        self.Closed()

    def Closed(self, event=None):
        try:
            self.tl.destroy()
        except:
            pass

