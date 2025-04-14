import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import colorsys
from TimeIt import TimeIT
from numba import jit
import customtkinter
import math
from functools import cache

class Colors:
    __slots__ = ("master", "rgb", "hue", "s", "v", "hsv", "hex_code")
    def __init__(self, master):
        self.master = master
        self.rgb = (255, 0, 0)
        self._update_colors()

    def _update_colors(self):
        r, g, b = (x / 255.0 for x in self.rgb)
        self.hue, self.s, self.v = colorsys.rgb_to_hsv(r, g, b)
        self.hsv = (self.hue * 360, self.s * 100, self.v * 100)
        self.hex_code = '#{:02x}{:02x}{:02x}'.format(*map(int, self.rgb))
    
    def setHue(self, hue=None, rgb=None):
        if rgb is not None:
            normalized_rgb = tuple(val / 255.0 for val in rgb)
            hue, *_ = colorsys.rgb_to_hsv(*normalized_rgb)
            self.rgb = tuple(rgb)  
        elif hue is not None:
            self.rgb = tuple(int(val * 255) for val in colorsys.hsv_to_rgb(hue, self.s, self.v))
        self._update_colors()
           
        # self.h, self.l, self.s = colorsys.rgb_to_hls(r, g, b)
        # self.hsl = (round(self.hue * 360), round(self.s * 100), round(self.l * 100))
        
        
    # def set_rgb(self, r, g, b):
    #     self.rgb = (r, g, b)
    #     self.update_all_from_rgb()

    # def set_hex(self, hex_code):
    #     hex_code = hex_code.lstrip('#')
    #     self.rgb = tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
    #     self.update_all_from_rgb()
        
    

class TextPropertyManager(customtkinter.CTkEntry):
    def __init__(self, master, value, variable, root, **kwargs):
        super().__init__(master, width=60, placeholder_text=variable.get(), textvariable=variable, **kwargs)
        self.root = root
        self.variable = variable
        self.bind("<KeyRelease>", self.update_attribute)
        
        
    def update_attribute(self, event):
        val = int(self.get())
        self.root.setColorCycle(val)
        self.variable.set(val)
        
class ColorfulSliders():
    def compute_h_line(width, length):
        pixels = np.zeros((width, length, 4), dtype=np.uint8)
        for y in range(width):
            for x in range(length):
                if y < width/2 and x in range(0, 16-y): continue
                if y == width/2 and x in range(y): continue
                if y > width/2 and x in range(y): continue
                if y < width/2 and x in range(length-16+y, length): continue
                if y == width/2 and x in range(length-16, length): continue
                if y > width/2 and x in range(length, length-y, -1): continue
                hue = x / length
                r, g, b = colorsys.hsv_to_rgb(hue, 1, 1)
                pixels[y, x] = [int(r * 255), int(g * 255), int(b * 255), 255]

        return Image.fromarray(pixels, "RGBA")
    
    def compute_s_line(self, width, length, hue, s, v):
        s = s if s else (x / (length - 1))
        v = v if v else (y / (length - 1))
        # center = size // 2
        pixels = np.zeros((width, length, 4), dtype=np.uint8)
        hue = hue/360
        for y in range(width):
            for x in range(length):
                r, g, b = colorsys.hsv_to_rgb(hue, s, v)
                pixels[y, x] = [int(r * 255), int(g * 255), int(b * 255), 255]

        return Image.fromarray(pixels, "RGBA")
    
    def compute_v_line(self, width, length, hue):
        # center = size // 2
        pixels = np.zeros((width, length, 4), dtype=np.uint8)
        hue = hue/360
        for y in range(width):
            for x in range(length):
                r, g, b = colorsys.hsv_to_rgb(hue, 1, (x / (length - 1)))
                pixels[y, x] = [int(r * 255), int(g * 255), int(b * 255), 255]

        return Image.fromarray(pixels, "RGBA")
    
    def compute_RGB_line(self, width, length, hue):
        # center = size // 2
        pixels = np.zeros((width, length, 4), dtype=np.uint8)
        hue = hue/360
        for y in range(width):
            for x in range(length):
                r, g, b = colorsys.hsv_to_rgb(hue, 1, (x / (length - 1)))
                pixels[y, x] = [int(r * 255), int(g * 255), int(b * 255), 255]

        return Image.fromarray(pixels, "RGBA")

class TraceInt(tk.IntVar):
    def __init__(self, master = None, controller = None):
        super().__init__(master)
        self.trace_add('write', lambda *args :self.controller.set_rgb(r=self.r.get(), g=self.g.get(), b=self.b.get()))

class ColorPicker(tk.Toplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.size = 300
        self.center = self.size/2
        self.geometry(f"{self.size}x600+500+200")
        self.overrideredirect(True)
        self.pack_propagate(True)
        
        self.r = tk.IntVar(self)
        self.g = tk.IntVar(self)
        self.b = tk.IntVar(self)
        self.hue = tk.IntVar(self)
        self.saturation = tk.IntVar(self)
        self.lightness = tk.IntVar(self)
        self.value = tk.IntVar(self)
        self.hex_code = tk.StringVar(self)
        self.hsl = tk.StringVar(self)
        self.hsv = tk.StringVar(self)
        
        self.colors = Colors(self)
        
        # self.r.trace_add('write', lambda *args : self.colors.set_rgb(r=self.r.get(), g=self.g.get(), b=self.b.get()))
        # self.g.trace_add('write', lambda *args : self.colors.set_rgb(r=self.r.get(), g=self.g.get(), b=self.b.get()))
        # self.b.trace_add('write', lambda *args : self.colors.set_rgb(r=self.r.get(), g=self.g.get(), b=self.b.get()))
        # self.hex_code.trace_add('write', lambda *args : self.colors.set_hex(self.hex_code.get()))
        
        self.color_cycle = self.compute_color_cycle(1200)
        self.color_cycle = self.color_cycle.resize((300, 300), Image.LANCZOS)
        self.color_cycle_img = ImageTk.PhotoImage(self.color_cycle)

        self.gradient = self.compute_gradient(136)
        self.gradient_img = ImageTk.PhotoImage(self.gradient)
        
        self.gradient_line = ColorfulSliders.compute_h_line(16, 150)
        self.gradient_line_img = ImageTk.PhotoImage(self.gradient_line)
        
        self.colors_canvas = tk.Canvas(self, bg="#181818", highlightthickness=0, width=self.size, height=self.size)
        self.colors_canvas.pack(anchor='n', fill='x')
        
        self.canvas_color_cycle = self.colors_canvas.create_image(self.center, self.center, anchor=tk.CENTER, image=self.color_cycle_img)
        self.canvas_gradient = self.colors_canvas.create_image(self.center, self.center, anchor=tk.CENTER, image=self.gradient_img)
        self.canvas_gradient_line = self.colors_canvas.create_image(self.center, self.center, anchor=tk.CENTER, image=self.gradient_line_img)
        
        self.gradient_pointer = self.colors_canvas.create_oval(self.center-10, self.center-10, self.center+10, self.center+10, fill='white', outline='gray', width=2)
        self.color_cycle_pointer = self.colors_canvas.create_oval(0, 0, 20, 20, fill='white', outline='gray', width=2)
        
        self.colors_canvas.tag_bind(self.canvas_color_cycle ,"<Button-1>", self.primary_col)
        self.colors_canvas.tag_bind(self.canvas_color_cycle ,"<B1-Motion>", self.primary_col)
        self.colors_canvas.tag_bind(self.canvas_gradient ,"<Button-1>", self.secondary_col)
        self.colors_canvas.tag_bind(self.canvas_gradient ,"<B1-Motion>", self.secondary_col)
        
        
        self.attributes_frame = customtkinter.CTkFrame(self, height=200)
        self.attributes_frame.pack(fill='x')
        self.attributes_frame.grid_columnconfigure([0,1,2,3], weight=1)
        
        self.attribute_manager(self.attributes_frame, "R :", 0, [0,1], 10, self.r)
        self.attribute_manager(self.attributes_frame, "G :", 1, [0,1], 10, self.g)
        self.attribute_manager(self.attributes_frame, "B :", 2, [0,1], 10, self.b)
        self.attribute_manager(self.attributes_frame, "Hue :", 0, [2,3], 10, self.hue)
        self.attribute_manager(self.attributes_frame, "Saturation :", 1, [2,3], 10, self.saturation)
        self.attribute_manager(self.attributes_frame, "Value :", 2, [2,3], 10, self.value)
        self.attribute_manager(self.attributes_frame, "HSV :", 3, [0,1], 10, self.hsv)
        
        self.attribute_manager(self.attributes_frame, "HSL :", 4, [0,1], 10, self.hsl)
        self.attribute_manager(self.attributes_frame, "Hex :", 5, [0,1], 10, self.hex_code)
        
        self.setColorCycle()
        self.setGradient()
        
    def attribute_manager(self, master, text, row, column, pady, variable):
        customtkinter.CTkLabel(master, text=text).grid(row=row, column=column[0], pady=(pady, 0))
        TextPropertyManager(master, value=0, root=self, variable=variable).grid(row=row, column=column[1], pady=(pady, 0))
        
    
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
        # center = size // 2
        pixels = np.zeros((size, size, 4), dtype=np.uint8)
        for y in range(size):
            for x in range(size):
                # dx, dy = x - center, y - center
                # angle = np.arctan2(dy, dx)
                # radius = np.sqrt(dx**2 + dy**2) / center
                
                # if 1 >= radius:
                    
                r, g, b = colorsys.hsv_to_rgb(self.colors.hue, (x / (size - 1)), 1 - (y / (size - 1)))
                pixels[y, x] = [int(r * 255), int(g * 255), int(b * 255), 255]

        return Image.fromarray(pixels, "RGBA")
            
    def primary_col(self, event):
        dx, dy = event.x - self.center, event.y - self.center
        radius = math.sqrt(dx**2 + dy**2) / self.center
        
        c_pos = self.colors_canvas.coords(self.color_cycle_pointer)
        if 0.65 <= radius <= 0.8:
            self.colors_canvas.move(self.color_cycle_pointer, event.x-c_pos[0]-10 , event.y-c_pos[1]-10)

        elif radius > 0.8:
            self.colors_canvas.move(self.color_cycle_pointer, (dx*(0.79/radius))-c_pos[0]-10+self.center , (dy*(0.79/radius))-c_pos[1]-10+self.center)
            
        elif radius < 0.65:
            self.colors_canvas.move(self.color_cycle_pointer, (dx*(0.65/radius))-c_pos[0]-10+self.center , (dy*(0.65/radius))-c_pos[1]-10+self.center)    
        
        col = self.color_cycle.getpixel([c_pos[0]+10, c_pos[1]+10])
        self.colors.setHue(rgb = col[:3])
        self.update()
        self.gradient = self.compute_gradient(136)
        self.gradient_img.paste(self.gradient)
        
    def secondary_col(self, event):
        if event.x < 82 or event.y < 82 or event.x >= 218 or event.y >= 218: return
        c_pos = self.colors_canvas.coords(self.gradient_pointer)
        self.colors_canvas.move(self.gradient_pointer, event.x-c_pos[0]-10 , event.y-c_pos[1]-10)
        col = self.gradient.getpixel([event.x-82,event.y-82])
        
        

    def RGBA_Hex(self, RGBA):
        return "".join(val for val in [hex(value).removeprefix("0x") for value in RGBA[:-1]])
    
    def setColorCycle(self):
        hue = self.colors.hsv[0]/360
        angle = (hue * (math.pi - (-math.pi))) + (-math.pi)
        dx = 115 * math.cos(angle)
        dy = 115 * math.sin(angle)
        x = dx + self.center
        y = dy + self.center
        c_pos = self.colors_canvas.coords(self.color_cycle_pointer)
        self.colors_canvas.move(self.color_cycle_pointer, x-c_pos[0]-10 , y-c_pos[1]-10)
        
    def setGradient(self, size = 136):
        col = self.colors.hsv

        x, y = col[1]*(size-1), (1 - col[2])*(size - 1)
        c_pos = self.colors_canvas.coords(self.gradient_pointer)
        self.colors_canvas.move(self.gradient_pointer, x-c_pos[0]-10 +82 , y-c_pos[1]-10 +82)

        self.gradient = self.compute_gradient(136)
        self.gradient_img.paste(self.gradient)
        
    def update(self):
        self.r.set(self.colors.rgb[0])
        self.g.set(self.colors.rgb[1])
        self.b.set(self.colors.rgb[2])
        self.hue.set(self.colors.hue)
        # self.saturation.set(self.colors.hsl[1])
        # self.lightness.set(self.colors.hsl[2])
        # self.value.set(self.colors.hsv[2])
        self.hex_code.set(self.colors.hex_code)
        # self.hsl.set(f"{self.colors.hsl}")
        self.hsv.set(f"{self.colors.hsv}")
               
class Main(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup = ColorPicker(master=self, bg="#181818")
    
       
    # def compute_donut(self, size, hue):
    #     x = np.linspace(-1, 1, size)
    #     y = np.linspace(-1, 1, size)
    #     X, Y = np.meshgrid(x, y)

    #     # Convert to polar coordinates
    #     radius = np.sqrt(X**2 + Y**2) / (size/2)
    #     theta = np.arctan2(Y, X)
    #     mask = (radius >= 0.6)
    #     pixels = np.zeros((size, size, 4), dtype=np.uint8)
    #     # Convert to HSV (Hue: fixed, Saturation: varies with X, Value: varies with Y)
    #     hue_normalized = hue / 360.0
    #     sat = (X + 1) / 2  # Normalize from -1 to 1 -> 0 to 1
    #     val = (1 - Y) / 2  # Normalize from -1 to 1 -> 1 to 0

    #     hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)
    #     r, g, b = hsv_to_rgb(hue_normalized, sat, val)

    #     img_array = np.dstack([r * 255, g * 255, b * 255, np.full_like(r, 255)])  # RGBA
    #     return img_array.astype(np.uint8)

    def compute_circle(self, size, hue):
        # x = np.linspace(-1, 1, size)
        # y = np.linspace(-1, 1, size)
        # X, Y = np.meshgrid(x, y)

        # radius = np.sqrt(X**2 + Y**2)
        # mask = radius <= 1 

        # hue_normalized = hue / 360.0
        # sat = (X + 1) / (256/size)
        # val = (1 - Y) / (256/size)  

        # hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)
        # r, g, b = hsv_to_rgb(hue_normalized, sat, val)

    
        # img_array = np.dstack([r * 255, g * 255, b * 255, mask * 255]) 
        # return img_array.astype(np.uint8)
        center = size // 2
        pixels = np.zeros((size, size, 4), dtype=np.uint8)
        hue = hue/360
        for y in range(size):
            for x in range(size):
                dx, dy = x - center, y - center
                angle = np.arctan2(dy, dx)
                radius = np.sqrt(dx**2 + dy**2) / center
                
                # if 1 >= radius:
                    
                r, g, b = colorsys.hsv_to_rgb(hue, (x/size)*0.9, 1 - (y/size)*0.9)
                pixels[y, x] = [int(r * 255), int(g * 255), int(b * 255), 255]

        return pixels


    def open_popup(self):
        if self.popup:
            self.popup.destroy()  

        self.popup = tk.Toplevel(master=self.root)
        self.popup.title("Popup Window")
        self.popup['bg'] = 'grey'
        self.popup.attributes('-transparentcolor', 'black')
        self.popup.overrideredirect(True)
        
        self.gradient_image = self.generate_optimized_donut(1200)
        self.final_image = self.gradient_image.resize((300, 300), Image.LANCZOS)
        self.tk_image1 = ImageTk.PhotoImage(self.final_image)

        img = Image.fromarray(self.compute_circle(135, 266), "RGBA")
        self.tk_image = ImageTk.PhotoImage(img)

        self.canvas = tk.Canvas(self.popup, width=self.size, height=self.size, bg="#181818", highlightthickness=0)
        self.canvas.pack()
        self.canvas_img = self.canvas.create_image(300/2, 300/2, anchor=tk.CENTER, image=self.tk_image)
        self.canvas_img1 = self.canvas.create_image(300/2, 300/2, anchor=tk.CENTER, image=self.tk_image1)
        
        self.canvas.tag_bind(self.canvas_img1 ,"<Button-1>", self.add_custom_col)
        self.canvas.tag_bind(self.canvas_img1 ,"<B1-Motion>", self.add_custom_col)
        
        customtkinter.CTkLabel(self.popup, text="Hue").pack(side="top")
        TextPropertyManager(self.popup, value=0, root=self).pack(side="left")
        
    
            
app = Main()
app.mainloop()
