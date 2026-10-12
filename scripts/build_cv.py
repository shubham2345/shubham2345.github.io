"""Build the public CV from the source resume.

Removes the phone number and rebuilds the contact line so no gap is left
behind. The line is redrawn in Helvetica -- the base-14 font that Nimbus Sans,
the resume's own face, is a clone of, so the metrics match the untouched lines
around it while the text stays selectable and searchable. (Re-embedding the
resume's subsetted Type1 font was tried first: it has no `space` glyph, so the
rebuilt line extracted as "Santa\x00Clara".) The bullet separator is drawn as a
circle measured off the links line below, because Helvetica's own bullet sits
differently from the one the rest of the document uses.
"""
import fitz

SRC, OUT = "Shubham_phd_intern_27_resume.pdf", "assets/cv/Shubham_Gaur_CV.pdf"
PHONE = "(408) 640-5717"
LINE = fitz.Rect(182, 37.8, 430, 49.4)   # contact line, between the name and the links
BASELINE, SIZE, FONT = 45.95, 8.47, "helv"
BLACK, BLUE = (0, 0, 0), (26 / 255, 59 / 255, 221 / 255)
DOT_R, DOT_RISE, DOT_GAP = 1.05, 2.39, 3.8   # measured off the links line below
LOCATION, EMAIL = "Santa Clara, CA, USA", "gshubhaur@gmail.com"

doc = fitz.open(SRC)
page = doc[0]
assert any(p.search_for(PHONE) for p in doc), "phone number not found in source"

page.add_redact_annot(LINE, fill=(1, 1, 1))
for other in doc:
    if other is not page:
        for rect in other.search_for(PHONE):
            other.add_redact_annot(rect, fill=(1, 1, 1))
for p in doc:
    p.apply_redactions()

w_loc = fitz.get_text_length(LOCATION, FONT, SIZE)
w_email = fitz.get_text_length(EMAIL, FONT, SIZE)
x = (page.rect.width - (w_loc + 2 * DOT_GAP + w_email)) / 2
x_dot = x + w_loc + DOT_GAP
x_email = x_dot + DOT_GAP

page.insert_text((x, BASELINE), LOCATION, fontname=FONT, fontsize=SIZE, color=BLACK)
page.draw_circle((x_dot, BASELINE - DOT_RISE), DOT_R, color=BLACK, fill=BLACK, width=0)
page.insert_text((x_email, BASELINE), EMAIL, fontname=FONT, fontsize=SIZE, color=BLUE)
page.insert_link({
    "kind": fitz.LINK_URI,
    "from": fitz.Rect(x_email, LINE.y0, x_email + w_email, LINE.y1),
    "uri": f"mailto:{EMAIL}",
})

doc.save(OUT, garbage=4, deflate=True)
print("wrote", OUT)
