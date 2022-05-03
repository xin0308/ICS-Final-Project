from tkinter import *
class HelloWorld:
   """
   A Hello World App.
   """
   def __init__(self, parent):
     self.label1 = Label(parent, text="Hello World1")
     self.label2 = Button(parent, text="Hello World2")
     self.label1.grid(column=0, row=0)
     self.label2.grid(column=0, row=1)
# create the root window
root = Tk()
# create the application
app = HelloWorld(root)
# enter the main loop
root.mainloop()
