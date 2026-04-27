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

    def add_sticky_note(self, page_num, text, point=(50, 50)):
        if not self.doc: return
        page = self.doc[page_num]
        annot = page.add_text_annot(point, text)
        annot.set_colors(stroke=(1, 0.8, 0)) # 노란색 계열
        annot.set_info(title="AllEdgeOfPizza", content=text)
        annot.update()

    def get_annotation_at(self, page_num, pt):
        if not self.doc: return None
        page = self.doc[page_num]
        for annot in page.annots():
            # 클릭 좌표가 아이콘 범위 내에 있는지 확인
            if annot.rect.contains(pt):
                return annot.info.get("content", "")
        return None

    def get_text_block_at(self, page_num, pt):
        if not self.doc: return None
        page = self.doc[page_num]
        blocks = page.get_text("blocks")
        for b in blocks:
            rect = fitz.Rect(b[:4])
            if rect.contains(pt) and b[6] == 0: # 0번 타입: 일반 텍스트
                return rect, b[4]
        return None

    def replace_text(self, page_num, rect, new_text):
        if not self.doc: return
        page = self.doc[page_num]
        # 원본 텍스트 분쇄 (Redaction)
        page.add_redact_annot(rect, fill=(1, 1, 1)) # 배경색(흰색)으로 덮음
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
        # 새 텍스트 우겨넣기
        page.insert_textbox(rect, new_text, fontname="cjk", fontsize=11, color=(0,0,0), align=0)

    def add_signature_text(self, page_num, name):
        if not self.doc: return
        page = self.doc[page_num]
        rect = fitz.Rect(50, 50, 300, 100)
        page.insert_textbox(rect, f"Digitally Signed by: {name}\nCertified Authentic.", fontsize=12, color=(0, 0, 0.8))

    def resave_remove_pdfa(self, out_path):
        if not self.doc: return
        self.doc.save(out_path, garbage=4, deflate=True)

    def create_blank(self):
        self.close()
        self.doc = fitz.open()
        self.doc.new_page()
        self.current_path = None
