import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import fitz

class PDFViewer(ttk.Frame):
    def __init__(self, parent, main_win):
        super().__init__(parent)
        self.main_win = main_win
        
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
        
        # 텍스트 선택(드래그) 영역 변수
        self.start_x = 0
        self.start_y = 0
        self.rect_id = None
        
        # 캔버스 이벤트 바인딩 (텍스트 추출용 드래그)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        
        # 캔버스 위에서 마우스 휠 작동
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)

    def on_mouse_wheel(self, event):
        # Ctrl 눌렀을 때 확대/축소 (Windows: state 4/8, macOS/Linux는 다를 수 있으므로 폭넓게 잡음)
        if event.state & 0x0004 or event.state & 0x0008:
            if event.delta > 0 or event.num == 4:
                self.main_win.zoom_in()
            elif event.delta < 0 or event.num == 5:
                self.main_win.zoom_out()
            return "break"
        else:
            # 일반 휠 스크롤
            if event.delta:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            elif event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    def on_mouse_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        # 선택 영역 박스 그리기
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='#00ff00', width=2, dash=(4,4), tags="selection")

    def on_mouse_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        if self.rect_id:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        # 드래그가 너무 짧으면 그냥 단순 클릭으로 간주
        if abs(end_x - self.start_x) < 5 and abs(end_y - self.start_y) < 5:
            if self.rect_id: self.canvas.delete(self.rect_id)
            return
            
        engine = self.main_win.engine
        if not engine or not engine.doc:
            if self.rect_id: self.canvas.delete(self.rect_id)
            return
            
        zoom = self.main_win.zoom
        page_num = self.main_win.current_page
        
        # 캔버스 20px 패딩 감안 및 줌 비율 계산 (화면 좌표 -> 실제 PDF 좌표)
        x0 = (min(self.start_x, end_x) - 20) / zoom
        y0 = (min(self.start_y, end_y) - 20) / zoom
        x1 = (max(self.start_x, end_x) - 20) / zoom
        y1 = (max(self.start_y, end_y) - 20) / zoom
        
        rect = fitz.Rect(x0, y0, x1, y1)
        
        try:
            page = engine.doc[page_num]
            # 지정 영역 텍스트 강제 추출 (극한의 편의성)
            text = page.get_text("text", clip=rect).strip()
            
            if text:
                self.clipboard_clear()
                self.clipboard_append(text)
                messagebox.showinfo("텍스트 드래그 추출 완료", f"지정한 영역의 텍스트가 클립보드에 복사되었다 이기:\n\n{text}")
        except Exception as e:
            print("Text extraction error:", e)
            
        # 선택 후 초록색 박스 지우기
        if self.rect_id: self.canvas.delete(self.rect_id)

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
            self.image_id = self.canvas.create_image(20, 20, anchor=tk.NW, image=self.current_image)
        
        # 스크롤 영역을 이미지 크기에 맞게 확실하게 업데이트
        self.canvas.config(scrollregion=(0, 0, pix.width + 40, pix.height + 40))
