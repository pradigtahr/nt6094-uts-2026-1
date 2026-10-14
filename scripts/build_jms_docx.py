"""Build the midterm answer sheet as a Journal of Materials Science (Springer) submission manuscript.

Follows https://link.springer.com/journal/10853/submission-guidelines: title page, structured abstract
(150-250 words), 4-6 keywords, decimal headings, Word equations, "Fig. n" captions, numbered references
in citation order, Statements and Declarations, Online Resource (ESM) appended.
"""
import json, os, re, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement, parse_xml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
D = json.load(open(os.path.join(ROOT, "data", "datasets.json")))
KEYS = sorted(R, key=lambda k: int(k[1:3]))
# --midterm: same JMS content, laid out with the course answer-sheet header (06_midterm_nt6094.pdf)
MIDTERM = "--midterm" in sys.argv
OUT = os.path.join(ROOT, "UTS-NT6094-PradigtaHR-28726019-" + ("midterm" if MIDTERM else "JMS") + ".docx")
FONT = "Aptos" if MIDTERM else "Times New Roman"
TEXT_W = 16.0  # cm, A4 with 2.5 cm margins

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = sec.top_margin = sec.bottom_margin = Cm(2.5)

normal = doc.styles["Normal"]
normal.font.name = FONT
normal.font.size = Pt(11)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.5
for name, size in (("Heading 1", 12), ("Heading 2", 11), ("Heading 3", 11)):
    h = doc.styles[name]
    h.font.name, h.font.size, h.font.bold = FONT, Pt(size), True
    h.font.italic = name == "Heading 3"
    h.font.color.rgb = RGBColor(0, 0, 0)
    rf = h.element.rPr.rFonts
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        if rf.get(qn(a)) is not None:
            del rf.attrib[qn(a)]
    rf.set(qn("w:ascii"), FONT); rf.set(qn("w:hAnsi"), FONT)
    h.paragraph_format.space_before = Pt(12)
    h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.line_spacing = 1.15

# page number in footer (automatic page numbering)
fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
for tag, text in (("begin", None), (None, "PAGE"), ("end", None)):
    r = fp.add_run()
    if tag:
        el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), tag)
    else:
        el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = text
    r._r.append(el)

# ------------------------------------------------------------------ text helpers
def add_runs(p, text, bold=False, italic=False, size=None):
    """Mini markup: **bold**, *italic*, _{sub}, ^{sup}."""
    for t in re.split(r"(\*\*.+?\*\*|\*.+?\*|_\{.+?\}|\^\{.+?\})", text):
        if not t:
            continue
        b, i, sub, sup = bold, italic, False, False
        if t.startswith("**"):
            t, b = t[2:-2], True
        elif t.startswith("*"):
            t, i = t[1:-1], True
        elif t.startswith("_{"):
            t, sub = t[2:-1], True
        elif t.startswith("^{"):
            t, sup = t[2:-1], True
        r = p.add_run(t)
        r.bold, r.italic = b, i
        r.font.subscript, r.font.superscript = sub, sup
        if size:
            r.font.size = Pt(size)
    return p


VAR = re.compile(r"(?<![\w*.\-{])([xygmbnr](?![A-Za-z0-9*])|R(?=²))")


def ital(text):
    """Italicise single-letter variables (JMS: italic variables), outside **bold** run-in headings."""
    parts = re.split(r"(\*\*.+?\*\*|https?://\S+)", text)
    return "".join(t if t.startswith(("**", "http")) else VAR.sub(r"*\1*", t) for t in parts)


def para(text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=None, bold=False, after=None, spacing=None,
         italic_vars=True):
    p = doc.add_paragraph()
    p.alignment = align
    add_runs(p, ital(text) if italic_vars else text, bold=bold, size=size)
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    if spacing:
        p.paragraph_format.line_spacing = spacing
    return p


def head(text, level):
    return doc.add_heading(text, level=level)


def bullet(text):
    p = doc.add_paragraph(style="List Bullet")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_runs(p, ital(text))
    p.paragraph_format.space_after = Pt(3)


# ------------------------------------------------------------------ citations (numbered in order of first use)
REFS = {
    "midterm": "S. Viridi, 2026-1 midterm-datasets. endap (2026). https://endap.github.io/26j76/. Accessed 14 Oct 2026",
    "posts": "S. Viridi, g40s1-data, g42s3-data, g44s3 data, g46s4-data, g48s2 data, g50s3-data, g52s3-data, "
             "g54s4-data, g56s3-data, g58s1-data. endap (2026). https://endap.github.io/26j34/ (also 26j40, 26j44, "
             "26j49, 26j51, 26j56, 26j60, 26j65, 26j68, 26j70). Accessed 14 Oct 2026",
    "p2mi": "S. Viridi, p2mi-wd data. endap (2026). https://endap.github.io/26j27/. Accessed 14 Oct 2026",
    "preproc": "S. Viridi, pre-proc p2mi-wd yessi-data. endap (2026). https://endap.github.io/26j26/. Accessed 14 Oct 2026",
    "viz": "S. Viridi, compression-test viz. endap (2026). https://endap.github.io/26j32/. Accessed 14 Oct 2026",
    "callister": "W.D. Callister Jr., D.G. Rethwisch, *Materials Science and Engineering: An Introduction*, 10th edn. "
                 "(Wiley, Hoboken, 2018)",
    "astm": "ASTM International, ASTM D695-15: Standard Test Method for Compressive Properties of Rigid Plastics "
            "(ASTM International, West Conshohocken, 2015). https://doi.org/10.1520/D0695-15",
    "treible": "L. Treible, M. Szulczewski, How do I calculate a linear regression? Finding relationships between "
               "variables in the Earth sciences. Math You Need – Majors (2023). https://serc.carleton.edu/277935. "
               "Accessed 14 Oct 2026",
    "r2": "M. Gupta, R squared | coefficient of determination. GeeksforGeeks (2026). "
          "https://www.geeksforgeeks.org/maths/r-squared/. Accessed 14 Oct 2026",
    "mermaid": "S. Viridi, mermaid diagram hands-on. endap (2026). https://endap.github.io/26i75/. Accessed 14 Oct 2026",
    "claude": "Anthropic, Claude Code (model Claude Opus 5.5), chat log “NT6094 midterm (UTS) 2026-1: processing the "
              "datasets of seed 28726019” (2026). https://github.com/pradigtahr/nt6094-uts-2026-1/blob/main/ai-chat/claude-code-chat-log.md. Accessed 14 Oct 2026",
}
ORDER = []


def c(*keys):
    """Return citation text like [1] or [1, 2]; numbers assigned on first use."""
    nums = []
    for k in keys:
        if k not in ORDER:
            ORDER.append(k)
        nums.append(ORDER.index(k) + 1)
    nums.sort()
    if len(nums) > 2 and nums == list(range(nums[0], nums[-1] + 1)):
        return f"[{nums[0]}–{nums[-1]}]"
    return "[" + ", ".join(map(str, nums)) + "]"


# ------------------------------------------------------------------ figures and tables
fig_n, tab_n, eq_n = [0], [0], [0]
FIGS = {}


def fig_ref(key):
    return f"Fig. {FIGS[key]}"


def reserve_fig(key):
    fig_n[0] += 1
    FIGS[key] = fig_n[0]


def figure(key, path, caption, width_cm):
    assert not caption.rstrip().endswith("."), "JMS: no punctuation at end of figure caption"
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(path, width=Cm(width_cm))
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    cp.paragraph_format.line_spacing = 1.15
    add_runs(cp, f"**Fig. {FIGS[key]}** " + ital(caption), size=10)
    cp.paragraph_format.space_after = Pt(10)


def shade(cell, fill):
    pr = cell._tc.get_or_add_tcPr()
    s = OxmlElement("w:shd"); s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), fill)
    pr.append(s)


def table(header, rows, caption, widths, footnotes=(), size=9):
    tab_n[0] += 1
    cp = doc.add_paragraph()
    cp.paragraph_format.keep_with_next = True
    cp.paragraph_format.line_spacing = 1.15
    add_runs(cp, f"**Table {tab_n[0]}** " + caption, size=10)
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate([header] + rows):
        for j, v in enumerate(row):
            cell = t.rows[i].cells[j]
            cell.width = Cm(widths[j])
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(1)
            add_runs(p, str(v), bold=(i == 0), size=size)
            if i == 0:
                shade(cell, "E7E7E7")
            if i < len(rows) or footnotes:
                p.paragraph_format.keep_with_next = True
    for f in footnotes:
        fp = doc.add_paragraph()
        fp.paragraph_format.line_spacing = 1.0
        fp.paragraph_format.space_after = Pt(1)
        fp.paragraph_format.keep_with_next = f is not footnotes[-1]
        add_runs(fp, f, size=9)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return tab_n[0]


# ------------------------------------------------------------------ Word equations (OMML)
M = 'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"'
def mr(t): return f"<m:r><m:t xml:space=\"preserve\">{t}</m:t></m:r>"
def mfrac(n, d): return f"<m:f><m:num>{n}</m:num><m:den>{d}</m:den></m:f>"
def msup(e, s): return f"<m:sSup><m:e>{e}</m:e><m:sup>{s}</m:sup></m:sSup>"
def msub(e, s): return f"<m:sSub><m:e>{e}</m:e><m:sub>{s}</m:sub></m:sSub>"
def mpar(e, beg="(", end=")"):
    return (f"<m:d><m:dPr><m:begChr m:val=\"{beg}\"/><m:endChr m:val=\"{end}\"/></m:dPr>"
            f"<m:e>{e}</m:e></m:d>")
def msum(e):
    return ("<m:nary><m:naryPr><m:chr m:val=\"∑\"/><m:limLoc m:val=\"undOvr\"/><m:subHide m:val=\"1\"/>"
            f"<m:supHide m:val=\"1\"/></m:naryPr><m:sub/><m:sup/><m:e>{e}</m:e></m:nary>")


def equation(omml, label):
    eq_n[0] += 1
    p = doc.add_paragraph()
    p.paragraph_format.tab_stops.add_tab_stop(Cm(TEXT_W / 2), WD_TAB_ALIGNMENT.CENTER)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(TEXT_W), WD_TAB_ALIGNMENT.RIGHT)
    p.add_run("\t")
    p._p.append(parse_xml(f"<m:oMath {M}>{omml}</m:oMath>"))
    p.add_run(f"\t({eq_n[0]})")
    return eq_n[0]


# ================================================================== TITLE PAGE
r40, r44, r58 = R["g40s1"], R["g44s3"], R["g58s1"]
if MIDTERM:
    # course header: ITB logo left, course / Midterm / schedule right (as in 06_midterm_nt6094.pdf)
    hdr = doc.add_table(rows=1, cols=2)
    lc, rc = hdr.rows[0].cells
    lc.width, rc.width = Cm(4.3), Cm(11.7)
    lp = lc.paragraphs[0]
    lp.paragraph_format.line_spacing = 1.0
    lp.add_run().add_picture(os.path.join(FIG, "itb_logo.png"), width=Cm(3.9))
    for i, (txt, size, after) in enumerate([("NT6094 Scientific Journal Writing", 16, 0), ("Midterm", 26, 2),
                                            ("Wd, 14 Oct 2026 | 9310 | 09:00–11:00 (2 hours)", 14, 3),
                                            ("Note: Open book, internet, discussion", 12, 0),
                                            ("Platform: Edunex, GitHub", 12, 0)]):
        q = rc.paragraphs[0] if i == 0 else rc.add_paragraph()
        q.paragraph_format.line_spacing = 1.0
        q.paragraph_format.space_after = Pt(after)
        r = q.add_run(txt); r.bold = True; r.font.size = Pt(size)
    rc.paragraphs[0].paragraph_format.space_before = Pt(10)
    para("Refer to https://github.com/dudung/26h67/issues/62 for the instructions.",
         align=WD_ALIGN_PARAGRAPH.LEFT, size=12, after=6, italic_vars=False).paragraph_format.space_before = Pt(10)
    idt = doc.add_table(rows=4, cols=2)
    idt.style = "Table Grid"
    for i, (k, v) in enumerate([("Name", "Pradigta Hisyam Ramadhan"), ("Student ID", "28726019"),
                                ("Midterm date", "Wednesday, 14 October 2026"),
                                ("Seed / datasets", "28726019 → g40s1, g42s3, g44s3, g46s4, g48s2, g50s3, g52s3, "
                                                    "g54s4, g56s3, g58s1")]):
        idt.rows[i].cells[0].width, idt.rows[i].cells[1].width = Cm(3.6), Cm(12.4)
        for j, txt in enumerate((k, v)):
            q = idt.rows[i].cells[j].paragraphs[0]
            q.paragraph_format.line_spacing = 1.1
            q.paragraph_format.space_after = Pt(2)
            add_runs(q, txt, bold=(j == 0), size=11)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
else:
    para("Original research article — Journal of Materials Science (manuscript)", align=WD_ALIGN_PARAGRAPH.LEFT,
         size=10, after=12)
para("Composition dependence of peak load and stiffness extracted from ten compression-test curves",
     align=WD_ALIGN_PARAGRAPH.LEFT, size=16, bold=True, after=12, spacing=1.15, italic_vars=False)
para("Pradigta Hisyam Ramadhan^{1,*}", align=WD_ALIGN_PARAGRAPH.LEFT, size=12, after=8, italic_vars=False)
para("^{1} Nanotechnology Study Program, The Graduate School of Multidisciplinary Science and Technology, "
     "Institut Teknologi Bandung, Jl. Ganesha 10, Bandung 40132, Indonesia",
     align=WD_ALIGN_PARAGRAPH.LEFT, size=10, after=2, italic_vars=False)
para("^{*} Corresponding author: 28726019@mahasiswa.itb.ac.id", align=WD_ALIGN_PARAGRAPH.LEFT, size=10, after=12, italic_vars=False)
info = [("Student ID (NIM)", "28726019"),
        ("Midterm date", "14 October 2026"),
        ("Course", "NT6094 Teknik Penulisan Jurnal Ilmiah, 2026-1 midterm examination (UTS)"),
        ("Seed and datasets", "28726019 → g40s1, g42s3, g44s3, g46s4, g48s2, g50s3, g52s3, g54s4, g56s3, g58s1"),
        ("Template", "Journal of Materials Science submission guidelines (Springer Nature)")]
if MIDTERM:
    info = [("Format", "Course answer sheet (06_midterm_nt6094) with content structured after the Journal of "
                       "Materials Science submission guidelines (Springer Nature)")]
t = doc.add_table(rows=len(info), cols=2)
for i, (k, v) in enumerate(info):
    t.rows[i].cells[0].width, t.rows[i].cells[1].width = Cm(4.2), Cm(11.8)
    for j, s in enumerate((k, v)):
        p = t.rows[i].cells[j].paragraphs[0]
        p.paragraph_format.line_spacing = 1.1
        p.paragraph_format.space_after = Pt(2)
        add_runs(p, s, bold=(j == 0), size=10)
doc.add_paragraph()
head("Acknowledgements", 1)
para("The author thanks Sparisoma Viridi for providing the datasets and the endap web applications used in "
     "this work.")

# ================================================================== ABSTRACT
doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
ABSTRACT = [
    ("Purpose", "Ten load–displacement-type curves from the endap 2026-1 midterm collection, selected with the "
     "seed 28726019, were analysed to find how their main features depend on the composition parameter g."),
    ("Methods", "Each dataset was processed in the web application published with it. The peak (maximum y), the "
     "last point (largest x) and a least-squares line y = mx + b over the linear region were extracted. One rule "
     "defined the linear region for all datasets: points on the rising branch between 25 % and 75 % of the peak "
     "y. All values were reproduced with an independent Python script."),
    ("Results", f"All fits gave R² ≥ 0.987, and application and script agreed to all printed digits. The peak y "
     f"fell from {r44['ypeak']:.0f} at g = 44 to {r58['ypeak']:.0f} at g = 58 and the slope m from "
     f"{r40['m']:.0f} at g = 40 to {r58['m']:.0f} at g = 58, about 25–28 % per increase of g by 2 (Pearson "
     "r ≈ −0.89). The x position of the peak and the intercept b were dominated by an initial seating (toe) "
     "region of variable length."),
    ("Conclusion", "The datasets are best read as compression tests in which x is displacement, y is load, m is "
     "specimen stiffness and g is the percentage of one constituent in the mixture; more of this constituent "
     "gives weaker and softer specimens."),
]
words = sum(len((h + " " + t).split()) for h, t in ABSTRACT)
assert 150 <= words <= 250, f"abstract has {words} words"
head("Abstract", 1)
for h, txt in ABSTRACT:
    para(f"**{h}** " + txt)
KEYWORDS = ["Compression test", "Load–displacement curve", "Linear regression", "Stiffness",
            "Composition dependence", "Feature extraction"]
assert 4 <= len(KEYWORDS) <= 6
para("**Keywords** " + " · ".join(KEYWORDS), align=WD_ALIGN_PARAGRAPH.LEFT, italic_vars=False)

# ================================================================== 1 INTRODUCTION
head("1 Introduction", 1)
para("A compression test loads a specimen between two plates and records the load against the displacement of "
     "the plates. The resulting curve normally starts with a non-linear toe while the plates seat on the "
     "specimen, continues with a linear part whose slope gives the stiffness, and ends at a maximum load where "
     f"the specimen fails {c('callister', 'astm')}. Reading these features from many curves is a routine step "
     "when a material is optimised by changing its composition.")
para(f"The 2026-1 midterm of the course NT6094 gives every student ten datasets chosen by the student ID used "
     f"as a seed {c('midterm')}. A dataset name such as g82s9 encodes g = 82 and s = 9, and each dataset is "
     f"published as its own post with an application that plots the data, lets the user mark four points by "
     f"their id and fits a straight line {c('posts')}. The datasets come from a collection called *p2mi-wd "
     f"data* {c('p2mi')}. Its pre-processing note lists ten compositions g40 to g58 with three constituents g, e "
     f"and h that always add up to t = 12.0, with h = e/2 and g = (code/100) × 12 {c('preproc')}. The same note "
     "reports 40 curves in ten clusters, i.e. four specimens per composition. The application itself was "
     f"developed in a post titled *compression-test viz* {c('viz')}.")
para("This work extracts the peak, the last point and the linear-region slope m and intercept b from the ten "
     "curves assigned to seed 28726019, reports them as functions of g, and discusses what the variables x, y "
     "and g most likely represent.")

# ================================================================== 2 METHODS
head("2 Materials and methods", 1)
head("2.1 Datasets", 2)
reserve_fig("seed")
para(f"The midterm page was opened and the seed 28726019 was selected; the application then lists the dataset "
     f"names and the links to their posts ({fig_ref('seed')}). Each link was opened in a new browser tab and the "
     "post title was checked against the dataset name. All ten titles matched (Table 1). In every post the raw "
     "data are two columns; the application uses the second column as the independent variable x and the first "
     "column as the dependent variable y.")
figure("seed", os.path.join(FIG, "app_00_seed.png"),
       "Midterm application with seed 28726019 selected, listing the ten dataset names (data) and the posts "
       "that hold them (link)", 15.0)
rows = [[k, k[1:3], k[4:], D[k]["link"], D[k]["title"], D[k]["n"], D[k]["every"], len(D[k]["ds"])] for k in KEYS]
table(["Dataset", "g", "s", "Link", "Post title", "Rows", "Step^{a}", "Points^{b}"], rows,
      "Datasets assigned to seed 28726019",
      [1.7, 1.0, 0.8, 1.6, 3.0, 1.5, 1.4, 1.6],
      ["^{a} Sampling step of the application: every *n*-th raw row is kept",
       "^{b} Number of sampled points that can be addressed by an id"])

head("2.2 Feature-extraction application", 2)
para("The application has a chart, a console listing every sampled point with its id (0000, 0001, …) and its "
     f"original row, and an input/output panel with four buttons {c('posts')}. **load** writes default values "
     "for four keys: PEAK-ID (point of maximum y), LAST-ID (point of largest x), LINI-ID and LINF-ID (first and "
     "last point of the linear regression). After the ids are edited, **read** marks the four points on the "
     "chart so that the choice can be checked visually, and **calc** fits a straight line to all points from "
     "LINI-ID to LINF-ID and prints m, b and R². **clear** resets the panel. The sampling step differs between "
     "posts (Table 1), so the same physical point has a different id on different pages.")

head("2.3 Linear model", 2)
para(f"The linear part of each curve is described by {c('viz', 'treible')}")
X, Y, N = mr("x"), mr("y"), mr("n")
SX, SY, SXY = msum(X), msum(Y), msum(mr("xy"))
SX2, SY2 = msum(msup(X, mr("2"))), msum(msup(Y, mr("2")))
equation(mr("y=mx+b"), 1)
para("where the least-squares slope and intercept over the n selected points are", after=2)
equation(mr("m=") + mfrac(N + SXY + mr("−") + SX + SY, N + SX2 + mr("−") + msup(mpar(SX), mr("2"))), 2)
equation(mr("b=") + mfrac(SY + mr("−m") + SX, N), 3)
para(f"and the coefficient of determination is {c('r2')}", after=2)
equation(msup(mr("R"), mr("2")) + mr("=") +
         mfrac(msup(mpar(N + SXY + mr("−") + SX + SY), mr("2")),
               mpar(N + SX2 + mr("−") + msup(mpar(SX), mr("2")), "[", "]") +
               mpar(N + SY2 + mr("−") + msup(mpar(SY), mr("2")), "[", "]")), 4)
para("R² close to 1 means that the selected points lie close to a straight line. The intercept of the fitted "
     "line with the x axis,", after=2)
equation(msub(mr("x"), mr("0")) + mr("=−") + mfrac(mr("b"), mr("m")), 5)
para("marks where the linear loading would start without the toe and is used to compare deformation between "
     "tests.")

head("2.4 Selection of points", 2)
para("To make the ten results comparable, one rule replaced the choice by eye. PEAK-ID is the id with the "
     "largest y; LAST-ID is the last id; LINI-ID is the first id on the rising branch with y ≥ 0.25 y_{peak}; "
     "LINF-ID is the last id before the peak with y ≤ 0.75 y_{peak}. The band avoids the curved toe and the "
     "rounding near the maximum. Bands of 10–90 %, 20–80 % and 30–70 % changed m by only a few per cent and "
     "did not change the trend with g. The ids (Table 2) were entered in each application and checked after "
     "**read**; screenshots of all ten applications after **calc** are given in Online Resource 1.")
rows = [[k[1:3], k, f"{R[k]['peak']:04d}", f"{R[k]['last']:04d}", f"{R[k]['lini']:04d}",
         f"{R[k]['linf']:04d}", R[k]["linf"] - R[k]["lini"] + 1] for k in KEYS]
table(["g", "Dataset", "PEAK-ID", "LAST-ID", "LINI-ID", "LINF-ID", "n"], rows,
      "Point ids entered in the application for each dataset",
      [1.0, 1.8, 1.8, 1.8, 1.8, 1.8, 1.2], ["n: number of points used in the regression"])

head("2.5 Verification and workflow", 2)
reserve_fig("flow")
para("The raw data of all ten posts were processed again with a Python script that copies the sampling of the "
     "application and Eqs. (2)–(4). The values of m, b and R² from the application and from the script agree "
     f"to all printed digits for every dataset. The whole workflow is summarised in {fig_ref('flow')}; it is "
     f"drawn in Mermaid with on-page connectors {c('mermaid')}, and its source code is listed in Online "
     "Resource 1.")
figure("flow", os.path.join(FIG, "flowchart.png"),
       "Workflow from the student ID (seed) to the manuscript. Green circles are on-page connectors", 12.0)

head("2.6 Use of generative AI", 2)
para(f"A large language model tool, Claude Code with the model Claude Opus 5.5 (Anthropic) {c('claude')}, "
     "was used on 14 October 2026 to read the assignment, download the dataset posts, write the scripts that "
     "reproduce the application, propose the point-selection rule, operate the applications in the browser for "
     "the screenshots, draw the figures and the flowchart, draft the text, and prepare the public "
     "repository with the exported chat log. The author selected the datasets "
     "with the author's own student ID, checked the application output against the script output, and reviewed the "
     "interpretation, and takes full responsibility for the content. The tool is not an author.")

# ================================================================== 3 RESULTS
head("3 Results and discussion", 1)
head("3.1 Shape of the curves", 2)
reserve_fig("all"); reserve_fig("fits")
drop44 = 100 * (r44["ypeak"] - r44["ylast"]) / r44["ypeak"]
para(f"All ten curves have the same three parts ({fig_ref('all')} and {fig_ref('fits')}): a flat toe in which "
     "y stays close to zero while x increases, a long and almost straight rise, and a rounded top that ends at "
     f"the maximum, after which y drops by 1.7–12 % until the last point (largest for g44s3, {drop44:.0f} %). "
     "The length of the toe differs strongly between tests (x_{0} from 0.59 to 3.82) and does not follow g, "
     f"which is typical of the seating stage of a compression test {c('astm')}. g44s3 shows a sudden fall of y "
     "at x ≈ 3.65 before the main rise, which looks like slipping or re-seating of the specimen. The curves with "
     "g ≥ 48 carry a regular small ripple; this is why g52s3 and g56s3 have the lowest R² (0.988 and 0.990), "
     "although the fitted lines still follow the data well.")
figure("all", os.path.join(FIG, "jms_fig_all_curves.png"),
       "Raw curves y(x) of the ten datasets; darker lines belong to larger g and each label marks the peak", TEXT_W)
figure("fits", os.path.join(FIG, "jms_fig_fits.png"),
       "Sampled points of each dataset (a–j) with the points used in the regression, the fitted line y = mx + b, "
       "the peak and the last point", TEXT_W)

head("3.2 Extracted features as functions of g", 2)
reserve_fig("feat")
para(f"Table 3 lists peak, last point, m, b and R² for the ten datasets, and {fig_ref('feat')} plots them "
     "against g.")
rows = [[k[1:3], k, f"{R[k]['xpeak']:.4f}", f"{R[k]['ypeak']:.2f}", f"{R[k]['xlast']:.4f}",
         f"{R[k]['ylast']:.2f}", f"{R[k]['m']:.2f}", f"{R[k]['b']:.2f}", f"{R[k]['R2']:.5f}"] for k in KEYS]
table(["g", "Dataset", "x_{peak}", "y_{peak}", "x_{last}", "y_{last}", "m", "b", "R²"], rows,
      "Peak, last point and linear-regression parameters as functions of g",
      [0.9, 1.6, 1.6, 1.7, 1.6, 1.7, 1.9, 2.1, 1.7],
      ["Values are those printed by the application; units are not given in the source "
       "(probably mm for x and N for y, see Sect. 3.3)"])
figure("feat", os.path.join(FIG, "jms_fig_features_vs_g.png"),
       "Extracted features versus g: a y of the peak and of the last point, b x of the peak and of the last "
       "point, c slope m, d intercept b", TEXT_W)
para(f"**Peak and last point.** y_{{peak}} is largest at g = 44 ({r44['ypeak']:.0f}) and falls to "
     f"{r58['ypeak']:.0f} at g = 58 ({fig_ref('feat')}a). A log-linear fit gives a decrease of about 25 % per "
     "increase of g by 2, and the Pearson correlation between g and y_{peak} is −0.89. The last point follows "
     "the peak closely, so both describe the same property: the largest load the specimen can carry.")
para(f"**Slope.** m falls from {r40['m']:.0f} at g = 40 to about 400 at g = 56–58 ({fig_ref('feat')}c), "
     "about 28 % per increase of g by 2 (r = −0.89). Specimens with more g are therefore both weaker and "
     "softer. g46s4 and g52s3 lie above the smooth trend; both have the shortest curves and short toes. With "
     "one specimen per composition, scatter between specimens cannot be separated from the effect of g.")
para(f"**Intercept and x positions.** b is negative for all datasets and approaches zero as g increases "
     f"({fig_ref('feat')}d, r = +0.85). Because b = −m x_{{0}}, its trend mostly mirrors the fall of m and the "
     f"random toe length. For the same reason x_{{peak}} and x_{{last}} jump between 1.3 and 5.8 without a "
     f"trend ({fig_ref('feat')}b). The deformation after the toe, x_{{peak}} − x_{{0}}, is 0.66–2.54 and tends "
     "to be larger at high g, which agrees with a softer and more ductile material.")

head("3.3 Meaning of x, y and g", 2)
bullet("*x* is most likely the displacement of the loading plate (crosshead), probably in mm. It increases "
       "steadily, it is the independent variable, it contains a seating toe, and its range (0–6) fits the "
       "shortening of a small specimen.")
bullet("*y* is most likely the compressive load, probably in N. It rises with x, reaches a maximum and drops "
       "when the specimen starts to fail, so y_{peak} is the failure load and m = dy/dx the specimen stiffness "
       f"in N mm^{{−1}}. With the specimen geometry they would give the compressive strength and modulus {c('callister')}.")
bullet("*g* is the share of one constituent in the mixture in per cent: g = (code/100) × 12 for a fixed total "
       f"of 12.0 (e.g. grams), with the other two constituents in a 2 : 1 ratio {c('preproc')}. Because more g "
       "lowers both strength and stiffness, this constituent is probably a weaker or softer phase; the material "
       "is not stated in the sources.")
bullet("*s* is the specimen (replicate) number within one composition, from 1 to 4.")
para("These meanings are interpretations of the data and of the source notes, not confirmed facts.")

head("3.4 Limitations", 2)
para("Only one specimen per composition was analysed, so scatter between specimens is unknown. The application "
     "works on sampled points, so the sampled peak can be slightly below the raw peak (g42s3: 6287 raw versus "
     "6286 sampled). The 25–75 % band is a convention. Without specimen dimensions m is a stiffness, not a "
     "modulus.")

# ================================================================== 4 CONCLUSIONS
head("4 Conclusions", 1)
para("Ten datasets assigned to seed 28726019 were processed in the endap application with one rule for the "
     "linear region, and an independent script reproduced every value. All curves are compression loading "
     "curves with a toe, a linear rise (R² ≥ 0.987), a maximum and a small drop. Peak load and stiffness m "
     "both decrease strongly with g (r ≈ −0.89; about 25–28 % per increase of g by 2), so more of constituent g "
     "gives weaker and softer specimens. The x positions and b are dominated by the seating toe and should be "
     "corrected by x_{0} before deformation is compared. Repeated specimens and the specimen geometry are "
     "needed to turn these features into material properties with uncertainties.")

# ================================================================== STATEMENTS AND DECLARATIONS
head("Statements and Declarations", 1)
for h, txt in [
    ("Funding", "No funding was received to assist with the preparation of this manuscript."),
    ("Competing interests", "The author has no relevant financial or non-financial interests to disclose."),
    ("Author contributions", "P.H. Ramadhan processed and analysed the data and wrote the manuscript."),
    ("Data availability", f"The datasets analysed are publicly available on endap {c('posts')}. The extracted "
     "values, the scripts, the figures and the AI chat log are available at https://github.com/pradigtahr/nt6094-uts-2026-1; the application "
     "screenshots are given in Online Resource 1."),
    ("Ethics approval", "Not applicable."),
    ("Use of generative AI", "A large language model tool was used as described in Sect. 2.6. It is not an "
     "author, and the author is accountable for the content."),
]:
    para(f"**{h}** " + txt)

# ================================================================== REFERENCES
head("References", 1)
for i, k in enumerate(ORDER, 1):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.9)
    p.paragraph_format.first_line_indent = Cm(-0.9)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(3)
    add_runs(p, f"{i}.\t" + REFS[k], size=10)
assert set(ORDER) == set(REFS), set(REFS) - set(ORDER)

# ================================================================== ONLINE RESOURCE 1
doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
head("Online Resource 1", 1)
para("Supplementary material for “Composition dependence of peak load and stiffness extracted from ten "
     "compression-test curves”, P.H. Ramadhan (NIM 28726019). Figs. S1–S10 show the application of each dataset "
     "after **calc**, with the post title (dataset name), the marked points, the entered ids and the printed m, "
     "b and R². Listing S1 gives the Mermaid source of the flowchart.", size=10)
grid = doc.add_table(rows=len(KEYS) // 2, cols=2)
grid.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, k in enumerate(KEYS):
    cell = grid.rows[i // 2].cells[i % 2]
    cell.width = Cm(8.0)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.0
    p.add_run().add_picture(os.path.join(FIG, f"app_{k}.png"), width=Cm(7.6))
    cp = cell.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.line_spacing = 1.0
    cp.paragraph_format.space_after = Pt(8)
    add_runs(cp, f"**Fig. S{i + 1}** {k} ({D[k]['link']}): PEAK-ID {R[k]['peak']:04d}, LAST-ID "
                 f"{R[k]['last']:04d}, LINI-ID {R[k]['lini']:04d}, LINF-ID {R[k]['linf']:04d}", size=8.5)
head("Listing S1 Mermaid source of Fig. 2", 2)
for line in open(os.path.join(FIG, "flowchart.mmd"), encoding="utf-8").read().rstrip().split("\n"):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(line or " ")
    r.font.name = "Consolas"
    r.font.size = Pt(8)

doc.save(OUT)
print(OUT, f"abstract={words} words, refs={len(ORDER)}, figs={fig_n[0]}, tables={tab_n[0]}, eqs={eq_n[0]}")
