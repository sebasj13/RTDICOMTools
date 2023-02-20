import os
import cv2
import numpy as np
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk

class NumpyViewer3D(ctk.CTk):
    """A 3D viewer for numpy arrays.
    """

    def __init__(self, array: np.ndarray) -> None:
        
        super().__init__(fg_color="black")
        
        self.apptitle = ("3D Numpy Viewer")
        self.author = "Sebastian Schäfer"
        self.version = "1.0"
        self.title(f"{self.apptitle} v{self.version} by {self.author}")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.geometry("800x600")
        self.minsize(800, 600)
        
        self.image_data = array
        self.dimensions = self.image_data.shape        
        self.X = array
        self.dimensions = self.X.shape
        
        self.Y = np.rot90(self.X, k=1, axes=(1, 0))
        self.Z = np.rot90(self.Y, k=1, axes=(0, 2))
        self.Z = np.rot90(self.Z, k=-1, axes=(1, 2))

        self.index = 0
        self.xindex = 0
        self.yindex = 0
        self.zindex = 0
        
        self.axis = 0

        self.tabview = ctk.CTkTabview(self)
        self.tabview.add("Single")
        self.tabview.add("Triple")

        self.single_frame = ctk.CTkFrame(self.tabview.tab("Single"), bg_color="black")
        self.triple_frame = self.TripleFrame(self.tabview.tab("Triple"))

        self.controlframe = self.ControlFrame(self.single_frame)
        self.viewframe = self.ViewFrame(self.single_frame)

        self.single_frame.columnconfigure(0, weight=1)
        self.single_frame.rowconfigure(0, weight=1)
        self.single_frame.rowconfigure(1, weight=0)

        self.viewframe.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.controlframe.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.single_frame.pack(fill=tk.BOTH, expand=True)
        self.triple_frame.pack(fill=tk.BOTH, expand=True)

        self.tabview.pack(fill=tk.BOTH, expand=True)
        self.single_frame.bind("<Configure>", lambda x : self.viewframe.update_image())

        self.mainloop()
        
    class ControlFrame(ctk.CTkFrame):
        """The control frame of the application.
        """
            
        def __init__(self, parent) -> None:
            super().__init__(master = parent, bg_color="black")

            self.parent = parent.master.master.master

            self.index_slider = ctk.CTkSlider(self, from_=0, to= self.parent.dimensions[0]-1, number_of_steps = self.parent.dimensions[0], orientation=tk.HORIZONTAL, width=300, height=10, command = self.update_index_label)
            self.index_slider.set(0)
            self.slider_label = ctk.CTkLabel(self, text=f"Index: {int(self.index_slider.get())}", font=("Arial", 20), text_color="white")

            self.AxisLabel = ctk.CTkLabel(self, text="Axis:", font=("Arial", 20), text_color="white")
            self.Axis = tk.IntVar(value=0)
            self.XAxis = ctk.CTkRadioButton(self, text="X", variable=self.Axis, value=0, font=("Arial", 20), text_color="white", command = self.change_axis)
            self.YAxis = ctk.CTkRadioButton(self, text="Y", variable=self.Axis, value=1, font=("Arial", 20), text_color="white", command = self.change_axis)
            self.ZAxis = ctk.CTkRadioButton(self, text="Z", variable=self.Axis, value=2, font=("Arial", 20), text_color="white", command = self.change_axis)

            self.columnconfigure(0, weight=1)
            self.columnconfigure(2, weight=1)
            self.rowconfigure(0, weight=0)

            self.index_slider.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            self.slider_label.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
            self.AxisLabel.grid(row=0, column=3, sticky="nsew", padx=5, pady=5)
            
            self.XAxis.grid(row=0, column=4, sticky="W", padx=5, pady=5)
            self.YAxis.grid(row=0, column=5, sticky="W", padx=5, pady=5)
            self.ZAxis.grid(row=0, column=6, sticky="W", padx=5, pady=5)

        def update_index_label(self, value):
            self.slider_label.configure(text=f"Index: {int(value)}")
            setattr(self.parent, {0: "xindex", 1: "yindex", 2: "zindex"}[self.parent.axis], int(value))
            setattr(self.parent, "index", {0: self.parent.xindex, 1: self.parent.yindex, 2: self.parent.zindex}[self.parent.axis])
            self.parent.viewframe.update_image()

        def change_axis(self):
            self.parent.axis = self.Axis.get()
            setattr(self.parent, "index", {0: self.parent.xindex, 1: self.parent.yindex, 2: self.parent.zindex}[self.parent.axis])
            self.parent.image_data = {0: self.parent.X, 1: self.parent.Y, 2: self.parent.Z}[self.parent.axis]
            self.parent.dimensions = self.parent.image_data.shape
            self.index_slider.configure(to=self.parent.dimensions[0]-1, number_of_steps=self.parent.dimensions[0])
            self.index_slider.set({0: self.parent.xindex, 1: self.parent.yindex, 2: self.parent.zindex}[self.parent.axis]+1)
            self.slider_label.configure(text=f"Index: {int(self.index_slider.get())}")            
            self.parent.viewframe.update_image()

        def scroll(self, event):
            self.index_slider.set(self.index_slider.get() + event.delta/120)
            self.update_index_label(self.index_slider.get())


    class ViewFrame(ctk.CTkFrame):
        """The view frame of the application.
        """

        def __init__(self, parent) -> None:
            super().__init__(master = parent, bg_color="black")

            self.parent = parent.master.master.master

            self.columnconfigure(0, weight=1)
            self.rowconfigure(0, weight=1)

            self.image = self.array_to_image(self.parent.image_data, self.parent.index)
            self.label = tk.Label(self, bg="black", image = self.image)
            self.label.image = self.image
            self.update_image()

            self.label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

            self.label.bind("<Enter>", self.on_enter)
            self.label.bind("<Leave>", self.on_leave)

        def on_enter(self, event):                
            self.parent.bind("<MouseWheel>", self.parent.controlframe.scroll)
        def on_leave(self, event):        
            self.parent.unbind("<MouseWheel>")

        def array_to_image(self, array: np.ndarray, slice: int) -> ctk.CTkImage:
            """Converts a numpy array to an image.
            

            Args:
                array (np.ndarray): The array to convert.
                slice (int): The slice to take.

            Returns:
                ctk.CTkImage: The image.
            """
   
            image = array[slice,:,:] 
   
            image = Image.fromarray(image)
            size = min([self.winfo_width(), self.winfo_height()])
            image = image.resize((size, size), Image.LANCZOS)

            return ImageTk.PhotoImage(image)
            

        def update_image(self):
            """Updates the image.
            """

            self.image = self.array_to_image(self.parent.image_data, self.parent.index)
            self.label.config(image = self.image)
            self.label.image = self.image

    class TripleFrame(ctk.CTkFrame):
        """Shows the three different views of the array side by side.
        """

        def __init__(self, parent) -> None:
            super().__init__(master = parent, bg_color="black")

            self.parent = parent
            self.pack_propagate(False)

            self.xview = self.ViewFrame(self, 0)
            self.yview = self.ViewFrame(self, 1)
            self.zview = self.ViewFrame(self, 2)

            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=1)
            self.columnconfigure(2, weight=1)
            self.rowconfigure(0, weight=1)

            self.xview.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            self.yview.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
            self.zview.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        class ViewFrame(ctk.CTkFrame):
            """A view frame for one of the views.
            """

            def __init__(self, parent, axis) -> None:
                super().__init__(master = parent, bg_color="black")
                self.parent = parent.master.master.master
                self.master = parent
                self.pack_propagate(False)          
                self.axis = axis
                #self.index = getattr(self.parent, {0: "xindex", 1: "yindex", 2: "zindex"}[axis])
                self.ref_dimension = getattr(self.parent, "dimensions")[axis]
                self.ref_image_data = getattr(self.parent, {0: "X", 1: "Y", 2: "Z"}[axis])
                self.index = self.ref_image_data.shape[0]//2

                self.title = ctk.CTkLabel(self, text=f"{['X', 'Y', 'Z'][axis]} view", font=("Arial", 20), text_color="white")
                self.title.pack(side="top", fill="x", expand=False, padx=5, pady=5)
                self.index_slider = ctk.CTkSlider(self, from_=0, to= self.ref_dimension-1, number_of_steps = self.ref_dimension, orientation=tk.HORIZONTAL, width=200, height=10, command = self.update_index_label)
                self.index_slider.set(self.index)
                self.slider_label = ctk.CTkLabel(self, text=f"Index: {int(self.index_slider.get())}", font=("Arial", 20), text_color="white")
                self.index_slider.pack(side="top", fill="x", expand=False, padx=5, pady=5)
                self.slider_label.pack(side="top", fill="x", expand=False, padx=5, pady=5)

                self.label = tk.Label(self, bg="black")
                self.label.pack(side="top", fill="both", expand=True, padx=5, pady=5)
                self.image = self.array_to_image(self.ref_image_data, self.index)
                self.label.config(image=self.image)
                self.label.image = self.image
                self.label.bind("<Enter>", self.on_enter)
                self.label.bind("<Leave>", self.on_leave)
                self.bind("<Configure>", lambda x: self.update_image())
                self.update_image()

            def on_enter(self, event): 
                self.parent.bind("<MouseWheel>", self.scroll)
            def on_leave(self, event):      
                self.parent.unbind("<MouseWheel>")

            def array_to_image(self, array: np.ndarray, slice: int, line_index=None, line_direction=None) -> ctk.CTkImage:
                """Converts a numpy array to an image.
                

                Args:
                    array (np.ndarray): The array to convert.
                    slice (int): The slice to take.

                Returns:
                    ctk.CTkImage: The image.
                """
    
                image = array[slice,:,:].copy()

                if line_index is not None:
                    if self.axis == 0 and line_direction =="x":
                        line_index = image.shape[1] - line_index
                    if self.axis == 1:
                        if line_direction =="x":
                            line_index = image.shape[1] - line_index
                        if line_direction =="y":
                            line_index = image.shape[0] - line_index
                    
                    if line_direction == "x":
                        cv2.line(image, (line_index, 0), (line_index, image.shape[0]), (255, 0, 0), 1)
                    elif line_direction == "y":
                        cv2.line(image, (0, line_index), (image.shape[1], line_index), (255, 0, 0), 1)

                image = Image.fromarray(image)
                size = min([self.label.winfo_height(), self.winfo_width()])
                image = image.resize((size,size), Image.LANCZOS)

                return ImageTk.PhotoImage(image)
                
            def update_image(self, line_index=None, line_direction=None):
                """Updates the image.
                """

                self.image = self.array_to_image(self.ref_image_data, self.index,  line_index=line_index, line_direction=line_direction,)
                self.label.config(image = self.image)
                self.label.image = self.image

            def update_index_label(self, value):
                    
                self.slider_label.configure(text=f"Index: {int(value)}")
                self.index = int(value)
                setattr(self.parent, {0: "xindex", 1: "yindex", 2: "zindex"}[self.axis], self.index+1)
                getattr(self.master, {0: "yview", 1: "zview", 2: "xview"}[self.axis]).update_image(self.index, {0: "y", 1: "y", 2: "x"}[self.axis])
                getattr(self.master, {0: "zview", 1: "xview", 2: "yview"}[self.axis]).update_image(self.index, {0: "x", 1: "y", 2: "x"}[self.axis])
                self.update_image()

            def scroll(self, event):
                self.index_slider.set(self.index_slider.get() + event.delta/120)
                self.update_index_label(self.index_slider.get())