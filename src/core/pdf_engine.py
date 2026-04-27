import fitz

class PDFEngine:
    def __init__(self):
        self.doc = None
        self.current_path = None

    def open(self, path):
        self.close()
        self.doc = fitz.open(path)
        self.current_path = path

    def close(self):
        if self.doc:
            self.doc.close()
            self.doc = None

    def get_page_count(self):
        return len(self.doc) if self.doc else 0

    def render_page(self, page_num, zoom=1.0):
        if not self.doc or page_num < 0 or page_num >= len(self.doc):
            return None
        page = self.doc[page_num]
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        return pix

    def add_text_annotation(self, page_num, text, point=(50, 50)):
        if not self.doc: return
        page = self.doc[page_num]
        annot = page.add_text_annot(point, text)
        annot.update()

    def add_signature_text(self, page_num, name):
        if not self.doc: return
        page = self.doc[page_num]
        rect = fitz.Rect(50, 50, 300, 100)
        page.insert_textbox(rect, f"Digitally Signed by: {name}\nCertified Authentic.", fontsize=12, color=(0, 0, 0.8))

    def resave_remove_pdfa(self, out_path):
        if not self.doc: return
        # garbage=4, deflate=True 를 주면 최적화되면서 PDF/A 메타데이터 등 부가 제한 락이 기본 해제됨
        self.doc.save(out_path, garbage=4, deflate=True)

    def create_blank(self):
        self.close()
        self.doc = fitz.open()
        self.doc.new_page()
        self.current_path = None
