import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import colorsys
from TimeIt import TimeIT, TimeITAvg, Chronos
from numba import jit
import customtkinter
import math
from functools import cache
from ChromaTk import *
import cv2
import SSC
from CustomTitleBar import TitleBar

class ChromaQuest(tk.Toplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.size = 300
        self.center = self.size/2
        self.geometry("350x650+500+200")
        self.overrideredirect(True)
        self.pack_propagate(True)
        
        self.titleBar = TitleBar(self, self.winfo_reqwidth())
        self.titleBar.pack(fill='x')
        
        self.r = tk.IntVar(self)
        self.g = tk.IntVar(self)
        self.b = tk.IntVar(self)
        self.hue = tk.IntVar(self)
        self.saturationv = tk.IntVar(self)
        self.saturationl = tk.IntVar(self)
        self.lightness = tk.IntVar(self)
        self.value = tk.IntVar(self)
        self.hex_code = tk.StringVar(self)
        self.hsl = tk.StringVar(self)
        self.hsv = tk.StringVar(self)
        
        self.action = None
        self.colors = chroma(self, (1.0 , 0, 0))
         
        try:
            with open("data.bin", "rb") as cache:
                image = cache.read()
                self.color_cycle = Image.frombytes("RGBA", (300,300), image)
        except IOError:
            self.color_cycle = self.compute_color_cycle(1200)
            self.color_cycle = self.color_cycle.resize((300, 300), Image.LANCZOS)
            
            with open("data.bin", "wb") as cache:
                cache.write(self.color_cycle.tobytes())

        customtkinter.CTkLabel(self, text="ChromaQuest", font=('', 24, 'bold'), text_color='white').pack(pady=(10,0))
        
        self.color_cycle_img = ImageTk.PhotoImage(self.color_cycle)

        self.gradient = self.compute_gradient(136)
        self.gradient_img = ImageTk.PhotoImage(self.gradient)
        
        self.colors_canvas = tk.Canvas(self, bg="#181818", highlightthickness=0, width=self.size, height=self.size)
        self.colors_canvas.pack(anchor='n')
        
        self.canvas_color_cycle = self.colors_canvas.create_image(self.center, self.center, anchor=tk.CENTER, image=self.color_cycle_img)
        self.canvas_gradient = self.colors_canvas.create_image(self.center, self.center, anchor=tk.CENTER, image=self.gradient_img)
        
        self.pointerImage = Image.new("RGBA", (60, 60), (255, 255, 255, 0))
        draw = ImageDraw.Draw(self.pointerImage)
        draw.ellipse((0, 0, 59, 59), outline="white", width=10)
        self.graidentPointerImg = ImageTk.PhotoImage(self.pointerImage.resize((12,12), Image.LANCZOS))
        self.colcylPointerImg = ImageTk.PhotoImage(self.pointerImage.resize((16,16), Image.LANCZOS))

        self.gradient_pointer = self.colors_canvas.create_image(self.center, self.center, image=self.graidentPointerImg, anchor=tk.CENTER)
        self.color_cycle_pointer = self.colors_canvas.create_image(0, 0, image=self.colcylPointerImg, anchor=tk.CENTER)
        
        self.colors_canvas.tag_bind(self.canvas_color_cycle ,"<Button-1>", self.primary_col)
        self.colors_canvas.tag_bind(self.canvas_color_cycle ,"<B1-Motion>", self.primary_col)
        self.colors_canvas.tag_bind(self.canvas_gradient ,"<Button-1>", self.secondary_col)
        self.colors_canvas.tag_bind(self.canvas_gradient ,"<B1-Motion>", self.secondary_col)
        
        self.attributes_frame = SSC.FrameLord(self, height=100, bg='#181818')
        self.attributes_frame.add('RGB')
        self.attributes_frame.add('HSV')
        self.attributes_frame.add('HSL')
        
        self.typeSelect = SSC.SSC(self, items=['RGB', 'HSV', 'HSL'], height=30, width=250, bg="#181818", 
                                  command=self.attributes_frame.switch, font=('', 10, 'bold'))
        self.typeSelect.pack()
        self.attributes_frame.pack(fill='x')
        
        self.hexEntry = CopyOutField(self, textvariable=self.hex_code, fg_color='#181818', font=('', 14), border_width=0, width=105)
        self.hexEntry.pack()
        
        self.history = ChromaPalette(self, 2, 7, height=150, bg='#1c1c1c', highlightthickness=0, colorVar=self.hex_code)
        self.history.pack(fill='x')
        
        
        self.attribute_manager(self.attributes_frame.RGB, "R :", 0, self.r, (0, 255), RGBSlider, 'r', width=45, height=12, justify='right')
        self.attribute_manager(self.attributes_frame.RGB, "G :", 1, self.g, (0, 255), RGBSlider, 'g', width=45, height=12, justify='right')
        self.attribute_manager(self.attributes_frame.RGB, "B :", 2, self.b, (0, 255), RGBSlider, 'b', width=45, height=12, justify='right')

        self.attribute_manager(self.attributes_frame.HSV, "H :", 0, self.hue, (0, 360), HSVSlider, 'hue', width=45, height=12, justify='right')
        self.attribute_manager(self.attributes_frame.HSV, "S :", 1, self.saturationv, (0, 100), HSVSlider, 's', width=45, height=12, justify='right')
        self.attribute_manager(self.attributes_frame.HSV, "V :", 2, self.value, (0, 100), HSVSlider, 'v', width=45, height=12, justify='right')

        self.attribute_manager(self.attributes_frame.HSL, "H :", 0, self.hue, (0, 360), HSLSlider, 'hue', width=45, height=12, justify='right')
        self.attribute_manager(self.attributes_frame.HSL, "S :", 1, self.saturationl, (0, 100), HSLSlider, 'sl', width=45, height=12, justify='right')
        self.attribute_manager(self.attributes_frame.HSL, "L :", 2, self.lightness, (0, 100), HSLSlider, 'l', width=45, height=12, justify='right')

        # self.attribute_manager(self.attributes_frame, "HSV :", 3, [0,1], 10, self.hsv)
        
        # self.attribute_manager(self.attributes_frame, "HSL :", 4, [0,1], 10, self.hsl)
        # self.attribute_manager(self.attributes_frame, "Hex :", 5, [0,1], 10, self.hex_code)
        
        self.r.trace_add('write', lambda *args : self.entryCallback("RGB"))
        self.g.trace_add('write', lambda *args : self.entryCallback("RGB"))
        self.b.trace_add('write', lambda *args : self.entryCallback("RGB"))
        self.hue.trace_add('write', lambda *args : self.entryCallback("HSV"))
        self.saturationv.trace_add('write', lambda *args : self.entryCallback("HSV"))
        self.saturationl.trace_add('write', lambda *args : self.entryCallback("HSL"))
        self.lightness.trace_add('write', lambda *args : self.entryCallback("HSL"))
        self.value.trace_add('write', lambda *args : self.entryCallback("HSV"))
        self.hex_code.trace_add('write', lambda *args : self.entryCallback("Hex"))
        
        self.setColorCycle()
        self.setGradient()
        self.update()
        
    def attribute_manager(self, master, text, row, variable, limit, slider_class, mode, **kwargs):
        master.grid_columnconfigure([0,2], weight=1)
        master.grid_columnconfigure(1, weight=5)
        master.grid_rowconfigure(row, weight=1)
        customtkinter.CTkLabel(master, text=text).grid(row=row, column=0, padx=(10, 5), pady=5, sticky='w')
        slider = slider_class(master, mode=mode, bg='#181818', length=250, variable=variable, colorMgr=self.colors, limit=limit, height=12)
        slider.grid(row=row, column=1, padx=0, sticky='we')

        spinbox = ChromaSpinBox(master, variable=variable, limit=limit, disableSteppers=True, bg='#181818', **kwargs)
        spinbox.grid(row=row, column=2, padx=(5, 10), sticky='e')
    
    def hsv_to_rgb(self, h, s, v):
        i = int(h * 6.0) 
        f = (h * 6.0) - i  
        p = v * (1.0 - s)
        q = v * (1.0 - f * s)
        t = v * (1.0 - (1.0 - f) * s)
        i = i % 6

        if i == 0: return v, t, p
        if i == 1: return q, v, p
        if i == 2: return p, v, t
        if i == 3: return p, q, v
        if i == 4: return t, p, v
        return v, p, q  # i == 5

    def compute_color_cycle(self, size, inner_radius=0.65, outer_radius=0.8):
        center = size // 2
        self.pixels = np.zeros((size, size, 4), dtype=np.uint8)
        for y in range(size):
            for x in range(size):
                dx, dy = x - center, y - center
                angle = np.arctan2(dy, dx)
                radius = np.sqrt(dx**2 + dy**2) / center

                if inner_radius <= radius <= outer_radius:
                    hue = (angle + np.pi) / (2 * np.pi)
                    r, g, b = self.hsv_to_rgb(hue, 1, 1)
                    self.pixels[y, x] = [int(r * 255), int(g * 255), int(b * 255), 255]
        return Image.fromarray(self.pixels, "RGBA")
    
    def compute_gradient(self, size):
        pixels = np.zeros((size, size, 3), dtype=np.uint8)
        lineS = np.linspace(0, 255, size)
        lineV = np.linspace(255, 0, size)

        pixels[:, :, 0] = self.colors.hue * 179
        pixels[:, :, 1] = lineS
        pixels[:, :, 2] = lineV[:, np.newaxis]

        pixels = cv2.cvtColor(pixels, cv2.COLOR_HSV2RGB)

        return Image.fromarray(pixels, "RGB")
    
    
    def primary_col(self, event):
        dx, dy = event.x - self.center, event.y - self.center
        radius = math.sqrt(dx**2 + dy**2) / self.center
        
        c_pos = self.colors_canvas.coords(self.color_cycle_pointer)
        if 0.65 <= radius <= 0.8:
            self.colors_canvas.move(self.color_cycle_pointer, event.x-c_pos[0] , event.y-c_pos[1])

        elif radius > 0.8:
            self.colors_canvas.move(self.color_cycle_pointer, (dx*(0.79/radius))-c_pos[0]+self.center , (dy*(0.79/radius))-c_pos[1]+self.center)
            
        elif radius < 0.65:
            self.colors_canvas.move(self.color_cycle_pointer, (dx*(0.65/radius))-c_pos[0]+self.center , (dy*(0.65/radius))-c_pos[1]+self.center)    
        
        c_pos = self.colors_canvas.coords(self.color_cycle_pointer)
        col = self.color_cycle.getpixel([c_pos[0], c_pos[1]])
        self.colors.setHue(rgb = col[:3])
        self.update()
        self.gradient = self.compute_gradient(136)
        self.gradient_img.paste(self.gradient)
    
    def secondary_col(self, event):
        if event.x < 82 or event.y < 82 or event.x >= 218 or event.y >= 218: return
        c_pos = self.colors_canvas.coords(self.gradient_pointer)
        self.colors_canvas.move(self.gradient_pointer, event.x-c_pos[0] , event.y-c_pos[1])
        
        col = self.gradient.getpixel([event.x-82,event.y-82])
        self.colors.setRGB(*col[:3])
        self.update()
        
    def RGBA_Hex(self, RGBA):
        return "".join(val for val in [hex(value).removeprefix("0x") for value in RGBA[:-1]])
    
    def setColorCycle(self):
        angle = (self.colors.hue * (math.pi - (-math.pi))) + (-math.pi)
        dx = 115 * math.cos(angle)
        dy = 115 * math.sin(angle)
        x = dx + self.center
        y = dy + self.center
        c_pos = self.colors_canvas.coords(self.color_cycle_pointer)
        self.colors_canvas.move(self.color_cycle_pointer, x-c_pos[0] , y-c_pos[1])
    
    def setGradient(self, size = 136):
        x, y = self.colors.s * (size-1), (1 - self.colors.v)*(size - 1)
        c_pos = self.colors_canvas.coords(self.gradient_pointer)
        self.colors_canvas.move(self.gradient_pointer, x-c_pos[0] +82 , y-c_pos[1] +82)

        self.gradient = self.compute_gradient(136)
        self.gradient_img.paste(self.gradient)
    
    def update(self):
        self.action = "click"
        
        self.r.set(self.colors.r)
        self.g.set(self.colors.g)
        self.b.set(self.colors.b)
        
        self.hsv.set(f"{self.colors.hsv}")
        self.hue.set(self.colors.hsv[0])
        self.saturationv.set(self.colors.hsv[1])
        self.value.set(self.colors.hsv[2])
        self.lightness.set(self.colors.hsl[2])
        
        self.hex_code.set(self.colors.hex_code)
        # self.hsl.set(f"{self.colors.hsl}")
        
        self.action = None
        
    def setPointers(self):
        self.setColorCycle()
        self.setGradient()
    
    def entryCallback(self, caller):
        if not self.action:
            match caller:
                case "RGB":
                    self.colors.setRGB(self.r.get(), self.g.get(), self.b.get())
                    
                case "HSV":
                    self.colors.setHSV(hue=self.hue.get(), s=self.saturationv.get(), v=self.value.get())

                case "HSL":
                    self.colors.setHLS(hue=self.hue.get(), s=self.saturationl.get(), l=self.lightness.get())
                
                case "Hex":
                    self.colors.setHex(self.hex_code.get())
                    
            self.update()
            self.setColorCycle()
            self.setGradient()      
                    
                    
               
class Main(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        button = tk.Button(self, command=self.click, text='open')
        button.pack()
        
    
    def click(self):
        self.popup = ChromaQuest(master=self, bg="#181818")

        

        
    
            
app = Main()

app.mainloop()
