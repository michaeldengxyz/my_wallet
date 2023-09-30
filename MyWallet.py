#Pyhton 3.x
# -*- coding: UTF-8 -*-


WindX  = {}
WindX['app_rev'] = '8.0'

"""
#required
pip install pwd
pip install pywin32
pip install pynput
pip install pycryptodome
pip install screeninfo

#https://blog.csdn.net/luanyongli/article/details/81385284
#pip install pytesseract 

#https://github.com/paddlepaddle/paddleocr
#https://github.com/PaddlePaddle/PaddleOCR/blob/develop/doc/doc_ch/installation.md
pip install paddlepaddle
pip install Shapely-1.8.2-cp310-cp310-win_amd64.whl
pip install paddleocr

pip install opencv-python
pip install pygetwindow
pip install numpyencoder
pip install psutil
pip install numpy==1.23
pip install ttkwidgets
"""

import time 
WindX['load_times'] = []
WindX['load_times'].append([time.time(), 'app start and load basic modules ...'])

import traceback
import re
import os,sys,glob
#os.system('cls')

#------------------------------
self_sys_argv0  = os.path.basename(sys.argv[0])
self_folder = ""
def find_real_file(ofile):
    self_folder = ""
    dirname = os.path.abspath(os.path.dirname(ofile))
    if dirname and os.path.exists(dirname):
        self_folder = re.sub(r'\\','/', dirname)
    else:
        fname = os.path.basename(ofile)        
        for root, dirs, files in os.walk(os.getcwd(), topdown=True):
            for name in files:
                if re.match(r'.*{}$'.format(fname), str(name), re.I):
                    print(sys._getframe().f_lineno,"find file:", name)
                    self_folder = re.sub(r'\\','/',os.path.abspath(os.path.dirname(name)))
                    break
            if self_folder:
                break
    return self_folder

if os.path.exists(sys.argv[0]):
    self_folder = re.sub(r'\\','/',os.path.abspath(os.path.dirname(sys.argv[0])))

if not (self_folder and os.path.exists(self_folder + '/MyWallet.ini.json')):
    self_folder = find_real_file(sys.argv[0])

print("\n#MW", sys._getframe().f_lineno,"root:", self_folder, "\n")
if not (self_folder and os.path.exists(self_folder + '/MyWallet.ini.json')):
    print(sys._getframe().f_lineno,"\n=========================== Failed to find root path!! ===========================\n")
    os._exit(0)
sys.path.append(self_folder)
#------------------------------

from mypyUtilzip import UZ_Check
UZ_Check(filename="mypyUtils",   fileExt='py')
UZ_Check(filename="mypyUtilsUI", fileExt='py')

import mypyUtilsUI
from mypyUtils import *
from mypyUtilsUI import *

import win32gui
import win32api
import tkinter as tk
from tkinter import *
from tkinter import filedialog,messagebox,ttk

from pynput import mouse
from pynput.mouse import Listener as mouseListener
from pynput import keyboard as keyboardX

import getpass
import json

import random, string
import threading
from multiprocessing import Process

from ctypes import *

WindX['load_times'].append([time.time(), 'app load modules: PIL module, ...'])
from PIL import Image #,ImageDraw,ImageGrab,ImageTk,ImageFont,
from io import BytesIO

WindX['load_times'].append([time.time(), 'app load modules: paddleocr class ...']) 
from image_ocr_class2 import PaddleOCR_Class, PaddleOCR_Load

WindX['load_times'].append([time.time(), 'app load modules - end.'])
WindXX = {}
WindX['self_folder'], WindX['pcName'], curUser = UT_GetInfoAppRoot()
if not (self_folder == WindX['self_folder']):
    WindX['self_folder'] = self_folder

WindX['self_folder_log'] = WindX['self_folder'] + '/MyWallet_Log'

#### Global variables
WindX['ClassWin'] = None
WindX['EncryptCode'] = ''
WindX['form_widgets'] = {}
WindX['form_widgets_short'] = {}
WindX['mouse_click_points'] = []

WindX['mouse_click_last_points'] = []
WindX['display_scale'] = []
WindX['display_sizes'] = []
WindX['keys_input_words'] = []
WindX['win_start'] = 1

WindX['win_ocr_used_time'] = {}
WindX['win_ocr_PaddleOCR']  = None
WindX['win_not_sending_key'] = 1
WindX['keyboard_keyPress'] = []
WindX['keyboard_keyAltPress'] = False

WindX['row_shortname'] = {}
WindX['mouse_last_time_click'] = [time.time(),0,0,0]
WindX['TopLevel_MessageAction'] = None
WindX['yscrollbar_oWidth'] = 0
WindX['win_orig_width'] = 0

WindX['configs_file'] = WindX['self_folder'] + "/MyWallet.ini.json"
WindX['mainPX'] = 0
WindX['mainPY'] = 0
WindX['UI_ToplevelAlertClass'] = None
WindX['FGW'] = {1:[],2:[]}

#### Configurations settings:
WindX['win_able_to_AlertSchedule'] = 1

UT_Print2Log('green',"\nconfgiurations:")
WindX['configs'] = UT_JsonFileRead(filepath=WindX['configs_file'])
if WindX['configs'] and WindX['configs'].__contains__('configuration'):
    for cf in sorted(WindX['configs']['configuration'].keys()):
        UT_Print2Log('green', "\t" + cf, WindX['configs']['configuration'][cf])
        WindX[cf] = WindX['configs']['configuration'][cf]['value']
UT_Print2Log('',"")

def Revisons():
    WindX['main_rev_list'] ={
        '7.0': "initiation",
        '8.0': "add new functions to manage encrypted files"
    }

def ConfigurationSave(): 
    try:
        for cf in WindX['configs']['configuration']:
            if WindX['configs']['configuration'].__contains__(cf):
                WindX['configs']['configuration'][cf]['value'] = WindX[cf]
            else:
                WindX['configs']['configuration'][cf] = {'value': WindX[cf]}

        UT_JsonFileSave(filepath=WindX['configs_file'], fdata=WindX['configs'])
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

def SaveLog(logFile='', isMainWin=False):    
    ConfigurationSave()
    if isMainWin:
        logFile = WindX['self_folder_log'] + '/MyWalletLog' + time.strftime("%Y%m%d%H%M%S%z",time.localtime(time.time())) + ".html"
    UT_LogSave2HTML(logFile)

def DisplayLoadTime():
    WindX['load_times'].append([time.time(), 'UI loaded - end.'])
    stime = WindX['load_times'][0][0]
    UT_Print2Log('\n-----------------------------')
    for s in WindX['load_times']:
        time_used = UT_UsedTime(0,s[0] - stime)
        if s[0] == stime:
            time_used = "00:00:00.000"
        UT_Print2Log('',time.strftime("%H:%M:%S",time.localtime(s[0])), "+"+time_used, s[1])

def WinFocusOn():
    if len(WindX['FGW'][1]):
        UT_Print2Log('', sys._getframe().f_lineno, ".... SetForegroundWindow:",WindX['FGW'][1])
        UT_WinFocusOn(WindX['FGW'][1][0])
    else:
        UT_Print2Log('red', sys._getframe().f_lineno, ".... Can not catch ForegroundWindow!")

def PSWaction(row=0,act=None,filename=None,delstr=False):
    UT_Print2Log('', "\n",sys._getframe().f_lineno,"psw action", row,act)
    UI_WinWidgetState(wid=WindX['ClassWin'].root, state="disabled", widName="button")
    UI_WinWidgetState(wid=WindX['ClassWin'].root, state="disabled", widName="entry")

    try:
        UT_ClipboardEmpty()
        if WindX['ClassWin'].label_tmp_status:
            try:
                WindX['ClassWin'].label_tmp_status.destroy()
            except:
                pass
            WindX['ClassWin'].label_tmp_status = None
            
        if act == "send":
            #WindX['form_widgets'][row] = [sv_fieldname, sv_value, bdelete.b, ef, ev, bsend.b]
            #   
            #                            0             1         2          3   4   5   
            if WindX['form_widgets'][row][11].get():                
                ExtensionRun(WindX['form_widgets'][row][1].get())
                PSWaction_Done()
                return

            WindX['ClassWin'].root.title("My Wallet " + WindX['app_rev'])    
            UT_Print2Log('', sys._getframe().f_lineno, "Action ("+act+") - to Foreground Window:", WindX['FGW'])
            if IsThisAppItself(WindX['FGW'][1][1]):
                UT_Print2Log('red', sys._getframe().f_lineno, ".. You can not input to self main window!")
                PSWaction_Done()
                return

            left, top, right, bottom = UT_WindowRectGet(WindX['FGW'][1][0])
            if left + top + right + bottom == 0:
                UT_Print2Log('red', sys._getframe().f_lineno, ".. Invalid window -", WindX['FGW'][1])
                PSWaction_Done()
                return

            pos = win32api.GetCursorPos()
            WindX['win_not_sending_key'] = 0
            t = re.sub(r'[^0-9]+','', WindX['ClassWin'].var_delay2send.get())
            WindX['ClassWin'].widget_delay2send.delete(0,"end")
            if not t:
                t = 0
            else:
                t = int(t)*1
                if t > 10:
                    t = 10
            WindX['ClassWin'].widget_delay2send.insert(0,str(t))
            
            try:
                if t:               
                    tt = int(t)*10
                    xmsg = " Sending: "+ WindX['form_widgets'][row][0].get() + ", please set foucs where you need to input!"
                    while tt:
                        #WindX['ClassWin'].root.title("{:>02d}".format(tt) + " Sending: "+ WindX['form_widgets'][row][0].get())
                        UI_ClassToplevelMessage("{:>02d}".format(tt) + xmsg, 'yellow', 'red')
                        WindX['ClassWin'].root.update()
                        time.sleep(0.1)
                        tt = tt - 1
                    #WindX['ClassWin'].root.title("Sending ["+ WindX['form_widgets'][row][0].get() +"] now ...")
                    UI_ClassToplevelMessage(xmsg, 'yellow', 'red')
                
                else:
                    n = len(WindX['mouse_click_points'])
                    if n >= 2:
                        win32gui.SetForegroundWindow(WindX['FGW'][1][0])
                        
                        x = WindX['mouse_click_points'][n - 2][0]
                        y = WindX['mouse_click_points'][n - 2][1]
                        left, top, right, bottom = UT_WindowRectGet(WindX['FGW'][1][0])  #win32gui.GetWindowRect(WindX['FGW'][1][0])
                        if x >= left and x <= right and y >= top and y <= bottom:
                            #UT_Print2Log('', sys._getframe().f_lineno, WindX['mouse_click_points'])
                            try:
                                imouse = mouse.Controller()
                                winScale = UI_DeviceDisplayScale(x,y) 
                                x1 = int(x/winScale)
                                y1 = int(y/winScale)                        
                                imouse.position = (x1, y1)    #fit to a 100% of Display Scale, and place the mouse at a correct point
                                posx = win32api.GetCursorPos()
                                UT_Print2Log('', sys._getframe().f_lineno, "Click to focus on this point (",x, x1,',', y, y1, ")",posx, WindX['FGW'][1])

                                if x1 != posx[0] or y1 != posx[1]:                            
                                    e = win32api.SetCursorPos((x1,y1))   
                                    if not e:
                                        UT_Print2Log('red', sys._getframe().f_lineno, "error to win32api.SetCursorPos:",win32api.GetLastError())                         
                                UT_Print2Log('', sys._getframe().f_lineno)
                                
                                time.sleep(0.2)
                                posx = win32api.GetCursorPos()
                                if abs(posx[0] - x1) > 5 or abs(posx[1] - y1) > 5:   
                                    UT_Print2Log('red', sys._getframe().f_lineno, "can not set mouse on the right point: ", (x1, y1),"!!")
                                    messagebox.showwarning(title='Warning', message="can not set mouse on this right point: (" + str(x1) + ", " + str(y1)+"), now it's here (" + str(posx[0]) + ", " + str(posx[1])+") !!")
                                    PSWaction_Done()
                                    return
                                UT_Print2Log('', sys._getframe().f_lineno)

                                #imouse.click(mouse.Button.left, 1)
                                UT_Print2Log('', sys._getframe().f_lineno)
                            except:
                                UT_Print2Log('red',sys._getframe().f_lineno, traceback.format_exc())
                        else:
                            WinFocusOn()
                    else:
                        WinFocusOn()

                kstr = str(WindX['form_widgets'][row][1].get())
                #UT_Print2Log('', sys._getframe().f_lineno, 'send key string:', kstr )
                UT_Print2Log('', sys._getframe().f_lineno)

                fgwHandle = win32gui.GetForegroundWindow()
                if fgwHandle and IsThisAppItself(win32gui.GetWindowText(fgwHandle)):
                    UT_Print2Log('red', sys._getframe().f_lineno, ".. You can not input to self main window!")
                    messagebox.showwarning(title='Warning', message="You can not input to self main window!!")
                    PSWaction_Done()
                    return
                elif not fgwHandle:
                    UT_Print2Log('red', sys._getframe().f_lineno, ".. No focus foreground window!")
                    messagebox.showwarning(title='Warning', message="No focus foreground window!")
                    PSWaction_Done()
                    return

                UT_ClipboardPaste(kstr,delstr=delstr)
                #kb = keyboardX.Controller()
                #kb.type(kstr)   #please make sure your keyboard with a right language setting
                UT_Print2Log('', sys._getframe().f_lineno)

                WindX['win_not_sending_key'] = 1
                WindX['mouse_click_points'] = []

                if not t:
                    time.sleep(0.2)
                    win32api.SetCursorPos(pos)
            except:
                UT_Print2Log('red',sys._getframe().f_lineno, traceback.format_exc())

        elif act == "copy":
            if WindX['form_widgets'][row][11].get():
                UI_WidgetEntryShow(None,e=WindX['form_widgets'][row][6],ishow='')

                UT_Print2Log('blue', sys._getframe().f_lineno, ".. select a file for the extension:", WindX['form_widgets'][row][0].get())
                filename = filedialog.askopenfilename(
                                filetypes= [('files', '.*')],
                                defaultextension='.py',
                                initialdir= WindX['self_folder'],
                                title= "Open File"
                                )
                if filename:
                    WindX['form_widgets'][row][1].set(filename)
                    PSWaction_Done()           
                return
    
            kstr = str(WindX['form_widgets'][row][1].get())
            UT_ClipboardInertText(kstr)

        elif act == "delete":
            #delete the row
            for i in range(4,len(WindX['form_widgets'][row])):
                #UT_Print2Log('', WindX['form_widgets'][row][i])
                try:
                    WindX['form_widgets'][row][i].grid_remove()
                except:
                    pass

            del WindX['form_widgets'][row]

            if WindX['form_widgets_short'].__contains__(row):
                try:
                    WindX['form_widgets_short'][row].destroy()
                except:
                    pass
            #UT_Print2Log('', WindX['form_widgets'])

        elif act == "save":
            if not CodeInputCheck():
                PSWaction_Done()
                return

            data = {
                'others'   : ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(2000))
            }   

            n = 0
            for irow in WindX['form_widgets']:    #[sv_fieldname,sv_value, bdelete.b, ef, ev, bsend.b, sv_fieldnameShort, efs]        
                if WindX['form_widgets'][irow][0].get() and WindX['form_widgets'][irow][1].get():
                    n +=1
                    short = WindX['form_widgets'][irow][2].get()
                    if not short:
                        short = WindX['form_widgets'][irow][0].get()
                    
                    data[n] = {
                        'field_name' : WindX['form_widgets'][irow][0].get(),
                        'field_value': WindX['form_widgets'][irow][1].get(),
                        'field_name_short': short,
                        'ischeck' : WindX['form_widgets'][irow][3].get(),
                        'ischeck_package': WindX['form_widgets'][irow][11].get()
                    }
             
            if n:
                filename = filedialog.asksaveasfilename(
                    filetypes= [('data files', '.dat')], 
                    defaultextension='.dat',
                    initialdir= WindX['self_folder'],
                    title= "Save As",
                    initialfile = "MyWallet." + getpass.getuser() + ".dat"
                    )

                if filename:
                    fdata = UT_CryptMe(json.dumps(data),key=UT_GetMD5(WindX['EncryptCode']), isEncript=True)
                    UT_FileSave(fdata, filename)
            else:
                UT_Print2Log('red', sys._getframe().f_lineno, "No data to save in your wallet!")
                messagebox.showwarning(title='Warning', message="No data to save in your wallet!")

        elif act == "get":
            if not CodeInputCheck():
                PSWaction_Done()
                return        
            if not (filename and os.path.exists(filename)):
                filename = filedialog.askopenfilename(
                            filetypes= [('data files', '.dat')], 
                            defaultextension='.dat',
                            initialdir= WindX['self_folder'],
                            title= "Open File"
                            )
            if filename:
                try:                   
                    fdata = UT_FileOpen(filename)
                    ffdata = UT_CryptMe(fdata,key=UT_GetMD5(WindX['EncryptCode']), isEncript=False)
                    if ffdata:
                        data  = json.loads(ffdata)
                        #UT_Print2Log('', data)
                        if data.__contains__('1'):     
                            if WindX['ClassWin'].form21_colnums > 1:               
                                for i in range(3,WindX['ClassWin'].form21_colnums+1):
                                    if WindX['form_widgets_short'].__contains__(i):
                                        try:
                                            WindX['form_widgets_short'][i].destroy()
                                        except:
                                            pass

                            for irow in WindX['form_widgets']:
                                for i in range(4,len(WindX['form_widgets'][irow])):
                                    #UT_Print2Log('', WindX['form_widgets'][row][i])
                                    try:
                                        WindX['form_widgets'][irow][i].destroy()
                                    except:
                                        pass

                            WindX['form_widgets'] = {}
                            WindX['ClassWin'].form22_rows =1
                            WindX['form_widgets_short'] = {}
                            WindX['ClassWin'].form21_colnums = 2
                            
                            ToNewRows = []                        
                            for i in data:
                                if not i == 'others':
                                    #print(i, data[i])
                                    #data[i]: {'field_name': 'JBL-Windows ID', 'field_value': 'dengm', 'field_name_short': 'JWID', 'ischeck': 0},
                                    if not data[i].__contains__('field_name_short'):
                                        data[i]['field_name_short'] = ''
                                    if not data[i].__contains__('ischeck'):
                                        data[i]['ischeck'] = 0
                                    if not data[i].__contains__('ischeck_package'):
                                        data[i]['ischeck_package'] = 0
                                    
                                    fname = str(data[i]['field_name' ])
                                    ToNewRows.append([fname[0].upper() + fname[1:], data[i]['field_value'], data[i]['field_name_short'], data[i]['ischeck'], data[i]['ischeck_package']])

                            if len(ToNewRows):
                                for s in sorted(ToNewRows, key=lambda x:x[0]):
                                    WindX['ClassWin'].UIaddNewRow(WindX['ClassWin'].frame221, 
                                                {'field_name' : s[0],
                                                'field_value': s[1],
                                                'field_name_short': s[2],
                                                'ischeck': s[3],
                                                'ischeck_package': s[4]
                                                })   

                                WindX['ClassWin'].ClassScrollableFrame.canvas.yview_moveto(0.0)                             
                                
                            WindX['win_login_done'] = True  
                            UI_WinFontSet(force=True, mainWin=WindX['ClassWin'].root)                     
                        else:
                            UT_Print2Log('red', "No data in your wallet!")
                            messagebox.showwarning(title='Warning', message="No data in your wallet!")
                            WindX['ClassWin'].frame222.grid()
                            WindX['ClassWin'].root.update()
                    else:
                        messagebox.showwarning(title='Warning!', message="!!! The file may not be correct, or the Encrypt Code may not be correct to decrypt this file:\n" + filename)
                except:
                    UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

            try:
                WindX['ClassWin'].button_files.grid()
                WindX['ClassWin'].label_delay2send.grid()
                WindX['ClassWin'].widget_delay2send.grid()
                WindX['ClassWin'].ClassScrollableFrame_files.grid_remove()
                WindX['ClassWin'].frame2211.grid_remove()
                WindX['ClassWin'].button_config.config(text='Config ∨')
                WindX['ClassWin'].configurations_show_on = False
                WindX['ClassWin'].frame222.grid()
                WindX['ClassWin'].root.update()

                t4 = threading.Timer(0.5, WindX['ClassWin'].ClassScrollableFrame.canvasLeave)
                t4.start() 
            except:
                UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

        elif act == 'new':
            para = {
                'field_name': 'new field ' + str(WindX['ClassWin'].form22_rows + 1),
                'field_value': '',
                'field_name_short': '',
                'ischeck': 0,
                'ischeck_package': 0
            }

            WindX['ClassWin'].UIaddNewRow(WindX['ClassWin'].frame221, para, True)
            UI_WinFontSet(force=True, mainWin=WindX['ClassWin'].root)
            WindX['ClassWin'].root.update()
            t4 = threading.Timer(0.5, WindX['ClassWin'].ClassScrollableFrame.canvasLeave, args=[None, 'both', "add-new-row"])
            t4.start()            

        elif act == 'Anchor':
            UI_WinGeometry(WindX['ClassWin'].root, '+0+0')

        PSWaction_Done()
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())
        PSWaction_Done()

def PSWaction_Done():
    WindX['ClassWin'].root.title("My Wallet " + WindX['app_rev'])
    UI_WidgetEntryShow(None,WindX['ClassWin'].widget_EncryptCode,'*')
    UI_WinWidgetState(wid=WindX['ClassWin'].root, state="normal", widName="button")
    UI_WinWidgetState(wid=WindX['ClassWin'].root, state="normal", widName="entry")
    WindX['win_not_sending_key'] = 1
    WindX['mouse_click_points'] = []

def Wind_Align_Browsers(): 
    ges = re.split(r'\+|x', WindX['ClassWin'].root.geometry())    
    scale = UI_DeviceDisplayScale(x=int(ges[2]), needScaled=True)
    UT_Print2Log('','\nmain.geometry()=', WindX['ClassWin'].root.geometry(), ', scale=', scale)
    UT_WindowsAlign(scale=scale, findWinTitle=r"Microsoft​\s+Edge|Internet\s+Explorer|Google\s+Chrome|SAP\s+Logon")


def IsThisAppItself(title):
    if re.match(r'^My\s+Wallet\s+\d+\.*\d*.*',title,re.I):
        return True
    else:
        return False

def KeyInputCheck(event,e=None):
    #UT_Print2Log('', event,':',e)   
    UI_CapLockStatus(event, e=e)
    UI_WidgetEntryShow(event,e)

    if event.keycode == 13 and e == WindX['ClassWin'].widget_EncryptCode:
        filename = WindX['self_folder'] + "/MyWallet." + getpass.getuser() + ".dat"
        if not os.path.exists(filename) and os.path.exists(WindX['self_folder'] + "/MyWallet.DengM.dat"):
            filename = WindX['self_folder'] + "/MyWallet.DengM.dat"

        PSWaction(0,"get", filename=filename)

def CodeInputCheck():
    yes = 1
    try:
        WindX['EncryptCode'] = re.sub(r'^\s+|\s+$', '', WindX['ClassWin'].var_EncryptCode.get())       
        if not WindX['EncryptCode']:
            yes = 0
            WindX['ClassWin'].widget_EncryptCode.configure(background='#FFFF66')
            UT_Print2Log('red', sys._getframe().f_lineno, 'Please input: Encrypt / Decrypt Code!')
            messagebox.showwarning(title='Warning', message='Please input: Encrypt / Decrypt Code!')
        else:
            WindX['ClassWin'].widget_EncryptCode.configure(background='#FFFFFF')
    except:
        pass
        
    return yes   

def DeviceDisplaysInfo():
    #return
    WindX['load_times'].append([time.time(), 'Get monitors: ...'])
    
    info = UI_DeviceDisplayInfoGet()
    WindX['display_scale'] = info['display_scale']
    WindX['display_sizes'] = info['display_sizes']
    mrect = [1000000, 1000000, -100, -100]
    for m in WindX['display_sizes']: 
        #m   Monitor(x=0, y=0, width=2560, height=1440, width_mm=700, height_mm=390, name='\\\\.\\DISPLAY1') 
        if m.x < mrect[0]:
            mrect[0] = m.x
        if m.y < mrect[1]:
            mrect[1] = m.y
        if m.x + m.width > mrect[2]:
            mrect[2] = m.x + m.width
        if m.y + m.height > mrect[3]:
            mrect[3] = m.y + m.height
            
    UT_Print2Log('', "ClipCursor=",mrect)
    sys.stdout.flush()
    try:
        win32api.ClipCursor(mrect)
        UI_WinFontSet(mainWin=WindX['ClassWin'].root)
        win32gui.SetForegroundWindow(WindX['ClassWin'].root.winfo_id())
    except:
        pass

    if not WindX['win_orig_width']:
        WindX['ClassWin'].root.update()
        WindX['win_orig_width'] = WindX['ClassWin'].root.winfo_width() 
    print("WindX['win_orig_width']=", WindX['win_orig_width'])

    WindX['ClassWin'].label_tmp_status.config(text="please input [Encrypt Code], then hit [Enter] key to load your data")

    t5 = threading.Timer(2,AlertSchedule)
    t5.start()

    WindX['ClassWin'].ClassScrollableFrame.canvasLeave(fixSide='width')
    DisplayLoadTime()

def GUI_Init(): 
    WindX['win_login_done'] = False 
    WindX['load_times'].append([time.time(), 'UI loading: ...'])

    WindX['ClassWin'] = ClassWinTkBase()
    UT_Print2Log('','ClassWinTkBase=', WindX['ClassWin'])

    WindX['ClassWin'].root.update()
    if not WindX['yscrollbar_oWidth']:
        try:
            rect = win32gui.GetWindowRect(WindX['ClassWin'].ClassScrollableFrame.scrollbar_y.winfo_id())  #Frame2.scrollbar_y left top right bottom (522, 78, 539, 382)
            WindX['yscrollbar_oWidth'] = abs(rect[2] - rect[0])
        except:
            UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

    UI_ToplevelRect([100, 15], [0,0])
    UI_ToplevelRectHide()

    UT_HideConsoleWindow(myfile= sys.argv[0])    
    t4 = threading.Timer(1, DeviceDisplaysInfo)
    t4.start()
    #AlertSchedule()
    WindX['ClassWin'].root.mainloop()

def ExtensionRun(filepath):
    if not os.path.exists(filepath):
        UT_Print2Log('red', sys._getframe().f_lineno, "!! The extension file is not exsting:", filepath)
        return
    
    UT_Print2Log('blue', sys._getframe().f_lineno, ".. Executing the extension: [" + filepath + "]")

    try:
        cmd = "\"" + filepath + "\""
        p = Process(target=UT_ProcessNew,args=[cmd])
        p.start()
        #new process target - UT_ProcessNew must be imported from other module!!! 
        #or will get - AttributeError: Can't get attribute 'long_time_task' on <module '__main__' (built-in)>
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

def ExtensionCheck(row=0):
    if WindX['form_widgets'].__contains__(row):
        try:        
            if WindX['form_widgets'][row][11].get():
                UI_WidgetEntryShow(None,e=WindX['form_widgets'][row][6],ishow='')

                WindX['form_widgets'][row][7].configure(text='Go')   #Send button
                WindX['form_widgets'][row][14].config(text='Execute this extension')

                WindX['form_widgets'][row][10].configure(text='Select File')  #copy button
                WindX['form_widgets'][row][13].config(text='Select an extension file')

                extfile = WindX['form_widgets'][row][1].get()
                isValid = True
                if extfile:
                    extdir  = os.path.dirname(extfile)
                    print("ExtensionCheck: row=", row, WindX['form_widgets'][row][11].get(), '\n\tFilepath:', extfile, '\n\tFile Dir:', extdir)
                    if not extdir:
                        extfile = WindX['self_folder'] + '/' + extfile

                    if not os.path.exists(extfile):
                        isValid = False
                else:
                    isValid = False
                    
                if not isValid:
                    UT_Print2Log('red', sys._getframe().f_lineno, "please input a valid file path into [field value]!")
                    messagebox.showwarning(title='Warning', message="The extension file is invalid: ["+ WindX['form_widgets'][row][1].get() +"]\n\nPlease input a valid file path into [field value]!")

            else:
                WindX['form_widgets'][row][7].configure(text='Send')   #Send button
                WindX['form_widgets'][row][14].config(text='Send field value of ' + WindX['form_widgets'][row][0].get())

                WindX['form_widgets'][row][10].configure(text='Copy')  #copy button
                WindX['form_widgets'][row][13].config(text='Copy field value of ' + WindX['form_widgets'][row][0].get())

        except:
            UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc()) 

def AlertSchedule():
    if not WindX['win_able_to_AlertSchedule']:
        return
    AlertScheduleEnd()

    WindX['UI_ToplevelAlertClass'] = UI_ClassToplevelAlertOnFullScreen(
        mainWin      = WindX['ClassWin'].root, 
        mainWin_start= WindX['win_start'], 
        e_display    = WindX['ClassWin'].widget_label_next_rest,
        alert        = "Time to get coffee,\n\nand check meetings for today!",
        interval     = 15
    )
    t5 = threading.Timer(0.01,WindX['UI_ToplevelAlertClass'].run)
    t5.start()

    WindX['win_start'] = 0

def AlertScheduleEnd():
    if WindX['UI_ToplevelAlertClass']:
        try:
            WindX['UI_ToplevelAlertClass'].tl.destroy()
        except:
            pass    

def ForeGroundWindow():
    try:
        fgwHandle = win32gui.GetForegroundWindow()
        if fgwHandle and WindX['win_not_sending_key']:
            title = win32gui.GetWindowText(fgwHandle)
            if IsThisAppItself(title):
                if mypyUtilsUI.WinUtilsUI['Win_last_geometry']:
                    UI_WinFontSet(mainWin=WindX['ClassWin'].root)
                return
            WindX['FGW'][1] = [fgwHandle, title]
    except:
        UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc()) 

def ForeGroundWindowsCheck():
    while True:
        ForeGroundWindow()
        time.sleep(0.1)

class ClassWinTkBase():
    def __init__(self, mainPX=0, mainPY=0, revision=WindX['app_rev'], collapse_color = 'red'):
        self.collapse_color = collapse_color
        if not self.collapse_color:
            self.collapse_color= 'red'
        
        self.root = None
        self.root_x0 = mainPX
        self.root_y0 = mainPY
        self.revision = revision
        self.Frame2HideCountdownTimer_timers = []
        self.Frame2HideCountdown_count = 0
        self.Frame22Show_Yes = True
        self.Frame2Hide_Yes  = False

        self.label_tmp_status = None
        self.form22_rows = 0
        self.form21_colnums = 1
        self.files_display_path = ""

        self.UI()

    def UI(self):
        try:
            self.root = tk.Tk()
        except:
            UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())
            self.WindExit()

        self.root.title("My Wallet " + self.revision)
        self.root.configure(bg='#A0A0A0')
        self.root.geometry('+' + str(self.root_x0) + '+' + str(self.root_y0))
        self.root.wm_attributes('-topmost',1) 
        #self.root.overrideredirect(1)
        self.root.protocol("WM_DELETE_WINDOW", self.WindExit)
        self.root.bind('<Motion>', self.WinOnMotion)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.frame1 = Frame(self.root, width=120, height=3, bg= self.collapse_color)
        self.frame1.grid(row=0,column=0,sticky=E+W+S+N,pady=0,padx=0)
        self.frame1.bind('<Motion>', self.MotionFrame1)

        self.frame2 = Frame(self.root,bg='#C0C0C0')
        self.frame2.grid(row=1,column=0,sticky=E+W+S+N,pady=0,padx=0)
        self.frame2.grid_columnconfigure(0, weight=1)
        self.frame2.grid_rowconfigure(1, weight=1)

        self.frame21 = Frame(self.frame2,bg='#E0E0E0')
        self.frame21.grid(row=0,column=0,sticky=E+W+S+N,pady=0,padx=0)

        self.frame22 = Frame(self.frame2,bg='#E0E0E0')
        self.frame22.grid(row=1,column=0,sticky=E+W+S+N,pady=1,padx=0)  
        self.frame22.grid_columnconfigure(0, weight=1)

        self.frame221x = Frame(self.frame22,bg='#E0E0E0')
        self.frame221x.grid(row=1,column=0,sticky=E+W+S+N,pady=0,padx=0)

        self.frame2211_bg = '#C5C5C5'
        self.frame2211 = Frame(self.frame221x,bg= self.frame2211_bg)
        self.frame2211.grid(row=0,column=0,sticky=E+W+S+N,pady=0,padx=0)

        self.file_list_button_bg = "#E8E8E8"
        self.ClassScrollableFrame_files = ClassScrollableFrame(self.frame221x)   #WindX['Frame1X']
        self.frame221_files = self.ClassScrollableFrame_files.scrollable_frame         #WindX['Frame1']
        self.ClassScrollableFrame_files.grid(row=1,column=0,sticky=E+W+S+N,pady=0,padx=0)
        self.root.bind("<MouseWheel>",  self.ClassScrollableFrame_files.canvasMouseWheel)
        self.ClassScrollableFrame_files.grid_remove()
        self.ClassScrollableFrame_files_show = False

        self.ClassScrollableFrame = ClassScrollableFrame(self.frame221x)   #WindX['Frame1X']
        self.frame221 = self.ClassScrollableFrame.scrollable_frame         #WindX['Frame1']
        self.ClassScrollableFrame.grid(row=1,column=0,sticky=E+W+S+N,pady=0,padx=0)
        self.root.bind("<MouseWheel>",  self.ClassScrollableFrame.canvasMouseWheel)

        self.frame222 = Frame(self.frame22,bg='#E0E0E0')
        self.frame222.grid(row=0,column=0,sticky=E+W+S+N,pady=0,padx=0)

        #- root
        #-- frame1
        #-- frame2
        #------ frame21: ⇡ ∧ (quick buttons)
        #------ frame22: 
        #--------- frame221x: 
        #------------- frame2211: Encrypt / Decrypt Code, 
        #------------- frame221 : data list
        #--------- frame222: Open, Save, New, Anchor, Auto, Files

        if self.frame21:
            b=ClassButtonGrid(self.frame21,0,0, self.Frame2Hide,'⇡',msg='Collapse Window', width=4)
            self.frame21_buttonCollapseWindow = b.b

            self.frame21_buttonShowFrame22Text = '  ∧  '
            b = ClassButtonGrid(self.frame21,0,1,self.Frame22Show, self.frame21_buttonShowFrame22Text, width=4)
            self.frame21_buttonShowFrame = b.b

            bs = ClassButtonGrid(self.frame21,0,1000, Wind_Align_Browsers,'A.B',p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',0,E+W+N+S,1,1])
            UI_WidgetBalloon(bs.b,  'Align browser windows')

            xlbl = Label(self.frame21, text='initiating ... ... please wait for seconds!', justify=CENTER, relief=FLAT,pady=3,padx=3, bg='yellow')
            xlbl.grid(row=0,column=0,columnspan=1005, sticky=E+W+N+S)
            self.label_tmp_status = xlbl

        if self.frame2211:
            row = 0  
            col = 0
            Label(self.frame2211, text='Encrypt Code', justify=CENTER, relief=FLAT,pady=5,padx=5, bg=self.frame2211_bg).grid(row=row,column=col,sticky=E+W)
            self.var_EncryptCode = StringVar()
            
            col+=1
            e=Entry(self.frame2211, justify=LEFT, relief=FLAT, textvariable=self.var_EncryptCode, show="*")
            e.grid(row=row,column=col,sticky=E+W+N+S,pady=1,padx=1)
            e.insert(0, WindX['EncryptCode'])
            e.bind('<FocusIn>',func=UT_HandlerAdaptor(KeyInputCheck,e=e))
            e.bind('<KeyRelease>',func=UT_HandlerAdaptor(KeyInputCheck,e=e))
            e.bind('<Leave>',func=UT_HandlerAdaptor(UI_WidgetEntryShow,e=e,ishow='*'))
            e.focus()
            self.widget_EncryptCode = e
            UI_WidgetBalloon(e,  'Code to encrypt or decrypt your data')

            col+=1
            self.label_delay2send = Label(self.frame2211, text='Delay to send', justify=CENTER, relief=FLAT,pady=5,padx=5, bg=self.frame2211_bg)
            self.label_delay2send.grid(row=row,column=col,sticky=E+W)
            
            col+=1
            self.var_delay2send = StringVar()
            e2=Entry(self.frame2211, justify=CENTER, relief=FLAT, textvariable= self.var_delay2send, width=6)
            e2.grid(row=row,column=col,sticky=E+W+N+S,pady=1,padx=0)
            e2.insert(0,0)
            self.widget_delay2send = e2
            UI_WidgetBalloon(e2,  'Delay to send, seconds after click')

            self.label_delay2send.grid_remove()
            self.widget_delay2send.grid_remove()

        if self.frame222:
            self.buttons_frame222_bg = '#D0D0D0'
            iwidth = 8

            row = 0 
            col = 0     
            self.var_Click_Watcher = IntVar()
            ef_chkb = Checkbutton(self.frame222, text= "Auto", variable= self.var_Click_Watcher, justify=LEFT, fg='blue', bg=self.buttons_frame222_bg, relief=FLAT, width=iwidth)
            ef_chkb.grid(row=row,column=col,sticky=E+W+N+S,padx=0,pady=0)
            UI_WidgetBalloon(ef_chkb,  '-- Auto check (and show OCR result) on the click-area.\n-- While pressing [Alt] key then copy OCR result to clipboard.\n-- Click middle-mouse to trigger this watcher once.', 'Mouse-click Watcher')
            #self.var_Click_Watcher.set(1)  
            
            self.buttons_frame222 = {}
            col+=1
            b = ClassButtonGrid(self.frame222,row,col,lambda:PSWaction(0,"get"),'Open', width=iwidth, bg=self.buttons_frame222_bg)
            self.buttons_frame222['Open'] = b.b
            
            col+=1
            b = ClassButtonGrid(self.frame222,row,col,lambda:PSWaction(0,"save"),'Save', width=iwidth, bg=self.buttons_frame222_bg)    
            self.buttons_frame222['Save'] = b.b

            col+=1
            b = ClassButtonGrid(self.frame222,row,col,lambda:PSWaction(0,"new"),'New', width=iwidth, bg=self.buttons_frame222_bg)  
            self.buttons_frame222['New'] = b.b
            UI_WidgetBalloon(b.b,  'Add new row')

            col+=1
            b = ClassButtonGrid(self.frame222,row,col, self.configurations_show,'Config ∧', width=iwidth, bg=self.buttons_frame222_bg)  
            UI_WidgetBalloon(b.b,  'Show/hide configurations')
            self.button_config = b.b
            self.configurations_show_on = True

            col+=1
            b = ClassButtonGrid(self.frame222,row,col,lambda:PSWaction(0,"Anchor"),'⇱', width=iwidth, bg=self.buttons_frame222_bg)  
            self.buttons_frame222['Anchor'] = b.b
            UI_WidgetBalloon(b.b,  'Anchor at the point (0,0)')

            col+=1
            b = ClassButtonGrid(self.frame222,row,col, self.files_list_show,'List', width=iwidth, bg=self.file_list_button_bg, fg='#8B2500')  
            UI_WidgetBalloon(b.b,  'Manage my encrypted files/list')
            self.button_files = b.b
            b.b.grid_remove()                   

            col+=1
            self.frame222.grid_columnconfigure(col, weight=1)
            xlbl = Label(self.frame222, text='0', justify=RIGHT, relief=FLAT,pady=5,padx=3, bg=self.file_list_button_bg, fg='#A0A0A0', anchor=E)
            xlbl.grid(row=row,column=col,sticky=E+W+N+S,pady=0,padx=0)
            self.widget_label_next_rest = xlbl
            UI_WidgetBalloon(xlbl,  'Seconds to have a break')

        self.frame222.grid_remove()

        if self.frame221_files:            
            self.frame221_files_01 = Frame(self.frame221_files, bg='#EFEFEF')
            self.frame221_files_01.grid(row=0,column=0,sticky=E+W+S+N,pady=1,padx=0)

            self.frame221_files_02 = Frame(self.frame221_files, bg='#EFEFEF')
            self.frame221_files_02.grid(row=1,column=0,sticky=E+W+S+N,pady=0,padx=0)

            Label(self.frame221_files_01, text='Folder', justify=LEFT, relief=FLAT,pady=5,padx=5, bg=self.file_list_button_bg, anchor=E).grid(row=0,column=0,sticky=E+W+S+N,pady=0,padx=0)
            self.files_folder_path = StringVar()
            e=Entry(self.frame221_files_01, justify=LEFT, relief=FLAT, textvariable= self.files_folder_path, state='readonly')
            e.grid(row=0,column=1,sticky=E+W+N+S,pady=0,padx=1)

            b= ClassButtonGrid(self.frame221_files_01,0,2, self.select_folder, '...' ,fg='blue', bg= self.file_list_button_bg, p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',10,E+W+N+S,0,0]) 
            UI_WidgetBalloon(b.b, 'Select Folder')

            b= ClassButtonGrid(self.frame221_files_01,0,3, self.files_display_list, '↻' ,fg='blue', bg= self.file_list_button_bg, p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',10,E+W+N+S,0,0]) 
            UI_WidgetBalloon(b.b, 'Refresh file list')

            self.frame221_files.grid_columnconfigure(0, weight=1)
            self.frame221_files_01.grid_columnconfigure(1, weight=1)

        #self.root.mainloop()

    def configurations_show(self):
        if self.configurations_show_on:
            self.configurations_show_on = False
            self.button_config.config(text='Config ∨')
            self.frame2211.grid_remove()
        else:
            self.configurations_show_on = True
            self.button_config.config(text='Config ∧')
            self.frame2211.grid()

            if self.ClassScrollableFrame_files_show:
                t2 = threading.Timer(0.5, self.ClassScrollableFrame_files.canvasLeave)
                t2.start()
            else:
                t1 = threading.Timer(0.5, self.ClassScrollableFrame.canvasLeave)
                t1.start()

    def select_folder(self):
        dir_path = UI_SetFolder(WindX['self_folder'])
        if dir_path:
            self.files_display_path = dir_path
            self.files_folder_path.set(dir_path)
            self.files_display_list()

    def files_display_list(self):
        if self.files_display_path and os.path.exists(self.files_display_path):
            UI_WinWidgetRemove(wid=self.frame221_files_02)
            self.files_display_buttons = {}
            
            n = 0
            try:
                #get all files in his folder
                os.chdir(self.files_display_path)
                lbl = Label(self.frame221_files_02, text='No.', justify=LEFT, relief=FLAT,pady=5,padx=3, bg=self.file_list_button_bg, anchor=E)
                lbl.grid(row=n,column=0,sticky=E+W+S+N,pady=1,padx=0)

                lbl = Label(self.frame221_files_02, text='Status', justify=LEFT, relief=FLAT,pady=5,padx=3, bg=self.file_list_button_bg, anchor=E)
                lbl.grid(row=n,column=1,sticky=E+W+S+N,pady=1,padx=1)

                lbl = Label(self.frame221_files_02, text='File Name', justify=CENTER, relief=FLAT,pady=5,padx=3, bg=self.file_list_button_bg, anchor='w', width=40)
                lbl.grid(row=n,column=2,sticky=E+W+S+N,pady=1,padx=0)

                lbl = Label(self.frame221_files_02, text='File Size (Kbs)', justify=LEFT, relief=FLAT,pady=5,padx=3, bg=self.file_list_button_bg, anchor='w')
                lbl.grid(row=n,column=3,sticky=E+W+S+N,pady=1,padx=1)

                lbl = Label(self.frame221_files_02, text='Last Modified', justify=LEFT, relief=FLAT,pady=5,padx=3, bg=self.file_list_button_bg, anchor='w')
                lbl.grid(row=n,column=4,sticky=E+W+S+N,pady=1,padx=0)    
                
                for f in sorted(glob.glob("*")): 
                    if (f == '.') or (f == '..'):
                        continue
                            
                    if not os.path.isdir(os.path.join(self.files_display_path, f)):
                        n += 1
                        try:
                            fid = UT_GetMD5(f)

                            ipay = 0
                            if n%2==0:
                                ipay = 1

                            tips = "Click to encrypt the file: "
                            status = ''
                            #if re.match(r'.*(\.[A-Z0-9]{4}\.crpt)$', f, re.I):
                            if re.match(r'.*\.crpt$', f, re.I):
                                status = 'lock'
                                tips = "Click to decrypt the file: "

                            fsize = round(os.path.getsize(f)/1024, 2)   #when the file path is deep and every long, will get error and fail to get file size
                            ftime = time.strftime("%y-%m-%d %H:%M:%S",time.localtime(os.path.getmtime(f)))

                            lbl = Label(self.frame221_files_02, text=str(n), justify=LEFT, relief=FLAT,pady=5,padx=3, bg=self.file_list_button_bg, anchor=E)
                            lbl.grid(row=n,column=0,sticky=E+W+S+N,pady=ipay,padx=0)
                            lbl.bind("<MouseWheel>",  self.ClassScrollableFrame_files.canvasMouseWheel)

                            lb2 = Label(self.frame221_files_02, text=status, justify=CENTER, relief=FLAT,pady=5,padx=3, bg=self.file_list_button_bg, fg='red')
                            lb2.grid(row=n,column=1,sticky=E+W+S+N,pady=ipay,padx=1)
                            lb2.bind("<MouseWheel>",  self.ClassScrollableFrame_files.canvasMouseWheel)

                            #b= ClassButtonGrid(self.frame221_files_02, n, 2, lambda:self.files_encrypt_decrypt(f), f ,fg='blue', bg= self.file_list_button_bg, TexAnchor='w' ,p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',10,E+W+N+S,ipay,0])  
                            #b.b.bind("<MouseWheel>",  self.ClassScrollableFrame_files.canvasMouseWheel)
                            #UI_WidgetBalloon(b.b, tips + f)
                            #self.files_display_buttons[UT_GetMD5(f)] = [b.b, n, 2]
                            b3 = self.files_list_add_rows(n, f, tips, ipay, fid)

                            lb4 = Label(self.frame221_files_02, text=str(fsize), justify=LEFT, relief=FLAT,pady=5,padx=3, bg=self.file_list_button_bg, anchor='w')
                            lb4.grid(row=n,column=3,sticky=E+W+S+N,pady=ipay,padx=1)
                            lb4.bind("<MouseWheel>",  self.ClassScrollableFrame_files.canvasMouseWheel)

                            lb5 = Label(self.frame221_files_02, text=ftime, justify=LEFT, relief=FLAT,pady=5,padx=3, bg=self.file_list_button_bg, anchor='w')
                            lb5.grid(row=n,column=4,sticky=E+W+S+N,pady=ipay,padx=0)    
                            lb5.bind("<MouseWheel>",  self.ClassScrollableFrame_files.canvasMouseWheel)

                            self.files_display_buttons[fid] = [n, 2, lb2, b3, lb4, lb5, ipay] 
                        except:
                            UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())                    
            
            except:
                UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

            t2 = threading.Timer(1, self.ClassScrollableFrame_files.canvasLeave)
            t2.start()

    def files_list_add_rows(self, n, f, tips, ipay, fid):
        b= ClassButtonGrid(self.frame221_files_02, n, 2, lambda:self.files_encrypt_decrypt(f), f ,fg='blue', bg= self.file_list_button_bg, TexAnchor='w' ,p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',10,E+W+N+S,ipay,0])  
        b.b.bind("<MouseWheel>",  self.ClassScrollableFrame_files.canvasMouseWheel)
        UI_WidgetBalloon(b.b, tips + f)
        return b.b      
        
    def files_encrypt_decrypt(self, file=""):
        try:
            file_dir = self.files_folder_path.get()
            filepath = os.path.join(file_dir, file)
            print("\nfiles_encrypt_decrypt:", file_dir, file)
            if os.path.exists(filepath):
                os.chdir(file_dir)
                EncryptCode = re.sub(r'^\s+|\s+$', '', self.var_EncryptCode.get())
                #VerifyCode = UT_MD5_VerifyCode(EncryptCode)

                to_encrypt = True  
                #filex = file + '.' + VerifyCode + '.crpt'  
                filex = file + '.crpt'  
                status = 'lock'
                tips = "Click to decrypt the file: "        
                if re.match(r'.*\.crpt$', file, re.I):
                #if re.match(r'.*(\.[A-Z0-9]{4}\.crpt)$', file, re.I):
                    #if not re.match(r'.*(\.{}\.crpt)$'.format(VerifyCode), file, re.I):
                    #    messagebox.showwarning(title='Warning!', message="!!! Encrypt Code is not correct to decrypt this file:\n" + file)
                    #    return

                    to_encrypt = False
                    #filex = re.sub(r'(\.[A-Z0-9]{4}\.crpt)$', '', file, flags=re.I)
                    filex = re.sub(r'\.crpt$', '', file, flags=re.I)
                    tips = "Click to encrypt the file: "
                    status = ''

                print("\tfile to_encrypt=", to_encrypt, filex)

                fdata  = UT_FileOpen(file, format='bytes')
                ffdata = UT_CryptMe(fdata, key=UT_GetMD5(EncryptCode), isEncript=to_encrypt, dataType='bytes')

                if ffdata:
                    UT_FileSave(ffdata, filex, format='bytes')
                    if os.path.exists(filex):
                        #self.files_display_list()
                        #return
                    
                        fsize = round(os.path.getsize(filex)/1024, 2)   #when the file path is deep and every long, will get error and fail to get file size            
                        ftime = time.strftime("%y-%m-%d %H:%M:%S",time.localtime(os.path.getmtime(filex)))

                        oid = UT_GetMD5(file)
                        wids = self.files_display_buttons[oid]   #[row, col, lb2, b3, lb4, lb5, ipay]
                        row  = wids[0]
                        ipay = wids[6]
                        self.files_display_buttons[oid][3].destroy()

                        nid = UT_GetMD5(filex)
                        b3  = self.files_list_add_rows(row, filex, tips, ipay, nid)            
                        self.files_display_buttons[nid] = wids
                        self.files_display_buttons[nid][3] = b3
                        self.files_display_buttons[nid][2].config(text = status)
                        self.files_display_buttons[nid][4].config(text = fsize)
                        self.files_display_buttons[nid][5].config(text = ftime)

                        del self.files_display_buttons[oid]
                        UT_FileDelete(file)

                    else:
                        UT_Print2Log('red', "\n", sys._getframe().f_lineno, "failed to encrypt/decrypt:", filepath)
                else:
                    if re.match(r'.*\.crpt$', file, re.I):
                        messagebox.showwarning(title='Warning!', message="!!! Encrypt Code may not be correct to decrypt this file:\n" + file)
                    else:
                        messagebox.showwarning(title='Warning!', message="!!! Encrypt Code my not be not correct to encrypt this file:\n" + file)

            else:
                UT_Print2Log('red', "\n", sys._getframe().f_lineno, "File not existing to encrypt/decrypt:", filepath)
        except:
            UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

    def files_list_show(self):
        if self.ClassScrollableFrame_files_show:
            self.ClassScrollableFrame_files.grid_remove()
            self.ClassScrollableFrame.grid()
            self.ClassScrollableFrame_files_show = False
            self.button_files.config(text='List')

            for b in self.buttons_frame222.keys():
                self.buttons_frame222[b].config(state='normal')

            t4 = threading.Timer(0.5, self.ClassScrollableFrame.canvasLeave)
            t4.start()
        else:
            self.ClassScrollableFrame.grid_remove()
            self.ClassScrollableFrame_files.grid()
            self.ClassScrollableFrame_files_show = True
            self.button_files.config(text='Files')

            for b in self.buttons_frame222.keys():
                self.buttons_frame222[b].config(state='disabled')

            t4 = threading.Timer(0.5, self.ClassScrollableFrame_files.canvasLeave)
            t4.start()

    def WinOnMotion(self, event=None):
        self.WinOnMotion_LastTime = time.time()
        self.Frame2HideCountdown_count = 30

    def StickOnTopSide(self):
        geos = re.split(r'\D', self.root.geometry(),re.I)
        gx = re.split(r'\+',geos[2])
        self.geo_xy = str(gx[0]) + '+0'
        self.root.geometry('+' + self.geo_xy)

    def Frame2Hide(self, event=None):
        self.root.geometry("")
        self.frame2.grid_remove()
        self.Frame2Hide_Yes = True
        self.StickOnTopSide()
        self.root.overrideredirect(1)
        self.Frame22Show(force2hide=True)

    def MotionFrame1(self, event=None):
        if not self.Frame22Show_Yes:
            self.root.geometry("")
            self.frame2.grid()        
            self.Frame2Hide_Yes  = False
            self.WinOnMotion()
            self.Frame22Show(force2hide=True)
            self.Frame2HideCountdownTimer()

    def Frame2HideCountdown(self, t=30):
        self.Frame2HideCountdown_count = t
        while self.Frame2HideCountdown_count > 0 and (not self.Frame2Hide_Yes) and (not self.Frame22Show_Yes):            
            self.frame21_buttonCollapseWindow.config(text='⇡ ' + str(self.Frame2HideCountdown_count))
            self.root.update()
            self.Frame2HideCountdown_count -= 1
            time.sleep(1)

        if not self.Frame2Hide_Yes:
            if self.WinOnMotion_LastTime and time.time() - self.WinOnMotion_LastTime > 30:
                self.Frame2Hide()
            elif not self.Frame22Show_Yes:
                if not self.Frame2HideCountdown_count:
                    self.Frame2Hide()
                else:
                    self.Frame2HideCountdown()

        self.frame21_buttonCollapseWindow.config(text='⇡')

    def Frame2HideCountdownTimer(self):
        if len(self.Frame2HideCountdownTimer_timers):
            for t in self.Frame2HideCountdownTimer_timers:
                try:
                    t.cancel()
                except:
                    UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())
        self.Frame2HideCountdownTimer_timers = []

        t1 = threading.Timer(0.01, self.Frame2HideCountdown)
        t1.start()
        self.Frame2HideCountdownTimer_timers.append(t1)

    def Frame22Show(self, event=None, force2hide=False):
        self.root.geometry("")
        if self.Frame22Show_Yes or force2hide:
            UI_WinWidgetState(wid=self.root, state="disabled", widName="entry")
            self.Frame22Show_Yes = False
            self.frame22.grid_remove()    
            self.frame21_buttonShowFrame22Text = "  ∨ "
            self.root.overrideredirect(1)
            if not force2hide:
                self.Frame2HideCountdownTimer()
        else:
            UI_WinWidgetState(wid=self.root, state="normal", widName="entry")
            self.Frame22Show_Yes = True
            self.frame22.grid()
            self.frame21_buttonShowFrame22Text = '  ∧  '
            self.root.overrideredirect(0)

        self.frame21_buttonShowFrame.configure(text= self.frame21_buttonShowFrame22Text)

    def ColumnPadx(self, col):
        if col % 2:
            return 1
        else:
            return 0

    def UIaddNewRow(self, form, para,addNew=None):
        self.form22_rows +=1
        row = self.form22_rows
        col = 0
        pady_row = 0
        if self.form22_rows % 2:
            pady_row = 1

        ef_chkbx = ClassCheckboxGrid(
            form,self.form22_rows, col, None, self.form22_rows - 1,
            fg='#009900',
            bg= self.file_list_button_bg, 
            p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',0,E+W+N+S,pady_row, self.ColumnPadx(col)], 
            isList=True,
            msg = 'Checked to show on the toolbar',
            ischeck= para['ischeck']                          
        )
        sv_ischeck = ef_chkbx.variable
        ef_chkb    = ef_chkbx.b 

        col +=1
        sv_fieldname = StringVar()
        ef=Entry(form, justify=LEFT, relief=FLAT, textvariable= sv_fieldname, width=25)
        ef.grid(row=self.form22_rows,column=col,sticky=E+W+N+S,padx=self.ColumnPadx(col),pady=pady_row)
        ef.insert(0,para['field_name'])
        ef.bind('<FocusIn>',func=UT_HandlerAdaptor(KeyInputCheck,e=ef))
        ef.bind('<KeyRelease>',func=UT_HandlerAdaptor(KeyInputCheck,e=ef))
        ef.bind('<Motion>',func=UT_HandlerAdaptor(self.UI_highlight_row, row=row,act=1))
        ef.bind('<Leave>', func=UT_HandlerAdaptor(self.UI_highlight_row, row=row,act=0))
        if addNew:
            ef.focus()
        UI_WidgetBalloon(ef,  'Field Name')

        col +=1
        sv_fieldnameShort = StringVar()
        efs=Entry(form, justify=LEFT, relief=FLAT, textvariable= sv_fieldnameShort,width=8)
        efs.grid(row=self.form22_rows,column=col,sticky=E+W+N+S,padx=self.ColumnPadx(col),pady=pady_row)
        efs.insert(0,para['field_name_short'])
        efs.bind('<FocusIn>',func=UT_HandlerAdaptor(KeyInputCheck,e=ef))
        efs.bind('<KeyRelease>',func=UT_HandlerAdaptor(KeyInputCheck,e=ef))
        efs.bind('<Motion>',func=UT_HandlerAdaptor(self.UI_highlight_row, row=row,act=1))
        efs.bind('<Leave>', func=UT_HandlerAdaptor(self.UI_highlight_row, row=row,act=0))

        UI_WidgetBalloon(efs,  'Short Field Name')
        
        if para['field_name_short'] == 'JWID' or para['field_name_short'] == 'JPSW' or para['field_name_short'] == 'JCOD':
            WindX['row_shortname'][para['field_name_short']] = row

        col +=1
        sv_value = StringVar()
        ev=Entry(form, justify=LEFT, relief=FLAT, textvariable= sv_value, show="*", width=22)
        ev.grid(row=self.form22_rows,column=col,sticky=E+W+N+S,padx=self.ColumnPadx(col),pady=pady_row)
        ev.insert(0,para['field_value'])
        ev.bind('<FocusIn>',func=UT_HandlerAdaptor(KeyInputCheck,e=ev))
        ev.bind('<KeyRelease>',func=UT_HandlerAdaptor(KeyInputCheck,e=ev))
        ev.bind('<Leave>',func=UT_HandlerAdaptor(UI_WidgetEntryShow,e=ev,ishow='*'))  
        UI_WidgetBalloon(ev,  'Field Value')

        col +=1
        ef_chkb_ext = ClassCheckboxGrid(
            form,self.form22_rows, col, lambda:ExtensionCheck(row), '',
            bg= self.file_list_button_bg, 
            p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',0,E+W+N+S,pady_row,self.ColumnPadx(col)], 
            isList=True,
            msg = 'Checked to be executed as an extension',
            ischeck= para['ischeck_package']                            
        )
        sv_ischeck_extension = ef_chkb_ext.variable
        ef_chkb_extension    = ef_chkb_ext.b

        texttips = {
            'copy':['Copy', 'Copy field value of ' + para['field_name']],
            'send':['Send', 'Send field value of ' + para['field_name']]
        }
        if para['ischeck_package']:
            texttips = {
                'copy':['Select File', 'Select an extension file'],
                'send':['Go', 'Execute this extension']
            }

        col +=1
        bcopy = ClassButtonGrid(
            form,self.form22_rows, col, lambda:PSWaction(row,"copy"),texttips['copy'][0], 
            bg= self.file_list_button_bg, 
            p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',8,E+W+N+S,pady_row,self.ColumnPadx(col)], 
            isList=True,
            msg = texttips['copy'][1]
            )

        col +=1
        bsend = ClassButtonGrid(
            form,self.form22_rows,col,lambda:PSWaction(row,"send"), texttips['send'][0], 
            bg= self.file_list_button_bg, 
            p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',8,E+W+N+S,pady_row,self.ColumnPadx(col)], 
            isList=True,
            msg = texttips['send'][1]
            )

        col +=1
        bdelete = ClassButtonGrid(
            form,self.form22_rows,col,lambda:PSWaction(row,"delete"),'x',
            fg='red', 
            bg= self.file_list_button_bg,
            p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',3,E+W+N+S,pady_row,self.ColumnPadx(col)], 
            isList=True,
            msg = 'Delete this row'
            )
        
        WindX['form_widgets'][self.form22_rows] = [
            sv_fieldname, sv_value, sv_fieldnameShort, sv_ischeck,            #0-3
            bdelete.b,    ef,       ev,                bsend.b,               #4-7
            efs,          ef_chkb,  bcopy.b,           sv_ischeck_extension,  #8-11
            ef_chkb_extension,      bcopy.balloon, bsend.balloon              #12-14
        ]

        if para['field_name_short'] and self.frame21 and para['ischeck']:
            self.form21_colnums +=1

            shortname = para['field_name_short']
            if para['ischeck_package']:
                shortname = "*" + para['field_name_short']

            bs = ClassButtonGrid(
                self.frame21,0,self.form21_colnums,lambda:PSWaction(row,"send"), shortname,
                bg = self.file_list_button_bg,
                p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',0,E+W+N+S,1,1],
                msg = para['field_name']
                )
            WindX['form_widgets_short'][self.form21_colnums] = bs.b

    def UI_highlight_row(self, event=None, row=0, act=0):
        fcolor = 'black'
        bcolor = 'white'
        if act:
            fcolor = 'green'
            bcolor = '#FFEFD5'

        if WindX['form_widgets'] and WindX['form_widgets'].__contains__(row):
            for i in [5,6,8]:
                try:
                    WindX['form_widgets'][row][i].configure(fg=fcolor, bg=bcolor)
                except:
                    pass

    def WindExit(self):
        UT_ClipboardEmpty()
        if self.root:
            self.root.destroy()
        SaveLog(logFile='', isMainWin=True)
        os._exit(0) 

class ClassMouseClickWatcher():
    def __init__(self,x,y):
        WindX['load_times'].append([time.time(), 'MouseClickWatcher loading: ...'])

        scale = UI_DeviceDisplayScale(x=x, needScaled=True)
        dx = int(100*scale)
        dy = int(15*scale)
        sizes = [dx*3, dy*2]
        xys   = [x-dx*2 - 2, y-dy]

        self.isDisplay = True
        self.x0 = x
        self.y0 = y
        self.tl = None
        self.action = ""

        if WindX['TopLevel_MessageAction']:
            try:
                WindX['TopLevel_MessageAction'].destroy()
                WindX['TopLevel_MessageAction'] = None            
            except:
                pass

        if self.isDisplay:
            UI_ToplevelRect(sizes, xys, icolor='#FF6666')  #F6F6F6
        try:       
            self.im_PIL,err = UT_ScreenShotXY(width=sizes[0],height=sizes[1],xSrc=xys[0],ySrc=xys[1])
            self.OCR_Run()
        except:
            UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())
            UI_ToplevelRectHide()    
    
    def OCR_Run(self, ):
        self.sstime = time.time()

        self.results = {
            'image_to_boxes':None,
            'image_to_data':None,
            'image_to_string': [],
            'image_data_paddle': [],
            'result_parsed': []
        }

        is_to_crop_class = False
        try:       
            if self.im_PIL:
                sizes  = self.im_PIL.size
                pixels = sizes[0]*sizes[1]

                output=BytesIO()
                self.im_PIL.save(output, format='PNG')
                im = Image.open(output)
                #byte_data = output.getvalue()         
                UT_Print2Log('', "\nImage ORC\n--------------------------------------------\nimage.size=", im.size)    

                if not WindX['win_ocr_PaddleOCR']:
                    WindX['win_ocr_PaddleOCR'] = PaddleOCR_Load()
                try:
                    stime = time.time()
                    iOCR = PaddleOCR_Class(PaddleOCR=WindX['win_ocr_PaddleOCR'], im=im, is_to_crop=is_to_crop_class)
                    iOCR.run()
                    """
                    iOCR.results as:
                        self.results = {
                            'image_to_string': [],  #all text in block
                            'image_data_paddle': [],  #all lines [[box1, text1, probability1], [box2, text2, probability2], ...]
                            'result_parsed': [] #all text in sequency
                        }
                    """
                    self.results['image_data_paddle'] = iOCR.results['image_data_paddle']
                    self.results['image_to_string']   = iOCR.results['image_to_string']
                    self.results['result_parsed']     = iOCR.results['result_parsed']

                    if not WindX['win_ocr_used_time'].__contains__('PaddleOCR'):
                        WindX['win_ocr_used_time']['PaddleOCR'] = {}
                    if not WindX['win_ocr_used_time']['PaddleOCR'].__contains__(pixels):
                        WindX['win_ocr_used_time']['PaddleOCR'][pixels] = []

                    WindX['win_ocr_used_time']['PaddleOCR'][pixels].append([stime, time.time()])
                except:
                    UT_Print2Log('red', sys._getframe().f_lineno, "\nTry PaddleOCR and get error:\n" + traceback.format_exc())

                if len(self.results['image_to_string']):
                    if self.isDisplay:
                        ocr_result = []
                        if len(self.results['result_parsed']):
                            ocr_result = self.results['result_parsed'][0]                
                        
                        UI_ClassToplevelMessage("\n".join(ocr_result), 'yellow', 'red', pos=[self.x0, self.y0])

                        if WindX['keyboard_keyAltPress']:
                            UT_ClipboardInertText("\n".join(ocr_result))                

                        UT_Print2Log('green', "\n".join(ocr_result))
                        UT_Print2Log('', self.results['image_to_boxes'])

                    self.ReactionPre(''.join(self.results['image_to_string']))
                #UT_Print2Log('', "\n--------------------------------------------\n")
                output.close()
        except:
            UT_Print2Log('red', sys._getframe().f_lineno, "Try OCR ...,\nand get error:\n" + traceback.format_exc())
            #messagebox.showwarning(title='OCR Warning', message= "Try OCR ...\nthen get the error:\n\n" + traceback.format_exc())

        UT_Print2Log('', sys._getframe().f_lineno, 'Image_OCR_Result used time:', UT_UsedTime(self.sstime), '\n')

        if self.isDisplay:
            t1 = threading.Timer(0.01,UI_ToplevelRectHide)
            t1.start()   

    def ReactionPre(self, text):        
        if re.match(r'.*Password',text,re.I):
            self.action = 'show-send-password'
        elif re.match(r'.*(username|user\s+name|login|logon)',text,re.I):
            self.action = 'show-username'
        elif re.match(r'.*answer',text,re.I):
            self.action = 'show-send-code'
        self.ReactionGo()
        
    def ReactionGo(self):
        UT_Print2Log('blue', "watch click - action=", self.action)
        if not self.action:
            return
        
        elif self.action == 'close':
            try:
                self.tl.destroy()            
            except:
                pass
            WindX['TopLevel_MessageAction'] = None
            return

        try:
            hasButton = 0
            patterns = {
                'show-send-password': '(Password|PSW)',
                'show-username': '(user\s+name|username|\s+ID|Login|\s+name)',
                'show-send-code': 'code'
            }

            findstr = ''
            if patterns.__contains__(self.action):
                findstr = patterns[self.action]

            if findstr:
                for irow in WindX['form_widgets']:
                    field_name = WindX['form_widgets'][irow][0].get()
                    if re.match(r'.*{}'.format(findstr), field_name, re.I):
                        go = True
                        if self.action == 'show-username' and re.match(r'.*{}'.format(patterns['show-send-password']), field_name, re.I):
                            go = False
                        if go:
                            hasButton += 1

            if hasButton == 0:
                return

            self.tl = Toplevel()
            WindX['TopLevel_MessageAction'] = self.tl

            dy = 40          
            pos = win32api.GetCursorPos()
            self.tl.geometry('+'+ str(pos[0]) +'+' + str(pos[1] + dy))
            frm = Frame(self.tl,bg='yellow')
            frm.grid(row=1,column=0,sticky=E+W+S+N,pady=5,padx=5)
            self.xlbl = Label(frm, text='10', justify=CENTER, relief=FLAT,pady=2,padx=2, bg='yellow', fg='#A0A0A0', width=3)
            self.xlbl.grid(row=0,column=0,sticky=E+W,pady=1,padx=1)
            col = 0
            row = 0
            if findstr:        
                delstr = True
                for irow in WindX['form_widgets']:
                    field_name = WindX['form_widgets'][irow][0].get()

                    if re.match(r'.*{}'.format(findstr), field_name, re.I):
                        go = True
                        if self.action == 'show-username' and re.match(r'.*{}'.format(patterns['show-send-password']), field_name, re.I):
                            go = False
                        if go:                        
                            col += 1
                            short = WindX['form_widgets'][irow][2].get()
                            self.ReactionButton(frm, row, col, irow, short, field_name, delstr)
                            if col >= 4:
                                row +=1
                                col = 0
            
            UI_WidgetFontSetAtPoint(wid=self.tl, widName="button", point=[self.x0, self.y0])
            self.tl.wm_attributes('-topmost',1)
            self.tl.overrideredirect(1)
            self.tl.update()

            t1 = threading.Timer(0.1,self.ButtonCloseDelay)
            t1.start()
        except:
            UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())    

    def ButtonCloseDelay(self):
        s = 10
        while True:
            time.sleep(1)
            s = s - 1
            if s <= 0:
                break
            try:
                self.xlbl.configure(text=s)
                self.tl.update()
            except:
                break
        
        self.action = "close"
        self.ReactionGo()

    def ReactionButton(self, frm, row, col, irow, short, field_name, delstr):
        bs = ClassButtonGrid(frm,row,col,lambda:self.ReactionButtonGo(irow,delstr),field_name,p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',0,E+W+N+S,1,1], TexAnchor=W)
        UI_WidgetBalloon(bs.b,  field_name)

    def ReactionButtonGo(self, irow, delstr):
        PSWaction(irow,"send",delstr=delstr)

        try:
            WindX['TopLevel_MessageAction'] = None
            self.tl.destroy()        
        except:
            pass    

class ClassMouseListener():
    def __init__(self,):
        WindX['load_times'].append([time.time(), 'MouseListener loading: ...'])
        with mouseListener(on_click=self.OnClick) as listener: #(on_move=on_move, on_click=on_click, on_scroll=on_scroll) 
            listener.join()

    def OnClick(self, x, y, button, pressed):
        dtime = time.time() - WindX['mouse_last_time_click'][0] 
        #UT_Print2Log('', sys._getframe().f_lineno, dtime, button,'{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
        if not pressed:
            if re.match(r'.*left',str(button),re.I):
                WindX['mouse_click_points'].append([x,y])        
                ForeGroundWindow()
                #UT_Print2Log('', sys._getframe().f_lineno, "mouse click - Foreground Window:", WindX['FGW'])
                UT_ClipboardEmpty()

                if WindX['FGW'][1][0]:
                    WindX['mouse_click_last_points'] = [x,y, time.time(), WindX['FGW'][1][0], WindX['FGW'][1][1]]
                    b = UT_WindowRectGet(WindX['FGW'][1][0])  #left, top, right, bottom
                    UT_Print2Log('', sys._getframe().f_lineno, "Click point ["+ str(x) +", "+ str(y) +"], Foreground Window:", WindX['FGW'][1][1],", relative point (",x - b[0], y - b[1],"), win box=", b)
                #UT_Print2Log('', sys._getframe().f_lineno, 'Click-OCR-Checked:', WindX['ClassWin'].var_Click_Watcher.get())
                else:
                    WindX['mouse_click_last_points'] = []

                if WindX['ClassWin'].var_Click_Watcher.get():
                    p = threading.Timer(0.001,ClassMouseClickWatcher, args=[x,y])
                    p.start()
                else:
                    UI_ToplevelRectHide()

            elif re.match(r'.*middle',str(button),re.I):
                p = threading.Timer(0.001,ClassMouseClickWatcher, args=[x,y])
                p.start()

            '''
            try:
                if dtime <= 1:
                    WindX['mouse_last_time_click'][0] = time.time()
                    if button == mouse.Button.left:
                        WindX['mouse_last_time_click'][1] +=1
                        if WindX['mouse_last_time_click'][1] >=3 and WindX['row_shortname'].__contains__('JPSW'):                    
                            WindX['mouse_last_time_click'] = [time.time(),0,0,0]
                            print("# send password")
                            t4 = threading.Timer(0.1,PSWaction,args=[WindX['row_shortname']['JPSW'],"send"])
                            t4.start()

                    elif button == mouse.Button.middle:
                        WindX['mouse_last_time_click'][2] +=1
                        if WindX['mouse_last_time_click'][2] >=3 and  WindX['row_shortname'].__contains__('JWID'):
                            WindX['mouse_last_time_click'] = [time.time(),0,0,0]
                            print("# send login ID") 
                            t4 = threading.Timer(0.1,PSWaction,args=[WindX['row_shortname']['JWID'],"send"])
                            t4.start()

                    elif button == mouse.Button.right:
                        WindX['mouse_last_time_click'][3] +=1
                        if WindX['mouse_last_time_click'][3] >=3 and WindX['row_shortname'].__contains__('JCOD'):
                            WindX['mouse_last_time_click'] = [time.time(),0,0,0]
                            print("# send security code")
                            t4 = threading.Timer(0.1,PSWaction,args=[WindX['row_shortname']['JCOD'],"send"])
                            t4.start()

                else:
                    WindX['mouse_last_time_click'] = [time.time(),0,0,0]
            except:
                UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())
            '''  

class ClassKeyboardListener():
    def __init__(self,):
        WindX['load_times'].append([time.time(), 'KeyboardListener loading: ...'])
        #return #not record key board input
        # Collect events until released
        with keyboardX.Listener(
                on_press  = self.OnPress,
                on_release= self.OnRelease) as listener:
            listener.join()

    def OnPress(self, key):
        self.KeyPress(key, 'press')

    def OnRelease(self, key):
        #UT_Print2Log('', sys._getframe().f_lineno, '{0} released'.format(key))
        #self.KeyIn(key,'release')

        #if key == keyboardX.Key.esc:
            # Stop listener
        #    return False
        self.KeyPress(key, 'release')
    
    def KeyPress(self, key, act):
        try:
            ikey = key.char
        except AttributeError:
            ikey = key
        #通过属性判断按键类型。
        #print('....', act, type(ikey),ikey)
        try:
            if act == 'press':
                if ikey == keyboardX.Key.alt_l or ikey == keyboardX.Key.alt_r or ikey == keyboardX.Key.alt_gr:
                    WindX['keyboard_keyAltPress'] = True
                #if not ikey in WindX['keyboard_keyPress']:
                #    WindX['keyboard_keyPress'].append(ikey)
                
                elif key == keyboardX.Key.esc:
                    AlertScheduleEnd()

            else:
                if ikey == keyboardX.Key.alt_l or ikey == keyboardX.Key.alt_r or ikey == keyboardX.Key.alt_gr:
                    WindX['keyboard_keyAltPress'] = False
                #WindX['keyboard_keyPress'].remove(ikey)
        except:
            pass
    
    def KeyIn(self, key,act):
        if WindX['ClassWin'].var_Click_Watcher.get():
            try:
                WindX['keys_input_words'].append([time.time(),act,key.char])
            except AttributeError:
                WindX['keys_input_words'].append([time.time(),act,key])
            #通过属性判断按键类型。

    def PrintRecords(self):
        return
        if not len(WindX['keys_input_words']):
            return
        UT_Print2Log('', "\n",sys._getframe().f_lineno, WindX['keys_input_words'])
        WindX['keys_input_words'] = []

class ClassCheckboxGrid:
    def __init__(self,frm,row=0,col=0, cmd=None, txt='', fg='blue', bg='#E0E0E0', ischeck=0,
                    colspan=1, width = 0, msg=None, isList=False, TexAnchor = CENTER,
                    p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',0,E+W+N+S,0,0]):

        if width:
            p[6] = width

        self.variable = IntVar()

        self.b = Checkbutton(
                    frm,
                    text=txt, 
                    variable= self.variable,
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

        if ischeck:
            self.b.select()

        self.b.bind('<Motion>',self.iMotion)
        self.b.bind('<Leave>',self.iLeave)
        self.bg = bg 
        self.txt= txt   
        self.isList=isList
        self.row = row  
        self.balloon = None         
        
        if msg:                
            self.message = msg
            self.balloon = UI_WidgetBalloon(self.b,  msg)
        else:
            self.message = ""

    def iMotion(self,event):
        self.b.config(bg = '#FFFFF0')
        if self.isList:
            WindX['ClassWin'].UI_highlight_row(None,self.row,1)

    def iLeave(self,event):
        self.b.config(bg = self.bg)
        if self.isList:
            WindX['ClassWin'].UI_highlight_row(None, self.row, 0)

class ClassButtonGrid:
    def __init__(self,frm,row=0,col=0,cmd=None,txt='?',fg='blue',bg='#E0E0E0',
                    colspan=1, width = 0, msg=None, isList=False, TexAnchor = CENTER,
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
        self.isList=isList
        self.row = row  
        self.balloon = None         
        
        if msg:                
            self.message = msg
            self.balloon = UI_WidgetBalloon(self.b,  msg)
        else:
            self.message = ""

    def iMotion(self,event):
        self.b.config(bg = '#FFFFF0')
        if self.isList:
            WindX['ClassWin'].UI_highlight_row(None,self.row,1)

    def iLeave(self,event):
        self.b.config(bg = self.bg)
        if self.isList:
            WindX['ClassWin'].UI_highlight_row(None, self.row, 0)

class ClassScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        print("\nClassScrollableFrame, args=", args)
        self.custom_bg = "#E8E8E8"

        self.canvas = Canvas(self, 
            width=500, 
            height=300,
            bg= self.custom_bg, #"#EFEFEF",
            relief=FLAT,
            bd = 0,
        )
        self.canvas.configure(highlightthickness = 0)

        self.scrollbar_y = ttk.Scrollbar(self, orient="vertical",   command=self.canvas.yview)
        #self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)

        gui_style = ttk.Style()
        gui_style.configure('My.TFrame', background= self.custom_bg, padx=0, pady=0, relief=FLAT, bd=0)  #background='#EFEFEF'
        self.scrollable_frame = ttk.Frame(self.canvas,style='My.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.container = container        
        container.bind("<Motion>", self.canvasMotion)
        container.bind("<Leave>",  self.canvasLeave)
        #container.bind("<MouseWheel>",  self.canvasMouseWheel)
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
        #self.canvas.configure(xscrollcommand=self.scrollbar_x.set)

        self.canvas.grid(row=0,column=0,sticky=E+W+N+S,padx=0,pady=0)
        self.scrollbar_y.grid(row=0,column=1,sticky=N+S)
        #self.scrollbar_x.grid(row=1,column=0,sticky=E+W) 

        self.scrollbar_y_show = True

        #- ttkFrame
        #---- canvas (0, 0)
        #-------- scrollable_frame
        #---- scrollbar_y (0,1), scrollbar_y (1,1)

    def canvasMouseWheel(self,e):
        if self.scrollbar_y_show:
            #print("canvasMouseWheel")
            self.canvas.yview_scroll(int(-1*(e.delta/120)), "unit")

    def canvasMotion(self,e):
        return
        self.scrollbar_y.grid()
        self.scrollbar_y_show = True

    def canvasLeave(self, e=None, fixSide='both', action=""):
        #print("\n----------\ncanvasLeave:", e, fixSide, action)
        
        #fit frame22 to window size

        #- root
        #-- frame1
        #-- frame2
        #------ frame21: ⇡ ∧ (quick buttons)
        #------ frame22: 
        #--------- frame221x: 
        #------------- frame2211: Encrypt / Decrypt Code, 
        #------------- frame221 : data list
        #--------- frame222: Open, Save, New, Anchor, Auto

        #- ttkFrame (class)
        #---- canvas (0, 0)
        #-------- scrollable_frame ==> as frame221
        #---- scrollbar_y (0,1), scrollbar_y (1,1)
        
        #print('container=', self.container)

        if not WindX['win_orig_width']:
            print('Not orig_width', WindX['win_orig_width'])
            return

        if WindX['ClassWin'].Frame2Hide_Yes:
            return

        if not WindX['ClassWin'].Frame22Show_Yes:
            return

        try:
            rectCanv = UI_WidgetRectGET(self.canvas)     #left top right bottom (18, 382, 522, 399)
            rectMain = UI_WidgetRectGET(WindX['ClassWin'].root)
            rectFram = UI_WidgetRectGET(self.scrollable_frame)

            CanvW = rectCanv[2] - rectCanv[0]
            CanvH = rectCanv[3] - rectCanv[1]

            MainW = rectMain[2] - rectMain[0]
            MainH = rectMain[3] - rectMain[1]
            geo = re.split(r'x|\+', WindX['ClassWin'].root.geometry())

            FramW = rectFram[2] - rectFram[0]
            FramH = rectFram[3] - rectFram[1]
            FramPadxy = rectFram[0] - rectCanv[0]

            #print("Before Win:", rectMain, MainW, MainH,", Canvas", rectCanv, CanvW, CanvH, ", Frame", rectFram, FramW, FramH, ", bar_oWidth", WindX['yscrollbar_oWidth'])
            refresh_scroll = False

            #1. check width
            if fixSide == 'both' or fixSide == 'width':
                caseText = ""
                if CanvW - (FramW + FramPadxy*2) < 0:
                    CanvW = FramW + FramPadxy*2
                    if MainW > CanvW + WindX['yscrollbar_oWidth']*1.5 + FramPadxy*2:  
                        CanvW = int(MainW - WindX['yscrollbar_oWidth']*1.5 - FramPadxy*2)
                    self.canvas.configure(width = CanvW)
                    refresh_scroll = True

                    if MainW < CanvW + WindX['yscrollbar_oWidth'] + FramPadxy*2:                
                        w = CanvW + WindX['yscrollbar_oWidth'] + FramPadxy*2
                        if w < WindX['win_orig_width']:
                            w = WindX['win_orig_width']
                        pp = str(w) + 'x' + str(MainH) + '+' + str(geo[2]) + '+' + str(geo[3])
                        if not (pp == WindX['ClassWin'].root.geometry()):
                            print("win width #1 ->")
                            UI_WinGeometry(WindX['ClassWin'].root, p= pp)

                    caseText = "case-1\n"

                elif CanvW - (FramW + FramPadxy*2) - WindX['yscrollbar_oWidth']*1.5 > 0 and  MainW < CanvW + WindX['yscrollbar_oWidth'] + FramPadxy*2:
                        CanvW = FramW + FramPadxy*2
                        if MainW  > CanvW + WindX['yscrollbar_oWidth']*1.5 + FramPadxy*2:  
                            CanvW = int(MainW - WindX['yscrollbar_oWidth']*1.5 - FramPadxy*2)                

                        self.canvas.configure(width = CanvW)
                        refresh_scroll = True

                        caseText = "case-2\n"

                elif MainW > CanvW + WindX['yscrollbar_oWidth']*1.5 + FramPadxy*2:
                    CanvW = int(MainW - WindX['yscrollbar_oWidth']*1.5 - FramPadxy*2)
                    self.canvas.configure(width = CanvW)
                    refresh_scroll = True

                    caseText = "case-3\n"

                elif MainW < int(CanvW + WindX['yscrollbar_oWidth']*1.5 + FramPadxy*2):            
                    w = CanvW + WindX['yscrollbar_oWidth'] + FramPadxy*2
                    if w < WindX['win_orig_width']:
                        w = WindX['win_orig_width']  
                    pp = str(int(w)) + 'x' + str(MainH) + '+' + str(geo[2]) + '+' + str(geo[3])
                    if not (pp == WindX['ClassWin'].root.geometry()):   
                        print("win width #2 ->") 
                        UI_WinGeometry(WindX['ClassWin'].root, p= pp)
                        refresh_scroll = True
                        caseText = "case-4\n"

                if caseText:
                    UT_Print2Log('blue',"\nframe22: check and fit to width", caseText)

                if not WindX['win_login_done']:
                    self.scrollbar_y.grid_remove()
                    self.scrollbar_y_show = False
                    return

            #2. check height
            win_height_max = 0.6
            if fixSide == 'both' or fixSide == 'height':
                caseText = ""
                SceenH = MainH
                for dp in WindX['display_scale']:
                    if rectMain[0] >= dp[0] and rectMain[0] < dp[1]:
                        SceenH = dp[5]
                        break

                rectFram1 = UI_WidgetRectGET(WindX['ClassWin'].frame1)
                Fram1H = rectFram1[3] - rectFram1[1]

                rectFram21 = UI_WidgetRectGET(WindX['ClassWin'].frame21)
                Fram21H = rectFram21[3] - rectFram21[1] 

                rectFram2211 = UI_WidgetRectGET(WindX['ClassWin'].frame2211)
                Fram2211H    = rectFram2211[3] - rectFram2211[1]

                rectFram23 = UI_WidgetRectGET(WindX['ClassWin'].frame222)
                Fram23H = rectFram23[3] - rectFram23[1] + Fram21H + Fram2211H

                CanvHmax = int(SceenH*win_height_max) - Fram1H - Fram23H        
                geo = re.split(r'x|\+', WindX['ClassWin'].root.geometry())

                if (FramH + FramPadxy*2 >= CanvHmax*win_height_max and MainH < int(SceenH*win_height_max)) or MainH > int(SceenH*win_height_max):
                    print("win heigt #3 ->")         
                    UI_WinGeometry(WindX['ClassWin'].root, p= geo[0] + 'x' + str(int(SceenH*win_height_max)) + '+' + str(geo[2]) + '+' + str(geo[3]))
                    rectMain = UI_WidgetRectGET(WindX['ClassWin'].root)
                    MainH = rectMain[3] - rectMain[1]
                CanvCurA = MainH - Fram1H - Fram23H

                if FramH + FramPadxy*2 > CanvH and (MainH < int(SceenH*win_height_max) or CanvH < CanvCurA) and (CanvH + Fram1H + Fram23H < int(SceenH*win_height_max)):
                    CanvH = CanvCurA
                    self.canvas.configure(height= CanvH)
                    #UI_WinGeometry(WindX['ClassWin'].root, p= geo[0] + 'x' + str(MainH) + '+' + str(geo[2]) + '+' + str(geo[3]))
                    refresh_scroll = True
                    caseText = "case-5 Height\n"            
                    
                elif (FramH + FramPadxy*4 < CanvH) and CanvH - FramPadxy > CanvHmax:
                    CanvH = FramH + FramPadxy*2
                    self.canvas.configure(height= CanvH)
                    
                    caseText = "case-6 Height\n"

                elif CanvH > CanvCurA:
                    CanvH = CanvCurA
                    self.canvas.configure(height= CanvH)
                    
                    caseText = "case-7 Height\n"

                if caseText:
                    UT_Print2Log('blue',"\nframe22: check and fit to height", caseText)

            rectCanv = UI_WidgetRectGET(self.canvas)
            CanvH = rectCanv[3] - rectCanv[1]
            rectMain = UI_WidgetRectGET(WindX['ClassWin'].root)
            MainH = rectMain[3] - rectMain[1]
            CanvCurA = MainH - Fram1H - Fram23H
            
            refresh_scroll = True
            
            if FramH < CanvCurA:
                self.scrollbar_y.grid_remove()
                self.scrollbar_y_show = False
                refresh_scroll = False
            else:
                self.scrollbar_y.grid()
                self.scrollbar_y_show = True

            if refresh_scroll:
                CanvW = rectCanv[2] - rectCanv[0]
                #print("refresh scroll:", refresh_scroll)          
                self.canvas.configure(scrollregion=(0, 0, CanvW, FramH))
            
            #self.scrollbar_y_show = False
            #self.scrollbar_y.grid_remove()
            #self.scrollbar_x.grid_remove()

            if action == 'add-new-row':
                self.canvas.yview_moveto(1.0)
        except:
            UT_Print2Log('red', sys._getframe().f_lineno, traceback.format_exc())

def main():
    #UT_Print2Log('', "\npyWorkPage (JABIL-OPS-PCMS-Work-Project) -->",re.sub(r'^\s+|\s+$','',re.sub(r'([^a-zA-Z0-9\s])+',UT_ReplaceFunction,'pyWorkPage (JABIL-OPS-PCMS-Work-Project)')), "\n")
    #MSTeams_Get_Calendar()
    #"""
    UT_FolderCreate(WindX['self_folder_log'])

    t1 = threading.Timer(1,ForeGroundWindowsCheck)
    t2 = threading.Timer(1, GUI_Init)
    t3 = threading.Timer(5,ClassMouseListener)
    t4 = threading.Timer(5,ClassKeyboardListener)
    t1.start()  
    t2.start()
    t3.start()
    t4.start()    
    #"""

if __name__ == "__main__":  
    main() 

        