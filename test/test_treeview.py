from aui import App, TreeView


app = App('A TreeView', size=(500, 800))   
layout = app.get('layout')
panel = app.get('panel')
msg = app.get('msg')
layout.add_V2(panel, msg, 0.7)
tree = TreeView(panel)
tree.enable_edit()

panel.add_button('Reset', tree.clear)
panel.add_button('New', lambda event=None: tree.add_dct('', dct))  
panel.add_button('Add', tree.new_node)  
panel.add(tree)
tree.place(x=0, y=45, relwidth=1, relheight=0.95)

def dctview(dct=None):

    if dct == None:
        dct = {'a':123, 'b':['ab', 'cd', 'ef', {1:'test', 2:'pratice', 3:'operation'}]}
    tree.add_dct('', dct)



dctview()

app.mainloop() 