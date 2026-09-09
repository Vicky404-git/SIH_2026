from paddleocr import PaddleOCR

IMAGE_PATH = r"C:\Users\Pcm\OneDrive\Desktop\SIH2026\SIH_2026\OCR\input\handwritten.jpeg"
OUTPUT_FILE = "ocr_text.txt"

print("Loading PaddleOCR model...")

ocr = PaddleOCR(
    lang="en",
    device="cpu",
    enable_mkldnn=False,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False
)

print("Model loaded!")
print("Running OCR...")

result = ocr.predict(IMAGE_PATH)

all_text = []

for res in result:
    data = res.json

    texts = data["res"].get("rec_texts", [])

    for text in texts:
        if text.strip():
            all_text.append(text.strip())

print("\n========== EXTRACTED TEXT ==========\n")

for text in all_text:
    print(text)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(all_text))

print("\n====================================")
print("OCR completed successfully!")
print(f"Detected text lines: {len(all_text)}")
print(f"Text saved to: {OUTPUT_FILE}")