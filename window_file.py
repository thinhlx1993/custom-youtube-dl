import PySimpleGUI as sg


sg.theme('Light Brown 3')  # Add a touch of color
# All the stuff inside your window.
headings = ['title', 'link film', 'download status']  # the text of the headings
# https://www.laughseejapan.com/playlist?list=1541
# https://www.laughseejapan.com/watch?v=19368&list=193
layout = [[sg.Text('Enter playlist link here'), sg.InputText(default_text="https://www.youtube.com/playlist?list=PLF0CB8E7B4C77DB61", key='input', size=(90, 20)),
           sg.Text('Threads'), sg.InputText(key='input_thread', default_text='5',  size=(15, 20))],
          [sg.Text('Google API key'), sg.InputText(key='input_gg_key', default_text='AIzaSyBDHutkFzJwEiSLkjy_7cMCgdWdZjaBobI')],
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
window = sg.Window('Youtube downloader', layout, size=(1000, 450))
