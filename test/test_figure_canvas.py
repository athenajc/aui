import tkinter as tk
from aui import  Panel, Layout, ImageObj
from aui.FigureCanvas import FigureCanvas
from aui.ImageGrid import DirGrid
import DB


class ColorGrid(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)    
        self.root = master.winfo_toplevel()
        lst = [('Set as Bkg', self.on_set_bkg), ('Put on Canvas', self.on_put_on_canvas)]
        panel = Panel(self)
        panel1 = Panel(self)      
        self.grid = grid = DirGrid(panel1)          
        panel1.menu = panel1.add_menu(lst)  
        grid.place(x=0, y=45, relwidth=1, relheight=1)
        path = DB.get_path('gallery') + '/bkg'
        grid.set_dir(path)   
        
        colorbar = panel.add_colorbar(self.on_select_color)
        layout = Layout(self)
        layout.add_V2(panel, panel1, 0.3)
        self.pack(fill='both', expand=True)
                
    def on_set_bkg(self, event=None):
        objs = self.grid.get_selection()
        for obj in objs:
            self.canvas.set_bkg(obj.filename)
            break
        
    def on_put_on_canvas(self, event=None):
        objs = self.grid.get_selection()
        for obj in objs:
            print(obj.filename)
            self.canvas.add_image(obj.filename)
        
    def on_select_color(self, event=None):
        color = event.widget.cget('bg')
        print(color)
                  


class Obj():
    def __init__(self, canvas, tag, mode, box, **kw):    
        self.canvas = canvas
        self.mode = mode
        self.tag = tag
        self.data = kw
        self.box = box
        self.modified = False
        self.size = 100, 50
        for item in self.data:
            self.__setattr__(item, self.data[item])
         
        if box == None:
            return
        x1, y1, x2, y2 = box    
        w = x2 - x1
        h = y2 - y1
        self.size = w, h        
                
    def update(self):
        box = self.canvas.bbox(self.tag)
        if box == None:
            return
        x1, y1, x2, y2 = box  
        self.pos = (x1, y1)  
        self.box = box  
        return box
        
    def get_center(self):
        x1, y1, x2, y2 = self.box  
        x = (x1 + x2)/2
        y = (y1 + y2)/2
        return (x, y)
        
    def set_color(self, color):    
        self.data['color'] = color
        self.color = color
        self.canvas.itemconfig(self.tag, fill=color)
        
    def moveto(self, xy):
        x, y = xy
        self.canvas.moveto(self.tag, x=x, y=y)
                

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
        
    def set_rect(self, box):
        canvas = self.canvas
        x1, y1, x2, y2 = box
        x, y = x1, y1 #pos[0:2]    
        w, h = x2-x1, y2-y1        
        #x1, y1 = x+w, y+h
        #x2, y2 = x+w/2, y+h/2
        canvas.delete('selectframe')
        self.item = self.canvas.create_rectangle(x1, y1, x2, y2, dash=(3,3), tag=('selectframe','fg'))  
        d = 3 
        canvas.create_rectangle(x2-d, y2-d, x2+d, y2+d, fill='#444', tag=('selectframe', 'dot'))
        self.box = box
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
        x1, y1, x2, y2 = self.box
        if self.dragging == 'resize':
            x2, y2 = event.x, event.y
            box = x1, y1, x2, y2
        else:                  
            self.pos = x, y
            self.canvas.moveto(self.obj.tag, x=x, y=y)
            box = self.canvas.bbox(self.obj.tag)
        
        self.set_rect(box)
        
    def on_release(self, event):
        self.dragging = False
        obj = self.obj
        if obj == None:
            return
        x, y = self.pos
        obj.moveto(self.pos)
        item = obj.tag
        self.canvas.config(cursor='arrow')
        box = obj.update()        
        obj.modified = True
        self.set_rect(box)
        self.canvas.event_generate("<<ObjMove>>")
        
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
        box = self.canvas.bbox(obj.tag)
        self.set_rect(box)
        
class MoveMode():
    def init_selectframe(self):
        self.objs = []
        self.obj = None
        self.mpos = (0, 0)
        self.selectframe = SelectFrame(self)
        
    def set_move_mode(self):
        if self.objs != []:
           self.obj = self.objs[-1]
           self.selectframe.set_obj(self.obj)
        self.bind('<ButtonPress-1>', self.on_press) 
        self.bind('<ButtonRelease-1>', self.on_release)  
        self.bind('<B1-Motion>', self.on_motion)    

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
        self.mpos = x, y
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
        if (x, y) == self.mpos:
            return
        if self.selectframe.dragging != False:
            s = str((x, y, 'release'))
            self.selectframe.on_release(event)
        else:
            item = self.find_closest(x, y)
            obj = self.select_obj(item)
            s = str((x, y, item))
        self.itemconfig('info', text=s)


class ImageCanvas(FigureCanvas, MoveMode):
    def __init__(self, master, size, **kw):
        super().__init__(master, **kw)  
        self.size = size
        self.root = master.winfo_toplevel()
        self.mode = 'move'
        self.text = '紅塵-黃-綠-藍-電子'
        self.font = ('Mono', 20)

        self.pos = 0, 0
        self.index = 0
        self.lw = 2
        self.color = '#444'
        self.colors = dict(text='#333', line='#999', pen='#444')
        self.objs = []
        self.obj = None
        self.bkg = None
        self.item_obj_map = {}
        self.points = []
        self.data = []
        self.init_selectframe()
        #self.add_text_item(200, 200, self.text)
        self.set_mode(self.mode)        
        
    def clear(self, event=None):
        for obj in self.objs:            
           self.delete(obj.tag)
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
            self.set_move_mode()            
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
        
    def on_mousedown(self, event=None, param=None):
        x, y = event.x, event.y     
        self.pos = x, y
        self.points = [(x, y)]        
        
    def get_verts_box(self, verts):   
        x, y = np.transpose(np.array(verts))
        left, right = np.min(x)-1, np.max(x)+1
        top, bottom = np.min(y)-1, np.max(y)+1
        return left, top, right, bottom
        
    def draw_line_points(self, tag, points, color):         
        verts = curve(points, steps=0.01)
        x0, y0 = verts[0]
        lst = []
        for x, y in verts[1:]:
            item = self.create_line((x0, y0, x, y), fill=color, width = self.lw, tag=('pen', tag))   
            lst.append(item)
            x0, y0 = x, y
        return lst    
            
    def draw_pen(self, points, color=None):
        if color == None:
            color = self.color
        self.delete('drawpen')        
        tag = 'pen' + str(self.index)
        self.index += 1
        
        box = self.get_verts_box(points)
        obj = Obj(self, tag, 'pen', box, points=points, color=color)
        self.objs.append(obj)    
        items = self.draw_line_points(tag, points, color)
        for item in items:
            self.item_obj_map[item] = obj
            
        self.item_obj_map[tag] = obj    
        return obj
        
    def add_pen_item(self, x, y):           
        self.points.append((x, y))
        points = simplify(self.points[1:-2])     
        self.draw_pen(points)
        
    def get_font_width(self, text):
        font = self.font
        family, size = font
        font = tk.font.Font(family=family, size=size)
        return font.measure(text) 
        
    def add_obj(self, obj, item, tag):
        self.objs.append(obj)
        self.item_obj_map[item] = obj
        self.item_obj_map[tag] = obj
        
    def draw_text(self, x, y, text, color=None, anchor='nw', font=None):
        if color == None:
           color = self.colors['text'] 
        if font == None:
            font = self.font    
        tag = 'text' + str(self.index)
        self.index += 1
        item = self.create_text(x, y, text=text, fill=color, font=font, anchor=anchor, tag=('text', tag))
        box = self.bbox(item)
        obj = Obj(self, tag, 'text', box, text=text, pos=(x, y), color=color)
        self.add_obj(obj, item, tag)
        return obj
        
    def draw_line(self, x0, y0, x, y, color=None):
        if color == None:
           color = self.colors['line'] 
        p2 = (x0, y0, x, y)
        tagindex = 'line' + str(self.index)
        tags = tagindex, 'line'
        self.index += 1
        item = self.create_line(p2, fill=color, width = self.lw, tag=tags)
        box = self.bbox(item)     
        obj = Obj(self, tagindex, 'line', box, pos=p2, color=color)
        obj.item = item
        self.add_obj(obj, item, tagindex)
        return obj
        
    def draw_image(self, mode, x, y, filename, imgtag='img'):
        imageobj = ImageObj(filename)
        if imageobj == None:
            return
        tag = mode + str(self.index)
        self.index += 1
        tkimage = imageobj.get_tkimage()  
        item = self.create_image(x, y, image=tkimage, anchor='nw', tag=(mode, tag, imgtag))
        box = self.bbox(item)   
        obj = Obj(self, tag, mode, box, imageobj=imageobj, filename=filename, pos=(x, y))
        obj.tkimage = tkimage
        self.add_obj(obj, item, tag)
        #if mode == 'bkg':
        #    self.lower(item)
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



if __name__ == '__main__':   
    from aui import App
    size = (1800, 1000)
    app = App('ImageCanvas', size)
    layout = app.get('layout')
    canvas = ImageCanvas(app, size, bg='#eaeaea') 
    colorgrid = ColorGrid(app)
    layout.add_H2(canvas, colorgrid, 0.7)  
    colorgrid.canvas = canvas  
    app.mainloop()
    

