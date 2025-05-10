import tkinter as tk
import customtkinter as ctk

class TitleBar(tk.Frame):
    def __init__(self, root, width=1920, height=40, bg='#181818', **kwargs):
        super().__init__(root, width=width, height=height, bg=bg, **kwargs)
        
        self.root = root
        padding = 3
        
        buttonStyle = {
            'fg_color'      : bg,
            'bg_color'      : bg,
            'border_width'  : 0,
            'font'          : ("", 13, 'bold'),
            'anchor'        :'center', 
            'height'        : height, 
            'width'         : height,
        }
        
        closeButton = ctk.CTkButton(self, text="✕", command=root.destroy, hover_color='red', **buttonStyle)
        closeButton.pack(side='right', padx=padding)

        maxButton = ctk.CTkButton(self, text="\u2610", command=self.toggleMax, hover_color='gray', **buttonStyle)
        maxButton.pack(side='right', padx=padding)

        minButton = ctk.CTkButton(self, text="\uFF0D", command=self.toggleMin, hover_color='gray', **buttonStyle)
        minButton.pack(side='right', padx=padding)
        
        self.setupDrag()

    def setupDrag(self):
        self.bind("<ButtonPress-1>", self.moveStart)
        self.bind("<ButtonRelease-1>", self.moveStop)
        self.bind("<B1-Motion>", self.move)

    def moveStart(self, event):
        self.x = event.x
        self.y = event.y

    def moveStop(self, event):
        self.x = None
        self.y = None

    def move(self, event):
        x = self.winfo_pointerx() - self.x
        y = self.winfo_pointery() - self.y
        self.root.geometry(f"+{x}+{y}")

    def toggleMax(self):
        if self.root.state() != 'zoomed':
            self.root.state('zoomed')
        else:
            self.root.state('normal')
            
    def toggleMin(self):
        self.root.iconify()



