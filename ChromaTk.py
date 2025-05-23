import tkinter as tk
import customtkinter
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import colorsys, cv2
import matplotlib.colors as mcolors
from functools import lru_cache

class ChromaSlider(tk.Canvas):
    cache = 20000
    def __init__(self, master, color, mode, length, height, limit, 
                 variable, pointerSize, corner_radius,colorMgr, autolink, **kwargs):
        super().__init__(master, width=length+pointerSize*2, height=height, highlightthickness=0, **kwargs)
        if isinstance(colorMgr, chroma):
            self.colors = colorMgr
        elif chroma._instances:
            print(f"Warning : color manager not provided or invalid, defaulting to automatic mode.\nActive color manager found. Channel {mode} linked to {tuple(chroma._instances[-1].sliders.keys())}")
            self.colors = chroma._instances[-1]
        elif colorMgr is None and autolink is True:
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
        
        self.photo = ImageTk.PhotoImage(self._computeGradient()) 
        self.create_image(pointerSize, 0, anchor='nw', image=self.photo)
        self.pointerImg = ChromaPointer.getPointer((height,height))
        self.pointer = self.create_image(0, 0, image=self.pointerImg, anchor=tk.CENTER)

        self.bind('<B1-Motion>', self.update)
        self.bind('<Button-1>', self.update)
        self.callback = True
        if variable is not None: variable.trace_add('write', self.variableCallback)
        
        
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
        self.coords(self.pointer, x, self.pointerY)
        self.value = value
    
    def update(self, event):
        x = event.x
        
        if not self.pointerSize <= x <= self.length + self.pointerSize:
            return

        self.value = int(((x - self.pointerSize) / self.length) * self.limit[1])
        
        self.coords(self.pointer, x, self.pointerY)
        
        if self.variable:
            self.callback = False
            self.variable.set(self.value)
            self.callback = True
            
        match self.mode:
            case 'r'|'g'|'b':
                self.colors.setRGB(**{self.mode:self.value})
            
            case 'hue':
                print(self.value)
                if self.value == 360: 
                    self.colors.setHue(self.colors.sliders['hue'].value)
                    self.setPointer(360)
                else:
                    self.colors.setHSV(self.colors.sliders['hue'].value, self.colors.sliders['s'].value, self.colors.sliders['v'].value)
            
            case 's'|'v':
                self.colors.setHSV(self.colors.sliders['hue'].value, self.colors.sliders['s'].value, self.colors.sliders['v'].value)

            case 'sl'|'l':
                self.colors.setHLS(self.colors.sliders['hue'].value, self.colors.sliders['l'].value, self.colors.sliders['sl'].value)
                
    def variableCallback(self, *args):
        if self.callback:
            self.setColor()
        
class RGBSlider(ChromaSlider):
    def __init__(self, master,
                 color=(1.0, 0, 0), mode='r',
                 length=300, height=10,
                 limit=None, variable=None, 
                 pointerSize = 10, corner_radius=30,
                 colorMgr=None, autolink=True, **kwargs):
        super().__init__(master, color, mode, length, height, limit, variable, pointerSize, corner_radius,colorMgr, autolink, **kwargs)
        
        self.setColor()
    
    @lru_cache(maxsize=ChromaSlider.cache)
    def _computeGradient(self, rgb=None):
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
        self.image = self._computeGradient(self.colors.rgb)
        self.photo.paste(self.image)


class HSVSlider(ChromaSlider):
    def __init__(self, master,
                 color=(1.0, 0, 0), mode='H',
                 length=300, height=10,
                 limit=None, variable=None, 
                 pointerSize = 10, corner_radius=30,
                 colorMgr=None, autolink=True, **kwargs):
        super().__init__(master, color, mode, length, height, limit, variable, pointerSize, corner_radius,colorMgr, autolink, **kwargs)
        
        self.setColor()
    
    @lru_cache(maxsize=ChromaSlider.cache)
    def _computeGradient(self, hsv=None):
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
        self.image = self._computeGradient(self.colors.hsv)
        self.photo.paste(self.image)
        
        
class HSLSlider(ChromaSlider):
    def __init__(self, master,
                 color=(1.0, 0, 0), mode='H',
                 length=300, height=10,
                 limit=None, variable=None, 
                 pointerSize = 10, corner_radius=30,
                 colorMgr=None, autolink=True, **kwargs):
        super().__init__(master, color, mode, length, height, limit, variable, pointerSize, corner_radius,colorMgr, autolink, **kwargs)
        
        self.setColor()
    
    @lru_cache(maxsize=ChromaSlider.cache)
    def _computeGradient(self, hls=None):
        # if self.colors.hsl in self.cache: return self.cache[self.colors.hsl]
        if self.mode == 'hue':
            self.pixels[:, :, 0] = self.linespaceHSV
            self.pixels[:, :, 1].fill(int(self.colors.l * 255))
            self.pixels[:, :, 2].fill(int(self.colors.s_hsl * 255))
        elif self.mode == 'sl':
            self.pixels[:, :, 0].fill(int(self.colors.hue * 255))
            self.pixels[:, :, 1].fill(int(self.colors.l * 255))
            self.pixels[:, :, 2] = self.linespaceHSV
        elif self.mode == 'l':
            self.pixels[:, :, 0].fill(int(self.colors.hue * 255))
            self.pixels[:, :, 1] = self.linespaceHSV
            self.pixels[:, :, 2].fill(int(self.colors.s_hsl * 255))
                
        self.pixels = cv2.cvtColor(self.pixels, cv2.COLOR_HLS2RGB_FULL)
        image = Image.fromarray(self.pixels, mode='RGB')
        image.putalpha(self._roundedMask)
        # self.cache[self.colors.hsl] = image
        return image
    
    def setColor(self, hue=None, s=None, l=None):
        self.setSliderColor(hue, s, l)
        self.setPointer(self.colors.hsl[0] if self.mode == 'hue' else self.colors.hsl[1] if self.mode == 'sl' else self.colors.hsl[2])
     
    def setSliderColor(self, hue=None, s=None, l=None):
        self.image = self._computeGradient(self.colors.hsl)
        self.photo.paste(self.image)
        
class ChromaSpinBox(tk.Canvas):
    def __init__(self, master, bg='#181818', limit=(0,100), variable=None, width=75, height=16,
                 command=None, commandKeyword='value', colorMgr=None, autolink=False, disableSteppers=False, 
                 mode='r', justify='center', autoHideSteppers=False, **kwargs):
        super().__init__(master, bg=bg, **kwargs)
        
        self.decrement = tk.Label(self, text='\u2212', font=('Helvetica',height,'bold'), foreground='white', bg=bg)
        self.entry = customtkinter.CTkEntry(self, fg_color=bg, width=width-10, justify=justify, border_width=0, height=self.decrement.winfo_reqheight(), corner_radius=0)
        self.increment = tk.Label(self, text='+', font=('Helvetica',height,'bold'), foreground='white', bg=bg)
        
        self.commandKeyword = commandKeyword
        self.limit = limit
        if variable is not None:
            self.variable = variable
        else:
            self.variable = tk.IntVar(self, value=0)
        self.command = command if command is not None else None
        self.callback = True
        self.colors = None
        self.mode = mode
        self.autoHideSteppers = autoHideSteppers
        
        self.value = tk.StringVar(self, int(self.variable.get()))
        self.switch = True
        self.inputCheck = self.register(self.ValueCheck)
        self.entry.configure(validate="key", validatecommand=(self.inputCheck, '%P'), textvariable=self.value)
        self.variable.trace_add('write', self.variableCallback)
        self.value.trace_add('write', self.onKeyPress)
        
        if not disableSteppers:
            self.decrement.pack(side='left', ipadx=height//5)
            self.entry.pack(side='left')
            self.increment.pack(side='left', ipadx=height//5)
            self.increment.bind("<ButtonPress-1>", self.increase)
            self.decrement.bind("<ButtonPress-1>", self.decrease)
            self.increment.bind("<ButtonRelease-1>", self.valueSwitch)
            self.decrement.bind("<ButtonRelease-1>", self.valueSwitch)
            self.increment.bind("<Enter>", lambda event: self.increment.configure(bg='#585858'))
            self.decrement.bind("<Enter>", lambda event: self.decrement.configure(bg='#585858'))
            self.increment.bind("<Leave>", lambda event: self.increment.configure(bg=bg))
            self.decrement.bind("<Leave>", lambda event: self.decrement.configure(bg=bg))
        
        else:
            self.entry.pack(side='left')
        # if self.autoHideSteppers:
        #     self.increment.pack_forget()
        #     self.decrement.pack_forget()
        #     self.entry.bind("<Enter>", lambda event: )
            
        if isinstance(colorMgr, chroma):
            self.colors = colorMgr
            self.colors.listeners.append(lambda: self.setValue(getattr(self.colors, mode)))
        elif chroma._instances and autolink:
            print(f"Warning : color manager not provided or invalid, defaulting to automatic mode.\nActive color manager found. Channel {mode} spin box linked to {tuple(chroma._instances[-1].sliders.keys())}")
            self.colors = chroma._instances[-1]
            self.colors.listeners.append(lambda: self.setValue(getattr(self.colors, mode)))
        elif colorMgr is None and autolink is True:
            print("Warning : color manager not provided or invalid, defaulting to automatic mode")
            self.colors = chroma(master, (1, 0, 0))
            self.colors.listeners.append(lambda: self.setValue(getattr(self.colors, mode)))
        
    def ValueCheck(self, entry):
        return entry[1:].isdigit() or entry.isdigit() or entry in '-'

    def variableCallback(self, *args):
        if not self.callback: pass

        self.callback = False
        self.value.set(max(self.limit[0], min(int(self.variable.get()), self.limit[1])))
        self.callback = True
    
    def onKeyPress(self, *args):
        if not self.callback: pass
        try:
            variable =  self.value.get()
            if variable in "-+":
                return
            value = max(self.limit[0], min(int(variable), self.limit[1]))
            self.value.set(value)
            if self.command is not None: self.command(**{self.commandKeyword:value})
            self.callback = False
            self.variable.set(value)
            self.callback = True
            if self.colors is not None: self.colors.setColor(**{self.mode:value})
                
        except Exception:
            pass
        
        
    def increase(self, event=None, count=1):
        self.variable.set(max(self.limit[0], min(int(self.variable.get())+1, self.limit[1])))
        self.switch = self.after(500//count+30, self.increase, None, count+1)
    
    def decrease(self, event=None, count=1):
        self.variable.set(max(self.limit[0], min(int(self.variable.get())-1, self.limit[1])))
        self.switch = self.after(500//count+30, self.decrease, None, count+1)
        
    def valueSwitch(self, event):
        self.after_cancel(self.switch)
        
    def get(self):
        self.value.get()
    
    def setValue(self, value):
        self.value.set(value=value)
        
class CopyOutField(customtkinter.CTkEntry):
    def __init__(self, master, textvariable, fg_color='#181818', font=('',14), border_width=0, **kwargs):
        super().__init__(master, textvariable=textvariable, fg_color=fg_color, font=font, border_width=border_width, **kwargs)

        self.bind("<Enter>", lambda event: self.onHover(1))
        self.bind("<Leave>", lambda event: self.onHover(0))
        
        self.copyButton = customtkinter.CTkButton(self, text='\u2398', bg_color=fg_color, fg_color=fg_color, command=self.copy, 
                                    border_width=0, font=('',16), width=10, height=10)
        self.copyButton.grid(row=0, padx=(75,0))
        self.copyButton.bind("<Enter>", lambda event: self.copyButton.configure(border_width=1))
        self.copyButton.bind("<Leave>", lambda event: self.copyButton.configure(border_width=0))
        
    def onHover(self, bd):
        self.configure(border_width=bd)
        
    def copy(self):
        self.clipboard_clear()
        self.clipboard_append(self.get())
        self.update()


class ChromaPointer:
    pointer = None
    if pointer is None:
        pointerImage = Image.new("RGBA", (60, 60), (255, 255, 255, 0))
        draw = ImageDraw.Draw(pointerImage)
        draw.ellipse((0, 0, 59, 59), outline="white", width=15)
        pointer = pointerImage
        
        
    def getPointer(size=(10,10)):
        return ImageTk.PhotoImage(ChromaPointer.pointer.resize(size, Image.LANCZOS))
      
class ColorTile(customtkinter.CTkFrame):
    def __init__(self, master, hexCode, height=40, width=40, variable=None, command=None, **kwargs):
        super().__init__(master, fg_color=hexCode, corner_radius=10, width=width, height=height, cursor="hand2", **kwargs)
        self.hexCode = hexCode
        self.hover = self.hex2gray(self.hexCode)
        self.height = height
        self.width = width

        self.bind("<Enter>", self.onHover)
        self.bind("<Leave>", self.onLeave)
        
        self.command = command
        self.variable = variable
        if command is not None or variable is not None:
            self.bind("<Button-1>", self.onClick)

    def onHover(self, event):
        self.tooltip = self._canvas.create_text(self.width//2, self.height//2, text=self.hexCode.strip('#'), fill="white", font=('',8))
        self.configure(fg_color=self.hover)
        
    def onLeave(self, event=None):
        self._canvas.itemconfigure(self.tooltip, fill = self.hexCode)
        self.configure(fg_color=self.hexCode)

    def onClick(self, event):
        if self.command:
            self.command(self.hexCode)
        if self.variable: self.variable.set(self.hexCode)
        
    def hex2gray(self, hex_color, strength=0.4):
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)

        mixer = lambda color: int(color * strength)

        return '#{:02x}{:02x}{:02x}'.format(mixer(r), mixer(g), mixer(b))
    
    

class array:
    def __init__(self, size, returnIndex):
        self.data = []
        self.size = size
        self.returnIndex = returnIndex
        
    def append(self, obj):
        self.data.append(obj)
        if len(self.data) > self.size:
            return self.data.pop(self.returnIndex)
        return None
    
    def get(self, index=0, invalid=None):
        return self.data[index] if -len(self.data) <= index < len(self.data) else invalid
    
    def pop(self, index=0):
        return self.data.pop(index)
        
class ChromaPalette(tk.Canvas):
    def __init__(self, master, rows, columns, height=150, width=150, tileWidth=40, tileHeight=40, colorVar=None, **kwargs):
        super().__init__(master, height=height, width=width, **kwargs)
        self.objects = []
        self.rows = rows
        self.columns = columns
        self.max = (rows*columns)-1
        self.count = 0
        self.variable = colorVar
        
        self.frames = [tk.Frame(self, **kwargs) for frame in range(rows)]
        for index, frame in enumerate(self.frames):
            frame.pack(fill='x')
            self.objects.append(array(*(self.columns-1, 0) if index==0 else (self.columns, 0)))
            
        self.addButton = customtkinter.CTkButton(self.frames[0], width=tileWidth, height=tileHeight, fg_color='#2c2c2c',
                                                 text='+', font=('',20,'bold'), command=lambda :self.add(colorVar.get()))
        self.addButton.pack(padx=3, pady=3, side='left')
    
    def add(self, hex):  
        tile = ColorTile(self.frames[0], hex, variable=self.variable)
        tile.pack(padx=3, pady=3, anchor='w', after=self.addButton, side='left')
        returnValue = self.objects[0].append(tile)
        self.count += 1
        
        if self.count > self.max: self.objects[-1].pop(0).destroy()
        
        if returnValue is not None:
            self.limitManager(returnValue, 1)
            
        
    def limitManager(self, returnValue, frame):
        if returnValue is not None:
            tile = ColorTile(self.frames[frame], returnValue.hexCode, variable=self.variable)
            returnValue.destroy()
            tile.pack(padx=3, anchor='w', before=self.objects[frame].get(-1), side='left')
            returnValue = self.objects[frame].append(tile)
            self.limitManager(returnValue, frame+1)

class ChromaHistory(tk.Canvas):
    def __init__(self, master, limit=20, height=50, width=150, tileWidth=40, tileHeight=40, colorVar=None, data=None, **kwargs):
        super().__init__(master, height=height, width=width, **kwargs)
        self.history = []
        self.max = limit
        self.variable = colorVar
        
        self.frame = tk.Frame(self, **kwargs)
        self.create_window(0, 0, anchor='nw',window=self.frame)
        
        if data is not None:
            for each in data:
                self.add(each)

    def add(self, hex):  
        tile = ColorTile(self.frame, hex, variable=self.variable)
        tile.pack(padx=3, pady=3, anchor='w', side='left', before=self.history[-1] if self.history else None)
        self.history.append(tile)
        
        self.count = len(self.history)
        if self.count > self.max: self.history.pop(0).destroy()
        
    def clear(self):
        for each in self.history:
            each.destroy()
        self.history.clear()


class chroma:
    _instances = []
    __slots__ = ("master", "rgb", "hue", "s", "v", "hsv", "hex_code","r","g","b","l","s_hsl","hsl","sliders","listeners")
    def __init__(self, master, rgb=(1.0, 0, 0)):
        self.master = master
        self.sliders = {}
        self.listeners = []
        self.rgb = rgb
        self._updateColors()
        chroma._instances.append(self)
                
    def _updateColorsPreservedHueOff(self):
        self.r , self.g, self.b = (val*255 for val in self.rgb)
        self.hue, self.s, self.v = colorsys.rgb_to_hsv(*self.rgb)
        self.l = self.v * (1 - self.s / 2)
        self.s_hsl = (self.v * self.s) / max(1 - abs(2 * self.l - 1), 1e-10)
        self.hsl = (self.hue * 360, self.s_hsl * 100, self.l * 100)
        self.hsv = (self.hue * 360, self.s * 100, self.v * 100)
        self.hex_code = '#{:02x}{:02x}{:02x}'.format(*[int(x * 255) for x in self.rgb])
        for listener in self.listeners: listener()
        
    def _updateColors(self):
        r, g, b = self.rgb
        r255 = int(r * 255)
        g255 = int(g * 255)
        b255 = int(b * 255)
        self.r, self.g, self.b = r255, g255, b255

        hue, s, v = colorsys.rgb_to_hsv(r, g, b)
        h_, l, s_hsl = colorsys.rgb_to_hls(r, g, b)

        if s < 1e-5:
            hue, s_hsl = self.hue, self.s_hsl
        if v < 1e-5:
            s = self.s

        self.hue, self.s, self.v = hue, s, v
        self.l = l
        self.s_hsl = s_hsl

        self.hsl = (hue * 360.0, s_hsl * 100.0, l * 100.0)
        self.hsv = (hue * 360.0, s * 100.0, v * 100.0)
        self.hex_code = f'#{r255:02x}{g255:02x}{b255:02x}'.upper()

        for listener in self.listeners:
            listener()

        
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
        
    def setHLS(self, hue=None, l=None, s=None):
        self.rgb =  colorsys.hls_to_rgb(self.hue if hue is None else hue/360, self.l if l is None else l/100, self.s_hsl if s is None else s/100)
        self._updateColors()
        
    def setColor(self, **kwargs):
        if 'r' or 'g' or 'b' in kwargs:
            self.setRGB(**kwargs)
        elif 'h' or 's' or 'v' in kwargs:
            self.setHSV(**kwargs)
        elif 'h' or 'sl' or 'l' in kwargs:
            self.setHLS(**kwargs)
            
    def hex2rgb(self, hex_code):
        byte = bytes.fromhex(hex_code)
        return (byte[0] / 255.0, byte[1] / 255.0, byte[2] / 255.0)
        
    def setHex(self, hex=None):
        hex = hex.lstrip('#')
        if len(hex) == 6 and all(c in '0123456789abcdefABCDEF' for c in hex):
            self.rgb = self.hex2rgb(hex)
            self._updateColors()
        else: self.hex_code = f"#{hex}"
        
    def RGBslider(self, master=False,
                 color=(1.0, 0, 0), mode='r',
                 length=300, height=10,
                 limit=(0,255), variable=False, 
                 pointerSize = 10, corner_radius=30,
                 colorMgr=False, **kwargs):
        if not master: master = self
        RGBSlider(master, color, mode, length, height, limit, variable, pointerSize, corner_radius, colorMgr=self, **kwargs )
        return self.sliders[mode]
    
    def HSVslider(self, master,
                color=(1.0, 0, 0), mode='hue',
                length=300, height=10,
                limit=(0,360), variable=False, 
                pointerSize = 10, corner_radius=30,
                colorMgr=False, **kwargs):
        if not master: master = self
        HSVSlider(master, color, mode, length, height, limit, variable, pointerSize, corner_radius, colorMgr=self, **kwargs )
        return self.sliders[mode]
    
    def notifyListeners(self):
        for listener in self.listeners: listener() 
    


# root = tk.Tk()
# root.configure()

# slider1 = RGBSlider(root, mode='r')
# slider1.pack(pady=10)
# slider2 = RGBSlider(root, mode='g')
# slider2.pack(pady=10)
# slider3 = RGBSlider(root, mode='b')
# slider3.pack(pady=10)

# slider4 = HSVSlider(root, mode='hue')
# slider4.pack(pady=10)
# slider5 = HSVSlider(root, mode='s')
# slider5.pack(pady=10)
# slider6 = HSVSlider(root, mode='v')
# slider6.pack(pady=10)

# slider7 = HSLSlider(root, mode='sl')
# slider7.pack(pady=10)
# slider8 = HSLSlider(root, mode='l')
# slider8.pack(pady=10)

# spinner = ChromaSpinBox(root, autolink=True, limit=(0,255), width=45, height=16)
# spinner.pack(pady=10)

# root.mainloop()
