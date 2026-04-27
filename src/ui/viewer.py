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
        
        self.start_x = 0
        self.start_y = 0
        self.rect_id = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)

    def on_mouse_wheel(self, event):
        if event.state & 0x0004 or event.state & 0x0008:
            if event.delta > 0 or event.num == 4:
                self.main_win.zoom_in()
            elif event.delta < 0 or event.num == 5:
                self.main_win.zoom_out()
            return "break"
        else:
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
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='#00ff00', width=2, dash=(4,4), tags="selection")

    def on_mouse_drag(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)
        if self.rect_id:
            self.canvas.coords(self.rect_id, self.start_x, self.start_y, cur_x, cur_y)

    def on_mouse_release(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        
        engine = self.main_win.engine
        zoom = self.main_win.zoom
        page_num = self.main_win.current_page
        
        # 드래그가 짧으면 단순 클릭
        is_click = abs(end_x - self.start_x) < 5 and abs(end_y - self.start_y) < 5
        
        if is_click:
            if self.rect_id: self.canvas.delete(self.rect_id)
            if not engine or not engine.doc: return
            
            # 캔버스 좌표 -> PDF 실좌표
            pt_x = (end_x - 20) / zoom
            pt_y = (end_y - 20) / zoom
            pt = fitz.Point(pt_x, pt_y)
            
            # 1. 주석(스티커 메모) 클릭 여부 확인
            annot_text = engine.get_annotation_at(page_num, pt)
            if annot_text:
                self.show_sticky_note(annot_text)
                return
                
            # 2. 편집 모드 ON일 경우 텍스트 클릭 확인
            if getattr(self.main_win, "edit_mode", False):
                block_info = engine.get_text_block_at(page_num, pt)
                if block_info:
                    rect, text = block_info
                    self.prompt_edit_text(page_num, rect, text)
            return

        # 일반 드래그 = 텍스트 강제 추출
        if not engine or not engine.doc:
            if self.rect_id: self.canvas.delete(self.rect_id)
            return
            
        x0 = (min(self.start_x, end_x) - 20) / zoom
        y0 = (min(self.start_y, end_y) - 20) / zoom
        x1 = (max(self.start_x, end_x) - 20) / zoom
        y1 = (max(self.start_y, end_y) - 20) / zoom
        
        rect = fitz.Rect(x0, y0, x1, y1)
        
        try:
            page = engine.doc[page_num]
            text = page.get_text("text", clip=rect).strip()
            
            if text:
                self.clipboard_clear()
                self.clipboard_append(text)
                messagebox.showinfo("텍스트 드래그 추출 완료", f"지정한 영역의 텍스트가 클립보드에 복사되었다 이기:\n\n{text}")
        except Exception as e:
            print("Text extraction error:", e)
            
        if self.rect_id: self.canvas.delete(self.rect_id)

    def show_sticky_note(self, text):
        top = tk.Toplevel(self)
        top.title("스티커 메모 (Annotation)")
        top.geometry("300x200")
        top.configure(bg="#ffffcc")
        lbl = tk.Label(top, text="📝 [ 주석 내용 ]", bg="#ffffcc", font=("Malgun Gothic", 12, "bold"))
        lbl.pack(pady=10)
        txt = tk.Text(top, bg="#ffffcc", wrap=tk.WORD, font=("Malgun Gothic", 10), relief=tk.FLAT)
        txt.insert("1.0", text)
        txt.config(state=tk.DISABLED) # 읽기 전용
        txt.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
    def prompt_edit_text(self, page_num, rect, old_text):
        top = tk.Toplevel(self)
        top.title("직접 텍스트 편집 (어도비 씹어먹기 모드)")
        top.geometry("450x350")
        
        lbl = tk.Label(top, text="기존 텍스트를 파괴하고 새 진리를 덮어씌운다:", font=("Malgun Gothic", 11, "bold"))
        lbl.pack(pady=10)
        
        txt = tk.Text(top, wrap=tk.WORD, font=("Malgun Gothic", 10), height=10)
        txt.insert("1.0", old_text)
        txt.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        def apply_edit():
            new_text = txt.get("1.0", tk.END).strip()
            if new_text:
                self.main_win.engine.replace_text(page_num, rect, new_text)
                self.main_win.render_current_page()
            top.destroy()
            
        btn = ttk.Button(top, text="적용 및 원본 분쇄 (Redaction)", command=apply_edit)
        btn.pack(pady=15)

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
        
        self.canvas.config(scrollregion=(0, 0, pix.width + 40, pix.height + 40))
