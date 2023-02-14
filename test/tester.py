import tkinter as tk

from aui import App, aFrame, ImageObj
w, h = 1200, 860        
app = App(size=(w, h))

def test_HV(app):
    layout = app.get('layout')
    panel = app.get('panel')
    layout.add_left(panel, 100)
    panel.config(bg='lightblue')

    frame = app.get('frame', bg='darkblue')     
    layout.add_top(frame, 45)    
  
    text = app.add('text')
    text.init_dark_config()
    msg = app.msg = app.add('msg')
    tree = app.tree = app.add('filetree')
    layout.add_HV(tree, text, msg)
    
def test_image(app):
    w, h = app.size
    size = w, h
    label = app.get('image', size=size) 
    label.pack(fill='both', expand=True)
    label.gradient('r', 'GnBu')    
    label.update()
    
def test_set1(app):
    app.add_set1()
    app.tree.set_path('.')
    app.text.open(__file__)
    

def test_class_view(app):    
    from aui.ClassTree import class_view
    class_view(app)
    
def test_class_view_button(app):    
    from aui.ClassTree import class_view
    def on_test(event=None):
        class_view()
    panel = app.add('panel')
    panel.packfill()    
    button = panel.add_button('test', on_test)    
    

app.root.title('test APP')
app.set_icon('puzzle.spng')

def on_test(event):     
    item = event.widget.text
    app.root.title('test App - ' + item)
    if item == 'img':
        test_image(app)  
    elif item == 'hv':
        test_HV(app)
    elif item == 'set1':
        test_set1(app)
    elif item == 'class_view':
        test_class_view(app)    
    elif item == 'class_view_button':
        test_class_view_button(app)         


panel = app.get('panel', height=1)
panel.pack()
for item in ['img', 'hv', 'set1', 'class_view', 'class_view_button']:
    panel.add_button(item, on_test)    
app.mainloop()
    

