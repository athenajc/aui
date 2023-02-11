from aui import App, Panel

def add_dbfile_entry(self, items=[], act=None):   
    combo = self.add_combo(label='dbFile:', values=items)
    #combo.config(font=(20), width=5)
    if act != None:
        combo.bind('<Return>', act) 
        combo.bind("<<ComboboxSelected>>", act)        
    self.add_sep()
    return combo

def test(event=None):
    print('test', event)

app = App()
panel = Panel(app)
entry = panel.add_combo(label='dbFile:', values=['code', 'note'])
options = panel.add_options(items=['code', 'note'])
options.add('abcd')
app.packfill(panel)
app.mainloop()