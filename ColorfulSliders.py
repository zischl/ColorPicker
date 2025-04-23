import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import colorsys

class RGBSlider(tk.Canvas):
    sliders = {}
    
    def __init__(self, master, color=(0, 0, 0), mode='r', length=300, height=20, limit=(0,255), pointerSize=6, **kwargs):
        super().__init__(master, width=length, height=height, bg='black', highlightthickness=0, **kwargs)
        RGBSlider.color = color
        self.mode = mode
        self.length = length
        self.height = height
        self.limit = limit
        self.pointerSize = pointerSize
        RGBSlider.sliders[mode] = self
        
        self.photo = ImageTk.PhotoImage(self._computeGradient()) 
        self.create_image(0, 0, anchor='nw', image=self.photo)
        self.pointer = self.create_oval(0, 0, 0, 0, fill='white', outline='gray', width=2)

        self.value = color[0] if mode=='r' else color[1] if mode=='g' else color[2]
        self.bind('<B1-Motion>', self.update)
        self.bind('<Button-1>', self.update)

        self.setColor()

    def _computeGradient(self):
        length = self.length
        height = self.height
        pixels = np.zeros((height, length, 4), dtype=np.uint8)
        
        match self.mode:
            case 'r':
                g,b = RGBSlider.color[1:3]
                for y in range(height):
                    for x in range(length):
                        r = x/length
                        pixels[y, x] = [int(r * 255), g, b, 255]
            case 'g':
                r,b = RGBSlider.color[0], RGBSlider.color[2]
                for y in range(height):
                    for x in range(length):
                        g = x/length
                        pixels[y, x] = [r, int(g * 255), b, 255]  
            case 'b':
                r,g = RGBSlider.color[0:2]
                for y in range(height):
                    for x in range(length):
                        b = x/length
                        pixels[y, x] = [r, g, int(b * 255), 255] 
        return Image.fromarray(pixels, "RGBA")

    def setColor(self, color=False):
        RGBSlider.color = color if color else RGBSlider.color
        self.image = self._computeGradient()
        self.photo.paste(self.image)

        x = int(self.value / 255 * (self.length - 1))
        y = self.height // 2
        self.coords(self.pointer, x - self.pointerSize, y - self.pointerSize, x + self.pointerSize, y + self.pointerSize)

    def update(self, event):
        x = event.x
        value = int(x / self.length * 255)
        if not self.limit[0] <= value <= self.limit[1]: return
        y = self.height // 2
        self.coords(self.pointer, x - self.pointerSize, y - self.pointerSize, x + self.pointerSize, y + self.pointerSize)
        
        
        match self.mode:
            case 'r':
                RGBSlider.sliders['g'].setColor(color=(value, *self.color[1:]))
                RGBSlider.sliders['b'].setColor(color=(value, *self.color[1:]))
            case 'g':
                RGBSlider.sliders['r'].setColor(color=(self.color[0], value, self.color[2]))
                RGBSlider.sliders['b'].setColor(color=(self.color[0], value, self.color[2]))
            case 'b':
                RGBSlider.sliders['r'].setColor(color=(self.color[0], self.color[1], value))
                RGBSlider.sliders['g'].setColor(color=(self.color[0], self.color[1], value))
                
                
root = tk.Tk()
root.title("RGB Slider Example")

slider_r = RGBSlider(root, mode='r')
slider_r.pack(pady=10)
slider_r = RGBSlider(root, mode='g')
slider_r.pack(pady=10)
slider_r = RGBSlider(root, mode='b')
slider_r.pack(pady=10)


root.mainloop()
