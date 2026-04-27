import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class PDFViewer(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # 스크롤바와 캔버스 설정
        self.vbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.hbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas = tk.Canvas(self, bg='#2d2d2d', yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.vbar.config(command=self.canvas.yview)
        self.hbar.config(command=self.canvas.xview)
        
        self.image_id = None
        self.current_image = None

    def show_pixmap(self, pix):
        if not pix:
            self.canvas.delete("all")
            return
            
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        self.current_image = ImageTk.PhotoImage(img)
        
        if self.image_id:
            self.canvas.itemconfig(self.image_id, image=self.current_image)
        else:
            # 화면 중앙 혹은 좌상단 배치
            self.image_id = self.canvas.create_image(20, 20, anchor=tk.NW, image=self.current_image)
        
        # 스크롤 영역을 이미지 크기에 맞게 업데이트
        self.canvas.config(scrollregion=(0, 0, pix.width + 40, pix.height + 40))
