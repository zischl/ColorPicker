import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import colorsys
from TimeIt import TimeIT
from numba import jit
import customtkinter

class TextPropertyManager(customtkinter.CTkEntry):
    def __init__(self, master, value, variable, root, **kwargs):
        super().__init__(master, width=60, placeholder_text=variable.get(), textvariable=variable, **kwargs)
        self.root = root
        self.variable = variable
        self.bind("<KeyRelease>", self.update_attribute)
        
        
    def update_attribute(self, event):
        val = self.get()
        self.root.change_col(val)
        self.variable.set(val)
        
class ColorPicker(tk.Toplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.size = 300
        self.center = self.size/2
        self.geometry(f"{self.size}x600+500+200")
        self.overrideredirect(True)
        self.pack_propagate(True)
        
        self.hue = tk.IntVar()
        self.r = tk.IntVar()
        self.g = tk.IntVar()
        self.b = tk.IntVar()
        self.saturation = tk.IntVar()
        self.lightness = tk.IntVar()
        self.value = tk.IntVar()
        self.hex_code = tk.StringVar()
        self.rgb = tk.StringVar()
        self.hsl = tk.StringVar()
        self.hsv = tk.StringVar()
        
        self.color_cycle = self.compute_color_cycle(1200)
        self.color_cycle = self.color_cycle.resize((300, 300), Image.LANCZOS)
        self.color_cycle_img = ImageTk.PhotoImage(self.color_cycle)

        self.gradient = self.compute_gradient(136, 0)
        self.gradient_img = ImageTk.PhotoImage(self.gradient)
        
        self.gradient_line = self.compute_h_line(50, 50)
        self.gradient_line_img = ImageTk.PhotoImage(self.gradient_line)
        
        self.colors_canvas = tk.Canvas(self, bg="#181818", highlightthickness=0, width=self.size, height=self.size)
        self.colors_canvas.pack(anchor='n', fill='x')
        
        self.canvas_color_cycle = self.colors_canvas.create_image(self.center, self.center, anchor=tk.CENTER, image=self.color_cycle_img)
        self.canvas_gradient = self.colors_canvas.create_image(self.center, self.center, anchor=tk.CENTER, image=self.gradient_img)
        self.canvas_gradient_line = self.colors_canvas.create_image(self.center, self.center, anchor=tk.CENTER, image=self.gradient_line_img)
        
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
        pixels = np.zeros((size, size, 4), dtype=np.uint8)

        for y in range(size):
            for x in range(size):
                dx, dy = x - center, y - center
                angle = np.arctan2(dy, dx)
                radius = np.sqrt(dx**2 + dy**2) / center

                if inner_radius <= radius <= outer_radius:
                    hue = (angle + np.pi) / (2 * np.pi)
                    r, g, b = self.hsv_to_rgb(hue, 1, 1)
                    pixels[y, x] = [int(r * 255), int(g * 255), int(b * 255), 255]

        return Image.fromarray(pixels, "RGBA")
    
    def compute_gradient(self, size, hue):
        # center = size // 2
        pixels = np.zeros((size, size, 4), dtype=np.uint8)
        hue = hue/360
        for y in range(size):
            for x in range(size):
                # dx, dy = x - center, y - center
                # angle = np.arctan2(dy, dx)
                # radius = np.sqrt(dx**2 + dy**2) / center
                
                # if 1 >= radius:
                    
                r, g, b = colorsys.hsv_to_rgb(hue, (x / (size - 1)), 1 - (y / (size - 1)))
                pixels[y, x] = [int(r * 255), int(g * 255), int(b * 255), 255]

        return Image.fromarray(pixels, "RGBA")
    
    def compute_h_line(self, width, length):
        pixels = np.zeros((width, length, 4), dtype=np.uint8)
        hue = hue/360
        for y in range(width):
            for x in range(length):
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
            
    def primary_col(self, event):
        col = self.color_cycle.getpixel([event.x,event.y])
        hsv = colorsys.rgb_to_hsv(*(col[:3]))
        if self.color_cycle:
            hue = int(hsv[0]*360)
            self.gradient = self.compute_gradient(136, hue)
            self.gradient_img.paste(self.gradient)
        self.r.set(col[0])
        self.g.set(col[1])
        self.b.set(col[2])
        self.hue.set(hsv[0]*360)
        self.saturation.set(hsv[1])
        self.value.set(hsv[2])
        self.hex_code.set(self.RGBA_Hex(col))
        # print(self.gradient.getpixel([134,0]))
        # print(event.x, event.y)
        
    def secondary_col(self, event):
        if event.x < 82 or event.y < 82 or event.x >= 218 or event.y >= 218: return
        col = self.gradient.getpixel([event.x-82,event.y-82])
        # print(col)
        hsv = colorsys.rgb_to_hsv(*(col[:3]))
        
        self.r.set(col[0])
        self.g.set(col[1])
        self.b.set(col[2])
        self.hue.set(hsv[0]*360)
        self.saturation.set(hsv[1])
        self.value.set(hsv[2])
        self.hex_code.set(self.RGBA_Hex(col))


    def RGBA_Hex(self, RGBA):
        return "".join(val for val in [hex(value).removeprefix("0x") for value in RGBA[:-1]])

    
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

    #     # Convert HSV to RGB (Vectorized)
    #     hsv_to_rgb = np.vectorize(colorsys.hsv_to_rgb)
    #     r, g, b = hsv_to_rgb(hue_normalized, sat, val)

    #     # Stack into image format
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
