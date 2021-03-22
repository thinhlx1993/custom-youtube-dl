import os
import json
import requests
import shutil
import logging
import youtube_dl

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


logger = logging.getLogger('spam_application')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('spam.log')
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
windows = None


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


def my_hook(d):
    if d['status'] == 'finished':
        if windows is not None:
            windows.write_event_value('UploadStatusDownload',
                                         [d['filename'], d['status']])  # put a message into queue for GUI
        print('Done downloading, now converting ...')
    if d['status'] == 'error':
        if windows is not None:
            windows.write_event_value('UploadStatusDownload',
                                         [d['filename'], d['status']])  # put a message into queue for GUI
        print('downloading errors')
    if d['status'] == 'downloading':
        if windows is not None:
            speed = round(d['speed']/1024/1024, 1) if d['speed'] is not None else 0
            windows.write_event_value('UploadStatusDownload',
                                         [d['filename'], f"{d['status']} {round(d['downloaded_bytes']/d['total_bytes']*100, 1)}% {speed}Mb/s"])  # put a message into queue for GUI
    # print(d['filename'], d['status'])


def get_links(name, window_env):
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome('chromedriver.exe', chrome_options=chrome_options)
        table_data_tmp = []
        driver.get(name)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#nav-image"))
        )

        try:
            content = driver.find_element_by_css_selector('div.playlist-scoll-wrapper')
            links = content.find_elements_by_tag_name('a')

            try:
                for link in links:
                    title = link.find_element_by_css_selector('h4').text
                    title = title.replace('/', '')
                    link = link.get_attribute('href')
                    if link and 'http' in link:
                        table_data_tmp.append([title, link, 'ready for download'])
            except Exception as ex:
                print(ex)
        except Exception as ex:
            print(ex)

        try:
            content_2 = driver.find_element_by_css_selector('div.intro-right')
            links = content_2.find_elements_by_tag_name('a')
            for link in links:
                try:
                    href = link.get_attribute('href')
                    title = link.find_element_by_tag_name('h4').text
                    title = title.replace('/', '')
                    if href and 'http' in href:
                        table_data_tmp.append([title, href, 'ready for download'])
                except Exception as ex:
                    print(ex)
        except Exception as ex:
            print(ex)

        for idx, data in enumerate(table_data_tmp):
            title, link, status = data
            try:
                ydl_opts = {}
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    meta = ydl.extract_info(link, download=False)
            except:
                driver.get(link)
                try:
                    iframe = driver.find_element_by_css_selector('#iframe')
                    if iframe:
                        link = iframe.get_attribute('src')
                        table_data_tmp[idx] = [title, link, status]
                except Exception as ex:
                    print(ex)

        window_env.write_event_value('GetLinksSuccessfully', json.dumps(table_data_tmp))  # put a message into queue for GUI
        driver.quit()
    except Exception as ex:
        if driver:
            driver.quit()
        # logger.error(f'get_links exception: {ex}')
        print(f'get_links exception: {ex}')


def start_download(link, link_idx, window_env):
    try:

        global windows
        if windows is None:
            windows = window_env

        os.makedirs('downloaded', exist_ok=True)
        link_title = link[0]
        input_link = link[1]

        ydl_opts = {
            'logger': MyLogger(),
            'progress_hooks': [my_hook],
            'outtmpl': f'downloaded/{link_title}.mp4'
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                meta = ydl.extract_info(
                    input_link, download=False)
                if meta:
                    ydl.download([input_link])
            except Exception as ex:
                r = requests.get(input_link, stream=True, headers={'User-agent': 'Mozilla/5.0'})
                if r.status_code == 200:
                    windows.write_event_value('UploadStatusDownload',
                                              [link_title, 'downloading'])  # put a message into queue for GUI
                    with open(f'downloaded/{link_title}.mp4', 'wb') as f:
                        r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)
                    windows.write_event_value('UploadStatusDownload',
                                              [link_title, 'finished'])  # put a message into queue for GUI
                else:
                    logger.error('can not get video info')
                    windows.write_event_value('UploadStatusDownload',
                                              [link_title, 'can not get video info'])  # put a message into queue for GUI
                    print(f'extract errors {ex}')
    except Exception as ex:
        print(ex)
        # logger.error(f'start_download exception: {ex}')
