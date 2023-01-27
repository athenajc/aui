import os
import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

from PIL import Image, ImageTk
from aui import ImageObj, load_svg
from fileio import *

imgdct = {}
thumbdct = {}
def init_thumb():
    obj = ImageObj(filename='/home/athena/data/svg/thumb.svg')
    tkimage = obj.get_tkimage()
    imgdct['thumb.tkimage'] = tkimage
    imgdct['thumb.obj'] = obj
    
def load_thumb(filename):
    if filename in thumbdct:
        return thumbdct[filename]
    filepath = realpath(filename)
    img = ImageObj(filepath, size=(90, 90))
    tkimage = img.get_tkimage()
    thumbdct[filename] = tkimage
    return tkimage
     

class Canvas(tk.Canvas):
    def __init__(self, master,  **kw):           
        super().__init__(master, **kw)
        self.rect = self.create_rectangle        
        
class ImageThumb(Canvas):
    def __init__(self, master, filename, size):
        w, h = size           
        super().__init__(master, width=w, height=h)
        self.size = w, h
        self.selected = False
        self.bg = '#f5f3f3'
        self.outline = '#999' 
        self.fill = self.bg
        thumbtk = imgdct.get('thumb.tkimage')
        self.create_image(0, 0, image=thumbtk, anchor='nw', tag='frame')
        
        self.tkimage = load_thumb(filename)
        self.create_image(w//2-4, h//2-4, image=self.tkimage,  tag='imageobj')      
       
        fn = filename.split(os.sep)[-1] 
        self.create_text(w//2, h-20, text=fn, anchor='n', tag='text', font=('mono',8))
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)      
        #self.bind('<ButtonRelease-1>', self.on_click)
        
    def on_select(self, selected):
        self.selected = selected        
        if self.selected:
            w, h = self.size
            item = self.create_rectangle(0, 0, w-10, h, fill='gray', outline='#999', tag='selected') 
            self.tag_lower('selected')
        else:
            self.delete('selected')
            
    def on_click(self, event):
        self.selected = not self.selected
        self.on_select(self.selected)
       
    def on_enter(self, event=None):
        self.itemconfigure('rect', fill='yellow', outline='yellow')        
        
    def on_leave(self, event=None):        
        self.itemconfigure('rect', fill=self.bg, outline=self.outline)  
        
class ImageGrid(tk.Frame):
    def __init__(self, master):   
        tk.Frame.__init__(self, master)
        self.row, self.col = 0, 0
        self.w = 400
        self.cellsize = 120
        self.objs = []
        self.clear_all()
        self.bind('<Configure>', self.on_configure)         
        
    def on_click(self, event):
        for obj in self.objs:
            if obj == event.widget:
                obj.on_select(True)
            elif obj.selected:
                obj.on_select(False)        
            
    def on_configure(self, event):
        w, h = event.width, event.height
        d = w - self.w
        if d > -5 and d < 5:
            return
        self.w = w
        self.row, self.col = 0, 0
        for obj in self.objs:
            self.grid_obj(obj)
        
    def clear_all(self):
        self.row, self.col = 0, 0
        self.objs = []
        
    def is_image(self, fn):
        ext = fn.split('.')[-1]
        if ext in ['svg', 'png', 'gif', 'jpg']:
            return True
        else:
            return False
            
    def add_dir(self, path):        
        lst = os.listdir(path)
        lst.sort()
        if path[-1] != os.sep:
            path += os.sep
        for s in lst:
            fn = path + s
            if os.path.isfile(fn) and self.is_image(fn):
                self.add_image(fn)
                
    def grid_obj(self, obj):
        obj.grid(row=self.row, column=self.col, padx=2, pady=2)
        self.col += 1
        if self.col * self.cellsize + self.cellsize > self.w:
            self.row += 1
            self.col = 0
            
    def add_image(self, filename):
        w = h = self.cellsize
        obj = ImageThumb(self, filename, size=(w, h))
        self.objs.append(obj)
        self.grid_obj(obj)
        obj.bind('<ButtonRelease-1>', self.on_click)
        


class DirGrid(ImageGrid):
    def __init__(self, master):
        ImageGrid.__init__(self, master)
        self.folder_image = ImageObj('resource/Folder.png', size=(64, 64))
        self.path = os.path.realpath('.')
        
    def add_folder(self, fn, name=None):
        if name == None:
            name = os.path.basename(fn)
        obj = ImageThumb(self.tframe, fn, image=self.folder_image, name=name)
        obj.action = self.on_click_folder
        self.add_obj(obj)
        
    def add_file(self, filename):
        name = os.path.basename(filename)
        obj = ImageThumb(self.tframe, filename, name=name)
        obj.action = self.on_click_file
        self.add_obj(obj)

    def is_image(self, fn):
        if not '.' in fn:
            return False
        ext = fn.split('.')[-1]
        if ext in ['svg', 'png', 'gif', 'jpg']:
            return True
        else:
            return False
            
    def set_dir(self, path):      
        self.path = path
        self.clear_all()  
        self.add_folder(self.path + '/..', name = '..')
        lst = os.listdir(path)
        lst.sort()
        if path[-1] != os.sep:
            path += os.sep
        for s in lst:
            fn = path + s
            if os.path.isdir(fn):
                self.add_folder(fn)
            elif os.path.isfile(fn) and self.is_image(fn):
                self.add_file(fn)      

    def go_upper_folder(self):
        p = self.path.split(os.sep)
        if p[-1] == '':
            p = p[0:-2]
        else:
            p = p[0:-1]
        p1 = os.sep.join(p)
        self.set_dir(p1)
                
    def on_doulble_click(self, obj):
        self.set_dir(obj.filename)
        return
        if obj.ftype == 'folder':
            if obj.name == '..':
                self.go_upper_folder()
            else:
                self.set_dir(obj.filename)
           
    def check_double_click(self, obj, event):
        d = event.time - obj.event_time        
        if d < 1000:
            double_click = True
            obj.event_time = 0
            self.on_doulble_click(obj)
            return True       
        else:
            return False
        
    def on_click_file(self, event):                
        obj = event.widget
        obj.set_selected(not obj.selected)
        
    def on_click_folder(self, event):  
        obj = event.widget           
        if obj.selected :
            self.clear_selection()
            obj.set_selected(True)
            if self.check_double_click(obj, event):
                return
        else:                     
            self.clear_selection()  
            obj.set_selected(True)
        obj.event_time = event.time      
        

class GridFrame(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master, **kw)
        init_thumb()
        self.pack(fill='both', expand=True)
        frame = tk.Frame(self)
        frame.pack(fill='x', expand=False)
        button = tk.Button(frame, text='Add file', bg='#eaeaea')
        button.pack(side='left', fill='none', expand=False)
        button.bind('<ButtonRelease-1>', self.on_open_file)
        self.grid = ImageGrid(self)
        self.grid.pack(fill='both', expand=True)
        
        self.grid.add_dir('/home/athena/Images/svg/')        
         
    def file_dialog(self, dialog, op='Open', mode='r'):        
        filepath = os.path.dirname(os.path.realpath('/home/athena/Images/svg/'))        
        filename = dialog(defaultextension='.svg', mode = mode,
               filetypes = [('Image files', '.*'), ('all files', '.*')],
               initialdir = filepath,
               initialfile = '',
               parent = self,
               title = op + ' File dialog'
               )
        if filename == None:
            return None
        return filename.name                
                
    def open_file(self, filename):        
        self.grid.add_image(filename)
        
    def on_open_file(self, event=None):   
        filename = self.file_dialog(filedialog.askopenfile, 'Open', 'r')   
        print('Filedialog return (%s)'%filename) 
        if filename == None or filename == '':
            return
        self.open_file(filename)
            
if __name__ == '__main__':   
    from aui import App
    app = App('Image Grid', size=(1000, 1000))
    
    frame = GridFrame(app)
    app.mainloop()
    


