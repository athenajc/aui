from aui import App
import tk          
import DB

dct = {'green': '#99c794', 'comment': '#a6acb9', 'key': '#9695d6', 'bg': '#323c44', 'text': '#d8dee9', 'dark': '#202327', 'str': '#f9ae58', 'in': '#e37373', 'name': '#5fb4b4', 'gray': '#777777', 'fg': '#acacac', 'def': '#c695c6'}

def get_colors(app):
    dct = {}
    for button in app.buttons:
        entry = button.entry
        dct[entry.get()] = button.color
    return dct    
    
def on_commit(event=None):
    app = event.widget.app
    text = str(get_colors(app))
    app.msg.puts(text)
    DB.set_cache('aui.colors', text)
    
app = App(size=(600, 700))
panel = app.add('panel')
panel.pack()
buttons = []
dct = eval(DB.get_cache('aui.colors'))
for name, c in dct.items():
    entry = panel.add_entry()
    entry.set(name)
    button = panel.add_button(c, panel.on_select_color)
    button.color = c
    button.entry = entry
    button.config(bg=c)    
    panel.newline()
    buttons.append(button)

app.buttons = buttons    
button = panel.add_button('commit', on_commit)
button.app = app
panel.newline()
msg = panel.get('msg')
panel.add(msg, fill='x')
app.msg = msg
msg.puts(dct)

app.mainloop()




