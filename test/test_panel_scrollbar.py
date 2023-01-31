from aui import App

def test_scrollbar():
    app = App(title='APP', size=(1000,860))   
  
    panel = app.add('panel', size=(960, 860))
    panel.pack(side='left', fill='both', expand=True)
    
    panel.add_scrollbar()       
    panel.puts('Reset,Open,,Close,,History,,Save,Save as,,Undo,Redo,,Copy,Cut,Paste,,')
    app.mainloop()    
    
test_scrollbar()



