#!/usr/bin/env python3
"""
Build "The Complete Guide to Horse Racing Wagering" as a PDF.

Usage:  python3 docs/build_wagering_pdf.py [output.pdf]

Requires: reportlab
"""

import io
import sys
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------

INK = colors.HexColor("#1A1A18")
MUTED = colors.HexColor("#5C5C55")
RULE = colors.HexColor("#C9C4B4")
ACCENT = colors.HexColor("#5B2333")        # racing silks burgundy
ACCENT_2 = colors.HexColor("#2F4B3C")      # turf green
WASH = colors.HexColor("#F4F1E9")          # parchment
WASH_2 = colors.HexColor("#EAE5D8")
CAUTION = colors.HexColor("#8A5A00")

PAGE_W, PAGE_H = A4
MARGIN = 20 * mm

PUB_DATE = "August 2026"
TITLE = "The Complete Guide to Horse Racing Wagering"
SUBTITLE = "Pools, Prices, Probability and Bankroll"


# --------------------------------------------------------------------------
# Styles
# --------------------------------------------------------------------------

def build_styles():
    ss = getSampleStyleSheet()
    S = {}

    S["body"] = ParagraphStyle(
        "body", parent=ss["Normal"], fontName="Times-Roman", fontSize=10.2,
        leading=14.6, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=7,
    )
    S["body_first"] = ParagraphStyle("body_first", parent=S["body"], spaceBefore=2)
    S["lead"] = ParagraphStyle(
        "lead", parent=S["body"], fontSize=11.4, leading=16.4,
        textColor=colors.HexColor("#33332E"), spaceAfter=10,
    )
    S["h1"] = ParagraphStyle(
        "h1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=20,
        leading=24, textColor=ACCENT, spaceBefore=0, spaceAfter=2,
    )
    # h1_plain is identical to h1 but is never recorded in the table of
    # contents or the running head -- used for front matter.
    S["h1_plain"] = ParagraphStyle("h1_plain", parent=S["h1"])
    S["h1num"] = ParagraphStyle(
        "h1num", parent=ss["Normal"], fontName="Helvetica-Bold", fontSize=9,
        leading=11, textColor=ACCENT_2, spaceAfter=4,
    )
    S["h2"] = ParagraphStyle(
        "h2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=12.5,
        leading=15.5, textColor=ACCENT_2, spaceBefore=14, spaceAfter=5,
        keepWithNext=1,
    )
    S["h3"] = ParagraphStyle(
        "h3", parent=ss["Heading3"], fontName="Helvetica-BoldOblique", fontSize=10.6,
        leading=13.5, textColor=INK, spaceBefore=10, spaceAfter=3,
        keepWithNext=1,
    )
    S["bullet"] = ParagraphStyle(
        "bullet", parent=S["body"], alignment=TA_JUSTIFY, spaceAfter=3.5, leading=14,
    )
    S["cell"] = ParagraphStyle(
        "cell", parent=ss["Normal"], fontName="Times-Roman", fontSize=8.6,
        leading=11.2, textColor=INK,
    )
    S["cell_b"] = ParagraphStyle("cell_b", parent=S["cell"], fontName="Times-Bold")
    S["cell_h"] = ParagraphStyle(
        "cell_h", parent=S["cell"], fontName="Helvetica-Bold", fontSize=8.2,
        leading=10.4, textColor=colors.white,
    )
    S["caption"] = ParagraphStyle(
        "caption", parent=ss["Normal"], fontName="Helvetica-Oblique", fontSize=8,
        leading=10.5, textColor=MUTED, spaceBefore=3, spaceAfter=10,
    )
    S["mono"] = ParagraphStyle(
        "mono", parent=ss["Normal"], fontName="Courier", fontSize=8.8, leading=12.4,
        textColor=INK, leftIndent=8,
    )
    S["callout_h"] = ParagraphStyle(
        "callout_h", parent=ss["Normal"], fontName="Helvetica-Bold", fontSize=8.6,
        leading=11, textColor=ACCENT, spaceAfter=3,
    )
    S["callout"] = ParagraphStyle(
        "callout", parent=S["body"], fontSize=9.4, leading=13.2, spaceAfter=0,
    )
    S["glossterm"] = ParagraphStyle(
        "glossterm", parent=S["cell"], fontName="Times-Bold", fontSize=9, leading=12,
    )
    S["glossdef"] = ParagraphStyle(
        "glossdef", parent=S["cell"], fontSize=9, leading=12,
    )

    S["toc0"] = ParagraphStyle(
        "toc0", parent=ss["Normal"], fontName="Helvetica-Bold", fontSize=9,
        leading=20, textColor=ACCENT_2, spaceBefore=11, spaceAfter=1,
    )
    S["toc1"] = ParagraphStyle(
        "toc1", parent=ss["Normal"], fontName="Helvetica-Bold", fontSize=9.6,
        leading=15, textColor=ACCENT, leftIndent=8, spaceBefore=4,
    )
    S["toc2"] = ParagraphStyle(
        "toc2", parent=ss["Normal"], fontName="Times-Roman", fontSize=9.2,
        leading=13, textColor=INK, leftIndent=22,
    )
    return S


ST = build_styles()


# --------------------------------------------------------------------------
# Document template: cover page + body pages with running head/foot
# --------------------------------------------------------------------------

class TOCMark(Flowable):
    """Zero-size flowable that registers a table-of-contents entry.

    Used for the part dividers, whose title lives inside a Table cell and so
    is never seen by afterFlowable as a Paragraph.
    """

    def __init__(self, level, text):
        Flowable.__init__(self)
        self.level = level
        self.text = text
        self.width = 0
        self.height = 0

    def wrap(self, availWidth, availHeight):
        return (0, 0)

    def draw(self):
        pass


class Guide(BaseDocTemplate):
    def __init__(self, filename, **kw):
        BaseDocTemplate.__init__(self, filename, pagesize=A4,
                                 leftMargin=MARGIN, rightMargin=MARGIN,
                                 topMargin=MARGIN, bottomMargin=MARGIN, **kw)
        self.current_chapter = ""
        self.toc_label = ""
        frame_cover = Frame(0, 0, PAGE_W, PAGE_H, id="cover",
                            leftPadding=0, rightPadding=0,
                            topPadding=0, bottomPadding=0)
        frame_body = Frame(MARGIN, MARGIN + 9 * mm,
                           PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN - 15 * mm,
                           id="body", leftPadding=0, rightPadding=0,
                           topPadding=0, bottomPadding=0)
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[frame_cover], onPage=self.draw_cover),
            # Furniture is drawn at page END so the running head reflects the
            # chapter that actually starts on this page, not the previous one.
            PageTemplate(id="body", frames=[frame_body], onPageEnd=self.draw_body),
        ])

    def handle_documentBegin(self):
        # multiBuild reuses this instance across passes; reset per-pass state.
        self.current_chapter = ""
        BaseDocTemplate.handle_documentBegin(self)

    # -- page furniture ----------------------------------------------------
    def draw_cover(self, canv, doc):
        """The cover is drawn entirely on the canvas, not composed from
        flowables, so that nothing can reflow or overflow the page."""
        cx = PAGE_W / 2.0
        gold = colors.HexColor("#C9A227")
        canv.saveState()

        canv.setFillColor(colors.HexColor("#22201C"))
        canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

        # turf band along the foot, with a burgundy rail stripe above it
        band_h = 44 * mm
        canv.setFillColor(colors.HexColor("#2F4B3C"))
        canv.rect(0, 0, PAGE_W, band_h, fill=1, stroke=0)
        canv.setFillColor(colors.HexColor("#5B2333"))
        canv.rect(0, band_h, PAGE_W, 2.0 * mm, fill=1, stroke=0)
        canv.setStrokeColor(colors.HexColor("#3A5A49"))
        canv.setLineWidth(0.6)
        for i in range(1, 7):
            y = band_h - i * 6.2 * mm
            if y > 0:
                canv.line(0, y, PAGE_W, y)

        def centred(text, font, size, colour, y, spacing=0):
            # Always drawn through a text object with an explicit char space,
            # otherwise a previous tracked line leaks its spacing into this one.
            width = canv.stringWidth(text, font, size)
            if spacing:
                width += spacing * (len(text) - 1)
            tobj = canv.beginText(cx - width / 2.0, y)
            tobj.setFont(font, size)
            tobj.setFillColor(colour)
            tobj.setCharSpace(spacing)
            tobj.textOut(text)
            canv.drawText(tobj)

        rule_x = MARGIN + 14 * mm
        canv.setStrokeColor(gold)
        canv.setLineWidth(0.8)

        centred("A PRACTICAL REFERENCE", "Helvetica-Bold", 9, gold,
                PAGE_H - 74 * mm, spacing=1.6)
        canv.line(rule_x, PAGE_H - 84 * mm, PAGE_W - rule_x, PAGE_H - 84 * mm)

        centred("The Complete Guide to", "Times-Bold", 30, colors.white,
                PAGE_H - 106 * mm)
        centred("Horse Racing Wagering", "Times-Bold", 30, colors.white,
                PAGE_H - 122 * mm)
        centred(SUBTITLE, "Times-Italic", 14, colors.HexColor("#E3D9C6"),
                PAGE_H - 138 * mm)

        canv.line(rule_x, PAGE_H - 150 * mm, PAGE_W - rule_x, PAGE_H - 150 * mm)

        topics = [
            "Pari-mutuel mechanics  ·  takeout and breakage  ·  straight and exotic bet types",
            "past performances  ·  speed and pace figures  ·  fair-odds lines and value",
            "ticket construction  ·  bankroll and staking  ·  record keeping",
            "fixed-odds and exchange markets  ·  regulation and player protection",
        ]
        y = PAGE_H - 164 * mm
        for line in topics:
            centred(line, "Helvetica", 8.5, colors.HexColor("#B9AE97"), y)
            y -= 6.4 * mm

        centred("Version 1.0  ·  %s" % PUB_DATE,
                "Helvetica", 8.5, colors.HexColor("#B9AE97"), band_h + 22 * mm)
        centred("Prepared for HorseHQ  ·  Educational use only",
                "Helvetica", 8.5, colors.HexColor("#B9AE97"), band_h + 15 * mm)

        canv.restoreState()

    def draw_body(self, canv, doc):
        canv.saveState()
        # running head
        canv.setFont("Helvetica", 7.4)
        canv.setFillColor(MUTED)
        canv.drawString(MARGIN, PAGE_H - MARGIN + 3 * mm, TITLE)
        canv.drawRightString(PAGE_W - MARGIN, PAGE_H - MARGIN + 3 * mm,
                             self.current_chapter)
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        canv.line(MARGIN, PAGE_H - MARGIN + 1.2 * mm, PAGE_W - MARGIN, PAGE_H - MARGIN + 1.2 * mm)
        # foot
        canv.line(MARGIN, MARGIN + 7 * mm, PAGE_W - MARGIN, MARGIN + 7 * mm)
        canv.setFont("Helvetica", 7.4)
        canv.setFillColor(MUTED)
        canv.drawString(MARGIN, MARGIN + 3 * mm,
                        "Educational reference. Wager only what you can afford to lose.")
        canv.setFont("Helvetica-Bold", 8.4)
        canv.setFillColor(ACCENT)
        canv.drawRightString(PAGE_W - MARGIN, MARGIN + 2.8 * mm, str(canv.getPageNumber() - 1))
        canv.restoreState()

    # -- TOC + running-head wiring ----------------------------------------
    def afterFlowable(self, flowable):
        if isinstance(flowable, TOCMark):
            self.notify("TOCEntry", (flowable.level, flowable.text, self.page - 1))
            if flowable.level == 0:
                self.current_chapter = Paragraph(
                    flowable.text, ST["body"]).getPlainText()
            return
        if not isinstance(flowable, Paragraph):
            return
        style = flowable.style.name
        text = flowable.getPlainText()
        if style == "h1":
            self.current_chapter = text
            label = getattr(flowable, "toc_label", None) or text
            self.notify("TOCEntry", (1, label, self.page - 1))
        elif style == "h1_plain":
            # Front matter: runs in the running head but not the contents.
            self.current_chapter = text
        elif style == "h2" and self.current_chapter:
            self.notify("TOCEntry", (2, text, self.page - 1))


# --------------------------------------------------------------------------
# Flowable helpers
# --------------------------------------------------------------------------

def P(text, style="body"):
    return Paragraph(text, ST[style])


def bullets(items, style="bullet", bullet_char="•"):
    return ListFlowable(
        [ListItem(Paragraph(t, ST[style]), leftIndent=14, value=bullet_char)
         for t in items],
        bulletType="bullet", start=bullet_char, leftIndent=12,
        bulletFontSize=7, bulletOffsetY=-1, spaceAfter=8,
    )


def numbered(items, style="bullet"):
    return ListFlowable(
        [ListItem(Paragraph(t, ST[style]), leftIndent=16) for t in items],
        bulletType="1", leftIndent=14, bulletFontName="Helvetica-Bold",
        bulletFontSize=8.6, spaceAfter=8,
    )


def table(rows, widths, header=True, align=None, caption=None,
          font_size=8.6, header_bg=ACCENT_2, zebra=True):
    """rows: list of lists of raw strings (row 0 = header if header=True)."""
    data = []
    for r_i, row in enumerate(rows):
        out = []
        for c_i, cell in enumerate(row):
            if header and r_i == 0:
                out.append(Paragraph(str(cell), ST["cell_h"]))
            else:
                st = ST["cell"]
                if c_i == 0:
                    st = ST["cell_b"]
                p = ParagraphStyle("t", parent=st, fontSize=font_size,
                                   leading=font_size * 1.32)
                out.append(Paragraph(str(cell), p))
        data.append(out)

    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    cmds = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -2), 0.35, RULE),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
    ]
    if header:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), header_bg),
            ("TOPPADDING", (0, 0), (-1, 0), 5),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ]
        if zebra:
            for i in range(2, len(data), 2):
                cmds.append(("BACKGROUND", (0, i), (-1, i), WASH))
    if align:
        for col, a in align.items():
            cmds.append(("ALIGN", (col, 0), (col, -1), a))
    t.setStyle(TableStyle(cmds))

    if caption:
        return KeepTogether([t, Paragraph(caption, ST["caption"])])
    return KeepTogether([t, Spacer(1, 9)])


def callout(title, body, tone="accent"):
    bar = {"accent": ACCENT, "green": ACCENT_2, "caution": CAUTION}[tone]
    bg = {"accent": WASH, "green": WASH, "caution": colors.HexColor("#FBF3E2")}[tone]
    inner = [Paragraph(title.upper(), ST["callout_h"])]
    for para in body:
        inner.append(Paragraph(para, ST["callout"]))
        inner.append(Spacer(1, 4))
    inner = inner[:-1]
    t = Table([[inner]], colWidths=[PAGE_W - 2 * MARGIN])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 2.4, bar),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return KeepTogether([t, Spacer(1, 10)])


def worked(title, lines):
    """Monospaced worked-example block."""
    inner = [Paragraph(title.upper(), ST["callout_h"]), Spacer(1, 3)]
    for ln in lines:
        # A truly empty Paragraph collapses to nothing, which would swallow the
        # blank separator lines these blocks rely on for readability.
        inner.append(Paragraph(ln.replace(" ", "&nbsp;") or "&nbsp;", ST["mono"]))
    t = Table([[inner]], colWidths=[PAGE_W - 2 * MARGIN])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WASH_2),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return KeepTogether([t, Spacer(1, 10)])


def chapter(number, title, standfirst=None, toc=True, toc_label=None):
    head = Paragraph(title, ST["h1" if toc else "h1_plain"])
    if toc_label:
        head.toc_label = toc_label
    elif number:
        head.toc_label = "%s.&nbsp; %s" % (number, title)
    out = [
        Paragraph("CHAPTER %s" % number if number else "&nbsp;", ST["h1num"]),
        head,
        Spacer(1, 2),
    ]
    hr = Table([[""]], colWidths=[PAGE_W - 2 * MARGIN], rowHeights=[2])
    hr.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 1.6, ACCENT_2),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    out += [hr, Spacer(1, 9)]
    if standfirst:
        out.append(Paragraph(standfirst, ST["lead"]))
    return out


def appendix(letter, title, standfirst=None):
    return chapter(None, "Appendix %s &nbsp;&middot;&nbsp; %s" % (letter, title),
                   standfirst,
                   toc_label="Appendix %s &nbsp;&middot;&nbsp; %s" % (letter, title))


# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------

W_FULL = PAGE_W - 2 * MARGIN


def cover():
    # All cover artwork is drawn by Guide.draw_cover; the story only needs to
    # occupy the page so that the template fires.
    return [Spacer(1, 1)]


def front_matter():
    s = [NextPageTemplate("body"), PageBreak()]

    toc = TableOfContents()
    toc.levelStyles = [ST["toc0"], ST["toc1"], ST["toc2"]]
    toc.dotsMinLevel = 1
    s += chapter(None, "Contents", toc=False)
    s.append(toc)
    s.append(PageBreak())

    s += chapter(None, "How to use this guide", toc=False)
    s.append(P(
        "This guide explains how money is wagered on horse racing: where the price comes "
        "from, what the operator keeps, which bets exist, how to form an opinion, how to "
        "turn that opinion into a ticket, and how to stake it without going broke. It is "
        "written for the reader who already knows a horse from a hurdle but has never been "
        "shown the arithmetic underneath the tote board.", "lead"))
    s.append(P(
        "The three parts are cumulative but independently readable. <b>Part I</b> covers "
        "market mechanics: pari-mutuel pools, takeout, breakage, and the fixed-odds and "
        "exchange alternatives. Skipping it is the single most common reason otherwise "
        "sharp bettors lose money slowly. <b>Part II</b> covers the bet menu, from win bets "
        "to the Pick 6, with the cost formulas for every ticket structure. <b>Part III</b> "
        "covers the actual work: handicapping inputs, building a fair-odds line, "
        "constructing tickets, staking, and keeping records honest enough to tell you "
        "whether any of it is working."))
    s.append(P(
        "Conventions used throughout. Pari-mutuel payouts are quoted per $2 unless stated, "
        "which is the North American convention; minimum bet units are often smaller "
        "($0.10 on superfectas, $0.50 on many multi-race bets), so always read the payout "
        "denomination on the tote board before you convert. Fractional odds (7/2) are used "
        "for British and Irish markets, decimal odds (4.50) for exchanges, and American "
        "odds (+350) where the context is a US sportsbook. Appendix B converts between all "
        "three. Money is written in dollars in pari-mutuel examples and pounds in "
        "fixed-odds examples, matching where those markets actually operate; nothing in the "
        "arithmetic depends on the currency."))
    s.append(callout(
        "What this guide is not",
        ["It is not a tipping service, a system, or a promise. No sequence of bets described "
         "here has a guaranteed positive expectation, and several are explained precisely so "
         "you can recognise why they are bad.",
         "It is not legal advice. The legality of each wager type described varies by "
         "jurisdiction and changes; Chapter 15 sketches the landscape but you are responsible "
         "for your own position.",
         "It is not a substitute for the rules of the racing authority and the operator you "
         "bet with. Where a rule below conflicts with theirs, theirs governs and yours is the "
         "money."],
        tone="caution"))
    s.append(P(
        "A note on the numbers. Takeout rates, minimum bet units, place terms and deduction "
        "scales change from track to track, operator to operator, and season to season. Every "
        "rate in this guide is a representative figure chosen to make the arithmetic clear. "
        "Treat them as illustrations of method, not as current published rates, and check the "
        "live figure before it matters to your wallet."))
    s.append(PageBreak())
    return s


def part_divider(numeral, title, blurb):
    t = Table([[Paragraph(
        "<font size=9 color='#C9A227'><b>PART %s</b></font><br/><br/>"
        "<font size=21 color='white' face='Times-Bold'>%s</font><br/><br/>"
        "<font size=9.5 color='#D8D1C0' face='Times-Italic'>%s</font>" % (numeral, title, blurb),
        ParagraphStyle("pd", fontName="Helvetica", alignment=TA_CENTER, leading=15))]],
        colWidths=[W_FULL], rowHeights=[62 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2F4B3C")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 18),
        ("RIGHTPADDING", (0, 0), (-1, -1), 18),
    ]))
    return [TOCMark(0, "Part %s &nbsp;&middot;&nbsp; %s" % (numeral, title)),
            Spacer(1, 72 * mm), t, PageBreak()]


# ---------------------------------------------------------------- Chapter 1
def ch1():
    s = chapter(1, "How a Pari-Mutuel Pool Works",
                "Nobody at the racetrack is betting against you. Understanding who you "
                "<i>are</i> betting against is the foundation of everything that follows.")

    s.append(P(
        "In a pari-mutuel market there is no bookmaker taking a position. Every wager of a "
        "given type on a given race goes into a common pool. When the race is official, the "
        "operator removes a fixed percentage &mdash; the takeout &mdash; and divides what "
        "remains among the winning tickets in proportion to their stake. The odds you see "
        "before the race are not a price offered to you by anyone. They are a running "
        "estimate of what the pool will pay if betting stops at that instant.", "body_first"))
    s.append(P(
        "Two consequences follow immediately, and almost everything else in this guide is "
        "downstream of them. First, your opponents are the other bettors, not the house. The "
        "house is indifferent to which horse wins; it takes its percentage either way. To "
        "profit you do not need to predict winners &mdash; you need to disagree with the "
        "crowd, correctly, often enough to overcome the takeout. Second, your own money "
        "moves the price. Backing a 20/1 shot with a large enough stake makes it a 12/1 "
        "shot, and you get the 12/1. Pari-mutuel bettors bet into their own effect."))

    s.append(Paragraph("The mechanics, step by step", ST["h2"]))
    s.append(numbered([
        "<b>The pool opens.</b> Each bet type on each race has its own separate pool. The win "
        "pool, the place pool, the show pool, the exacta pool and the trifecta pool on a "
        "single race are five distinct piles of money that never touch each other.",
        "<b>Money comes in.</b> Bets arrive from the on-track tote, from off-track betting "
        "shops, from account-wagering platforms, and from other tracks and countries taking "
        "commingled bets into the same pool. All of it lands in the same pile.",
        "<b>Approximate odds are broadcast.</b> The tote recalculates and displays what each "
        "runner would pay, typically every 30 to 60 seconds, and more frequently as the "
        "start approaches. These are estimates and they are not binding.",
        "<b>The race is run and the pool is closed.</b> Betting stops. In practice the tote "
        "keeps accepting wagers fractionally past the official start while pending bets clear, "
        "which is why odds sometimes move after the gates open.",
        "<b>Takeout is deducted.</b> A fixed percentage set by statute or regulation is removed "
        "from the gross pool. What is left is the net pool.",
        "<b>The net pool is divided.</b> It is split among the winning tickets in proportion to "
        "stake. Payouts are then rounded down to a convenient increment &mdash; breakage &mdash; "
        "and the rounding remainder is kept.",
        "<b>The result is declared official.</b> Only after the stewards confirm the placings, "
        "and any inquiry or objection is resolved, does the tote pay.",
    ]))

    s.append(Paragraph("The win pool arithmetic", ST["h2"]))
    s.append(P(
        "The win pool is the simplest case, and it is worth being able to do by hand. Let "
        "<i>W</i> be the gross win pool, <i>t</i> the takeout rate, and <i>w</i> the amount "
        "bet on the horse that wins. The net pool is W(1&nbsp;&minus;&nbsp;t). Each dollar on "
        "the winner is entitled to a share of that net pool equal to its share of <i>w</i>, "
        "and it also gets its own stake back. So:"))
    s.append(worked("Win payout formula", [
        "net pool           = W x (1 - t)",
        "payout per $1      = net pool / w",
        "payout per $2      = 2 x net pool / w        <- the posted figure",
        "odds to $1         = (net pool / w) - 1",
        "",
        "then apply breakage: round the $2 payout DOWN",
        "to the nearest $0.10 (or $0.20 at some tracks).",
    ]))
    s.append(P(
        "Note that the posted $2 payout includes the return of your $2 stake, whereas the "
        "posted <i>odds</i> exclude it. A horse showing 3/1 pays $8.00 for $2: six dollars of "
        "profit plus the two you staked. Confusing the two is the most common beginner error "
        "at the window, and it makes every value calculation come out wrong by exactly one "
        "unit."))

    s.append(worked("Worked example: a $180,000 win pool, 16% takeout", [
        "Gross win pool  W = $180,000",
        "Takeout         t = 16%   ->  net pool = $151,200",
        "",
        "Runner        Bet on runner    Net pool / w    $2 payout   Odds",
        "Achill Bay        $12,600          12.00         $24.00      11/1",
        "Coldharbour       $37,800           4.00          $8.00       3/1",
        "Marlpit           $50,400           3.00          $6.00       2/1",
        "Silverlode        $79,200           1.909         $3.82       0.91/1",
        "                 --------",
        "                 $180,000",
        "",
        "If Silverlode wins:  $151,200 / $79,200 = 1.9091 per $1",
        "                     x 2 = $3.818  ->  breakage down to $3.80",
        "                     posted odds 9/10 (i.e. 0.90 to 1)",
    ]))
    s.append(P(
        "Observe that the four payouts are not independent numbers &mdash; they are four "
        "views of the same $151,200. Money that arrives on one runner lengthens every other "
        "runner's price. This is why a late plunge on the favourite is good news if you hold "
        "a ticket on anything else."))

    s.append(Paragraph("Place and show pools", ST["h2"]))
    s.append(P(
        "Place and show pools are harder because more than one runner is paid, and the payouts "
        "are interdependent. In the North American place pool the two horses finishing first "
        "and second are both paid. The operation is: take the gross pool, deduct takeout, then "
        "deduct the amount bet to place on <i>both</i> of the placing horses &mdash; that money "
        "is returned to those ticket holders as their stake. What remains is the profit pool. "
        "Split it in half, and give each half to the backers of one placing horse, pro rata."))
    s.append(worked("Place payout formula (two placed horses, A and B)", [
        "profit pool = [ P x (1 - t) ] - p(A) - p(B)",
        "",
        "payout per $2 on A = 2 x [ (profit pool / 2) + p(A) ] / p(A)",
        "payout per $2 on B = 2 x [ (profit pool / 2) + p(B) ] / p(B)",
        "",
        "where p(X) = total staked to place on horse X.",
        "The show pool is identical with three horses and thirds.",
    ]))
    s.append(P(
        "The split-in-half step is the important one. A place payout depends not only on how "
        "much is on your horse but on how much is on the <i>other</i> one that placed. Back a "
        "well-supported horse to place alongside a longshot and you collect a poor price; back "
        "the same horse alongside another favourite and you collect worse still. This is also "
        "the mechanism behind a <i>minus pool</i>."))
    s.append(callout(
        "Minus pools and the $2.10 floor",
        ["Most jurisdictions guarantee a minimum payout, commonly $2.10 for a $2 ticket &mdash; "
         "a 5% return. When an overwhelming favourite attracts so much of a place or show pool "
         "that the pro-rata calculation would pay less than the guaranteed minimum, the track "
         "must top the pool up out of its own funds. That is a minus pool, and the track loses "
         "money on the race.",
         "For the bettor the lesson is defensive: a 1/9 shot in the show pool can tie up your "
         "capital for a 5% return with a real chance of losing 100%. Bridge-jumping &mdash; "
         "very large show bets on short-priced horses &mdash; is the classic way to convert a "
         "large bankroll into a small one, one 5% win at a time."],
        tone="caution"))

    s.append(Paragraph("Commingling and why the price moves at the bell", ST["h2"]))
    s.append(P(
        "Modern pools are commingled: a bet struck in Hong Kong, an off-track shop in "
        "Pennsylvania and a phone account in London can all flow into the same host pool at "
        "the track. Commingling is good for bettors because it deepens the pool and makes "
        "large bets less self-destructive. It is also the main reason odds drop sharply at "
        "or after the start."))
    s.append(bullets([
        "<b>Batch transmission.</b> Remote hubs forward their wagers to the host tote in "
        "batches, and the last batch often lands as the gates open. That money was bet before "
        "the off; it is simply reported late.",
        "<b>Computer-assisted wagering.</b> High-volume automated players deliberately wait "
        "until the final seconds so that their own price impact is not visible to others, and "
        "so they can compute final odds against a near-complete pool.",
        "<b>Cancelled and corrected tickets.</b> Late voids remove money from the pool, which "
        "can move a price in either direction.",
    ]))
    s.append(P(
        "You cannot escape this. The practical response is to price your bet against the odds "
        "you would still accept after a plausible late drop, not against the odds flashing "
        "when you press the button. If a horse is only a bet at 8/1 and it is showing 8/1 with "
        "ninety seconds to go, it is probably not a bet."))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 2
def ch2():
    s = chapter(2, "Takeout, Breakage and the Real Cost of Playing",
                "Takeout is the single largest determinant of long-run results for a "
                "recreational bettor, and the one most of them never look up.")
    s.append(P(
        "Every pari-mutuel bet is made into a pool from which a percentage has already been "
        "promised to someone else. Before you have formed an opinion about a single horse, "
        "the arithmetic has been set against you by an amount that dwarfs the edge most "
        "bettors can realistically generate. A 20% takeout means that for every $100 wagered "
        "into that pool, $80 comes back to bettors collectively. To break even you must be "
        "25% better than the crowd &mdash; not 20%, because you need $100 back out of the $80 "
        "the pool returns.", "body_first"))

    s.append(Paragraph("Representative takeout rates", ST["h2"]))
    s.append(P(
        "Rates are set by state or national regulation and vary by track and bet type. The "
        "figures below are typical of North American thoroughbred racing and are given to "
        "show the shape of the schedule, not as current published rates."))
    s.append(table([
        ["Pool", "Typical range", "What drives it", "Bettor implication"],
        ["Win / Place / Show", "14% &ndash; 18%", "Statutory floor; the oldest and most "
         "politically fixed rates.", "The cheapest pools on the card. Most straight bettors "
         "never realise this."],
        ["Exacta / Quinella /<br/>Daily Double", "18% &ndash; 22%", "Classified as an exotic; "
         "higher rate permitted.", "Roughly 4 points more expensive than a win bet for a "
         "harder question."],
        ["Trifecta / Superfecta", "19% &ndash; 25%", "Highest tier; justified by large "
         "payouts and marketing value.", "You need a very large edge for these to clear."],
        ["Pick 3 / Pick 4", "15% &ndash; 25%", "Highly variable; some tracks cut Pick 4 "
         "takeout deliberately to attract volume.", "Worth shopping. A 15% Pick 4 is a "
         "materially different product from a 25% one."],
        ["Pick 5 / Pick 6", "12% &ndash; 25%", "Low-takeout Pick 5s are a common promotional "
         "tool; jackpot Pick 6s often carry high rates.", "The single best headline rates on "
         "the continent live here &mdash; and some of the worst."],
    ], [30 * mm, 24 * mm, 58 * mm, 58 * mm],
        caption="Table 2.1 &mdash; Indicative takeout by pool type. Always verify the live "
                "rate: the track's published takeout schedule, or your platform's "
                "wagering menu, is the authority."))

    s.append(P(
        "The strategic reading of that table is unglamorous but correct: the bet with the "
        "lowest cost of entry is the win bet, and the bets with the highest cost are precisely "
        "the ones marketed hardest. By the arithmetic above, 15% takeout requires you to be 17.6% "
        "better than the crowd, while 25% takeout requires 33.3% better. A bettor with a genuine "
        "20% edge in judgement can profit at the first and cannot profit at the second. The same "
        "skill, applied to a different window, produces opposite results."))

    s.append(Paragraph("Breakage: the quiet second tax", ST["h2"]))
    s.append(P(
        "After takeout, the calculated payout is rounded down. Traditional breakage rounds the "
        "$2 payout down to the nearest $0.10 &mdash; dime breakage &mdash; and some "
        "jurisdictions still round to $0.20, which costs twice as much. The remainder is "
        "retained. It sounds trivial and is not, because the effect is worst on exactly the "
        "short-priced horses that place and show bettors favour."))
    s.append(worked("Breakage bites hardest at short prices", [
        "True calculated $2 payout   Paid after dime breakage   Lost to breakage",
        "        $2.38                        $2.30                  3.4%",
        "        $3.18                        $3.10                  2.5%",
        "        $4.19                        $4.10                  2.1%",
        "        $9.19                        $9.10                  1.0%",
        "       $24.19                       $24.10                  0.4%",
        "",
        "Under 20-cent breakage every figure above roughly doubles:",
        "the $2.38 payout becomes $2.20, a loss of 7.6%.",
    ]))
    s.append(P(
        "Some jurisdictions have moved to penny breakage, which nearly eliminates this. It is "
        "worth knowing which regime your track uses; combined with takeout it can be the "
        "difference between a marginal strategy and a losing one."))

    s.append(Paragraph("Effective takeout, rebates and churn", ST["h2"]))
    s.append(P(
        "High-volume players do not pay list price. Account wagering platforms rebate a "
        "percentage of handle &mdash; typically fractions of a percent to several percent, "
        "scaled to volume and bet type &mdash; regardless of whether the bet wins. A 5% rebate "
        "against 20% takeout produces an effective takeout near 15%, which is the difference "
        "between a break-even player and a winning one. The existence of tiered rebating means "
        "that the pool you are betting into contains participants playing a materially cheaper "
        "game than you are."))
    s.append(P(
        "Churn is the related idea. If you bet $100 at 16% takeout and reinvest everything you "
        "get back, then bet again, and again, your original stake decays geometrically: after "
        "<i>n</i> cycles you expect to hold 100&nbsp;&times;&nbsp;(0.84)^n. Five cycles leaves "
        "$41.82; ten leaves $17.49. This is the true mathematical description of a day at the "
        "races with no edge, and it is why 'I only lost forty dollars' after betting eleven "
        "races is not the bargain it feels like."))
    s.append(worked("Bankroll decay with no edge, $100 start", [
        "Races played    16% takeout    20% takeout    25% takeout",
        "      1           $84.00         $80.00         $75.00",
        "      3           $59.27         $51.20         $42.19",
        "      5           $41.82         $32.77         $23.73",
        "      8           $24.79         $16.78          $10.01",
        "     10           $17.49         $10.74           $5.63",
        "",
        "This assumes an average bettor with zero skill edge who",
        "recycles the entire returned amount into the next race.",
    ]))
    s.append(callout(
        "The one-sentence version",
        ["Your handicapping has to beat the crowd by more than the takeout before you win a "
         "penny, so the cheapest way to improve your results is to bet less often, into "
         "cheaper pools, at a platform that rebates &mdash; none of which requires you to "
         "become a better judge of a horse."]))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 3
def ch3():
    s = chapter(3, "Fixed Odds, Exchanges and Tote: Three Different Games",
                "The same horse can be priced three ways at the same moment. Knowing which "
                "market you are in tells you what your edge has to be.")
    s.append(P(
        "Pari-mutuel wagering dominates North America, Japan, Hong Kong and France. British "
        "and Irish racing is dominated instead by fixed-odds bookmaking, with a tote "
        "operating alongside it and a betting exchange operating alongside both. The three "
        "structures have genuinely different economics.", "body_first"))
    s.append(table([
        ["", "Pari-mutuel (tote)", "Fixed-odds bookmaker", "Betting exchange"],
        ["Who sets the price", "The betting public, collectively", "The bookmaker, who takes "
         "the other side", "Other bettors, by offer and acceptance"],
        ["When your price is locked", "Never &mdash; you get the final pool price", "At the "
         "moment you strike, if you take a board price", "At the moment your bet is matched"],
        ["Operator's margin", "Takeout, typically 14&ndash;25%", "Overround built into the "
         "book, typically 10&ndash;25% on a big field", "Commission on net winnings, typically "
         "2&ndash;5%"],
        ["Can you be limited or refused?", "No &mdash; the pool accepts all money", "Yes, "
         "routinely, and winning accounts often are", "Rarely; you can also be the layer"],
        ["Can you bet a horse to lose?", "No", "No", "Yes &mdash; laying is native"],
        ["Effect of your own stake", "Shortens your own price", "None once struck", "Consumes "
         "the offered liquidity at that price"],
        ["Best-suited edge", "Disagreeing with the crowd's ranking", "Beating a slow or "
         "generous price, and shopping", "Speed, liquidity reading, and in-running judgement"],
    ], [30 * mm, 44 * mm, 48 * mm, 48 * mm], font_size=8.2,
        caption="Table 3.1 &mdash; Structural comparison. A strategy that works in one column "
                "may be meaningless in another."))

    s.append(Paragraph("Overround: the bookmaker's version of takeout", ST["h2"]))
    s.append(P(
        "A fixed-odds book does not deduct a percentage. Instead it offers prices whose implied "
        "probabilities sum to more than 100%. That excess is the overround, or 'vig', and it is "
        "the direct analogue of takeout."))
    s.append(worked("Computing the overround", [
        "For each runner, implied probability = 1 / decimal odds",
        "                                     = denom / (num + denom)  [fractional]",
        "",
        "Runner        Fractional   Decimal   Implied %",
        "Coldharbour       2/1        3.00      33.33",
        "Marlpit           5/2        3.50      28.57",
        "Achill Bay        4/1        5.00      20.00",
        "Silverlode        6/1        7.00      14.29",
        "Penny Whistle    12/1       13.00       7.69",
        "                                     --------",
        "                        book total =   103.88%",
        "",
        "Overround = 3.88%.  The bookmaker expects to keep about",
        "3.88 / 103.88 = 3.7% of turnover on a perfectly balanced book.",
    ]))
    s.append(P(
        "A five-runner book at 103.88% is a tight, competitive market. A twenty-runner "
        "handicap priced at 130% is a market you should be very reluctant to bet into blind. "
        "The overround is not distributed evenly, either: bookmakers habitually load more "
        "margin onto outsiders than onto favourites, which reinforces the well-documented "
        "<i>favourite&ndash;longshot bias</i> &mdash; the tendency of long-priced horses to be "
        "worse value than their odds suggest. Margin loading is not the whole explanation, "
        "though. The same bias appears in pari-mutuel pools, where no bookmaker sets the price "
        "at all, so bettor behaviour is doing most of the work."))

    s.append(Paragraph("Exchange pricing and commission", ST["h2"]))
    s.append(P(
        "On an exchange, one user backs and another lays. The exchange's revenue is commission "
        "on net winnings on a market, commonly 2% to 5%. Because there is no overround built "
        "into the price and commission is charged only on profit, exchange prices are usually "
        "the best available &mdash; and they are the closest thing racing has to a genuine "
        "consensus probability. Many serious bettors use exchange prices at the off as their "
        "benchmark of true probability even when they bet elsewhere."))
    s.append(P(
        "Laying deserves particular caution. When you lay a horse at 10.0 for a &pound;20 "
        "stake, you are accepting a liability of &pound;180 to win &pound;20. The risk-reward "
        "is inverted relative to backing, and a run of losses arrives in large lumps. Exchange "
        "liability is the most common way a new user destroys an account balance in a single "
        "afternoon."))
    s.append(callout(
        "Best-odds-guaranteed and the price you actually get",
        ["Many bookmakers offer 'best odds guaranteed' (BOG): take an early price, and if the "
         "starting price is bigger, you are paid at the SP. Where available this is a genuine "
         "and material edge &mdash; you hold a free option on the price drifting.",
         "It is also the reason bookmakers restrict accounts. A customer who consistently "
         "takes early prices on horses that shorten is demonstrating that they price faster "
         "than the book does, and will be limited long before they are rich."]))

    s.append(Paragraph("Deductions when a horse is withdrawn", ST["h2"]))
    s.append(P(
        "In pari-mutuel markets a non-runner is simple: bets on it are refunded and the pool "
        "recalculates. In fixed-odds markets the price you struck is now too generous, because "
        "one competitor has been removed. British and Irish rules handle this with a scale of "
        "deductions from winnings, applied to bets struck before the withdrawal at the price "
        "then available. The deduction depends on the odds of the <i>withdrawn</i> horse: the "
        "shorter it was, the more the remaining field's chances improve, and the larger the "
        "deduction. Appendix C gives the full scale."))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 4
def ch4():
    s = chapter(4, "Straight Wagers: Win, Place, Show and Each-Way",
                "The simplest bets are also the cheapest, and one of them is systematically "
                "misunderstood on both sides of the Atlantic.")
    s.append(P(
        "A straight wager concerns one horse in one race. There are only a few of them and "
        "they carry the lowest takeout on the card, which makes them the natural home of a "
        "bettor who believes their edge lies in judging horses rather than in constructing "
        "combinations.", "body_first"))

    s.append(table([
        ["Wager", "Wins if your horse&hellip;", "Notes"],
        ["Win", "finishes first", "The purest expression of an opinion, and the cheapest pool. "
         "Every other bet type can be understood as a modification of this one."],
        ["Place (North America)", "finishes first or second", "Paid from the place pool. "
         "Payout depends on who else placed."],
        ["Show", "finishes first, second or third", "Paid from the show pool. Lowest variance, "
         "lowest return, most exposed to breakage."],
        ["Across the board", "any of the above", "Three separate bets of equal size on the same "
         "horse. A $2 across-the-board costs $6 and is usually a worse allocation than $6 to win."],
        ["Place (UK/IRE tote)", "finishes in a paid place", "The number of paid places depends "
         "on field size, not a fixed two or three."],
        ["Each-way", "wins, and/or is placed", "Two equal bets: one to win, one to place at "
         "fractional odds. A &pound;10 each-way bet costs &pound;20."],
    ], [30 * mm, 40 * mm, 100 * mm],
        caption="Table 4.1 &mdash; The straight wager menu."))

    s.append(Paragraph("Each-way betting, properly explained", ST["h2"]))
    s.append(P(
        "An each-way bet is not one bet with a safety net. It is two bets of equal stake, "
        "settled independently: the win half at the full odds, and the place half at a "
        "fraction of those odds, paying if the horse finishes within the advertised places. "
        "Saying '&pound;10 each-way' means you are staking &pound;20."))
    s.append(P(
        "The place terms depend on the race type and the number of runners. The scale below "
        "is the long-standing industry standard, though individual bookmakers frequently "
        "enhance it &mdash; extra places on big handicaps are a routine promotion, and they "
        "are one of the few genuinely bettor-favourable offers in the sport."))
    s.append(table([
        ["Race and field size", "Places paid", "Place odds"],
        ["2 to 4 runners", "Win only &mdash; no each-way betting", "&mdash;"],
        ["5 to 7 runners", "1st and 2nd", "1/4 of the win odds"],
        ["8 or more runners (non-handicap)", "1st, 2nd, 3rd", "1/5 of the win odds"],
        ["8 to 11 runners (handicap)", "1st, 2nd, 3rd", "1/5 of the win odds"],
        ["12 to 15 runners (handicap)", "1st, 2nd, 3rd", "1/4 of the win odds"],
        ["16 or more runners (handicap)", "1st, 2nd, 3rd, 4th", "1/4 of the win odds"],
    ], [62 * mm, 44 * mm, 44 * mm],
        caption="Table 4.2 &mdash; Standard each-way place terms. Enhanced terms are common on "
                "televised handicaps; the bookmaker's own terms at the moment of striking "
                "govern."))
    s.append(worked("Settling a 10 each-way bet at 8/1, 16-runner handicap", [
        "Stake:        GBP 10 win  +  GBP 10 place  =  GBP 20 total",
        "Place terms:  1/4 odds, 4 places  ->  place odds = 8/4 = 2/1",
        "",
        "Horse WINS:",
        "  win part   10 x 8/1 = 80 profit, + 10 stake  = 90",
        "  place part 10 x 2/1 = 20 profit, + 10 stake  = 30",
        "  returned  120   |   staked 20   |   PROFIT 100",
        "",
        "Horse finishes 3rd:",
        "  win part   loses                             = 0",
        "  place part 10 x 2/1 = 20 profit, + 10 stake  = 30",
        "  returned   30   |   staked 20   |   PROFIT 10",
        "",
        "Horse finishes 6th:",
        "  returned    0   |   staked 20   |   LOSS -20",
    ]))
    s.append(P(
        "The critical judgement in each-way betting is the break-even price. Below a certain "
        "win price, the place half is bad value in isolation and drags the whole bet down; "
        "above it, the place half can be the better half. With 1/5 odds and three places, the "
        "place bet is generally poor below about 5/1 and interesting above roughly 8/1 in a "
        "big field, because a horse's chance of placing declines far more slowly than its "
        "chance of winning. This asymmetry is the entire basis of the 'each-way thief' "
        "&mdash; a long-priced runner in a field where the place terms are generous relative "
        "to the horse's true placing chance."))

    s.append(Paragraph("Which straight bet should you actually make?", ST["h2"]))
    s.append(P(
        "For most bettors, most of the time, the answer is the win bet, and the reasoning is "
        "purely mechanical. Place and show pools are smaller, so a large bet distorts them "
        "more. They are more exposed to breakage. Their payouts depend on the identity of the "
        "other placed horses, which is a source of variance you have no ability to forecast. "
        "And crucially, the crowd's opinion is better represented in the place and show pools "
        "than in the win pool, because those pools are dominated by risk-averse money on "
        "obvious horses &mdash; leaving less room for disagreement to pay."))
    s.append(bullets([
        "<b>Bet to win</b> when you have a genuine opinion on the horse most likely to win, and "
        "when the price is above your fair estimate.",
        "<b>Bet to place</b> when your read is that the horse is much better than the field but "
        "carries a specific winning risk &mdash; an awkward draw, a doubtful trip, a habitual "
        "slow start &mdash; and the place price still exceeds your placing estimate.",
        "<b>Bet to show</b> almost never, unless you are exploiting a specific pool distortion "
        "and can compute the payout in advance.",
        "<b>Bet each-way</b> in large fields at long prices where the place terms overpay your "
        "estimate of the placing chance &mdash; not as a way to feel safer about a short price.",
    ]))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 5
def ch5():
    s = chapter(5, "Vertical Exotics: Exacta, Trifecta, Superfecta",
                "Betting the order of finish within a single race. High takeout, high "
                "variance, and the place where ticket construction begins to matter more "
                "than opinion.")
    s.append(P(
        "Vertical exotics ask you to name the finishing order of two, three, four or occasionally five horses "
        "in one race. They are the most heavily promoted bets in racing and among the most "
        "expensive by takeout. They are nevertheless where a strong opinion can be leveraged, "
        "because the crowd's ability to rank horses correctly decays far faster than its "
        "ability to pick a winner.", "body_first"))
    s.append(table([
        ["Wager", "You must select", "Typical minimum", "Combinations in a 10-horse field"],
        ["Exacta (Forecast)", "1st and 2nd, in exact order", "$1 or $2", "90"],
        ["Quinella", "1st and 2nd, in either order", "$2", "45"],
        ["Trifecta (Tricast)", "1st, 2nd and 3rd, in exact order", "$0.50 or $1", "720"],
        ["Superfecta", "1st, 2nd, 3rd and 4th, in exact order", "$0.10 or $1", "5,040"],
        ["Super High Five", "The first five, in exact order", "$0.10 or $1", "30,240"],
    ], [32 * mm, 52 * mm, 28 * mm, 46 * mm],
        caption="Table 5.1 &mdash; Vertical exotics. Combination counts are for covering every "
                "possibility, which is never a strategy &mdash; they are given to show how "
                "quickly the space explodes."))

    s.append(Paragraph("Ticket structures and what they cost", ST["h2"]))
    s.append(P(
        "Almost every exotic ticket is one of four shapes. Knowing the cost formula for each "
        "is what separates deliberate ticket construction from guessing at the window."))
    s.append(table([
        ["Structure", "What it means", "Cost formula", "Example"],
        ["Straight", "One exact combination", "1 unit", "5-3 exacta: $1"],
        ["Box", "All orderings of the chosen horses", "n(n&minus;1) exacta;<br/>"
         "n(n&minus;1)(n&minus;2) trifecta", "4-horse trifecta box = 24 units = $24 at $1"],
        ["Key (wheel)", "One horse fixed in a position, all others fill the rest", "depends on "
         "position; see below", "5 keyed on top of 4 others, trifecta: 4&times;3 = 12"],
        ["Part-wheel", "Different horse lists in each position", "product of list sizes, minus "
         "duplicates", "See the worked example below"],
    ], [26 * mm, 46 * mm, 44 * mm, 42 * mm], font_size=8.2,
        caption="Table 5.2 &mdash; The four ticket shapes. Every exotic wager you will ever "
                "make is one of these."))
    s.append(worked("Box costs at a $1 base", [
        "Horses    Exacta box    Trifecta box    Superfecta box",
        "   3          $6            $6              n/a",
        "   4         $12           $24              $24",
        "   5         $20           $60             $120",
        "   6         $30          $120             $360",
        "   7         $42          $210             $840",
        "   8         $56          $336           $1,680",
        "  10         $90          $720           $5,040",
        "",
        "Formula: exacta n(n-1);  trifecta n(n-1)(n-2);",
        "         superfecta n(n-1)(n-2)(n-3).",
    ]))
    s.append(callout(
        "The box is usually the wrong ticket",
        ["A box says every ordering of your horses is equally likely. You almost never believe "
         "that. If you have separated four horses well enough to isolate them from the field, "
         "you certainly have an opinion about which is most likely to win &mdash; and a box "
         "spends equal money on the combinations where your best horse runs fourth.",
         "The alternative is a structured part-wheel that spends most on your opinion and a "
         "little on the ways you might be wrong. It costs less and pays more when you are right."],
        tone="caution"))

    s.append(Paragraph("Building a structured trifecta", ST["h2"]))
    s.append(P(
        "Suppose you have separated a field into three groups: <b>A</b> is your single best "
        "horse (#5); <b>B</b> are two horses you rate close behind (#2, #9); <b>C</b> are three "
        "you think can hit the board but not win (#1, #4, #11). A part-wheel lets you express "
        "exactly that."))
    s.append(worked("Part-wheel: A / A+B / A+B+C, trifecta at $1", [
        "1st position:  5                     (1 horse)",
        "2nd position:  2, 9                   (2 horses)",
        "3rd position:  2, 9, 1, 4, 11         (5 horses)",
        "",
        "Combinations = 1 x 2 x 5 = 10, MINUS the 2 combinations",
        "where the same horse would occupy both 2nd and 3rd.",
        "  5-2-2 (invalid), 5-9-9 (invalid)",
        "Valid tickets = 1 x 2 x 5 - 2 = 8   ->   cost $8",
        "",
        "Compare: a 6-horse trifecta box covering the same runners",
        "         = 6 x 5 x 4 = 120 combinations = $120.",
        "",
        "The part-wheel is 15x cheaper. It gives up the outcomes in",
        "which #5 fails to win -- which you already said was unlikely",
        "-- plus the 12 in which #5 wins but a C horse runs second.",
    ]))
    s.append(P(
        "Most tote systems compute the deduplication for you and quote the true ticket cost "
        "before you confirm. Always read that number back before pressing accept: a "
        "mis-entered wheel is the classic way to turn an intended $8 bet into an $800 one."))

    s.append(Paragraph("When vertical exotics are actually worth playing", ST["h2"]))
    s.append(bullets([
        "<b>When you can beat the favourite.</b> If the crowd's top choice is vulnerable and "
        "you can construct tickets that exclude it, or use it only underneath, the payouts "
        "inflate enormously. Exotic pools are dominated by tickets keyed on the favourite.",
        "<b>When the field is unevenly readable.</b> A race with three obvious contenders and "
        "seven no-hopers is a poor exotic race &mdash; everyone sees it. A race where the "
        "bottom half contains a horse you can justify is where exotic value lives.",
        "<b>When you have a legitimate 'all' opinion in one slot.</b> Sometimes the honest read "
        "is that one position is genuinely unpredictable. Spreading there while keying your "
        "opinion above it is a legitimate structure, not laziness.",
        "<b>When the pool is large enough.</b> A trifecta pool of $4,000 cannot absorb a "
        "meaningful bet without collapsing its own payout. Check pool size before you size a bet.",
    ]))
    s.append(P(
        "Conversely, the strongest argument against habitual exotic play is the compounding of "
        "takeout with difficulty. A trifecta asks a question roughly an order of magnitude "
        "harder than a win bet and charges you 25% more to answer it. It is entirely possible "
        "to be a skilled handicapper and a losing exotic player, and the usual cause is not "
        "bad opinions but tickets that cost more than the opinion is worth."))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 6
def ch6():
    s = chapter(6, "Horizontal Exotics: Doubles, Pick 3 to Pick 6",
                "Multi-race bets compound your edge and your error at the same rate. They "
                "reward exactly one thing: opinion held with discipline about which races to "
                "spread and which to single.")
    s.append(P(
        "A horizontal exotic requires you to select the winner of each of several consecutive "
        "races on a single ticket. There is no partial credit in most formats: miss one leg "
        "and the ticket is dead. The appeal is that the payoffs multiply, and that the pools "
        "are large enough to absorb serious money.", "body_first"))
    s.append(table([
        ["Wager", "Legs", "Typical minimum", "Character"],
        ["Daily Double", "2", "$1 or $2", "The entry point. Often better value than the "
         "equivalent parlay because it is a single pool."],
        ["Pick 3", "3", "$0.50 or $1", "The workhorse multi-race bet. Cheap to construct, "
         "frequently offered in rolling sequences across the card."],
        ["Pick 4", "4", "$0.50", "Large pools, often reduced takeout. The most commonly "
         "recommended multi-race bet for a serious player."],
        ["Pick 5", "5", "$0.50", "Increasingly the flagship low-takeout bet; pools can be "
         "very large."],
        ["Pick 6", "6", "$1 or $2", "Lottery-scale payouts, carryovers, and often a jackpot "
         "rule requiring a unique winning ticket."],
        ["Placepot (UK/IRE)", "6", "&pound;0.10 units", "Requires a <i>placed</i> finish in each "
         "of the first six races &mdash; far more forgiving than a Pick 6."],
        ["Scoop6 (UK)", "6", "&pound;2", "Win fund plus place fund and a bonus round; large "
         "carryovers."],
    ], [30 * mm, 14 * mm, 26 * mm, 88 * mm], font_size=8.4,
        caption="Table 6.1 &mdash; Horizontal exotics in common use."))

    s.append(Paragraph("Cost is multiplicative, and it is brutal", ST["h2"]))
    s.append(P(
        "The cost of a horizontal ticket is the product of the number of horses used in each "
        "leg, times the base unit. Adding one horse to one leg of a Pick 4 does not add one "
        "ticket; it adds an entire slice of the ticket."))
    s.append(worked("Pick 4 cost, $0.50 base", [
        "Structure (horses per leg)     Combinations     Cost",
        "  1 x 1 x 1 x 1                      1          $0.50",
        "  2 x 2 x 2 x 2                     16          $8.00",
        "  1 x 3 x 4 x 2                     24         $12.00",
        "  3 x 3 x 3 x 3                     81         $40.50",
        "  2 x 4 x 5 x 3                    120         $60.00",
        "  4 x 4 x 4 x 4                    256        $128.00",
        "  1 x 6 x 8 x 6                    288        $144.00",
        "  5 x 5 x 5 x 5                    625        $312.50",
        "",
        "Notice rows 6 and 7: nearly identical cost, radically",
        "different bets. Row 6 admits it has no opinion anywhere;",
        "row 7 backs a strong single and spends the savings",
        "spreading in the three legs it cannot read.",
    ]))

    s.append(Paragraph("The single is the whole game", ST["h2"]))
    s.append(P(
        "Every horizontal ticket is a negotiation between coverage and cost, and the currency "
        "is the single &mdash; a leg in which you use exactly one horse. A correct single "
        "halves or quarters your ticket cost and lets you spend the savings spreading in the "
        "legs you genuinely cannot read. An incorrect single loses the entire ticket."))
    s.append(bullets([
        "<b>Single where you have a price-independent opinion.</b> The right single is a horse "
        "you would bet to win at the odds, in a race where the alternatives are genuinely "
        "inferior &mdash; not merely the favourite.",
        "<b>Never single the vulnerable favourite.</b> A short-priced horse with a question "
        "&mdash; first time on the surface, a wide draw, returning from a layoff &mdash; is the "
        "worst single on the card, because everyone else has singled it and you carry the same "
        "risk for none of the reward.",
        "<b>Spread where the crowd is confident and you are not.</b> A leg with a 4/5 favourite "
        "you doubt is exactly where a three- or four-horse spread earns its cost.",
        "<b>Spread widest in the leg with the largest field and the flattest odds.</b> A "
        "fourteen-runner maiden claimer with no horse under 4/1 is not a leg to single.",
    ]))
    s.append(callout(
        "Ticket shape beats ticket size",
        ["Two players spend $144 on the same Pick 4. Player A plays 1&times;6&times;8&times;6, "
         "keying a strong single and spreading everywhere else. Player B plays "
         "4&times;4&times;3&times;6 &mdash; the same 288 combinations, but moderate coverage in "
         "every leg and a single nowhere.",
         "Player A wins big or loses everything in the first race. Player B wins something more "
         "often but at a fraction of the price, because the horses in B's tickets are the same "
         "horses on everyone else's tickets. Over a season A's structure has higher variance "
         "and, if the single is genuinely an opinion rather than a guess, higher expectation."]))

    s.append(Paragraph("Carryovers, jackpots and mandatory payouts", ST["h2"]))
    s.append(P(
        "When nobody selects all legs, many multi-race pools carry the money forward to the "
        "next racing day. Jackpot formats go further, requiring a <i>unique</i> winning ticket "
        "to take the main pool and carrying it over otherwise, sometimes for weeks. Carryover "
        "money is dead money contributed by previous days' losers: it enters the pool with no "
        "takeout applied against you."))
    s.append(P(
        "This creates the closest thing racing offers to a structurally positive-expectation "
        "situation. On a mandatory-payout day &mdash; when the rules require the accumulated "
        "pool to be paid out in full regardless of whether anyone hits every leg &mdash; a "
        "large carryover can exceed the takeout on the new money entering. The catch is that "
        "everybody knows this. Mandatory payout days attract enormous volume from syndicates "
        "with far more capital and better tools than a recreational player, and the practical "
        "result is that the free money is competed away and then some. Treat carryovers as a "
        "reason to look, not as a reason to bet."))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 7
def ch7():
    s = chapter(7, "Reading the Past Performances",
                "The single densest information object in sport. Everything a bettor knows "
                "before the horses walk into the paddock comes from this page.")
    s.append(P(
        "A past performance line &mdash; from the Daily Racing Form, Brisnet, TimeformUS, "
        "Timeform, the Racing Post, or a track programme &mdash; compresses a horse's entire "
        "career into a few rows of type. The formats differ but the content is broadly "
        "consistent, and learning to read one transfers to the rest.", "body_first"))

    s.append(Paragraph("The header block", ST["h2"]))
    s.append(table([
        ["Field", "What it tells you", "What to do with it"],
        ["Name, age, sex, colour", "Basic identity", "Age matters enormously in the first half "
         "of the year for three-year-olds, who are still improving month to month."],
        ["Sire and dam (and damsire)", "Genetic aptitude", "The best predictor available for an "
         "unraced or lightly raced horse's surface, distance and going preference."],
        ["Owner, trainer, jockey", "The connections", "Trainer statistics by category are among "
         "the most reliably predictive data in the form."],
        ["Career record box", "Starts, wins, places, earnings &mdash; usually split by year, "
         "surface, track and distance", "Look for the split records. A horse that is 0-for-14 "
         "on turf and 4-for-6 on dirt has told you something the overall record hides."],
        ["Weight carried", "Assigned or claimed weight", "In handicaps this is the entire point "
         "of the race. Weight shifts of 3&ndash;5 lb are meaningful over a distance."],
        ["Equipment and medication", "Blinkers, tongue tie, first-time Lasix, shoe changes",
         "First-time equipment changes are a stated intention by the trainer to change "
         "something. They deserve attention, in both directions."],
        ["Claiming price", "The level at which the horse can be bought out of the race",
         "The purest available statement of what the connections think the horse is worth."],
    ], [34 * mm, 60 * mm, 76 * mm], font_size=8.2,
        caption="Table 7.1 &mdash; The header block, field by field."))

    s.append(Paragraph("The running lines", ST["h2"]))
    s.append(P(
        "Each past race occupies one line. Read left to right: date and track; distance and "
        "surface; track condition; fractional times of the race; the horse's own position and "
        "beaten lengths at each call; the finishing position and margin; the jockey, weight and "
        "odds; the speed figure; and a short comment naming the first three finishers."))
    s.append(worked("Anatomy of one running line", [
        "12May26 Bel 7f fst  22.4 45.1 1:23.2  6-4  5-3  3-1  2-nk  Doyle 126  9/2  91",
        "|        |   |   |   |________________|  |____|____|____|   |     |    |    |",
        "|        |   |   |          fractions     position and      jockey wt  SP  figure",
        "|        |   |   track condition          lengths behind",
        "|        |   distance and surface",
        "|        track",
        "date",
        "",
        "Read it as: at Belmont over 7 furlongs on a fast track, the",
        "field went 22.4 to the quarter, 45.1 to the half, 1:23.2 final.",
        "Our horse was 6th, 4 lengths back at the first call; 5th and 3",
        "back at the second; 3rd and 1 back at the stretch call; and",
        "finished 2nd beaten a neck. Carried 126 lb, started 9/2,",
        "earned a speed figure of 91.",
    ]))
    s.append(P(
        "The position-and-lengths sequence is the most under-used data on the page. It is a "
        "compressed description of <i>how</i> the horse ran, not merely where it finished. A "
        "horse that is 1st by 3, 1st by 2, 1st by 1, 4th beaten 2 has stopped badly. A horse "
        "that is 9th by 11, 9th by 9, 6th by 5, 3rd beaten 1 has run an enormous race that its "
        "finishing position understates. These two lines can produce identical finishing "
        "positions across a career and describe completely different animals."))

    s.append(Paragraph("What the comment lines hide", ST["h2"]))
    s.append(P(
        "The trouble-line comment &mdash; 'bumped start', 'steadied 3/8', 'checked, altered "
        "course', 'no room late' &mdash; is written by a chart caller under time pressure and "
        "is systematically incomplete. It is nevertheless the cheapest source of edge available "
        "to a casual bettor, because the crowd prices the finishing position and largely "
        "ignores the reason for it."))
    s.append(bullets([
        "<b>Trouble that cost ground is worth more than trouble that cost momentum</b>, and "
        "both are worth more when they happened late in a short race.",
        "<b>'Wide' is the most valuable single word in the comment line.</b> A horse racing "
        "three or four paths off the rail around two turns covers materially more ground than "
        "the winner and is beaten by the geometry, not the ability.",
        "<b>Watch the replay if the comment is interesting.</b> The chart says 'no room late'. "
        "The replay tells you whether the horse was going to win or was already beaten and "
        "conveniently blocked.",
    ]))
    s.append(callout(
        "Build the habit before you build the system",
        ["Take one race a day. Read the past performances, write down in one sentence what you "
         "expect to happen and why, then watch the replay and write one sentence on what "
         "actually happened. Do this for a month before you bet a penny on a method.",
         "This is dull and it is the only training regime in this guide that reliably works. "
         "Handicapping is pattern recognition, and pattern recognition requires labelled "
         "examples."]))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 8
def ch8():
    s = chapter(8, "Speed, Pace and the Shape of a Race",
                "Two horses with identical final times can have run races with nothing in "
                "common. Pace is the variable that explains why.")
    s.append(P(
        "Raw final time is nearly useless on its own. It reflects the going, the wind, the "
        "distance of ground actually covered, the class of the field, how hard the early pace "
        "was, and whether the winner was asked for anything in the last furlong. Speed figures "
        "exist to strip out as much of that as possible and leave a number comparable across "
        "tracks and days.", "body_first"))

    s.append(Paragraph("How a speed figure is made", ST["h2"]))
    s.append(numbered([
        "<b>Start with the final time</b> for the race at the distance.",
        "<b>Compare it to a par time</b> &mdash; the expected time for that class, age and sex "
        "at that track and distance.",
        "<b>Adjust for the daily track variant.</b> Every race on the card is compared to par; "
        "if the whole card ran two lengths slow, the track was slow that day, not the horses.",
        "<b>Convert lengths to points</b> using a scale that depends on distance &mdash; a "
        "length is worth more at five furlongs than at two miles, because it is a larger "
        "fraction of the total time.",
        "<b>Adjust each runner for beaten lengths</b> from the winner's figure.",
    ]))
    s.append(table([
        ["Figure", "Publisher / origin", "Scale and character"],
        ["Beyer Speed Figure", "Andrew Beyer, published in the Daily Racing Form",
         "Roughly 0&ndash;120+. A top US Grade 1 performance is around 105&ndash;115. The most "
         "widely known figure in North America, and therefore the most heavily bet."],
        ["Brisnet Speed Rating", "Brisnet", "Similar scale to Beyer; accompanied by separate "
         "pace ratings for each call."],
        ["TimeformUS Speed Figure", "TimeformUS", "Similar scale, with an explicit pace figure "
         "and a colour-coded pace projection."],
        ["Timeform rating", "Timeform (UK/IRE)", "Expressed in pounds. A top-class flat horse "
         "rates around 130; a modest handicapper around 70."],
        ["Official BHA / handicap mark", "Racing authority", "In pounds. Determines the weight "
         "carried in handicaps and the races a horse is eligible for. Not a speed figure but "
         "used similarly."],
        ["Ragozin 'The Sheets' / Thoro-Graph", "Independent", "Lower is better. Plotted "
         "graphically over time to reveal form cycles. Explicitly adjusted for ground lost and "
         "weight."],
    ], [34 * mm, 40 * mm, 96 * mm], font_size=8.2,
        caption="Table 8.1 &mdash; The main figure families. Scales are not interchangeable; "
                "never compare a Beyer to a Timeform rating directly."))
    s.append(P(
        "The important limitation: because the leading figures are published, they are already "
        "in the price. Betting the top figure horse is a losing strategy on average, not "
        "because the figures are wrong but because everyone can see them. Figures are most "
        "useful for identifying horses whose figures <i>understate</i> them &mdash; a hidden "
        "trouble line, a wide trip, a race run into a brutal headwind, a first start off a "
        "layoff."))

    s.append(Paragraph("Running styles and pace scenarios", ST["h2"]))
    s.append(table([
        ["Style", "Abbreviation", "Behaviour", "Needs"],
        ["Front-runner", "E (early)", "Wants the lead and holds it", "An uncontested lead. "
         "Devastating if alone in front, vulnerable if pressed."],
        ["Pace presser", "E/P", "Sits just off the leader", "A lead to track. The most "
         "adaptable and generally the most profitable profile."],
        ["Stalker / midpack", "P (presser)", "Races in the middle, moves at the turn",
         "A moderate pace and a clear run."],
        ["Closer", "S (sustained)", "Last early, runs on late", "A fast, contested early pace "
         "that collapses. Needs the race to fall apart."],
    ], [28 * mm, 22 * mm, 44 * mm, 76 * mm], font_size=8.4,
        caption="Table 8.2 &mdash; Running styles. The abbreviations are those used by most "
                "North American form providers."))
    s.append(P(
        "The pace scenario is the interaction of these styles in a specific field, and it is "
        "the most reliable source of edge available to a bettor willing to do the work. The "
        "core insight is simple: the number of horses that want the lead determines who wins."))
    s.append(worked("Two pace shapes, opposite outcomes", [
        "FIELD A -- lone speed",
        "  1 front-runner, 3 pressers, 4 closers",
        "  The front-runner gets an uncontested, slow lead. It has",
        "  petrol left in the stretch. Closers arrive too late.",
        "  -> Bet the lone front-runner. Often over-priced because",
        "     the crowd sees a moderate horse, not a soft lead.",
        "",
        "FIELD B -- speed duel",
        "  4 front-runners, 1 presser, 3 closers",
        "  Four horses fight for the lead, each forcing the others",
        "  to run faster than they want. All four stop.",
        "  -> Bet the closers. The single presser is often the best",
        "     value of all: it inherits the lead without the fight.",
    ]))
    s.append(P(
        "Quirin speed points, published in some form guides, quantify early speed on a 0&ndash;8 "
        "scale from a horse's position at the first call in recent races. Summing the speed "
        "points across a field gives a quick read of whether a race is likely to be fast or "
        "slow early. It is crude, and it is far better than nothing."))
    s.append(callout(
        "Track bias: the variable that invalidates everything else",
        ["On some days a track favours a particular running style or a particular part of the "
         "course &mdash; the rail is fast, or dead; front-runners are winning every race, or "
         "none. A biased day produces speed figures and form lines that are simply wrong as "
         "predictors of future performance.",
         "Two disciplines follow. First, watch the early races on a card before betting "
         "seriously into the later ones, and note whether winners are coming from the front or "
         "from behind, on the rail or wide. Second, when reviewing past performances, ask "
         "whether the day the horse ran badly was a day its style could not win. Horses "
         "forgiven for a bias are among the most reliably over-priced runners in racing."]))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 9
def ch9():
    s = chapter(9, "Class, Form Cycles and Connections",
                "Speed says how fast. Class says against whom. Form cycle says whether "
                "today is the day.")
    s.append(P(
        "Class is the quality of company a horse has been keeping. It is measured crudely by "
        "the type of race &mdash; maiden, claiming, allowance, listed, group or graded &mdash; "
        "and more finely by purse value and by the ratings of the horses actually beaten.",
        "body_first"))
    s.append(table([
        ["Level", "North America", "Britain and Ireland", "Notes"],
        ["Bottom", "Maiden claiming", "Selling / claiming", "Horses that have never won, "
         "running for a price. The most volatile form in racing."],
        ["", "Claiming", "Claiming / banded", "Any horse can be bought out of the race. A drop "
         "in claiming price is a meaningful signal, in both directions."],
        ["", "Maiden special weight", "Maiden", "Non-winners of any race, no claiming price. "
         "Often contains genuinely good horses."],
        ["Middle", "Allowance / optional claiming", "Handicap (Class 5&ndash;2)", "Conditions "
         "races for winners. Where most careers are spent."],
        ["", "Starter allowance", "Class 3&ndash;2 handicap", "Restricted by prior claiming "
         "starts or rating band."],
        ["Top", "Listed / Grade 3", "Listed / Group 3", "Black type begins. Breeding value "
         "attaches to placings here."],
        ["", "Grade 2 / Grade 1", "Group 2 / Group 1", "Championship racing."],
    ], [16 * mm, 42 * mm, 42 * mm, 70 * mm], font_size=8.2,
        caption="Table 9.1 &mdash; A rough class ladder. Purse value is often a better guide to "
                "true class than the race's name, particularly across jurisdictions."))
    s.append(P(
        "The two class moves worth watching are the drop and the rise. A horse dropping in "
        "class is meeting easier company &mdash; but ask why. A drop from allowance to a "
        "modest claimer, from a barn that rarely does it, in a horse that has just run badly, "
        "often signals a physical problem the connections know about and you do not. "
        "Conversely a drop that follows a good but unlucky run at a higher level, especially "
        "from a barn with a strong record at the new level, is exactly the profile of a "
        "well-meant horse."))

    s.append(Paragraph("Form cycles", ST["h2"]))
    s.append(P(
        "Thoroughbreds do not hold peak fitness indefinitely. A typical cycle runs: a "
        "reappearance run after a layoff, often needed and short of peak; a sharp improvement "
        "second or third time out; a peak of two to four runs; then a decline requiring a "
        "freshening. Reading where a horse sits in this cycle is more predictive than its last "
        "figure in isolation."))
    s.append(bullets([
        "<b>First off a layoff.</b> Check the trainer's statistics with layoff runners "
        "specifically. Some barns win at 25% first time back; others need three runs. This is "
        "one of the highest-value data points in the form.",
        "<b>Second start off a layoff.</b> Frequently the sweet spot &mdash; fitness has "
        "arrived and the crowd is still pricing the poor reappearance run.",
        "<b>The bounce.</b> A horse producing a career-best figure, especially a lightly raced "
        "or recently returned one, often regresses next time. Treat a sudden large figure "
        "improvement with suspicion rather than enthusiasm.",
        "<b>Too many runs in a short window.</b> Four hard races in six weeks will flatten most "
        "horses. Look at the spacing, not just the results.",
        "<b>Workouts and gallops.</b> Regular, purposeful workouts after a layoff indicate "
        "intent. A horse returning with no recorded work is a horse whose trainer is not trying "
        "to tell you anything good.",
    ]))

    s.append(Paragraph("Connections: trainers, jockeys and intent", ST["h2"]))
    s.append(P(
        "Trainer statistics, broken down by category, are among the most robust predictive data "
        "available and are systematically under-weighted by casual bettors. The categories that "
        "matter are not the headline win percentage but the specific situational ones."))
    s.append(table([
        ["Statistic", "Why it matters", "What is a strong number"],
        ["First time with this trainer", "A new barn often revives a horse; some trainers "
         "specialise in it", "20%+ is notable; the field average is around 12&ndash;14%"],
        ["Off a layoff of 60&ndash;180 days", "Distinguishes barns that train them fit at home",
         "20%+ with a positive return is a genuine angle"],
        ["Second start off the layoff", "The classic improvement spot", "Compare directly "
         "against the same barn's first-off-layoff figure"],
        ["First-time blinkers / first-time Lasix", "A deliberate intervention", "Look for both "
         "a high strike rate and a positive ROI"],
        ["Dirt to turf, or sprint to route", "Surface and trip changes reveal intent", "Small "
         "samples; require several years of data before believing it"],
        ["Today's jockey combination", "Some trainers reserve their best rider for their best "
         "chance", "A stable's top jockey on a longshot in the barn's second string is a signal"],
    ], [42 * mm, 62 * mm, 66 * mm], font_size=8.2,
        caption="Table 9.2 &mdash; The trainer statistics worth looking up, and what counts as "
                "a meaningful number in each."))
    s.append(callout(
        "Beware of small samples",
        ["A trainer who is '3 for 5 with first-time starters' is very likely a trainer who has "
         "had five first-time starters. Sample sizes in the situational statistics printed in "
         "form guides are frequently in single digits, and at those sizes the numbers are "
         "noise dressed as insight.",
         "A useful rule of thumb: below about 30 starts in a category, treat the percentage as "
         "unreliable; below 10, ignore it entirely. Where a data provider offers a multi-year "
         "sample, use that instead of the current meet."],
        tone="caution"))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 10
def ch10():
    s = chapter(10, "Value: Building a Fair-Odds Line",
                "The central discipline. You are not trying to find winners. You are trying "
                "to find prices that are wrong.")
    s.append(P(
        "Everything so far has been input. This chapter is where the inputs become a bet, and "
        "the mechanism is a fair-odds line: your own estimate, made before you look at the "
        "board, of each horse's probability of winning. Comparing that line to the market is "
        "the only defensible reason to place a wager.", "body_first"))

    s.append(Paragraph("Odds and probability", ST["h2"]))
    s.append(P(
        "The conversions are simple and must become automatic. For fractional odds "
        "<i>a/b</i>, the implied probability is b/(a+b). For decimal odds <i>d</i>, it is 1/d. "
        "Going the other way, a probability <i>p</i> corresponds to fair decimal odds of 1/p "
        "and fair fractional odds of (1&minus;p)/p."))
    s.append(table([
        ["Fractional", "Decimal", "American", "Implied win probability", "Wins needed per 100 "
         "bets to break even"],
        ["1/5", "1.20", "&minus;500", "83.3%", "84"],
        ["1/2", "1.50", "&minus;200", "66.7%", "67"],
        ["Evens (1/1)", "2.00", "+100", "50.0%", "50"],
        ["2/1", "3.00", "+200", "33.3%", "34"],
        ["3/1", "4.00", "+300", "25.0%", "25"],
        ["9/2", "5.50", "+450", "18.2%", "19"],
        ["6/1", "7.00", "+600", "14.3%", "15"],
        ["10/1", "11.00", "+1000", "9.1%", "10"],
        ["20/1", "21.00", "+2000", "4.8%", "5"],
        ["50/1", "51.00", "+5000", "2.0%", "2"],
    ], [24 * mm, 20 * mm, 22 * mm, 40 * mm, 64 * mm], font_size=8.4,
        caption="Table 10.1 &mdash; Odds conversion. Appendix B gives a fuller table."))

    s.append(Paragraph("Making the line", ST["h2"]))
    s.append(numbered([
        "<b>Handicap the race with the odds hidden.</b> This is not optional. Once you have "
        "seen that a horse is 5/2 you cannot un-see it, and your 'independent' estimate will "
        "anchor to it.",
        "<b>Assign each runner a probability</b> of winning, as a percentage. Start with your "
        "top few and work down; give genuine no-hopers 1% rather than zero.",
        "<b>Make them sum to 100%.</b> They will not on the first pass. Scale everything "
        "proportionally until they do. This step alone catches an enormous amount of sloppy "
        "thinking &mdash; it is very easy to talk yourself into four horses at 30% each.",
        "<b>Convert each probability to fair odds</b> using (1&minus;p)/p.",
        "<b>Now look at the board.</b> Any horse whose market price is meaningfully longer than "
        "your fair odds is an overlay and a candidate bet. Any horse shorter is an underlay and "
        "is not a bet at any stake.",
        "<b>Apply a margin of safety.</b> Your line is not perfect. Requiring the market price "
        "to exceed your fair price by a set margin &mdash; 25% or more is a common discipline "
        "&mdash; protects you against your own optimism and against a late drop.",
    ]))
    s.append(worked("A completed line for an eight-runner handicap", [
        "Horse            My %    My fair odds   Board    Verdict",
        "Ashgrove          28%        5/2         2/1     UNDERLAY - no bet",
        "Ninebarrow        20%        4/1         6/1     OVERLAY  - bet",
        "Cranmere          16%        5/1         9/2     underlay - no bet",
        "Saltmarsh         12%        7/1        11/1     OVERLAY  - bet",
        "Bell Heather       9%       10/1         8/1     underlay - no bet",
        "Winterditch        7%       13/1        20/1     OVERLAY  - bet",
        "Owlpen             5%       19/1        16/1     underlay - no bet",
        "Redmire            3%       32/1        50/1     overlay  - too small to matter",
        "                 ----",
        "                 100%",
        "",
        "Three bets, applying a 25% margin over fair odds. Note that",
        "the horse I rate MOST likely to win is not one of them --",
        "that is the discipline working.",
    ]))
    s.append(P(
        "The final line of that example is the hardest habit in betting to acquire. Your "
        "opinion about which horse will win and your decision about which horse to back are "
        "different questions, and confusing them is the defining error of the recreational "
        "bettor. A 28% chance at 2/1 is a bad bet. A 7% chance at 20/1 is a good one. You will "
        "lose the second bet more than nine times in ten and it will still be the correct "
        "wager."))

    s.append(Paragraph("Expected value", ST["h2"]))
    s.append(P(
        "Expected value formalises the comparison. For a bet at decimal odds <i>d</i> with true "
        "probability <i>p</i>, staking one unit:"))
    s.append(worked("Expected value", [
        "EV  =  p x (d - 1)  -  (1 - p) x 1",
        "    =  p x d  -  1",
        "",
        "Positive EV means the bet is worth making. Examples:",
        "",
        "  p = 0.20, d = 7.00  ->  EV = 1.40 - 1 = +0.40  (+40% per unit)",
        "  p = 0.20, d = 5.00  ->  EV = 1.00 - 1 =  0.00  (break even)",
        "  p = 0.20, d = 4.00  ->  EV = 0.80 - 1 = -0.20  (-20% per unit)",
        "  p = 0.33, d = 3.00  ->  EV = 0.99 - 1 = -0.01  (marginally bad)",
        "",
        "In a pari-mutuel pool, d is not known when you bet. Use a",
        "conservative estimate of the FINAL price, not the current one.",
    ]))
    s.append(callout(
        "The uncomfortable truth about your line",
        ["The market's implied probabilities, stripped of takeout or overround, are a very "
         "good forecast. Decades of studies find that public odds are close to calibrated: "
         "horses sent off at 3/1 win close to 25% of the time, with a known bias against the "
         "longest prices.",
         "This means your line is competing with a well-informed consensus, and most of the "
         "time your line will be worse. The correct response is not to abandon the exercise but "
         "to bet rarely: on the small number of races where you have a specific, articulable "
         "reason to believe the crowd has missed something &mdash; a trip, a bias, a pace "
         "setup, a trainer angle &mdash; rather than on every race on the card."]))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 11
def ch11():
    s = chapter(11, "Bankroll and Staking",
                "The best handicapper in the world goes broke with bad staking. The "
                "arithmetic of ruin does not care how good your opinions are.")
    s.append(P(
        "A bankroll is money set aside for wagering, separate from money required for living. "
        "That separation is not a moral point but an operational one: staking rules only work "
        "if the total is fixed and known, and a bankroll that can be topped up from the rent "
        "is not a bankroll.", "body_first"))

    s.append(Paragraph("Flat staking", ST["h2"]))
    s.append(P(
        "Betting the same amount on every wager is the correct default for almost everyone. It "
        "is simple, it makes your records interpretable &mdash; profit is directly comparable "
        "across bets &mdash; and it removes the emotional escalation that destroys most "
        "accounts. A common rule is 1% to 3% of bankroll per bet, with 2% a reasonable "
        "starting point. At 2%, a twenty-bet losing run costs 40% of the bankroll and is survivable; at 10% the same run wipes you out twice over."))
    s.append(P(
        "The refinement worth making is <i>flat to win</i> rather than flat stake. Betting to "
        "win a fixed amount rather than to risk a fixed amount means larger stakes on short "
        "prices, which is usually wrong for a value bettor whose edge is concentrated at longer "
        "prices. Flat stake is the better default."))

    s.append(Paragraph("The Kelly criterion", ST["h2"]))
    s.append(P(
        "Kelly gives the stake that maximises the long-run growth rate of a bankroll, given a "
        "known edge. For a bet at decimal odds <i>d</i> with true win probability <i>p</i>, "
        "define b = d &minus; 1 (the profit per unit staked) and q = 1 &minus; p."))
    s.append(worked("Kelly stake", [
        "f* = ( b x p  -  q ) / b        as a fraction of bankroll",
        "",
        "equivalently   f* = ( p x d - 1 ) / ( d - 1 )   =   EV / b",
        "",
        "Example: p = 0.20, decimal odds 7.00, bankroll 5,000",
        "  b = 6.0,  q = 0.80",
        "  f* = (6.0 x 0.20 - 0.80) / 6.0 = 0.40 / 6.0 = 0.0667",
        "  full Kelly stake = 6.67% of 5,000 = 333",
        "",
        "Example: p = 0.20, decimal odds 5.00  (a fair price)",
        "  f* = (4.0 x 0.20 - 0.80) / 4.0 = 0 / 4.0 = 0",
        "  Kelly correctly says: do not bet.",
    ]))
    s.append(P(
        "Two properties make Kelly attractive: it never risks the whole bankroll, and it "
        "maximises long-run growth. One property makes it dangerous in practice: it assumes "
        "you know <i>p</i>. You do not. You have an estimate, and if that estimate is "
        "optimistic &mdash; as estimates by people who have just talked themselves into a bet "
        "reliably are &mdash; full Kelly over-stakes badly, and the resulting drawdowns are "
        "severe even when the edge is real."))
    s.append(table([
        ["Approach", "Stake", "Behaviour"],
        ["Full Kelly", "f*", "Maximum growth if p is exact. Drawdowns of 50% or more are "
         "routine. Over-estimating p by even a little produces over-betting that can be "
         "growth-negative."],
        ["Half Kelly", "f* / 2", "About 75% of the growth rate with roughly half the volatility. "
         "The standard recommendation for anyone estimating their own probabilities."],
        ["Quarter Kelly", "f* / 4", "Very conservative. Appropriate when your edge estimate is "
         "genuinely uncertain, which for most bettors is always."],
        ["Capped Kelly", "min(f*/2, cap)", "Half Kelly with a hard ceiling, commonly 3&ndash;5% "
         "of bankroll. Protects against a single miscalculated huge edge."],
    ], [26 * mm, 22 * mm, 122 * mm], font_size=8.4,
        caption="Table 11.1 &mdash; Fractional Kelly. Almost nobody estimating their own "
                "probabilities should be playing full Kelly."))
    s.append(callout(
        "Kelly in a pari-mutuel pool",
        ["Kelly assumes a fixed price. In a pari-mutuel pool your stake changes the price, so "
         "the correct calculation is a fixed point: the stake that is optimal given the odds "
         "that stake produces. In practice, compute Kelly against a conservatively estimated "
         "final price, then reduce further if the pool is small relative to your bet. If your "
         "bet is more than about 1% of the pool, its effect on the price is not negligible."]))

    s.append(Paragraph("Dutching and hedging", ST["h2"]))
    s.append(P(
        "Dutching means backing several horses in the same race in proportions that return the "
        "same profit whichever of them wins. It is worth doing when you have identified two or "
        "three overlays and cannot separate them, and it is worth <i>not</i> doing when it is "
        "merely a way of avoiding a decision."))
    s.append(worked("Dutching three runners for a level return", [
        "Target total outlay: 100.  Runners at decimal 4.0, 6.0, 11.0",
        "",
        "  1/4.0 = 0.2500     1/6.0 = 0.1667     1/11.0 = 0.0909",
        "  sum of reciprocals = 0.5076   (i.e. book of 50.76%)",
        "",
        "  stake on each = 100 x (its reciprocal) / 0.5076",
        "    at 4.0  ->  100 x 0.2500 / 0.5076 =  49.25",
        "    at 6.0  ->  100 x 0.1667 / 0.5076 =  32.84",
        "    at 11.0 ->  100 x 0.0909 / 0.5076 =  17.91",
        "                                        ------",
        "                                        100.00",
        "",
        "Any winner returns 49.25 x 4.0 = 197.0 (same for the others).",
        "Profit 97.0 if any of the three wins; -100 otherwise.",
        "",
        "The bet is good only if your combined estimate of the three",
        "horses' chances exceeds 50.76%.",
    ]))
    s.append(P(
        "The reciprocal sum is the key diagnostic. If the reciprocals of your selections' odds "
        "sum to 0.5076, you need those horses to win a combined 50.76% of the time to break "
        "even. Writing that number down before staking converts a vague feeling that 'one of "
        "these three must win' into a testable claim."))

    s.append(Paragraph("Drawdown, variance and the length of a bad run", ST["h2"]))
    s.append(P(
        "Losing runs are longer than intuition suggests. A bettor with a genuine edge backing "
        "horses at an average 8/1 wins roughly one bet in nine. The probability of at least "
        "one run of twenty consecutive losses over a season of a thousand bets is close to "
        "certain. This is not a sign that the method has stopped working; it is the arithmetic "
        "of an 11% strike rate."))
    s.append(table([
        ["Average price", "Approx. strike rate", "Chance of a 20-loss run in 500 bets",
         "Bankroll units to survive comfortably"],
        ["2/1", "33%", "Very low", "50&ndash;100"],
        ["5/1", "17%", "Very likely &mdash; about 90%", "100&ndash;200"],
        ["10/1", "9%", "Near certain", "200&ndash;400"],
        ["25/1", "4%", "Certain; 50-loss runs are routine", "500+"],
    ], [26 * mm, 30 * mm, 56 * mm, 50 * mm], font_size=8.4,
        caption="Table 11.2 &mdash; The longer the prices you play, the deeper the bankroll you "
                "need for the same level of comfort. Figures are indicative, assuming a small "
                "positive edge."))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 12
def ch12():
    s = chapter(12, "Records, Metrics and Knowing Whether You Are Any Good",
                "Almost every losing bettor believes they are close to breaking even. "
                "Records are how you find out.")
    s.append(P(
        "Memory is a hostile witness. It preserves the 25/1 winner in vivid detail and quietly "
        "discards eleven losing favourites. Any assessment of your own betting that is not "
        "written down at the time of the bet is worthless, and this is true of experienced "
        "bettors as much as beginners.", "body_first"))

    s.append(Paragraph("What to record, at the time of the bet", ST["h2"]))
    s.append(table([
        ["Field", "Why"],
        ["Date, track, race number", "Lets you find the replay and the chart later."],
        ["Selection and bet type", "Obvious, and routinely omitted."],
        ["Stake and total ticket cost", "For exotics these differ; record both."],
        ["Odds taken, and odds at the off", "The gap between them measures whether you are "
         "beating the closing line &mdash; the single best leading indicator of skill."],
        ["Your estimated probability", "Without this you cannot ever calibrate. Record it "
         "before the result."],
        ["Reason for the bet, in one line", "'Lone speed, drops in class' is a category you can "
         "later analyse. 'Looked good' is not."],
        ["Result and return", "Gross return, not profit &mdash; compute profit later."],
    ], [52 * mm, 118 * mm], font_size=8.4,
        caption="Table 12.1 &mdash; The minimum useful bet log. Every field must be filled in "
                "before the race runs, except the last."))

    s.append(Paragraph("The metrics that matter", ST["h2"]))
    s.append(worked("Core performance metrics", [
        "Turnover        = total amount staked",
        "Net profit      = total returned  -  turnover",
        "ROI             = net profit / turnover           (as a %)",
        "Strike rate     = winning bets / total bets",
        "Average odds    = mean decimal odds of all bets struck",
        "Yield per bet   = net profit / number of bets",
        "",
        "Closing line value (CLV):",
        "  CLV per bet   = (odds taken / odds at the off) - 1",
        "  Positive average CLV means you are consistently getting",
        "  a better price than the final market. Over a few hundred",
        "  bets this predicts long-run profitability far better",
        "  than your actual profit does.",
    ]))
    s.append(P(
        "ROI is the headline number and it deserves a warning: it is extremely noisy at small "
        "sample sizes, and it is noisier the longer the prices you play. A hundred bets at an "
        "average of 10/1 tells you almost nothing about your ROI, because a single extra winner "
        "moves it by eleven percentage points. Do not draw conclusions from a hundred bets. Draw "
        "tentative conclusions from five hundred and firmer ones from two thousand."))
    s.append(P(
        "This is why closing line value is worth tracking. If you take 6/1 about a horse that "
        "starts at 4/1, you have beaten the market's final assessment, and you have done so in "
        "a way that does not depend on whether the horse won. CLV accumulates signal far faster "
        "than profit does, and a bettor with consistently positive CLV and negative profit is "
        "almost always suffering variance rather than a broken method."))

    s.append(Paragraph("Segmenting the record", ST["h2"]))
    s.append(P(
        "The purpose of records is to find out which parts of your betting are working. Segment "
        "by every dimension you can, and be prepared for the answer to be unflattering."))
    s.append(bullets([
        "<b>By bet type.</b> The commonest finding by far: a bettor is comfortably profitable on "
        "win bets and loses it all back on exotics.",
        "<b>By price band.</b> Are your longshots winning at anything like the implied rate? "
        "This is a direct calibration check.",
        "<b>By race type, surface, distance and field size.</b> Many bettors have a real edge in "
        "a narrow niche and none outside it.",
        "<b>By reason code.</b> If 'lone speed' returns +14% over 300 bets and 'trainer angle' "
        "returns &minus;30%, you have learned something worth more than any tip.",
        "<b>By time of day and day of week.</b> An unglamorous but frequently revealing cut. "
        "Late-card bets after a losing day are, for most people, the worst bets they make.",
    ]))
    s.append(callout(
        "Calibration: the test that cannot be faked",
        ["Group all your bets by the probability you assigned them. Take every bet where you "
         "said 20%. Did close to 20% of them win?",
         "If your 20% horses win 12% of the time, you are systematically over-confident and "
         "your entire fair-odds line is inflated &mdash; which means bets you scored as "
         "overlays were not. This single check, run over a few hundred bets, is the most "
         "valuable diagnostic in this guide, and it is only possible if you wrote the "
         "probability down before the race."]))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 13
def ch13():
    s = chapter(13, "The Modern Pool: Syndicates, Rebates and Automated Play",
                "Who else is in the pool with you, and why the game changed.")
    s.append(P(
        "The recreational bettor's mental model of a pari-mutuel pool &mdash; a few thousand "
        "people at a racetrack, each backing a fancy &mdash; has not been accurate for decades. "
        "A substantial share of the money in major North American pools comes from "
        "computer-assisted wagering teams: syndicates running quantitative models, betting "
        "large volumes across many tracks, and operating on rebate arrangements that "
        "materially reduce their effective takeout.", "body_first"))
    s.append(P(
        "This matters to you in three concrete ways, and none of them is a reason to stop "
        "betting."))
    s.append(numbered([
        "<b>Late odds movement is structural, not sinister.</b> Automated players submit in the "
        "final seconds precisely so their price impact is not observable in time for others to "
        "react. Prices will drop after you bet. Price your bets accordingly.",
        "<b>The most efficiently priced bets are the ones models handle well.</b> Win pools on "
        "large-field races at major tracks are heavily modelled. The residual inefficiency "
        "tends to sit where models are weakest &mdash; small fields, unusual conditions, "
        "first-time starters, horses whose form requires watching a replay rather than reading "
        "a number.",
        "<b>Effective takeout differs between participants.</b> A syndicate on a 10% rebate is "
        "playing a 10% takeout game while you play a 20% one. You cannot fix this by "
        "handicapping better; you can partially fix it by using a platform that rebates and by "
        "betting into lower-takeout pools.",
    ]))

    s.append(Paragraph("Account wagering and where to bet", ST["h2"]))
    s.append(P(
        "Advance-deposit wagering (ADW) platforms let you fund an account and bet into "
        "commingled pools remotely. Choosing between them is a genuine and under-appreciated "
        "decision, and it is worth more to most bettors than any handicapping improvement they "
        "will make this year."))
    s.append(table([
        ["Consideration", "What to look for"],
        ["Rebate or rewards structure", "Is it a cash rebate on handle, or points redeemable for "
         "merchandise? Cash on handle is worth several times its nominal value in points."],
        ["Which tracks and pools are offered", "Not every platform carries every track, and "
         "low-takeout pools are exactly the ones you want access to."],
        ["Takeout transparency", "The best platforms publish a takeout schedule per track and "
         "pool. Treat its absence as a warning."],
        ["Bet-entry tooling", "Can you build and cost a part-wheel before submitting? Can you "
         "see pool sizes and will-pays? These prevent expensive mistakes."],
        ["Data included", "Some platforms bundle past performances, replays and figures. "
         "Priced separately these are a significant annual cost."],
        ["Withdrawal terms and licensing", "Confirm the operator is licensed in your "
         "jurisdiction and understand the withdrawal timetable before you deposit."],
    ], [46 * mm, 124 * mm], font_size=8.4,
        caption="Table 13.1 &mdash; Choosing an account wagering platform. For most bettors "
                "this decision is worth more than a year of handicapping improvement."))

    s.append(Paragraph("Will-pays, probables and reading the other pools", ST["h2"]))
    s.append(P(
        "The tote publishes more than win odds. Exacta probables show what each two-horse "
        "combination would pay; double will-pays show what each horse in the second leg would "
        "return given the winner of the first. These are free information about how the crowd "
        "is betting in pools other than the one you are watching, and discrepancies between "
        "them are occasionally exploitable."))
    s.append(bullets([
        "<b>A horse much better supported in the exacta pool than the win pool</b> is often "
        "being backed by people using it underneath &mdash; or by people who know something. "
        "Either way it is information the win-pool odds do not contain.",
        "<b>Double will-pays reveal opinions about the next race</b> before that race's own "
        "pools have meaningful money in them. If one horse's will-pay is far shorter than its "
        "morning line implies, the market has already formed a view.",
        "<b>Large discrepancies are usually explained by a large single ticket</b>, not by "
        "insider knowledge. Do not over-read them.",
    ]))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 14
def ch14():
    s = chapter(14, "Common Errors and How They Cost Money",
                "A catalogue of the specific, repeatable mistakes that separate losing "
                "bettors from breaking-even ones.")
    s.append(P(
        "Most losing bettors are not bad judges of horses. They are decent judges of horses "
        "making a small number of structural errors, repeatedly, with real money. The list "
        "below is ordered roughly by how much it costs the average player.", "body_first"))

    items = [
        ("Betting every race",
         "Takeout is charged per bet, not per day. A bettor who plays eleven races has paid "
         "eleven tolls to express perhaps two genuine opinions. The single highest-value change "
         "most bettors can make is to pass more races &mdash; and passing is a skill that "
         "requires the same deliberate practice as selecting."),
        ("Confusing the most likely winner with the best bet",
         "These are different questions with different answers. Backing the horse you think "
         "will win, at any price, is a strategy with a guaranteed long-run loss equal to the "
         "takeout. The bet is the discrepancy, not the horse."),
        ("Chasing losses",
         "Increasing stakes after losing converts a small negative expectation into a large "
         "one and destroys the interpretability of your records. Every progressive staking "
         "system ever devised &mdash; martingale, Fibonacci, d'Alembert &mdash; converts a "
         "high probability of small wins into a small probability of catastrophic loss. None "
         "of them changes expectation, because expectation is a property of the bets and not "
         "of the sequence."),
        ("Betting exotics with straight-bet-sized opinions",
         "A trifecta requires you to be right about three positions and charges you a quarter "
         "of your stake for the privilege. If your opinion supports one horse, bet one horse."),
        ("Boxing everything",
         "A box asserts that all orderings are equally likely, which contradicts the opinion "
         "that made you select the horses. Structure instead."),
        ("Ignoring takeout when choosing a bet type",
         "Playing the 25% superfecta at a track offering a 15% Pick 5 is a ten-point handicap "
         "chosen voluntarily and usually unknowingly."),
        ("Anchoring on the morning line or the current board",
         "The morning line is the track handicapper's estimate of how the public will bet, not "
         "an estimate of probability. Looking at it before making your own line contaminates "
         "the exercise."),
        ("Over-weighting the last run",
         "Recency bias is the crowd's most consistent flaw and therefore your most consistent "
         "opportunity &mdash; but only if you are not doing it too. A horse's last race is one "
         "data point run under one set of conditions."),
        ("Backing the top speed figure",
         "The figure is printed. Everyone can see it. It is in the price. Figures create value "
         "when they are wrong or when they conceal something, not when they are highest."),
        ("Treating a big-race day like a normal day",
         "Championship days attract enormous casual money, which distorts pools in predictable "
         "directions &mdash; towards famous horses, famous jockeys, and recognisable names. "
         "This is an opportunity, but only for a bettor who has not also become excited."),
        ("Failing to shop the price",
         "In fixed-odds markets, taking the first price you see is a straightforward donation. "
         "The difference between the best and worst available price on a mid-priced horse is "
         "routinely 10% or more of the return."),
        ("Betting under the influence, or tired, or angry",
         "Trite, true, and responsible for a substantial share of lifetime losses. The last "
         "race of a losing day, bet from a phone in a bad mood, is statistically the worst bet "
         "most people ever make."),
    ]
    for title, body in items:
        s.append(Paragraph(title, ST["h3"]))
        s.append(P(body))

    s.append(Spacer(1, 4))
    s.append(callout(
        "The meta-error",
        ["Underneath most of the list is one habit: making the bet first and finding the reason "
         "afterwards. Every discipline in this guide &mdash; handicapping with the odds hidden, "
         "writing the probability down before the race, recording a reason code, requiring a "
         "margin over fair odds &mdash; exists to force the reasoning to come first.",
         "If you adopt nothing else from this document, adopt the rule that no bet is placed "
         "until you have written down, in advance, the price at which you would decline it."]))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Chapter 15
def ch15():
    s = chapter(15, "Regulation, Integrity and Player Protection",
                "The rules that govern the wager, the sport, and &mdash; most importantly "
                "&mdash; you.")
    s.append(P(
        "Horse racing is among the most heavily regulated forms of gambling, largely for "
        "historical reasons: pari-mutuel wagering was legalised in many jurisdictions long "
        "before other forms of betting, under statutes that tied the industry closely to state "
        "supervision. The details vary enormously, and the summary below is orientation only.",
        "body_first"))

    s.append(Paragraph("Jurisdictional sketch", ST["h2"]))
    s.append(table([
        ["Jurisdiction", "Structure", "Notes"],
        ["United States", "Predominantly pari-mutuel, regulated state by state. Interstate account "
         "wagering is permitted under federal law subject to state consent.",
         "Legality of ADW, the tracks available and the takeout rates all differ by state. "
         "Fixed-odds horse wagering has been introduced in a small number of states and remains "
         "the exception."],
        ["Britain and Ireland", "Fixed-odds bookmaking dominates, with a tote and a betting "
         "exchange operating alongside.",
         "Licensed and supervised by the national gambling regulator; racing itself is governed "
         "separately by the racing authority."],
        ["Australia", "Both totalisator and licensed fixed-odds corporate bookmakers.",
         "State-based licensing; substantial product fees paid by operators to racing bodies."],
        ["Hong Kong, Japan, France", "Monopoly pari-mutuel operators.",
         "Very large pools, high takeout in some cases, with a substantial share of revenue "
         "returned to the sport."],
        ["Canada", "Pari-mutuel, federally supervised.",
         "Commingled with US pools for many events."],
    ], [30 * mm, 62 * mm, 78 * mm], font_size=8.2,
        caption="Table 15.1 &mdash; Indicative only. Verify the current position in your own "
                "jurisdiction before betting; this landscape changes frequently."))

    s.append(Paragraph("Integrity", ST["h2"]))
    s.append(P(
        "Bettors have a direct financial interest in integrity, since every undisclosed factor "
        "affecting a horse's performance is a hidden tax on the informed. Modern integrity "
        "frameworks address medication control, out-of-competition testing, whip rules, "
        "raceday veterinary inspection, and the reporting of ownership and betting interests. "
        "In the United States the Horseracing Integrity and Safety Act established a national "
        "framework replacing what had been a patchwork of state rules, covering racetrack "
        "safety and anti-doping. Britain, Ireland, Hong Kong and Japan operate long-standing "
        "national integrity units with broad investigatory powers."))
    s.append(bullets([
        "<b>Stewards' inquiries and objections.</b> A result is not final until declared "
        "official. Never tear up a ticket before the board shows official, and understand that "
        "demotion rules differ by jurisdiction &mdash; the standard for taking a horse down "
        "varies considerably between North America and Europe.",
        "<b>Late scratches.</b> Rules for refunds and for substitute selections in multi-leg "
        "bets vary. In many pari-mutuel jurisdictions a scratched horse in a multi-race bet is "
        "replaced by the post-time favourite rather than refunded. Know this before it happens "
        "to you.",
        "<b>Dead heats.</b> The pool is divided among the tied runners; in fixed-odds markets "
        "the stake is reduced proportionally and paid at full odds. A two-way dead heat "
        "typically pays half your stake at full odds.",
        "<b>Void and abandoned races.</b> Rules differ for meetings abandoned mid-card, "
        "particularly for multi-race bets. Consult the operator's terms.",
    ]))

    s.append(Paragraph("Player protection", ST["h2"]))
    s.append(P(
        "Betting on horses is a form of gambling, and gambling harms a meaningful minority of "
        "the people who do it. The features that make racing intellectually engaging &mdash; "
        "frequent events, complex bets, the feeling that study confers control &mdash; are also "
        "the features that make it capable of causing serious harm. That risk is not eliminated "
        "by being good at handicapping; several of the tools in this guide can make it worse by "
        "sustaining the belief that the next bet is the one that corrects everything."))
    s.append(bullets([
        "<b>Set deposit limits before you need them.</b> Every licensed operator offers them. "
        "Setting one on a calm day is easy and setting one on a bad day is impossible.",
        "<b>Never bet with borrowed money</b>, and never with money allocated to anything else. "
        "A bankroll that can be topped up is not a bankroll.",
        "<b>Take the time-out and self-exclusion tools seriously.</b> They exist, they are free, "
        "and they work.",
        "<b>Watch for the specific warning signs</b>: betting more to recover losses, betting "
        "on races you have not studied, hiding the extent of your betting, borrowing, and "
        "feeling that you cannot stop.",
        "<b>Seek help early.</b> National support services exist in every regulated market and "
        "are free and confidential. In Britain, GamCare and the National Gambling Helpline; in "
        "the United States, the National Problem Gambling Helpline; elsewhere, the regulator's "
        "website lists local services.",
    ]))
    s.append(callout(
        "The honest summary",
        ["Most people who bet on horse racing lose money over time, and this is a mathematical "
         "consequence of takeout rather than a failure of effort or intelligence. A small "
         "minority profit, usually through some combination of low effective takeout, a narrow "
         "and genuine specialisation, rigorous staking, and a great deal of work.",
         "Treat the money you bet as the price of an absorbing pastime, and any profit as a "
         "pleasant surprise. Anyone selling you a different framing &mdash; a system, a "
         "guaranteed tipping service, a bot &mdash; is selling you the takeout."],
        tone="caution"))
    s.append(PageBreak())
    return s


# ---------------------------------------------------------------- Appendices
def app_a():
    s = appendix("A", "Glossary",
                 "Terms as used in this guide. Regional variants are noted where they differ.")
    terms = [
        ("Across the board", "Three equal bets on one horse: win, place and show."),
        ("Allowance race", "A race for winners with conditions that adjust the weight carried; "
         "above claiming and below stakes level."),
        ("Ante-post", "A fixed-odds bet struck well in advance of a race, usually forfeit if "
         "the horse does not run."),
        ("Bounce", "A regression in performance immediately following an unusually good effort."),
        ("Breakage", "The rounding down of pari-mutuel payouts to a set increment; the "
         "remainder is retained by the track and the state."),
        ("Bridge-jumper", "A bettor placing very large show wagers on short-priced horses for a "
         "small percentage return."),
        ("Carryover", "Money in a multi-race pool that was not won and is added to a later "
         "day's pool."),
        ("Chalk", "The favourite. 'Chalk player' means someone who habitually backs favourites."),
        ("Claiming race", "A race in which every runner may be purchased for a stated price."),
        ("Closing line value (CLV)", "The difference between the odds you took and the odds at "
         "the off; a leading indicator of long-run skill."),
        ("Commingling", "Combining wagers from multiple locations into a single host pool."),
        ("Dead heat", "A tied finish. Pari-mutuel pools split; fixed-odds stakes are reduced "
         "proportionally and paid at full odds."),
        ("Dutching", "Backing several runners in one race in proportions that yield the same "
         "return whichever wins."),
        ("Each-way", "Two equal bets, one to win and one to place at fractional odds. Chiefly "
         "British and Irish."),
        ("Exacta", "A bet on the first two finishers in exact order. Called a forecast in "
         "Britain and Ireland."),
        ("Exotic", "Any wager other than win, place or show."),
        ("Fair odds", "The price at which a bet has zero expected value, given your estimated "
         "probability."),
        ("Form cycle", "The pattern of a horse's fitness and performance across successive runs."),
        ("Furlong", "One-eighth of a mile, 220 yards, about 201 metres."),
        ("Going", "The condition of the racing surface. British terminology runs from hard "
         "through firm, good, soft to heavy."),
        ("Handicap", "A race in which weights are assigned to equalise the runners' chances; "
         "also, the act of analysing a race."),
        ("Handle", "The total amount wagered."),
        ("Key horse", "A horse used in a fixed position in an exotic ticket while others vary."),
        ("Lasix (furosemide)", "A diuretic used in some jurisdictions to reduce exercise-induced "
         "pulmonary bleeding; its first-time use is a notable form angle."),
        ("Maiden", "A horse that has never won a race."),
        ("Minus pool", "A pool in which the guaranteed minimum payout exceeds the amount "
         "available, requiring the track to contribute."),
        ("Morning line", "The track handicapper's published forecast of how the public will bet "
         "&mdash; not a probability estimate."),
        ("Overlay", "A horse whose market price is longer than your estimated fair price."),
        ("Overround", "The amount by which a fixed-odds book's implied probabilities exceed "
         "100%; the bookmaker's margin."),
        ("Pari-mutuel", "Pool betting in which all wagers of a type are combined and shared by "
         "the winners after takeout."),
        ("Part-wheel", "An exotic ticket using different lists of horses in different positions."),
        ("Placepot", "A British and Irish tote bet requiring a placed runner in each of six "
         "races."),
        ("Rebate", "A percentage of handle returned to a bettor regardless of outcome, reducing "
         "effective takeout."),
        ("Rule 4", "The British and Irish scale of deductions applied to winnings when a horse "
         "is withdrawn after a market has formed."),
        ("Scratch", "A horse withdrawn from a race after entry."),
        ("Speed figure", "A number expressing a performance's speed, adjusted for track "
         "conditions and distance to allow comparison."),
        ("Starting price (SP)", "The officially returned odds at the moment the race begins, in "
         "fixed-odds markets."),
        ("Takeout", "The percentage removed from a pari-mutuel pool before payouts."),
        ("Trifecta", "A bet on the first three finishers in exact order. Called a tricast in "
         "Britain and Ireland."),
        ("Underlay", "A horse whose market price is shorter than your estimated fair price."),
        ("Variant", "A daily adjustment measuring how fast or slow a track played, used in "
         "computing speed figures."),
        ("Wheel", "An exotic ticket in which one position is fixed and all other runners are "
         "used in the remaining positions."),
        ("Will-pay", "The tote's published payout for each possible outcome of a pending "
         "multi-leg or combination bet."),
    ]
    rows = [[Paragraph(t, ST["glossterm"]), Paragraph(d, ST["glossdef"])] for t, d in terms]
    tb = Table(rows, colWidths=[42 * mm, 128 * mm], repeatRows=0, hAlign="LEFT")
    cmds = [("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("LINEBELOW", (0, 0), (-1, -2), 0.3, RULE)]
    for i in range(0, len(rows), 2):
        cmds.append(("BACKGROUND", (0, i), (-1, i), WASH))
    tb.setStyle(TableStyle(cmds))
    s.append(tb)
    s.append(PageBreak())
    return s


def app_b():
    s = appendix("B", "Odds Conversion Table",
                 "Fractional, decimal and American odds with implied probability. Implied "
                 "probability here is the break-even win rate for a bet at that price.")
    rows = [["Fractional", "Decimal", "American", "Implied %", "Fractional", "Decimal",
             "American", "Implied %"]]
    M = "&minus;"
    left = [("1/10", 1.10, M + "1000"), ("1/5", 1.20, M + "500"),
            ("2/7", 9.0 / 7.0, M + "350"), ("1/3", 4.0 / 3.0, M + "300"),
            ("2/5", 1.40, M + "250"), ("1/2", 1.50, M + "200"),
            ("8/13", 21.0 / 13.0, M + "163"), ("4/5", 1.80, M + "125"),
            ("10/11", 21.0 / 11.0, M + "110"),
            ("1/1", 2.00, "+100"), ("11/10", 2.10, "+110"), ("5/4", 2.25, "+125"),
            ("11/8", 2.375, "+138"), ("6/4", 2.50, "+150"), ("13/8", 2.625, "+163"),
            ("7/4", 2.75, "+175"), ("15/8", 2.875, "+188"), ("2/1", 3.00, "+200")]
    right = [("9/4", 3.25, "+225"), ("5/2", 3.50, "+250"), ("11/4", 3.75, "+275"),
             ("3/1", 4.00, "+300"), ("7/2", 4.50, "+350"), ("4/1", 5.00, "+400"),
             ("9/2", 5.50, "+450"), ("5/1", 6.00, "+500"), ("6/1", 7.00, "+600"),
             ("8/1", 9.00, "+800"), ("10/1", 11.00, "+1000"), ("12/1", 13.00, "+1200"),
             ("14/1", 15.00, "+1400"), ("16/1", 17.00, "+1600"), ("20/1", 21.00, "+2000"),
             ("25/1", 26.00, "+2500"), ("33/1", 34.00, "+3300"), ("50/1", 51.00, "+5000")]
    # The epsilon forces exact .xx5 decimals (11/8, 13/8) to round up
    # consistently; Python's default round-half-even would send 2.375 up and
    # 2.625 down, which looks like a mistake in a printed table.
    def dec(d):
        return "%.2f" % (d + 1e-9)

    for (lf, ld, la), (rf, rd, ra) in zip(left, right):
        rows.append([lf, dec(ld), la, "%.1f%%" % (100.0 / ld),
                     rf, dec(rd), ra, "%.1f%%" % (100.0 / rd)])
    s.append(table(rows, [20 * mm, 18 * mm, 21 * mm, 20 * mm,
                          20 * mm, 18 * mm, 21 * mm, 20 * mm],
                   font_size=8.2,
                   caption="Table B.1 &mdash; Implied probability is 1/decimal odds. A book's "
                           "implied probabilities sum to more than 100%; the excess is the "
                           "overround."))

    # Bundled explicitly: this block is just over the automatic threshold in
    # bind_headings, and the page it would otherwise head is already short.
    s.append(KeepTogether([
        Paragraph("Converting a probability to a price", ST["h2"]),
        worked("Both directions", [
        "probability -> odds        odds -> probability",
        "  decimal   d = 1 / p        p = 1 / d",
        "  fraction  a/b where        p = b / (a + b)",
        "            a/b = (1-p)/p",
        "  American  if p < 0.5:      if odds are +A:  p = 100 / (A + 100)",
        "              +A, A = 100(1-p)/p",
        "            if p > 0.5:      if odds are -A:  p = A / (A + 100)",
        "              -A, A = 100p/(1-p)",
        "",
        "Worked: p = 0.15",
        "  decimal  = 1/0.15   = 6.67",
        "  fraction = 0.85/0.15 = 5.67/1, i.e. about 11/2",
        "  American = 100 x 0.85/0.15 = +567",
        ]),
    ]))
    s.append(PageBreak())
    return s


def app_c():
    s = appendix("C", "Reference Tables",
                 "Deduction scales, ticket costs and pool arithmetic, collected for use at the "
                 "window.")

    s.append(Paragraph("C.1 &nbsp;Rule 4 deductions (Britain and Ireland)", ST["h2"]))
    s.append(P(
        "When a horse is withdrawn before coming under starter's orders and there is "
        "insufficient time to re-form the market, a deduction is applied to winnings on bets "
        "struck at prices agreed before the withdrawal. The deduction depends on the odds of "
        "the withdrawn horse at the time of withdrawal. Stakes are returned in full; the "
        "deduction applies to winnings only."))
    s.append(table([
        ["Odds of withdrawn horse", "Deduction from winnings"],
        ["1/9 or shorter", "90p in the pound"],
        ["2/11 to 2/17", "85p"],
        ["1/4 to 1/5", "80p"],
        ["3/10 to 2/7", "75p"],
        ["2/5 to 1/3", "70p"],
        ["8/15 to 4/9", "65p"],
        ["8/13 to 4/7", "60p"],
        ["4/5 to 4/6", "55p"],
        ["20/21 to 5/6", "50p"],
        ["6/5 to Evens", "45p"],
        ["6/4 to 5/4", "40p"],
        ["7/4 to 8/5", "35p"],
        ["9/4 to 9/5", "30p"],
        ["3/1 to 12/5", "25p"],
        ["4/1 to 16/5", "20p"],
        ["11/2 to 9/2", "15p"],
        ["9/1 to 6/1", "10p"],
        ["14/1 to 10/1", "5p"],
        ["Longer than 14/1", "No deduction"],
    ], [60 * mm, 50 * mm], font_size=8.2,
        caption="Table C.1 &mdash; The standard scale. Where more than one horse is withdrawn "
                "the deductions are combined, capped at a maximum total. Operators' own rules "
                "govern; check them."))
    s.append(worked("Applying a Rule 4", [
        "You back a horse at 6/1 for GBP 20. A 5/2 shot is withdrawn.",
        "",
        "  Deduction for a 5/2 withdrawal = 25p in the pound = 25%",
        "  Gross winnings   = 20 x 6 = 120",
        "  Deduction        = 120 x 0.25 = 30",
        "  Net winnings     = 90",
        "  Total returned   = 90 + 20 stake = 110",
        "",
        "Effective price received: 90/20 = 4.5, i.e. 9/2.",
    ]))

    s.append(Paragraph("C.2 &nbsp;Exotic ticket cost quick reference", ST["h2"]))
    s.append(table([
        ["Horses used", "Exacta box", "Trifecta box", "Superfecta box", "Trifecta key<br/>"
         "(1 over n&minus;1)", "Superfecta key<br/>(1 over n&minus;1)"],
        ["3", "6", "6", "&mdash;", "2", "&mdash;"],
        ["4", "12", "24", "24", "6", "6"],
        ["5", "20", "60", "120", "12", "24"],
        ["6", "30", "120", "360", "20", "60"],
        ["7", "42", "210", "840", "30", "120"],
        ["8", "56", "336", "1,680", "42", "210"],
        ["9", "72", "504", "3,024", "56", "336"],
        ["10", "90", "720", "5,040", "72", "504"],
    ], [24 * mm, 24 * mm, 26 * mm, 30 * mm, 32 * mm, 34 * mm], font_size=8.4,
        caption="Table C.2 &mdash; Number of combinations. Multiply by the base unit for cost. "
                "'Key' means one horse fixed to win with the remaining horses filling the other "
                "positions in any order."))

    s.append(Paragraph("C.3 &nbsp;Multi-race ticket costs", ST["h2"]))
    s.append(table([
        ["Structure", "Combos", "at $0.50", "at $1", "at $2"],
        ["1 x 2 x 2 x 2 (Pick 4)", "8", "$4.00", "$8", "$16"],
        ["1 x 3 x 4 x 2 (Pick 4)", "24", "$12.00", "$24", "$48"],
        ["2 x 3 x 3 x 4 (Pick 4)", "72", "$36.00", "$72", "$144"],
        ["1 x 4 x 5 x 6 (Pick 4)", "120", "$60.00", "$120", "$240"],
        ["1 x 2 x 3 x 3 x 4 (Pick 5)", "72", "$36.00", "$72", "$144"],
        ["2 x 3 x 4 x 4 x 5 (Pick 5)", "480", "$240.00", "$480", "$960"],
        ["1 x 2 x 3 x 4 x 4 x 5 (Pick 6)", "480", "$240.00", "$480", "$960"],
        ["2 x 3 x 3 x 4 x 4 x 6 (Pick 6)", "1,728", "$864.00", "$1,728", "$3,456"],
    ], [56 * mm, 24 * mm, 28 * mm, 26 * mm, 26 * mm], font_size=8.4,
        caption="Table C.3 &mdash; Cost is the product of the horses used in each leg, times "
                "the base unit."))

    # Bundled explicitly: the block is over the bind_headings threshold, and
    # the page it would otherwise head is already nearly full.
    s.append(KeepTogether([
        Paragraph("C.4 &nbsp;Pool payout formulas, collected", ST["h2"]),
        worked("Every formula in this guide, in one place", [
        "WIN",
        "  payout per $2 = 2 x [ W(1-t) ] / w        then apply breakage",
        "",
        "PLACE  (placed horses A and B)",
        "  profit pool = P(1-t) - p(A) - p(B)",
        "  per $2 on A = 2 x [ profit pool/2 + p(A) ] / p(A)",
        "",
        "SHOW   (placed horses A, B and C)",
        "  profit pool = S(1-t) - s(A) - s(B) - s(C)",
        "  per $2 on A = 2 x [ profit pool/3 + s(A) ] / s(A)",
        "",
        "ANY EXOTIC (single winning combination)",
        "  payout per unit = [ X(1-t) ] / (units on the winning combination)",
        "",
        "OVERROUND         = sum of (1 / decimal odds) across all runners",
        "EXPECTED VALUE    = p x d - 1              per unit staked",
        "FAIR ODDS         = (1 - p) / p            fractional",
        "KELLY FRACTION    = (p x d - 1) / (d - 1)",
        "ROI               = net profit / turnover",
        "CLV               = (odds taken / odds at the off) - 1",
        "",
        "  W, P, S, X = gross pool for that bet type",
        "  t = takeout rate;  w, p(), s() = amount staked on a runner",
        "  p = your estimated probability;  d = decimal odds",
        ]),
    ]))
    s.append(PageBreak())
    return s


def app_d():
    s = appendix("D", "A Race, Start to Finish",
                 "One complete worked example, applying every stage of the method to a single "
                 "hypothetical race.")
    s.append(P(
        "The race: a 7-furlong handicap on a good surface, eight runners, a $260,000 win pool. "
        "Takeout 16% on win, 21% on the exacta. The horses and connections below are invented; "
        "the reasoning is not.", "body_first"))

    s.append(Paragraph("Step 1 &mdash; Read the form with the odds hidden", ST["h2"]))
    s.append(table([
        ["Horse", "Style", "Last run", "Notes from the form"],
        ["Coldharbour", "E", "Won by 3, career-best figure", "Clear top figure, but that was a "
         "career best off a layoff &mdash; bounce candidate. Also one of four horses that want "
         "the lead, and the one most committed to it."],
        ["Achill Bay", "E/P", "4th, beaten 2, wide throughout", "Chart says 'wide into the "
         "stretch'. Replay confirms it lost about three lengths on the turn. Effectively a "
         "winning run. Second start off a layoff for a barn that hits 24% in that spot."],
        ["Marlpit", "S", "2nd, beaten a neck", "Solid, consistent, closes late. Needs pace to "
         "collapse. Will be well backed on the strength of the last run."],
        ["Silverlode", "E", "6th, beaten 9", "Contested a fast pace and stopped. Will contest "
         "again today."],
        ["Penny Whistle", "P", "3rd, beaten 4", "Honest, exposed, no obvious improvement "
         "available."],
        ["Grey Sessions", "S", "8th, beaten 11", "Terrible-looking line, but ran on a day the "
         "rail was dead and it raced on the rail throughout. Forgivable. Drops in class."],
        ["Foxbarrow", "E", "5th, beaten 6", "Third of the four front-runners."],
        ["Tallowmere", "P", "7th, beaten 8", "Little to recommend it."],
    ], [26 * mm, 14 * mm, 40 * mm, 90 * mm], font_size=8.2,
        caption="Table D.1 &mdash; The field as read from the form, before looking at a single "
                "price."))
    s.append(P(
        "The structural read: <b>four</b> horses want the lead (Coldharbour, Silverlode, "
        "Foxbarrow, and Achill Bay if forced). That is a speed duel. The front end is likely "
        "to over-race and stop, which favours the closers &mdash; Marlpit and Grey Sessions "
        "&mdash; and favours the one horse able to sit just off the fight, which is Achill Bay "
        "if its rider is patient."))

    s.append(Paragraph("Step 2 &mdash; Build the line", ST["h2"]))
    s.append(worked("Fair-odds line, then the board", [
        "Horse            My %    Fair odds    Board    Verdict",
        "Achill Bay        24%       3/1        11/2    OVERLAY  - bet",
        "Marlpit           20%       4/1         9/2    slight overlay",
        "Coldharbour       18%       9/2         7/4    UNDERLAY - avoid",
        "Grey Sessions     12%       7/1        12/1    OVERLAY  - bet",
        "Penny Whistle     10%       9/1         8/1    underlay",
        "Silverlode         8%      11/1        12/1    fair",
        "Foxbarrow          5%      19/1        20/1    fair",
        "Tallowmere         3%      32/1        40/1    small overlay, ignore",
        "                 ----",
        "                 100%",
    ]))
    s.append(P(
        "Coldharbour is 7/4 because the crowd sees the top speed figure and the last-time-out "
        "win. Our reasons for downgrading it &mdash; the bounce risk and, more importantly, "
        "the pace duel it cannot avoid &mdash; are exactly the sort of factors the tote board "
        "prices badly. That is the entire opportunity in this race."))

    s.append(Paragraph("Step 3 &mdash; Size the bets", ST["h2"]))
    s.append(worked("Half-Kelly on a 5,000 bankroll, capped at 3%", [
        "ACHILL BAY   p = 0.24, board 11/2, decimal 6.50",
        "  edge:  p x d = 0.24 x 6.50 = 1.56   ->  EV +56%",
        "  f* = (1.56 - 1) / 5.50 = 0.56 / 5.50 = 0.1018",
        "  half Kelly = 5.09%  ->  exceeds the cap, so cap at 3%",
        "  STAKE  $150 to win",
        "",
        "GREY SESSIONS  p = 0.12, board 12/1, decimal 13.00",
        "  edge:  p x d = 0.12 x 13.00 = 1.56  ->  EV +56%",
        "  f* = (1.56 - 1) / 12.00 = 0.56 / 12.00 = 0.0467",
        "  half Kelly = 2.33%  ->  under the cap",
        "  STAKE  $117 to win  ->  round to $115",
        "",
        "Total win exposure: $265 on a $5,000 bankroll = 5.3%.",
    ]))
    s.append(P(
        "The two bets have <i>identical</i> expected value &mdash; both are priced at 56% above "
        "fair &mdash; and Kelly still stakes one at $150 and the other at $115. That is not an "
        "inconsistency. Kelly weights the probability as well as the price: the same percentage "
        "edge is worth less when it is spread across a longer, less certain shot, because the "
        "variance you must survive to collect it is far greater. Any staking rule that sizes "
        "purely on perceived edge, ignoring the win probability, will over-bet longshots."))
    s.append(P(
        "The cap matters too. Unconstrained half-Kelly wanted 5.09% of the bankroll on Achill "
        "Bay, which relies on a 24% estimate being accurate to within a point or two. It is "
        "not. The 3% cap is the acknowledgement that our probability estimate is itself "
        "uncertain &mdash; and when a line produces several bets that all want the cap, the "
        "right response is to distrust the line, not to raise the cap."))

    s.append(Paragraph("Step 4 &mdash; Consider an exotic, then decide", ST["h2"]))
    s.append(P(
        "The exacta is tempting: if the pace collapses, the finish is plausibly Achill Bay over "
        "Marlpit or Grey Sessions, and Coldharbour's absence from the top two would inflate the "
        "payout enormously. A structured ticket rather than a box:"))
    s.append(worked("Exacta part-wheel at $2", [
        "1st:  Achill Bay, Grey Sessions              (2 horses)",
        "2nd:  Achill Bay, Grey Sessions, Marlpit,",
        "      Penny Whistle                          (4 horses)",
        "",
        "  Combinations = 2 x 4 - 2 (self-pairs) = 6",
        "  Cost = 6 x $2 = $12",
        "",
        "Deliberately EXCLUDES Coldharbour from both positions.",
        "That is the opinion. If Coldharbour runs second the ticket",
        "is dead -- accepted, because the whole thesis is that the",
        "pace duel beats it.",
        "",
        "Total outlay for the race: $150 + $115 + $12 = $277",
    ]))
    s.append(P(
        "Whether to make the exacta bet at all is a real question, and the honest answer is "
        "that at 21% takeout it needs the pace read to be strongly correct. A defensible "
        "alternative is to skip it and put the $12 into the win bets. Both are reasonable; what "
        "is not reasonable is boxing six horses for $60 because the race 'looks wide open'."))

    s.append(Paragraph("Step 5 &mdash; Record it before the race runs", ST["h2"]))
    s.append(worked("The log entry, written before the gates open", [
        "Date/Track/Race   12 May / Belmont / R6",
        "Bet 1  Achill Bay WIN  $150 @ 11/2   my p = 24%",
        "Bet 2  Grey Sessions WIN $115 @ 12/1  my p = 12%",
        "Bet 3  Exacta part-wheel $12",
        "Reason code       PACE-COLLAPSE + TRIP (wide last time)",
        "Against           Coldharbour, top figure, 7/4",
        "",
        "Result and closing odds to be filled in afterwards.",
        "CLV to be computed from odds taken vs odds at the off.",
    ]))
    s.append(P(
        "Whatever happens next is one data point. If Coldharbour makes every yard and wins by "
        "four, the analysis was not necessarily wrong &mdash; an 18% chance comes in roughly "
        "once every five or six races, and the record will show that we priced it at 18% and "
        "the market "
        "priced it at 36%. Only the accumulated log across several hundred such races can tell "
        "us which of those two numbers was closer to the truth. That is the whole discipline, "
        "and it is the note this guide should end on."))
    return s


# --------------------------------------------------------------------------
# Assemble
# --------------------------------------------------------------------------

def bind_headings(story):
    """Bundle a heading with the block that follows it.

    ParagraphStyle.keepWithNext handles a heading followed by body text, but
    not one followed by a KeepTogether (a table or a worked example) -- those
    move to the next page on their own and leave the heading stranded at the
    foot of the previous one. Bundling the pair into a single KeepTogether
    makes them travel together.

    Bundling is skipped for tall blocks: a big table nested two KeepTogethers
    deep stops splitting across pages and starts wasting whole pages instead.
    Those keep the old behaviour, where the table breaks and the heading may
    sit above it on the previous page.
    """
    # 60mm is the measured sweet spot: bundling blocks larger than this
    # buys a few less orphans at a cost of several near-empty pages.
    limit = 60 * mm
    # Flowables need a canvas bound before they can be measured outside a build.
    probe = Canvas(io.BytesIO(), pagesize=A4)
    out = []
    i = 0
    while i < len(story):
        f = story[i]
        nxt = story[i + 1] if i + 1 < len(story) else None
        if (isinstance(f, Paragraph) and f.style.name in ("h2", "h3")
                and isinstance(nxt, (KeepTogether, ListFlowable))):
            try:
                nxt.canv = probe
                wrapped = nxt.wrap(W_FULL, PAGE_H)[1]
                # KeepTogether.wrap reports a sentinel height to force a split,
                # stashing the real measurement on _H.
                height = getattr(nxt, "_H", None)
                if not height:
                    height = wrapped
            except Exception:
                height = limit + 1
            finally:
                if hasattr(nxt, "canv"):
                    del nxt.canv
            if height <= limit:
                out.append(KeepTogether([f, nxt]))
                i += 2
                continue
        out.append(f)
        i += 1
    return out


def build(path):
    doc = Guide(path, title=TITLE, author="HorseHQ",
                subject="A reference guide to horse racing wagering")

    story = []
    story += cover()
    story += front_matter()

    story += part_divider(
        "I", "The Market",
        "How the price is made, what it costs to play, and how the three<br/>"
        "great wagering structures differ from one another.")
    story += ch1()
    story += ch2()
    story += ch3()

    story += part_divider(
        "II", "The Bets",
        "Every wager on the menu, what it costs, what it requires,<br/>"
        "and when it is the right instrument for an opinion.")
    story += ch4()
    story += ch5()
    story += ch6()

    story += part_divider(
        "III", "The Work",
        "Forming an opinion, pricing it, staking it, recording it,<br/>"
        "and finding out honestly whether it was any good.")
    story += ch7()
    story += ch8()
    story += ch9()
    story += ch10()
    story += ch11()
    story += ch12()
    story += ch13()
    story += ch14()
    story += ch15()

    story += part_divider(
        "IV", "Reference",
        "Definitions, conversions, deduction scales and one race<br/>"
        "worked from first read to final log entry.")
    story += app_a()
    story += app_b()
    story += app_c()
    story += app_d()

    doc.multiBuild(bind_headings(story))
    return path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "docs/horse-racing-wagering-guide.pdf"
    build(out)
    print("wrote %s" % out)
