import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter import ttk
from csv import reader
import pandas as pd
from datetime import date
import time
import requests
import json
import urllib
import webbrowser
# Moved request variables out of main
from lookup_source import request_url, domain

# Icon path
from pathlib import Path
bundle_dir = Path(__file__).parent
path_to_ico = Path.cwd() / bundle_dir / 'fetch.ico'


# Base window
window = tk.Tk()
window.title('Postcode Lookup')

window.rowconfigure(0, minsize=250, weight=1)
window.columnconfigure(0, minsize=250, weight=1)

window.wm_iconbitmap(path_to_ico)

# Open file to data frame
def open_file():
    # Clear field of new file is search for
    text_open.delete('1.0','end')
    openfile = askopenfilename(
        filetypes=[('Text Files', ['*.txt', '*.csv']), ("All Files", "*.*")]
        )
    if not openfile:
        return
    global lookup
    lookup = pd.read_csv(openfile)
    # save filename for output file
    global filename
    filename = openfile.split('/')[-1].split('.')[-2]
    input_file = openfile.split('/')[-1]
    text_open.insert('1.0', input_file)
    # Save path for output file
    global filepath
    filepath = openfile.rpartition('/')[0]

# Modal window to explain wait seconds
def wait_info():
    tk.messagebox.showinfo(title='Wait', message=
                           'This application using a non-public API protected against DDOS attacks.'
                           ' If running requests to fast your IP will be temporarily blocked. '
                           'A 5 second wait between request is recommended but no less than 3 seconds should be used.')
    
# Modal window to explain call notice
def call_info():
    tk.messagebox.showinfo(title='Call Notice', message=
                           'You can get a counter next to the progressbar to see every 100/50/10 number of calls that have been made.'
                           'This may help estimate time remaining' )
    
# Request error
def request_error(URL):
    tk.messagebox.showerror(title='Too many requests', message='Max requests exceeded with url: {}. Failed to resolve {}'.format(URL, domain))

# Function to open directory from interface
def openlink(path_print):
    webbrowser.open(path_print)

# Lookup post codes
base_url = request_url
def run_file():
    code = []
    count = 0
    progressbar.start()
    lookup_lenght = len(lookup)
    for row in lookup.itertuples(index=False):
        # Update progressbar
        steps = 1 if count == 0 else count/lookup_lenght * 10
        progressbar.step(steps)
        progressbar.update_idletasks()
        count += 1
        street = row[int(strt.get())-1]
        city = row[int(cty.get())-1]
        URL = base_url + urllib.parse.quote(street+', '+city)
        try:
            page = requests.get(URL).json()
        except ConnectionError:
            request_error(URL)
        address = page.get('addresses')
        # Add poat code (if found)
        if address == None:
            code.append('NOT FOUND')
        else:
            pc = [i['postalCode']['postalCode'] for i in address]
            code.append(pc[0])
        # If fetch:count is none or 0, set to 1000
        counter = int(fetch_count.get().strip() or 1000)
        if counter == 0:
            counter = 1000
        # Print how many request have been made
        if count % counter == 0:
                fetched = tk.Label(area, text='Row {}'.format(count), fg='red', font=('Arial', 10))
                fetched.grid(row=2, column=3, sticky='e', padx=(5,15))
        # slow down loop to overcome DDOS protection IP block
        time.sleep(int(wait.get()))
    progressbar.stop()
    # Add new post code to df
    lookup['Post Code'] = code
    # Get time for output file name
    today = date.today().isoformat()
    # Save to spreadsheet using source path
    lookup.to_excel(filepath + '/' + filename + '_' + today +'.xlsx', index=False)
    # Print file name to input field
    text_done.delete('1.0', 'end')
    text_done.insert('1.0', filename + '_' + today + '.xlsx')
    # Link to open directory
    global path_print
    path_print = ('file://' + filepath)
    path_label = tk.Label(area, text='Open Directory', fg='blue', cursor='hand2', font=('Arial', 10, 'underline'))
    path_label.grid(row=4, column=3, sticky='ew', padx=(30,15), pady=5)
    path_label.bind('<Button-1>', lambda e: openlink(path_print))

# Create a working frame
area = tk.Frame(window, bd=0)

# Buttons
btn_open = tk.Button(area, text='Open', command=open_file)
btn_run = tk.Button(area, text='Run', bg='red', command=run_file)
btn_wait = tk.Button(area, text='What is this ?', command=wait_info)
btn_call = tk.Button(area, text='What is this ?', command=call_info)

btn_open.grid(row=1, column=0, sticky='ew', padx=(15, 5))
btn_run.grid(row=1, column=3, sticky='ew', padx=(30,15))
btn_wait.grid(row=4, column=1)
btn_call.grid(row=5, column=1)

area.grid(row=0, column=0, sticky='nsew')

# Text fields
text_open = tk.Text(area, height=1, width=25)
text_done = tk.Text(area, height=1, width=25)
text_done.insert('1.0', 'Output file')

text_open.grid(row=1, column=1, sticky='ew', padx=5)
text_done.grid(row=3, column=3, sticky='ew', padx=(30,15))

# Labels
open_label = tk.Label(area, text='Input file:', font=('Arial', 10))
strt_label = tk.Label(area, text='Street column', font=('Arial', 10))
cty_label = tk.Label(area, text='City column', font=('Arial', 10))
wait_label = tk.Label(area, text='Wait seconds', font=('Arial', 10))
count_label = tk.Label(area, text='Requests', font=('Arial', 10))

open_label.grid(row=0, column=1, sticky='sw', padx=5, pady=5)
strt_label.grid(row=2, column=0, padx=5, pady=5)
cty_label.grid(row=3, column=0, padx=5, pady=5)
wait_label.grid(row=4, column=0, padx=5, pady=5)
count_label.grid(row=5, column=0, padx=5, pady=5)

# Entries
strt = tk.Entry(area, width=5)
cty = tk.Entry(area, width=5)
wait = tk.Entry(area, width=5)
wait.insert(0,5)
fetch_count = tk.Entry(area, width=5)
fetch_count.insert(0,50)

strt.grid(row=2, column=1, sticky='w', padx=5)
cty.grid(row=3, column=1, sticky='w', padx=5)
wait.grid(row=4, column=1, sticky='w', padx=5)
fetch_count.grid(row=5, column=1, sticky='w', padx=5)

# Progress bar
progressbar = ttk.Progressbar(area, length=150)
progressbar.grid(row=2, column=3, sticky='w', padx=(30,15))



window.mainloop()