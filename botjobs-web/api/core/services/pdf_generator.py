"""
Genera el CV de Timoteo Pereyra en PDF, optimizado para ATS.
Incluye adaptación automática con IA si se proveen datos de una vacante.
"""

from core.services.ai_handler import adapt_cv_for_job
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle
)

BLACK      = colors.HexColor("#0f0f0f")
DARK_GRAY  = colors.HexColor("#2e2e2e")
MID_GRAY   = colors.HexColor("#555555")
LIGHT_GRAY = colors.HexColor("#d0d0d0")

PAGE_W, PAGE_H = A4
MARGIN_H  = 2.0 * cm
MARGIN_V  = 1.8 * cm
CONTENT_W = PAGE_W - 2 * MARGIN_H


def make_styles():
    return {
        "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=20, textColor=BLACK, leading=24, spaceAfter=2),
        "headline": ParagraphStyle("headline", fontName="Helvetica-Oblique", fontSize=9.5, textColor=MID_GRAY, leading=14, spaceAfter=5),
        "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=8.5, textColor=colors.HexColor("#444444"), leading=13, spaceAfter=2),
        "contact2": ParagraphStyle("contact2", fontName="Helvetica", fontSize=8.5, textColor=colors.HexColor("#444444"), leading=13, spaceAfter=8),
        "section": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=7.5, textColor=MID_GRAY, leading=10, spaceBefore=10, spaceAfter=4, charSpace=2.2),
        "summary": ParagraphStyle("summary", fontName="Helvetica", fontSize=9.5, textColor=DARK_GRAY, leading=14.5, spaceAfter=2),
        "job_title": ParagraphStyle("job_title", fontName="Helvetica-Bold", fontSize=10.5, textColor=BLACK, leading=14),
        "job_period": ParagraphStyle("job_period", fontName="Helvetica-Oblique", fontSize=9, textColor=MID_GRAY, leading=13, alignment=2),
        "job_company": ParagraphStyle("job_company", fontName="Helvetica-Oblique", fontSize=9, textColor=MID_GRAY, leading=13, spaceAfter=3),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9, textColor=DARK_GRAY, leading=13.5, leftIndent=10, spaceAfter=1.5),
        "edu_degree": ParagraphStyle("edu_degree", fontName="Helvetica-Bold", fontSize=10, textColor=BLACK, leading=14),
        "edu_period": ParagraphStyle("edu_period", fontName="Helvetica-Oblique", fontSize=9, textColor=MID_GRAY, leading=13, alignment=2),
        "edu_inst": ParagraphStyle("edu_inst", fontName="Helvetica", fontSize=9, textColor=MID_GRAY, leading=13, spaceAfter=4),
        "skill_row": ParagraphStyle("skill_row", fontName="Helvetica", fontSize=9, textColor=DARK_GRAY, leading=14, spaceAfter=1),
    }


def divider_heavy():
    return HRFlowable(width="100%", thickness=1.5, color=BLACK, spaceAfter=5, spaceBefore=2)

def divider_light():
    return HRFlowable(width="100%", thickness=0.4, color=LIGHT_GRAY, spaceAfter=3, spaceBefore=0)

def section_title(text, s):
    return [divider_light(), Paragraph(text.upper(), s["section"])]

def two_col_row(left_para, right_para, left_pct=0.70):
    t = Table([[left_para, right_para]], colWidths=[CONTENT_W * left_pct, CONTENT_W * (1 - left_pct)])
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "BOTTOM"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    return t


def generate_cv_pdf(profile: dict, scraped_data: dict = None) -> bytes:
    """
    Genera el CV de Timoteo Pereyra en PDF. 
    Si se provee scraped_data, adapta automáticamente el perfil con Gemini antes de compilar.
    """
    buffer = io.BytesIO()
    s = make_styles()

    # Si vienen datos de la oferta desde el frontend, llamamos al handler de la IA primero
    if scraped_data:
        print("🤖 [PDF Generator] Detectada oferta de trabajo. Adaptando CV con Gemini antes de renderizar...")
        profile = adapt_cv_for_job(scraped_data)
    else:
        print("📄 [PDF Generator] No se detectó oferta. Renderizando CV original...")

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=MARGIN_H, rightMargin=MARGIN_H,
        topMargin=MARGIN_V, bottomMargin=MARGIN_V,
        title=profile.get("name", "CV"),
        author=profile.get("name", ""),
        subject="Curriculum Vitae",
    )

    story = []

    # HEADER
    story.append(Paragraph(profile["name"], s["name"]))
    if profile.get("headline"):
        story.append(Paragraph(profile["headline"], s["headline"]))
    story.append(divider_heavy())

    line1 = [profile.get("email",""), profile.get("phone",""), profile.get("location","")]
    story.append(Paragraph("   ·   ".join(p for p in line1 if p), s["contact"]))
    line2 = [profile.get("linkedin",""), profile.get("github","")]
    story.append(Paragraph("   ·   ".join(p for p in line2 if p), s["contact2"]))

    # RESUMEN
    if profile.get("summary"):
        story += section_title("Perfil Profesional", s)
        story.append(Paragraph(profile["summary"], s["summary"]))

    # EXPERIENCIA
    if profile.get("experience"):
        story += section_title("Experiencia Laboral", s)
        for i, exp in enumerate(profile["experience"]):
            story.append(two_col_row(
                Paragraph(exp.get("title",""), s["job_title"]),
                Paragraph(exp.get("period",""), s["job_period"]),
            ))
            if exp.get("company"):
                story.append(Paragraph(exp["company"], s["job_company"]))
            for bullet in exp.get("bullets", []):
                story.append(Paragraph(f"\u2013\u2003{bullet}", s["bullet"]))
            if i < len(profile["experience"]) - 1:
                story.append(Spacer(1, 5))

    # EDUCACION
    if profile.get("education"):
        story += section_title("Formación", s)
        for edu in profile["education"]:
            story.append(two_col_row(
                Paragraph(edu.get("degree",""), s["edu_degree"]),
                Paragraph(edu.get("year",""), s["edu_period"]),
                left_pct=0.75,
            ))
            if edu.get("institution"):
                story.append(Paragraph(edu["institution"], s["edu_inst"]))

    # TECNOLOGIAS
    skills = profile.get("skills", {})
    skill_map = [
        ("Backend",        skills.get("backend", [])),
        ("Frontend",       skills.get("frontend", [])),
        ("Bases de datos", skills.get("databases", [])),
        ("Herramientas",   skills.get("tools", [])),
    ]
    if any(items for _, items in skill_map):
        story += section_title("Tecnologías", s)
        for label, items in skill_map:
            if items:
                story.append(Paragraph(f"<b>{label}:</b>  {' · '.join(items)}", s["skill_row"]))

    # IDIOMAS
    langs = skills.get("languages", [])
    if langs:
        story += section_title("Idiomas", s)
        story.append(Paragraph("   |   ".join(langs), s["skill_row"]))

    doc.build(story)
    return buffer.getvalue()