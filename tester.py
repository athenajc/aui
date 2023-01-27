import tkinter as tk

from aui import App, aFrame, ImageObj

def test_textobj():               
    app = App(title='APP', size=(1500,860))
    app.add_set1()
    app.mainloop()      
    
def test_image():
    w, h = 800, 600
    size = w, h
    bkg = ImageObj(size=size) 
    bkg.get_draw()          
    bkg.gradient('r', 'GnBu')
    bkg.draw.rectangle((10, 10, w-10, h-10), outline=(0, 0, 0, 128))
    bkg.draw.rectangle((9, 9, w-11, h-11), outline=(255, 255, 255, 180))
    bkg.show()
    
if 0:
    test_textobj()
else:    
    test_image()
    

