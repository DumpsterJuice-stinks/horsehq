#!/usr/bin/env python3
"""
Build the 8-page sampler for "The Complete Guide to Horse Racing Wagering".

The preview is a genuine extract: every passage below is lifted verbatim from
the full guide, so a reader who downloads the whole thing gets exactly what
the sample promised. Styling, page furniture and the flowable helpers are
imported from the main generator so the two documents stay a visual family
and there is one source of truth for the design.

Usage:  python3 docs/build_wagering_preview.py [output.pdf] [download-url]
"""

import os
import sys

# Importable regardless of the working directory it is invoked from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from build_wagering_pdf import (
    ACCENT,
    ACCENT_2,
    MARGIN,
    MUTED,
    PAGE_H,
    PAGE_W,
    PUB_DATE,
    RULE,
    ST,
    W_FULL,
    WASH,
    Guide,
    P,
    bind_headings,
    callout,
    table,
    worked,
)

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

# Replace with the real landing page before publishing, or pass it as argv[2].
DOWNLOAD_URL = "thehorsehq.com/wagering-guide"

FULL_PAGES = 53
FULL_WORDS = "21,000"
GOLD = colors.HexColor("#C9A227")

PREVIEW_TITLE = "Horse Racing Wagering"
PREVIEW_SUB = "Pools, Prices, Probability and Bankroll"


def preview_styles():
    """A few styles specific to the sampler, layered over the shared set."""
    S = dict(ST)
    S["kicker"] = ParagraphStyle(
        "kicker", parent=ST["body"], fontName="Helvetica-Bold", fontSize=8,
        leading=11, textColor=ACCENT_2, spaceAfter=2,
    )
    S["pull"] = ParagraphStyle(
        "pull", parent=ST["body"], fontName="Times-Italic", fontSize=13,
        leading=18, textColor=ACCENT, alignment=0, spaceAfter=4,
    )
    S["statnum"] = ParagraphStyle(
        "statnum", parent=ST["body"], fontName="Helvetica-Bold", fontSize=17,
        leading=20, textColor=ACCENT, alignment=1, spaceAfter=1,
    )
    S["statlab"] = ParagraphStyle(
        "statlab", parent=ST["body"], fontName="Helvetica", fontSize=7.4,
        leading=9.5, textColor=MUTED, alignment=1,
    )
    S["cta_big"] = ParagraphStyle(
        "cta_big", parent=ST["body"], fontName="Times-Bold", fontSize=19,
        leading=24, textColor=colors.white, alignment=1, spaceAfter=6,
    )
    S["cta_body"] = ParagraphStyle(
        "cta_body", parent=ST["body"], fontSize=10, leading=14.5,
        textColor=colors.HexColor("#E3D9C6"), alignment=1, spaceAfter=4,
    )
    S["cta_url"] = ParagraphStyle(
        "cta_url", parent=ST["body"], fontName="Helvetica-Bold", fontSize=13,
        leading=17, textColor=GOLD, alignment=1,
    )
    return S


PS = preview_styles()


# --------------------------------------------------------------------------
# Document template
# --------------------------------------------------------------------------

class Preview(Guide):
    """Same page furniture as the guide, with a sampler cover and footer."""

    def __init__(self, filename, **kw):
        Guide.__init__(self, filename, **kw)
        # Guide's constructor installed its own cover/body templates;
        # drop them so the sampler's three are the only ones registered.
        self.pageTemplates = []
        frame_cover = Frame(0, 0, PAGE_W, PAGE_H, id="cover",
                            leftPadding=0, rightPadding=0,
                            topPadding=0, bottomPadding=0)
        frame_body = Frame(MARGIN, MARGIN + 9 * mm,
                           PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN - 15 * mm,
                           id="body", leftPadding=0, rightPadding=0,
                           topPadding=0, bottomPadding=0)
        # Inset: the dark background is painted on the canvas, so the frame
        # itself only needs to hold text away from the page edges.
        frame_full = Frame(30 * mm, 24 * mm, PAGE_W - 60 * mm, PAGE_H - 48 * mm,
                           id="full", leftPadding=0, rightPadding=0,
                           topPadding=0, bottomPadding=0)
        self.addPageTemplates([
            PageTemplate(id="cover", frames=[frame_cover], onPage=self.draw_cover),
            PageTemplate(id="body", frames=[frame_body], onPageEnd=self.draw_body),
            PageTemplate(id="closing", frames=[frame_full], onPage=self.draw_closing),
        ])

    def draw_cover(self, canv, doc):
        cx = PAGE_W / 2.0
        canv.saveState()
        canv.setFillColor(colors.HexColor("#22201C"))
        canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

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
            width = canv.stringWidth(text, font, size)
            if spacing:
                width += spacing * (len(text) - 1)
            tobj = canv.beginText(cx - width / 2.0, y)
            tobj.setFont(font, size)
            tobj.setFillColor(colour)
            tobj.setCharSpace(spacing)
            tobj.textOut(text)
            canv.drawText(tobj)

        # sample badge
        bw, bh = 62 * mm, 9.5 * mm
        by = PAGE_H - 66 * mm
        canv.setFillColor(GOLD)
        canv.rect(cx - bw / 2.0, by, bw, bh, fill=1, stroke=0)
        centred("FREE 8-PAGE SAMPLE", "Helvetica-Bold", 9.5,
                colors.HexColor("#22201C"), by + 3.2 * mm, spacing=1.4)

        rule_x = MARGIN + 14 * mm
        canv.setStrokeColor(GOLD)
        canv.setLineWidth(0.8)
        canv.line(rule_x, PAGE_H - 84 * mm, PAGE_W - rule_x, PAGE_H - 84 * mm)

        centred(PREVIEW_TITLE, "Times-Bold", 34, colors.white, PAGE_H - 108 * mm)
        centred(PREVIEW_SUB, "Times-Italic", 14,
                colors.HexColor("#E3D9C6"), PAGE_H - 124 * mm)
        canv.line(rule_x, PAGE_H - 136 * mm, PAGE_W - rule_x, PAGE_H - 136 * mm)

        lines = [
            "Where the price comes from. What the operator keeps.",
            "Which bets are worth making, and how to size them.",
        ]
        y = PAGE_H - 150 * mm
        for line in lines:
            centred(line, "Times-Roman", 11.5, colors.HexColor("#C6BCA6"), y)
            y -= 7 * mm

        inside = [
            "How a pari-mutuel pool sets the price",
            "What takeout really costs you",
            "Why boxing an exotic is usually wrong",
            "Building a fair-odds line",
        ]
        centred("INSIDE THIS SAMPLE", "Helvetica-Bold", 7.5,
                GOLD, PAGE_H - 172 * mm, spacing=1.5)
        y = PAGE_H - 183 * mm
        for line in inside:
            centred(line, "Helvetica", 9, colors.HexColor("#B9AE97"), y)
            y -= 6.4 * mm

        centred("A sample of the %d-page reference guide" % FULL_PAGES,
                "Helvetica", 8.5, colors.HexColor("#B9AE97"), band_h + 24 * mm)
        centred(DOWNLOAD_URL, "Helvetica-Bold", 10, GOLD, band_h + 16 * mm)
        canv.restoreState()

    def draw_body(self, canv, doc):
        canv.saveState()
        canv.setFont("Helvetica", 7.4)
        canv.setFillColor(MUTED)
        canv.drawString(MARGIN, PAGE_H - MARGIN + 3 * mm,
                        "Horse Racing Wagering — sample")
        canv.drawRightString(PAGE_W - MARGIN, PAGE_H - MARGIN + 3 * mm,
                             self.current_chapter)
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        canv.line(MARGIN, PAGE_H - MARGIN + 1.2 * mm,
                  PAGE_W - MARGIN, PAGE_H - MARGIN + 1.2 * mm)
        canv.line(MARGIN, MARGIN + 7 * mm, PAGE_W - MARGIN, MARGIN + 7 * mm)
        canv.setFont("Helvetica", 7.4)
        canv.drawString(MARGIN, MARGIN + 3 * mm,
                        "Full guide: %s  ·  18+. Wager only what you can "
                        "afford to lose." % DOWNLOAD_URL)
        canv.setFont("Helvetica-Bold", 8.4)
        canv.setFillColor(ACCENT)
        canv.drawRightString(PAGE_W - MARGIN, MARGIN + 2.8 * mm,
                             str(canv.getPageNumber() - 1))
        canv.restoreState()

    def draw_closing(self, canv, doc):
        canv.saveState()
        canv.setFillColor(colors.HexColor("#22201C"))
        canv.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        canv.setFillColor(colors.HexColor("#2F4B3C"))
        canv.rect(0, 0, PAGE_W, 30 * mm, fill=1, stroke=0)
        canv.setFillColor(colors.HexColor("#5B2333"))
        canv.rect(0, 30 * mm, PAGE_W, 1.8 * mm, fill=1, stroke=0)
        canv.restoreState()

    def afterFlowable(self, flowable):
        # The sampler has no table of contents; only the running head matters.
        if isinstance(flowable, Paragraph) and flowable.style.name in ("h1", "h1_plain"):
            self.current_chapter = flowable.getPlainText()


# --------------------------------------------------------------------------
# Building blocks
# --------------------------------------------------------------------------

def section(kicker, title):
    """A sampler section head: source label above, title below, rule under."""
    out = [Paragraph(kicker, PS["kicker"]),
           Paragraph(title, ST["h1"]), Spacer(1, 2)]
    hr = Table([[""]], colWidths=[W_FULL], rowHeights=[2])
    hr.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 1.6, ACCENT_2),
                            ("TOPPADDING", (0, 0), (-1, -1), 0),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    out += [hr, Spacer(1, 9)]
    return out


def stat_strip(items):
    row = []
    for num, lab in items:
        row.append([Paragraph(num, PS["statnum"]), Paragraph(lab, PS["statlab"])])
    t = Table([[c for c in row]], colWidths=[W_FULL / len(row)] * len(row))
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), WASH),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return KeepTogether([t, Spacer(1, 12)])


def pull_quote(text, attrib=None):
    inner = [Paragraph(text, PS["pull"])]
    if attrib:
        inner.append(Paragraph(attrib, ST["caption"]))
    t = Table([[inner]], colWidths=[W_FULL])
    t.setStyle(TableStyle([
        ("LINEBEFORE", (0, 0), (0, -1), 2.4, GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return KeepTogether([t, Spacer(1, 12)])


def continues(where):
    """Footer line pointing at the chapter this extract came from."""
    t = Table([[Paragraph(
        "&rarr;&nbsp;&nbsp;<b>Continues in the full guide:</b> %s" % where,
        ParagraphStyle("cont", parent=ST["body"], fontSize=8.8, leading=12,
                       textColor=ACCENT_2, spaceAfter=0))]], colWidths=[W_FULL])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WASH),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return KeepTogether([t, Spacer(1, 10)])


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------

def page_whats_inside():
    s = [NextPageTemplate("body"), PageBreak()]
    s += section("THE SAMPLE", "What you are holding")
    s.append(P(
        "This is a short extract from a %d-page reference on horse racing wagering. The pages "
        "that follow are lifted from it unaltered &mdash; four passages chosen because they "
        "are the ones that change how people bet, not the ones that are easiest to excerpt."
        % FULL_PAGES, "lead"))
    s.append(stat_strip([
        ("%d" % FULL_PAGES, "pages"),
        ("15", "chapters"),
        ("24", "worked<br/>examples"),
        ("22", "tables"),
        ("43", "glossary<br/>terms"),
    ]))
    s.append(Paragraph("What the full guide covers", ST["h2"]))
    s.append(table([
        ["Part", "Chapters", "What you get"],
        ["I &mdash; The Market", "Pari-mutuel pools; takeout and breakage; fixed odds, "
         "exchanges and tote compared", "Where the price actually comes from, what it costs "
         "you before you have picked a horse, and why the same bet is three different products "
         "in three different markets."],
        ["II &mdash; The Bets", "Straight wagers and each-way; vertical exotics; horizontal "
         "exotics", "Every wager on the menu with its cost formula &mdash; boxes, keys, "
         "part-wheels, Pick 3 through Pick 6 &mdash; and when each one is the right instrument "
         "for an opinion."],
        ["III &mdash; The Work", "Past performances; speed and pace; class and form; value; "
         "staking; records; the modern pool; common errors; regulation", "Forming an opinion, "
         "pricing it against the market, sizing the bet, and keeping records honest enough to "
         "tell you whether any of it is working."],
        ["IV &mdash; Reference", "Glossary; odds conversion; deduction scales and ticket "
         "costs; a race worked end to end", "The pages you will actually keep open: Rule 4 "
         "deductions, each-way terms, box and part-wheel costs, and one race taken from first "
         "read to final log entry."],
    ], [30 * mm, 52 * mm, 88 * mm], font_size=8.2))
    s.append(callout(
        "Who this is for",
        ["Anyone who has stood in front of a tote board and not been entirely sure what the "
         "numbers meant. It assumes you can tell a horse from a hurdle and nothing else.",
         "It is not a tipping service, a system, or a promise. No sequence of bets described "
         "in it has a guaranteed positive expectation, and several are explained precisely so "
         "you can recognise why they are bad."]))
    s.append(PageBreak())
    return s


def extract_one():
    s = section("EXTRACT 1 &nbsp;&middot;&nbsp; CHAPTERS 1 AND 2",
                "Nobody at the track is betting against you")
    s.append(P(
        "In a pari-mutuel market there is no bookmaker taking a position. Every wager of a "
        "given type on a given race goes into a common pool. When the race is official, the "
        "operator removes a fixed percentage &mdash; the takeout &mdash; and divides what "
        "remains among the winning tickets in proportion to their stake. The odds you see "
        "before the race are not a price offered to you by anyone. They are a running "
        "estimate of what the pool will pay if betting stops at that instant.", "body_first"))
    s.append(P(
        "Two consequences follow immediately. First, your opponents are the other bettors, "
        "not the house. The house is indifferent to which horse wins; it takes its percentage "
        "either way. To profit you do not need to predict winners &mdash; you need to disagree "
        "with the crowd, correctly, often enough to overcome the takeout. Second, your own "
        "money moves the price. Backing a 20/1 shot with a large enough stake makes it a 12/1 "
        "shot, and you get the 12/1."))
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
    s.append(Paragraph("What it costs before you have picked a horse", ST["h2"]))
    s.append(P(
        "Every pari-mutuel bet is made into a pool from which a percentage has already been "
        "promised to someone else. A 20% takeout means that for every $100 wagered into that "
        "pool, $80 comes back to bettors collectively. To break even you must be 25% better "
        "than the crowd &mdash; not 20%, because you need $100 back out of the $80 the pool "
        "returns."))
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
    s.append(pull_quote(
        "&ldquo;Your handicapping has to beat the crowd by more than the takeout before you "
        "win a penny, so the cheapest way to improve your results is to bet less often, into "
        "cheaper pools &mdash; none of which requires you to become a better judge of a "
        "horse.&rdquo;"))
    s.append(continues(
        "the full takeout schedule by pool type, breakage, rebates and effective takeout "
        "(Chapter 2), and how fixed odds, exchanges and the tote differ (Chapter 3)."))
    s.append(PageBreak())
    return s


def extract_two():
    s = section("EXTRACT 2 &nbsp;&middot;&nbsp; CHAPTER 5",
                "The box is usually the wrong ticket")
    s.append(P(
        "A box says every ordering of your horses is equally likely. You almost never believe "
        "that. If you have separated four horses well enough to isolate them from the field, "
        "you certainly have an opinion about which is most likely to win &mdash; and a box "
        "spends equal money on the combinations where your best horse runs fourth.",
        "body_first"))
    s.append(P(
        "The alternative is a structured part-wheel that spends most on your opinion and a "
        "little on the ways you might be wrong. Suppose you have separated a field into three "
        "groups: <b>A</b> is your single best horse (#5); <b>B</b> are two horses you rate "
        "close behind (#2, #9); <b>C</b> are three you think can hit the board but not win "
        "(#1, #4, #11)."))
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
        "That is the whole idea behind ticket construction: the shape of the bet should match "
        "the shape of the opinion. Most tote systems compute the deduplication for you and "
        "quote the true ticket cost before you confirm. Always read that number back before "
        "pressing accept &mdash; a mis-entered wheel is the classic way to turn an intended $8 "
        "bet into an $800 one."))
    s.append(continues(
        "cost formulas for every box, key and part-wheel up to the Super High Five "
        "(Chapter 5), and the same logic applied to Pick 4s, Pick 5s and Pick 6s "
        "(Chapter 6)."))
    s.append(PageBreak())
    return s


def extract_three():
    s = section("EXTRACT 3 &nbsp;&middot;&nbsp; CHAPTER 10",
                "You are not looking for winners")
    s.append(P(
        "The central discipline is a fair-odds line: your own estimate, made before you look "
        "at the board, of each horse's probability of winning. Comparing that line to the "
        "market is the only defensible reason to place a wager.", "lead"))
    s.append(P(
        "Handicap the race with the odds hidden &mdash; this is not optional, because once "
        "you have seen that a horse is 5/2 you cannot un-see it. Assign each runner a "
        "probability. Make them sum to 100%: they will not on the first pass, and this step "
        "alone catches an enormous amount of sloppy thinking. Convert each probability to fair "
        "odds using (1&nbsp;&minus;&nbsp;p)/p. Only then look at the board.", "body_first"))
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
    s.append(pull_quote(
        "&ldquo;A 28% chance at 2/1 is a bad bet. A 7% chance at 20/1 is a good one. You will "
        "lose the second bet more than nine times in ten and it will still be the correct "
        "wager.&rdquo;"))
    s.append(P(
        "Your opinion about which horse will win and your decision about which horse to back "
        "are different questions, and confusing them is the defining error of the recreational "
        "bettor. The market's implied probabilities, stripped of takeout, are a very good "
        "forecast &mdash; which means most of the time your line will be worse. The correct "
        "response is not to abandon the exercise but to bet rarely: on the small number of "
        "races where you have a specific, articulable reason to believe the crowd has missed "
        "something."))
    s.append(continues(
        "expected value, the Kelly criterion and fractional staking (Chapters 10 and 11), and "
        "how to test whether your probability estimates are calibrated at all (Chapter 12)."))
    s.append(PageBreak())
    return s


def extract_four():
    s = section("EXTRACT 4 &nbsp;&middot;&nbsp; CHAPTER 4 AND APPENDIX C",
                "The reference pages you will keep open")
    s.append(P(
        "Roughly a quarter of the guide is reference material: the tables you consult under "
        "time pressure rather than read once. Two short samples follow.", "body_first"))
    s.append(Paragraph("Each-way place terms", ST["h2"]))
    s.append(P(
        "An each-way bet is not one bet with a safety net. It is two bets of equal stake, "
        "settled independently: the win half at the full odds, and the place half at a "
        "fraction of those odds. Saying '&pound;10 each-way' means you are staking &pound;20."))
    s.append(table([
        ["Race and field size", "Places paid", "Place odds"],
        ["2 to 4 runners", "Win only &mdash; no each-way betting", "&mdash;"],
        ["5 to 7 runners", "1st and 2nd", "1/4 of the win odds"],
        ["8 or more runners (non-handicap)", "1st, 2nd, 3rd", "1/5 of the win odds"],
        ["8 to 11 runners (handicap)", "1st, 2nd, 3rd", "1/5 of the win odds"],
        ["12 to 15 runners (handicap)", "1st, 2nd, 3rd", "1/4 of the win odds"],
        ["16 or more runners (handicap)", "1st, 2nd, 3rd, 4th", "1/4 of the win odds"],
    ], [62 * mm, 44 * mm, 44 * mm], font_size=8.4))
    s.append(Paragraph("Rule 4 deductions, in part", ST["h2"]))
    s.append(P(
        "When a horse is withdrawn before coming under starter's orders, a deduction is "
        "applied to winnings on bets struck beforehand. The shorter the withdrawn horse was, "
        "the more the remaining field's chances improve, and the larger the deduction. The "
        "full nineteen-band scale is in Appendix C; here are six of them."))
    s.append(table([
        ["Odds of withdrawn horse", "Deduction from winnings"],
        ["1/9 or shorter", "90p in the pound"],
        ["4/5 to 4/6", "55p"],
        ["6/4 to 5/4", "40p"],
        ["3/1 to 12/5", "25p"],
        ["9/1 to 6/1", "10p"],
        ["Longer than 14/1", "No deduction"],
    ], [60 * mm, 50 * mm], font_size=8.4))
    s.append(continues(
        "the complete Rule 4 scale, a full odds-conversion table, box and multi-race ticket "
        "costs, every pool payout formula collected on one page, and a 43-term glossary "
        "(Appendices A to C)."))
    s.append(NextPageTemplate("closing"))
    s.append(PageBreak())
    return s


def closing_page():
    """Full-bleed call to action on the dark cover stock."""
    s = [Spacer(1, 50 * mm)]
    s.append(Paragraph("That was eight pages of %d." % FULL_PAGES, PS["cta_big"]))
    s.append(Spacer(1, 4 * mm))
    s.append(Paragraph(
        "The rest covers reading past performances line by line, speed figures and pace "
        "scenarios, class and form cycles, bankroll and staking, record keeping and closing "
        "line value, who else is in the pool with you, and one race worked from first read "
        "to final log entry.", PS["cta_body"]))
    s.append(Spacer(1, 10 * mm))

    inner = [Paragraph("DOWNLOAD THE FULL GUIDE", ParagraphStyle(
        "dl", parent=PS["cta_body"], fontName="Helvetica-Bold", fontSize=8.5,
        textColor=colors.HexColor("#B9AE97"), spaceAfter=5)),
        Paragraph(DOWNLOAD_URL, PS["cta_url"])]
    box = Table([[inner]], colWidths=[110 * mm])
    box.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 1.0, GOLD),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    box.hAlign = "CENTER"
    s.append(box)
    s.append(Spacer(1, 16 * mm))

    s.append(Paragraph(
        "Free. No email required. %s." % PUB_DATE, ParagraphStyle(
            "fine", parent=PS["cta_body"], fontSize=8.5,
            textColor=colors.HexColor("#8E856F"))))
    s.append(Spacer(1, 26 * mm))

    s.append(Paragraph(
        "Most people who bet on horse racing lose money over time, and this is a mathematical "
        "consequence of takeout rather than a failure of effort or intelligence. Treat the "
        "money you bet as the price of an absorbing pastime, and any profit as a pleasant "
        "surprise.", ParagraphStyle(
            "resp", parent=PS["cta_body"], fontSize=8.8, leading=13,
            textColor=colors.HexColor("#9A9180"))))
    s.append(Spacer(1, 6 * mm))
    s.append(Paragraph(
        "18+ only. If betting stops being fun, stop. Free, confidential support is available "
        "in every regulated market &mdash; in Britain from GamCare and the National Gambling "
        "Helpline, in the United States from the National Problem Gambling Helpline.",
        ParagraphStyle("resp2", parent=PS["cta_body"], fontSize=8,
                       leading=12, textColor=colors.HexColor("#8E856F"))))
    return s


# --------------------------------------------------------------------------
# Assemble
# --------------------------------------------------------------------------

def build(path):
    doc = Preview(path, title="Horse Racing Wagering — free sample",
                  author="HorseHQ",
                  subject="An 8-page sample of the complete wagering guide")
    story = []
    story.append(Spacer(1, 1))          # cover page
    story += page_whats_inside()
    story += extract_one()
    story += extract_two()
    story += extract_three()
    story += extract_four()
    story += closing_page()
    doc.build(bind_headings(story))
    return path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "docs/horse-racing-wagering-preview.pdf"
    if len(sys.argv) > 2:
        DOWNLOAD_URL = sys.argv[2]
    build(out)
    print("wrote %s" % out)
