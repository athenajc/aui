import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import matplotlib

from aui import App
from aui.FigureCanvas import FigureTk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('TkAgg')

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

class FigureCanvas(tk.Canvas):
    def __init__(self, master, size=(1024, 768), **kw):
        w, h = size
        super().__init__(master, width=w, height=h, **kw) 
        self.msg = master.msg
        self.dpi = 100
        self.figure = FigureTk(self, size)   
        G = nx.dodecahedral_graph()
        nodes = nx.draw_networkx_nodes(G, pos=nx.spring_layout(G))
        self.msg.puts(type(nodes))
        #self.figure.ax.add_collection(nodes)
        self.bind('<ButtonRelease-1>', self.on_mouseup)
        
    def on_mouseup(self, event):
        x, y = event.x/self.dpi, event.y/self.dpi
        self.msg.puts(x, y)
        self.patch = self.figure.add_text(x, y, '中文')
        self.figure.ax.add_patch(self.patch.obj) 
        self.figure.update()
        #self.patch = PatchObj(self.mode, self.points, ec=color, fc='none', lw=self.line_width)  

app = App()
msg = app.add('msg')
app.msg = msg
frame = FigureCanvas(app)


layout = app.get('layout')
layout.add_V2(frame, msg, 0.7)

app.mainloop()




