import os
import re
import sys
import tkinter as tk
import tkinter.ttk as ttk
from aui.Menu import *
from aui.TextObj import Text
from aui.aui_ui import *
from aui.Messagebox import Messagebox
from aui.FileTree import FileTreeView
from aui.TreeView import TreeView
from aui import ImageObj, load_svg, ScrollBar
from fileio import realpath, fread, fwrite
import DB

vars = {}
def get(key, default=None):
    return vars.get(key, default)
    
def set(key, value):
    vars[key] = value

class ImageLabel(tk.Frame):
    def __init__(self, master, obj=None, tkimage=None, filename=None):       
        tk.Frame.__init__(self, master)
        self.label = tk.Label(self)
        self.label.pack(fill='both', expand=True)        
        if obj != None:
            tkimage = obj.get_tkimage()
        elif tkimage == None:
            imgobj = ImageObj.open(filename)
            tkimage = imgobj.get_tkimage()
        if tkimage != None:    
           self.set_image(tkimage)        
   
    def set_image(self, tkimage):
        self.tkimage = tkimage
        self.label.configure(image = self.tkimage)    
        
            
def add_image(master, obj):
    widget = ImageLabel(master, obj)
    widget.pack()
    return widget          
        
def addFrame(master, Frame, fill=True):
    frame = Frame(master)
    if fill == True:
       frame.pack(fill='both', expand=True) 
    return frame
    
def packframe(master, **kw):
    frame = tk.Frame(master, **kw)  
    frame.pack(fill='both', expand=True) 
    return frame     
           
def twoframe(master, style='', sep=0.5):
    frame = TwoFrame(master, type=style, sep=sep)  
    frame.pack(fill='both', expand=True) 
    return frame
    
def add_top(master, style='top', sep=0.25):
    frame = TwoFrame(master, type=style, sep=sep)  
    frame.pack(fill='both', expand=True) 
    return frame
    
def add_left(master, style='left', sep=0.25):
    frame = TwoFrame(master, type=style, sep=sep)  
    frame.pack(fill='both', expand=True) 
    return frame
    
def add_right(master, style='right', sep=0.25):
    frame = TwoFrame(master, type=style, sep=sep)  
    frame.pack(fill='both', expand=True) 
    return frame
    
def twoframev(master, sep=0.5):
    return twoframe(master, style='v', sep=sep)  
    
def twoframeh(master, sep=0.5):
    return twoframe(master, style='h', sep=sep)  
    
def add_textobj(master, TextClass=None, fill=True):
    frame = tk.Frame(master, background='#323c44', relief='sunken', padx=10)
    if fill == True:
        frame.pack(side='left', fill='both', expand=True)
    frame.scrollframe = master
    if TextClass == None:
        TextClass = Text
    textbox = TextClass(master)
    if hasattr(textbox, 'init_dark_config'):
        textbox.init_dark_config()
    #textbox.pack(side='left', fill='both', expand=True)
    textbox.tag_config('find', foreground='black', background='#999')    
    return textbox
    
def add_msg(master, fill=True):
    msg = Messagebox(master)
    if fill == True: 
        msg.pack(side='left', fill='both', expand=True)
    msg.tk.setvar('msg', msg)    
    return msg
    
def add_filetree(master, fill=True):
    tree = FileTreeView(master)
    if fill == True:
        tree.pack(fill='both', expand=True)
    tree.tk.setvar('filetree', tree)   
    return tree
    
def add_tree(master, fill=True):
    tree = TreeView(master)
    if fill == True:
       tree.pack(fill='both', expand=True)
    tree.tk.setvar('tree', tree)   
    return tree
    
def add_menu(master):
    frame = twoframe(master, style='h', sep=0.05)
    frame.pack(side='left', fill='both', expand=False)
    names = 'New,Open,,Close,,History,,Save,Save as,,Undo,Redo,,Copy,Cut,Paste,,'
    names += 'Add Tab,Remove Tab,,Graph'
    menubar = MenuBar(frame, items=names.split(',')) 
    menubar.pack(side='top', fill='x', expand=False)
    menubar.right = frame.right
    return menubar
    
def add_frames( master):        
    mframe = twoframe(master, style='leftbar', sep=0.25)
    frameLR = twoframe(mframe.right, style='h', sep=0.2)  
    return mframe, frameLR                      
    
def add_textmsg(master, TextClass=None):     
    frameTB = twoframe(master, style='v', sep=0.7)   
    textbox = add_textobj(frameTB.top, TextClass)
    msg = msg = add_msg(frameTB.bottom)
    textbox.msg = msg
    msg.textbox = textbox
    root = master.winfo_toplevel()
    root.msg = msg
    root.textbox = textbox
    return textbox, msg
    
def add_set1(master=None, SideFrame=None, TextClass=None):
    mframe, frameLR = add_frames(master)        
    add_menu(mframe.left) 
    textbox, msg = add_textmsg(frameLR.right, TextClass)    
    if SideFrame == None:
        filetree = add_filetree(frameLR.left)
        filetree.click_select = 'click' 
        filetree.msg = msg
        master.filetree = sideframe = filetree
    else:
        sideframe = SideFrame(frameLR.left)
        sideframe.pack(fill='both', expand=True)
    p = textbox, msg, sideframe
    master.textbox, master.msg, master.sideframe= p    
    return p    

def add_bar_msg(master):
    frame = twoframe(master, style='top', sep=0.2)
    msg = add_msg(frame.bottom)
    frame.msg = msg
    sys.stdout = msg         
    return frame

def set_icon(app, icon):
    if icon == None:
        icon = '/home/athena/data/icon/dev.png'
    try:    
        icon = realpath(icon)
        root = app.winfo_toplevel()
        root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=icon))  
    except:
        print('load icon', icon, 'fail')

class ObjCommon():    
    def add_obj_name(self, master, name, **kw):
        if name == 'frame':
            return aFrame(master, **kw)
        elif name == 'msg':
            return Messagebox(master)
        elif name == 'tree':
            return TreeView(master)
        elif name == 'text':
            return Text(master, **kw)
        elif name == 'filetree':
            return FileTreeView(master)
        elif name == 'panel':
            return Panel(master, **kw)    
        elif name == 'menu':
            return MenuBar(master, **kw)    
                
    def add_frame(self, objclass=tk.Frame, master=None, **kw):
        if master == None:
            master = self        
        frame = objclass(master, **kw)
        frame.root = self
        frame.size = self.size
        return frame
        
    def packfill(self, obj):
        obj.pack(fill='both', expand=True)
        
    def add(self, obj='frame', **kw):
        if obj == 'frame':
            return aFrame(self, **kw)
        elif type(obj) == str:    
            return self.add_obj_name(self, obj, **kw)
        else:
            return aFrame(self, **kw)   
        
    def get_layout(self, master=None):
        from aui.Layout import Layout
        if master == None:
            master = self
        layout = Layout(master)
        return layout       
        
    def get(self, name, **kw):
        if name == 'layout':
            return self.get_layout(self)
        if name in ['frame', 'text', 'msg', 'tree', 'filetree', 'nb', 'panel', 'menu']:
            return self.add_obj_name(self, name, **kw)     
        if name in globals():
            return globals().get(name)
            
        return self.tk.getvar(name)
            
        
class aFrame(tk.Frame, ObjCommon):     
    def __init__(self, master, pack=True, **kw):       
        super().__init__(master, **kw)
        self.master = master
        self.root = master.winfo_toplevel()    
        if pack == True:  
           self.pack(fill='both', expand=True)   

    def mainloop(self):
        self.root.mainloop()    
        
    def run(self, WidgetClass=None, arg=None):
        if WidgetClass != None:       
            if arg != None:    
                frame = WidgetClass(self, arg)
            else:
                frame = WidgetClass(self)
            frame.pack(fill='both', expand=True) 
        frame.mainloop()
        
    def add_frame(self, master, **kw):
        frame = aFrame(master, **kw)  
        frame.pack(fill='both', expand=True) 
        return frame 
        
    def add_button(self, master, name, action=None, **kw):
        button = tk.Button(master, text=name, command=action)
        button.pack(**kw)
        return button
        
    def add_buttons(self, master, buttons, side='top'):
        frame = tk.Frame(master)  
        lst = []   
        for b in buttons:
            if type(b) != tuple:
                obj = b(frame)
                obj.pack(side='left', padx=5)
                lst.append(obj)
                continue
            name, action = b   
            btn = self.add_button(frame, name, action)   
            lst.append(btn)
        frame.pack(side=side, fill='x')     
        return lst
        
    def twoframe(self, master, style='', sep=0.5):
        frame = TwoFrame(master, type=style, sep=sep)  
        frame.pack(fill='both', expand=True) 
        return frame
        
    def load_svg(self, filename):
        image = load_svg(filename)
        return image
        
    def add_image(self, obj):
        imagelabel = add_image(self, obj)
        return imagelabel
        
    def add_textobj(self, master=None, TextClass=None):
        if master==None:
            master = self
        self.textbox = add_textobj(master, TextClass)    
        return self.textbox
        
    def add_msg(self, master=None):
        if master==None:
            master = self
        self.msg = add_msg(master)
        return self.msg
        
    def add_filetree(self, master):
        if master==None:
            master = self
        self.filetree = add_filetree(master)
        return self.filetree
        
    def add_tree(self, master):
        if master==None:
            master = self
        self.tree = TreeView(master)
        return self.tree
        
    def add_tree(self, master):
        if master==None:
            master = self
        tree = TreeView(master)
        return tree
        
    def add_menu(self, master):
        if master==None:
            master = self
        self.menubar = add_menu(master)
        return self.menubar        

    def add_combo(self, master, text='', values=[], **kw):
        from aui import AutoCombo
        combo = AutoCombo(master, values=values)
        combo.set_text(text)
        combo.pack(**kw)
        return combo
        
    def add_label(self, master, text, **kw):
        label = tk.Label(master, text=text, **kw)    
        label.pack(**kw)
        return label
        
    def add_frames(self, master):      
        if master==None:
            master = self
        self.mframe, self.frameLR = add_frames(master)  
        return self.mframe, self.frameLR                     
        
    def add_textmsg(self, master, TextClass=None):   
        if master==None:
            master = self
        p = add_textmsg(master, TextClass)  
        self.textbox, self.msg = p
        return p                   
        
    def add_set1(self, master=None, SideFrame=None, TextClass=None):
        if master==None:
            master = self
        p = add_set1(master, SideFrame, TextClass)    
        self.textbox, self.msg, self.filetree= p
        return p        
        
    def add_test_msg(self, master=None):
        if master==None:
            master = self
        frame = self.twoframe(master, style='v', sep=0.7)
        frame1 = self.twoframe(frame.top, style='top', sep=0.2)
        msg = self.add_msg(frame.bottom)
        sys.stdout = msg         
        return frame1
        
    def add_bar_msg(self, master=None):
        if master==None:
            master = self
        return add_bar_msg(master)
        
    def get_cache(self, name):
        cdb = DB.open('cache')
        return cdb.getdata('cache', name)
        
    def set_cache(self, name, text):
        cdb = DB.open('cache')
        cdb.setdata('cache', name, text)        
        
    def set_icon(self, icon):
        set_icon(self, icon)
        

from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
filetypes = {
    'py': ('Python files', '*.py, *.txt'),
    'txt': ('Text files', '*.txt, *.py'),
    'img': ('Image files', '*.png *.svg *.jpg'),
    'image': ('Image files', '*.png *.svg *.jpg'),
    'all': ('All files', '*.*'),
    '*': ('All files', '*.*') 
}    
    
def get_filetypes(ext):
    ftlst = []
    for name in [ext, 'all']:
        p = filetypes.get(name, (name, '*.'+name))        
        ftlst.append(p)  
    return ftlst

def askopenfile(title='Open a file', path='/link', ext='py'):          
    return fd.askopenfile(title=title, initialdir=path, filetypes=get_filetypes(ext))
    
def askopenfilename(title='Open an image', path=None, ext='img'):          
    if path == None:
       if ext == 'img':
          path =  '/link/data'
       else:
          path = '/link'
    return fd.askopenfilename(title=title, initialdir=path, filetypes=get_filetypes(ext))
            
def askopenfiles(title='Open files', path='/link', ext='py'):          
    return fd.askopenfiles(title=title, initialdir=path, filetypes=get_filetypes(ext))
    
def asksaveasfile(title='Save as file', path='/link', ext='py'):          
    return fd.asksaveasfilename(title=title, initialdir=path, filetypes=get_filetypes(ext))

def askstring(title, prompt):
    from tkinter import simpledialog
    answer = simpledialog.askstring(title, prompt)
    return answer

               
class TopFrame(tk.Toplevel, ObjCommon):    
    def __init__(self, title='Test Frame', size=(1300, 900)):       
        super().__init__()
        w, h = size
        self.size = (w, h)
        self.title(title)
        self.geometry('%dx%d'%(w, h)) 
        
    def add(self, objclass, arg=None):
        if arg != None:
            return objclass(self, arg)
        frame = objclass(self)
        return frame
        
class tkApp(tk.Tk, ObjCommon):
    def __init__(self, title='tkApp', size=(1024, 768), icon=None):
        super().__init__()
        self.title(title)
        self.setvar('root', self)
        appname = title.replace(' ', '')
        self.setvar('appname', appname)
        self.set_size(size)
        
    def set_icon(self, icon):
        set_icon(icon)
        
    def set_size(self, size):
        w, h = size        
        self.geometry('%dx%d'%(w, h)) 
        self.size = size
        
    def setvar(self, key, value):
        self.tk.setvar(key, value)
        
    def getvar(self, key):
        self.tk.getvar(key)       
        
    def showinfo(self, *msg):
        showinfo(str(msg))
        
    def ask(self, op='openfile', **kw):
        if 'open' in op:
            if op == 'openfile':
                return askopenfile(**kw)
            if op == 'openfilename':
                return askopenfilename(**kw)    
            if op == 'openfiles':
                return askopenfiles(**kw)            
        if op == 'savefile' or op == 'saveasfile':
            return asksaveasfile(**kw)
        if op == 'string':
            return askstring(**kw)    
        
                    
    
def App(title='A frame', size=(800, 600), Frame=aFrame, icon=None):    
    root = tkApp(title, size, icon)
    frame = root.add(Frame)
    frame.size = size
    return frame
    


if __name__ == '__main__':
    app = App()
    layout = app.get('layout')  
    menu = app.get('menu')
    layout.add_left(menu, 100)
    frame = app.get('frame', bg='#333')
    layout.add_top(frame, 32)   
    tree = app.get('tree')
    msg = app.get('msg')
    layout.add_V2(tree, msg)
    #app.add_set1()
    #print(app.tk.getvar('app'))
    app.mainloop()
    
    


