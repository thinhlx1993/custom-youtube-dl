import os
import json
import logging
import threading

import youtube_dl
from googleapiclient import discovery
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger('spam_application')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)


class MyLogger(object):
    def debug(self, msg):
        # logger.debug(msg)
        pass

    def warning(self, msg):
        # logger.warning(msg)
        pass

    def error(self, msg):
        # global windows
        # if windows is not None:
        # windows.write_event_value('UploadStatusDownload',
        #                              [d['filename'], d['status']])  # put a message into queue for GUI
        logger.error(msg)


def get_links(url, api_key,  window_env):
    try:
        # extract playlist id from url
        # url = 'https://www.youtube.com/playlist?list=PL3D7BFF1DDBDAAFE5'
        query = parse_qs(urlparse(url).query, keep_blank_values=True)
        playlist_id = query["list"][0]

        # Path to the json file you downloaded:
        path_json = 'rest.json'

        with open(path_json, encoding='utf-8') as f:
            service = json.load(f)
        print(f'get all playlist items links from {playlist_id}')
        # api_key = "AIzaSyBDHutkFzJwEiSLkjy_7cMCgdWdZjaBobI"
        youtube = discovery.build_from_document(service,
                                           developerKey=api_key)
        # youtube = googleapiclient.discovery.build("youtube", "v3",
        #                                           developerKey="AIzaSyBDHutkFzJwEiSLkjy_7cMCgdWdZjaBobI")

        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50
        )
        response = request.execute()

        playlist_items = []
        while request is not None:
            response = request.execute()
            playlist_items += response["items"]
            request = youtube.playlistItems().list_next(request, response)

        print(f"total: {len(playlist_items)}")
        table_data_tmp = [(t["snippet"]["title"],
                           f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}',
                           'ready for download') for t in playlist_items]

        window_env.write_event_value('GetLinksSuccessfully',
                                     json.dumps(table_data_tmp))  # put a message into queue for GUI
    except Exception as ex:
        logger.error(f'get_links exception: {ex}')
        print(f'get_links exception: {ex}')


class DownloadingThread(threading.Thread):
    def __init__(self, threadID, video, window):
        threading.Thread.__init__(self, daemon=True)
        self.threadID = threadID
        self.video = video
        self.window = window

    def run(self):
        os.makedirs('downloaded', exist_ok=True)
        link_title = self.video[0]
        input_link = self.video[1]

        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            # 'logger': MyLogger(),
            # 'progress_hooks': [self.my_hook],
            'outtmpl': f'downloaded/{link_title}.mp4'
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([input_link])
        except:
            pass

        try:
            self.window.write_event_value('-THREAD-',
                                          json.dumps(
                                              [self.threadID, 'finished']))  # put a message into queue for GUI
        except:
            pass

    # @staticmethod
    # def my_hook(d):
    #     try:
    #         filename = d['filename'].replace('downloaded\\', '')
    #         link_idx = int(filename.rsplit('-')[0])
    #         # self.window.write_event_value('UploadStatusDownload', '** DONE **')  # put a message into queue for GUI
    #         if d['status'] == 'finished':
    #             window.write_event_value('-THREAD-',
    #                                      json.dumps([link_idx, d['status']]))  # put a message into queue for GUI
    #             print('Done downloading, now converting ...')
    #         if d['status'] == 'error':
    #             window.write_event_value('-THREAD-',
    #                                      json.dumps([link_idx, d['status']]))  # put a message into queue for GUI
    #             print('downloading errors')
    #         if d['status'] == 'downloading':
    #             speed = round(d['speed'] / 1024 / 1024, 1) if d['speed'] is not None else 0
    #             download_info = f"{d['status']} {round(d['downloaded_bytes'] / d['total_bytes'] * 100, 1)}% {speed}Mb/s"
    #
    #     except:
    #         pass
