import os
import sys
import tkinter as tk
from tkinter import ttk
import time  
from aui import MenuBar, Text, App, TreeView, FileTreeView, Messagebox, TreeView


def get_box( box):  
    lst = []    
    for v in box:
        if type(v) == tk.DoubleVar:
            lst.append(v.get())
        else:
            lst.append(v)                        
    return lst
    
class SpliterVarV():
    def __init__(self, master, sepvar, box, yrange=(0.1, 0.9)):
        self.master = master
        self.layout = master.layout
        spliter = tk.Frame(master, relief='raise', bd=2)
        spliter.config(cursor='hand2')
        spliter.bind('<B1-Motion>', self.drag_v)
        self.spliter = spliter
        self.sepvar = sepvar  
        self.box = box
        self.yrange = yrange
        self.set_place(sepvar.get())        
        for v in self.box:
            if type(v) == tk.DoubleVar:
                v.trace('w', self.on_trace)        

    def set_place(self, yvar):
        x, y, w, h = get_box(self.box)
        x += 0.01
        self.spliter.place(relx=x, rely=yvar, relwidth=w-x, height=8)  
                 
    def on_trace(self, *event):
        yvar = self.sepvar.get()        
        self.set_place(yvar)                  
        
    def drag_v(self, event):
        obj = event.widget
        h = self.layout.size[1]
        obj_y = self.sepvar.get()
        obj_y += (event.y / h) /3
        y1, y2 = self.yrange
        if obj_y < y1:
            obj_y = y1
        elif obj_y > y2:
            obj_y = y2           
        y1 = obj_y + (8 / h) 
        self.set_place(obj_y)
        self.sepvar.set(obj_y)       


class SpliterVarH():
    def __init__(self, master, sepvar, box, xrange=(0.1, 0.9)):
        self.master = master
        self.layout = master.layout
        spliter = tk.Frame(master, relief='raise', bd=2)
        spliter.config(cursor='hand2')
        spliter.bind('<B1-Motion>', self.drag_h)
        self.spliter = spliter
        self.sepvar = sepvar  
        self.box = box        
        self.xrange = xrange
        self.set_pos(self.sepvar.get())       
        for v in self.box:
            if type(v) == tk.DoubleVar:
                v.trace('w', self.on_trace)   
            
    def set_pos(self, xsep):
        x, y, w, h = get_box(self.box)
        dw = w/self.layout.size[0]
        x1, x2 = self.xrange
        relx = xsep    
        self.spliter.place(relx=xsep, rely=y, width=8, relheight=h)
        
    def on_trace(self, *event):    
        xsep = self.sepvar.get()
        self.set_pos(xsep)
        
    def drag_h(self, event):        
        x1, x2 = self.xrange
        obj = event.widget
        obj_x = self.sepvar.get()
        x = event.x
        dw = (abs(x)  / self.master.size[0]) /3
        if x < -1 and obj_x > x1:
            obj_x -= dw
        elif x > 1 and obj_x < x2:
            obj_x += dw         
        self.set_pos(obj_x)    
        self.sepvar.set(obj_x)     
                
         
class AuiObj():
    def add_textobj(self, master, TextClass=None):
        if TextClass == None:
            TextClass = Text
        textbox = TextClass(master)
        if hasattr(textbox, 'init_dark_config'):
            textbox.init_dark_config()   
        textbox.tag_config('find', foreground='black', background='#999')    
        return textbox
        
    def add_msg(self, master):
        msg = Messagebox(master)
        msg.tk.setvar('msg', msg)    
        master.msg = msg
        return msg
        
    def add_filetree(self, master, TreeFrame=FileTreeView):
        tree = TreeFrame(master)
        tree.tk.setvar('filetree', tree)   
        master.filetree = tree
        master.tree = tree
        return tree
        
    def add_tree(self, master, TreeFrame=TreeView):
        tree = TreeFrame(master)
        tree.tk.setvar('filetree', tree)   
        master.filetree = tree
        master.tree = tree
        return tree
        
    def add_menu(self, master):
        names = 'New,Open,,Close,,History,,Save,Save as,,Undo,Redo,,Copy,Cut,Paste,,'
        names += 'Add Tab,Remove Tab,,Graph'
        menubar = MenuBar(master, items=names.split(',')) 
        return menubar
        

class Layout(AuiObj):     
    def __init__(self, master, **kw):              
        self.master = master
        master.layout = self
        self.root = master.winfo_toplevel()           
        self.tk = master.tk     
        self.objs = []
        self.seps = {}
        self.left, self.top = 0, 0
        w, h = master.winfo_width(), master.winfo_height()
        self.size = self.root.size
        top = self.add_sepvar(value=0, name='top')
        left = self.add_sepvar(value=0, name='left')
        bottom = self.add_sepvar(value=1, name='bottom')
        right = self.add_sepvar(value=1, name='right')   
        self.box = left, top, right, bottom 
        master.bind('<Configure>', self.on_config_master)
        
    def on_config_master(self, event):
        w = event.width
        h = event.height
        self.set_sep('left', self.left/w)
        self.set_sep('top', self.top/h)
        self.size = w, h        
        self.update_objs()
        
    def pack(self, **kw):
        pass        
        
    def getvalue(self, v):
        if type(v) == tk.DoubleVar:
            return v.get()
        else:
            return v
        
    def add(self, widget, box):
        if not widget in self.objs:   
            widget.box = box
            self.objs.append(widget)
            self.place_obj(widget)    
        
    def place_obj(self, obj):        
        x, y, w, h = get_box(obj.box)        
        x += 6/self.size[0]
        if x > 1:
            x = x/self.size[0]
        if y > 1:
            y = y/self.size[1]            
      
        obj.place(relx=x, rely=y, relwidth=w-x, relheight=h-y) 
           
    def update_objs(self):         
        for obj in self.objs:
            self.place_obj(obj) 
           
    def update_sep(self, *event):    
        name = event[0]
        self.update_objs()                
        
    def get_sep(self, name):
        name = str(name)
        return self.seps[name].get()
        
    def set_sep(self, name, value):
        name = str(name)
        self.seps[name].set(value)
        
    def add_sepvar(self, value, name):
        obj = tk.DoubleVar(value=value, name=name)
        obj.trace('w', self.update_sep)  
        self.seps[name] = obj
        return obj
        
    def add_left(self, obj, w=100):
        x, y = self.left, self.top
        obj.place(x=x, y=y, width=w, relheight=1)
        self.left += w
        self.set_sep('left', self.left/self.size[0])        
        
    def add_top(self, obj, h=32):
        x, y = self.left, self.top
        obj.place(x=x, y=y, relwidth=1, height=h)
        self.top += h
        self.set_sep('top', self.top/self.size[1])        

    def add_H3(self, objs=(), sep=(0.2, 0.75), box=None):
        if box == None:
            box = self.box
        left, top, right, bottom = box
        x1, x2 = sep
        sep1 = self.add_sepvar(value=x1, name='h1')
        sep2 = self.add_sepvar(value=x2, name='h2')
        y, h = left, bottom
        split1 = SpliterVarH(self.master, sep1, box=(x1, y, 8, h), xrange=(0.1, 0.5))  
        split2 = SpliterVarH(self.master, sep2, box=(x2, y, 8, h), xrange=(0.35, 0.95))
        f0, f1, f2 = objs
        self.add(f0, box=(left, top, sep1, bottom))
        self.add(f1, box=(sep1, top, sep2, bottom))       
        self.add(f2, box=(sep2, top, right, bottom)) 

    def add_H2(self, f0, f1, sep=0.5, xrange=(0.25, 0.75), box=None):
        if box == None:
            box = self.box
        left, top, right, bottom = box
        xsep = self.add_sepvar(value=sep, name='h2')
        split1 = SpliterVarH(self.master, xsep, box=(sep, top, 8, bottom), xrange=xrange)  
        self.add(f0, box=(left, top, xsep, bottom))
        self.add(f1, box=(xsep, top, right, bottom))
        
    def add_V2(self, f0, f1, sep=0.5, yrange=(0.2, 0.9), box=None):
        if box == None:
            box = self.box
        left, top, right, bottom = box
        sepv = self.add_sepvar(value=sep, name='v2')
        spliter = SpliterVarV(self.master, sepv, (left, sep, right, 8), yrange=yrange)    
        self.add(f0, box=(left, top, right, sepv))
        self.add(f1, box=(left, sepv, right, bottom))

    def add_set1(self, objs=(), seph=0.2, sepv=0.7, box=None):            
        if box == None:
            box = self.box
        left, top, right, bottom = box     
        sep1 = self.add_sepvar(value=seph, name='1')        
        tree, f0, f1 = objs
        self.add(tree, (left, top, sep1, bottom))
        self.add_V2(f0, f1, sepv, (0.2, 0.95), box=(sep1, top, right, bottom))
        split1 = SpliterVarH(self.master, sep1, box=(left, top, 8, bottom), xrange=(0.12, 0.6))     
    
    def add_setH(self, objs=(), seph=(0.2, 0.75), sepv=0.6, box=None):   
        if box == None:
            box = self.box
        left, top, right, bottom = box
        x1, x2 = seph
        sep1 = self.add_sepvar(value=x1, name='h1')
        sep2 = self.add_sepvar(value=x2, name='h2')
        y, h = top, bottom
        split1 = SpliterVarH(self.master, sep1, box=(x1, y, 8, h), xrange=(0.1, 0.5))  
        split2 = SpliterVarH(self.master, sep2, box=(x2, y, 8, h), xrange=(0.35, 0.95))
        sepv1 = self.add_sepvar(value=sepv, name='v2')
        spliter = SpliterVarV(self.master, sepv1, (sep1, sepv, sep2, 8), yrange=(0.2, 0.9))  
        f0, f1, f2 = objs
        f1a, f1b = f1
        self.add(f0, box=(left, top, sep1, bottom))
        self.add(f1a, box=(sep1, top, sep2, sepv1))       
        self.add(f1b, box=(sep1, sepv1, sep2, bottom))       
        self.add(f2, box=(sep2, top, right, bottom))      
        

if __name__ == '__main__':
    from aui import App, Panel    
    app = App(title='Test', size=(1100, 900))   
    layout = Layout(app)
    f0 = app.textbox = Text(app)
    f0.init_dark_config()
    f1 = app.msg = layout.add_msg(app)    
    tree = app.tree = FileTreeView(app)
    tree1 = app.tree1 = TreeView(app)

    def test_add_left_top():        
        menu = layout.add_menu(app)
        layout.add_left(menu, 100)
        frame = tk.Frame(app, bg='#333')
        layout.add_top(frame, 32)  
        frame1 = tk.Frame(app, bg='gray')
        layout.add_top(frame1, 32) 
        
    def test_H2():    
        layout.add_H2(f0, f1, 0.6, (0.2, 0.9)) 
        
    def test_V2():    
        layout.add_V2(f0, f1, 0.6, (0.2, 0.9))         
       
    def test_puts():
        app.textbox.open(__file__)
        for i in range(100):
            app.msg.puts(i, ' ' * 10, i)
        
    test_add_left_top()       
    #layout.add_H3(objs=(tree, f0, f1))
    #test_V2()
    layout.add_setH(objs=(tree, (f0, f1), tree1))
    test_puts()
    app.mainloop()






