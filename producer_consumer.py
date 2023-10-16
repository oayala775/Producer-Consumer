import ttkbootstrap as ttk
import threading as th
import time as t
import random as rd
# import tkinter as tk

window = ttk.Window(themename='superhero')
window.title("Productor - consumidor")
window.state('zoomed')
window.columnconfigure((0,1,2), weight = 1)
window.rowconfigure((0,1,2), weight = 1)

title_label = ttk.Label(text="Productor - consumidor", font="Calibri 24 bold")
title_label.grid(row=0, column=1)


window.mainloop()