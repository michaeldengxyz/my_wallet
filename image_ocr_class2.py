#Pyhton 3.x
# -*- coding: UTF-8 -*-
#rev 0.1
#image ocr class

import sys, os, re
import threading
import time
import traceback
import numpy

from PIL import Image
from io import BytesIO
from paddleocr import PaddleOCR
from colorama import init
init(autoreset=True) #set this True to print color fonts in the console

#class input: image as isinstance(im, Image.Image)
#class output: recognized text and frame coordinates [left top right bottom]
"""
return as:
    self.results = {
        'image_to_string': [],  #all text in block
        'image_data_paddle': [],  #all lines [[box1, text1, probability1], [box2, text2, probability2], ...]
        'result_parsed': [] #all text in sequency
    }
"""

class PaddleOCR_Class():
    def __init__(self, im=None, filepath="", PaddleOCR=None, zoom_ocr=2.5, is_to_crop=True, diplay_row_number=False):
        self.image_in = None
        self.is_to_crop = is_to_crop
        self.errors  = []
        self.cropframes = []
        self.izoom = zoom_ocr
        self.win_ocr_crop_layers = {
                1: 0,
                2: 0
            }

        self.PaddleOCR = None
        if PaddleOCR:
            self.PaddleOCR = PaddleOCR

        if filepath and os.path.exists(filepath):
            im = Image.open(filepath)

        if isinstance(im, Image.Image):            
            self.output= BytesIO()
            im.save(self.output, format='PNG')
            ##byte_data = output.getvalue()
            im = Image.open(self.output)
            im = im.convert('RGB') #!!!! have to convert the image to RGB 3 channels!!!!!
            self.image_in = im
        else:
            self.errors.append("image is not valid!!")

        self.results = {
            'image_to_string': [],
            'image_data_paddle': [],
            'result_parsed': []
        }
        self.cropframes = []
        self.stime = time.time()

        self.parse_text_add_row_number = diplay_row_number

    def run(self, ):
        if not self.image_in:
            return

        if not self.PaddleOCR:
            PaddleOCR_Load(self)

        if not self.PaddleOCR:
            self.output.close()
            print("\n-------- Image_OCR_Result - Failed, used time " + self.usedTime() + " --------")
            return

        self.results = {
            'image_to_string': [],
            'image_data_paddle': [],
            'result_parsed': []
        }
        self.cropframes = []

        try:
            self.stime = time.time()

            if self.is_to_crop:
                self.cropframes = self.Image_cleanUp()
                
            if not len(self.cropframes): #[[boxes, box, ny, nx], [...]]
                boxes = []
                box   = [0,0,self.image_in.size[0],self.image_in.size[1]]
                boxes.append(box)
                ny = 1
                nx = 1
                self.cropframes.append([boxes, box, ny, nx])
            #return
            print("\nwin_ocr_crop_layers=", self.win_ocr_crop_layers,"\n")

            imssX = []
            for cfs in self.cropframes:  #cfs: [boxes, box, ny, nx]
                    for cf in cfs[0]:
                        try:
                            imssX.append([cf[0],cf[1], self.image_in.crop(cf), cf, cfs[2], cfs[3]])  #[x0, y0, im_crop, box, ny, nx]  
                        except:
                            print(cf, cfs[2], cfs[3])
                            print(sys._getframe().f_lineno, "\ncrop image:\n" + traceback.format_exc())
   
            print("\nimage size:", self.image_in.size, '-->',str(len(imssX)) + 'X', ", used time " + self.usedTime() + "\n")
            
            print(sys._getframe().f_lineno, "Try PaddleOCR ...")
            try:
                i = 0
                print("")
                threads = []
                Go_This_Way_No_Threads = True #False - the multiple threads will kill the app!!!

                for im in imssX: 
                    i+=1
                    
                    if Go_This_Way_No_Threads:
                        self.PaddleOCR_Go(i, im)
                    else:
                        threads.append(threading.Thread(target=self.PaddleOCR_Go, args=[i, im]))

                if not Go_This_Way_No_Threads: #the multiple threads will kill the app!!!
                    for t in threads:
                        t.start()
                    for t in threads:
                        t.join()

                print("")    
                #print(results,"\n\n")
            except:
                print(sys._getframe().f_lineno, "\nTry PaddleOCR and get error:\n" + traceback.format_exc())

            print("\n--------",sys._getframe().f_lineno, "Image_OCR_Result - End, used time " + self.usedTime() + " --------")
            
            self.output.close()

            self.PaddleOCR_ParseText()
        except:
            self.output.close()
            print(traceback.format_exc())

    def PaddleOCR_Go(self, i, im):
        isBlank = self.Image_IsBlank(numpy.array(im[2].copy()), 'Result') #check if the image is blank
        if not isBlank:    
            ny = im[4]
            nx = im[5]
            print('\033[0;32;40m*'+str(i)+'\033[0m',end=" ")  #32 - green color, print *                        
            #print("*", end="")
            #print("-- block (width,height):", im[2].size, ', is blank=', isBlank) 
            #image box: left,top and right, bottom
            x1 = im[3][0]+1
            y1 = im[3][1]+1
            x2 = im[3][2]-1
            y2 = im[3][3]-1
            if x2 >= self.image_in.size[0] - 2:
                x2 = self.image_in.size[0] - 2
            if y2 >= self.image_in.size[1] - 2:
                y2 = self.image_in.size[1] - 2

            #image OCR
            try:
                imgx = im[2].copy()
                if self.izoom != 1:
                    sizes = imgx.size
                    imgx  = imgx.resize((int(sizes[0]*self.izoom), int(sizes[1]*self.izoom)),Image.ANTIALIAS)

                #add edge to the image
                dxy = 15 #edge height or width
                bgColor = self.Image_getBGColor(numpy.array(imgx))
                im_arr  = numpy.array(imgx.convert("RGB"))
                imshape = im_arr.shape
                im_arrX = numpy.zeros((imshape[0] + dxy*2, imshape[1] + dxy*2,3), numpy.uint8)
                im_arrX[:] = bgColor #[255,0,0]
                #print(im_arrX)
                im_arrX[dxy:dxy+imshape[0],dxy:dxy+imshape[1]] = im_arr
                #im_arr_temp1 = Image.fromarray(im_arrX)
                #im_arr_temp1.show()
                #im_arr_temp1.save(tmp_folder + '/X' + str(izoom) + ' ' + str(i) + '.png')
                
                #print(im_arr.shape,im_arr)  #.shape(height, width, color-channels)
                data_paddle = self.PaddleOCR.ocr(im_arrX)  

                parsedLines = []
                for line in data_paddle:
                    if not len(line):
                        continue

                    '''      
                    print("\n",sys._getframe().f_lineno,'line=', line,"\n")
                    #结果是一个list，每个item包含了文本框，文字和识别置信�?
                    ##### paddleocr version<2.6.1.2 #####
                    #case-1
                    line = [   
                        [[24.0, 36.0], [304.0, 34.0], [304.0, 72.0], [24.0, 74.0]], 
                        ['纯臻营养护发�?, 0.964739]
                    ]

                    ##### paddleocr version=2.6.1.2 #####
                    #case-2
                    line= [
                        [
                            [[29.0, 52.0], [292.0, 52.0], [292.0, 79.0], [29.0, 79.0]], 
                            ('Bo,Qingzhu,Wenjian', 0.9083628058433533)
                        ]
                    ]

                    #case-3
                    line= [
                        [
                            [[18.0, 31.0], [383.0, 29.0], [383.0, 64.0], [19.0, 67.0]], 
                            ('ohan Zoom Image: 2', 0.9425995349884033)
                        ], 
                        [
                            [[15.0, 97.0], [516.0, 97.0], [516.0, 129.0], [15.0, 129.0]], 
                            ('vaSankar Yepuri; Saibaba Kon', 0.9415278434753418)
                        ]
                    ]
                    '''
                    try:
                        if len(line) == 1: #case-2
                            line = line[0]

                        if len(line) < 2:
                            print('\tinvlad line:', line)
                            continue
                        elif len(line) == 2 and len(line[0]) == 4 and len(line[1]) == 2 and type(line[1][0]) == str and (type(line[1][1]) == float or type(line[1][1]) == int): #case-1                   
                            line[1] = list(line[1])
                            parsedLines.append(line)
                        else: 
                            line0 = line[0]  #case-3
                            if len(line0) == 2 and len(line0[0]) == 4 and len(line0[1]) == 2 and type(line0[1][0]) == str and (type(line0[1][1]) == float or type(line0[1][1]) == int): #case-1   
                                for linex in line:
                                    linex[1] = list(linex[1])
                                    parsedLines.append(linex)
                    except:
                        print(sys._getframe().f_lineno,'line=', line)
                        print(sys._getframe().f_lineno, "Try to parse line of PaddleOCR result and get error:\n" + traceback.format_exc())

                for line in parsedLines:
                    '''
                    Print2Log('', line)
                    #结果是一个list，每个item包含了文本框，文字和识别置信�?
                    [   
                        [[24.0, 36.0], [304.0, 34.0], [304.0, 72.0], [24.0, 74.0]], 
                        ['纯臻营养护发�?, 0.964739]
                    ]
                    '''
                    try:
                        if len(line[1][0]):
                            line[0][0] = [(line[0][0][0] - dxy)/self.izoom + im[0], (line[0][0][1] - dxy)/self.izoom + im[1]]
                            line[0][1] = [(line[0][1][0] - dxy)/self.izoom + im[0], (line[0][1][1] - dxy)/self.izoom + im[1]]
                            line[0][2] = [(line[0][2][0] - dxy)/self.izoom + im[0], (line[0][2][1] - dxy)/self.izoom + im[1]]
                            line[0][3] = [(line[0][3][0] - dxy)/self.izoom + im[0], (line[0][3][1] - dxy)/self.izoom + im[1]]
                            self.results['image_to_string'].append(line[1][0])

                            xx = sorted(list(set([line[0][0][0], line[0][1][0], line[0][2][0], line[0][3][0]])))
                            yy = sorted(list(set([line[0][0][1], line[0][1][1], line[0][2][1], line[0][3][1]])))                                
                            ibox = [int(xx[0]), int(yy[0]), int(xx.pop()), int(yy.pop())]
                            self.results['image_data_paddle'].append([ibox, line[1][0], line[1][1], ny, nx]) 
                    except:
                        print('\nline=', line)
                        print('line[0][0][0]=', line[0][0][0],', dxy=', dxy,', self.izoom=', self.izoom,', im[0]=', im[0],', line[0][0][1]=', line[0][0][1],', im[1]=', im[1]) 
                        print(sys._getframe().f_lineno, "Try to process line of PaddleOCR result and get error:\n" + traceback.format_exc())                    
                                
            except:
                print(sys._getframe().f_lineno, "\nTry PaddleOCR and get error:\n" + traceback.format_exc())
        else:
            print("\n!!! blank image!")

    def PaddleOCR_ParseText(self):
        rett = []
        ttbox= []
        linebox = []
        try:
            xx = []
            yy = []
            if len(self.results['image_data_paddle']):
                avg_line_height = 10
                line_heights = []
                for i in range(0, len(self.results['image_data_paddle'])):
                    line = self.results['image_data_paddle'][i]
                    ibox = line[0]
                    line_heights.append(abs(int(ibox[3] - ibox[1])))
                if len(line_heights):
                    avg_line_height = int(sum(line_heights)/len(line_heights))
                print("\n\tOne line height (avg, pixel):", avg_line_height)

                boxs = {}
                boxsNyXs = []
                lengths = []            
                for i in range(0, len(self.results['image_data_paddle'])):
                    line = self.results['image_data_paddle'][i]
                    ibox = line[0]
                    xx = sorted(list(set([ibox[0], ibox[2]])))
                    yy = sorted(list(set([ibox[1], ibox[3]])))                                
                
                    xs = int(ibox[0])
                    ys = int(ibox[1])
                    xe = int(ibox[2])
                    ye = int(ibox[3])
                    rtext = line[1]
                    if len(rtext):
                        lengths.append((xe - xs) / len(rtext))

                    ny = line[3]
                    nx = line[4]

                    xx.extend([xs,xe])
                    yy.extend([ys,ye])

                    cy = int((ys + ye)/2)
                    #Print2Log('', cy, xs, rtext)
                    ibcy = cy
                    if boxs.__contains__(ny):
                        for bcy in boxs[ny].keys():
                            if abs(bcy - cy) <= avg_line_height/2:
                                ibcy = bcy  #just get all into one line

                    if not boxs.__contains__(ny):
                        boxs[ny] = {}                
                    if not boxs[ny].__contains__(ibcy):
                        boxs[ny][ibcy] = []
                    boxs[ny][ibcy].append([[xs, ys, xe, ye], rtext])

                    boxsNyXs.append(xs)

                """
                for ny in sorted(boxs.keys()):
                    for ibcy in sorted(boxs[ny].keys()):
                        ss = []
                        for nx in sorted(boxs[ny][ibcy].keys()):
                            for item in sorted(boxs[ny][ibcy][nx], key=lambda x:x[0][0]):
                                ss.append(item[1])

                        print(">>", ny, ibcy, " | ".join(ss))
                """
                xlen = 7
                if len(lengths):
                    xlen = int(sum(lengths)/len(lengths))
                print("\tOne space length (avg, pixel):", xlen)

                xs_min = min(boxsNyXs)
                last_ny = sorted(boxs.keys())[0]
                xx_line = []
                yy_line = []
                for ny in sorted(boxs.keys()):                
                    if ny - last_ny > 1:
                        rett.append('')

                    for ibcy in sorted(boxs[ny].keys()):
                        xs_min0 = xs_min
                        last_xe = 0
                        nx_texts = []

                        for item in sorted(boxs[ny][ibcy], key=lambda x:x[0][0]):
                            xx_line.extend([item[0][0], item[0][2]])
                            yy_line.extend([item[0][1], item[0][3]])
                            
                            gap_x = item[0][0] - last_xe - xs_min0
                            if gap_x < 0:
                                gap_x = 0
                            print("\tgap=", gap_x, item[1])
                            spaces_k = int(gap_x/xlen)
                            if spaces_k == 0 and gap_x >= xlen/4:
                                spaces_k = 1

                            nx_texts.append(" " * spaces_k  + item[1])
                            last_xe = item[0][2]
                            xs_min0 = 0
                        
                        xx = sorted(xx_line)
                        yy = sorted(yy_line)
                        linebox.append([[xx[0], yy[0], xx.pop(), yy.pop()], "".join(nx_texts)])
                        if self.parse_text_add_row_number:
                            rett.append("{:0>3d}".format(ny) + ": " + "".join(nx_texts))
                        else:
                            rett.append("".join(nx_texts))
                    last_ny = ny     
                    
            if len(xx) and len(yy):
                ttbox= [min(xx), min(yy), max(xx), max(yy)]
        except:
            print(sys._getframe().f_lineno, traceback.format_exc())

        self.results['result_parsed'] = [rett, ttbox, linebox]

    def Image_getBGColor(self, im_arr_temp):
        #get background color of the image
        #!!!! have to convert the image to RGB 3 channels, before come to here!!!!! as im = im.convert('RGB')
        bgColor = [255,255,255]
        try:
            im_arr_temp_1 = im_arr_temp.reshape(-1,3)
            #print("\nim_arr_temp.reshape(-1,3)=",im_arr_temp_1.shape,im_arr_temp_1)
            unique,counts=numpy.unique(im_arr_temp_1, axis=0,return_counts=True)
            bgColor = list(unique[numpy.argmax(counts)])
            #print("unique=",unique)
            #print("counts=",counts)
            #print("background color=",bgColor,"\n")        
            #im_arr_temp[:,:,0], im_arr_temp[:,:,1], im_arr_temp[:,:,2] = bgColor
            #im_arr_temp = Image.fromarray(im_arr_temp)
            #im_arr_temp.show()
        except:
            #print("\t", im_arr_temp.shape, "\n", traceback.format_exc())
            pass
        #print("background color=",bgColor,"\n")

        return bgColor

    def Image_IsBlank(self, im_arr, wherfrom):
        #check if the image is blank
        try:
            a1 = im_arr[0][0]  #get the first point color
            aa = numpy.ones((im_arr.shape[0], im_arr.shape[1], 3), dtype=numpy.int16)  #create an image array
            aa[:,:,[0]] = a1[0]      #fill up the new image array with the first point color                 
            aa[:,:,[1]] = a1[1]                       
            aa[:,:,[2]] = a1[2]     
            return (im_arr == aa).all()  #compare the image arrays
        except:
            print('\033[0;31;40m-!!-\033[0m',end="")  #31 - red color
            #print("\nImage_IsBlank, from=",wherfrom)
            #print(traceback.format_exc())
            return False

    def Image_IsOneLine(self, arr, minNonZero=5, getNonzeroIndex=False):
        icount = False
        result = {
            'unique': None,
            'inverse': None,
            'counts' : None,
            'nonzero':None
        }    
        try:
            unique,inverse,counts=numpy.unique(arr,axis=0,return_inverse=True,return_counts=True)
            result= [unique,inverse,counts]
            result = {
                'unique': unique,
                'inverse': inverse,
                'counts' : counts,
                'nonzero':None
            }
            
            if getNonzeroIndex or len(counts) <= 5:
                #print("\tY:", y, ", unique=", unique.tolist(),', counts=',counts,', inverse=', inverse)
                #How many times the values change in the series of [inverse]?
                a = numpy.array(inverse[1:len(inverse)])
                b = numpy.array(inverse[0:len(inverse)-1])                        
                nz_indexs = numpy.nonzero(a - b)
                
                #print("\tY: nz_indexs=",nz_indexs)

                #print("\tY:", y, ", unique=", unique.tolist(),', counts=',counts, ", nz_indexs=",nz_indexs, type(nz_indexs), len(nz_indexs[0]))
                
                zn = 0
                if type(nz_indexs) == tuple:
                    zn = len(nz_indexs[0])             
                    result['nonzero'] = nz_indexs[0]
                    #print("type(result['nonzero'])=", type(result['nonzero']))
                else:
                    zn = len(nz_indexs)
                    result['nonzero'] = nz_indexs

                if zn <= minNonZero:                        
                    icount = True
        except:
            print(traceback.format_exc())

        return icount, result

    def Image_cleanUp(self):
        img = self.image_in.copy()
        
        #get background color of the image
        bgColor = self.Image_getBGColor(numpy.array((img.copy()).convert("RGB")))
        Lcolor = int(bgColor[0] * 299/1000 + bgColor[1] * 587/1000 + bgColor[2] * 114/1000)
        print("background color=",bgColor, Lcolor,"\n") 
        #bgColor = Lcolor

        #statistic color of the image
        im_arr_temp1 = numpy.array((img.copy()).convert("RGB"))
        print("im_arr_temp1 (height, width, channels)=",im_arr_temp1.shape)
        #im_arr_temp1[int(im_arr_temp1.shape[0]/2),:] = [0,0,0]
        #im_arr_temp1[:,int(im_arr_temp1.shape[1]/2)] = [0,0,0]
        print(sys._getframe().f_lineno, ".... Image Clean to get background color, used time", self.usedTime())
        #return

        #clean in frist round: erase the line whose width/height is not least than value of [step] 
        clean_fillColor = bgColor
        cleanBox = []
        step  = 10
        for shape_i in [0,1,1]:
            for row in range(im_arr_temp1.shape[shape_i]):
                arr = []
                try:
                    if shape_i == 0:
                        arr = im_arr_temp1[row]
                    else:
                        arr = im_arr_temp1[:,row]
                except:
                    print("im_arr_temp1[?], row=", row,"\n")
                    print(traceback.format_exc())   
                
                IsOneLine, result = self.Image_IsOneLine(arr, minNonZero=0, getNonzeroIndex=True)

                if IsOneLine:
                    #one color in one line, no text, can be erased
                    if shape_i == 0:
                        im_arr_temp1[row,:] = clean_fillColor
                        cleanBox.append(['row', row, 0, im_arr_temp1.shape[1]])
                    else:
                        im_arr_temp1[:, row] = clean_fillColor
                        cleanBox.append(['col', row, 0, im_arr_temp1.shape[0]])
                    continue

                start_i = 0
                next_i  = 1
                try:
                    nz_indexs = result['nonzero']
                    inverse   = result['inverse']

                    nz_indexs_copy = nz_indexs.copy()
                    if nz_indexs_copy[0] !=0:
                        nz_indexs_copy = [0] + nz_indexs_copy
                    if nz_indexs_copy[len(nz_indexs_copy) - 1] != len(inverse) - 2:
                        nz_indexs_copy = nz_indexs_copy + [len(inverse)]

                    index1 = nz_indexs_copy[start_i]
                    index2 = nz_indexs_copy[next_i]

                    #print(nz_indexs)
                    #print(nz_indexs_copy)  
                    # erase the line whose width/height is not least than value of [step]              
                    while True:        
                        if index2 - index1 + 1 >= step:
                            ss = index1
                            ee = index2 + 1                            

                            if ss > 0:
                                ss = index1 + 2
                            if ee < len(inverse) - 2:
                                ee = index2 - 1                       

                            if shape_i == 0:
                                im_arr_temp1[row, ss: ee] = clean_fillColor
                                cleanBox.append(['row',row, ss, ee])
                            else:
                                im_arr_temp1[ss:ee, row] = clean_fillColor
                                cleanBox.append(['col',row, ss, ee])

                        start_i += 1
                        next_i  += 1

                        if start_i >= len(nz_indexs_copy) - 1 or next_i >= len(nz_indexs_copy):
                            break

                        index1 = nz_indexs_copy[start_i]
                        index2 = nz_indexs_copy[next_i]
                except:
                    print("\nresult.inverse=", result['inverse'],"\n")
                    print("result.nonzero=",   result['nonzero'],"\n")
                    print(traceback.format_exc())

        im_arr_temp1 = Image.fromarray(im_arr_temp1)
        print(sys._getframe().f_lineno, ".... Image Clean in first round, used time", self.usedTime())

        boxs = self.Image_Crop_Pre(
            numpy.array((im_arr_temp1.copy()).convert("RGB")), 
            im_arr_temp1.size, 
            im_RGB_raw= numpy.array((img.copy()).convert("RGB"))
            )
        print(sys._getframe().f_lineno, ".... Image Clean - crop image, used time", self.usedTime())
        return boxs

    def Image_Crop_Y(self, im_RGB, isize, step_x=50, step_y=15, x0=0, y0=0):
        cropframes = []
        i = 0
        if isize[0] > step_x or isize[1] > step_y:
            y1 = y0
            y2 = y0
            last_y2 = y0          

            while last_y2 < y0  + isize[1]:
                i += 1

                y1 = last_y2
                if y1 >= y0 + isize[1]:
                    break
                
                if i > 1:
                    y2 = y1 + step_y
                    if y2 > y0  + isize[1]:
                        y2 = y0 + isize[1]

                y_blank_count = 0
                y_blank_last_y2 = 0
                #print('--------- 1 y2:', y2, isize)
                while True:
                    if y2 > y0 + isize[1]:                    
                        break

                    #'''
                    #check by line, use less time!!!
                    try:
                        IsOneLine, result = self.Image_IsOneLine(im_RGB[y2,x0:isize[0]], minNonZero=5)
                        if IsOneLine and y2 - y1 > 5:
                            if y2 - y_blank_last_y2 == 1:
                                y_blank_count += 1
                                if y_blank_count >= 2:
                                    y_blank_count = 0
                                    y_blank_last_y2 = y2
                                    break
                            else:
                                y_blank_count = 0
                            y_blank_last_y2 = y2
                    except:
                        pass
                        #print("\nim_RGB[y2,x0:isize[0]]=im_RGB[", y2, x0, isize[0],"]\n")
                        #print(traceback.format_exc())
                    y2 +=1

                #print('\n--------- '+ str(i) + '/' + str(ny) +' y1, y2, ibox, rgb:', y1, y2, ibox, rgb)

                if y2 > y0 + isize[1]:
                    y2 = y0 + isize[1]
                elif abs(y0 + isize[1] - y2) <= 10:
                    y2 = y0 + isize[1]

                last_y2 = y2
                cropframes.append(y2)

                if y2 == y1:
                    break
        
            if y2 < y0 + isize[1]:
                cropframes.append(y0 + isize[1])

        else:
            cropframes.append(y0 + isize[1])

        return cropframes

    def Image_Crop_X(self, im_RGB, isize, step_x=50, step_y=15, x0=0, y0=0, im_RGB_raw=None, cropframes=[]):
        #print('\nImage_OCR_Result_Crop_X:', )
        
        i = 0
        #if isize[0] > step_x or isize[1] > step_y:
        if isize[0] and isize[1]:    
            nx = int(isize[0] / step_x) + 1   #total blocks in X axis
            x1 = x0
            y1 = y0
            y2 = y0 + isize[1]
        
            last_x2 = x0
            for j in range(nx):   
                i += 1

                x1 = last_x2
                if x1 >= x0 + isize[0]:
                    break

                x2 = x1 + step_x
                x_blank_count = 0
                x_blank_last_x2 = 0
                #print('--------- 1 x2:', x2, isize)
                while True:
                    icount = 0

                    if x2 >= x0 + isize[0]:
                        break
                    
                    #'''
                    #check by line, use less time!!!
                    try:
                        unique,counts=numpy.unique(im_RGB[y1:y2+1,x2], axis=0,return_counts=True)
                        icount = len(counts) - 1
                    except:
                        pass
                        #print("\tX:unique,counts=numpy.unique(im_RGB",im_RGB.shape, "[",y1,":",y2+1,",",x2,"], axis=0, return_counts=True)")
                        icount = 1
                    #'''

                    if icount == 0 and x2 - x1 > 5:
                        if x2 - x_blank_last_x2 == 1:
                            x_blank_count += 1
                            if x_blank_count > 5:
                                x_blank_count = 0
                                x_blank_last_x2 = x2
                                break
                        else:
                            x_blank_count = 0
                        x_blank_last_x2 = x2

                    x2 +=1

                #print('--------- 2 x2:', x2)

                if x2 > x0 + isize[0]:
                    x2 = x0 + isize[0]  
                elif abs(x2 - (x0 + isize[0])) <= 10:
                    x2 = x0 + isize[0]  

                if x1 == x2:
                    break     
                    
                last_x2 = x2  

                x_blank = []
                GoCheckXagain = False
                if GoCheckXagain:
                    x1_final = x1
                    x_all_icounts = {}
                    for xx in range(x1,x2):
                        icount = 1
                        try:
                            unique,counts=numpy.unique(im_RGB_raw[y1:y2+1,xx], axis=0,return_counts=True)
                            if len(counts) == 1:
                                icount = 0
                            #print(unique)
                        except:
                            pass
                            #print("\tXX:unique,counts=numpy.unique(im_RGB",im_RGB.shape, "[",y1,":",y2+1,",",xx,"], axis=0, return_counts=True)")                 
                        
                        if icount == 0:
                            x_blank.append(xx)
                        elif x1_final == x1:
                            if xx - x1 >=2:
                                x1_final = xx - 2
                            else:
                                x1_final = xx - 1
                        x_all_icounts[xx] = icount

                if len(x_blank):
                    xx1 = x1_final
                    for xii in range(len(x_blank)):
                        xx = x_blank[xii]
                        if xx <= x1_final:
                            continue             

                        if xx - xx1 >=10:
                            canGo = 0
                            toBreak = 0

                            for ddd in range(1, 3):
                                if toBreak:
                                    break
                                if x_all_icounts.__contains__(xx-ddd):
                                    if x_all_icounts[xx-ddd] == 1:
                                        toBreak = 1

                                if x_all_icounts.__contains__(xx+ddd):
                                    if x_all_icounts[xx+ddd] == 1:
                                        toBreak = 1

                            if canGo or toBreak == 0:
                                canGo2 = 0
                                for xxx in range(xx1,xx+1):
                                    if x_all_icounts.__contains__(xxx):
                                        canGo2 += x_all_icounts[xxx]
                                if canGo2:
                                    self.Image_Crop_X_Check(cropframes, xx, [xx, y1, xx, y2], i, step_x)
                                xx1 = xx
                    
                    if xx1 < x2:
                        self.Image_Crop_X_Check(cropframes, x2, [x2, y1, x2, y2], i, step_x)
                else:
                    self.Image_Crop_X_Check(cropframes, x2, [x2, y1, x2, y2], i, step_x)
        else:
            self.Image_Crop_X_Check(cropframes, x0 + isize[0], [x0 + isize[0], y0, x0 + isize[0], y0 + isize[1]], i, step_x)

        return sorted(cropframes)

    def Image_Crop_X_Check(self, cropframes, x, ibox, i, step_x):
        e = False
        for xx in cropframes:
            if abs(xx - x) < step_x:
                e = True
                break
        if not e:
            cropframes.append(x)

    def Image_Crop_Pre(self,im_RGB, isize, step_x=50, step_y=15, x0=0, y0=0, im_RGB_raw=None, layer=1, box0=[]):
        cropframes = []

        if layer > 1:
            x0 = box0[0]
            y0 = box0[1]
        
        cropframesY = self.Image_Crop_Y(im_RGB, isize, step_x=50, step_y=15, x0=x0, y0=y0)
        print("cropframesY=", cropframesY, "\n")
        
        for ny in range(len(cropframesY)):
            #print("cropframesX", len(cropframesX))
            x1 = x0
            cropframesX = []
            isizeXX = [isize[0], cropframesY[ny] - y0]
            cropframesX = self.Image_Crop_X(im_RGB, isizeXX, step_x=50, step_y=15, x0=x0, y0=y0, im_RGB_raw=im_RGB_raw, cropframes=cropframesX)
            print("{:0>3d} X={} blocks".format(ny+1, len(cropframesX) +1))

            for nx in range(len(cropframesX)):
                cropframes.append([[x1, y0, cropframesX[nx], cropframesY[ny]], ny+1, nx+1])
                x1 = cropframesX[nx]
            y0 = cropframesY[ny]

        cropframesX = []
        for cf in cropframes:        
            box = cf[0]
            im_RGB2 = im_RGB[box[1]:box[3]+1 , box[0]:box[2]+1]
            
            isBlank = self.Image_IsBlank(im_RGB2, 'Crop_pre') #check if the image is blank
            if not isBlank:                
                isize = [box[2] - box[0] + 1, box[3] - box[1] + 1]
                im_RGB_raw2 = im_RGB_raw[box[1]:box[3]+1 , box[0]:box[2]+1]

                cfx = self.Image_Crop(im_RGB2, isize, step_x=step_x, step_y=step_y, x0=0, y0=0, im_RGB_raw=im_RGB_raw2, layer=1, box0=box)
                if len(cfx):            
                    cfxx = []
                    for b in cfx:
                        box2 = [b[0] + box[0], b[1] + box[1], b[2] + box[0], b[3] + box[1]]
                        if box2[0] < 0:
                            box2[0] = 0
                        if box2[1] < 0:
                            box2[1] = 0
                        cfxx.append(box2)
                        #Image_OCR_Result_Crop_Frame(ibox=box2, i=0, lcolor='green',  is2go=True)

                    cropframesX.append([cfxx, box, cf[1], cf[2]])   #[[boxes, box, ny, nx], [...]]

        return cropframesX

    def Image_Crop(self, im_RGB, isize, step_x=50, step_y=15, x0=0, y0=0, im_RGB_raw=None, layer=1, box0=[]):
        #print("\n//// Image_OCR_Result_Crop layer=", layer, isize)

        cropframes = []
        if isize[0] > step_x or isize[1] > step_y:
            nx = int(isize[0] / step_x) + 1   #total blocks in X axis
            ny = int(isize[1] / step_y) + 1   #total blocks in Y axis
            x1 = x0
            y1 = y0
            y2 = y0
            last_y2 = y0
            ibox = [x0, y0, x0 + isize[0],y0 + isize[1]]   #box of the whole image              

            i = 0
            while last_y2 < y0  + isize[1]:
                i += 1

                y1 = last_y2
                if y1 >= y0 + isize[1]:
                    break
                
                if i > 1:
                    y2 = y1 + step_y
                    if y2 > y0  + isize[1]:
                        y2 = y0 + isize[1]

                y_blank_count = 0
                y_blank_last_y2 = 0
                #print('--------- 1 y2:', y2, isize)
                while True:
                    if y2 > y0 + isize[1]:                    
                        break

                    #'''
                    #check by line, use less time!!!
                    try:
                        IsOneLine, result = self.Image_IsOneLine(im_RGB[y2,x0:isize[0]], minNonZero=5)
                        if IsOneLine and y2 - y1 > 5:
                            if y2 - y_blank_last_y2 == 1:
                                y_blank_count += 1
                                if y_blank_count >= 2:
                                    y_blank_count = 0
                                    y_blank_last_y2 = y2
                                    break
                            else:
                                y_blank_count = 0
                            y_blank_last_y2 = y2
                    except:
                        pass
                        #print("\nim_RGB[y2,x0:isize[0]]=im_RGB[", y2, x0, isize[0],"]\n")
                        #print(traceback.format_exc())

                    y2 +=1

                #print('\n--------- '+ str(i) + '/' + str(ny) +' y1, y2, ibox, rgb:', y1, y2, ibox, rgb)

                if y2 > y0 + isize[1]:
                    y2 = y0 + isize[1]
                elif abs(y0 + isize[1] - y2) <= 10:
                    y2 = y0 + isize[1]

                last_y2 = y2

                if y2 == y1:
                    break

                last_x2 = x0
                for j in range(nx):                            
                    x1 = last_x2
                    if x1 >= x0 + isize[0]:
                        break

                    x2 = x1 + step_x
                    x_blank_count = 0
                    x_blank_last_x2 = 0
                    #print('--------- 1 x2:', x2, isize)
                    while True:
                        icount = 0

                        if x2 >= x0 + isize[0]:
                            break
                        
                        #'''
                        #check by line, use less time!!!
                        try:
                            unique,counts=numpy.unique(im_RGB[y1:y2+1,x2], axis=0,return_counts=True)
                            icount = len(counts) - 1
                        except:
                            pass
                            #print("\tX:unique,counts=numpy.unique(im_RGB",im_RGB.shape, "[",y1,":",y2+1,",",x2,"], axis=0, return_counts=True)")
                            icount = 1
                        #'''

                        if icount == 0 and x2 - x1 > 5:
                            if x2 - x_blank_last_x2 == 1:
                                x_blank_count += 1
                                if x_blank_count > 5:
                                    x_blank_count = 0
                                    x_blank_last_x2 = x2
                                    break
                            else:
                                x_blank_count = 0
                            x_blank_last_x2 = x2

                        x2 +=1

                    #print('--------- 2 x2:', x2, ibox, rgb)

                    if x2 > x0 + isize[0]:
                        x2 = x0 + isize[0]  
                    elif abs(x2 - (x0 + isize[0])) <= 10:
                        x2 = x0 + isize[0]  

                    if x1 == x2:
                        break     
                        
                    last_x2 = x2   

                    x_blank = []
                    GoCheckXagain = True
                    if GoCheckXagain:
                        x1_final = x1
                        x_all_icounts = {}
                        for xx in range(x1,x2):
                            icount = 1
                            try:
                                unique,counts=numpy.unique(im_RGB_raw[y1:y2+1,xx], axis=0,return_counts=True)
                                if len(counts) == 1:
                                    icount = 0
                                #print(unique)
                            except:
                                pass
                                #print("\tXX:unique,counts=numpy.unique(im_RGB",im_RGB.shape, "[",y1,":",y2+1,",",xx,"], axis=0, return_counts=True)")                 
                            
                            if icount == 0:
                                x_blank.append(xx)
                            elif x1_final == x1:
                                if xx - x1 >=2:
                                    x1_final = xx - 2
                                else:
                                    x1_final = xx - 1
                            x_all_icounts[xx] = icount

                    if len(x_blank):
                        xx1 = x1_final
                        for xii in range(len(x_blank)):
                            xx = x_blank[xii]
                            if xx <= x1_final:
                                continue             

                            if xx - xx1 >=10:
                                canGo = 0
                                toBreak = 0

                                for ddd in range(1, 3):
                                    if toBreak:
                                        break
                                    if x_all_icounts.__contains__(xx-ddd):
                                        if x_all_icounts[xx-ddd] == 1:
                                            toBreak = 1

                                    if x_all_icounts.__contains__(xx+ddd):
                                        if x_all_icounts[xx+ddd] == 1:
                                            toBreak = 1

                                if canGo or toBreak == 0:
                                    canGo2 = 0
                                    for xxx in range(xx1,xx+1):
                                        if x_all_icounts.__contains__(xxx):
                                            canGo2 += x_all_icounts[xxx]
                                    if canGo2:
                                        self.Image_Crop2(
                                            im_RGB, step_x=step_x, step_y=step_y, 
                                            box=[xx1,y1,xx,y2], 
                                            im_RGB_raw=im_RGB_raw, 
                                            cropframes=cropframes,
                                            layer = layer
                                        )
                                        #print('crop (x1,y1,x2,y2) [0,0,width,height]:',(xx1,y1,xx,y2), ibox) 
                                        #cropframes.append([xx1,y1,xx,y2])
                                    xx1 = xx
                        
                        if xx1 < x2:
                            self.Image_Crop2(
                                im_RGB, step_x=step_x, step_y=step_y, 
                                box=[xx1,y1,x2,y2], 
                                im_RGB_raw=im_RGB_raw, 
                                cropframes=cropframes,
                                layer = layer
                            )
                            #print('crop (x1,y1,x2,y2) [0,0,width,height]:',(xx1,y1,x2,y2), ibox) 
                            #cropframes.append([xx1,y1,x2,y2])
                    else:
                        self.Image_Crop2(
                            im_RGB, step_x=step_x, step_y=step_y, 
                            box=[x1,y1,x2,y2], 
                            im_RGB_raw=im_RGB_raw, 
                            cropframes=cropframes,
                            layer = layer
                        )
                        #print('crop (x1,y1,x2,y2) [0,0,width,height]:',(x1,y1,x2,y2), ibox) 
                        #cropframes.append([x1,y1,x2,y2])
        
            if y2 < y0 + isize[1]:
                self.Image_Crop2(
                    im_RGB, step_x=step_x, step_y=step_y, 
                    box=[x0, y2, x0 + isize[0], y0 + isize[1]], 
                    im_RGB_raw=im_RGB_raw, 
                    cropframes=cropframes,
                    layer = layer
                )
                #print("&", end="")
                #print('crop (x1,y1,x2,y2) [0,0,width,height]:',(x1,y1,x2,y2), ibox) 
                #cropframes.append([x0, y2, x0 + isize[0], y0 + isize[1]])

        else:
            self.Image_Crop2(
                im_RGB, step_x=step_x, step_y=step_y, 
                box=[x0, y0, x0 + isize[0], y0 + isize[1]], 
                im_RGB_raw=im_RGB_raw, 
                cropframes=cropframes,
                layer = 100
            )
            #cropframes.append([x0, y0, x0 + isize[0], y0 + isize[1]])

        if layer < 2:
            print("")
        return cropframes

    def Image_Crop2(self, im_RGB, step_x=50, step_y=50, box=[], im_RGB_raw=None, cropframes=[], layer=2):
        if box[2] - box[0] < 10 or box[3] - box[1] < 10:
            return
        
        if not self.win_ocr_crop_layers.__contains__(layer):
            self.win_ocr_crop_layers[layer] = 0
        self.win_ocr_crop_layers[layer] +=1

        if layer < 2 and (box[3] - box[1])/step_y > 3:
            isize = [box[2] - box[0] + 1, box[3] - box[1] + 1]
            im_RGB2     = im_RGB[box[1]:box[3]+1 , box[0]:box[2]+1]
            im_RGB_raw2 = im_RGB_raw[box[1]:box[3]+1 , box[0]:box[2]+1]
            cropframesX = self.Image_Crop(im_RGB2, isize, step_x=step_x, step_y=step_y, im_RGB_raw=im_RGB_raw2, layer=2)
            for b in cropframesX:
                box2 = [b[0] + box[0], b[1] + box[1], b[2] + box[0], b[3] + box[1]]
                if box2[0] < 0:
                    box2[0] = 0
                if box2[1] < 0:
                    box2[1] = 0

                isBlank = self.Image_IsBlank(im_RGB[box2[1]:box2[3], box2[0]:box2[2]], 'Crop2 B') #check if the image is blank
                if not isBlank:
                    print("%" + str(layer)+ '.' + str(len(cropframes)+1), end=" ")
                    #print('crop2 (x1,y1,x2,y2):', box2) 
                    cropframes.append(box2)
        else:
            boxes = []
            nn = 5
            #crop the image in width if its width is too large which will result in bad text recognization
            if (box[2] - box[0])/step_x > nn:
                for i in range(int((box[2] - box[0])/step_x)):
                    b0 = box[0] + step_x*nn*i
                    b2 = box[0] + step_x*nn*(i + 1)
                    if b2 > box[2]:
                        b2 = box[2]
                    boxes.append([b0, box[1], b2, box[3]])

                    if b2 == box[2]:
                        break
            else:
                boxes.append(box)

            for ibox in boxes:
                if ibox[0] < 0:
                    ibox[0] = 0
                if ibox[1] < 0:
                    ibox[1] = 0
                isBlank = self.Image_IsBlank(im_RGB[ibox[1]:ibox[3], ibox[0]:ibox[2]], 'Crop2 A') #check if the image is blank
                if not isBlank:
                    print("#"+ str(layer) +'.'+ str(len(cropframes)+1), end=" ")
                    #print('crop1 (x1,y1,x2,y2):', box)
                    cropframes.append(ibox)

    def usedTime(self, t=0):
        if not t:
            t = time.time() - self.stime

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

def PaddleOCR_Load(self=None, is2show_log=True):
    xPaddleOCR = None

    self_folder = re.sub(r'\\','/',os.path.abspath(os.path.dirname(__file__)))
    print("\nPaddleOCR_Load - self_folder:",self_folder)

    options = {
        'use_gpu':True,
        'use_angle_cls':True,
        'lang':"ch",
        'det_max_side_len':2000,
        'show_log': is2show_log,
        'cls':True,
        'max_text_length':256,
        'det_model_dir'     : self_folder + '/paddleocr/inference-default/ch_PP-OCRv3_det_infer',
        'rec_model_dir'     : self_folder + '/paddleocr/inference-default/ch_PP-OCRv3_rec_infer',        
        'cls_model_dir'     : self_folder + '/paddleocr/inference-default/ch_ppocr_mobile_v2.0_cls_infer',
        'rec_char_dict_path': self_folder + '/paddleocr/doc-default/ppocr_keys_v1.txt'
    }
    try:
        #https://github.com/PaddlePaddle/PaddleOCR/blob/static/doc/doc_ch/whl.md
        # need to run only once to download and load model into memory, try to use GPU at first
        # paddleocr whl包会自动下载ppocr轻量级模型作为默认模型，可以根据�?节自定义模型进行自定义更换�?

        '''
        xPaddleOCR = PaddleOCR(
            use_gpu=True,
            use_angle_cls=True,
            lang="ch",
            det_max_side_len=2000,
            show_log=True,
            cls=True,
            max_text_length=256,
            det_model_dir     = self_folder + '/paddleocr/inference-default/ch_PP-OCRv3_det_infer',
            rec_model_dir     = self_folder + '/paddleocr/inference-default/ch_PP-OCRv3_rec_infer',        
            cls_model_dir     = self_folder + '/paddleocr/inference-default/ch_ppocr_mobile_v2.0_cls_infer',
            rec_char_dict_path= self_folder + '/paddleocr/doc-default/ppocr_keys_v1.txt'
        )
        
        default settings:
            det_model_dir     ='C:\\Users\\Administrator/.paddleocr/whl\\det\\ch\\ch_PP-OCRv3_det_infer', 
            rec_model_dir     ='C:\\Users\\Administrator/.paddleocr/whl\\rec\\ch\\ch_PP-OCRv3_rec_infer', 
            rec_char_dict_path='C:\\Program Files\\Python310\\lib\\site-packages\\paddleocr\\ppocr\\utils\\ppocr_keys_v1.txt', 
            cls_model_dir     ='C:\\Users\\Administrator/.paddleocr/whl\\cls\\ch_ppocr_mobile_v2.0_cls_infer', 
        '''
                        
        print("\nLoad PaddleOCR with GPU enabled ...\n")
        xPaddleOCR = PaddleOCR(**options)



    except:
        print("\n", traceback.format_exc())
        xPaddleOCR = None
        try:
            #not use GPU, if error
            options['use_gpu'] = False

            # need to run only once to download and load model into memory
            print("\nLoad PaddleOCR with GPU disabled ...\n")            
            xPaddleOCR = PaddleOCR(**options)
        except:
            xPaddleOCR = None
            print("\n",traceback.format_exc())
        
    if self:
        self.PaddleOCR = xPaddleOCR
    
    return xPaddleOCR
    '''
    xPaddleOCR default settings:
    [2023/02/23 12:53:29] ppocr DEBUG: Namespace(
        help='==SUPPRESS==', 
        use_gpu=False, 
        use_xpu=False, 
        use_npu=False, 
        ir_optim=True, 
        use_tensorrt=False, 
        min_subgraph_size=15, 
        precision='fp32', 
        gpu_mem=500, 
        image_dir=None, 
        page_num=0, 
        det_algorithm='DB', 
        det_model_dir='C:\\Users\\Administrator/.paddleocr/whl\\det\\ch\\ch_PP-OCRv3_det_infer', 
        det_limit_side_len=960, 
        det_limit_type='max', 
        det_box_type='quad', 
        det_db_thresh=0.3, 
        det_db_box_thresh=0.6, 
        det_db_unclip_ratio=1.5, 
        max_batch_size=10, 
        use_dilation=False, 
        det_db_score_mode='fast', 
        det_east_score_thresh=0.8, 
        det_east_cover_thresh=0.1, 
        det_east_nms_thresh=0.2, 
        det_sast_score_thresh=0.5, 
        det_sast_nms_thresh=0.2, 
        det_pse_thresh=0, 
        det_pse_box_thresh=0.85, 
        det_pse_min_area=16, 
        det_pse_scale=1, 
        scales=[8, 16, 32], 
        alpha=1.0, 
        beta=1.0, fourier_degree=5, 
        rec_algorithm='SVTR_LCNet', 
        rec_model_dir='C:\\Users\\Administrator/.paddleocr/whl\\rec\\ch\\ch_PP-OCRv3_rec_infer', 
        rec_image_inverse=True, 
        rec_image_shape='3, 48, 320', 
        rec_batch_num=6, 
        max_text_length=256, 
        rec_char_dict_path='C:\\Program Files\\Python310\\lib\\site-packages\\paddleocr\\ppocr\\utils\\ppocr_keys_v1.txt', 
        use_space_char=True, 
        vis_font_path='./doc/fonts/simfang.ttf', 
        drop_score=0.5, 
        e2e_algorithm='PGNet', 
        e2e_model_dir=None, 
        e2e_limit_side_len=768, 
        e2e_limit_type='max', 
        e2e_pgnet_score_thresh=0.5, 
        e2e_char_dict_path='./ppocr/utils/ic15_dict.txt',
        e2e_pgnet_valid_set='totaltext', 
        e2e_pgnet_mode='fast', 
        use_angle_cls=True, 
        cls_model_dir='C:\\Users\\Administrator/.paddleocr/whl\\cls\\ch_ppocr_mobile_v2.0_cls_infer', 
        cls_image_shape='3, 48, 192', 
        label_list=['0', '180'], 
        cls_batch_num=6, 
        cls_thresh=0.9, 
        enable_mkldnn=False, 
        cpu_threads=10, 
        use_pdserving=False, 
        warmup=False, 
        sr_model_dir=None, 
        sr_image_shape='3, 32, 128', 
        sr_batch_num=1, 
        draw_img_save_dir='./inference_results', 
        save_crop_res=False, 
        crop_res_save_dir='./output', 
        use_mp=False, 
        total_process_num=1, 
        process_id=0, 
        benchmark=False, 
        save_log_path='./log_output/', 
        show_log=True, 
        use_onnx=False, 
        output='./output', 
        table_max_len=488, 
        table_algorithm='TableAttn', 
        table_model_dir=None, 
        merge_no_span_structure=True, 
        table_char_dict_path=None, 
        layout_model_dir=None, 
        layout_dict_path=None, 
        layout_score_threshold=0.5, 
        layout_nms_threshold=0.5, 
        kie_algorithm='LayoutXLM', 
        ser_model_dir=None, 
        re_model_dir=None, 
        use_visual_backbone=True, 
        ser_dict_path='../train_data/XFUND/class_list_xfun.txt', 
        ocr_order_method=None, 
        mode='structure', 
        image_orientation=False, 
        layout=True, 
        table=True, 
        ocr=True, 
        recovery=False, 
        use_pdf2docx_api=False, 
        lang='ch', 
        det=True, 
        rec=True, 
        type='ocr', 
        ocr_version='PP-OCRv3', 
        structure_version='PP-StructureV2', 
        det_max_side_len=2000, 
        cls=True)
    '''
def main():   
    iOCR = PaddleOCR_Class(filepath = 'C:/Users/dengm/OneDrive - Jabil/X-SourceCode/ScreenCatch.S01-01.png')
    iOCR.run()
    print("\n", iOCR.results)
    print("\n" + "\n".join(iOCR.results['result_parsed'][0]), "\n")

if __name__ == "__main__":          
    main()