from aui import App

def on_test(event=None):
    print(event.widget.name)
    
app = App()
layout = app.get('layout')  
panel = app.add('panel')
layout.add_top(panel, 45)  
entry = panel.add_entry(label='File:')
lst = [('test', on_test), ('open', on_test)]
panel.add_buttons(lst, relief='flat')

tree = app.add('tree')
msg = app.add('msg')
layout.add_V2(tree, msg)
app.mainloop()