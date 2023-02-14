#! /usr/bin/python3.8
import os, sys, re, time
import tkinter as tk
from random import Random
from pprint import pformat
from aui import  aFrame, Panel
import DB          
        
class dbSelector(aFrame):     
    def __init__(self, master, name='code', table=None, **kw):       
        super().__init__(master, **kw)
        self.size = master.size
        self.app = self
        icon = '/home/athena/data/icon/view.png'
        master.winfo_toplevel().set_icon(icon)
        self.bg = self.cget('bg')
        self.fg = self.cget('highlightcolor')
        self.config(borderwidth=3)
        self.editor = None
        self.root = self.winfo_toplevel()
        self.db = DB.open(name)
        self.name = name
        self.tables = tables = self.db.get('tables')
        self.table = None
        self.vars = {'history':[]}
        self.data = []
        self.tree_item = ''
         
        self.init_ui()   
        self.dboptions.set(name)
        if table != None:
            if tables != None and len(tables) > 1: 
                table = tables[0]
        self.set_table_menu(table)    
        self.update_all()   
        self.actions = {}   
        
    def on_select_db(self, event=None, arg1=None, arg2=None):
        if type(event) == str:
            name = self.getvar(event)
        else:
            name = event.widget.get()   
        self.set_db(name)
        
    def set_db(self, name, table=None):
        self.name = name
        self.db = DB.open(name)
        self.dboptions.set(name)
        names = self.db.get('tables')
        if names == [] or names == None:
            return
        if table == None:
            table = Random().choice(names)     
        self.tables = names    
        self.set_table_menu(table)    
        
    def get_db_table(self):
        return self.table
          
    def bind_act(self, event, action):
        self.actions[event] = action
        
    def set_table_menu(self, table_name=None):
        self.menubar.reset()   
        self.menubar.base.config(pady=3)    
        lst = []
        for s in self.tables:
            lst.append((s, self.on_select_table))
        lst.append(('-', 0))
        lst.append(('+', self.on_create_table))    
        btns = self.menubar.add_buttons(lst, style='v')
        self.buttons = btns
        for b in btns:
            b.config(width=7, relief='flat')
        if table_name == None:
            return
        self.table = self.db.get_table(table_name)         
        dct = self.menubar.button
        for bn in dct:            
            dct[bn].set_state(bn == table_name)       
    
    def update_all(self, event=None):
        if self.table == None:
            return
        self.item_names = names = self.table.getnames()        
        self.tree.set_list(names)
        table_name = self.table.name
        name1 = table_name + '-' + str(len(names)) + ' '   
        title = self.name + ':' + name1
        self.textvar.set(name1)
        self.root.title(self.name + '-' + table_name) 

    def switch_table(self, table_name='example'): 
        table_name = str(table_name)   
        self.table = self.db.get_table(table_name)   
        dct = self.menubar.button
        for bn in dct:            
            dct[bn].set_state(bn == table_name)   
        #self.update_all()
        
    def on_create_table(self, event=None): 
        table_name = self.app.askstring('Input Sting', 'New table name?')
        if table_name == None:
            return
        self.table = self.db.create(table_name)
        self.set_db(self.name, table_name)
        self.update_all()
            
    def on_select_table(self, event=None):        
        table_name = str(event.widget.name)            
        self.switch_table(table_name)  
        self.update_all()             
        
    def on_new_item(self, event=None):
        self.editor.new_item()
        self.tree_item = ''
        
    def on_import(self, event=None):
        files = aui.askopenfiles(ext='py')
        if files == None or len(files) == 0:
            return
        for fp in files:     
            name = os.path.basename(fp.name).split('.', 1)[0]
            text = fp.read()
            self.table.setdata(name, text)  
        self.update_all()
        
    def on_commit(self, event=None):              
        name, text = self.editor.get_data()    
        
        if self.tree_item != '':
            prename = self.tree.get_text(self.tree_item)  
            self.table.delete_key(prename)
            self.msg.puts('on_commit', [prename, name])
        else:
            self.msg.puts('on_commit', [name])    
        self.table.insert_data(name, text)    
        self.item_names = self.table.get('names')
        self.tree.set_list(self.item_names)
        
    def on_copy(self, event=None):
        self.clipboard_clear()
        text = self.textbox.get_text()
        self.clipboard_append(text)   
        
    def on_save(self, event=None):
        self.on_commit(event)
        
    def on_delete_item(self, event=None):
        item = self.tree.focus()
        dct = self.tree.item(item)
        self.msg.puts('delete', item, dct)
        if item == '':
            return    
        key = dct.get('text')
        self.table.deldata(key)    
        self.tree.remove_item(item)
                
    def update_item(self, key, item):
        data = (self.table.name, key, item)
        info = str(data)
        self.msg.set_text(info + '\n')
        self.root.title(info)
        text = self.table.getdata(key)
        if self.editor != None:
            self.editor.set_item(self.table, key, item)    
        if 'select' in self.actions:
            act = self.actions['select']
            act(key, text)     
        
    def on_select(self, event=None):         
        item, key = self.tree.get_focus_item_and_key()
        self.update_item(key, item)       
        
    def on_rename_item(self, event=None):
        p = event.widget.getvar('<<RenameItem>>')
        if p == None:
            return
        item, newkey = p
        self.msg.puts('rename', self.tree.item(item))
        self.tree.set_node_data(item, newkey)         

    def init_top_panel(self, panel):        
        panel.config(bg=self.cget('bg'), font=('Mono', 11))

        dbfiles = ['code', 'cache', 'file', 'note']
        self.dboptions = self.add_dbfile_entry(panel, dbfiles, act = self.app.on_select_db) 
        self.textvar = self.add_textlabel(panel)                
        
    def on_dbentry(self, event=None):
        name = event.widget.get()
        if not name in self.dboptions.items:
            self.dboptions.add(name)
        
    def add_dbfile_entry(self, panel, items=[], act=None):
        options = panel.add_options(label='dbFile:', items=items, act=act)  
        options.config(width=8) 
        entry = panel.add_entry(act=self.on_dbentry)        
        entry.config(width=7)
        panel.add_sep()
        return options       
        
    def add_textlabel(self, panel):
        label = panel.add_textvar()
        label.config(relief='sunken', height=2, bg='#aaa', font=('Serif', 10))
        return label.textvar
        
    def init_ui(self):
        x, y = 100, 45
        layout = self.get('layout')        
               
        self.panel = self.get('panel')
        layout.add_top(self.panel, y)  
        self.menubar = self.get('panel', style='v', width=12) 
        layout.add_left(self.menubar, x)  
        
        tree = self.tree = self.add('tree')
        msg = self.msg = self.add('msg')
        layout.add_V2(tree, msg, sep=0.9)
     
        tree.click_select = 'click'   
        tree.bind('<ButtonRelease-1>', self.on_select) 
        
        self.init_top_panel(self.panel)
         


class dbMenuPanel(Panel):     
    def __init__(self, master, name='code', table=None, **kw):       
        super().__init__(master, **kw)        
        self.root = self.winfo_toplevel()        
        self.db = DB.open(name)
        self.name = name
        tables = self.db.get('tables')
        self.table = table
        self.vars = {'history':[]}
        self.data = []
        self.tree_item = ''
        self.editor = None 
        self.init_ui()      
        self.dboptions.set(name)        
        if self.table != None:
           self.switch_table(table)  
        elif tables != None and len(tables) > 1: 
           self.switch_table(tables[0]) 
        self.actions = {}   
          
    def get_db_table(self):
        return self.table
        
    def bind_act(self, event, action):
        self.actions[event] = action
    
    def update_all(self):
        if self.table == None:
            return
        self.item_names = names = self.table.getnames()        
        self.tree.set_list(names)
        table_name = self.table.name
        name1 = table_name + '-' + str(len(names)) + ' '   
        title = self.name + ':' + name1
        self.root.title(self.name + '-' + table_name) 

    def switch_table(self, table_name='example'): 
        table_name = str(table_name)   
        self.table = self.db.get_table(table_name)   
        if (self.table_opt.get() != table_name):
            self.table_opt.set(table_name)
        self.update_all()        
            
    def on_select_table(self, event=None):  
        if event == None:
            return      
        table_name = event.text              
        self.switch_table(table_name)               
        
    def on_select_db(self, event=None, arg1=None, arg2=None):
        if type(event) == str:
            name = self.getvar(event)
        else:
            name = event.text   
        if self.name != name:    
           self.set_db(name)
        
    def set_db(self, name):
        self.name = name
        self.db = DB.open(name)
        names = self.db.get('tables')
        if names == [] or names == None:
            return
        if self.table_opt.items != names:
            self.table_opt.set_items(names)          
        name = Random().choice(names)
        self.switch_table(name)      

    def update_item(self, key, item):
        data = (self.table.name, key, item)
        info = str(data)       
        self.root.title(info)
        text = self.table.getdata(key)
        if self.editor != None:
            self.editor.set_item(self.table, key, item)    
        if 'select' in self.actions:
            act = self.actions['select']
            act(key, text)     
        
    def on_select(self, event=None):         
        item, key = self.tree.get_focus_item_and_key()
        self.update_item(key, item)              
        
    def add_opt_button(self, items=[], act=None):
        options = self.add_options(items=items, act=act)  
        options.config(width=8) 
        return options     
        
    def init_ui(self):
        dbfiles = ['code', 'cache', 'file', 'note']
        self.dboptions = self.add_opt_button(dbfiles, act = self.on_select_db) 
        self.dboptions.config(width=4, anchor='nw')   
        dbtables = self.db.get('tables')
        self.table_opt = self.add_opt_button(dbtables, act = self.on_select_table) 
        self.table_opt.config(width=8, anchor='nw')   
        self.newline()
        tree = self.tree = self.get('tree')
        self.add(tree, fill='y')
        tree.click_select = 'click'   
        tree.bind('<ButtonRelease-1>', self.on_select) 


def test(name):    
    from aui import App        
    if 0:
       app = App('DB Table Selector', size=(800, 900))    
       panel = dbMenuPanel(app, 'note', 'Graph')    
       sep = 0.2
    else:   
       app = App('DB Table Selector', size=(1200, 900))   
       panel = dbSelector(app, 'note', 'note')
       sep = 0.3
    from aui.dbEditorFrame import dbEditorFrame     
    panel.editor = editor = dbEditorFrame(app) 
    editor.entry.config(width=48)
    editor.get_db_table = panel.get_db_table
    layout = app.get('layout') 
    layout.add_H2(panel, editor, sep)

    app.mainloop()   
            
if __name__ == '__main__':   
    test('code')
    #test()

        
    

