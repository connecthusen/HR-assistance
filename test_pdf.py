from utils.pdf_loader import extract_text_from_pdf
from utils.text_splitter import split_text_into_chunks

pdf_path = "data/hr_policies/leave_policy.pdf"   # change to your file

text = extract_text_from_pdf(pdf_path)
print("PDF extracted length:", len(text))

chunks = split_text_into_chunks(text)
print("Number of chunks:", len(chunks))
print(chunks[0][:300])  # preview first chunk
