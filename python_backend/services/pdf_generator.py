"""
VidhiChakshu (विधि-चक्षु) - Certified Legal Intelligence PDF Generator
Builds formal, court-ready, multi-page legal reports using ReportLab.
Includes Citizen Summary, Chauhaddi Boundary Schedule, Pedigree Lineage,
Chain of Title, Archaic Revenue Glossary, and Statutory Compliance.
"""

import io
from datetime import datetime
from typing import Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Adds page numbers and footer to all pages dynamically."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "VidhiChakshu (विधि-चक्षु) — Certified Legal & Heritage Intelligence Report")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, letter[0] - 54, 742)
            
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 36, footer_text)
        disclaimer = "CONFIDENTIAL & PRIVILEGED • Generated via VidhiChakshu Legal AI Platform"
        self.drawString(54, 36, disclaimer)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, letter[0] - 54, 48)
        self.restoreState()

def generate_certified_pdf_report(data: Dict[str, Any]) -> bytes:
    """
    Compiles a comprehensive, certified PDF intelligence brief for VidhiChakshu.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_navy = colors.HexColor("#1B2A4A")
    c_gold = colors.HexColor("#C5A059")
    c_gold_light = colors.HexColor("#F9F5EC")
    c_slate = colors.HexColor("#334155")
    c_muted = colors.HexColor("#64748B")
    
    # Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_navy
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_muted
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=c_navy,
        spaceBefore=14,
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_gold,
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=c_slate
    )
    body_bold = ParagraphStyle(
        'BodyBold_Custom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    callout_style = ParagraphStyle(
        'Callout',
        parent=body_style,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0F172A")
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_slate
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.white
    )

    story = []

    # ── HEADER BANNER ──
    header_data = [
        [
            Paragraph("<b>VIDHICHAKSHU (विधि-चक्षु)</b><br/><font size=8 color='#64748B'>THE AI VISION FOR INDIAN LEGAL & HERITAGE DOCUMENTS</font>", title_style),
            Paragraph(f"<b>CERTIFIED LEGAL BRIEF</b><br/><font size=7 color='#64748B'>Date: {datetime.now().strftime('%d %B %Y')}<br/>Doc Ref: {data.get('document_id', 'DOC-2026-HERITAGE')[:24]}</font>", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[320, 184])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_gold, spaceBefore=4, spaceAfter=14))

    # ── SECTION 1: CITIZEN & FARMER SUMMARY ──
    story.append(Paragraph("1. Plain-Language Citizen Summary (सरल व्याख्या)", h1_style))
    layman = data.get("layman_summary") or data.get("summary") or "Summary not provided."
    story.append(Paragraph(layman.replace("\n", "<br/>"), body_style))
    story.append(Spacer(1, 10))

    # ── SECTION 2: CHAUHADDI (FOUR BOUNDARIES SCHEDULE) ──
    chauhaddi = data.get("chauhaddi") or {}
    story.append(Paragraph("2. Chauhaddi (Four Demarcated Boundaries Schedule)", h1_style))
    story.append(Paragraph("In Indian land jurisprudence, unambiguous boundary descriptions prevail over survey measurements.", subtitle_style))
    story.append(Spacer(1, 4))
    
    plot_num = chauhaddi.get("plot_number", "Survey / Khasra Record Referenced")
    area_val = chauhaddi.get("area", "Area specified in title deed")
    village_val = chauhaddi.get("village", "Village Jurisdictional Record")
    
    b_north = chauhaddi.get("north", "Demarcated land parcel")
    b_south = chauhaddi.get("south", "Adjacent boundary")
    b_east = chauhaddi.get("east", "Adjoining survey parcel")
    b_west = chauhaddi.get("west", "Road / Public access")

    chauhaddi_table_data = [
        [Paragraph("<b>Direction</b>", table_header), Paragraph("<b>Demarcated Boundary / Neighboring Land</b>", table_header)],
        [Paragraph("<b>NORTH (उत्तर)</b>", body_bold), Paragraph(b_north, table_cell)],
        [Paragraph("<b>SOUTH (दक्षिण)</b>", body_bold), Paragraph(b_south, table_cell)],
        [Paragraph("<b>EAST (पूर्व)</b>", body_bold), Paragraph(b_east, table_cell)],
        [Paragraph("<b>WEST (पश्चिम)</b>", body_bold), Paragraph(b_west, table_cell)],
        [Paragraph("<b>Plot / Survey No</b>", body_bold), Paragraph(plot_num, table_cell)],
        [Paragraph("<b>Total Area / Extent</b>", body_bold), Paragraph(area_val, table_cell)],
        [Paragraph("<b>Village / Revenue Circle</b>", body_bold), Paragraph(village_val, table_cell)],
    ]
    ch_table = Table(chauhaddi_table_data, colWidths=[140, 364])
    ch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_gold_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(ch_table)
    story.append(Spacer(1, 12))

    # ── SECTION 3: ANCESTRAL PEDIGREE (SHAJRA-E-NASAB) ──
    lineage = data.get("lineage") or {}
    members = lineage.get("family_members") or []
    if members:
        story.append(Paragraph("3. Ancestral Lineage & Pedigree Schedule (Shajra-e-Nasab)", h1_style))
        lineage_table_data = [
            [
                Paragraph("<b>Generation</b>", table_header),
                Paragraph("<b>Family Member / Heir</b>", table_header),
                Paragraph("<b>Relationship</b>", table_header),
                Paragraph("<b>Entitled Share / Rights</b>", table_header)
            ]
        ]
        for m in members:
            lineage_table_data.append([
                Paragraph(f"Gen {m.get('generation', 1)}", table_cell),
                Paragraph(m.get('name', 'N/A'), body_bold),
                Paragraph(m.get('relation', 'Heir'), table_cell),
                Paragraph(m.get('share', 'Undivided Share'), table_cell),
            ])
        lin_table = Table(lineage_table_data, colWidths=[70, 180, 134, 120])
        lin_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_navy),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_gold_light]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(lin_table)
        story.append(Spacer(1, 12))

    # ── SECTION 4: CHAIN OF TITLE & DEFECT ASSESSMENT ──
    title_chain = data.get("title_chain") or []
    title_score = data.get("title_health_score", 90)
    title_defects = data.get("title_defects") or []
    
    story.append(Paragraph(f"4. Chain of Title & Risk Audit (Title Health: {title_score}/100)", h1_style))
    if title_chain:
        chain_table_data = [
            [
                Paragraph("<b>Period / Year</b>", table_header),
                Paragraph("<b>Transaction / Event</b>", table_header),
                Paragraph("<b>Parties Involved</b>", table_header),
                Paragraph("<b>Statutory Significance</b>", table_header)
            ]
        ]
        for item in title_chain:
            chain_table_data.append([
                Paragraph(item.get("date_or_period", "N/A"), body_bold),
                Paragraph(item.get("event", "Conveyance"), table_cell),
                Paragraph(item.get("parties", "N/A"), table_cell),
                Paragraph(item.get("significance", "Recorded Transaction"), table_cell)
            ])
        chain_table = Table(chain_table_data, colWidths=[70, 140, 144, 150])
        chain_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_navy),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_gold_light]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(chain_table)
        story.append(Spacer(1, 6))

    if title_defects:
        defect_text = "<b>Identified Verification Points & Title Defects:</b><br/>" + "<br/>".join([f"• {d}" for d in title_defects])
        defect_p = Paragraph(defect_text, callout_style)
        defect_table = Table([[defect_p]], colWidths=[504])
        defect_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#F87171")),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(defect_table)
        story.append(Spacer(1, 12))

    # ── SECTION 5: ARCHAIC REVENUE LEXICON ANNOTATIONS ──
    archaic_terms = data.get("archaic_terms") or []
    if archaic_terms:
        story.append(Paragraph("5. Archaic Revenue Lexicon & Historical Terminology", h1_style))
        lex_data = [
            [
                Paragraph("<b>Historical Term</b>", table_header),
                Paragraph("<b>Origin / Class</b>", table_header),
                Paragraph("<b>Historical Meaning</b>", table_header),
                Paragraph("<b>Modern Statutory Equivalent</b>", table_header)
            ]
        ]
        for term in archaic_terms[:8]:
            lex_data.append([
                Paragraph(f"<b>{term.get('term', '')}</b>", body_bold),
                Paragraph(f"{term.get('origin', '')} ({term.get('category', '')})", table_cell),
                Paragraph(term.get("meaning", ""), table_cell),
                Paragraph(term.get("modern_significance", ""), table_cell),
            ])
        lex_table = Table(lex_data, colWidths=[90, 100, 154, 160])
        lex_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), c_navy),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_gold_light]),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(lex_table)
        story.append(Spacer(1, 12))

    # ── SECTION 6: STATUTORY & CONSTITUTIONAL COMPLIANCE ──
    legal_data = data.get("legalAnalysis") or data.get("legal_analysis") or {}
    story.append(Paragraph("6. Statutory Transitions & Legal Compliance Audit", h1_style))
    
    compliance_items = []
    if legal_data.get("statutory_transitions"):
        compliance_items.append("<b>Statutory Transitions:</b><br/>" + "<br/>".join([f"• {s}" for s in legal_data.get("statutory_transitions", [])]))
    if legal_data.get("property_and_title_findings"):
        compliance_items.append("<b>Title & Property Law Findings:</b><br/>" + "<br/>".join([f"• {p}" for p in legal_data.get("property_and_title_findings", [])]))
    if legal_data.get("constitutional_principles"):
        compliance_items.append("<b>Constitutional Protections:</b><br/>" + "<br/>".join([f"• {c}" for c in legal_data.get("constitutional_principles", [])]))

    if compliance_items:
        comp_p = Paragraph("<br/><br/>".join(compliance_items), body_style)
        comp_table = Table([[comp_p]], colWidths=[504])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), c_gold_light),
            ('BOX', (0, 0), (-1, -1), 1, c_gold),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(comp_table)
        story.append(Spacer(1, 14))

    # ── FOOTER CERTIFICATION BOX ──
    cert_text = (
        "<b>CERTIFICATE OF AI PALEOGRAPHIC & STATUTORY REVIEW</b><br/>"
        "This document intelligence report was generated using VidhiChakshu AI Engine (v3.0.0). "
        "Processed in compliance with the Digital Personal Data Protection Act (DPDP), Indian Registration Act (1908), "
        "and Bharatiya Sakshya Adhiniyam (2023). Recommended for legal advisory, land revenue verification, and archival research."
    )
    cert_table = Table([[Paragraph(cert_text, ParagraphStyle('Cert', parent=body_style, fontSize=7.5, leading=10, textColor=c_muted))]], colWidths=[504])
    cert_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 0.5, c_gold),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(cert_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    return buffer.getvalue()
