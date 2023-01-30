#! /usr/bin/python3.8
import os
import sys
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
from PIL import ImageFont
from aui import ImageObj

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
        ln = text.count('\n')     
        n = len(text)
        
        if text[0] in ['[', '{']:
            if ln < 3 and n > 200:
               text = text.replace(', ', ',    \n')
        else:
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
        

class Obj():
    def __init__(self, canvas, item, mode, box, **kw):    
        self.canvas = canvas
        self.mode = mode
        self.canvas_item = item
        self.data = kw
        self.box = box
        self.size = 100, 50
        for item in self.data:
            print(item, self.data[item])
            self.__setattr__(item, self.data[item])
         
        if box == None:
            return
        x1, y1, x2, y2 = box    
        w = x2 - x1
        h = y2 - y1
        self.size = w, h
        
    def update(self):
        box = self.canvas.bbox(self.canvas_item)
        if box == None:
            return
        x1, y1, x2, y2 = box  
        self.pos = (x1, y1)       
        
    def set_color(self, color):    
        self.data['color'] = color
        self.color = color
        self.canvas.itemconfig(self.canvas_item, fill=color)
        
    def moveto(self, xy):
        x, y = xy
        self.canvas.moveto(self.canvas_item, x=x, y=y)
                

class SelectFrame():
    def __init__(self, canvas):
        self.canvas = canvas
        self.obj = None
        self.size = 100, 100
        self.item = canvas.create_rectangle(0, 0, 10, 10, dash=(5,1), tag=('selectframe','fg'))     
        canvas.tag_bind(self.item, '<ButtonPress-1>', self.on_press)
        canvas.tag_bind(self.item, '<ButtonRelease-1>', self.on_release)
        canvas.tag_bind(self.item, '<Motion>', self.on_motion)
     
        self.offset = 0, 0
        self.pos = 0, 0
        self.dragging = False
        
    def set_rect(self, pos, size):
        canvas = self.canvas
        x, y = pos    
        w, h = size        
        x1, y1 = x+w, y+h
        x2, y2 = x+w/2, y+h/2
        canvas.delete('selectframe')
        self.item = self.canvas.create_rectangle(x, y, x1, y1, dash=(3,3), tag=('selectframe','fg'))  
        d = 3 
        canvas.create_rectangle(x1-d, y1-d, x1+d, y1+d, fill='#444', tag=('selectframe', 'dot'))
        self.size = w, h
        self.pos = x, y
        self.offset = w/2, h/2
        #canvas.itemconfig('dot', cursor='cross')        
        
    def on_press(self, event):            
        self.dragging = 'move'
        x, y = event.x, event.y
        x0, y0 = self.pos        
        dx, dy = x-x0, y-y0
        w, h = self.size
        d = 10
        if abs(dx-w) < d and abs(dy-h) < d:
             self.dragging = 'resize'
             print('resize', dx, dy)
             self.canvas.config(cursor='cross')
        self.offset = dx, dy
        self.canvas.tag_raise(self.item)
        
    def on_motion(self, event):
        if self.dragging == False or self.obj == None:
            return
        dx, dy = self.offset    
        x, y = event.x-dx, event.y-dy  
        if self.dragging == 'resize':
            x0, y0 = self.pos
            w, h = event.x - x0, event.y - y0            
            self.size = w,h
        else:                  
            self.pos = x, y
            self.canvas.moveto(self.obj.canvas_item, x=x, y=y)
        
        self.set_rect(self.pos, self.size)
        
    def on_release(self, event):
        self.dragging = False
        obj = self.obj
        x, y = self.pos
        obj.moveto(self.pos)
        item = obj.canvas_item
        self.canvas.config(cursor='arrow')
        #self.canvas.scale(item, w, h, w1/w, h1/w)
        #self.canvas.moveto(item, x=x, y=y)
        #self.canvas.tag_lower(self.item)
        self.set_rect((x, y), self.size)
        
    def includep(self, p):
        x, y = p
        x0, y0 = self.pos
        if x < x0 or y < y0:
            return False            
        w, h = self.size
        x1, y1 = x0 + w, y0 + h
        if x > x1 or y > y1:
            return False            
        return True
            
    def set_obj(self, obj):        
        self.obj = obj
        self.set_rect(obj.pos, obj.size)
        

class ImageCanvas(tk.Canvas):
    def __init__(self, master, **kw):
        tk.Canvas.__init__(self, master, **kw)  
        self.mode = 'move'
        self.text = 'test draw 中文 text'
        self.font = ('Mono', 20)
        self.fontname = '/home/athena/data/ttf/ChinSong1.ttf'
        #self.font = (self.fontname, 16)
        self.imagefont = ImageFont.truetype(self.fontname, 35)
        self.pos = 0, 0
        self.index = 0
        self.lw = 2
        self.color = '#444'
        self.colors = dict(text='#333', line='#999', pen='#444')
        self.objs = []
        self.obj = None
        self.item_obj_map = {}
        self.points = []
        self.data = []
        self.selectframe = SelectFrame(self)
        self.add_text_item(200, 200, self.text)
        self.add_text_item(300, 300, self.text)
        self.set_mode(self.mode)        
        
    def clear(self, event=None):
        for obj in self.objs:            
           self.delete(obj.item)
        self.item_obj_map = {}
        self.objs = []
        self.modified = []     
        self.data = []   
        self.index = 0  
        
    def set_color(self, color):
        self.color = color
        if self.obj != None:
            self.obj.set_color(color)
        
    def set_mode(self, mode):
        self.mode = mode.lower()        
        if self.mode == 'move':
            if self.objs != []:
               self.obj = self.objs[-1]
               self.selectframe.set_obj(self.obj)
            self.bind('<ButtonPress-1>', self.on_press) 
            self.bind('<ButtonRelease-1>', self.on_release)  
            self.bind('<B1-Motion>', self.on_motion)            
        else:    
            self.obj = None
            self.bind('<ButtonPress-1>', self.on_mousedown) 
            self.bind('<ButtonRelease-1>', self.on_mouseup)  
            self.bind('<B1-Motion>', self.on_button_motion)

    def set_input_text(self, text):
        self.text = text
        
    def draw_cur_line(self, x, y):
        self.delete('drawline')
        x0, y0 = self.pos
        self.create_line((x0, y0, x, y), fill=self.color, width = self.lw, tag='drawline')        
                
    def on_button_motion(self, event=None):
        if self.mode == 'move' and self.selectframe.dragging != False:
            self.selectframe.on_motion(event)
            return
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
        
    def select_obj(self, item):
        if type(item ) == tuple:
            item = item[0]
        for tag in self.gettags(item):
            obj = self.item_obj_map.get(tag)
            if obj != None:
                self.selectframe.set_obj(obj)
                return obj
        
    def on_press(self, event):
        x, y = event.x, event.y
        if self.selectframe.includep((x, y)):
            s = str((x, y, 'press'))
            self.selectframe.on_press(event)
        else:
            item = self.find_closest(x, y)
            
            obj = self.select_obj(item)
            s = str((x, y, item))    
            if obj != None:
                self.obj = obj
                self.selectframe.on_press(event)
        self.itemconfig('info', text=s)

    def on_motion(self, event):
        x, y = event.x, event.y
        if self.selectframe.dragging != False:
            self.selectframe.on_motion(event)        
        
    def on_release(self, event):
        x, y = event.x, event.y        
        
        if self.selectframe.dragging != False:
            s = str((x, y, 'release'))
            self.selectframe.on_release(event)
        else:
            item = self.find_closest(x, y)
            obj = self.select_obj(item)
            s = str((x, y, item))
        self.itemconfig('info', text=s)
        
    def on_mousedown(self, event=None, param=None):
        x, y = event.x, event.y     
        self.pos = x, y
        self.points = [(x, y)]        
            
    def puts_item(self, mode, **kw):
        self.data.append((mode, kw))
        self.editor.puts(mode + '=' + str(kw))
        return kw
        
    def get_verts_box(self, verts):   
        x, y = np.transpose(np.array(verts))
        left, right = np.min(x)-1, np.max(x)+1
        top, bottom = np.min(y)-1, np.max(y)+1
        return left, top, right, bottom
        
    def draw_line_points(self, tag, points):         
        verts = curve(points, steps=0.01)
        x0, y0 = verts[0]
        lst = []
        for x, y in verts[1:]:
            item = self.create_line((x0, y0, x, y), fill=self.color, width = self.lw, tag=('pen', tag))   
            lst.append(item)
            x0, y0 = x, y
        return lst    
            
    def add_pen_item(self, x, y):           
        self.points.append((x, y))
        verts = simplify(self.points[1:-2])     
        self.delete('drawpen')        
        tag = 'pen' + str(self.index)
        self.index += 1
        
        box = self.get_verts_box(points)
        obj = Obj(self, tag, 'pen', box, verts=points, color=color)
        self.objs.append(obj)    
        items = self.draw_line_points(tag, verts)
        for item in items:
            self.item_obj_map[item] = obj
        self.item_obj_map[tag] = obj    
        return obj
        
    def get_font_width(self, text):
        font = self.font
        family, size = font
        font = tk.font.Font(family=family, size=size)
        return font.measure(text) 
        
    def add_obj(self, obj, item, tag):
        self.objs.append(obj)
        self.item_obj_map[item] = obj
        self.item_obj_map[tag] = obj
        
    def draw_text(self, x, y, text):
        color = self.colors['text'] 
        tag = 'text' + str(self.index)
        self.index += 1
        item = self.create_text(x, y, text=text, fill=color, font=self.font, anchor='nw', tag=('text', tag))
        box = self.bbox(item)
        obj = Obj(self, tag, 'text', box, text=text, pos=(x, y), color=color)
        self.add_obj(obj, item, tag)
        return obj
        
    def draw_line(self, x0, y0, x, y):
        color = self.colors['line'] 
        p2 = (x0, y0, x, y)
        tag = 'line' + str(self.index)
        self.index += 1
        item = self.create_line(p2, fill=color, width = self.lw, tag=('line', tag))
        box = self.bbox(item)
        #self.puts_item('line', pos=p2, color=color)        
        obj = Obj(self, tag, 'line', box, pos=p2, color=color)
        self.add_obj(obj, item, tag)
        return obj
        
    def add_text_item(self, x, y, text):
        mode = 'text'
        if not '-' in text:           
           self.draw_text(x, y, text)
           return
        lst = text.split('-')
        plst = []        
        y1 = 0
        for s in lst:            
            obj = self.draw_text(x, y, s)
            box = obj.box
            plst.append(box[2])            
            x = box[2] + 72
            if y1 == 0:
               y1 = (box[1] + box[3])//2 + 3
               
        for x in plst[0:-1]:    
            self.draw_line(x+15, y1, x+49, y1)            
                
    def on_mouseup(self, event):
        x, y = event.x, event.y
        x0, y0 = self.pos
        mode = self.mode
        if mode == 'line':
            self.draw_line(x0, y0, x, y)
        if mode == 'pen':
            self.add_pen_item(x, y)            
        elif mode == 'text':    
            self.add_text_item(x, y, self.text)
        self.index += 1
        
    def on_puts_editor(self, event=None):
        for obj in self.objs:
            obj.update()
            if obj.mode == 'line':
                self.puts_item('line', pos=obj.pos, color=obj.color)  
            elif obj.mode == 'text':    
                self.puts_item('\"'+obj.text+'\"', pos=obj.pos, color=obj.color)
            elif obj.mode == 'pen':    
                self.puts_item('pen', color=obj.color, points=obj.verts)  
            
    def add_image(self, imageobj, tag='imageobj'):
        self.tkimage = imageobj.get_tkimage()  
        self.create_image(0, 0, image=self.tkimage, anchor='nw', tag=tag)
        self.update()
        
    def save_image(self):        
        w, h = 1024, 768
        imageobj = ImageObj(size=(w, h))
        lw = self.lw      
        draw = imageobj.get_draw()
        name, fsize = self.font

        for mode, dct in self.data:
            if mode == 'line':     
                x0, y0, x1, y1 = dct['pos']           
                draw.line((x0, y0, x1, y1), fill=dct['color'], width=lw)
            elif mode == 'pen':
                pass
            else:
                pos = dct['pos']
                draw.text(pos, text=mode, fill=dct['color'], font=self.imagefont)     
        from fileio import get_path        
        imageobj.save(get_path('~/tmp/canvas.png'))    
        
            

class CanvasFrame(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master, **kw)
        layout = Layout(self)
        panel = aui.Panel(self)
        layout.add_top(panel, 50)
        self.add_toolbar(panel)        
        canvas = ImageCanvas(self, bg='#f5f3f3')
        self.canvas = canvas                
        self.editor = Editor(self)
    
        self.editor.text.bind('<ButtonRelease-1>', self.get_sel_text)
        self.editor.puts('紅塵-黃-綠-藍-電子')
        canvas.editor = self.editor
        layout.add_V2(canvas, self.editor, 0.6)
        
    def add_toolbar(self, tb):        
        lst = [('Clear', self.on_clear), ('-', ''),
               ('Text', self.on_set_mode), 
               ('Line', self.on_set_mode),
               ('Pen',  self.on_set_mode),
               ('Move', self.on_set_mode), 
               ('Color', self.on_select_color),
               ('-', ''),
               ('Puts on Editor', self.on_puts_editor),
               ('-', ''),
               ('Save Image', self.on_save)
               ]               
        self.buttons = tb.add_buttons(lst)   
        self.buttons[0].set_state(True)
        self.label = tb.add_label(text = 'test draw 中文 text')

    def on_puts_editor(self, event=None):
        self.canvas.on_puts_editor(event)
        
    def on_save(self, event=None):
        self.canvas.save_image()
        
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
        if '\n' in text:           
            label = text.replace('\n', ',')[0:100]
        else:
            label = text
        self.label.config(text=label, fg=self.canvas.color)
        self.canvas.set_input_text(text)
        
    def get_sel_text(self, event=None):
        text = self.editor.get_text('sel')                
        self.set_input_text(text)
        
    def set_data(self, key, text):
        self.set_input_text(key)
        #self.editor.set_text(text + '\n')        
        
    def set_color(self, color):
        self.canvas.set_color(color)
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
        canvas.canvas.msg = selector.msg
        sys.stdout = selector.msg
    
    def on_select(self, key, text):
        self.canvas.set_input_text(key)    
         
    
if __name__ == '__main__':
    app = App('Text to Canvas', size=(1920, 1080))    
    DrawText(app)    
    app.mainloop()

