from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, KeepTogether, Image as RLImage)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from PIL import Image, ImageDraw, ImageFilter
import os, io

# ─── Color palette ─────────────────────────────────────────────────────────
BROWN        = colors.HexColor('#6B5B45')
BROWN_DARK   = colors.HexColor('#5A4A38')
BG_HEADER    = colors.HexColor('#7B6B55')
BG_ROW_LIGHT = colors.HexColor('#F5F0EB')
BG_ROW_DARK  = colors.HexColor('#EDE6DC')
GRAY_TEXT    = colors.HexColor('#555555')
ORANGE_WARM  = colors.HexColor('#C8845A')
WHITE        = colors.white
BLACK        = colors.HexColor('#1A1A1A')
CREAM        = colors.HexColor('#FDF8F2')
BORDER_COLOR = colors.HexColor('#D5CAB8')

# ─── Styles ────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, parent=styles['Normal'], **kw)

title_s      = S('T',  fontSize=22, fontName='Helvetica-Bold',   textColor=BROWN_DARK, alignment=TA_CENTER, spaceAfter=4)
subtitle_s   = S('Su', fontSize=12, fontName='Helvetica',        textColor=BROWN_DARK, alignment=TA_CENTER, spaceAfter=2)
tagline_s    = S('Tg', fontSize=10, fontName='Helvetica-Oblique',textColor=BROWN,      alignment=TA_CENTER)
sec_title_s  = S('St', fontSize=13, fontName='Helvetica-Bold',   textColor=WHITE,      leftIndent=8)
scene_lbl_s  = S('Sl', fontSize=8,  fontName='Helvetica-Bold',   textColor=WHITE,      alignment=TA_CENTER)
vo_s         = S('V',  fontSize=10, fontName='Helvetica-Oblique',textColor=BLACK,      leftIndent=4, spaceAfter=2)
pause_s      = S('P',  fontSize=9,  fontName='Helvetica',        textColor=GRAY_TEXT,  leftIndent=4, spaceAfter=2)
body_s       = S('B',  fontSize=10, fontName='Helvetica',        textColor=BLACK)
note_s       = S('N',  fontSize=9,  fontName='Helvetica-Oblique',textColor=BROWN)
cat_s        = S('C',  fontSize=9,  fontName='Helvetica-Bold',   textColor=WHITE)
item_s       = S('I',  fontSize=9.5,fontName='Helvetica',        textColor=BLACK,      leftIndent=4)
img_cap_s    = S('Ic', fontSize=7.5,fontName='Helvetica-Oblique',textColor=GRAY_TEXT,  alignment=TA_CENTER)
ref_url_s    = S('Ru', fontSize=6.5,fontName='Helvetica',        textColor=colors.HexColor('#8B7355'), alignment=TA_CENTER)

# ─── Gradient placeholder images ───────────────────────────────────────────
IMG_DATA = [
    {
        'filename': 'ref_images/img1_materials.png',
        'colors':   [(210,175,130), (180,140,90)],
        'label':    'Materiales Montessori sobre mesa',
        'icon':     '📦',
    },
    {
        'filename': 'ref_images/img2_shelf.png',
        'colors':   [(190,160,120), (160,125,80)],
        'label':    'Estantería baja con materiales',
        'icon':     '📚',
    },
    {
        'filename': 'ref_images/img3_hands.png',
        'colors':   [(220,185,145), (195,155,105)],
        'label':    'Manos de niño — close-up',
        'icon':     '🤲',
    },
    {
        'filename': 'ref_images/img4_garden.png',
        'colors':   [(160,200,140), (120,170,100)],
        'label':    'Jardín exterior del colegio',
        'icon':     '🌿',
    },
]

IMG_URLS = [
    "https://d8j0ntlcm91z4.cloudfront.net/user_30DDdq4kdoIkXStVffZRJcvQchF/hf_20260609_030858_f77dce49-9165-452c-a2b2-b79d48f3b9a8.png",
    "https://d8j0ntlcm91z4.cloudfront.net/user_30DDdq4kdoIkXStVffZRJcvQchF/hf_20260609_030914_1c99ce4d-0800-4830-b3d2-602394596ce9.png",
    "https://d8j0ntlcm91z4.cloudfront.net/user_30DDdq4kdoIkXStVffZRJcvQchF/hf_20260609_030915_c2304cd1-ba63-4865-8ef7-c23c8777fe4a.png",
    "https://d8j0ntlcm91z4.cloudfront.net/user_30DDdq4kdoIkXStVffZRJcvQchF/hf_20260609_030916_7d9addec-c546-4358-aaa8-33ca4e261f4f.png",
]

os.makedirs('ref_images', exist_ok=True)

def make_gradient_img(path, color1, color2, w=640, h=200, label=''):
    img = Image.new('RGB', (w, h))
    draw = ImageDraw.Draw(img)
    for x in range(w):
        r = int(color1[0] + (color2[0]-color1[0]) * x/w)
        g = int(color1[1] + (color2[1]-color1[1]) * x/w)
        b = int(color1[2] + (color2[2]-color1[2]) * x/w)
        draw.line([(x,0),(x,h)], fill=(r,g,b))
    # subtle vignette overlay
    vig = Image.new('RGBA', (w,h), (0,0,0,0))
    vd = ImageDraw.Draw(vig)
    for i in range(40):
        alpha = int(60 * (i/40))
        vd.rectangle([i, i, w-i, h-i], outline=(0,0,0,alpha))
    img.paste(Image.alpha_composite(img.convert('RGBA'), vig).convert('RGB'))
    # label text placeholder
    draw = ImageDraw.Draw(img)
    draw.rectangle([w//2-120, h//2-14, w//2+120, h//2+14], fill=(255,255,255,180))
    img.save(path)
    return path

for d in IMG_DATA:
    make_gradient_img(d['filename'], d['colors'][0], d['colors'][1], label=d['label'])

# ─── Helpers ───────────────────────────────────────────────────────────────
def section_header(text):
    t = Table([[Paragraph(text, sec_title_s)]], colWidths=[17*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), BG_HEADER),
        ('TOPPADDING',    (0,0),(-1,-1), 8),
        ('BOTTOMPADDING', (0,0),(-1,-1), 8),
        ('LEFTPADDING',   (0,0),(-1,-1), 10),
    ]))
    return t

def scene_row(scene_name, vo_lines):
    label_cell = Table(
        [[Paragraph(scene_name, scene_lbl_s)]],
        colWidths=[3.8*cm]
    )
    label_cell.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), BROWN),
        ('TOPPADDING',    (0,0),(-1,-1), 10),
        ('BOTTOMPADDING', (0,0),(-1,-1), 10),
        ('LEFTPADDING',   (0,0),(-1,-1), 6),
        ('RIGHTPADDING',  (0,0),(-1,-1), 6),
        ('VALIGN',        (0,0),(-1,-1), 'MIDDLE'),
    ]))

    vo_items = []
    for line in vo_lines:
        if line.startswith('[') and line.endswith(']'):
            vo_items.append(Paragraph(line, pause_s))
        elif line == '':
            vo_items.append(Spacer(1,3))
        else:
            vo_items.append(Paragraph(line, vo_s))

    rows = [[label_cell, vo_items[0]]]
    for item in vo_items[1:]:
        rows.append(['', item])

    t = Table(rows, colWidths=[3.8*cm, 13.2*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (1,0),(1,-1), BG_ROW_LIGHT),
        ('VALIGN',        (0,0),(-1,-1), 'TOP'),
        ('TOPPADDING',    (0,0),(-1,-1), 9),
        ('BOTTOMPADDING', (0,0),(-1,-1), 9),
        ('LEFTPADDING',   (0,0),(-1,-1), 0),
        ('RIGHTPADDING',  (0,0),(-1,-1), 10),
        ('LEFTPADDING',   (1,0),(1,-1), 12),
        ('LINEBELOW',     (0,-1),(-1,-1), 0.5, BORDER_COLOR),
        ('SPAN',          (0,0),(0,-1)),
    ]))
    return t

def ref_image_block(img_path, caption, url, w=8.2*cm):
    """Returns a table cell with gradient image + caption + url."""
    img = RLImage(img_path, width=w, height=w*0.45)
    data = [
        [img],
        [Paragraph(f'<b>{caption}</b>', img_cap_s)],
        [Paragraph(f'↗ Ver imagen generada por IA', ref_url_s)],
    ]
    t = Table(data, colWidths=[w])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), CREAM),
        ('TOPPADDING',    (0,0),(-1,-1), 4),
        ('BOTTOMPADDING', (0,0),(-1,-1), 4),
        ('LEFTPADDING',   (0,0),(-1,-1), 4),
        ('RIGHTPADDING',  (0,0),(-1,-1), 4),
        ('BOX',           (0,0),(-1,-1), 0.5, BORDER_COLOR),
        ('ALIGN',         (0,0),(-1,-1), 'CENTER'),
    ]))
    return t

def image_grid(items):
    """2-column grid of image reference blocks."""
    row = [ref_image_block(items[0][0], items[0][1], items[0][2]),
           ref_image_block(items[1][0], items[1][1], items[1][2])]
    t = Table([row], colWidths=[8.3*cm, 8.3*cm])
    t.setStyle(TableStyle([
        ('LEFTPADDING',  (0,0),(-1,-1), 3),
        ('RIGHTPADDING', (0,0),(-1,-1), 3),
        ('TOPPADDING',   (0,0),(-1,-1), 0),
        ('BOTTOMPADDING',(0,0),(-1,-1), 0),
    ]))
    return t

def props_section(category, items, accent=BROWN):
    header_row = [[Paragraph(category, cat_s)]]
    th = Table(header_row, colWidths=[17*cm])
    th.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),(-1,-1), accent),
        ('TOPPADDING',    (0,0),(-1,-1), 6),
        ('BOTTOMPADDING', (0,0),(-1,-1), 6),
        ('LEFTPADDING',   (0,0),(-1,-1), 12),
    ]))
    item_rows = [[Paragraph(f'◾  {i}', item_s)] for i in items]
    ti = Table(item_rows, colWidths=[17*cm])
    cmds = [('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LEFTPADDING',(0,0),(-1,-1),16),('RIGHTPADDING',(0,0),(-1,-1),10)]
    for idx in range(len(item_rows)):
        cmds.append(('BACKGROUND',(0,idx),(-1,idx),
                     BG_ROW_LIGHT if idx%2==0 else BG_ROW_DARK))
    ti.setStyle(TableStyle(cmds))
    return [th, ti]

# ─── Build document ────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    '/home/user/staff/VillaMontessori_Voiceover_Utileria.pdf',
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2.5*cm, bottomMargin=2.5*cm,
)

story = []

# ── Cover block ─────────────────────────────────────────────────────────────
story.append(Paragraph('VILLA MONTESSORI', title_s))
story.append(Paragraph('Voiceover Completo + Listado de Utilería', subtitle_s))
story.append(Paragraph('Video Promocional Principal', subtitle_s))
story.append(Spacer(1, 0.5*cm))
story.append(HRFlowable(width='100%', thickness=1.5, color=BROWN, spaceAfter=5))
story.append(Paragraph('<i>Raíces para un futuro infinito</i>', tagline_s))
story.append(HRFlowable(width='100%', thickness=1.5, color=BROWN, spaceBefore=5))
story.append(Spacer(1, 0.9*cm))

# ── Section 01: Voiceover ────────────────────────────────────────────────────
story.append(section_header('01 — Voiceover Completo'))
story.append(Spacer(1, 0.2*cm))

note_box = Table(
    [[Paragraph('Voz cálida, pausada, femenina o masculina grave · Grabación en post-producción', note_s)]],
    colWidths=[17*cm]
)
note_box.setStyle(TableStyle([
    ('BACKGROUND',    (0,0),(-1,-1), CREAM),
    ('TOPPADDING',    (0,0),(-1,-1), 7),
    ('BOTTOMPADDING', (0,0),(-1,-1), 7),
    ('LEFTPADDING',   (0,0),(-1,-1), 12),
    ('BOX',           (0,0),(-1,-1), 0.8, BROWN),
]))
story.append(note_box)
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
    ('ESCENA 4\nFAMILIA &\nCOMUNIDAD\n[38 – 55s]', [
        '"Una familia."',
        '[pausa]',
        '"Una comunidad."',
        '[pausa]',
        '"Un lugar donde la cercanía y el respeto por la infancia no son valores decorativos — son la base de todo."',
    ]),
    ('ESCENA 5\nCIERRE\nEMOCIONAL\n[55 – 70s]', [
        '"Porque la educación más poderosa no solo transmite conocimiento…"',
        '[pausa larga]',
        '"…también ayuda a que los niños se sientan capaces, valorados y profundamente vistos."',
    ]),
]

for scene_name, vo_lines in scenes:
    story.append(KeepTogether(scene_row(scene_name, vo_lines)))
    story.append(Spacer(1, 0.15*cm))

story.append(Spacer(1, 0.8*cm))

# ── Section 02: Utilería ─────────────────────────────────────────────────────
story.append(section_header('02 — Listado de Utilería'))
story.append(Spacer(1, 0.35*cm))

# Image references header
ref_header = Table(
    [[Paragraph('Imágenes de Referencia — Generadas con IA', S('RH',
        fontSize=9, fontName='Helvetica-Bold', textColor=BROWN_DARK))]],
    colWidths=[17*cm]
)
ref_header.setStyle(TableStyle([
    ('BACKGROUND',    (0,0),(-1,-1), colors.HexColor('#EDE6DC')),
    ('TOPPADDING',    (0,0),(-1,-1), 5),
    ('BOTTOMPADDING', (0,0),(-1,-1), 5),
    ('LEFTPADDING',   (0,0),(-1,-1), 10),
    ('BOX',           (0,0),(-1,-1), 0.5, BORDER_COLOR),
]))
story.append(ref_header)
story.append(Spacer(1, 0.25*cm))

# 2x2 image grid
story.append(image_grid([
    ('ref_images/img1_materials.png', 'Materiales sobre mesa — Macro Shot', IMG_URLS[0]),
    ('ref_images/img2_shelf.png',     'Estantería Montessori organizada',   IMG_URLS[1]),
]))
story.append(Spacer(1, 0.2*cm))
story.append(image_grid([
    ('ref_images/img3_hands.png', 'Close-up manos de niño — Utensilios', IMG_URLS[2]),
    ('ref_images/img4_garden.png','Exterior jardín — Escenas 4 y 5',      IMG_URLS[3]),
]))
story.append(Spacer(1, 0.5*cm))

# Props tables
sections = [
    ('Materiales Montessori — Escenas 1, 2 y 3', [
        'Materiales Montessori sobre mesa para macro shot de apertura (utensilios, letras de colores, etc.)',
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

accent_colors = [BG_HEADER, BROWN, BG_HEADER, BROWN, BG_HEADER, colors.HexColor('#A0522D')]

for (cat, items), accent in zip(sections, accent_colors):
    group = props_section(cat, items, accent=accent)
    story.append(KeepTogether(group + [Spacer(1, 0.25*cm)]))

story.append(Spacer(1, 0.4*cm))

# Final note
fn = Table([[Paragraph(
    '<b>Nota:</b> Los materiales Montessori son el elemento de utilería más crítico — '
    'deben ser auténticos, en buen estado y organizados de forma coherente con la metodología. '
    'Confirmar con la escuela cuáles tienen disponibles antes del día de rodaje.',
    S('FN', fontSize=9, fontName='Helvetica', textColor=BROWN_DARK, leftIndent=4)
)]], colWidths=[17*cm])
fn.setStyle(TableStyle([
    ('BACKGROUND',    (0,0),(-1,-1), CREAM),
    ('TOPPADDING',    (0,0),(-1,-1), 9),
    ('BOTTOMPADDING', (0,0),(-1,-1), 9),
    ('LEFTPADDING',   (0,0),(-1,-1), 12),
    ('BOX',           (0,0),(-1,-1), 1, BROWN),
]))
story.append(fn)

# ─── Footer ────────────────────────────────────────────────────────────────
def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(GRAY_TEXT)
    canvas.drawString(2*cm, 1.5*cm, 'VILLA MONTESSORI  |  Voiceover Completo + Listado de Utilería')
    canvas.drawRightString(A4[0]-2*cm, 1.5*cm, f'Página {doc.page}')
    canvas.setStrokeColor(colors.HexColor('#C8B89A'))
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.8*cm, A4[0]-2*cm, 1.8*cm)
    canvas.restoreState()

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("PDF v2 generado correctamente.")
