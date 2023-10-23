import ttkbootstrap as ttk
import threading as th
import time as t
import random as rd
from PIL import Image, ImageTk

# Global variables
# Creates the shared buffer
buffer = []
# Creates the mutex to lock the buffer
mutex = th.Semaphore(1)
# Creates the semaphore to control the number of empty spaces
empty_spaces = th.Semaphore(20)
# Creates the semaphore to control if the buffer is full
full_spaces = th.Semaphore(0)
# Variable used to stop the threads
stop_threads = False

# Configuration of the window
window = ttk.Window(themename='superhero')
window.title("Productor - consumidor")
window.state('zoomed')
window.columnconfigure((0,1,2), weight = 1)
window.rowconfigure((0,1,2,3), weight = 1)

title_label = ttk.Label(text="Productor - consumidor", font="Calibri 24 bold")
title_label.grid(row=0, column=1, pady=8, padx=8)

# Images of the states
working_image = ImageTk.PhotoImage(Image.open("trabajando.png").resize((400,400)))
sleeping_image = ImageTk.PhotoImage(Image.open("durmiendo.png").resize((400,400)))
product_image = ImageTk.PhotoImage(Image.open("process.png").resize((100,100)))
black_square = ImageTk.PhotoImage(Image.open("cuadro_negro.jpeg").resize((100,100)))
entering_image = ImageTk.PhotoImage(Image.open("knocking.png").resize((400,400)))

producer_label = ttk.Label(text="Productor", font="Calibri 16 bold")
producer_label.grid(row=1, column=0, sticky="s")

# Canvas where the image of the producer will be displayed
canvas_producer = ttk.Label(window, image=entering_image)
canvas_producer.grid(row=2, column=0, sticky="n")

# Label to display the state of the producer
producer_state = ttk.Label(text="State", font="Calibri 16 bold")
producer_state.grid(row=3, column=0, sticky="n")

consumer_label = ttk.Label(text="Consumidor", font="Calibri 16 bold")
consumer_label.grid(row=1, column=2, sticky="s")

# Canvas where the image of the consumer will be displayed
canvas_consumer = ttk.Label(window, image=sleeping_image)
canvas_consumer.grid(row=2, column=2, sticky="n")

# Label to display the state of the consumer
consumer_state = ttk.Label(text="DORMIDO", font="Calibri 16 bold", bootstyle="danger")
consumer_state.grid(row=3, column=2, sticky="n")

buffer_label = ttk.Label(text="Buffer", font="Calibri 16 bold")
buffer_label.grid(row=1, column=1, sticky="s")

# Frame where the buffer will be displayed
buffer_main_frame = ttk.Frame(window,width=1200,height=400)
buffer_main_frame.grid(row=2, column=1, sticky="n")

buffer_main_frame.columnconfigure((0,1,2,3,4,5,6,7,8,9),weight=1)
buffer_main_frame.rowconfigure((0,1,2,3),weight=1)

# Creation of the buffer and displaying of the buffer states
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

# Producer class
class Producer:
    def __init__(self, position):
        self.position = position
    
    def produce(self):
        while True:
            # Gets the variable time to sleep
            self.time_to_sleep = rd.randint(1, 8)
            # If the stop_threads variable is true, the thread stops
            if not stop_threads:
                # Checks if there is any available space in the buffer
                if empty_spaces.acquire():
                    # Releases the empty spaces semaphore
                    empty_spaces.release()
                    # Acquires the mutex to lock the buffer
                    mutex.acquire()
                    # Gets a variable with the amount of products to produce
                    amount_to_produce = rd.randint(4, 7)
                    # Sets the image of the producer to working
                    canvas_producer['image'] = working_image
                    # Sets the state of the producer to active
                    producer_state.config(text="ACTIVO", bootstyle="success")
                    # Produces every product indicated by the amount_to_produce variable
                    for i in range(amount_to_produce):
                        # Reduces the amount of empty spaces
                        empty_spaces.acquire()
                        full_spaces.release()
                        # Sets the image of the buffer to the product image
                        buffer[self.position].config(image=product_image)
                        # Sleeps for 1 second
                        t.sleep(1)
                        # Increments the position of the buffer by 1
                        self.position += 1
                        # If the position is greater than 20, it resets the position to 0 to make the buffer circular
                        if self.position == 20:
                            self.position = 0
                    # Unlocks the buffer
                    mutex.release()
                    # Sets the image of the producer to sleeping
                    canvas_producer['image'] = sleeping_image
                    # Sets the state of the producer to sleeping
                    producer_state.config(text="DORMIDO", bootstyle="danger")
                    # Sleeps the producer for the time indicated by the time_to_sleep variable
                    t.sleep(self.time_to_sleep)
                # If the buffer is full
                else:
                    # Sets the image of the producer to entering_image
                    canvas_producer['image'] = entering_image
                    # Sets the state of the producer to trying to enter
                    producer_state.config(text="INTENTANDO\nENTRAR", bootstyle="warning")
                    # Sleeps for 1 second
                    t.sleep(1)
                    # Sets the image of the producer to sleeping
                    canvas_producer['image'] = sleeping_image
                    # Sets the state of the producer to sleeping
                    producer_state.config(text="DORMIDO", bootstyle="danger")
                    # Sleeps the producer for the time indicated by the time_to_sleep variable
                    t.sleep(self.time_to_sleep)

# Consumer class
class Consumer:
    def __init__(self, position):
        self.position = position
        
    def consume(self):
        while True:
            # Gets the variable time to sleep
            self.time_to_sleep = rd.randint(1,8)
            # If the stop_threads variable is true, the thread stops
            if not stop_threads:
                # Checks if there is any product in the buffer
                if full_spaces.acquire():
                    # Releases the full spaces semaphore
                    full_spaces.release()
                    # Locks the buffer to prevent other threads from accessing the buffer
                    mutex.acquire()
                    # Sets the image of the consumer to working
                    canvas_consumer['image'] = working_image
                    # Sets the stae of the consumer to active
                    consumer_state.config(text="ACTIVO", bootstyle="success")
                    # Gets the variable with the amount of products to consume
                    amount_to_produce = rd.randint(4,7)
                    # If there is enough products in the buffer to consume
                    if amount_to_produce <= full_spaces._value:
                        # Consumer every product indicated by the amount_to_produce variable
                        for i in range(amount_to_produce):
                            # Lowers the amount of empty spaces
                            empty_spaces.release()
                            # Indicates there is a product in the buffer
                            full_spaces.acquire()
                            # Sets the image of the buffer to the black square
                            buffer[self.position].config(image=black_square)
                            # Sleeps for 1 second
                            t.sleep(1)
                            # Increments the position of the buffer by 1
                            self.position += 1
                            # If the position is greater than 20, it resets the position to 0 to make the buffer circular
                            if self.position >= 20:
                                self.position = 0
                        # Unlocks the buffer
                        mutex.release()
                        # Sets the image of the consumer to sleeping
                        canvas_consumer['image'] = sleeping_image
                        # Sets the state of the consumer to sleeping
                        consumer_state.config(text='DORMIDO', bootstyle="danger")
                        # Sleeps the consumer for the time indicated by the time_to_sleep variable
                        t.sleep(self.time_to_sleep)
                    # If there is not enough products in the buffer to consume
                    else:
                        # It consumes all the products in the buffer
                        for i in range(full_spaces._value):
                            # Lowers the amount of empty spaces
                            empty_spaces.release()
                            # Indicates there is a product in the buffer
                            full_spaces.acquire()
                            # Sets the image of the buffer to the black square
                            buffer[self.position].config(image=black_square)
                            # Sleeps for 1 second
                            t.sleep(1)
                            # Increments the position of the buffer by 1
                            self.position += 1
                            # If the position is greater than 20, it resets the position to 0 to make the buffer circular
                            if self.position >= 20:
                                self.position = 0
                        # Sets the image of the consumer to entering
                        canvas_consumer['image'] = entering_image
                        # Sets the state of the consumer to trying to enter
                        consumer_state.config(text="INTENTANDO\nENTRAR", bootstyle="warning")
                        # Sleeps for 1 second
                        t.sleep(1)
                        # Sets the image of the consumer to sleeping
                        canvas_consumer['image'] = sleeping_image
                        # Sets the state of the consumer to sleeping
                        consumer_state.config(text="DORMIDO", bootstyle="danger")
                        # Unlocks the buffer
                        mutex.release()
                        # Sleeps the consumer for the time indicated by the time_to_sleep variable
                        t.sleep(self.time_to_sleep)
                # If there is no product in the buffer
                else:
                    # Sets the image of the consumer to entering
                    canvas_consumer['image'] = entering_image
                    # Sets the state of the consumer to trying to enter
                    consumer_state.config(text="INTENTANDO\nENTRAR", bootstyle="warning")
                    # Sleeps for 1 second
                    t.sleep(1)
                    # Sets the image of the consumer to sleeping
                    canvas_consumer['image'] = sleeping_image
                    # Sets the state of the consumer to sleeping
                    consumer_state.config(text="DORMIDO", bootstyle="danger")
                    # Sleeps the consumer for the time indicated by the time_to_sleep variable
                    t.sleep(self.time_to_sleep)

# Creates the producer and consumer objects
producer = Producer(0)
consumer = Consumer(0)

# Creates the producer and consumer threads
producing_thread = th.Thread(target=producer.produce)
consumering_thread = th.Thread(target=consumer.consume)

# Starts the producer and consumer threads
producing_thread.start()
consumering_thread.start()

# Creates the function that stops the threads when the window is closed
def on_key_release(event):
    if event.keysym == "Escape":
        window.quit()   
        window.destroy()
        stop_threads = True
   
# Command to check all the time the key pressed 
window.bind('<KeyRelease>',on_key_release)

# Intializes the window
window.mainloop()

# Joins the threads to make sure they stop when the window is closed
producing_thread.join()
consumering_thread.join()

