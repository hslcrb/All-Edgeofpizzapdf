import fitz
import os

def extract_fonts(file_path, out_dir):
    doc = fitz.open(file_path)
    extracted_count = 0
    for i in range(len(doc)):
        for font in doc.get_page_fonts(i):
            xref = font[0]
            font_info = doc.extract_font(xref)
            ext = font_info[3]
            font_data = font_info[0]
            font_name = font_info[1]
            
            safe_font_name = "".join(x for x in font_name if x.isalnum() or x in " -_")
            save_path = os.path.join(out_dir, f"{safe_font_name}.{ext}")
            
            with open(save_path, "wb") as f:
                f.write(font_data)
            extracted_count += 1
    doc.close()
    return extracted_count
