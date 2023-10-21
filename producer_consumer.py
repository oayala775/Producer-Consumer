import ttkbootstrap as ttk
import threading as th
import time as t
import random as rd
from PIL import Image, ImageTk
from pynput import keyboard

buffer = []
mutex = th.Semaphore(1)
empty_spaces = th.Semaphore(20)
full_spaces = th.Semaphore(0)
stop_threads = False

window = ttk.Window(themename='superhero')
# window = ttk.Tk()
window.title("Productor - consumidor")
window.state('zoomed')
window.columnconfigure((0,1,2), weight = 1)
window.rowconfigure((0,1,2,3), weight = 1)

title_label = ttk.Label(text="Productor - consumidor", font="Calibri 24 bold")
title_label.grid(row=0, column=1, pady=8, padx=8)

working_image = ImageTk.PhotoImage(Image.open("trabajando.png").resize((400,400)))
sleeping_image = ImageTk.PhotoImage(Image.open("durmiendo.png").resize((400,400)))
product_image = ImageTk.PhotoImage(Image.open("process.png").resize((100,100)))
black_square = ImageTk.PhotoImage(Image.open("cuadro_negro.jpeg").resize((100,100)))
entering_image = ImageTk.PhotoImage(Image.open("knocking.png").resize((400,400)))

producer_label = ttk.Label(text="Productor", font="Calibri 16 bold")
producer_label.grid(row=1, column=0, sticky="s")

canvas_producer = ttk.Label(window, image=entering_image)
canvas_producer.grid(row=2, column=0, sticky="n")

producer_state = ttk.Label(text="State", font="Calibri 16 bold")
producer_state.grid(row=3, column=0, sticky="n")

consumer_label = ttk.Label(text="Consumidor", font="Calibri 16 bold")
consumer_label.grid(row=1, column=2, sticky="s")

canvas_consumer = ttk.Label(window, image=sleeping_image)
canvas_consumer.grid(row=2, column=2, sticky="n")

consumer_state = ttk.Label(text="DORMIDO", font="Calibri 16 bold", bootstyle="danger")
consumer_state.grid(row=3, column=2, sticky="n")

buffer_label = ttk.Label(text="Buffer", font="Calibri 16 bold")
buffer_label.grid(row=1, column=1, sticky="s")

buffer_main_frame = ttk.Frame(window,width=1200,height=400)
buffer_main_frame.grid(row=2, column=1, sticky="n")

buffer_main_frame.columnconfigure((0,1,2,3,4,5,6,7,8,9),weight=1)
buffer_main_frame.rowconfigure((0,1,2,3),weight=1)

for i in range(0,20):
    if i < 10:
        ttk.Label(buffer_main_frame,text=str(i+1), font="Calibri 16 bold").grid(row = 0, column=i, padx=10)
        image = ttk.Label(buffer_main_frame,image=black_square)
        buffer.append(image)
        buffer[i].grid(row=1, column=i, padx=10)
    else:
        ttk.Label(buffer_main_frame,text=str(i+1), font="Calibri 16 bold").grid(row = 2, column=i-10, padx=10)
        image = ttk.Label(buffer_main_frame,image=black_square)
        buffer.append(image)
        buffer[i].grid(row=3, column=i-10, padx=10)

class Producer:
    def __init__(self, position):
        self.position = position
    
    def produce(self):
        while True:
            self.time_to_sleep = rd.randint(1, 8)
            if not stop_threads:
                if empty_spaces.acquire():
                    empty_spaces.release()
                    mutex.acquire()
                    amount_to_produce = rd.randint(4, 7)
                    canvas_producer['image'] = working_image
                    producer_state.config(text="ACTIVO", bootstyle="success")
                    for i in range(amount_to_produce):
                        empty_spaces.acquire()
                        full_spaces.release()
                        buffer[self.position].config(image=product_image)
                        t.sleep(1)
                        self.position += 1
                        if self.position == 20:
                            self.position = 0
                    mutex.release()
                    canvas_producer['image'] = sleeping_image
                    producer_state.config(text="DORMIDO", bootstyle="danger")
                    t.sleep(self.time_to_sleep)
                else:
                    canvas_producer['image'] = entering_image
                    producer_state.config(text="INTENTANDO\nENTRAR", bootstyle="warning")
                    t.sleep(1)
                    canvas_producer['image'] = sleeping_image
                    producer_state.config(text="DORMIDO", bootstyle="danger")
                    t.sleep(self.time_to_sleep)

class Consumer:
    def __init__(self, position):
        self.position = position
        
    def consume(self):
        while True:
            self.time_to_sleep = rd.randint(1,8)
            if not stop_threads:
                if full_spaces.acquire():
                    full_spaces.release()
                    mutex.acquire()
                    canvas_consumer['image'] = working_image
                    consumer_state.config(text="ACTIVO", bootstyle="success")
                    amount_to_produce = rd.randint(4,7)
                    if amount_to_produce <= full_spaces._value:
                        for i in range(amount_to_produce):
                            empty_spaces.release()
                            full_spaces.acquire()
                            buffer[self.position].config(image=black_square)
                            t.sleep(1)
                            self.position += 1
                            if self.position >= 20:
                                self.position = 0
                        mutex.release()
                        canvas_consumer['image'] = sleeping_image
                        consumer_state.config(text='DORMIDO', bootstyle="danger")
                        t.sleep(self.time_to_sleep)
                    else:
                        for i in range(full_spaces._value):
                            empty_spaces.release()
                            full_spaces.acquire()
                            buffer[self.position].config(image=black_square)
                            t.sleep(1)
                            self.position += 1
                            if self.position >= 20:
                                self.position = 0
                        canvas_consumer['image'] = entering_image
                        consumer_state.config(text="INTENTANDO\nENTRAR", bootstyle="warning")
                        t.sleep(1)
                        canvas_consumer['image'] = sleeping_image
                        consumer_state.config(text="DORMIDO", bootstyle="danger")
                        mutex.release()
                        t.sleep(self.time_to_sleep)
                else:
                    canvas_consumer['image'] = entering_image
                    consumer_state.config(text="INTENTANDO\nENTRAR", bootstyle="warning")
                    t.sleep(1)
                    canvas_consumer['image'] = sleeping_image
                    consumer_state.config(text="DORMIDO", bootstyle="danger")
                    t.sleep(self.time_to_sleep)

producer = Producer(0)
consumer = Consumer(0)

producing_thread = th.Thread(target=producer.produce)
consumering_thread = th.Thread(target=consumer.consume)

producing_thread.start()
consumering_thread.start()

def on_key_release(event):
    if event.keysym == "Escape":
        window.quit()   
        window.destroy()
        stop_threads = True
                
window.bind('<KeyRelease>',on_key_release)
                        
window.mainloop()

producing_thread.join()
consumering_thread.join()

