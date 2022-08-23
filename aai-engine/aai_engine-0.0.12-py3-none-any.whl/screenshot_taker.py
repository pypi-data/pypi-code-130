import pyautogui
import sys
import os
import time
import random
from random import choice
from string import digits

if sys.version_info[0] == 2:  # the tkinter library changed it's name from Python 2 to 3.
    import Tkinter
    tkinter = Tkinter #I decided to use a library reference to avoid potential naming conflicts with people's programs.
else:
    import tkinter
    from tkinter import ttk
from PIL import Image, ImageTk, ImageGrab
from PIL.PngImagePlugin import PngImageFile, PngInfo

LARGE_FONT = ("Courier", 12)
NORM_FONT = ("Courier", 10)
SMALL_FONT = ("Courier", 8)

REGION_PICK_VIEW = 0
OFFSET_PICK_VIEW = 1
SIMILARITY_PICK_VIEW = 2
NAME_PICK_VIEW = 3


script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "my_screenshot.png"
abs_file_path = os.path.join(script_dir, rel_path)
SCREENSHOT = abs_file_path

class ScreenShotTaker():
    """
    Class to manage screenshot selecting process,
    draws the screenshot on a canvas where a region is selected along with
    an offset and matching confidence.
    """
    def __init__(self, master, save_location, needle='', haystack=SCREENSHOT, editing=False, temp_screenshot_path='my_screenshot.png'):
        """
        Initialize values and prepare the region pick view
        """
        self.save_location = save_location
        self.needle = needle
        self.haystack = haystack
        self.editing = editing
        self.id = ''.join(choice(digits) for i in range(12))
        self.save_path = ''.join([save_location, "/img/aai_", self.id, ".png"])
        self.file_name = ''.join(['aai_', self.id])
        self.master = master
        self.master.title("AAI Image Extractor")
        
        if self.editing:
            self.init_canvas_screenshot(self.needle)
        else:
            self.init_canvas_screenshot(self.haystack)
    
        self.button = ttk.Button(master, text ="Confirm region", command = self.view_offset_picker, style='Accent.TButton')
        self.button.pack(side=tkinter.BOTTOM, pady=20)
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.x = self.y = 0

        if self.editing:
            self.view_offset_picker()
        else:
            self.confidence = 0.9
            self.view = REGION_PICK_VIEW

            self.offset_x = 0
            self.offset_y = 0

            self.canvas.bind("<ButtonPress-1>", self.on_button_press_rectangle)
            self.canvas.bind("<B1-Motion>", self.on_move_press)




    def view_offset_picker(self):
        """
        View to choose the offset to be used, 
        saved as offset to center of the selected region
        """
        self.view = OFFSET_PICK_VIEW
        self.canvas.delete(self.screenshot)
        self.button.configure(text = "Confirm offset!", command=lambda: self.view_confidence_picker())
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<ButtonPress-1>", self.on_button_press_offset)

        # cropping screenshot to selected region
        if not self.editing:
            ratio = self.original_im.size[0] / self.im.size[0]
            self.ratio = ratio
            x1, y1, x2, y2 = self.canvas.coords(self.rect)
            left = x1 * ratio
            top = y1 * ratio
            right = x2 * ratio
            bottom = y2 * ratio
            self.cropped = self.original_im.crop((left, top, right, bottom))
            self.cropped.save('my_cropped.png', 'PNG')
            self.tk_cropped = ImageTk.PhotoImage(self.cropped, master=self.master)
            w, h = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
            self.w = w
            self.h = h

            w = w / 4
            h = h / 4
            self.selected_region = self.canvas.create_image(w, h, image=self.tk_cropped)  

            # drawing default cross at center
            self.cross_h = self.canvas.create_line(w - 10, h, w + 10, h, fill='red')
            self.cross_v = self.canvas.create_line(w, h - 10, w, h + 10, fill='red')
            
            # center of img
            self.offset_x = self.w / 4 # was / 2
            self.offset_y = self.h / 4 # was / 2 (should a bug occur) 

            self.canvas.delete(self.rect)

        else:
            self.cropped = self.original_im
            self.cropped.save('my_cropped.png', 'PNG')
            self.tk_cropped = ImageTk.PhotoImage(self.im, master=self.master)
            w, h = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
            self.w = w
            self.h = h
            w = w / 4
            h = h / 4
            self.selected_region = self.canvas.create_image(w, h, image=self.tk_cropped)  

            # drawing default cross at center
            targetImage = PngImageFile(self.needle)
            print(targetImage.text)
            self.offset_x = w + float(targetImage.text["offset_x"])
            self.offset_y = h + float(targetImage.text["offset_y"])
            self.cross_h = self.canvas.create_line(w - 10, h, w + 10, h, fill='red')
            self.cross_v = self.canvas.create_line(w, h - 10, w, h + 10, fill='red')

            self.canvas.coords(self.cross_h, self.offset_x - 10, self.offset_y, self.offset_x + 10, self.offset_y)
            self.canvas.coords(self.cross_v, self.offset_x, self.offset_y - 10, self.offset_x, self.offset_y + 10)


            self.canvas.delete(self.rect)



    def view_confidence_picker(self):
        """ 
        View showing the confidence picker 
        """
        self.view = SIMILARITY_PICK_VIEW
        self.canvas.delete('all')
        for widget in self.master.winfo_children():
            widget.destroy()
        
        self.confidence = 0.9
        self.button = ttk.Button(self.master, text ="Confirm confidence", command = self.view_name_picker, style='Accent.TButton')
        self.button_check = ttk.Button(self.master, text ="Check", command = self.reset_confidence)
        # self.confidenceEntry = ttk.Entry(self.master)
        self.w2 = ttk.Scale(self.master, from_=0, to=100, orient=tkinter.HORIZONTAL, command = lambda val: (self.set_confidence(val)), length=200)

        if not self.editing:        
            self.w2.set(90)
        else:
            targetImage = PngImageFile(self.needle)
            self.w2.set(int(float(targetImage.text["confidence"]) * 100))
        # self.confidenceEntry.pack(side=tkinter.BOTTOM)
        self.button.pack(side=tkinter.BOTTOM, padx=20, pady=20)
        self.button_check.pack(side=tkinter.BOTTOM, padx=20, pady=20)
        self.w2.pack(side=tkinter.BOTTOM)
        self.init_canvas_screenshot(self.haystack)
        
        # imloc = pyautogui.locateAll('my_cropped.png', 'my_screenshot.png', confidence=0.9)
        # self.matches = []
        # for coords in imloc:
        #     left, top, width, height = coords
        #     left = left / self.ratio
        #     top = top / self.ratio
        #     width = width / self.ratio
        #     height = height / self.ratio
        #     match = self.canvas.create_rectangle(left, top, left + width, top + height, fill="", outline="red")
        #     self.matches.append(match)
        # print([x for x in imloc])

    def view_name_picker(self):
        """
        View showing the name picker
        """
        self.view = NAME_PICK_VIEW
        self.canvas.delete('all')
        for widget in self.master.winfo_children():
            widget.destroy()
        self.button = ttk.Button(self.master, text ="Confirm name", command = self.confirm_name, style='Accent.TButton')
        # self.textBox = tkinter.Text(self.master, height=1, width=30)
        self.textBox = ttk.Entry(self.master)
        self.textBox.insert(tkinter.END, self.file_name)
        self.button.pack(side=tkinter.BOTTOM, padx=20, pady=20)
        self.textBox.pack(side=tkinter.BOTTOM, pady=(20, 0))
        self.init_canvas_cropped()


    def init_canvas_screenshot(self, haystack):
        """ 
        Initialize the canvas to take remaining space on screen, filled with screenshot 
        """
        w, h = self.master.winfo_screenwidth() / 2, self.master.winfo_screenheight() / 2
        self.master.focus_set()    
        self.master.bind("<Return>", lambda e: (e.widget.withdraw(), e.widget.quit()))
        self.canvas = tkinter.Canvas(self.master, width=w, height=h, cursor="cross")
        self.canvas.pack()
        self.canvas.configure(background='black')
        print("Haystack: ", haystack)
        self.original_im = Image.open(haystack)
        self.im = Image.open(haystack)
        imgWidth, imgHeight = self.im.size
        imgWidth = imgWidth
        imgHeight = imgHeight
        if imgWidth > w or imgHeight > h:
            ratio = min(w/imgWidth, h/imgHeight)
            imgWidth = int(imgWidth*ratio)
            imgHeight = int(imgHeight*ratio)
            self.im = self.im.resize((imgWidth,imgHeight), Image.ANTIALIAS)

        self.wazil,self.lard=self.im.size
        self.canvas.config(scrollregion=(0,0,self.wazil,self.lard))
        self.tk_im = ImageTk.PhotoImage(self.im, master=self.master)
        print("Screenshot HAYSTACK", haystack)
        self.screenshot = self.canvas.create_image(w/2, h/2, image=self.tk_im)   


    def init_canvas_cropped(self):
        """ 
        Initialize the canvas to take remaining space on screen, filled with screenshot 
        """
        w, h = self.master.winfo_screenwidth() / 2, self.master.winfo_screenheight() / 2
        self.master.focus_set()    
        self.master.bind("<Return>", lambda e: (e.widget.withdraw(), e.widget.quit()))
        self.canvas = tkinter.Canvas(self.master, width=w, height=h, cursor="cross")
        self.canvas.pack()
        self.canvas.configure(background='black')
        self.original_im = Image.open("my_cropped.png")
        self.im = Image.open("my_cropped.png")
        imgWidth, imgHeight = self.im.size
        if imgWidth > w or imgHeight > h:
            ratio = min(w/imgWidth, h/imgHeight)
            imgWidth = int(imgWidth*ratio)
            imgHeight = int(imgHeight*ratio)
            self.im = self.im.resize((imgWidth,imgHeight), Image.ANTIALIAS)

        self.wazil,self.lard=self.im.size
        self.canvas.config(scrollregion=(0,0,self.wazil,self.lard))
        self.tk_im = ImageTk.PhotoImage(self.im, master=self.master)
        self.screenshot = self.canvas.create_image(w/2,h/2,image=self.tk_im)   

    def confirm_name(self):
        """
        Confirm the name and save the selected region to a png
        with the chosen confidence and offsets to the center as metadata

        This metadata can be retrieved through the text field of 
        PngImageFile("my_image_meta.png")
        """
        metadata = PngInfo()
        metadata.add_text("offset_x", str(self.offset_x - self.w/4))
        metadata.add_text("offset_y", str(self.offset_y - self.h/4))
        metadata.add_text("confidence", str(self.confidence))

        self.save_path = ''.join([self.save_location, '/', self.textBox.get().strip(), ".png"])

        print("Save path: ")
        print(self.save_path)

        self.cropped.save(self.save_path, pnginfo=metadata)
        targetImage = PngImageFile(self.save_path)
        print(targetImage.text)
        self.master.destroy()

    def set_confidence(self, val):
        """
        Sets the confidence when slider is moved and recalculates matching regions
        """
        self.confidence = float(val) / 100.0

    
    def reset_confidence(self):
        """ 
        Recalculates matching regions 
        """
        # self.confidence = float(self.confidence) / 100.0
        try:
            for match in self.matches:
                self.canvas.delete(match)
        except AttributeError:
            pass

        self.calculate_all_matches()
        print(self.confidence)


    def calculate_all_matches(self):
        """ 
        Calculates all the matching regions in the taken screenshot, displays these
        regions with red rectangles 
        """
        confidence_float = float(self.confidence) 
        imloc = pyautogui.locateAll('my_cropped.png', self.haystack, confidence=confidence_float)
        self.matches = []
        self.ratio = self.original_im.size[0] / self.im.size[0]
        for coords in imloc:
            left, top, width, height = coords
            left = left / self.ratio
            top = top / self.ratio
            width = width / self.ratio
            height = height / self.ratio
            match = self.canvas.create_rectangle(left, top, left + width, top + height, fill="", outline="red")
            self.matches.append(match)

    def on_button_press_rectangle(self, event):
        """ Starts a new rectangle """
        # save mouse drag start position
        self.start_x = event.x
        self.start_y = event.y

        # create rectangle if not yet exist
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, fill="", outline="red")


    def on_button_press_offset(self, event):
        """ Draws a cross at the clicked coordinates and saves the offsets """
        self.offset_x = event.x
        self.offset_y = event.y
        self.canvas.coords(self.cross_h, self.offset_x - 10, self.offset_y, self.offset_x + 10, self.offset_y)
        self.canvas.coords(self.cross_v, self.offset_x, self.offset_y - 10, self.offset_x, self.offset_y + 10)


    def on_move_press(self, event):
        """ Updates the rectangle to match the current selected region """
        curX, curY = (event.x, event.y)

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)   