from aui import App

app = App()
layout = app.get('layout')    
tree = app.get('tree')
msg = app.get('msg')
layout.add_V2(tree, msg)
app.mainloop()
