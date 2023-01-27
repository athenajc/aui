import tkinter as tk
from tkinter import ttk
import PIL


class Button(tk.Button):
    def __init__(self, master, text='', action=None, pack=None, **kw):
        super().__init__(master, text=text, cursor='arrow', **kw)
        self.bg = self.cget('bg') # '#d9d9d9'
        self.group = []
        self.name = text
        self.text = text
        self.action = action     
        self.bind('<ButtonRelease-1>', self.on_click)   
        if pack != None:
           self.pack(*pack)
           
    def on_click(self, event=None):
        if self.action != None:
            self.action(event)
        
    def set_state(self, state=True):
        if state:
            self.config(relief='raised', bg='#d0d0ff', fg='#000')
            self.focus()  
        else:    
            self.config(relief='flat', bg=self.bg, fg='#555')              

def add_button(master, name, action=None, pack=(), **kw):
    btn = Button(master, text=name)
    if action != None:
       btn.bind('<ButtonRelease-1>', action)
    if pack != None:
       btn.pack(pack)
    return btn
    
    
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
        
         
def add_entry(frame, label=None, button=None):                      
    entry = LabelEntry(frame, label=label)
    entry.set('test')
    if button != None:
        entry.add_button(button)   
    return entry
    


class AutoCombo(ttk.Combobox):
    def __init__(self, master, auto=False, **kw):
        ttk.Combobox.__init__(self, master, **kw)
        self.auto = auto
        self.default_values = list(self['values'])
        self._values = self.default_values
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = tk.StringVar()

        self.var.trace('w', self.on_changed)       
        self.pre_token = '' 
        
    def on_changed(self, name, index, mode):    
        if self.get() == self.pre_token:
            return
        self.event_generate('<<TextChanged>>')      
        token = self.get()
        if token == '':
            self['values'] = self.default_values
            self.close_listbox()
            self.pre_token = token
            return
        if self.auto == True:
            if token[-1] == '.':
                self['values'] = get_lst(token.rsplit('.', 1)[0])  
                #self.event_generate('<Down>')                     
                    
        words = self.comparison()        
        if len(words) == 1:
            if len(token) > len(self.pre_token):
                word = words[0]           
                n = len(token) 
                self.insert(n, words[0][n:])
                self.update()
        if words:
            self.update_listbox(words)
        else:
            self.close_listbox()
        self.pre_token = token

    def set_list(self, words):
        self['values'] = words 
        
    def set_text(self, text):
        self.var.set(text)
        
    def close_listbox(self):
        self.event_generate('<Up>')
        
    def update_listbox(self, words):
        if 0: #self.auto == True:
            self['values'] = words        
        
    def matches(self, fieldValue, acListEntry):
        pattern = re.compile(re.escape(fieldValue) + '.*', re.IGNORECASE)
        return re.match(pattern, acListEntry)

    def comparison(self):
        return [ w for w in self['values'] if self.matches(self.var.get(), w) ]

def add_combo(master, text='', values=[]):
    combo = AutoCombo(master, values=values)
    combo.set_text(text)
    return combo
    
def add_sep(frame, w=1, h=100, padx=1, pady=1):
    return tk.Frame(frame, width=w, height=h, bg='#979899')


class PopMenu():
    def add_popmenu(self, cmds=[]):
        menu = tk.Menu(self)
        for p in cmds:
            if p[0] == '-':
                menu.add_separator()
            else:
                menu.add_command(label=p[0], command=p[1])         
        self.menu = menu   
        self.menu.show = False
        self.bind('<ButtonRelease-1>', self.unpost_menu)
        self.bind('<ButtonRelease-3>', self.post_menu)             

    def unpost_menu(self, event=None):
        if self.menu.show == False:
            return
        self.menu.unpost()
        self.menu.show = False
        
    def post_menu(self, event=None):
        x, y = event.x, event.y   
        x1 = event.widget.winfo_rootx()     
        y1 = event.widget.winfo_rooty()
        self.menu.post(x + x1, y + y1)
        self.menu.show = True
        

class ToolBar(tk.Frame):
    def __init__(self, master, **kw):
        tk.Frame.__init__(self, master, **kw)
        self.button = {}
        self.images = {}
        self.pressed = None
        self.bg = self.cget('bg')
        
    def set_pressed(self, label):
        if self.pressed != None:
            self.button[self.pressed].configure(relief='flat')
            self.button[self.pressed].configure(bg=self.bg)
        self.button[label].configure(relief='sunken')
        self.button[label].configure(bg='#777')
        self.pressed = label
            
    def load_image(self, filename):
        img = PIL.Image.open(filename).resize((32, 32))
        tkimage = PIL.ImageTk.PhotoImage(img)
        self.images[filename] = tkimage
        return tkimage
        
    def add_label(self, text, **kw):        
        label = tk.Label(self, text=text, **kw)
        label.pack(side='left')
        return label
        
    def add_button(self, label, image, action):
        img = self.load_image(image)
        button = tk.Button(self, relief='flat', compound='left', image=img)
        button.pack(side='left')
        self.button[label] = button
        button.label = label
        button.bind('<ButtonRelease-1>', action)
        return button        
        
    def add_spinbox(self, label='', value=3, vrange=(1,30), svar=None, action=None):
        if svar == None:
            svar = tk.StringVar(value=value)
        self.add_label(text=label)
        r0, r1 = vrange
        spin_box = ttk.Spinbox(self, from_=r0, to=r1, textvariable=svar, wrap=True, width=3)
        spin_box.pack(side='left')
        spin_box.svar = svar
        if action != None:
           spin_box.bind('<ButtonRelease-1>', action) 
           spin_box.bind('<KeyRelease>', action) 
        return spin_box 
        
    def add_vline(self):
        frame = tk.Frame(self, relief='sunken', bg='#777777', borderwidth=2)
        frame.pack(side='left', fill='y', expand=False, padx=1)
        

class MenuBar(tk.Frame):
    def __init__(self, master, items=[], style='v', **kw):
        super().__init__(master, **kw)
        self.button = {}
        self.style = style
        if style == 'h':
            self.side = 'left'
            self.fill = 'y'
        else:
            self.side = 'top'
            self.fill = 'x'
        self.add_buttons(items)
        
    def reset(self):        
        for widget in self.pack_slaves():
            widget.destroy()
        self.buttons = {}
        
    def add_button(self, key, action=None):
        button = Button(self, text=key, relief='flat', action=action)
        button.pack(side=self.side, fill=self.fill, expand=False) 
        self.button[key] = button
        
    def add_sep(self, h=1):
        if self.style == 'v':
           sep = tk.Frame(self, width=100, height=1, bg='#979899')
           sep.pack(side='top', fill='x', pady=5) 
        else:
           sep = tk.Frame(self, width=1, height=40, bg='#979899')
           sep.pack(side='left', fill='y', padx=5) 
        
    def add_buttons(self, items):        
        self.button = {}
        for key in items:
            action = None
            if type(key) == tuple:
                key, action = key
                
            if key != '':
                self.add_button(key, action)
            else:
                self.add_sep()
          
    def bind_action(self, item, action):
        self.button[item].bind('<ButtonRelease-1>', action) 
         
         
class Panel():
    def __init__(self, master, style='h', items=None, size=None, **kw):
        self.size = size
        self.style = style
        self.relief = 'flat'
        self.master = master
        
        self.base = obj = tk.Text(master, cursor='arrow', **kw)
        obj.config(background = master.cget('background'))
        obj.config(state= "disabled", font=('Mono', 20))
        self.place = self.base.place
        self.widgets = []
        self.limit = 1000
        if items != None:
            self.add_buttons(items, style=style)
        
    def add_scrollbar(self, frame):
        from aui.aui_ui import ScrollBar
        self.scrollbar = ScrollBar(self.base)        

    def reset(self):        
        self.base.delete('1.0', 'end')
        for widget in self.widgets:
            widget.destroy()
        self.widgets = []
        
    def puts(self, *lst, end='\n'):
        text = ''
        for s in lst:
            text += str(s) + ' '
        if len(text) > self.limit:
            text = text[0:self.limit]    
        obj = self.base    
        obj.config(state= "normal")
        obj.insert('end', text + end)
        obj.config(state= "disabled")
        
    def add_space(self, n = 1):
        if self.style == 'h':
            obj = tk.Label(self.base, text='', height=n)
        else:
            obj = tk.Label(self.base, text='', width=n)
        self.add(obj)        
        
    def add_sep(self):
        if self.size != None:
            w, h = self.size
        else:
            w, h = 100, 50
            
        if self.style == 'v':
            sep = add_sep(self.base, w, 1, pady=15)
            self.add(sep)   
        else:
            self.add_space(1) 
            sep = add_sep(self.base, 1, h)
            self.add(sep)   
            self.add_space(1) 
        
    def pack(self, **kw):
        self.base.pack(**kw)
        
    def insert(self, index, widget):        
        if type(widget) == str:
            self.base.insert('end', widget)
        else:
            self.widgets.append(widget)
            self.base.window_create(index, window=widget)
        
    def add(self, widget):
        if type(widget) == list:
            for obj in widget:
                self.base.insert('end', obj)
        elif type(widget) == str:
            self.base.insert('end', widget)
        else:     
            self.insert('end', widget)
        if self.style == 'v':
            self.insert('end', '\n')
        
    def add_combo(self, text='', values=[]):
        add_combo(self.base, text, values)
        self.add(combo)
        return combo
        
    def add_label(self, text, **kw):
        label = tk.Label(self.base, text=text, **kw)    
        self.add(label)
        return label
        
    def add_textvar(self):       
        textvar = tk.StringVar()
        label = tk.Label(self.base, textvariable=textvar, padx=20)
        label.textvar = textvar
        self.add(label)         
        return label
        
    def add_button(self, name, action=None):
        button = Button(self.base, text=name, action=action)
        if self.style == 'v':
            button.config(width=12, relief='flat')
            button.pack(fill='x')
        self.add(button)
        return button
        
    def add_buttons(self, buttons, style='h'):
        self.add_sep()
        lst = []   
        for a, b in buttons:   
            if a == '-' or a == '':
                self.add_sep()
                continue        
            btn = self.add_button(a, b)   
            lst.append(btn) 
        self.add_sep()
        return lst
        
    def add_entry(self, label=None, button=None):   
        entry = add_entry(self.base, label, button)
        self.add(entry)

#----------------------------------------------------------------------------------      
if __name__ == '__main__':   
    from tkinter.messagebox import showinfo
    import aui
    from aui import App
    
    def on_test(event):
        s = event.widget.text
        if s == 'Reset':
            menubar = event.widget.master
            menubar.reset()
            menubar.add_buttons([('Test', on_test), ('ABCD', on_test)])
        else:
            showinfo('[ %s ] selected' % s, s + '\n' + str((event)))
        
    def test_menubar(style):                 
        if style == 'v':
            w, h = 130,860
        else:
            w, h = 1260, 50
        frame = App(title='APP', size=(w, h))
        frame1 = aui.twoframe(frame, 'right', 0.1)
        names = 'Reset,Open,,Close,,History,,Save,Save as,,Undo,Redo,,Copy,Cut,Paste,,'
        names += 'Add Tab,Remove Tab,,Exec,,Run'
        items = []
        for s in names.split(',') :
            items.append((s, on_test))
        panel = Panel(frame1.left, items=items, style=style, size=(w, h)) 
        
        panel.pack(fill='y', expand=False)
        panel.add_scrollbar(frame1.right)   
        frame.mainloop()  
                 
    def test_scrollbar():
        app = App(title='APP', size=(1000,860))   

        panel = Panel(app, size=(960, 860))
        #panel.base.config(width=960//16)
        panel.pack(side='left', fill='both', expand=True)
        panel.add_scrollbar(app)       
        panel.puts('Reset,Open,,Close,,History,,Save,Save as,,Undo,Redo,,Copy,Cut,Paste,,')
        app.mainloop()    
        
    test_scrollbar()
    #test_menubar('v')


