import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import threading

from src.core.pdf_engine import PDFEngine
from src.ui.viewer import PDFViewer
from src.core.extract import extract_fonts
from src.core.crypto import brute_force_manager

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("All Edge Of Pizza PDF Pro - 쌉근본 우파식 어도비 대체제 (고양이민주주의)")
        self.geometry("1400x900")
        
        style = ttk.Style()
        style.configure('TButton', font=('Malgun Gothic', 10, 'bold'))
        
        self.engine = PDFEngine()
        self.current_page = 0
        self.zoom = 1.0
        
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        self.viewer = PDFViewer(self.paned_window, self)
        self.sidebar = ttk.Frame(self.paned_window, width=300, relief=tk.SUNKEN)
        
        self.paned_window.add(self.viewer, weight=4)
        self.paned_window.add(self.sidebar, weight=1)
        
        self.build_sidebar()
        
        # 키보드 바인딩 (줌 인/아웃 - 컨트롤 + / - / =)
        self.bind("<Control-plus>", lambda e: self.zoom_in())
        self.bind("<Control-equal>", lambda e: self.zoom_in())
        self.bind("<Control-minus>", lambda e: self.zoom_out())
        # 전역 마우스 휠 바인딩도 캔버스로 포워딩
        self.bind("<Control-MouseWheel>", self.viewer.on_mouse_wheel)

    def build_sidebar(self):
        ttk.Label(self.sidebar, text="🔥 PDF Command Center", font=('Malgun Gothic', 14, 'bold')).pack(pady=15)
        
        ttk.Button(self.sidebar, text="📂 기존 PDF 열기", command=self.open_pdf).pack(fill=tk.X, padx=15, pady=5)
        ttk.Button(self.sidebar, text="📄 빈 PDF 작성", command=self.new_pdf).pack(fill=tk.X, padx=15, pady=5)
        ttk.Button(self.sidebar, text="💾 현재 PDF 저장", command=self.save_pdf).pack(fill=tk.X, padx=15, pady=5)
        
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # 뷰어 컨트롤
        ttk.Label(self.sidebar, text="[ 네비게이션 ]", font=('Malgun Gothic', 10, 'bold')).pack()
        nav_frame = ttk.Frame(self.sidebar)
        nav_frame.pack(fill=tk.X, padx=15, pady=5)
        ttk.Button(nav_frame, text="◀ 이전", command=self.prev_page).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(nav_frame, text="다음 ▶", command=self.next_page).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)
        
        zoom_frame = ttk.Frame(self.sidebar)
        zoom_frame.pack(fill=tk.X, padx=15, pady=5)
        ttk.Button(zoom_frame, text="확대 (+)", command=self.zoom_in).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(zoom_frame, text="축소 (-)", command=self.zoom_out).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)
        
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # 편집 및 주석
        ttk.Label(self.sidebar, text="[ 편 집 / 주 석 ]", font=('Malgun Gothic', 10, 'bold')).pack()
        ttk.Button(self.sidebar, text="📝 메모 주석 (Annotation)", command=self.add_comment).pack(fill=tk.X, padx=15, pady=5)
        ttk.Button(self.sidebar, text="🖋 전자서명 (인증 마크 삽입)", command=self.add_signature).pack(fill=tk.X, padx=15, pady=5)
        
        ttk.Separator(self.sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        
        # PDF/A 및 보안 해제
        ttk.Label(self.sidebar, text="[ 보 안 / 최 적 화 ]", font=('Malgun Gothic', 10, 'bold')).pack()
        ttk.Button(self.sidebar, text="🔓 PDF/A 락 해제 (강제 재저장)", command=self.remove_pdfa).pack(fill=tk.X, padx=15, pady=5)
        ttk.Button(self.sidebar, text="🔠 내장 폰트 강제 적출", command=self.do_extract_fonts).pack(fill=tk.X, padx=15, pady=5)
        ttk.Button(self.sidebar, text="💣 암호 무차별대입 크랙", command=self.do_bruteforce).pack(fill=tk.X, padx=15, pady=5)

    def open_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            self.engine.open(path)
            self.current_page = 0
            self.zoom = 1.0
            self.render_current_page()

    def new_pdf(self):
        self.engine.create_blank()
        self.current_page = 0
        self.zoom = 1.0
        self.render_current_page()
        
    def save_pdf(self):
        if not self.engine.doc: return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if path:
            self.engine.doc.save(path)
            messagebox.showinfo("저장 완료", "진리의 말씀이 성공적으로 저장되었다!")
            
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.render_current_page()
            
    def next_page(self):
        if self.current_page < self.engine.get_page_count() - 1:
            self.current_page += 1
            self.render_current_page()
            
    def zoom_in(self):
        self.zoom += 0.2
        self.render_current_page()
        
    def zoom_out(self):
        if self.zoom > 0.4:
            self.zoom -= 0.2
            self.render_current_page()
            
    def render_current_page(self):
        pix = self.engine.render_page(self.current_page, self.zoom)
        self.viewer.show_pixmap(pix)
        
    def add_comment(self):
        if not self.engine.doc: return
        text = simpledialog.askstring("주석 추가", "주석 내용을 입력해라 이기:")
        if text:
            self.engine.add_text_annotation(self.current_page, text)
            self.render_current_page()
            
    def add_signature(self):
        if not self.engine.doc: return
        sig_text = simpledialog.askstring("전자서명", "서명할 이름을 입력 (본질적 우파의 인증):")
        if sig_text:
            self.engine.add_signature_text(self.current_page, sig_text)
            self.render_current_page()
            
    def remove_pdfa(self):
        if not self.engine.doc: return
        path = filedialog.asksaveasfilename(defaultextension=".pdf", title="PDF/A 해제 후 저장")
        if path:
            self.engine.resave_remove_pdfa(path)
            messagebox.showinfo("성공", "유물론적 규제(PDF/A)를 타파하고 편집 가능한 자유의 PDF로 재저장했다!")

    def do_extract_fonts(self):
        if not self.engine.doc:
            messagebox.showwarning("경고", "먼저 PDF를 열어라!")
            return
        if not self.engine.current_path:
            messagebox.showwarning("경고", "새로 만든 파일은 먼저 저장해야 폰트 추출이 가능하다 이기.")
            return
            
        out_dir = filedialog.askdirectory()
        if out_dir:
            try:
                cnt = extract_fonts(self.engine.current_path, out_dir)
                messagebox.showinfo("성공", f"폰트 {cnt}개 추출 완료!")
            except Exception as e:
                messagebox.showerror("에러", f"폰트 추출 실패: {e}")

    def do_bruteforce(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not path: return
        max_len = simpledialog.askinteger("길이", "최대 비밀번호 길이:", initialvalue=4)
        if not max_len: return
        
        messagebox.showinfo("알림", "터미널(콘솔)을 확인하면서 기다려라. 십자군 맹공격 시작!")
        threading.Thread(target=brute_force_manager, args=(path, max_len, self.on_brute_done), daemon=True).start()

    def on_brute_done(self, msg):
        self.after(0, lambda: messagebox.showinfo("결과", msg))
