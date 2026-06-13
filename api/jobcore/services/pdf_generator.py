import io
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT

# ── Paleta de Colores Corporativa y Elegante (ATS-Friendly) ─────────────────
PRIMARY = colors.HexColor("#1e293b")     # Slate oscuro para textos principales
TEXT_DARK = colors.HexColor("#334155")   # Gris azulado para descripciones y bullets
ACCENT = colors.HexColor("#0284c7")      # Azul sutil para títulos de sección e impacto
MUTED = colors.HexColor("#64748b")       # Gris medio para fechas y locación
LINE_COLOR = colors.HexColor("#e2e8f0")  # Gris claro para bordes limpios

PAGE_W, PAGE_H = A4
MARGIN_H = 1.5 * cm  
MARGIN_V = 1.5 * cm
CONTENT_W = PAGE_W - 2 * MARGIN_H

# ── Estilos Tipográficos Optimizados ──────────────────────────────────────────
def make_styles():
    return {
        # Header Principal
        "name": ParagraphStyle(
            "name", fontName="Helvetica-Bold", fontSize=24,
            textColor=PRIMARY, leading=28, spaceAfter=2,
        ),
        "headline": ParagraphStyle(
            "headline", fontName="Helvetica-Bold", fontSize=11,
            textColor=ACCENT, leading=15, spaceAfter=4,
        ),
        "contact_line": ParagraphStyle(
            "contact_line", fontName="Helvetica", fontSize=9,
            textColor=TEXT_DARK, leading=14, spaceAfter=0,
        ),

        # Secciones con diseño moderno de línea inferior nativa
        "section": ParagraphStyle(
            "section", fontName="Helvetica-Bold", fontSize=11,
            textColor=ACCENT, leading=14, spaceBefore=12, spaceAfter=8,
            borderColor=LINE_COLOR, borderWidth=1, borderPadding=(0, 0, 4, 0)
        ),

        # Resumen Profesional
        "summary": ParagraphStyle(
            "summary", fontName="Helvetica", fontSize=9.5,
            textColor=TEXT_DARK, leading=14.5, spaceAfter=0,
            alignment=TA_LEFT,
        ),

        # Experiencia Laboral y Educación
        "job_title": ParagraphStyle(
            "job_title", fontName="Helvetica-Bold", fontSize=10.5,
            textColor=PRIMARY, leading=14,
        ),
        "job_period": ParagraphStyle(
            "job_period", fontName="Helvetica", fontSize=9,
            textColor=MUTED, leading=14, alignment=TA_RIGHT,
        ),
        "job_company": ParagraphStyle(
            "job_company", fontName="Helvetica-Bold", fontSize=9.5,
            textColor=TEXT_DARK, leading=13, spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Helvetica", fontSize=9,
            textColor=TEXT_DARK, leading=13.5, 
            leftIndent=12, firstLineIndent=0, spaceAfter=3,
        ),

        # Tecnologías y Habilidades
        "skill_label": ParagraphStyle(
            "skill_label", fontName="Helvetica-Bold", fontSize=9,
            textColor=PRIMARY, leading=13,
        ),
        "skill_text": ParagraphStyle(
            "skill_text", fontName="Helvetica", fontSize=9,
            textColor=TEXT_DARK, leading=13,
        ),
    }

# ── Helpers de Estructura / Layout ────────────────────────────────────────────
def two_col(left, right, left_pct=0.75):
    """Tabla de dos columnas limpia y perfectamente alineada horizontalmente."""
    t = Table(
        [[left, right]],
        colWidths=[CONTENT_W * left_pct, CONTENT_W * (1 - left_pct)],
    )
    t.setStyle(TableStyle([
        ("VALIGN",         (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",    (0,0), (-1,-1), 0),
        ("RIGHTPADDING",   (0,0), (-1,-1), 0),
        ("TOPPADDING",     (0,0), (-1,-1), 0),
        ("BOTTOMPADDING",  (0,0), (-1,-1), 0),
    ]))
    return t

# ── Generador Principal del CV ────────────────────────────────────────────────
def generate_cv_pdf(profile: dict, scraped_data: dict = None) -> bytes:
    buffer = io.BytesIO()
    s = make_styles()

    # Integración simulada de la tubería de IA
    if scraped_data:
        try:
            from jobcore.services.ai_handler import adapt_cv_for_job
            print("Adaptando CV con IA...")
            profile = adapt_cv_for_job(scraped_data)
        except ImportError:
            print("ai_handler no disponible, usando perfil original.")

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=MARGIN_H, rightMargin=MARGIN_H,
        topMargin=MARGIN_V,  bottomMargin=MARGIN_V,
        title=profile.get("name", "CV"),
        author=profile.get("name", ""),
        subject="Curriculum Vitae",
    )

    story = []

    # ── HEADER ────────────────────────────────────────────────────────────────
    if profile.get("name"):
        story.append(Paragraph(profile["name"], s["name"]))
    if profile.get("headline"):
        story.append(Paragraph(profile["headline"], s["headline"]))
    
    story.append(Spacer(1, 2))

    # Línea de contacto optimizada usando barras verticales legibles para ATS
    contact_parts = [
        profile.get("email", ""),
        profile.get("phone", ""),
        profile.get("location", ""),
        profile.get("linkedin", ""),
        profile.get("github", ""),
    ]
    contact_line = "  |  ".join(p for p in contact_parts if p)
    if contact_line.strip():
        story.append(Paragraph(contact_line, s["contact_line"]))
    story.append(Spacer(1, 6))

    # ── RESUMEN PROFESIONAL ───────────────────────────────────────────────────
    if profile.get("summary"):
        story.append(Paragraph("PERFIL PROFESIONAL", s["section"]))
        story.append(Paragraph(profile["summary"], s["summary"]))

    # ── EXPERIENCIA LABORAL ───────────────────────────────────────────────────
    if profile.get("experience"):
        story.append(Paragraph("EXPERIENCIA LABORAL", s["section"]))
        for i, exp in enumerate(profile["experience"]):
            block = []
            
            # Título del Puesto y Período alineados perfectamente
            title_p = Paragraph(exp.get("title", ""), s["job_title"])
            period_p = Paragraph(exp.get("period", ""), s["job_period"])
            block.append(two_col(title_p, period_p, left_pct=0.75))
            
            # Empresa / Organización
            if exp.get("company"):
                block.append(Paragraph(exp["company"], s["job_company"]))
            
            # Formato nativo de viñetas para ReportLab (Mantiene sangrías correctas)
            for b in exp.get("bullets", []):
                block.append(Paragraph(b, s["bullet"], bulletText="•"))
            
            if i < len(profile["experience"]) - 1:
                block.append(Spacer(1, 6))
            
            story.append(KeepTogether(block))

    # ── EDUCACIÓN ─────────────────────────────────────────────────────────────
    if profile.get("education"):
        story.append(Paragraph("FORMACIÓN ACADÉMICA", s["section"]))
        for i, edu in enumerate(profile["education"]):
            block = []
            degree_p = Paragraph(edu.get("degree", ""), s["job_title"])
            year_p = Paragraph(edu.get("year", ""), s["job_period"])
            block.append(two_col(degree_p, year_p, left_pct=0.75))
            
            if edu.get("institution"):
                block.append(Paragraph(edu["institution"], s["job_company"]))
                
            if i < len(profile["education"]) - 1:
                block.append(Spacer(1, 4))
                
            story.append(KeepTogether(block))

    # ── TECNOLOGÍAS ───────────────────────────────────────────────────────────
    skills = profile.get("skills", {})
    skill_map = [
        ("Backend:",        skills.get("backend", [])),
        ("Frontend:",       skills.get("frontend", [])),
        ("Bases de Datos:", skills.get("databases", [])),
        ("Herramientas:",   skills.get("tools", [])),
    ]
    
    if any(items for _, items in skill_map):
        story.append(Paragraph("COMPETENCIAS TÉCNICAS", s["section"]))
        rows = []
        for label, items in skill_map:
            if items:
                rows.append([
                    Paragraph(label, s["skill_label"]),
                    Paragraph(", ".join(items), s["skill_text"]),
                ])
        if rows:
            tech_table = Table(rows, colWidths=[CONTENT_W * 0.18, CONTENT_W * 0.82])
            tech_table.setStyle(TableStyle([
                ("VALIGN",         (0,0), (-1,-1), "TOP"),
                ("LEFTPADDING",    (0,0), (-1,-1), 0),
                ("RIGHTPADDING",   (0,0), (-1,-1), 0),
                ("TOPPADDING",     (0,0), (-1,-1), 2),
                ("BOTTOMPADDING",  (0,0), (-1,-1), 2),
            ]))
            story.append(tech_table)

    # ── IDIOMAS ───────────────────────────────────────────────────────────────
    langs = skills.get("languages", [])
    if langs:
        story.append(Paragraph("IDIOMAS", s["section"]))
        story.append(Paragraph(", ".join(langs), s["skill_text"]))

    doc.build(story)
    return buffer.getvalue()


# ── Datos de Estructura ───────────────────────────────────────────────────────
PROFILE = {
    "name": "Timoteo Pereyra",
    "headline": "Desarrollador Full Stack  ·  PHP  ·  Laravel  ·  JavaScript  ·  Python",
    "email": "timopereyra@gmail.com",
    "phone": "(+54) 2345 425347",
    "location": "Buenos Aires, AR",
    "linkedin": "linkedin.com/in/timoteo-pereyra",
    "summary": (
        "Desarrollador Full Stack con más de 3 años de experiencia construyendo y "
        "manteniendo aplicaciones web en producción para los sectores de gestión "
        "empresarial y salud digital. Especializado en PHP/Laravel, JavaScript y Python, con "
        "historial comprobado de reducir tiempos de respuesta en sistemas de alta carga "
        "y de entregar funcionalidades end-to-end de manera autónoma. Aportaré solidez "
        "técnica, criterio arquitectónico y ownership real del código desde el primer día."
    ),
    "experience": [
        {
            "title": "Analista Desarrollador",
            "company": "Uakika",
            "period": "Nov 2023 – Mar 2025",
            "bullets": [
                "Mantuve 2 sistemas web en producción (Laravel + HTML/CSS y CodeIgniter + jQuery) para áreas de negocio distintas, sin interrupciones de servicio.",
                "Optimicé consultas SQL críticas en pantallas de alta carga, reduciendo tiempos de respuesta de forma medible.",
                "Desarrollé funcionalidades end-to-end: desde el relevamiento de requerimientos con stakeholders hasta el despliegue en producción.",
                "Participé en la planificación técnica de sprints y en la documentación de decisiones de arquitectura.",
            ],
        },
        {
            "title": "Analista Desarrollador",
            "company": "Health Management Solutions",
            "period": "Abr 2023 – Nov 2023",
            "bullets": [
                "Lideré la migración de Oracle Forms legacy a Oracle Apex, reduciendo deuda técnica y modernizando la interfaz para usuarios clínicos.",
                "Desarrollé plugins personalizados en Oracle Apex y procedimientos almacenados en PL/SQL para automatizar procesos críticos de gestión de salud.",
                "Integré servicios externos para sincronización de datos entre sistemas, garantizando consistencia e integridad de la información.",
                "Resolví incidencias en producción con diagnóstico preciso y seguimiento hasta el cierre.",
            ],
        },
        {
            "title": "Soporte Técnico",
            "company": "Centro Universitario Chivilcoy",
            "period": "Mar 2023 – Nov 2023",
            "bullets": [
                "Brindé asistencia técnica a usuarios, diagnosticando y resolviendo problemas de hardware y software en entorno universitario.",
            ],
        },
        {
            "title": "Desarrollador – Proyecto de Tesina",
            "company": "Centro Universitario Chivilcoy",
            "period": "Jun 2022 – Nov 2022",
            "bullets": [
                "Diseñé e implementé (frontend + backend) un sistema web de pedidos multi-categoría con gestión dinámica de servicios.",
                "Stack: PHP · JavaScript · HTML · CSS · MySQL.",
            ],
        },
    ],
    "education": [
        {
            "degree": "Tecnicatura Universitaria en Programación",
            "institution": "UTN Regional San Nicolás",
            "year": "Mar 2021 – Nov 2022",
        }
    ],
    "skills": {
        "backend":   ["PHP", "Laravel", "CodeIgniter", "Node.js", "Python", "C/C++"],
        "frontend":  ["JavaScript", "jQuery", "HTML5", "CSS3", "Bootstrap", "React", "Tailwind"],
        "databases": ["MySQL", "SQL", "PL/SQL", "Oracle Apex", "MongoDB"],
        "tools":     ["Git", "Linux", "REST APIs", "Postman"],
        "languages": ["Inglés B1 — lectura técnica fluida, documentación y comunicación escrita"],
    },
}

if __name__ == "__main__":
    pdf_bytes = generate_cv_pdf(PROFILE)
    output_path = "/tmp/CV_Timoteo_Pereyra.pdf" 
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)
    print(f"PDF generado exitosamente en: {output_path}")