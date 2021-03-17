import json
import os
import subprocess
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# logger = logging.getLogger('spam_application')
# logger.setLevel(logging.DEBUG)
# fh = logging.FileHandler('spam.log')
# fh.setLevel(logging.DEBUG)
#
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
# logger.addHandler(fh)


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
                    title = link.find_element_by_tag_name('h4')
                    if href and 'http' in href:
                        table_data_tmp.append([title.text, href, 'ready for download'])
                except Exception as ex:
                    print(ex)
        except Exception as ex:
            print(ex)

        window_env.write_event_value('GetLinksSuccessfully', json.dumps(table_data_tmp))  # put a message into queue for GUI
        driver.quit()
    except Exception as ex:
        if driver:
            driver.quit()
        # logger.error(f'get_links exception: {ex}')
        print(f'get_links exception: {ex}')


def start_download(links, window_env):
    try:
        os.makedirs('downloaded', exist_ok=True)
        for link_idx, link in enumerate(links):
            link_title = link[0]
            input_link = link[1]
            process = subprocess.Popen(['./youtube-dl.exe', input_link, '-o', f'downloaded/{link_title}.mp4'],
                                       stdout=subprocess.PIPE)
            last_text = ''
            emit_downloading = False
            while True:
                output = process.stdout.readline().decode("utf-8")

                if output == '' and process.poll() is not None:
                    # logger.info(f"break {link_title}, {output.strip()}")
                    break
                if output:
                    if not emit_downloading:
                        window_env.write_event_value('UploadStatusDownload',
                                                     [link_idx, 'Downloading'])  # put a message into queue for GUI
                        emit_downloading = True
                    last_text = output.strip()
            rc = process.poll()
            status = 'Downloaded'

            for file in os.listdir('downloaded'):
                if link_title in file and 'part' in file:
                    status = 'Downloading errors, network aborted'

            if f'{link_title}.mp4' not in os.listdir('downloaded'):
                status = 'Video not found errors'

            if 'Extracting information' in last_text:
                status = 'Can not download'
            # logger.info(f'Download end: {rc}')
            # logging.info(f'Download end: {rc}')
            window_env.write_event_value('UploadStatusDownload', [link_idx, status])  # put a message into queue for GUI
    except Exception as ex:
        print(ex)
        # logger.error(f'start_download exception: {ex}')
