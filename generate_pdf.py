from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, KeepTogether)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Colors matching the original document
BROWN = colors.HexColor('#6B5B45')
BROWN_DARK = colors.HexColor('#5A4A38')
BG_HEADER = colors.HexColor('#7B6B55')
BG_ROW_LIGHT = colors.HexColor('#F5F0EB')
BG_ROW_DARK = colors.HexColor('#EDE6DC')
GRAY_TEXT = colors.HexColor('#555555')
WHITE = colors.white
BLACK = colors.HexColor('#1A1A1A')

doc = SimpleDocTemplate(
    '/home/user/staff/VillaMontessori_Voiceover_Utileria.pdf',
    pagesize=A4,
    rightMargin=2*cm,
    leftMargin=2*cm,
    topMargin=2.5*cm,
    bottomMargin=2.5*cm,
)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'Title', parent=styles['Normal'],
    fontSize=22, fontName='Helvetica-Bold',
    textColor=BROWN_DARK, alignment=TA_CENTER,
    spaceAfter=4
)
subtitle_style = ParagraphStyle(
    'Subtitle', parent=styles['Normal'],
    fontSize=13, fontName='Helvetica',
    textColor=BROWN_DARK, alignment=TA_CENTER,
    spaceAfter=2
)
tagline_style = ParagraphStyle(
    'Tagline', parent=styles['Normal'],
    fontSize=10, fontName='Helvetica-Oblique',
    textColor=BROWN, alignment=TA_CENTER,
    spaceAfter=0
)
section_title_style = ParagraphStyle(
    'SectionTitle', parent=styles['Normal'],
    fontSize=13, fontName='Helvetica-Bold',
    textColor=WHITE, alignment=TA_LEFT,
    spaceAfter=0, spaceBefore=0,
    leftIndent=8
)
scene_label_style = ParagraphStyle(
    'SceneLabel', parent=styles['Normal'],
    fontSize=9, fontName='Helvetica-Bold',
    textColor=GRAY_TEXT, alignment=TA_LEFT,
    spaceAfter=0
)
vo_text_style = ParagraphStyle(
    'VOText', parent=styles['Normal'],
    fontSize=10, fontName='Helvetica-Oblique',
    textColor=BLACK, alignment=TA_LEFT,
    spaceAfter=0, leftIndent=4
)
pause_style = ParagraphStyle(
    'Pause', parent=styles['Normal'],
    fontSize=9, fontName='Helvetica',
    textColor=GRAY_TEXT, alignment=TA_LEFT,
    spaceAfter=0, leftIndent=4
)
note_style = ParagraphStyle(
    'Note', parent=styles['Normal'],
    fontSize=9, fontName='Helvetica-Oblique',
    textColor=BROWN, alignment=TA_LEFT,
    spaceAfter=0
)
body_style = ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontSize=10, fontName='Helvetica',
    textColor=BLACK, alignment=TA_LEFT,
    spaceAfter=0
)
confidential_style = ParagraphStyle(
    'Confidential', parent=styles['Normal'],
    fontSize=8, fontName='Helvetica',
    textColor=GRAY_TEXT, alignment=TA_LEFT,
)
page_num_style = ParagraphStyle(
    'PageNum', parent=styles['Normal'],
    fontSize=8, fontName='Helvetica-Bold',
    textColor=GRAY_TEXT, alignment=TA_LEFT,
)

def section_header(text):
    data = [[Paragraph(text, section_title_style)]]
    t = Table(data, colWidths=[17*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_HEADER),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [BG_HEADER]),
        ('TOPPADDING', (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('ROUNDEDCORNERS', [3,3,3,3]),
    ]))
    return t

def scene_row(scene_name, vo_lines):
    """Creates a two-column table row: scene label | voiceover lines"""
    vo_content = []
    for line in vo_lines:
        if line.startswith('[') and line.endswith(']'):
            vo_content.append(Paragraph(line, pause_style))
        elif line == '':
            vo_content.append(Spacer(1, 4))
        else:
            vo_content.append(Paragraph(line, vo_text_style))

    data = [
        [Paragraph(scene_name, scene_label_style), vo_content[0] if vo_content else Paragraph('', body_style)]
    ]
    for item in vo_content[1:]:
        data.append(['', item])

    t = Table(data, colWidths=[4.5*cm, 12.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), BG_ROW_DARK),
        ('BACKGROUND', (1,0), (1,-1), BG_ROW_LIGHT),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.HexColor('#D5CAB8')),
        ('SPAN', (0,0), (0,-1)),
    ]))
    return t

def props_table(category, items):
    rows = [[Paragraph(category, ParagraphStyle('Cat', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica-Bold', textColor=WHITE))]]
    t_header = Table(rows, colWidths=[17*cm])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BROWN),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))

    item_rows = []
    for i, item in enumerate(items):
        bg = BG_ROW_LIGHT if i % 2 == 0 else BG_ROW_DARK
        item_rows.append(
            [Paragraph(f'◾  {item}', ParagraphStyle('Item', parent=styles['Normal'],
                fontSize=9.5, fontName='Helvetica', textColor=BLACK,
                leftIndent=4))]
        )

    t_items = Table(item_rows, colWidths=[17*cm])
    style_cmds = [
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
    ]
    for i in range(len(item_rows)):
        bg = BG_ROW_LIGHT if i % 2 == 0 else BG_ROW_DARK
        style_cmds.append(('BACKGROUND', (0,i), (-1,i), bg))
    t_items.setStyle(TableStyle(style_cmds))

    return [t_header, t_items]


# ─── Build story ─────────────────────────────────────────────────────────────
story = []

# Title block
story.append(Spacer(1, 0.3*cm))
story.append(Paragraph('<strike>VILLA MONTESSORI</strike>', title_style))
story.append(Paragraph('Voiceover Completo + Listado de Utilería', subtitle_style))
story.append(Paragraph('Video Promocional Principal', subtitle_style))
story.append(Spacer(1, 0.6*cm))
story.append(HRFlowable(width='100%', thickness=1, color=BROWN, spaceAfter=6))
story.append(Paragraph('Raíces para un futuro infinito', tagline_style))
story.append(HRFlowable(width='100%', thickness=1, color=BROWN, spaceBefore=6))
story.append(Spacer(1, 1*cm))

# ─── SECTION 1: VOICEOVER ────────────────────────────────────────────────────
story.append(section_header('01 — Voiceover Completo'))
story.append(Spacer(1, 0.2*cm))

note_data = [[Paragraph('Voz cálida, pausada, femenina o masculina grave. Grabación en post-producción.', note_style)]]
note_t = Table(note_data, colWidths=[17*cm])
note_t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FDF8F2')),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ('LEFTPADDING', (0,0), (-1,-1), 10),
    ('BOX', (0,0), (-1,-1), 0.5, BROWN),
]))
story.append(note_t)
story.append(Spacer(1, 0.3*cm))

scenes = [
    ('ESCENA 1\nAPERTURA\n[0 – 5s]', [
        '"Hay lugares donde los niños simplemente asisten a clases…"',
        '[pausa — corte a close-up de ojos]',
        '"…y hay lugares donde son verdaderamente conocidos."',
    ]),
    ('ESCENA 2\nLA EXPERIENCIA\n[5 – 20s]', [
        '"Aquí cada niño aprende a su ritmo."',
        '[pausa]',
        '"En un ambiente donde sentirse seguro… no es opcional."',
    ]),
    ('ESCENA 3\nEL ORIGEN\n[20 – 38s]', [
        '"Villa Montessori nació de una búsqueda personal."',
        '[pausa]',
        '"Una madre que quería algo más humano para su hija."',
        '[pausa]',
        '"Esa búsqueda se convirtió en una comunidad que lleva 17 años acompañando familias en Punta Cana."',
    ]),
    ('ESCENA 4\nFAMILIA & COMUNIDAD\n[38 – 55s]', [
        '"Una familia."',
        '[pausa]',
        '"Una comunidad."',
        '[pausa]',
        '"Un lugar donde la cercanía y el respeto por la infancia no son valores decorativos — son la base de todo."',
    ]),
    ('ESCENA 5\nCIERRE EMOCIONAL\n[55 – 70s]', [
        '"Porque la educación más poderosa no solo transmite conocimiento…"',
        '[pausa larga]',
        '"…también ayuda a que los niños se sientan capaces, valorados y profundamente vistos."',
    ]),
]

for scene_name, vo_lines in scenes:
    story.append(KeepTogether(scene_row(scene_name, vo_lines)))
    story.append(Spacer(1, 0.15*cm))

story.append(Spacer(1, 0.8*cm))

# ─── SECTION 2: PROPS ────────────────────────────────────────────────────────
story.append(section_header('02 — Listado de Utilería'))
story.append(Spacer(1, 0.3*cm))

props_sections = [
    ('Materiales Montessori — Escenas 1, 2 y 3', [
        'Materiales Montessori sobre mesa para macro shot de apertura (bandejas, cilindros, letras de lija, cuentas, etc.)',
        'Estantes con materiales organizados para que el niño elija (estantería baja tipo Montessori)',
        'Materiales de trabajo en mesa para close-ups de manos',
    ]),
    ('Ambientación del Salón — Escenas 1, 2 y 3', [
        'Mobiliario de escala infantil (mesas y sillas pequeñas)',
        'Estantes bajos con materiales ordenados y accesibles',
    ]),
    ('Utilería de la Directora — Escena 3', [
        'Materiales que la directora pueda acomodar/preparar de forma natural',
        '2–3 fotografías antiguas del colegio (impresas o digitales — para efecto Ken Burns en edición)',
    ]),
    ('Exteriores — Jardín / Fachada — Escenas 4 y 5', [
        'El espacio natural del jardín y patio tal como está (sin utilería adicional necesaria)',
    ]),
    ('Equipo Técnico de Rodaje', [
        'Sony A7S III',
        'Lente 35mm T1.4',
        'Lente Sigma 24-70mm f2.8',
        'Gimbal DJI RS3 o similar',
        'Trípode con rótula de bola',
        'Reflector blanco (fill de luz natural)',
        'Tarjetas CFexpress o SD V90 (alta velocidad para 4K 120fps)',
        'Baterías Sony A7S III — mínimo 3 unidades',
    ]),
    ('Documentación / Logística — INDISPENSABLE', [
        'Formularios de permiso firmados por los padres (autorización de imagen de menores)',
    ]),
]

for category, items in props_sections:
    group = props_table(category, items)
    story.append(KeepTogether(group + [Spacer(1, 0.25*cm)]))

story.append(Spacer(1, 0.5*cm))

# Final note
note2_data = [[Paragraph(
    '<b>Nota:</b> Los materiales Montessori son el elemento de utilería más crítico del video — '
    'deben ser auténticos, en buen estado y organizados de forma coherente con la metodología. '
    'Confirmar con la escuela cuáles tienen disponibles antes del día de rodaje.',
    ParagraphStyle('FinalNote', parent=styles['Normal'], fontSize=9,
                   fontName='Helvetica', textColor=BROWN_DARK, leftIndent=4))]]
note2_t = Table(note2_data, colWidths=[17*cm])
note2_t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FDF8F2')),
    ('TOPPADDING', (0,0), (-1,-1), 8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ('LEFTPADDING', (0,0), (-1,-1), 12),
    ('BOX', (0,0), (-1,-1), 0.8, BROWN),
]))
story.append(note2_t)

# ─── Footer callback ──────────────────────────────────────────────────────────
def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(GRAY_TEXT)
    canvas.drawString(2*cm, 1.5*cm, 'VILLA MONTESSORI  |  Voiceover Completo + Listado de Utilería')
    canvas.drawRightString(A4[0] - 2*cm, 1.5*cm, f'Página {doc.page}')
    canvas.setStrokeColor(BROWN)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.8*cm, A4[0] - 2*cm, 1.8*cm)
    canvas.restoreState()

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("PDF generado correctamente.")
