import tkinter as tk
from aui import App

def test(app):
    layout = app.get('layout')    
    menu = app.get('menu')
    layout.add_left(menu, 100)
    frame = app.get('frame', bg='#333')
    layout.add_top(frame, 32)  
    frame1 = app.get('frame',  bg='gray')
    layout.add_top(frame1, 32) 


app = App()
test(app)
app.mainloop()