import os, sys

import DB
from DB import FileDB
from pprint import pformat, pprint
from fileio import *

dct = {}
def get_files_dct():
    for d in ['p1', 'p2', 'p5']:
        path = get_path(d)
        print(path)
        files = get_files(path)
        dct[path] = files
    text = pformat(dct)
    fwrite('/home/athena/data/files.dct', text)
        
#get_files_dct()

def get_words():
    from aui import App
    app = App(title='APP', size=(1000,860))      
    msg = app.add('msg', font=('Mono', 14))
    sys.stdout = msg
    table = DB.get_table('tokens', 'token')
    names = table.getnames()
    dct = {}
    
    def next_file():
        #msg.clear_all()
        if names == []:
            text = pformat(dct)
            print('done')
            #fwrite('/link/tmp/words.txt', text)
            return
        name = names.pop(0)
        msg.puts(name)
        
        app.after(10, next_file)
        
    app.after(10, next_file)      
    
    app.mainloop()
get_words()
