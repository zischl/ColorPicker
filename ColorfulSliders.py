import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import numpy as np

class RGBSlider(tk.Canvas):
    sliders = {}

    def __init__(self, master, color=(0, 0, 0), mode='r', length=300, height=10, limit=(0,255), variable=False, 
                 pointerSize = 6, corner_radius=30, **kwargs):
        super().__init__(master, width=length+pointerSize*2, height=height, highlightthickness=0, **kwargs)
        RGBSlider.color = color
        self.mode = mode
        self.length = length
        self.height = height
        self.limit = limit
        self.pointerSize = pointerSize
        self.corner_radius = corner_radius
        self.variable = variable
        RGBSlider.sliders[mode] = self
        
        self.photo = ImageTk.PhotoImage(self._computeGradient()) 
        self.create_image(pointerSize, 0, anchor='nw', image=self.photo)
        self.pointer = self.create_oval(0, 0, 0, 0, fill='white', outline='gray', width=2)

        self.value = color[0] if mode=='r' else color[1] if mode=='g' else color[2]
        self.bind('<B1-Motion>', self.update)
        self.bind('<Button-1>', self.update)
        

        self.setSliderColor()
        self.setPointer()
    
    def _computeGradient(self):
        r, g, b = RGBSlider.color
        base = np.zeros((self.height, self.length, 4), dtype=np.uint8)
        ramp = np.linspace(0, 255, self.length, dtype=np.uint8)

        if self.mode == 'r':
            base[:, :, 0] = ramp
            base[:, :, 1] = g
            base[:, :, 2] = b
        elif self.mode == 'g':
            base[:, :, 0] = r
            base[:, :, 1] = ramp
            base[:, :, 2] = b
        elif self.mode == 'b':
            base[:, :, 0] = r
            base[:, :, 1] = g
            base[:, :, 2] = ramp
        base[:, :, 3] = 255
        image = Image.fromarray(base, "RGBA")

        if self.corner_radius > 0:
            scale = 4 
            mask_big = Image.new("L", (self.length * scale, self.height * scale), 0)
            draw = ImageDraw.Draw(mask_big)
            draw.rounded_rectangle(
                (0, 0, self.length * scale, self.height * scale),
                radius=self.corner_radius * scale,
                fill=255
            )
            mask = mask_big.resize((self.length, self.height), Image.LANCZOS)
            image.putalpha(mask)

        return image

    def setColor(self, color=False):
        self.setSliderColor(color)
        self.setPointer(RGBSlider.color[0] if self.mode == 'r' else RGBSlider.color[1] if self.mode == 'g' else RGBSlider.color[2])

    def setPointer(self, value=0):
        y = self.height // 2
        x = ((value/255)*self.length)+self.pointerSize
        self.coords(self.pointer, x - self.pointerSize, y - self.pointerSize, x + self.pointerSize, y + self.pointerSize)
    
    def setSliderColor(self, color=False):
        RGBSlider.color = color if color else RGBSlider.color
        self.image = self._computeGradient()
        self.photo.paste(self.image)

    def update(self, event):
        x = event.x
        if x <= self.pointerSize or x > self.length+self.pointerSize: return
        value = int(((x-self.pointerSize) / self.length) * 255)
        y = self.height // 2
        self.coords(self.pointer, x - self.pointerSize, y - self.pointerSize, x + self.pointerSize, y + self.pointerSize)

        match self.mode:
            case 'r':
                RGBSlider.sliders['g'].setSliderColor(color=(value, *self.color[1:]))
                RGBSlider.sliders['b'].setSliderColor(color=(value, *self.color[1:]))
            case 'g':
                RGBSlider.sliders['r'].setSliderColor(color=(self.color[0], value, self.color[2]))
                RGBSlider.sliders['b'].setSliderColor(color=(self.color[0], value, self.color[2]))
            case 'b':
                RGBSlider.sliders['r'].setSliderColor(color=(self.color[0], self.color[1], value))
                RGBSlider.sliders['g'].setSliderColor(color=(self.color[0], self.color[1], value))
        
        if self.variable: self.variable.set(value)
