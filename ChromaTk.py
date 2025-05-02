import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import numpy as np
from TimeIt import TimeIT, TimeITAvg, Chronos
import colorsys, cv2, inspect
import matplotlib.colors as mcolors


class ChromaSlider(tk.Canvas):
    def __init__(self, master, color, mode, length, height, limit, variable, pointerSize, corner_radius,colorMgr, **kwargs):
        super().__init__(master, width=length+pointerSize*2, height=height, highlightthickness=0, **kwargs)
        if isinstance(colorMgr, chroma):
            self.colors = colorMgr
        elif chroma._instances:
            print(f"Warning : color manager not provided or invalid, defaulting to automatic mode.\nActive color manager found. Channel {mode} linked to {tuple(chroma._instances[-1].sliders.keys())}")
            self.colors = chroma._instances[-1]
        elif colorMgr is None:
            print("Warning : color manager not provided or invalid, defaulting to automatic mode")
            self.colors = chroma(master, color)

        self.mode = mode
        self.length = length
        self.height = height
        self.limit = limit if limit is not None else (0,255) if mode in 'rgb' else (0,360) if mode == 'hue' else (0,100)
        self.pointerSize = pointerSize
        self.corner_radius = corner_radius
        self.pointerY = self.height // 2
        self.variable = variable
        
        self.colors.sliders[mode] = self
        self.colors.listeners.append(self.setColor)
        
        self.pixels = np.zeros((self.height, self.length, 3), dtype=np.uint8)
        self._roundedMask = self._roundedEdgeMask()
        self.linespaceRGB = np.linspace(0, 255, self.length, dtype=np.uint8)
        self.linespaceHue = np.linspace(0, 179, self.length)
        self.linespaceHSV = np.linspace(0, 255, self.length)
        # self.cache = {}
        
        self.photo = ImageTk.PhotoImage(self._computeGradient()) 
        self.create_image(pointerSize, 0, anchor='nw', image=self.photo)
        self.pointer = self.create_oval(0, 0, 0, 0, fill='white', outline='gray', width=2)

        self.bind('<B1-Motion>', self.update)
        self.bind('<Button-1>', self.update)
        self.callback = True
        if variable is not None: variable.trace_add('write', self.variableCallback)
        
        # self.modeMap = {
        #     'r' : self.colors.r,
        #     'g' : self.colors.g,
        #     'b' : self.colors.b,
        #     'hue' : self.colors.hsv[0],
        #     's' : self.colors.hsv[1],
        #     'v' : self.colors.hsv[2]
        # }
        
    def _roundedEdgeMask(self, scale=4):
        if self.corner_radius > 0:
            scale = scale 
            mask = Image.new("L", (self.length * scale, self.height * scale), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle(
                (0, 0, self.length * scale, self.height * scale),
                radius=self.corner_radius * scale,
                fill=255
            )
            mask = mask.resize((self.length, self.height), Image.LANCZOS)
            return mask
    
    def setPointer(self, value=0):
        x = ((value - self.limit[0]) / (self.limit[1] - self.limit[0])) * self.length + self.pointerSize
        self.coords(self.pointer, x - self.pointerSize, self.pointerY - self.pointerSize, x + self.pointerSize, self.pointerY + self.pointerSize)
        self.value = value
    
    @TimeITAvg(id=3)
    def update(self, event):
        x = event.x
        
        if not self.pointerSize <= x <= self.length + self.pointerSize:
            return

        self.value = int(((x - self.pointerSize) / self.length) * self.limit[1])
        
        self.coords(self.pointer, x - self.pointerSize, self.pointerY - self.pointerSize,
                    x + self.pointerSize, self.pointerY + self.pointerSize)
        
        if self.variable:
            self.callback = False
            self.variable.set(self.value)
            self.callback = True
            
        match self.mode:
            case 'r'|'g'|'b':
                self.colors.setRGB(**{self.mode:self.value})
            
            case 'hue':
                if self.value == 360: 
                    self.colors.setHue(self.colors.sliders['hue'].value)
                    self.setPointer(360)
                else:
                    self.colors.setHSV(self.colors.sliders['hue'].value, self.colors.sliders['s'].value, self.colors.sliders['v'].value)
            
            case 's'|'v':
                self.colors.setHSV(self.colors.sliders['hue'].value, self.colors.sliders['s'].value, self.colors.sliders['v'].value)
    
    def variableCallback(self, *args):
        if self.callback:
            self.setColor()
        
class RGBSlider(ChromaSlider):
    def __init__(self, master,
                 color=(1.0, 0, 0), mode='r',
                 length=300, height=10,
                 limit=None, variable=None, 
                 pointerSize = 6, corner_radius=30,
                 colorMgr=None, **kwargs):
        super().__init__(master, color, mode, length, height, limit, variable, pointerSize, corner_radius,colorMgr, **kwargs)
        
        self.setColor()
    
    def _computeGradient(self):
        match self.mode:
            case 'r':
                self.pixels[:, :, 0] = self.linespaceRGB
                self.pixels[:, :, 1] = self.colors.g
                self.pixels[:, :, 2] = self.colors.b
            case 'g':
                self.pixels[:, :, 0] = self.colors.r
                self.pixels[:, :, 1] = self.linespaceRGB
                self.pixels[:, :, 2] = self.colors.b
            case 'b':
                self.pixels[:, :, 0] = self.colors.r
                self.pixels[:, :, 1] = self.colors.g
                self.pixels[:, :, 2] = self.linespaceRGB
        # self.pixels[:, :, 3] = 255

        image = Image.fromarray(self.pixels, "RGB")
        image.putalpha(self._roundedMask)

        return image

    def setColor(self, RGB=None):
        self.setSliderColor(RGB)
        self.setPointer(self.colors.r if self.mode == 'r' else self.colors.g if self.mode == 'g' else self.colors.b)
    
    def setSliderColor(self, RGB=None):
        self.image = self._computeGradient()
        self.photo.paste(self.image)


class HSVSlider(ChromaSlider):
    def __init__(self, master,
                 color=(1.0, 0, 0), mode='r',
                 length=300, height=10,
                 limit=None, variable=None, 
                 pointerSize = 6, corner_radius=30,
                 colorMgr=None, **kwargs):
        super().__init__(master, color, mode, length, height, limit, variable, pointerSize, corner_radius,colorMgr, **kwargs)
        
        self.setColor()
        
    
    
    def _computeGradient(self):
        # if self.colors.hsv in self.cache: return self.cache[self.colors.hsv]
        if self.mode == 'hue':
            self.pixels[:, :, 0] = self.linespaceHue
            self.pixels[:, :, 1].fill(int(self.colors.s * 255))
            self.pixels[:, :, 2].fill(int(self.colors.v * 255))
        elif self.mode == 's':
            self.pixels[:, :, 0].fill(int(self.colors.hue * 179))
            self.pixels[:, :, 1] = self.linespaceHSV
            self.pixels[:, :, 2].fill(int(self.colors.v * 255))
        elif self.mode == 'v':
            self.pixels[:, :, 0].fill(int(self.colors.hue * 179))
            self.pixels[:, :, 1].fill(int(self.colors.s * 255))
            self.pixels[:, :, 2] = self.linespaceHSV
                
        self.pixels = cv2.cvtColor(self.pixels, cv2.COLOR_HSV2RGB)
        image = Image.fromarray(self.pixels, mode='RGB')
        image.putalpha(self._roundedMask)
        # self.cache[self.colors.hsv] = image
        return image
    
    def _computeGradientNoHueUpdates(self):
        match self.mode:
            case 'hue':
                hsv = np.column_stack([self.linespaceHSV, np.ones_like(self.linespaceHSV), np.ones_like(self.linespaceHSV)])
                rgb = mcolors.hsv_to_rgb(hsv) * 255
            
            case 's':
                hsv = np.column_stack([np.full_like(self.linespaceHSV, self.colors.hue), self.linespaceHSV, np.ones_like(self.linespaceHSV)])
                rgb = mcolors.hsv_to_rgb(hsv) * 255
                
            case 'v':
                hsv = np.column_stack([np.full_like(self.linespaceHSV, self.colors.hue), np.ones_like(self.linespaceHSV), self.linespaceHSV])
                rgb = mcolors.hsv_to_rgb(hsv) * 255
                
        pixels = np.tile(rgb, [self.height, 1, 1])     
        image = Image.fromarray(pixels.astype(np.uint8))  
        image.putalpha(self._roundedMask)

        return image
    
    def setColor(self, hue=None, s=None, v=None):
        self.setSliderColor(hue, s, v)
        self.setPointer(self.colors.hsv[0] if self.mode == 'hue' else self.colors.hsv[1] if self.mode == 's' else self.colors.hsv[2])
     
    def setSliderColor(self, hue=None, s=None, v=None):
        self.image = self._computeGradient()
        self.photo.paste(self.image)
        
class chroma:
    _instances = []
    __slots__ = ("master", "rgb", "hue", "s", "v", "hsv", "hex_code","r","g","b","sliders","listeners")
    def __init__(self, master, rgb=(1.0, 0, 0)):
        self.master = master
        self.sliders = {}
        self.listeners = []
        self.rgb = rgb
        self._updateColors()
        chroma._instances.append(self)
        
    # def rgb_hsv_preserved(self):
        
    def _updateColorsPreservedHueOff(self):
        self.r , self.g, self.b = (val*255 for val in self.rgb)
        self.hue, self.s, self.v = colorsys.rgb_to_hsv(*self.rgb)
        self.hsv = (self.hue * 360, self.s * 100, self.v * 100)
        self.hex_code = '#{:02x}{:02x}{:02x}'.format(*[int(x * 255) for x in self.rgb])
        for listener in self.listeners: listener()
    
    def _updateColors(self):
        self.r , self.g, self.b = (val*255 for val in self.rgb)
        hue, s, v = colorsys.rgb_to_hsv(*self.rgb)
        if s == 0: hue = self.hue
        if v == 0: s = self.s
        self.hue, self.s, self.v = hue, s, v
        self.hsv = (self.hue * 360, self.s * 100, self.v * 100)
        self.hex_code = '#{:02x}{:02x}{:02x}'.format(*[int(x * 255) for x in self.rgb])
        for listener in self.listeners: listener()

    def setHue(self, hue=None, rgb=None):
        if rgb:
            self.rgb = tuple(x / 255.0 for x in rgb)
            hue, *_ = colorsys.rgb_to_hsv(*self.rgb)
        else:
            hue = self.hue if hue is None else hue/360
        self.rgb = colorsys.hsv_to_rgb(hue, self.s, self.v )
        self._updateColors()
    
    def setHSV(self, hue=None, s=None, v=None, rgb=None):
        if rgb is not None:
            self.rgb = tuple(x / 255.0 for x in rgb)
            hue, s, v = colorsys.rgb_to_hsv(*self.rgb)

        self.rgb = colorsys.hsv_to_rgb(self.hue if hue is None else hue/360, self.s if s is None else s/100, self.v if v is None else v/100)
        self._updateColors()


    def setRGB(self, r=None, g=None, b=None):
        self.rgb = (r/255 if r is not None else self.rgb[0], g/255 if g is not None else self.rgb[1], b/255 if b is not None else self.rgb[2])
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
    
    def notifyListeners(self):
        for listener in self.listeners: listener() 
    
    


