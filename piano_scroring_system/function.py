import configparser
import pandas as pd
import numpy as numpy
import imgur_downloader


# Load data from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')
TG_access_token = config['TELEGRAM']['TG_access_token']
imgur_client_id = config['IMGUR']['imgur_client_id']
imgur_client_secret = config['IMGUR']['imgur_client_secret']
imgur_album_id = config['IMGUR']['imgur_album_id']
imgur_access_token = config['IMGUR']['imgur_access_token']
imgur_refresh_token = config['IMGUR']['imgur_refresh_token']

def search_img(song_name):
    print(song_name)
    print(type(song_name))
    text = song_name
    df = pd.read_csv('temp/music_list.csv', index_col=False)
    img_url = df.loc[df['music_name'] == text]['music_sheet_url'].values[0]
    imgur_downloader.ImgurDownloader(imgur_url=img_url, file_name='song_img').save_images('image')