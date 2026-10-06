from fpdf import FPDF

# Paleta Natura (tons terrosos + verde + acentos vibrantes)
VERDE_FLORESTA = (34, 68, 45)
VERDE_CLARO = (120, 160, 110)
BEGE = (244, 238, 226)
MARROM_TERRA = (120, 80, 45)
TERRACOTA = (198, 110, 60)
AMARELO_SOL = (232, 180, 60)
OFFWHITE = (252, 250, 245)
CINZA_TEXTO = (50, 50, 50)

class PDF(FPDF):
    def header(self):
        self.set_fill_color(*VERDE_FLORESTA)
        self.rect(0, 0, 210, 20, 'F')
        # círculos decorativos no cabeçalho
        self.set_fill_color(*TERRACOTA)
        self.ellipse(170, -10, 30, 30, 'F')
        self.set_fill_color(*AMARELO_SOL)
        self.ellipse(185, 5, 25, 25, 'F')
        self.set_fill_color(*VERDE_CLARO)
        self.ellipse(-8, -8, 22, 22, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 13)
        self.set_y(6)
        self.cell(0, 8, 'Skill: Criacao de Documentos no Estilo Natura', align='C')
        self.ln(18)

    def footer(self):
        self.set_y(-14)
        self.set_fill_color(*BEGE)
        self.rect(0, 283, 210, 14, 'F')
        self.set_text_color(*MARROM_TERRA)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 8, f'Pagina {self.page_no()} - Bem Estar Bem', align='C')

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=22)
pdf.add_page()
pdf.set_fill_color(*OFFWHITE)
pdf.rect(0, 20, 210, 270, 'F')

with open('skill.md', encoding='utf-8') as f:
    lines = f.read().splitlines()

acent_cycle = [TERRACOTA, AMARELO_SOL, VERDE_CLARO, MARROM_TERRA]
i = 0
for line in lines:
    line = line.rstrip()
    if line.startswith('# '):
        pdf.set_font('Helvetica', 'B', 17)
        pdf.set_text_color(*VERDE_FLORESTA)
        pdf.multi_cell(0, 9, line[2:])
        pdf.ln(1)
        # faixa colorida sob o título
        pdf.set_fill_color(*TERRACOTA)
        pdf.rect(pdf.l_margin, pdf.get_y(), 40, 2, 'F')
        pdf.set_fill_color(*AMARELO_SOL)
        pdf.rect(pdf.l_margin + 42, pdf.get_y(), 20, 2, 'F')
        pdf.ln(4)
    elif line.startswith('## '):
        pdf.ln(4)
        y = pdf.get_y()
        pdf.set_fill_color(*BEGE)
        pdf.rect(pdf.l_margin, y, 190, 8, 'F')
        cor = acent_cycle[i % len(acent_cycle)]
        pdf.set_fill_color(*cor)
        pdf.rect(pdf.l_margin, y, 4, 8, 'F')
        pdf.set_x(pdf.l_margin + 8)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(*MARROM_TERRA)
        pdf.cell(0, 8, line[3:])
        pdf.ln(10)
        i += 1
    elif line.startswith('- '):
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(*CINZA_TEXTO)
        cor = acent_cycle[i % len(acent_cycle)]
        pdf.set_fill_color(*cor)
        pdf.ellipse(pdf.l_margin + 1, pdf.get_y() + 1.5, 2.5, 2.5, 'F')
        pdf.set_x(pdf.l_margin + 7)
        pdf.multi_cell(0, 6, line[2:])
        pdf.set_x(pdf.l_margin)
    elif line.strip() and line[0].isdigit() and '. ' in line[:4]:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(*VERDE_FLORESTA)
        pdf.multi_cell(0, 6, '  ' + line)
        pdf.set_x(pdf.l_margin)
    elif line.strip() == '':
        pdf.ln(2)
    else:
        pdf.set_font('Helvetica', '', 10)
        pdf.set_text_color(*CINZA_TEXTO)
        pdf.multi_cell(0, 6, line)
        pdf.set_x(pdf.l_margin)

# detalhe final: folhas estilizadas no fim
y = pdf.get_y() + 6
pdf.set_fill_color(*VERDE_CLARO)
pdf.ellipse(95, y, 10, 5, 'F')
pdf.set_fill_color(*VERDE_FLORESTA)
pdf.ellipse(105, y + 2, 10, 5, 'F')

pdf.output('skill.pdf')
print('criado skill.pdf colorido')
