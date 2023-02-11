from aui import App
app = App()

def testv2():
    layout = app.get('layout')    
    tree = app.get('tree')
    msg = app.get('msg')
    layout.add_V2(tree, msg)

def test_set1():
    app.add_set1()
    app.tree.set_path('.')
    
def test_menu():    
    layout = app.get('layout')  
    menu = app.get('menu')
    layout.add_left(menu, 100)
    frame = app.get('frame', bg='#333')
    layout.add_top(frame, 32)   
    tree = app.get('tree')
    msg = app.get('msg')
    layout.add_V2(tree, msg)  
       
test_set1()

app.mainloop()