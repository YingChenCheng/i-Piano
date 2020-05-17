import sys
import subprocess
import time
import numpy as np
from best_fit import fit
from rectangle import Rectangle
from note import Note
from random import randint
from midiutil.MidiFile3 import MIDIFile
import matplotlib.pyplot as plt
import cv2
import pickle
import os

from PIL import Image

# 初始化滑鼠點擊座標
VertexLeftTop = [-1, -1]
x = VertexLeftTop[0]
y = VertexLeftTop[1]
VertexLeftDown = [-1, -1]
x = VertexLeftDown[0]
y = VertexLeftDown[1]

# 滑鼠點擊座標
point = []
point.append([])
point.append([])
point.append([])
point.append([])
point[0].append(-1)
point[0].append(-1)
point[1].append(-1)
point[1].append(-1)
point[2].append(-1)
point[2].append(-1)
point[3].append(-1)
point[3].append(-1)

# 欲轉換之矩形座標
src_corners = []
src_corners.append([])
src_corners.append([])
src_corners.append([])
src_corners.append([])
src_corners[0].append(-1)
src_corners[0].append(-1)
src_corners[1].append(-1)
src_corners[1].append(-1)
src_corners[2].append(-1)
src_corners[2].append(-1)
src_corners[3].append(-1)
src_corners[3].append(-1)

# 轉換後的矩形座標(a4大小)
dst_corners = []
dst_corners.append([])
dst_corners.append([])
dst_corners.append([])
dst_corners.append([])
dst_corners[0].append(int(0))
dst_corners[0].append(int(0))
dst_corners[1].append(int(0))
dst_corners[1].append(int(780))
dst_corners[2].append(int(780*210/297))
dst_corners[2].append(int(780))
dst_corners[3].append(int(780*210/297))
dst_corners[3].append(int(0))

staff_files = [
    "resources/template/staff3.png",
    "resources/template/staff2.png",
    "resources/template/staff.png"]

finger1_files = ["resources/fingers/finger1.PNG"]
finger2_files = ["resources/fingers/finger2.PNG"]
finger3_files = ["resources/fingers/finger3.PNG"]
finger4_files = ["resources/fingers/finger4.PNG"]
finger5_files = ["resources/fingers/finger5.PNG"]

staff_imgs = [cv2.imread(staff_file, 0) for staff_file in staff_files]
finger1_imgs = [cv2.imread(finger1_file, 0) for finger1_file in finger1_files]
finger2_imgs = [cv2.imread(finger2_file, 0) for finger2_file in finger2_files]
finger3_imgs = [cv2.imread(finger3_file, 0) for finger3_file in finger3_files]
finger4_imgs = [cv2.imread(finger4_file, 0) for finger4_file in finger4_files]
finger5_imgs = [cv2.imread(finger5_file, 0) for finger5_file in finger5_files]

staff_lower, staff_upper, staff_thresh = 40, 80, 0.70
finger1_lower, finger1_upper, finger1_thresh = 5, 20, 0.65
finger2_lower, finger2_upper, finger2_thresh = 5, 20, 0.65
finger3_lower, finger3_upper, finger3_thresh = 5, 20, 0.65
finger4_lower, finger4_upper, finger4_thresh = 5, 20, 0.65
finger5_lower, finger5_upper, finger5_thresh = 5, 20, 0.65

def locate_images(img, templates, start, stop, threshold):
    locations, scale = fit(img, templates, start, stop, threshold)
    img_locations = []
    for i in range(len(templates)):
        w, h = templates[i].shape[::-1]
        w *= scale
        h *= scale
        img_locations.append([Rectangle(pt[0], pt[1], w, h) for pt in zip(*locations[i][::-1])])
    return img_locations

def merge_recs(recs, threshold):
    filtered_recs = []
    while len(recs) > 0:
        r = recs.pop(0)
        recs.sort(key=lambda rec: rec.distance(r))
        merged = True
        while(merged):
            merged = False
            i = 0
            for _ in range(len(recs)):
                if r.overlap(recs[i]) > threshold or recs[i].overlap(r) > threshold:
                    r.merge(recs.pop(i))
                    merged = True
                elif recs[i].distance(r) > r.w/2 + recs[i].w/2:
                    break
                else:
                    i += 1
        filtered_recs.append(r)
    return filtered_recs

def open_file(path):
    cmd = {'linux':'eog', 'win32':'explorer', 'darwin':'open'}[sys.platform]
    subprocess.run([cmd, path])

def image_process_1():
    image = cv2.imread('temp/src_image.jpg', 0)
    # list_ = image.tolist()
    start_time = time.time()
    # image_copy = image.copy()
    # print('max value',max(map(max, list_)))
    # print('min value',min(map(min, list_)))

    blurred = cv2.GaussianBlur(image, (11, 11), 0)
    edged = cv2.Canny(blurred, 30, 150)
    _, cnts, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:1]
    c = cnts[0]
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.01 * peri, True)
    # cv2.drawContours(image_copy, [approx], -1, (0, 255, 0), -1)

    for index, item in enumerate(approx):
        point[index][0] = item[0, 0]
        point[index][1] = item[0, 1]

    src_i = (point[0][0]+point[1][0]+point[2][0]+point[3][0])/4
    src_j = (point[0][1]+point[1][1]+point[2][1]+point[3][1])/4

    for t in range(4):
        if point[t][0]<src_i and point[t][1]<src_j:
            src_corners[0][0] = point[t][0]
            src_corners[0][1] = point[t][1]
        elif point[t][0]<src_i and point[t][1]>src_j:
            src_corners[1][0] = point[t][0]
            src_corners[1][1] = point[t][1]
        elif point[t][0]>src_i and point[t][1]>src_j:
            src_corners[2][0] = point[t][0]
            src_corners[2][1] = point[t][1]
        elif point[t][0]>src_i and point[t][1]<src_j:
            src_corners[3][0] = point[t][0]
            src_corners[3][1] = point[t][1]

    np_src_corners = np.asarray(src_corners, np.float32)
    np_dst_corners = np.asarray(dst_corners, np.float32)

    mat = cv2.getPerspectiveTransform(np_src_corners, np_dst_corners)

    srcImg = image

    global dstImg
    dstImg = cv2.warpPerspective(srcImg, mat, (int(780 * 210 / 297), 780), cv2.INTER_LINEAR)
    
    print('轉正', time.time() - start_time)
    cv2.imwrite('temp/dstImg.png', dstImg)
    # open_file('dstImg.png')   

def image_process_2():
    image = cv2.imread('temp/src_image.jpg', 0)
    list_ = image.tolist()
    if max(map(max, list_))>225:
        thresh_1 = 0.66* max(map(max, list_))
        thresh_2 = 0.70* max(map(max, list_))
        thresh_3 = 0.72* max(map(max, list_))
    elif max(map(max, list_))<200:
        thresh_1 = 0.65* max(map(max, list_))
        thresh_2 = 0.75* max(map(max, list_))
        thresh_3 = 0.84* max(map(max, list_))
    else:
        thresh_1 = 0.66* max(map(max, list_))
        thresh_2 = 0.72* max(map(max, list_))
        thresh_3 = 0.75* max(map(max, list_))

    ret,img_gray1 = cv2.threshold(dstImg, thresh_1, 255, cv2.THRESH_BINARY)
    ret,img_gray2 = cv2.threshold(dstImg, thresh_2, 255, cv2.THRESH_BINARY)
    ret,img_gray3 = cv2.threshold(dstImg, thresh_3, 255, cv2.THRESH_BINARY)    

    img_gray = 255 * np.ones(shape = [780, 551], dtype = np.uint8)

    # cv2.namedWindow("img_gray", cv2.WINDOW_AUTOSIZE)
    # cv2.imshow("img_gray", img_gray)

    for i in range(780):
        for j in range(551):
            if img_gray1[i][j] == 0 and img_gray2[i][j] == 0 and img_gray3[i][j] == 0:
                img_gray[i][j] = 0
            elif img_gray1[i][j] == 0 or img_gray2[i][j] == 0:
                if img_gray3[i][j] == 0:
                    img_gray[i][j] = 0
            elif img_gray1[i][j] == 0 or img_gray3[i][j] == 0:
                if img_gray2[i][j] == 0:
                    img_gray[i][j] = 0
            elif img_gray2[i][j] == 0 or img_gray3[i][j] == 0:
                if img_gray1[i][j] == 0:
                    img_gray[i][j] = 0

    img = img_gray

    # height, width = img.shape[:2]
    # img_width, img_height = img_gray.shape[::-1]

    # <<找五線譜
    staff_recs = locate_images(img_gray, staff_imgs, staff_lower, staff_upper, staff_thresh)
    staff_recs = [j for i in staff_recs for j in i]
    heights = [r.y for r in staff_recs] + [0]
    histo = [heights.count(i) for i in range(0, max(heights) + 1)]
    avg = np.mean(list(set(histo)))
    staff_recs = [r for r in staff_recs if histo[r.y] > avg]
    staff_recs = merge_recs(staff_recs, 0.01)
    # staff_recs_img = img.copy()
    # for r in staff_recs:
    #     r.draw(staff_recs_img, (0, 0, 255), 2)
    # >>


    #  <<找五線譜的模板
    resul = []
    resul.append(staff_recs[0])
    for index, item in enumerate(staff_recs):
        if abs(resul[-1].y - item.y) > 100:
            resul.append(item)
        else:
            continue
    # print("resul", resul)
    # >>

    # <<找五線譜的y座標
    staff = []
    line_axis = []
    for item in resul:
        # print("item.y", item.y)
        line_axis.append(item.y)
        y_project = []
        line_ = []
        for i in range(int(item.h)):
            count = 0
            for j in range(int(item.w)):
                if img[item.y + i, item.x + j] == 0:
                    count += 1
                else:
                    continue
            y_project.append(count)
        # print("y_project(count)", y_project)
            
        i = 1
        while i < len(y_project):
            if (y_project[i] == 0):
                i += 1
                continue
            elif (y_project[i]>0 and y_project[i+1]>0 and y_project[i+2]>0):
                line = (i + i+1 + i+2)//3
                line_.append(line + item.y)
                i += 3
            elif (y_project[i]>0 and y_project[i+1]>0):
                line = (i + i+1)//2
                line_.append(line + item.y)
                i += 2
            else:
                line = i
                line_.append(line + item.y)
                i += 1
                continue
        staff.append(line_)
    # print("line_axis", line_axis)   #每行譜的五條線的最上面那條
    # print("staff", staff)   #每行譜的五條線
    # >>


    ##### 第一行對x投影
    x_range = [102]*(len(resul))
    x_range[0] = 120
    # print('ra_list',ra_list)
    quarter_recs = []
    half_recs = []
    for x_range_index, x_range_ in enumerate(x_range):
        x_project1 = []   
        for x in range(x_range_, 485):          
            count = 0
            for y in range(staff[x_range_index][0]-15, staff[x_range_index][4]+15):
                if img[y,x] == 0:
                    count +=  1
                else :
                    continue
            x_project1.append(count)

        # <<音符的x範圍
        note_xposition = []
        one_note = []
        next_to = False
        for index, item in enumerate(x_project1):
            if item > 8 and next_to == False:      #找到第一個大於9的x
                one_note.append(index)
                next_to = True                      #觸發next_to等於True
            elif item > 8 and next_to == True:      #next_to等於True的情況下如果還是大於九則不做理會
                continue
            elif item < 8 and next_to == True:      #next_to等於True的情況下如果小於九則存入one_note
                one_note.append(index - 1)
                if one_note[1] - one_note[0] > 5:   #one_note[0]是起始x，one_note[1]是結束的x，間距要超過5才會把它存入note_xposition
                    # print("index" ,index)
                    note_xposition.append(one_note)
                one_note = []
                next_to = False                     #next_to等於False
        # print("note_xposition", note_xposition)
        # print('xpo', time.time() - start_time)
        # 音符的x範圍>>

        # <<音符的y範圍  
        note_yposition = []
        note_xpos_yproject = []
        # for index__ in note_xposition:
            # note_xpos_yproject = []
        for r in range(len(note_xposition)):
            for j in range(staff[x_range_index][0] - 15, staff[x_range_index][4] + 15):         
                count = 0 
                for i in range(note_xposition[r][0] + x_range_, note_xposition[r][1] + x_range_):
                    if img[j, i] == 0:
                        count += 1
                    else:
                        continue
                note_xpos_yproject.append(count)

            one_note_ = []
            next_to_ = False
            for index_, item in enumerate(note_xpos_yproject):
                if item > 3 and next_to_ == False:       #找到第一個大於3的y
                    one_note_.append(index_)
                    next_to_ = True                      #觸發next_to_等於True
                elif item > 3 and next_to_ == True:      #next_to_等於True的情況下如果還是大於3則不做理會
                    continue
                elif item < 3 and next_to_ == True:      #next_to_等於True的情況下如果小於3則存入one_note_
                    one_note_.append(index_ - 1)
                    if one_note_[1] - one_note_[0] > 6:   #one_note_[0]是起始y，one_noteY[1]是結束的y，間距要超過6才會把它存入note_xposition
                        note_yposition.append(one_note_)
                    one_note_ = []
                    next_to_ = False                   #next_to等於False
            # print("note_xpos_yproject", note_xpos_yproject)
            note_xpos_yproject = []
        # print("note_yposition", note_yposition)
        # 音符的y範圍>>

        # fingers = []
        # for i in range(len(note_xposition)):
        #     crop_img = img[staff[x_range_index][4]+15 : staff[x_range_index][4]+30, x_range[x_range_index] + note_xposition[i][0] : x_range[x_range_index] + note_xposition[i][1]]
        #     if i == 1:
        #         print("crop_img", crop_img)
        #     # 找finger1
        #     finger1_recs = locate_images(crop_img, finger1_imgs, finger1_lower, finger1_upper, finger1_thresh)
            
        #     # finger1_recs = finger1_recs[0]
        #     finger1_recs = merge_recs([j for i in finger1_recs for j in i], 0.5)
        #     finger1_recs_img = img.copy()
        #     if i == 1:
        #         print("finger1_recs", len(finger1_recs))
        #     for r in finger1_recs:
        #         r.draw(finger1_recs_img, (0, 0, 255), 2)
        # cv2.imwrite('finger1_recs_img.png', finger1_recs_img)
        # open_file('finger1_recs_img.png')            


             
        global recs
        recs = []
        for r in range(len(note_xposition)):
            count = 0 
            for j in range(staff[x_range_index][0] - 15 + note_yposition[r][0], staff[x_range_index][0] - 15 + note_yposition[r][1]):         
                for i in range(note_xposition[r][0] + x_range_, note_xposition[r][1] + x_range_):
                    if img[j, i] == 0:
                        count += 1
                    else:
                        continue
            # print(count/((note_xposition[r][1]-note_xposition[r][0])*(note_yposition[r][1]-note_yposition[r][0])))
            if (count/((note_xposition[r][1]-note_xposition[r][0])*(note_yposition[r][1]-note_yposition[r][0])) > 0.64):
                rec = Rectangle(note_xposition[r][0] + x_range_, staff[x_range_index][0] - 15 + note_yposition[r][0], note_xposition[r][1] - note_xposition[r][0], note_yposition[r][1]- note_yposition[r][0])
                quarter_recs.append(rec)
                recs.append(rec)
            elif (count/((note_xposition[r][1]-note_xposition[r][0])*(note_yposition[r][1]-note_yposition[r][0])) <= 0.64):
                rec = Rectangle(note_xposition[r][0] + x_range_, staff[x_range_index][0] - 15 + note_yposition[r][0], note_xposition[r][1] - note_xposition[r][0], note_yposition[r][1]- note_yposition[r][0])
                half_recs.append(rec)
                recs.append(rec)
        
    # print("quarter_recs", quarter_recs)
    # print("half_recs", half_recs)
    # print("quarter_recs", len(quarter_recs))
    # print("half_recs", len(half_recs))
    l = recs
    # print("rec", rec)
    with open("temp/output.txt", "wb") as fp:   #Pickling
        pickle.dump(l, fp)
    

    # with open("test.txt", "rb") as fp:   # Unpickling
    #     b = pickle.load(fp)

    staff_boxes = [Rectangle(x_range[r], staff[r][2] - 33, 485 - x_range[r], 68) for r in range(len(staff))]
    # staff_boxes_img = img.copy()
    # for r in staff_boxes:
    #     r.draw(staff_boxes_img, (0, 0, 255), 2)
    # cv2.imwrite('staff_boxes_img.png', staff_boxes_img)
    # open_file('staff_boxes_img.png')

    # objects_img = staff_boxes_img

    # 畫四分音符        
    # quarter_recs_img = img.copy()
    # for r in quarter_recs:
    #     r.draw(quarter_recs_img, (0, 0, 255), 2)
    # cv2.imwrite('quarter_recs_img.png', quarter_recs_img)
    # open_file('quarter_recs_img.png')

    # 畫二分音符
    # half_recs_img = img.copy()
    # for r in half_recs:
    #     r.draw(half_recs_img, (0, 0, 255), 2)
    # cv2.imwrite('half_recs_img.png', half_recs_img)
    # open_file('half_recs_img.png')

    staff_notes = []
    note_groups = []
    for box in staff_boxes:
        staff_sharps = []
        staff_flats = []
        quarter_notes = [Note(r, "4,8", box, staff_sharps, staff_flats) 
            for r in quarter_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]
        half_notes = [Note(r, "2", box, staff_sharps, staff_flats) 
             for r in half_recs if abs(r.middle[1] - box.middle[1]) < box.h*5.0/8.0]

        staff_notes = quarter_notes + half_notes

        staff_notes.sort(key=lambda n: n.rec.x)
        staffs = [r for r in staff_recs if r.overlap(box) > 0]
        staffs.sort(key=lambda r: r.x)
        note_color = (randint(0, 255), randint(0, 255), randint(0, 255))
        note_group = []
        i = 0
        j = 0
        while(i < len(staff_notes)):
            if j < len(staffs):
                if staff_notes[i].rec.x > staffs[j].x:
                    r = staffs[j]
                    j += 1
                    if len(note_group) > 0:
                        note_groups.append(note_group)
                        note_group = []
                    note_color = (randint(0, 255), randint(0, 255), randint(0, 255))
                else:
                    note_group.append(staff_notes[i])
                    # staff_notes[i].rec.draww(img, note_color, 2)
                    i += 1                    
            else:
                note_group.append(staff_notes[i])
                # staff_notes[i].rec.draww(img, note_color, 2)
                i += 1
        note_groups.append(note_group)

    # for r in staff_boxes:
    #     r.draw(img, (0, 0, 255), 2)
        
    # cv2.imwrite('res.png', img)
    # open_file('res.png')

   
    # for note_group in note_groups:
    #     print([ note.note + " " + note.sym for note in note_group])

    midi = MIDIFile(1)
     
    track = 0   
    time = 0
    channel = 0
    volume = 100
    
    midi.addTrackName(track, time, "Track")
    midi.addTempo(track, time, 60)
    
    for note_group in note_groups:
        duration = None
        for note in note_group:
            note_type = note.sym
            if note_type == "1":
                duration = 4
            elif note_type == "2":
                duration = 2
            elif note_type == "4,8":
                # duration = 1 if len(note_group) == 1 else 0.5
                duration = 1
            pitch = note.pitch
            midi.addNote(track, channel, pitch, time, duration, volume)
            time += duration

    # And write it to disk.
    binfile = open("temp/output.mid", 'wb')
    midi.writeFile(binfile)
    binfile.close()
    # open_file('output.mid')