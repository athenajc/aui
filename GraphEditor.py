import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser
import aui
from aui import App, add_entry, Text, Layout, dbSelector, ColorFrame
import shapely
import numpy as np
import matplotlib as mp
from matplotlib import patches, transforms, bezier
from shapely.geometry import polygon, linestring

def curve(points, steps=0.05):
    a = np.array(points)
    t_points = np.arange(0, 1+ steps, steps)    
    bz = bezier.BezierSegment(a)   
    verts = bz.point_at_t(t_points)    
    return np.array(verts).astype(int)

def simplify(points):
    p1 = linestring.LineString(points)
    s = p1.simplify(2, preserve_topology=False)
    a = np.array(s.coords).astype(int)
    return a    
       

class Editor(tk.Frame):
    def __init__(self, master, **kw):       
        super().__init__(master, **kw)
        self.config(padx=10)
        self.tree_item = None
        frame = tk.Frame(self)
        frame.config(padx = 10, pady=5, bg='#232323')  
        self.add(frame)
        self.add_entry(frame)

        self.text = Text(self, width=120)
        self.text.init_dark_config()
        self.puts = self.text.puts
        self.get_text = self.text.get_text
        #self.add(self.text)
        self.text.pack(fill='both', expand=True)
        self.tag_config = self.text.tag_config
        self.table = None
        self.db_key = 'temp'        
        self.text.add_menu_cmd('Set Nane', self.on_setname)   
        
    def add(self, obj):
        obj.pack(fill='x')
        
    def reset(self):
        self.tree_item = None
        self.entry.set('')
        self.text.set_text('')
        
    def add_entry(self, frame):
        frame.config(padx = 10, pady=5, bg='#232323') 
        entry = aui.add_entry(frame, label='Title Name: ', width=70)
        entry.add_button('commit', self.on_commit)               
        entry.set('test')
        self.entry = entry
        entry.add_button('Redraw Canvas', self.on_redraw_canvas)
            
    def set_text(self, text):
        text = text.strip()
        if len(text) == 0:
            self.text.set_text('')
            return
            
        if text[0] in ['[', '{']:
            if check_textlen(text, 200):
               text = text.replace(', ', ',    \n')
        else:
            ln = text.count('\n') 
            n = len(text)
            if ln < 3 and n > 200:
                text = pformat(text, width=200)
        self.text.set_text(text)
        
    def set_item(self, table, key, item):        
        self.table = table
        self.db_key = key
        self.tree_item = item
        self.entry.set(key)
        res = self.table.getdata(key)
        if len(res) == 0:
            res = 'empty'
        text = res
        self.set_text(text)
    
    def get_title(self, text):
        for s in re.findall('((?<=class)\s+\w+)|((?<=def)\s+\w+)|([a-zA-Z]\w+)', text):
            return s
        return ''
        
    def get_data(self):
        name = self.entry.get()
        text = self.text.get_text()
        return name, text
        
    def on_savefile(self, event=None):        
        text = self.text.get_text()
        self.table.setdata(self.db_key, text)        
        
    def on_new(self, event=None):
        self.master.event_generate("<<NewItem>>")
        
    def on_commit(self, event=None):
        self.master.event_generate("<<CommitItem>>")
        
    def new_item(self):    
        #key = time.strftime("%Y%m%d_%H%M%S") 
        self.text.set_text('')
        self.entry.set('')
        self.db_key = ''
        self.focus()        
        return ''
           
    def on_setname(self, event=None):
        newkey = self.text.get_text('sel')
        if len(newkey) < 2:
            return        
        self.table.renamedata(self.db_key, newkey)
        self.db_key = newkey
        self.entry.set(newkey)
        self.master.setvar('<<RenameItem>>', (self.tree_item, newkey))
        self.master.event_generate('<<RenameItem>>')  
        
    def on_redraw_canvas(self, event=None):
        pass

class ImageCanvas(tk.Canvas):
    def __init__(self, master, **kw):
        tk.Canvas.__init__(self, master, **kw)  
        self.mode = 'text'
        self.text = 'test draw 中文 text'
        self.pos = 0, 0
        self.index = 0
        self.lw = 2
        self.color = 'blue'
        self.items = []
        self.points = []
        self.bind('<ButtonPress-1>', self.on_mousedown) 
        self.bind('<ButtonRelease-1>', self.on_mouseup)  
        self.bind('<B1-Motion>', self.on_button_motion)
        
    def clear(self, event=None):
        for item in self.find_all():
            self.delete(item)
        self.items = []
        self.modified = []        
        self.index = 0  
        
    def set_color(self, color):
        self.color = color
        
    def set_mode(self, mode):
        self.mode = mode.lower()

    def set_input_text(self, text):
        self.text = text
        
    def draw_cur_line(self, x, y):
        self.delete('drawline')
        x0, y0 = self.pos
        self.create_line((x0, y0, x, y), fill=self.color, width = self.lw, tag='drawline')
        
    def on_button_motion(self, event=None):
        x, y = event.x, event.y  
        mode = self.mode  
        if mode == 'pen':
            x0, y0 = self.pos
            self.create_line((x0, y0, x, y), fill=self.color, width = self.lw, tag='drawpen')
            self.pos = x, y
            if not self.pos in self.points:
               self.points.append(self.pos)
        elif mode == 'line':
            self.draw_cur_line(x, y)
        
    def on_mousedown(self, event=None, param=None):
        x, y = event.x, event.y     
        self.pos = x, y
        self.points = [(x, y)]
            
    def add_item(self, mode, **kw):
        self.editor.puts('Graph[\"%s\"].append('%mode, str(kw) +'}')
        
    def draw_line_points(self, points):
        verts = curve(points, steps=0.01)
        x0, y0 = verts[0]
        for x, y in verts[1:]:
            self.create_line((x0, y0, x, y), fill=self.color, width = self.lw, tag='pen')   
            x0, y0 = x, y
            
    def add_pen_item(self, x, y):           
        self.points.append((x, y))
        verts = simplify(self.points[1:-2])
        self.add_item('pen', fill=self.color, points=verts)
        self.delete('drawpen')
        self.draw_line_points(verts)
        
    def on_mouseup(self, event):
        x, y = event.x, event.y
        x0, y0 = self.pos
        mode = self.mode
        if mode == 'line':
            self.add_item(mode, box=(x0, y0, x, y), fill=self.color )
            self.create_line((x0, y0, x, y), fill=self.color, width = self.lw, tag='line')
        if mode == 'pen':
            self.add_pen_item(x, y)            
        elif mode == 'text':    
            self.add_item(mode, pos=(x, y), text=self.text, fill=self.color)
            self.create_text(x, y, text=self.text, fill=self.color, tag='text')
        self.index += 1

class CanvasFrame(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master, **kw)
        layout = Layout(self)
        panel = aui.Panel(self)
        layout.add_top(panel, 50)
        self.add_toolbar(panel)        
        canvas = ImageCanvas(self, bg='#f5f3f3')
        self.canvas = canvas        
        canvas.create_text(65, 100, text='test draw 中文 text', tag='TEXT', anchor='nw')   
        self.editor = Editor(self)
    
        self.editor.text.bind('<ButtonRelease-1>', self.get_sel_text)
        canvas.editor = self.editor
        layout.add_V2(canvas, self.editor, 0.6)
        
    def add_toolbar(self, tb):        
        lst = [('Clear', self.on_clear), ('-', ''),
               ('Text', self.on_set_mode), 
               ('Line', self.on_set_mode),
               ('Pen',  self.on_set_mode),
               ('Color', self.on_select_color)]               
        self.buttons = tb.add_buttons(lst)   
        self.buttons[0].set_state(True)
        self.label = tb.add_label(text = 'test draw 中文 text')

    def on_clear(self, event=None):
        self.canvas.clear()
        
    def on_select_color(self, event=None):        
        color_code = colorchooser.askcolor(title ="Choose color")
        c0, c1 = color_code
        self.label.config(fg=c1)
        self.canvas.set_color(c1)
        
    def on_set_mode(self, event=None):
        button = event.widget
        for bn in self.buttons:
            bn.set_state(False)
        button.set_state(True)
        self.canvas.set_mode(button.text)
        
    def set_input_text(self, text):
        self.label.config(text=text, fg=self.canvas.color)
        self.canvas.set_input_text(text)
        
    def get_sel_text(self, event=None):
        text = self.editor.get_text('sel')
        self.set_input_text(text)
        
    def set_data(self, key, text):
        self.set_input_text(key)
        #self.editor.set_text(text + '\n')
        
        
    def set_color(self, color):
        self.canvas.color = color
        self.label.config(fg=color)

class DrawText(tk.Frame):
    def __init__(self, app, **kw):
        super().__init__(app, **kw)
        self.layout = Layout(self)
        selector = dbSelector(self, 'note', 'Graph') 
        self.tk.setvar('selector', selector)
        canvas = CanvasFrame(self) 
        colorbox = ColorFrame(self)
        self.layout.add_H3(selector, canvas, colorbox, sep=(0.2, 0.8))
        self.canvas = canvas 
        selector.editor = canvas.editor
        selector.bind_act('select', self.canvas.set_data)
        colorbox.bind_act('select', self.canvas.set_color)
        self.pack(fill='both', expand=True)
        canvas.editor.bind_all('<<CommitItem>>', selector.on_commit)  
    
    def on_select(self, key, text):
        self.canvas.set_input_text(key)    
         
    
if __name__ == '__main__':
    app = App('Text to Canvas', size=(1920, 1080))    
    DrawText(app)    
    app.mainloop()

