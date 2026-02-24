import easyocr
import re
import time

# Load once (takes ~2s at startup)
reader = easyocr.Reader(['ja'], gpu=False)

def is_japanese(text):
    if not text:
        return False

    # Only keep if 60%+ of the characters are Japanese and 2+ characters are Japanese
    jp_chars = re.findall(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]', text)
    ratio = len(jp_chars) / len(text) if len(text) > 0 else 0
    return len(jp_chars) >= 2 and ratio >= 0.5

def extract_japanese_text(image_np):
    start = time.time()
    results = reader.readtext(image_np)
    print(f"[OCR] Found {len(results)} total results")

    filtered = []
    for bbox, text, confidence in results:
        if is_japanese(text):
            filtered.append({
                'bbox': bbox,
                'text': text,
                'confidence': confidence,
                'translation': None
            })

    print(f"[OCR] Filtered {len(filtered)} Japanese entries")
    print(f"[OCR] Done in {time.time() - start:.2f}s")
    return filtered
