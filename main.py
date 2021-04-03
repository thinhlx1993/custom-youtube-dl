# This is a sample Python script.
import threading
import json
import time
import os

from window_file import window
import PySimpleGUI as sg

from donwloader import get_links, DownloadingThread

processed = 0

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    # print(event, values)
    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        break
    elif event == 'Get Playlist':
        window.Element('Get Playlist').Update(disabled=True, text='Getting Playlist...')
        processed = 0
        window.Element('table').Update(values=[])
        x = threading.Thread(target=get_links, args=(values['input'], window,), daemon=True)
        x.start()
    elif event == 'GetLinksSuccessfully':
        try:
            # sg.Popup('Get link successfully!', keep_on_top=True, title="Warning!")
            crawled_link = json.loads(values.get('GetLinksSuccessfully'))
            window.Element('table').Update(values=crawled_link)
            window.Element('Get Playlist').Update(disabled=False, text='Get Playlist')
        except Exception as ex:
            print(ex)
    elif event == 'download_btn':
        processed = 0
        window.Element('download_btn').Update(disabled=True, text='Downloading...')
        window.Element('Remove').Update(disabled=True)
        window.Element('Get Playlist').Update(disabled=True)
        table_data = window.Element('table').Get()
        try:
            thread = int(values['input_thread'])
        except:
            thread = 5
        for data_idx, data in enumerate(table_data[:thread]):
            table_data[data_idx][2] = 'downloading'
            thread1 = DownloadingThread(processed, data, window)
            thread1.start()
            processed += 1
        window.Element('table').Update(values=table_data)
    elif event == '-THREAD-':
        data = values.get('-THREAD-')
        data = json.loads(data)
        file_index, status = data
        old_data = window.Element('table').Get()
        old_data[file_index][2] = status
        window.Element('table').Update(values=old_data)

        result = list(filter(lambda x: (x[2] == 'ready for download' or 'downloading' not in x[2]), old_data))
        if len(result) == 0:
            window.Element('download_btn').Update(disabled=False, text='Start download')
            window.Element('Remove').Update(disabled=False)
            window.Element('Get Playlist').Update(disabled=False)

        if status == 'finished' or status == 'error' or status == 'can not get video info':
            if processed <= len(old_data):
                print(f'start download video: {data[0]}')
                data = old_data[processed]
                old_data[processed][2] = 'downloading'
                thread1 = DownloadingThread(processed, data, window)
                thread1.start()
                processed += 1
                window.Element('table').Update(values=old_data)
                window.refresh()

        all_downloaded = os.listdir("downloaded")
        num_downloading = len(list(filter(lambda x: x[2] == 'downloading', old_data)))
        for i in range(processed):
            title = f'{old_data[i][0]}.mp4'
            status = old_data[i][2]
            if status == 'downloading' and title in all_downloaded and processed <= len(old_data):
                # downloaded, start new thread
                try:
                    num_thread = int(values['input_thread'])
                except:
                    num_thread = 5
                if num_downloading <= num_thread + 1:
                    old_data[i][2] = 'finished'
                    data = old_data[processed]
                    old_data[processed][2] = 'downloading'
                    thread1 = DownloadingThread(processed, data, window)
                    thread1.start()
                    processed += 1
                    window.Element('table').Update(values=old_data)
                    window.refresh()

    elif event == 'Remove':
        removed = values['table']
        table_data = window.Element('table').Get()
        for item in reversed(removed):
            table_data.pop(item)
        window.Element('table').Update(values=table_data)

window.close()
