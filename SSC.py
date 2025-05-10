import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

class SSC(tk.Canvas):
        def __init__(self, master, height, width, bg, padx=5, cornerSmoothness=4,
                     command=None, commandArgs : tuple = (), items=[], highlightthickness=0, font=('',13), **kwargs):
                super().__init__(master, width=width, height=height, highlightthickness=0, **kwargs)
                self.grid_propagate(False)
                self.grid_columnconfigure([0,2], weight=1)
                # self.grid_columnconfigure(1, weight=5)
                self.grid_rowconfigure(0, weight=1)
                self.configure(bg=master.cget('bg'))
                
                bacK = tk.Label(self, text="<", bg=bg, fg='white', font=font)
                bacK.grid(row=0, column=0, sticky='nes')
                self.thing = container(self, bg=bg, width=width, height=height, highlightthickness=highlightthickness, padx=padx, items=items
                                  , command=command, commandArgs=commandArgs, font=font)
                self.thing.grid(row=0, column=1)
                nexT = tk.Label(self, text=">", bg=bg, fg='white', font=font)
                nexT.grid(row=0, column=2, sticky='nws')
                nexT.bind("<Enter>", self.fwscroller)
                bacK.bind("<Enter>", self.bwscroller)
                nexT.bind("<Leave>", self.scrollReset)
                bacK.bind("<Leave>", self.scrollReset)
                nexT.bind("<Button-1>", self.thing.iterNext)
                bacK.bind("<Button-1>", self.thing.iterBack)
                
                self.img = Image.new("RGBA", (width*cornerSmoothness, height*cornerSmoothness))
                draw = ImageDraw.Draw(self.img)
                draw.pieslice((0, 0, height*cornerSmoothness, height*cornerSmoothness), start=90, end=270, fill=bg, width=5)
                draw.rectangle(((height*cornerSmoothness)/2, 0, (width*cornerSmoothness)-(height*cornerSmoothness)/2, height*cornerSmoothness), fill=bg)
                draw.pieslice(((width*cornerSmoothness)-(height*cornerSmoothness), 0, width*cornerSmoothness, height*cornerSmoothness), start=270, end=90, fill=bg, width=5)
                self.img = self.img.resize((width,height), Image.LANCZOS)
                self.image = ImageTk.PhotoImage(self.img, (width,height))
                self.create_image(0, 0, image=self.image, anchor='nw')


                
        def fwscroller(self, event=None, xview=0):
                if self.thing.xviewCenter == 1: return
                self.thing.xview_moveto(self.thing.xviewCenter+xview)
                self.callback = self.after(30, self.fwscroller, None, xview+0.01)
        
        def bwscroller(self, event=None, xview=0):
                if self.thing.xviewCenter == 0: return
                self.thing.xview_moveto(self.thing.xviewCenter+xview)
                self.callback = self.after(30, self.bwscroller, None, xview-0.01)
                
        def scrollReset(self, event):
                self.after_cancel(self.callback)
                self.thing.xview_moveto(self.thing.xviewCenter)
                print(self.thing.xviewCenter, self.thing.xview(), self.coords(self.thing.window))
        

class container(tk.Canvas):
        def __init__(self, master, width, height, bg, padx, items=None, command=None, commandArgs : tuple = (), font=('',13), **kwargs):
                super().__init__(master, height=height, width=width-height*2, bg=bg, **kwargs)
                self.grid_propagate(False)
                
                self.width = width-height*2
                self.height = height
                self.bg = bg
                self.padx = padx
                self.command = command
                self.commandArgs = commandArgs
                self.font = font
                
                self.itemFrame = tk.Frame(self, bg=bg, height=height)
                self.itemFrame.grid_rowconfigure(0, weight=1)
                self.items = [ ]
                self.window = self.create_window(0,0, window=self.itemFrame, anchor='nw', height=height)
                
                if items is not None:
                        for item in items: self.add(item)
                        self.selection = self.items[len(self.items)//2]
                        
                
                for _ in range(len(self.items)//2):
                        self.iterBack()
                                
                self.bind_class('node', "<Button-1>", self.onClick)
                self.bind_class('node', "<Enter>", self.onHover)
                self.bind_class('node', "<Leave>", self.onHover)

        def add(self, text):
                item = tk.Label(self.itemFrame, text=text, font=self.font, bg=self.bg, fg='gray', anchor='center', justify='center', height=self.height, padx=self.padx)
                self.items.append(item)
                self.itemFrame.columnconfigure(len(self.items), weight=1)
                item.grid(row=0, column=len(self.items))
                item.bindtags('node')
                self.update()
                self.xviewCenter = (self.itemFrame.winfo_reqwidth()/2-self.width/2)/self.itemFrame.winfo_reqwidth()
                self.configure(scrollregion=(0,0,self.itemFrame.winfo_reqwidth(),self.height))
                self.after(50, lambda: self.xview_moveto(self.xviewCenter))
                return item
                
        def itemManager(self):
                for index in range(len(self.items)):
                        self.items[index].grid_forget()
                        self.items[index].grid(row=0, column=index)
                self.selection.configure(fg='gray')
                self.selection = self.items[len(self.items)//2]
                self.selection.configure(fg='white')
        
        def iterBack(self, *args):
                self.items.insert(0, self.items.pop(-1))
                self.itemManager()
                if self.command is not None:
                        self.command(*self.commandArgs, self.selection.cget('text'))

        def iterNext(self, *args):
                self.items.append(self.items.pop(0))
                self.itemManager()
                if self.command is not None:
                        self.command(*self.commandArgs, self.selection.cget('text'))
                
        def onClick(self, event):
                times = self.items.index(event.widget) - self.items.index(self.selection)
                if times > 0:
                        for _ in range(times):
                                self.iterNext()
                else:
                        for _ in range(abs(times)):
                                self.iterBack()
        
        def onHover(self, event):
                event.widget.configure(fg='white' if event.widget.cget('fg') != 'white' or event.widget == self.selection else 'gray')



class FrameLord(tk.Frame):
        def __init__(self, master, **kwargs):
                super().__init__(master, **kwargs)        
                self.active = None
                self.frames = {}
                self.kwargs = kwargs
                self.grid_propagate(False)
                self.grid_rowconfigure(0, weight=1)
                self.grid_columnconfigure(0, weight=1)

        def add(self, id):
                self.frames[id] = tk.Frame(self, **self.kwargs)
                if self.active is None:
                        self.active = self.frames[id]
                        self.active.grid(row=0, column=0, sticky='nwse')
        
        def switch(self, id):
                self.active.grid_remove()
                self.frames[id].grid(in_=self, row=0, column=0, sticky='nwse')
                self.active = self.frames[id]
                
        def __getattr__(self, what):
                if what in self.frames:
                        return self.frames[what]
    
# root = tk.Tk()


# framelord = FrameLord(master=root, bg='#181818', width=500, height=500)
# for x in range(1,6):
#         framelord.add(f'item{x}')
# framelord.item1.configure(bg='red')
# tk.Button(framelord.item1).pack()

# test = container(root, bg='#181818', width=250, height=30, highlightthickness=0, command=framelord.switch)
# test.grid()
# framelord.grid()




# root.mainloop()