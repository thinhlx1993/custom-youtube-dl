# This is a sample Python script.
import threading
import json
import time

import PySimpleGUI as sg

from donwloader import get_links, start_download

sg.theme('DarkAmber')  # Add a touch of color
# All the stuff inside your window.
headings = ['title', 'link film', 'download status']  # the text of the headings
layout = [[sg.Text('Enter playlist link here'), sg.InputText(default_text="https://www.laughseejapan.com/watch?v=19368&list=193", key='input', size=(115, 20))],
          [sg.Table(values=[],
                    headings=headings,
                    display_row_numbers=True,
                    justification='left',
                    auto_size_columns=False,
                    col_widths=[50, 30, 20],
                    vertical_scroll_only=False,
                    num_rows=20, key='table')],
          [sg.Button('Get Playlist'), sg.Button('Start download', key='download_btn'), sg.Button('Remove'), sg.Button('Cancel')]]

# Create the Window
window = sg.Window('laughseejapan downloader', layout, size=(1000, 450))

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
        break
    elif event == 'Get Playlist':
        window.Element('Get Playlist').Update(disabled=True, text='Getting Playlist...')
        window.Element('table').Update(values=[])
        x = threading.Thread(target=get_links, args=(values['input'], window,), daemon=True)
        x.start()
    elif event == 'GetLinksSuccessfully':
        try:
            sg.Popup('Get link successfully!', keep_on_top=True, title="Warning!")
            crawled_link = json.loads(values.get('GetLinksSuccessfully'))
            window.Element('table').Update(values=crawled_link)
            window.Element('Get Playlist').Update(disabled=False, text='Get Playlist')
        except Exception as ex:
            print(ex)
    elif event == 'download_btn':
        try:
            window.Element('download_btn').Update(disabled=True, text='Downloading...')
            window.Element('Remove').Update(disabled=True)
            window.Element('Get Playlist').Update(disabled=True)
            table_data = window.Element('table').Get()
            x = threading.Thread(target=start_download, args=(table_data, window,), daemon=True)
            x.start()
        except Exception as ex:
            print(ex)
    elif event == 'UploadStatusDownload':
        try:
            data = values.get('UploadStatusDownload')
            link_idx, status = data
            old_data = window.Element('table').Get()
            old_data[link_idx][2] = status
            window.Element('table').Update(values=old_data)

            result = list(filter(lambda x: (x[2] == 'ready for download' or x[2] == 'Downloading'), old_data))
            if len(result) == 0:
                window.Element('download_btn').Update(disabled=False, text='Start download')
                window.Element('Remove').Update(disabled=False)
                window.Element('Get Playlist').Update(disabled=False)

        except Exception as ex:
            print(ex)
    elif event == 'Remove':
        removed = values['table']
        table_data = window.Element('table').Get()
        for item in reversed(removed):
            table_data.pop(item)
        window.Element('table').Update(values=table_data)

window.close()
