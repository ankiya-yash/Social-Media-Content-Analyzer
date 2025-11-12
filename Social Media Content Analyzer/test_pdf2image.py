from pdf2image import convert_from_path
pages = convert_from_path(r"C:\Lavish_Verma_Resume.pdf", dpi=150, poppler_path=r"C:\Users\lv909\Downloads\Release-25.07.0-0\poppler-25.07.0\Library\bin")

print("Pages converted:", len(pages))