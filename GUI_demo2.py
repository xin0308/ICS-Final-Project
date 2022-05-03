from tkinter import *
class HelloWorld:
   """
   A Hello World App.
   """
   def __init__(self, parent):
     self.hello_button = Button(parent, text="Hello",command=self.say_hi)
     self.hello_button.grid(column=0, row=0)
     self.quit_button = Button(parent, text="Quit", fg="red",command=parent.destroy)
     self.quit_button.grid(column=1, row=0)
   def say_hi(self):
     print("hi there")
root = Tk()
app = HelloWorld(root)
root.mainloop()
