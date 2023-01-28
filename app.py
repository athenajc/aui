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
        
def addFrame(master, Frame):
    frame = Frame(master)
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
    
def add_textobj(master, TextClass=None):
    frame = tk.Frame(master, background='#323c44', relief='sunken', padx=10)
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
    
def add_msg(master):
    msg = Messagebox(master)
    msg.pack(side='left', fill='both', expand=True)
    msg.tk.setvar('msg', msg)    
    return msg
    
def add_filetree(master):
    tree = FileTreeView(master)
    tree.pack(fill='both', expand=True)
    tree.tk.setvar('filetree', tree)   
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

        
class aFrame(tk.Frame):     
    def __init__(self, master, **kw):       
        super().__init__(master, **kw)
        self.master = master
        self.root = master.winfo_toplevel()   
        self.tk = master.tk     
        self.pack(fill='both', expand=True)   

    def mainloop(self):
        self.root.mainloop()
        
    def add(self, WidgetClass):
        frame = WidgetClass()
        frame.pack(fill='both', expand=True) 
        return frame        
        
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
               
class TopFrame(tk.Toplevel):    
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
        
    


def App(title='A frame', size=(800, 600), Frame=None, icon=None):    
    root = tk.Tk()
    root.title(title)
    root.tk.setvar('root', root)
    appname = title.replace(' ', '')
    root.tk.setvar('appname', appname)
    w, h = size
    root.size = size
    root.geometry('%dx%d'%(w, h)) 
    set_icon(root, icon)
    if Frame == None:
        Frame = aFrame
    
    frame = Frame(root)
    frame.size = (w, h)
    #frame.pack(fill='both', expand=True)
    root.tk.setvar('app', frame)
    frame.name = appname
    frame.root = root
    return frame
    
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
filetypes = {
    'py': ('Python files', '*.py, *.txt'),
    'txt': ('Text files', '*.txt, *.py'),
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
            
def askopenfiles(title='Open files', path='/link', ext='py'):          
    return fd.askopenfiles(title=title, initialdir=path, filetypes=get_filetypes(ext))
    
def asksaveasfile(title='Save as file', path='/link', ext='py'):          
    return fd.asksaveasfile(title=title, initialdir=path, filetypes=get_filetypes(ext))

def askstring(title, prompt):
    from tkinter import simpledialog
    answer = simpledialog.askstring(title, prompt)
    return answer


if __name__ == '__main__':
    app = App(title='APP', size=(1500,860))
    app.add_set1()
    print(app.tk.getvar('app'))
    app.mainloop()
    
    


