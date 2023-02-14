from aui import aFrame
from pprint import pprint, pformat


class dbEditorFrame(aFrame):
    def __init__(self, master, databox=False, **kw):       
        super().__init__(master, **kw)
        root = master.winfo_toplevel()
        self.app = self.root = root
        self.master = master
        self.msg = None
        layout = self.layout = self.get('layout')        
        self.tree_item = None
        panel = self.panel = self.get('panel', bg='#232323', height=1)
        layout.add_top(panel, 42)
        self.add_entry(panel)
        self.databox = None
        self.selector = None
        self.text = self.get('text', width=120)
        self.text.init_dark_config()     
        self.font = ('Mono', 10)
        self.puts = self.text.puts
        if databox == True:
            self.add_databox()
        elif databox == 'msg':
            self.add_msg()
        else:
            layout.add_box(self.text)               
        
        self.tag_config = self.text.tag_config
        self.table = None
        self.db_key = 'temp'        
        
    def add_databox(self):
        self.databox = self.get('text', width=120)       
        self.layout.add_V2(self.text, self.databox, 0.6)
        
    def add_msg(self):
        self.msg = msg = self.get('msg')        
        self.layout.add_V2(self.text, self.msg, 0.7)
        msg.textbox = self.text
        self.text.msg = msg
        
    def set_name(self, name):
        self.name = name
        self.entry.set(name)
        
    def reset(self, event=None):
        self.tree_item = ''
        self.entry.set('')
        self.text.set_text('')           
        
    def set_font_size(self, event=None):
        if type(event) == int:
            n = event
        else:
            n = int(self.font_size_combo.get())
        self.text.config(font=('Mono', n))
        
    def add_entry(self, panel):        
        panel.add_button('New', self.reset)      
        panel.add_button('Del', self.on_delete)      
        lst = [10, 12, 14, 16, 18, 20, 23, 26]
        combo = panel.add_combo(label='Font:', text='10', values=lst, act=self.set_font_size)
        entry = panel.add_entry(label=' Name: ', width=16)
        panel.add_button('commit', self.on_commit) 
        panel.add_button('Rename', self.on_rename)
        
        combo.config(width=5)
        self.font_size_combo = combo
        self.entry = entry        
             
    def get_text(self):
        return self.text.get_text()
        
    def set_text(self, text):
        text = text.strip()
        if len(text) == 0:
            self.text.set_text('')
            return
        ln = text.count('\n') 
        n = len(text)    
        if ln < 2 and n > 200:
            text = pformat(text, width=60, depth=3)
        self.text.set_text(text)
        if self.databox != None:
           self.databox.delete('1.0', 'end')
        
    def update_data(self, dct, objs):  
        if objs == []:
            return   
        box = self.databox    
        pretext = box.get_text()
      
        if objs[0][0] in pretext:       
            start = box.search('pos', '1.0')
            if start == '':
                return
            for name, xy in objs:
                pos = box.search(name, start)
                if pos == '':
                    continue
                p1, p2 = box.index(pos + ' linestart'), box.index(pos + ' lineend')
                line = box.get(p1, p2)
                a, b = line.split('(')
                line1 = a + str(xy) + ','
                box.replace(p1, p2, line1)
        else:
           text = pformat(dct.get('pos'), width=50, depth=3)
           self.databox.delete('1.0', 'end')
           self.databox.insert('1.0', text)
        
    def set_item(self, table, key, item): 
        if table.name == 'note':
            self.set_font_size(14)       
        self.table = table
        self.db_key = key
        self.tree_item = item
        self.entry.set(key)
        res = self.table.getdata(key)
        if len(res) == 0:
            res = 'empty'
        text = res
        self.set_text(text)    
        
    def get_data(self):
        name = self.entry.get()
        text = self.text.get_text()
        return name, text
        
    def on_savefile(self, event=None):        
        text = self.text.get_text()
        self.table.setdata(self.db_key, text)        
        
    def on_new(self, event=None):
        self.app.on_new(event)
        
    def get_db_table(self):
        return self.app.get_db_table()
        
    def on_delete(self, event=None):
        table = self.get_db_table()  
        name = self.entry.get() 
        table.deldata(name)
        self.event_generate('<<UpdateTree>>')
        
    def on_commit(self, event=None):
        name, text = self.get_data()   
        table = self.get_db_table()
        a = table.getnames()
        table.setdata(name, text)
        b = table.getnames()
        if a != b:
           self.event_generate('<<UpdateTree>>')
        
    def on_rename(self, event=None):
        self.app.rename(self.entry.get())   
        
    def on_set_text(self, key, text):
        self.entry.set(key)
        self.text.set_text(text)
        
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
        self.app.setvar('<<RenameItem>>', (self.tree_item, newkey))
        self.app.event_generate('<<RenameItem>>')  
        
    def on_test_cmd(self, arg):        
        text = self.text.get_text()  
        self.puts = self.msg.puts    
        self.msg.clear_all()

        filename = '/home/athena/tmp/tmp.py'
        from fileio import fwrite
        fwrite(filename, text)
        from aui.runfile import RunServer    
        app.server = RunServer(app, filename)  
        
def test(size=(1200, 800)):
    from aui import App           
    def add_db_selector(master, table=None):
        from aui.dbSelector import dbSelector
        panel = dbSelector(master, name='note', table='note') 
        panel.bind_act('select', master.editor.on_set_text)             
        return panel
        
    app = App(size=size)    
    layout = app.get('layout')
    app.editor = editor = dbEditorFrame(app, databox='msg')
    editor.entry.config(width=48)
    panel = add_db_selector(app, table=('note', 'note'))    
    layout.add_H2(panel, editor, 0.3)
    editor.get_db_table = panel.get_db_table
    panel.editor = editor
    panel.msg = editor.msg
    editor.bind('<<UpdateTree>>', panel.update_all)
    app.mainloop()

if __name__ == '__main__':    
    test()
    




