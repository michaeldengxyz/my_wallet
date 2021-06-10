#Pyhton 3.x
# -*- coding: UTF-8 -*-
# rev.2.0.0.0

import time 
import traceback
import re
import os,sys,signal

import win32gui
import win32api
import win32con
import win32com.client
import win32process
import win32clipboard

from tkinter import *
from tkinter import filedialog,messagebox,tix as Tix
import tkinter.font as tf

from pynput import mouse
from pynput.mouse import Listener
from pynput import keyboard as keyboardX

import getpass
import zlib
import base64
import hashlib
from Crypto.Cipher import AES
import json
from ctypes import *
import random, string
import threading
import subprocess
import psutil
import ctypes

WindX  = {}
WindXX = {}
WindX['self_folder'] = re.sub(r'\\','/',os.path.abspath(os.path.dirname(__file__)))
print("\nroot:",WindX['self_folder'])  
sys.path.append(WindX['self_folder'])  
os.chdir(WindX['self_folder'])
WindX['pcName'] = os.environ['COMPUTERNAME']
print("getcwd:",os.getcwd() + "\nDevice Name:",WindX['pcName'])

WindX['main'] = None
WindX['LoginID']  = 'dengm'       
WindX['LoginPSW'] = ''
WindX['LoginSCD'] = '' 
WindX['EncryptCode'] = ''
WindX['mainPX'] = 0
WindX['mainPY'] = 0 
WindX['ShowHideBasic'] = 1
WindX['form_rows'] = 0
WindX['form_widgets'] = {}
WindX['form_widgets_short'] = {}
WindX['e_warnLabel'] = None
WindX['win_pos'] = {'orig_width':0, 'geo_xy':'', 'toolbar_height':0}  
WindX['mouse_click_points'] = []
WindX['TopLevel'] = None
WindX['TopLevel_Label'] = None

def WinFocusOn():    
    if len(WindX['FGW'][1]):
        try:           
            l, t, r, b = get_window_rect(WindX['FGW'][1][0])
            print(".... SetForegroundWindow:",WindX['FGW'][1], l, t, r, b)                    
            win32gui.SetForegroundWindow(WindX['FGW'][1][0])

            x = l + 2
            y = t + 2
            #win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(x/SCREEN_WIDTH*65535.0), int(y/SCREEN_HEIGHT*65535.0))
            win32api.SetCursorPos((x,y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)            
        except:
            print(traceback.format_exc())
    else:
        print(".... Can not catch ForegroundWindow!")

def HideConsole():
    try:
        myfile = re.sub(r'.*(\\|\/)','',sys.argv[0])
        print("\nfile: ",myfile,"\n")
        if re.match(r'.*\.py$',myfile,re.I):
            return
            
        whnd = win32gui.FindWindowEx(0,0,'ConsoleWindowClass',None)
        title  = win32gui.GetWindowText(whnd)
        print(whnd,title)
        if title.endswith(myfile) or re.match(r'.*'+ title +'',myfile,re.I):
            win32gui.ShowWindow(whnd, win32con.SW_HIDE)
    except:
        print(traceback.format_exc())

def EnableEntry(wid=None, state="normal", act=1):
    if not wid:
        return
    try:
        for item in wid.winfo_children():
            #print("-"*act,item)
            if re.match(r'.*\!entry\d*$',str(item),re.I):
                item.configure(state=state)

            if item.winfo_children() :
                EnableEntry(item, state=state, act=act+1)
    except:
        pass

def Clipboard_Empty():
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.CloseClipboard()

def SendStrViaClipboard(text,delstr=False):
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()
        #time.sleep(0.1)

        ctr = keyboardX.Controller()
        if delstr:
            with ctr.pressed(keyboardX.Key.ctrl,"a"):
                pass
            with ctr.pressed(keyboardX.Key.delete):
                pass

        #print(".. paste text from clipboard:", win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)) dengmmeDDY#$JABIL22xSHANGHAI218.107.14.4
        with ctr.pressed(keyboardX.Key.ctrl,"v"):
            pass   
    except:
        win32clipboard.CloseClipboard()
        print(traceback.format_exc())

def get_window_rect(hwnd):
    try:
        f = ctypes.windll.dwmapi.DwmGetWindowAttribute
    except WindowsError:
        f = None
    if f:
        rect = ctypes.wintypes.RECT()
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        f(ctypes.wintypes.HWND(hwnd),
          ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
          ctypes.byref(rect),
          ctypes.sizeof(rect)
          )
        return rect.left, rect.top, rect.right, rect.bottom

def Message(msg, bgColor, fgColor):
    if WindX['TopLevel']:
        WindX['TopLevel_Label'].config(text=msg,bg=bgColor, fg=fgColor)
        return
        #WindX['TopLevel'].destroy()

    WindX['TopLevel'] = Toplevel()
    WindX['TopLevel'].wm_attributes('-topmost',1)        
    pos = win32api.GetCursorPos()
    WindX['TopLevel'].geometry('+'+ str(pos[0]) +'+' + str(pos[1] + 20))
    WindX['TopLevel'].overrideredirect(1)

    font_type = None 
    try:
        font_type = tf.Font(family="Lucida Grande")  #, size=12
    except:
        pass
    label = Label(WindX['TopLevel'], text=msg, justify=LEFT, relief=FLAT,pady=3,padx=3, anchor='w', bg=bgColor, fg=fgColor, font=font_type)
    label.pack(side=TOP, fill=X)
    WindX['TopLevel_Label'] = label

def PSWaction(row=0,act=None):
    #print("psw action",row,act)
    if WindX['TopLevel']:
        WindX['TopLevel'].destroy()
        WindX['TopLevel'] = None

    if WindX['e_warnLabel']:
        try:
            WindX['e_warnLabel'].destroy()
        except:
            pass
        WindX['e_warnLabel'] = None
        
    if act == "send":
        #WindX['form_widgets'][row] = [sv_fieldname, sv_value, bdelete.b, ef, ev, bsend.b]
        #   
        #                            0             1         2          3   4   5        
        WindX['main'].title("My Wallet")    
        if WindX['form_widgets'][row][1].get() == 'LoginCiscoVPN':
            LoginCiscoVPN()
            return

        #print("Action ("+act+") - to Foreground Window:", WindX['FGW'])
        if WindX['FGW'][1][1] == "My Wallet":
            print(".. You can not input to self main window!")
            return

        left, top, right, bottom = get_window_rect(WindX['FGW'][1][0])
        if left + top + right + bottom == 0:
            print(".. Invalid window -", WindX['FGW'][1])
            return

        pos = win32api.GetCursorPos()
        WindX['win_not_sending_key'] = 0
        t = re.sub(r'[^0-9]+','', WindXX['delay2send'].get())
        WindX['e_delay2send'].delete(0,"end")
        if not t:
            t = 0
        else:
            t = int(t)*1
            if t > 10:
                t = 10
        WindX['e_delay2send'].insert(0,str(t))
        
        try:
            if t:               
                tt = int(t)*10
                xmsg = " Sending: "+ WindX['form_widgets'][row][0].get() + ", please set foucs where you need to input!"
                while tt:
                    #WindX['main'].title("{:>02d}".format(tt) + " Sending: "+ WindX['form_widgets'][row][0].get())
                    Message("{:>02d}".format(tt) + xmsg, 'yellow', 'red')
                    WindX['main'].update()
                    time.sleep(0.1)
                    tt = tt - 1
                #WindX['main'].title("Sending ["+ WindX['form_widgets'][row][0].get() +"] now ...")
                Message(xmsg, 'yellow', 'red')
            
            else:
                n = len(WindX['mouse_click_points'])
                if n >= 2:
                    win32gui.SetForegroundWindow(WindX['FGW'][1][0])
                    
                    x = WindX['mouse_click_points'][n - 2][0]
                    y = WindX['mouse_click_points'][n - 2][1]
                    left, top, right, bottom = get_window_rect(WindX['FGW'][1][0])  #win32gui.GetWindowRect(WindX['FGW'][1][0])
                    if x >= left and x <= right and y >= top and y <= bottom:
                        #print(WindX['mouse_click_points'])
                        print("Click to focus on this point (",x, y,")", WindX['FGW'][1])
                        imouse = mouse.Controller()
                        imouse.position = (x, y)
                        time.sleep(0.2)
                        imouse.click(mouse.Button.left, 1)
                    else:
                        WinFocusOn()
                else:
                    WinFocusOn()

            kstr = str(WindX['form_widgets'][row][1].get())
            #print('send key string:', kstr )

            fgwHandle = win32gui.GetForegroundWindow()
            if fgwHandle and win32gui.GetWindowText(fgwHandle) == "My Wallet":
                print(".. You can not input to self main window!")
                if WindX['TopLevel']:
                    WindX['TopLevel'].destroy()
                    WindX['TopLevel'] = None
                return
            elif not fgwHandle:
                print(".. No focus foreground window!")
                if WindX['TopLevel']:
                    WindX['TopLevel'].destroy()
                    WindX['TopLevel'] = None
                return

            SendStrViaClipboard(kstr)
            #kb = keyboardX.Controller()
            #kb.type(kstr)   #please make sure your keyboard with a right language setting

            WindX['win_not_sending_key'] = 1
            WindX['mouse_click_points'] = []

            if not t:
                time.sleep(0.2)
                win32api.SetCursorPos(pos)
        except:
            print(traceback.format_exc())

    elif act == "delete":
        #delete the row
        for i in range(4,len(WindX['form_widgets'][row])):
            #print(WindX['form_widgets'][row][i])
            WindX['form_widgets'][row][i].grid_remove()

        del WindX['form_widgets'][row]

        if WindX['form_widgets_short'].__contains__(row):
            WindX['form_widgets_short'][row].destroy()
        #print(WindX['form_widgets'])

    elif act == "save":
        if not InputCheck():
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
                    'ischeck' : WindX['form_widgets'][irow][3].get()
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
                fdata = CryptMe(json.dumps(data),key=GetMD5(WindX['EncryptCode']), isEncript=True)
                Save2File(fdata, filename)
        else:
            print("No data to save in your wallet!")
            messagebox.showwarning(title='Warning', message="No data to save in your wallet!")

    elif act == "get":
        if not InputCheck():
            return        

        filename = filedialog.askopenfilename(
                    filetypes= [('data files', '.dat')], 
                    defaultextension='.dat',
                    initialdir= WindX['self_folder'],
                    title= "Open File"
                    )
        if filename:
            try:
                WindX['win_pos'] = {'orig_width':0, 'geo_xy':'', 'toolbar_height':0}
                
                fdata = OpenFile(filename)
                data  = json.loads(CryptMe(fdata,key=GetMD5(WindX['EncryptCode']), isEncript=False))

                #print(data)
                if data.__contains__('1'):     
                    if WindX['Frame3_colnum'] > 1:               
                        for i in range(2,WindX['Frame3_colnum']+1):
                            if WindX['form_widgets_short'].__contains__(i):
                                WindX['form_widgets_short'][i].destroy()

                    for irow in WindX['form_widgets']:
                        for i in range(4,len(WindX['form_widgets'][irow])):
                            #print(WindX['form_widgets'][row][i])
                            WindX['form_widgets'][irow][i].destroy()

                    WindX['form_widgets'] = {}
                    WindX['form_rows'] =1
                    WindX['form_widgets_short'] = {}
                    WindX['Frame3_colnum'] = 1                    

                    for i in data:
                        if not i == 'others':
                            if not data[i].__contains__('field_name_short'):
                                data[i]['field_name_short'] = ''
                            if not data[i].__contains__('ischeck'):
                                data[i]['ischeck'] = 0

                            UIaddNewRow(WindX['Frame1'], 
                                        {'field_name' : data[i]['field_name' ],
                                        'field_value': data[i]['field_value'],
                                        'field_name_short': data[i]['field_name_short'],
                                        'ischeck': data[i]['ischeck']
                                        })
                else:
                    print("No data in your wallet!")
                    messagebox.showwarning(title='Warning', message="No data in your wallet!")
            except:
                print(traceback.format_exc())

    elif act == 'new':
        para = {
            'field_name': 'new field ' + str(WindX['form_rows'] + 1),
            'field_value': '',
            'field_name_short': '',
            'ischeck': 0
        }

        UIaddNewRow(WindX['Frame1'], para, True)

    elif act == 'Anchor':
        WinAnchor()

    elif act == 'LoginCiscoVPN':
        LoginCiscoVPN()

    WindX['main'].title("My Wallet")
    SeeMe(None,WindX['e_EncryptCode'],'*')

    if WindX['TopLevel']:
        WindX['TopLevel'].destroy()
        WindX['TopLevel'] = None

def WinAnchor():
    #gs = re.split(r'x|\+', WindX['main'].geometry()) #506x152+-1418+224
    WindX['main'].geometry('+0+0')

def processinfo(processName):
    pids = psutil.pids()
    res = False
    for pid in pids:
        # print(pid)
        p = psutil.Process(pid)
        try:
            #print(p.name())
            if str(p.name()).upper() == str(processName).upper():
                print('--- killing pid ', pid)
                print(os.popen('taskkill.exe /pid '+str(pid)))
                res = True  # 如果找到该进程则打印它的PID，返回true
                break
        except:
            pass

    return res  # 没有找到该进程，返回false

def LoginCiscoVPN():
    print("\nLogin Cisco VPN ...")
    
    if not (WindX['LoginPSW'] and WindX['LoginSCD']):
        return

    hwnd = win32gui.FindWindow(0, 'Cisco AnyConnect Secure Mobility Client')
    if hwnd:
        print(hwnd, win32gui.GetWindowText(hwnd),'--- existing!')
        print("Find and kill vpnui.exe process:", processinfo('vpnui.exe'))
        #return

    t1 = threading.Timer(1,LoginCiscoVPN_Open)
    t1.start() 

    isVPNopen = 0
    hwnd = None
    while not isVPNopen:
        hwnd = win32gui.FindWindow(0, 'Cisco AnyConnect Secure Mobility Client')
        if hwnd:
            isVPNopen = 1
        else:
            print("\t... wait for: Cisco AnyConnect Secure Mobility Client, 3 seconds")
            time.sleep(3)

    if hwnd:
        win32gui.SetForegroundWindow(hwnd)
        imouse = mouse.Controller()
        keyboard = keyboardX.Controller()
        
        #Title = Cisco AnyConnect Secure Mobility Client
        fgwHandle1 = Wind_Input_Submit('Input IP',hwnd,[180, 112, 340, 112], imouse,keyboard, '218.107.14.4')
        if fgwHandle1 and (not fgwHandle1 == hwnd) and win32gui.GetWindowText(fgwHandle1)=='Cisco AnyConnect Secure Mobility Client':
            #Title = Cisco AnyConnect Secure Mobility Client
            fgwHandle2 = Wind2ClickButton('Confirmed IP 218.107.14.4',fgwHandle1, [250, 288],imouse)
            if fgwHandle2 and (not fgwHandle2 == fgwHandle1) and win32gui.GetWindowText(fgwHandle2)=='Cisco AnyConnect | 218.107.14.4':
                #Title = Cisco AnyConnect | 218.107.14.4
                fgwHandle3 = Wind_Input_Submit('Input Password',fgwHandle2,[155, 146, 220, 204], imouse,keyboard, WindX['LoginPSW'])

                if fgwHandle3 and (not fgwHandle2 == fgwHandle3) and win32gui.GetWindowText(fgwHandle3)=='Cisco AnyConnect | 218.107.14.4':
                    #Title = Cisco AnyConnect | 218.107.14.4
                    fgwHandle4 = Wind_Input_Submit('Input Code Option',fgwHandle3,[145, 85, 188, 253], imouse,keyboard, '3')

                    if fgwHandle4 and (not fgwHandle4 == fgwHandle3) and win32gui.GetWindowText(fgwHandle4)=='Cisco AnyConnect | 218.107.14.4':
                        #Title = Cisco AnyConnect | 218.107.14.4
                        fgwHandle5 = Wind_Input_Submit('Input Code value',fgwHandle4,[145, 89, 188, 253], imouse,keyboard, WindX['LoginSCD'])

                        if fgwHandle5 and (not fgwHandle4 == fgwHandle5) and win32gui.GetWindowText(fgwHandle5)=='Cisco AnyConnect':
                            #Title = Cisco AnyConnect
                            Wind2ClickButton('Accept and complete',fgwHandle5, [216, 187],imouse)
                        else:
                            print("\n--- Catch wrong window (5 Accept and complete):", win32gui.GetWindowText(fgwHandle5), fgwHandle5, fgwHandle4)
                    else:
                        print("\n--- Catch wrong window (4 Input Code value):", win32gui.GetWindowText(fgwHandle4), fgwHandle4, fgwHandle3) 
                else:
                    print("\n--- Catch wrong window (3 Input Code Option):", win32gui.GetWindowText(fgwHandle3), fgwHandle3, fgwHandle2)
            else:
                print("\n--- Catch wrong window (2 Input Password):", win32gui.GetWindowText(fgwHandle2), fgwHandle2, fgwHandle1)
        else:
            print("\n--- Catch wrong window (1 Confirmed IP):", win32gui.GetWindowText(fgwHandle1), fgwHandle1, hwnd)

def LoginCiscoVPN_Open():    
    p = subprocess.Popen('C:/Program Files (x86)/Cisco/Cisco AnyConnect Secure Mobility Client/vpnui.exe', shell=True)

def Wind_Input_Submit(todo,hwnd,offsetXY,imouse,keyboard,str_in):
    print("\n" + todo, hwnd,offsetXY,imouse,keyboard,str_in)
    rect = get_window_rect(hwnd)  #left, top, right, bottom
    print(hwnd, win32gui.GetWindowText(hwnd), rect)
    win32gui.SetForegroundWindow(hwnd)

    x = rect[0] + offsetXY[0]
    y = rect[1] + offsetXY[1]
    print("Click on this point (",x, y,")")
    imouse.position = (x, y)
    time.sleep(1)
    imouse.click(mouse.Button.left, 1)

    '''
    with keyboard.pressed(keyboardX.Key.ctrl):
        keyboard.press('a')
        keyboard.release('a')

    for i in range(100):
        keyboard.press(keyboardX.Key.backspace)
        keyboard.release(keyboardX.Key.backspace)

    keyboard.type(str_in)
    '''
    SendStrViaClipboard(str_in,delstr=True)

    x = rect[0] + offsetXY[2]
    y = rect[1] + offsetXY[3]
    print("Click on this point (",x, y,")")
    imouse.position = (x, y)
    time.sleep(1)
    imouse.click(mouse.Button.left, 1)

    time.sleep(5)
    return win32gui.GetForegroundWindow()

def Wind2ClickButton(todo,hwnd,offsetXY,imouse):
    print("\n" + todo)

    rect = get_window_rect(hwnd)  #left, top, right, bottom
    print(hwnd, win32gui.GetWindowText(hwnd), rect)

    x = rect[0] + offsetXY[0]
    y = rect[1] + offsetXY[1]
    print("Click on this point (",x, y,")")
    imouse.position = (x, y)
    time.sleep(1)
    imouse.click(mouse.Button.left, 1)

    time.sleep(5)
    return win32gui.GetForegroundWindow()

def FindChildWinds(wxs, hwnd, xhwndChild= None,wantedClass= None, wantedText= None):
    if not wxs.__contains__(hwnd):
        wxs[str(hwnd)] = {}

    go = 1
    c = 0
    checkedChilds = {}
    while go:
        print(c, hwnd, xhwndChild, wantedClass, wantedText)
        hwndChild = win32gui.FindWindowEx(hwnd, xhwndChild, wantedClass, wantedText)
        if hwndChild:
            if not wxs[str(hwnd)].__contains__(str(hwndChild)):
                print("\t",hwnd, hwndChild, 'Class:[' + str(win32gui.GetClassName(hwndChild)) + ']  Text:['+  str(win32gui.GetWindowText(hwndChild)) + ']',"\n")
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
                go = 0

    #for hwndChild in wxs[str(hwnd)]:
    #    FindChildWinds(wxs[str(hwnd)][hwndChild], hwndChild, None, wantedClass, wantedText)

def OpenFile(filepath):    
    print("\t.... Open file:",filepath)
    try:
        if os.path.exists(filepath):  
            buffer = b''   
            with open(filepath,'rb') as f:   
                buffer = f.read()   
                f.close()

            return buffer
    except:
        print(traceback.format_exc())   

def Save2File(data,filepath):    
    print("\t.... Save to file:",filepath)
    try:
        if os.path.exists(filepath):       
            os.unlink(filepath) 
            
        with open(filepath,'wb+') as f:   
            f.write(data)   
    except:
        print(traceback.format_exc())    

def CryptMe(instring,key=None,isEncript=True):    
        
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
            #print("\n\t.. Encrypt ..."); 
            fdata['data'] = zlib.compress(fdata['string'].encode(encoding='UTF-8',errors='ignore'))       
            if(fdata['data']):         
                ckey = re.sub(r'-','',fdata['key']); 
                #print("\t\tEncrypted:\n\t\t-- KEY: "+ fdata['key']) 

                cryptor = AES.new(ckey.encode('utf-8'),AES.MODE_CBC,str(ckey[0:16]).encode('utf-8'))                       
                fdata['data'] = base64.b64encode(cryptor.encrypt(pad_text(fdata['data']))); 
                
                #print("\t\t-- KEYSIZE: "+str(len(ckey))+"\n\t\t-- BLOCKSIZE: "+str(AES.block_size)+"\n\t\t-- IV: "+ckey[0:16])
            
                fdata['sizeZ']= len(fdata['data'])
                if(fdata['sizeZ']):
                    fdata['rateC'] = "{:0.2f}".format(fdata['size']/fdata['sizeZ'])
            else:
                print("\t.. Failed to compress!\n")        
            
            #print("\t.. Compressed: before size="+str(fdata['size'])+" "+unit+", after size="+str(fdata['sizeZ'])+", compressed rate "+str(fdata['rateC'])+"\n") dhkaads
        else:
            #print("\n\t.. Decrypt ..."); 
            ckey = re.sub(r'-','',fdata['key']); 
            cryptor = AES.new(ckey.encode('utf-8'),AES.MODE_CBC,str(ckey[0:16]).encode('utf-8'))  
            fdata['data'] = cryptor.decrypt(base64.b64decode(fdata['string'])); 
            fdata['data'] = zlib.decompress(fdata['data']).decode(encoding='UTF-8',errors='ignore') 
    except:
        print(traceback.format_exc()) 

    #print('In: ',instring,'\nout: ',fdata['data'],'\n')
    return fdata['data']

def pad_text(s):
    '''Pad an input string according to PKCS#7''' #
    BS = AES.block_size
    return s + (BS - len(s) % BS) * chr(BS - len(s) % BS).encode("utf-8")

def GetMD5(instring):
    return str(hashlib.md5(instring.encode(encoding='UTF-8',errors='strict')).hexdigest()).upper()

def RandomKey(n=1):
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

def IsTrue(obj):
    #print(type(obj),obj)
    if(type(obj) == numpy.ndarray and obj.any()):
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

def CapLockStatus(event,e=None): 
    #print(event,':',e)   
    if win32api.GetKeyState(win32con.VK_CAPITAL) == 1:
        #print ("CAPS Lock is on.") 
        if e:
            e.configure(background='#FFFF66')
        
    elif win32api.GetKeyState(win32con.VK_CAPITAL) == 0:
        #print ("CAPS Lock is off.")
        if e:
            e.configure(background='#FFFFFF')

    SeeMe(event,e)

def WindExit():       
    Clipboard_Empty()
    if WindX['TopLevel']:
        WindX['TopLevel'].destroy()
        WindX['TopLevel'] = None

    WindX['main'].destroy()    
    os._exit(0)
    #sys.exit(0)  # This will cause the window error: Python has stopped working ...

def SeeMe(event,e=None,ishow=''):
    e.config(show=ishow)
    return

def handlerAdaptor(fun,**kwds):
    return lambda event,fun=fun,kwds=kwds:fun(event,**kwds) 

def DefTmp():
    return None

def InputCheck():    
    yes = 1
    try:
        WindX['EncryptCode'] = WindXX['EncryptCode'].get()       
        if not WindX['EncryptCode']:
            yes = 0
            print('Please input: Encrypt / Decrypt Code!')
            messagebox.showwarning(title='Warning', message='Please input: Encrypt / Decrypt Code!')
    except:
        pass
        
    return yes   

def ShowHideBasic():
    if not WindX['win_pos']['orig_width']:
        WindX['win_pos']['orig_width'] = WindX['main'].winfo_width()        

    if WindX['ShowHideBasic'] == 1:
        EnableEntry(wid=WindX['main'], state="disabled", act=1)

        WindX['ShowHideBasic'] = 0
        WindX['Frame1'].grid_remove()
        WindX['Frame2'].grid_remove()
        WindX['e_HideBase'].config(text="  ∨ ")
        geos = re.split(r'\D',WindX['main'].geometry(),re.I)
        WindX['win_pos']['geo_xy'] = geos[2]

        if not WindX['win_pos']['toolbar_height']:
            WindX['main'].update()
            WindX['win_pos']['toolbar_height'] = WindX['main'].winfo_height()

        WindX['main'].geometry(str(WindX['win_pos']['orig_width']) + 'x' + str(WindX['win_pos']['toolbar_height']) + '+' + WindX['win_pos']['geo_xy'])
        WindX['main'].overrideredirect(1)
    else:
        EnableEntry(wid=WindX['main'], state="normal", act=1)

        WindX['main'].geometry("")
        WindX['ShowHideBasic'] = 1
        WindX['Frame1'].grid()
        WindX['Frame2'].grid()
        WindX['e_HideBase'].config(text="  ∧ ")
        WindX['main'].overrideredirect(0)

def Init(IsInit=1):          
    WindX['main'] = Tix.Tk()
    WindX['main'].title("My Wallet")
    WindX['main'].configure(bg='#A0A0A0')
    WindX['main'].geometry('+' + str(WindX['mainPX']) + '+' + str(WindX['mainPY']))
    WindX['main'].wm_attributes('-topmost',1) 
    #WindX['main'].overrideredirect(1)
    WindX['main'].protocol("WM_DELETE_WINDOW", WindExit)

    WindX['Frame3'] = Frame(WindX['main'],bg='#E0E0E0')
    WindX['Frame3'].grid(row=0,column=0,sticky=E+W+S+N,pady=0,padx=0)

    WindX['Frame1'] = Frame(WindX['main'],bg='#E0E0E0')
    WindX['Frame1'].grid(row=1,column=0,sticky=E+W+S+N,pady=1,padx=0)
    WindX['Frame2'] = Frame(WindX['main'],bg='#E0E0E0')
    WindX['Frame2'].grid(row=2,column=0,sticky=E+W+S+N,pady=0,padx=0)
    
    balstatus = Label(WindX['main'], justify=CENTER, relief=FLAT,pady=3,padx=3, bg='yellow',wraplength = 50)
    #balstatus.grid(row=4,column=0,sticky=E+W+S+N,pady=0,padx=0)
    WindX['winBalloon'] = Tix.Balloon(WindX['main'], statusbar = balstatus)

    hideshow_icon = '  ∧  '

    if WindX['Frame1']:
        WindX['form_rows'] +=1

        row = 0  
        Label(WindX['Frame1'], text='Encrypt / Decrypt Code', justify=CENTER, relief=FLAT,pady=3,padx=3, bg='#E0E0E0').grid(row=row,column=0,sticky=E+W,columnspan=2)
        WindXX['EncryptCode'] = StringVar()
        e=Entry(WindX['Frame1'], justify=LEFT, relief=FLAT, textvariable= WindXX['EncryptCode'], show="*")
        e.grid(row=row,column=2,sticky=E+W,columnspan=2,pady=0,padx=1)
        e.insert(0,WindX['EncryptCode'])
        e.bind('<FocusIn>',func=handlerAdaptor(CapLockStatus,e=e))
        e.bind('<KeyRelease>',func=handlerAdaptor(CapLockStatus,e=e))
        e.bind('<Leave>',func=handlerAdaptor(SeeMe,e=e,ishow='*'))
        e.focus()
        WindX['e_EncryptCode'] = e

        WindXX['delay2send'] = StringVar()
        e2=Entry(WindX['Frame1'], justify=CENTER, relief=FLAT, textvariable= WindXX['delay2send'])
        e2.grid(row=row,column=4,sticky=E+W,columnspan=2,pady=0,padx=1)
        e2.insert(0,0)
        WindX['e_delay2send'] = e2
        WindX['winBalloon'].bind_widget(e2, balloonmsg= 'Delay to send, seconds after click')

    if WindX['Frame2']: 
        row = 0 
        iButton(WindX['Frame2'],row,0,lambda:PSWaction(0,"get"),'Open', width=10) 
        #iSeparator(WindX['Frame2'],row,1)
        
        iButton(WindX['Frame2'],row,2,lambda:PSWaction(0,"save"),'Save', width=10)  
        #iSeparator(WindX['Frame2'],row,3)    

        b = iButton(WindX['Frame2'],row,4,lambda:PSWaction(0,"new"),'New', width=10)  
        #iSeparator(WindX['Frame2'],row,5)
        WindX['winBalloon'].bind_widget(b.b, balloonmsg= 'Add new row')

        b = iButton(WindX['Frame2'],row,6,lambda:PSWaction(0,"Anchor"),'Anchor', width=10)  
        WindX['winBalloon'].bind_widget(b.b, balloonmsg= 'Anchor at the point (0,0)')

        b = iButton(WindX['Frame2'],row,7,lambda:PSWaction(0,"LoginCiscoVPN"),'Cisco VPN', width=10)  
        WindX['winBalloon'].bind_widget(b.b, balloonmsg= 'Login Cisco VPN')
        
    if WindX['Frame3']: 
        b = iButton(WindX['Frame3'],0,1,ShowHideBasic,hideshow_icon, width=4)
        WindX['e_HideBase'] = b.b  
        WindX['ShowHideBasic'] = 1

        WindX['Frame3_colnum'] = 1

        xlbl = Label(WindX['Frame3'], text='Input [Code], then [Open] to load data ...', justify=CENTER, relief=FLAT,pady=3,padx=3, bg='yellow')
        xlbl.grid(row=0,column=2,sticky=E+W,columnspan=2)
        WindX['e_warnLabel'] = xlbl

    HideConsole()
    mainloop()

def ColumnPadx(col):
    if col % 2:
        return 1
    else:
        return 0

def UIaddNewRow(form, para,addNew=None):
    WindX['form_rows'] +=1
    row = WindX['form_rows']
    col = 0
    pady_row = 0
    if WindX['form_rows'] % 2:
        pady_row = 1
    
    sv_ischeck = IntVar()
    ef_chkb = Checkbutton(form, text= WindX['form_rows'] - 1, variable= sv_ischeck, justify=LEFT, fg='#009900', bg='#E0E0E0', relief=FLAT)
    ef_chkb.grid(row=WindX['form_rows'],column=col,sticky=E+W+N+S,padx=ColumnPadx(col),pady=pady_row)
    if para['ischeck']:
        ef_chkb.select()
    WindX['winBalloon'].bind_widget(ef_chkb, balloonmsg= 'Checked to show on the toolbar')

    col +=1
    sv_fieldname = StringVar()
    ef=Entry(form, justify=LEFT, relief=FLAT, textvariable= sv_fieldname, width=30)
    ef.grid(row=WindX['form_rows'],column=col,sticky=E+W+N+S,padx=ColumnPadx(col),pady=pady_row)
    ef.insert(0,para['field_name'])
    ef.bind('<FocusIn>',func=handlerAdaptor(CapLockStatus,e=ef))
    ef.bind('<KeyRelease>',func=handlerAdaptor(CapLockStatus,e=ef))
    if addNew:
        ef.focus()
    WindX['winBalloon'].bind_widget(ef, balloonmsg= 'Field Name')

    col +=1
    sv_fieldnameShort = StringVar()
    efs=Entry(form, justify=LEFT, relief=FLAT, textvariable= sv_fieldnameShort,width=6)
    efs.grid(row=WindX['form_rows'],column=col,sticky=E+W+N+S,padx=ColumnPadx(col),pady=pady_row)
    efs.insert(0,para['field_name_short'])
    efs.bind('<FocusIn>',func=handlerAdaptor(CapLockStatus,e=ef))
    efs.bind('<KeyRelease>',func=handlerAdaptor(CapLockStatus,e=ef))
    WindX['winBalloon'].bind_widget(efs, balloonmsg= 'Short Field Name')
    
    col +=1
    sv_value = StringVar()
    ev=Entry(form, justify=LEFT, relief=FLAT, textvariable= sv_value, show="*", width=30)
    ev.grid(row=WindX['form_rows'],column=col,sticky=E+W+N+S,padx=ColumnPadx(col),pady=pady_row)
    ev.insert(0,para['field_value'])
    ev.bind('<FocusIn>',func=handlerAdaptor(CapLockStatus,e=ev))
    ev.bind('<KeyRelease>',func=handlerAdaptor(CapLockStatus,e=ev))
    ev.bind('<Leave>',func=handlerAdaptor(SeeMe,e=ev,ishow='*'))  
    WindX['winBalloon'].bind_widget(ev, balloonmsg= 'Field Value to be sent')

    col +=1
    bsend = iButton(form,WindX['form_rows'],col,lambda:PSWaction(row,"send"),'Send',p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',6,E+W+N+S,pady_row,ColumnPadx(col)])
    WindX['winBalloon'].bind_widget(bsend.b, balloonmsg= 'Send field value of ' + para['field_name'])

    col +=1
    bdelete = iButton(form,WindX['form_rows'],col,lambda:PSWaction(row,"delete"),'x',fg='red',p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',3,E+W+N+S,pady_row,ColumnPadx(col)])
    WindX['winBalloon'].bind_widget(bdelete.b, balloonmsg= 'Delete this row')

    WindX['form_widgets'][WindX['form_rows']] = [sv_fieldname,sv_value, sv_fieldnameShort, sv_ischeck, bdelete.b, ef, ev, bsend.b, efs, ef_chkb]

    if para['field_name_short'] and WindX['Frame3'] and para['ischeck']:
        WindX['Frame3_colnum'] +=1
        bs = iButton(WindX['Frame3'],0,WindX['Frame3_colnum'],lambda:PSWaction(row,"send"),para['field_name_short'],p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',4,E+W+N+S,1,1])
        WindX['form_widgets_short'][WindX['Frame3_colnum']] = bs.b
        WindX['winBalloon'].bind_widget(bs.b, balloonmsg= para['field_name'])

    if para['field_name_short'] == 'JPSW':
        WindX['LoginPSW'] = para['field_value']
    elif para['field_name_short'] == 'JCOD':
        WindX['LoginSCD'] = para['field_value']
    elif para['field_name_short'] == 'JWID':
        WindX['LoginID']  = para['field_value']

class iSeparator:
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
                        
class iButton:
    def __init__(self,frm,row=0,col=0,cmd=None,txt='?',fg='blue',bg='#E0E0E0',
                    colspan=1, width = 0,
                    p=[LEFT,FLAT,3,1,'#FFFF66','#FFFF99',0,E+W+N+S,0,0]):

        if width:
            p[6] = width

        self.b = Button( frm, 
                    text=txt, 
                    fg=fg,
                    bg=bg,
                    justify=p[0], 
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
        
    def iMotion(self,event):
        self.b.config(bg = '#FFFFF0')

    def iLeave(self,event):
        self.b.config(bg = self.bg)

def main():
    Init()

def ForeGroundWindow():
    try:
        fgwHandle = win32gui.GetForegroundWindow()
        if fgwHandle and WindX['win_not_sending_key']:
            title = win32gui.GetWindowText(fgwHandle)
            if title == "My Wallet":
                return
            WindX['FGW'][1] = [fgwHandle, title]

            '''
            if len(WindX['FGW'][1]) == 0:
                WindX['FGW'][1] = [fgwHandle, win32gui.GetWindowText(fgwHandle)]
                #print("FGW", WindX['FGW'])

            elif len(WindX['FGW'][2]) == 0:
                WindX['FGW'][2] = [fgwHandle, win32gui.GetWindowText(fgwHandle)]
                #print("FGW", WindX['FGW'])

            elif not (fgwHandle == WindX['FGW'][2][0]):
                WindX['FGW'][1] = WindX['FGW'][2]
                WindX['FGW'][2] = [fgwHandle, win32gui.GetWindowText(fgwHandle)]
                #print("FGW", WindX['FGW'])
            '''
    except:
        print(traceback.format_exc()) 

def ForeGroundWindowsCheck():
    WindX['FGW'] = {1:[],2:[]}

    while True:
        ForeGroundWindow()
        time.sleep(0.1)

def MouseOnClick(x, y, button, pressed):
    #print(button,'{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
    if re.match(r'.*left',str(button),re.I) and (not pressed):
        WindX['mouse_click_points'].append([x,y])
        ForeGroundWindow()
        #print("mouse click - Foreground Window:", WindX['FGW'])

def MouseOnMove(x, y):
    try:
        if WindX['TopLevel']: 
            WindX['TopLevel'].geometry('+'+ str(x) +'+' + str(y + 20))
    except:
        pass

def MouseListener():
    with Listener(on_click=MouseOnClick, on_move=MouseOnMove) as listener: #(on_move=on_move, on_click=on_click, on_scroll=on_scroll) 
        listener.join()


if __name__ == "__main__": 
    WindX['win_not_sending_key'] = 1

    delaySeconds = 1
    t1 = threading.Timer(delaySeconds,ForeGroundWindowsCheck)
    t2 = threading.Timer(delaySeconds,main)
    t3 = threading.Timer(delaySeconds,MouseListener)
    t1.start()  
    t2.start()
    t3.start()
        