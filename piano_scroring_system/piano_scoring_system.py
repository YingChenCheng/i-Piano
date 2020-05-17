from tkinter import *
import time
import tkinter as tk
import tkinter.messagebox
import pandas as pd
import numpy as numpy
import imgur_downloader
import cv2
from PIL import Image, ImageTk
import mido
import pygame.midi
import midiutil
from midiutil.MidiFile3 import MIDIFile
import subprocess
import hand_test_ml
import sys
import os
import pickle
from rectangle import Rectangle
import matplotlib.pyplot as plt
import dropbox
from dropbox.files import WriteMode
import paho.mqtt.client as mqtt   #  pip install paho-mqtt

dbx = dropbox.Dropbox('jgH_djvkJasAAAAAAAAAFQslYkn9coLtRYvDeXQtXevRFR5WBAeHp42ZuLzUAly0')

# *********************************************************************
# MQTT Config

MQTT_SERVER = "broker.hivemq.com"  
MQTT_PORT = 1883  
MQTT_ALIVE = 60  

MQTT_po_song  = "po/song/"
MQTT_po_user  = "po/song/user/"

MQTT_po_pic   = "po/pic_url/"
MQTT_po       = "po/"
MQTT_po_score = "/score/"
# *********************************************************************


mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_SERVER, MQTT_PORT, MQTT_ALIVE)

temp_song_score = {
    'user_name': 'none',
    'score': ' none'
}

def open_file(path):
    cmd = {'linux':'eog', 'win32':'explorer', 'darwin':'open'}[sys.platform]
    subprocess.run([cmd, path])

def to_midi(events_):
    midistream = MIDIFile(1)
     
    track = 0   
    time = 0
    channel = 0
    volume = 100

    midistream.addTrackName(track, time, "Track")
    midistream.addTempo(track, time, 60)
    
    temp = []
    for index, event_ in enumerate(events_):            
        if event_[0][0] == 144: #key down
            temp = event_
        elif event_[0][0] == 128: #key up
            duration = (event_[1] - temp[1])/1000
            pitch = event_[0][1]
            time = temp[1]/1000
            midistream.addNote(track, channel, pitch, time, duration, volume)

    # And write it to disk.
    binfile = open("temp/user_output.mid", 'wb')
    midistream.writeFile(binfile)
    print(midistream)
    binfile.close()
    # open_file('output.mid')

class Practice(Frame):
    msec = 50
    tempo_count = 1
    tempo = 0
    flipflop = False
    def __init__(self, parent=None, **kw):
        Frame.__init__(self, parent, kw)
        self.flag  = True
        self._running = False
    def search_img(self, song_name):
        text = song_name
        dbx.files_download_to_file('temp/music_list.csv', '/i_Piano/music_list.csv')
        df = pd.read_csv('temp/music_list.csv', index_col=False)
        img_url = df.loc[df['music_name'] == text]['music_sheet_url'].values[0]
        print(img_url)
        os.remove('temp/dst_image.png')
        imgur_downloader.ImgurDownloader(imgur_url=img_url, file_name='dst_image').save_images('temp')

    def _layout(self, song_name, user_name):
        if self.flag == True:
        #介面設定
            label = tk.Label(root, text=song_name, font=('Arial', 20))
            label.pack(pady=10,padx=10)
            label = tk.Label(root, text="Tempo:", font=('Arial', 24))
            label.place(x=60, y=120)
            tempo_var = tk.StringVar()
            tempo_entry = tk.Entry(root, textvariable=tempo_var, show=None, font=('Arial', 24), width=18)  # 顯示成明文形式
            tempo_entry.place(x=60, y=175)
            start_button = tk.Button(root, text='Setup', font=('Arial', 24), width=16, height=1, command=lambda: self.setup())
            start_button.place(x=60, y=240)
            start_button = tk.Button(root, text='Start', font=('Arial', 24), width=16, height=1, command=lambda: self.start(int(tempo_var.get())))
            start_button.place(x=60, y=330)
            stop_button = tk.Button(root, text='Stop', font=('Arial', 24), width=16, height=1, command=lambda: self.stop(song_name, int(tempo_var.get()), user_name))
            stop_button.place(x=60, y=420)

            #載入圖片
            load = Image.open("temp/dst_image.png")
            render = ImageTk.PhotoImage(load)
            img = Label(root, image=render)
            img.image = render
            img.pack()
        self.flag = False
    def setup(self):
        success, frame = camera.read()  # 從攝像頭讀取照片
        frame = cv2.flip(frame, -1)
        
        label_finger_text = tk.Label(root, text="指法: 1", font=('Arial', 28))
        label_finger = tk.Label(root, font=('Arial', 28))
        if success:
            cv2.waitKey(20)

            # 辨識手指
            if piano_input.poll():
                midi_event = piano_input.read(1)[0]
                notes = ['c', 'c+', 'd', 'd+', 'e', 'f', 'f+', 'g', 'g+', 'a', 'a+', 'b']
                notes_standard = [48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72]
                finger_standard = [56, 87, 118, 159, 190, 222, 262, 294, 325, 356, 397, 428, 459, 490, 531]
                finger_note = notes[midi_event[0][1] % 12]
                print(midi_event)
                if midi_event[0][0] == 144:    
                    finger_frame, finger_points = hand_test_ml.detect_fingers(frame)
                    finger_points = [finger_points[4], finger_points[8], finger_points[12], finger_points[16], finger_points[20]]
                    # print('finger_points', finger_points)
                    finded_index = 0
                    for index, item in enumerate(notes_standard):
                        if midi_event[0][1] == item:
                            finded_index = index
                    # print(finded_index)
                    temp_near = 1000
                    finger_result = 0
                    for index, i in enumerate(finger_points):
                        if temp_near > abs(finger_standard[finded_index] - i[0]):
                            temp_near = abs(finger_standard[finded_index] - i[0])
                            finger_result = index+1
                    # print(finger_result)
                    cv2.putText(finger_frame, 'Finger: ' + str(finger_result), (10, 40), cv2.FONT_HERSHEY_DUPLEX, 1, (100, 100, 255), 1, cv2.LINE_AA)
                    cv2.putText(finger_frame, 'Note: ' + finger_note, (10, 70), cv2.FONT_HERSHEY_DUPLEX, 1, (100, 100, 255), 1, cv2.LINE_AA)
                    cv2.imshow('setup', finger_frame)
                    cv2.waitKey(5000)
                        
        
            #畫框框
            pos = 260
            cv2.rectangle(frame, (0, pos), (640, pos+30), (0, 255, 0), 2)
            cv2.circle(frame,(300, pos+15), 15, (0, 255, 255), -1)
            cv2.circle(frame,(330, pos+15), 15, (0, 0, 255), -1)
            cv2.imshow('setup', frame)
            self.setting = root.after(1, self.setup)

    def delete(self, song_name, user_name):
        frame1.destroy()
        label_1.destroy()
        label_2.destroy()
        search_entry.destroy()
        user_entry.destroy()
        search_button.destroy()
        self.search_img(song_name)
        self._layout(song_name, user_name)

    def update(self):
        Metronome = tk.Label(root, bg='white', width=50, height=50)
        Metronome.place(x=1080, y=60)
        if piano_input.poll():
            event.append(piano_input.read(1)[0])
        if self.tempo_count % (self.tempo//6) == 0:
            self.flipflop = not self.flipflop
        if self.flipflop == True:
            Metronome.config(bg='yellow')
        else:
            Metronome.config(bg='white')
        self.tempo_count += 1
        self._updating = self.after(self.msec, self.update)
    
    def prepare(self):
        success, frame = camera.read()  # 從攝像頭讀取照片

    def start(self, tempo_):
        if not self._running:
            self.after_cancel(self.setting)
            cv2.destroyWindow('setup')
            self.tempo = tempo_
            self.prepare()
            self.update()
            self._running = True

    def stop(self, song_name, tempo_, user_name):
        if self._running:
            self._running = False
            self.after_cancel(self._updating)
        to_midi(event)
        self.scoring(song_name, tempo_, user_name)

    def mid_2_script(self, mid):
        script = []
        for track in mid.tracks:
            track_tempo = 0
            start_time = 0
            #find tempo
            for msg in track:
                if msg.type == 'set_tempo':
                    track_tempo = msg.tempo
                    print('track_tempo', track_tempo)
            #find start time
            for msg in track:
                if msg.type == 'note_on':
                    start_time = msg.time
                    print('start',start_time)
                    break

            all_over_time = 0
            for index, msg in enumerate(track):
                #one_note = [note, bit, duration]
                if msg.type == 'note_on':
                    one_note = [] 
                    if start_time != msg.time:
                        all_over_time += msg.time
                    for i in range(index, len(track)):
                        if (track[i].type == 'note_off'):
                            if (msg.note == track[i].note):
                                
                                one_note.append(msg.note)
                                one_note.append((all_over_time) / 960 + 1)
                                print(all_over_time)
                                one_note.append(track[i].time / 960)
                                all_over_time += track[i].time
                                # print(all_over_time)
                                print(one_note)
                                break
                    script.append(one_note)
                elif msg.type == 'end_of_track':
                    break
        return script

    def script_eveluation(self, script, script_user):
        final_score = []
        for index, script_note in enumerate(script):
            one_note_score = []
            min_index = -1
            for i, user_note in enumerate(script_user):
                if abs(user_note[1] - script_note[1]) < 0.5:
                    min_index = i
                    break
            if min_index != -1:
                print(script_user)
                print(min_index)
                scoring_note = script_user.pop(min_index)
                if scoring_note[0] == script_note[0]:
                    one_note_score.append(1)
                else:
                    one_note_score.append(0)

                if abs(scoring_note[1] - script_note[1]) < 0.25:
                    one_note_score.append(1)
                else:
                    one_note_score.append(0.5)

                if scoring_note[2] > (script_note[2] / 2):
                    one_note_score.append(1)
                else:
                    one_note_score.append(0.5)
                
            else:
                one_note_score.append(0)
                one_note_score.append(0)
                one_note_score.append(0)  
            

            final_score.append(one_note_score)

        print("script_user", script_user)
        return final_score

    def final_update(self, final_score, song_name, user_name):
        
        #計算各分項分數
        all_note_score = []
        all_bit_score = []
        all_tempo_score = []
        for item in final_score:
            all_note_score.append(item[0])
            all_bit_score.append(item[1])
            all_tempo_score.append(item[2])
        print(sum(all_note_score))
        print(sum(all_bit_score))
        print(sum(all_tempo_score))
        score = (sum(all_note_score) + sum(all_bit_score) + sum(all_tempo_score)) * 25 / len(final_score) + 25
        print(score)
        score = score//1
        
        #顯示分數
        label_score_text = tk.Label(root, text='分數', font=('Arial', 28))
        label_score_text.place(x=60, y=600)
        label_score = tk.Label(root, text=score, font=('Arial', 28))
        label_score.place(x=60, y=690)

        #標出錯音
        dbx.files_download_to_file('temp/output.txt' ,'/i_Piano/' + song_name + '.txt')
        with open('temp/output.txt', 'rb') as fp:
            rec = pickle.load(fp)
            
        sheet_img = cv2.imread("temp/dst_image.png", 3)
        for index, note_score in enumerate(final_score):
            if sum(note_score) > 2:
                continue
            elif sum(note_score) == 2:
                rec[index].draw(sheet_img, (240, 250, 255), 2)
            elif sum(note_score) >= 1:
                rec[index].draw(sheet_img, (180, 204, 255), 2)
            elif sum(note_score) < 1:
                rec[index].draw(sheet_img, (125, 168, 255), 2)
        # sheet_img = cv2.imread('temp/mistake_note.png')
        cv2.imshow('mistake note', sheet_img)
        # cv2.imwrite('temp/mistake_note.png', sheet_img)

        #更新user成績
        temp_song_score['user_name'] = [user_name]
        temp_song_score['score'] = [score]
        try:
            dbx.files_download_to_file('temp/song_score.csv' ,'/i_Piano/' + song_name + '.csv')

            df = pd.read_csv('temp/song_score.csv', index_col=False)
            df_temp = pd.DataFrame.from_dict(temp_song_score)
            df = df.append(df_temp)
            df.to_csv('temp/song_score.csv', encoding="utf_8_sig", index=False)

        except:
            df = pd.DataFrame.from_dict(temp_song_score)
            df.to_csv('temp/song_score.csv', encoding="utf_8_sig", index=False)

        #上傳user分數檔案
        with open('temp/song_score.csv', 'rb') as f:
            dbx.files_upload(f.read(), '/i_Piano/' + song_name + '.csv', mode=WriteMode('overwrite'))

        #劃出分析圖
        analysis_bar = [sum(all_note_score), sum(all_bit_score),  sum(all_tempo_score)]
        bar_column = ['Note', 'Bit', 'Value']
        plt.bar(bar_column, analysis_bar)
        plt.ylabel('score')
        plt.show()
        



    def scoring(self, song_name, tempo_, user_name):
        dbx.files_download_to_file('temp/output.mid', '/i_Piano/'+ song_name +'.mid')
        mid = mido.MidiFile('temp/output.mid')
        mid_user = mido.MidiFile('temp/user_output.mid')
        script = self.mid_2_script(mid)
        script_user = self.mid_2_script(mid_user)
        final_score = self.script_eveluation(script, script_user)
        for i in final_score:
            print(i)
        self.final_update(final_score, song_name, user_name)

camera = cv2.VideoCapture(0)    #攝像頭

root = Tk()
root.geometry('{}x{}'.format(root.maxsize()[0], root.maxsize()[1]))
frame1 = Frame(root, width=root.maxsize()[0]/2, height=root.maxsize()[1]/3)
frame1.pack()
prac = Practice(root)
label_1 = tk.Label(root, text="使用者名稱：", font=('Arial', 32))
label_1.pack()
user_name_str = tk.StringVar()
user_entry = tk.Entry(root, textvariable=user_name_str, show=None, font=('Arial', 32), width=40)  # 顯示成明文形式
user_entry.pack()
label_2 = tk.Label(root, text="請輸入曲目名稱：", font=('Arial', 32))
label_2.pack()
song_name_str = tk.StringVar()
search_entry = tk.Entry(root, textvariable=song_name_str, show=None, font=('Arial', 32), width=40)  # 顯示成明文形式
search_entry.pack()
search_button = tk.Button(root, text='search', font=('Arial', 32), width=38, height=1, command=lambda: prac.delete(song_name_str.get(), user_name_str.get()))
search_button.pack()

event = []
pygame.midi.init()
piano_input = pygame.midi.Input(pygame.midi.get_default_input_id())

if __name__ == '__main__':
    
    root.mainloop()