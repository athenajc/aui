import os
import tkinter as tk
from tkinter import ttk
import re

class LabelEntry():
    def __init__(self, master, text='', cmd=None, label=None, **kw):
        self.master = master
        if label != None:
            label = tk.Label(master, text=label, bg='#232323', fg='white', font=(14))
            label.pack(side='left', padx=5)
        self.entry = tk.Entry(master, **kw)    
        self.entry.pack(side='left', fill='x', expand=True, padx=5)
            
    def add_button(self, *data):
        text, action = data
        btn = add_button(self.master, text, action)
        btn.pack(side='left', padx=5)
        return btn
        
    def get(self):
        return self.entry.get()
        
    def set(self, text):
        entry = self.entry
        n = len(entry.get())
        entry.delete(0, n)
        entry.insert(0, text)       
        
         
def add_entry(frame, label=None, button=None, **kw):                      
    entry = LabelEntry(frame, label=label, **kw)
    if button != None:
        entry.add_button(button)   
    return entry
    
from aui import TextObj 
        
class MsgBox(TextObj):
    def __init__(self, master, **kw):
        super().__init__(master, scroll=False, fill=False, **kw)
        pass
        
    def update_tag(self):
        pass
        
    def flush(self, text=''):
        return
        
    def write(self, text):
        if text.strip() == '':
            return
        self.insert('insert', str(text))

class ScrollBar():
    def __init__(self, target):
        self.base = target
        scrollbar = ttk.Scrollbar(target, command=target.yview, cursor='arrow')
        scrollbar.place(relx=0.987, w=16, rely=0, relheight=1)
        self.scrollbar =  scrollbar
        target.config(yscrollcommand = self.on_scroll)
        target.bind('<Button-4>', self.on_scrollup)
        target.bind('<Button-5>', self.on_scrolldown)  
        
    def on_scrollup(self, event):  
        x, y = self.base.winfo_pointerxy()
        if self.base.winfo_containing(x, y):
           self.base.yview_scroll(-1, 'units')
    
    def on_scrolldown(self, event):
        x, y = self.base.winfo_pointerxy()
        if self.base.winfo_containing(x, y):
            self.base.yview_scroll(1, 'units')        
        
    def on_scroll(self, arg0, arg1):
        self.scrollbar.set(arg0, arg1) 



class CodePanel(tk.Text):
    def __init__(self, master, **kw):
        super().__init__(master, cursor='arrow', **kw)
        self.style = 'h'
        self.relief = 'flat'
        self.master = master
        self.config(background = "#d9d9d9")
        self.config(state= "disabled", font=('Mono', 10))
        self.widgets = []
        
    def add(self, widget):
        self.widgets.append(widget)
        self.window_create('end', window=widget)
            
    def add_scrollbar(self):
        self.scrollbar = ScrollBar(self)        

    def reset(self):        
        self.delete('1.0', 'end')
        for widget in self.widgets:
            widget.destroy()
        self.widgets = []

def set_icon(app, icon):
    if icon == None:
        icon = '/home/athena/data/icon/dev.png'
    try:    
        icon = os.path.realpath(icon)
        root = app.winfo_toplevel()
        root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=icon))  
    except:
        print('load icon', icon, 'fail')

from aui import App
app = App()
panel = CodePanel(app)
app.packfill(panel)
app.mainloop()



