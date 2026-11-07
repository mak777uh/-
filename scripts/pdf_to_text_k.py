"""Convert the Krishnamurti PDF into plain text so the whole book can be read at once.

Writes:
  <out>.txt        - full text, page markers kept
  <out>.chunks.txt - the same text split into ~40k-character chunks for reading in order
"""
import os
import re
import sys

from pypdf import PdfReader

SRC = r"C:\Users\Admin\Downloads\Krishnamurti - The Awakening of Intelligence.pdf"
OUTDIR = r"C:\Users\Admin\Documents\Qoder\2026-10-18\82ab86cd\repo\_exports"
BASE = os.path.join(OUTDIR, "k-awakening-of-intelligence")

os.makedirs(OUTDIR, exist_ok=True)
reader = PdfReader(SRC)
print("pages:", len(reader.pages))

parts = []
for i, page in enumerate(reader.pages, 1):
    try:
        t = page.extract_text() or ""
    except Exception as e:  # noqa: BLE001
        t = f"[page {i} failed: {e}]"
    parts.append(f"\n\n===== PAGE {i} =====\n\n{t}")

text = "".join(parts)
# tidy: collapse runs of blank lines and hard-wrapped hyphenation
text = re.sub(r"[ \t]+\n", "\n", text)
text = re.sub(r"\n{3,}", "\n\n", text)
text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

with open(BASE + ".txt", "w", encoding="utf-8") as fh:
    fh.write(text)

words = len(text.split())
print("chars:", len(text), "words:", words)

# chunks of ~40k chars on paragraph boundaries
CH = 40000
chunks, cur = [], ""
for para in text.split("\n\n"):
    if len(cur) + len(para) > CH and cur:
        chunks.append(cur)
        cur = ""
    cur += para + "\n\n"
if cur:
    chunks.append(cur)
with open(BASE + ".chunks.txt", "w", encoding="utf-8") as fh:
    for i, c in enumerate(chunks, 1):
        fh.write(f"\n\n########## CHUNK {i} of {len(chunks)} ##########\n\n{c}")
print("chunks:", len(chunks))
print("written:", BASE + ".txt")
