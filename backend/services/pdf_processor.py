# backend/services/pdf_processor.py
try:
    import fitz
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    print("PyMuPDF not available, using pdfminer.six as fallback")

import re
import os
import nltk
from concurrent.futures import ThreadPoolExecutor
from pdfminer.high_level import extract_text

nltk.data.path.append('./core_engine_data/nltk_data')

def _clean_text(text):
    text = re.sub(r'[\u2022\u25E6\u25CF\ufb00-\ufb04]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

class SectionExtractor:
    def _is_heading_by_layout(self, text: str) -> bool:
        if not text or len(text.split()) > 12 or text.strip().endswith(('.', '!', '?')): return False
        if not (text.istitle() or text.isupper()) and len(text.split()) > 1: return False
        if len(text) <= 2: return False
        return True

    def extract_from_pdf(self, pdf_path: str) -> dict:
        doc_name = os.path.basename(pdf_path)
        sections = []
        bookmarks = []
        pages = []  # Store individual page content

        try:
            if HAS_PYMUPDF:
                # Use PyMuPDF if available
                doc = fitz.open(pdf_path)

                # Extract bookmarks/table of contents
                toc = doc.get_toc()
                for item in toc:
                    level, title, page = item
                    bookmarks.append({
                        "title": title.strip(),
                        "page": page,
                        "level": level
                    })

                # Extract individual pages for page-specific queries
                for page_num, page in enumerate(doc, 1):
                    page_text = _clean_text(page.get_text())
                    if page_text.strip():
                        pages.append({
                            "page_number": page_num,
                            "content": page_text,
                            "source": doc_name,
                            "title": f"Page {page_num}"
                        })

                # Extract sections as before
                current_heading, current_content, heading_page = "Introduction", [], 1
                for page_num, page in enumerate(doc, 1):
                    for block in page.get_text("blocks"):
                        block_text = _clean_text(block[4])
                        if not block_text: continue
                        if self._is_heading_by_layout(block_text):
                            if current_content:
                                sections.append({"title": current_heading, "content": " ".join(current_content), "source": doc_name, "page": heading_page})
                            current_heading, current_content, heading_page = block_text, [], page_num
                        else:
                            current_content.append(block_text)
                if current_content:
                    sections.append({"title": current_heading, "content": " ".join(current_content), "source": doc_name, "page": heading_page})
            else:
                # Fallback to pdfminer.six
                text = extract_text(pdf_path)
                text = _clean_text(text)

                # For fallback, create a single page entry
                pages.append({
                    "page_number": 1,
                    "content": text,
                    "source": doc_name,
                    "title": "Page 1"
                })

                # Simple section splitting based on text patterns
                paragraphs = text.split('\n\n')
                current_heading = "Introduction"
                current_content = []

                for para in paragraphs:
                    para = para.strip()
                    if not para:
                        continue

                    if self._is_heading_by_layout(para):
                        if current_content:
                            sections.append({
                                "title": current_heading,
                                "content": " ".join(current_content),
                                "source": doc_name,
                                "page": 1
                            })
                        current_heading = para
                        current_content = []
                    else:
                        current_content.append(para)

                if current_content:
                    sections.append({
                        "title": current_heading,
                        "content": " ".join(current_content),
                        "source": doc_name,
                        "page": 1
                    })

        except Exception as e:
            print(f"[ERROR] Could not process {doc_name}: {e}")

        return {
            "sections": sections,
            "bookmarks": bookmarks,
            "pages": pages  # Add individual page content
        }

    def extract_parallel(self, pdf_paths: list) -> dict:
        results = {}
        with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 1)) as executor:
            future_to_path = {executor.submit(self.extract_from_pdf, path): path for path in pdf_paths}
            for future in future_to_path:
                path = future_to_path[future]
                try:
                    result = future.result()
                    results[path] = result
                except Exception as exc:
                    results[path] = {"sections": [], "bookmarks": []}
        return results

pdf_processor_service = SectionExtractor()