from rtdicomtools import *
import customtkinter as ctk
import tkinter as tk

class Explorer(ctk.CTk):
    
    def __init__(self):
        
        super().__init__(fg_color="#FFFFFF")
        
        self.appname = "Explorer" 
        self.author = "Sebastian Schäfer"
        self.version = "0.1"
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("dark-blue")
        
        self.title(f"{self.appname} v{self.version} by {self.author}")
        
        self.geometry("800x600")
        self.minsize(800, 600)

        self.mainframe = ctk.CTkFrame(self)
        self.menu = self.Menu(self)
        
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.rowconfigure(1, weight=0)
        self.mainframe.columnconfigure(0, weight=1)
        
        self.viewframe = ctk.CTkFrame(self.mainframe)
        self.progressbar = self.ProgressBar(self.mainframe)
        
        self.viewframe.grid(row=0, column=0, sticky="nsew")
        self.progressbar.grid(row=1, column=0, sticky="nsew")
        
        self.mainframe.pack(fill="both", expand=True, padx= 15)
        
    class ProgressBar(ctk.CTkFrame):
        
        def __init__(self, master):
            
            super().__init__(master)
            
            self.progressbar = ctk.CTkProgressBar(self, orientation="horizontal", mode="indeterminate",fg_color="#FFFFFF", height = 15, corner_radius=0)
            self.progressbar.start()
            self.progressbar.pack(fill="x", expand=True)
            
        def set(self, value):
            self.progressbar.set(value)
            
        def get(self):
            return self.progressbar.get()
        
    class Menu(tk.Menu):
        
        def __init__(self, master):
            
            self.parent = master
            super().__init__(self.parent, tearoff=0, relief="flat", font=("Segoe UI", 10))
            
            self.filemenu = tk.Menu(self, tearoff=0)
            self.add_cascade(label="File", menu=self.filemenu)
            
            self.parent.config(menu=self)
            
            
app = Explorer()
app.mainloop()