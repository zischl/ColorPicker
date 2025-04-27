import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import numpy as np

import colorsys

class RGBSlider(tk.Canvas):
    def __init__(self, master,
                 color=(1.0, 0, 0), mode='r',
                 length=300, height=10,
                 limit=(0,255), variable=False, 
                 pointerSize = 6, corner_radius=30,
                 colorMgr=False, **kwargs):
        super().__init__(master, width=length+pointerSize*2, height=height, highlightthickness=0, **kwargs)
        if colorMgr:
            self.colors = colorMgr
        else:
            self.colors = chroma(master, color)

        self.mode = mode
        self.length = length
        self.height = height
        self.limit = limit
        self.pointerSize = pointerSize
        self.corner_radius = corner_radius
        self.variable = variable
        self.colors.sliders[mode] = self
        self._roundedMask = self._roundedEdgeMask()
        
        self.photo = ImageTk.PhotoImage(self._computeGradient()) 
        self.create_image(pointerSize, 0, anchor='nw', image=self.photo)
        self.pointer = self.create_oval(0, 0, 0, 0, fill='white', outline='gray', width=2)

        self.bind('<B1-Motion>', self.update)
        self.bind('<Button-1>', self.update)
        

        self.setSliderColor()
        self.setPointer()
    
    def _computeGradient(self):
        r, g, b = self.colors.r, self.colors.g, self.colors.b
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
        image.putalpha(self._roundedMask)

        return image
    
    def _roundedEdgeMask(self, scale=4):
        if self.corner_radius > 0:
            scale = scale 
            mask_big = Image.new("L", (self.length * scale, self.height * scale), 0)
            draw = ImageDraw.Draw(mask_big)
            draw.rounded_rectangle(
                (0, 0, self.length * scale, self.height * scale),
                radius=self.corner_radius * scale,
                fill=255
            )
            mask = mask_big.resize((self.length, self.height), Image.LANCZOS)
            return mask        

    def setColor(self, RGB=False):
        self.setSliderColor(RGB)
        self.setPointer(self.colors.r if self.mode == 'r' else self.colors.g if self.mode == 'g' else self.colors.b)

    def setPointer(self, value=0):
        y = self.height // 2
        x = ((value/255)*self.length)+self.pointerSize
        self.coords(self.pointer, x - self.pointerSize, y - self.pointerSize, x + self.pointerSize, y + self.pointerSize)
    
    def setSliderColor(self, RGB=False):
        RGB = RGB if RGB else (self.colors.r, self.colors.g, self.colors.b)
        self.colors.setRGB(*RGB)
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
                self.colors.sliders['g'].setSliderColor(RGB=(value, self.colors.g, self.colors.b))
                self.colors.sliders['b'].setSliderColor(RGB=(value, self.colors.g, self.colors.b))
            case 'g':
                self.colors.sliders['r'].setSliderColor(RGB=(self.colors.r, value, self.colors.b))
                self.colors.sliders['b'].setSliderColor(RGB=(self.colors.r, value, self.colors.b))
            case 'b':
                self.colors.sliders['r'].setSliderColor(RGB=(self.colors.r, self.colors.g, value))
                self.colors.sliders['g'].setSliderColor(RGB=(self.colors.r, self.colors.g, value))
        
        if self.variable: self.variable.set(value)

class HSVSlider(tk.Canvas):
    def __init__(self, master,
                color=(1.0, 0, 0), mode='hue',
                length=300, height=10,
                limit=(0,360), variable=False, 
                pointerSize = 6, corner_radius=30,
                colorMgr=False, **kwargs):
        super().__init__(master, width=length+pointerSize*2, height=height, highlightthickness=0, **kwargs)
        
        if colorMgr:
            self.colors = colorMgr
        else:
            self.colors = chroma(master, color)

        self.mode = mode
        self.length = length
        self.height = height
        self.limit = limit
        self.pointerSize = pointerSize
        self.corner_radius = corner_radius
        self.variable = variable
        self.colors.sliders[mode] = self
        
        self.photo = ImageTk.PhotoImage(self._computeGradient()) 
        self.create_image(pointerSize, 0, anchor='nw', image=self.photo)
        self.pointer = self.create_oval(0, 0, 0, 0, fill='white', outline='gray', width=2)

        self.bind('<B1-Motion>', self.update)
        self.bind('<Button-1>', self.update)
        

        self.setSliderColor()
        self.setPointer()
    
    def _computeGradient(self):
        
        match self.mode:
            case 'hue':
                line = np.linspace(0.0, 1.0, self.length)
                pixels = np.array([colorsys.hsv_to_rgb(hue, 1, 1) for hue in line])
                pixels = pixels * 255
                pixels = np.tile(pixels, (self.height, 1, 1))
                image = Image.fromarray(pixels.astype(np.uint8))
            
            case 's':
                line = np.linspace(0.0, 1.0, self.length)
                pixels = np.array([colorsys.hsv_to_rgb(self.colors.hue, s, 1) for s in line])
                pixels = pixels * 255
                pixels = np.tile(pixels, (self.height, 1, 1))
                image = Image.fromarray(pixels.astype(np.uint8))
                
            case 'v':
                line = np.linspace(0.0, 1.0, self.length)
                pixels = np.array([colorsys.hsv_to_rgb(self.colors.hue, 1, v) for v in line])
                pixels = pixels * 255
                pixels = np.tile(pixels, (self.height, 1, 1))
                image = Image.fromarray(pixels.astype(np.uint8))
            
            
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

    def setColor(self, hue=False, s=False, v=False):
        self.setSliderColor(hue, s, v)
        self.setPointer()

    def setPointer(self, value=False):
        if not value:
            value = self.colors.hsv[0] if self.mode == 'hue' else self.colors.hsv[1] if self.mode == 's' else self.colors.hsv[2]
        y = self.height // 2
        x = ((value/self.limit[1])*self.length)+self.pointerSize
        self.coords(self.pointer, x - self.pointerSize, y - self.pointerSize, x + self.pointerSize, y + self.pointerSize)
    
    def setSliderColor(self, hue=False, s=False, v=False):
        h, saturation, value = self.colors.hsv
        self.colors.setHSV(h if not hue else hue, saturation if not s else s, value if not v else v)
        self.image = self._computeGradient()
        self.photo.paste(self.image)

    def update(self, event):
        x = event.x
        if x <= self.pointerSize or x > self.length+self.pointerSize: return
        value = int(((x-self.pointerSize) / self.length) * self.limit[1])
        y = self.height // 2
        self.coords(self.pointer, x - self.pointerSize, y - self.pointerSize, x + self.pointerSize, y + self.pointerSize)
        
        match self.mode:
            case 'hue':
                self.colors.sliders['s'].setColor(hue=value)
                self.colors.sliders['v'].setColor(hue=value)
        if self.variable: self.variable.set(value)

        
class chroma:
    __slots__ = ("master", "rgb", "hue", "s", "v", "hsv", "hex_code","r","g","b","sliders")
    def __init__(self, master, rgb):
        self.master = master
        self.rgb = rgb
        self._updateColors()
        self.sliders = {}

    def _updateColors(self):
        self.r , self.g, self.b = (val*255 for val in self.rgb)
        self.hue, self.s, self.v = colorsys.rgb_to_hsv(*self.rgb)
        self.hsv = (self.hue * 360, self.s * 100, self.v * 100)
        self.hex_code = '#{:02x}{:02x}{:02x}'.format(*[int(x * 255) for x in self.rgb])
        
    def setHue(self, hue=None, rgb=None):
        if rgb:
            self.rgb = tuple(x / 255.0 for x in rgb)
            hue, *_ = colorsys.rgb_to_hsv(*self.rgb)
        else:
            hue = self.hue if not hue else hue/360
        self.rgb = colorsys.hsv_to_rgb(hue, self.s, self.v )
        self._updateColors()
        
    def setHSV(self, hue=None, s=None, v=None, rgb=None):
        if rgb:
            self.rgb = tuple(x / 255.0 for x in rgb)
            hue, s, v = colorsys.rgb_to_hsv(*self.rgb)

        self.rgb = colorsys.hsv_to_rgb(self.hue if not hue else hue/360, self.s if not s else s/100, self.v if not v else v/100)
        self._updateColors()

           
    def setRGB(self, r, g, b):
        self.rgb = (r/255, g/255, b/255)
        self._updateColors()
        
    def RGBslider(self, master=False,
                 color=(1.0, 0, 0), mode='r',
                 length=300, height=10,
                 limit=(0,255), variable=False, 
                 pointerSize = 6, corner_radius=30,
                 colorMgr=False, **kwargs):
        if not master: master = self
        RGBSlider(master, color, mode, length, height, limit, variable, pointerSize, corner_radius, colorMgr=self, **kwargs )
        return self.sliders[mode]
    
    def HSVslider(self, master,
                color=(1.0, 0, 0), mode='hue',
                length=300, height=10,
                limit=(0,360), variable=False, 
                pointerSize = 6, corner_radius=30,
                colorMgr=False, **kwargs):
        if not master: master = self
        HSVSlider(master, color, mode, length, height, limit, variable, pointerSize, corner_radius, colorMgr=self, **kwargs )
        return self.sliders[mode]
    
    