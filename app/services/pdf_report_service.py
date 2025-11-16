"""
Servicio de Generación de Reportes PDF. (NUEVO)

Utiliza ReportLab para "dibujar" el reporte de la solución en un archivo PDF,
incluyendo las tablas intermedias del Simplex.
"""
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

class PdfReportService:
    """Genera un PDF a partir del diccionario 'final_report'."""

    # --- INICIO DE CORRECCIÓN (¡EL BUG ESTABA AQUÍ!) ---
    def __init__(self, report_data: dict, output_filename: str): # ¡DOBLE GUIÓN BAJO!
    # --- FIN DE CORRECCIÓN ---
        self.report_data = report_data
        self.output_filename = output_filename
        self.doc = SimpleDocTemplate(output_filename, pagesize=A4,
                                     rightMargin=1.5*cm, leftMargin=1.5*cm,
                                     topMargin=1.5*cm, bottomMargin=1.5*cm)
        self.story = []
        self.styles = self._setup_styles()

    def _setup_styles(self):
        """Configura estilos de párrafo personalizados."""
        styles = getSampleStyleSheet()
        
        # Renombramos los estilos para que no choquen con los de ReportLab
        styles.add(ParagraphStyle(name='PDFTitle', fontSize=18, alignment=TA_CENTER, spaceAfter=20))
        styles.add(ParagraphStyle(name='PDFHeading1', fontSize=14, spaceAfter=12, spaceBefore=10, textColor=colors.HexColor("#0d6efd")))
        styles.add(ParagraphStyle(name='PDFHeading2', fontSize=12, spaceAfter=8, spaceBefore=8, textColor=colors.HexColor("#343a40")))
        styles.add(ParagraphStyle(name='PDFHeading3', fontSize=10, spaceAfter=6, spaceBefore=6, textColor=colors.HexColor("#555555")))
        styles.add(ParagraphStyle(name='PDFCode', fontName='Courier', fontSize=9, alignment=TA_LEFT, spaceAfter=6, borderPadding=8, backgroundColor=colors.whitesmoke, borderRadius=5, paddingLeft=10, paddingRight=10, paddingTop=10, paddingBottom=10))
        styles.add(ParagraphStyle(name='PDFSuccess', fontSize=12, textColor=colors.darkgreen))
        styles.add(ParagraphStyle(name='PDFFail', fontSize=12, textColor=colors.red))
        
        return styles

    def generate(self) -> str:
        """Construye y guarda el documento PDF. Retorna el path."""
        try:
            self.story.append(Paragraph("Reporte de Solución Simplex", self.styles['PDFTitle']))

            problem = self.report_data.get('problema_definicion', {})
            solution = self.report_data.get('solucion_encontrada', {})
            tableaus = self.report_data.get('tablas_intermedias', [])

            self._build_problem_section(problem)
            self._build_solution_section(solution)
            self._build_tableaus_section(tableaus)

            self.doc.build(self.story)
            return self.output_filename

        except Exception as e:
            print(f"Error al generar el archivo PDF: {e}")
            raise 

    def _build_problem_section(self, problem: dict):
        """Añade la sección de Definición del Problema al PDF."""
        self.story.append(Paragraph("1. Definición del Problema", self.styles['PDFHeading1']))
        
        fo_data = problem.get('funcion_objetivo', {})
        constraints_data = problem.get('restricciones', [])

        self.story.append(Paragraph("Función Objetivo (F.O.)", self.styles['PDFHeading2']))
        
        fo_type = fo_data.get('type', 'N/A').capitalize()
        fo_coeffs = fo_data.get('coefficients', {})
        fo_str = " + ".join(f"{v}*{k}" for k, v in fo_coeffs.items()).replace("+-", "- ")
        
        self.story.append(Paragraph(f"<b>Tipo:</b> {fo_type}", self.styles['Normal']))
        self.story.append(Paragraph(f"Z = {fo_str}", self.styles['PDFCode']))

        self.story.append(Paragraph("Restricciones", self.styles['PDFHeading2']))
        if not constraints_data:
            self.story.append(Paragraph("No se ingresaron restricciones.", self.styles['Normal']))
            return

        for i, const in enumerate(constraints_data):
            coeffs = const.get('coefficients', {})
            op = const.get('operator', '?')
            rhs = const.get('rhs', '?')
            const_str = " + ".join(f"{v}*{k}" for k, v in coeffs.items() if v != 0).replace("+-", "- ")
            full_str = f"<b>{i+1})</b> {const_str} {op} {rhs}"
            self.story.append(Paragraph(full_str, self.styles['PDFCode']))
        
        self.story.append(Spacer(1, 0.25 * inch))

    def _build_solution_section(self, solution: dict):
        """Añade la sección de Solución Encontrada al PDF."""
        self.story.append(Paragraph("2. Solución Encontrada", self.styles['PDFHeading1']))
        status = solution.get('status', 'Error')

        if status == "Solucion Factible":
            self.story.append(Paragraph("Estado: ¡Solución Factible! ✅", self.styles['PDFSuccess']))
            self.story.append(Spacer(1, 0.1 * inch))

            z_value = solution.get('valor_optimo_z', 0.0)
            self.story.append(Paragraph(f"<b>Valor Óptimo (Z) = {z_value:.4f}</b>", self.styles['PDFHeading2']))
            self.story.append(Spacer(1, 0.1 * inch))

            self.story.append(Paragraph("Valores de las Variables:", self.styles['PDFHeading2']))
            var_data = solution.get('valores_variables', {})
            if not var_data:
                self.story.append(Paragraph("No se encontraron valores.", self.styles['Normal']))
                return

            table_data = [["Variable", "Valor Óptimo"]] 
            for var, val in var_data.items():
                table_data.append([var, f"{val:.4f}"])

            t = Table(table_data, colWidths=[2 * inch, 3 * inch], hAlign='LEFT')
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#343a40")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ]))
            self.story.append(t)
        else:
            status = solution.get('status', 'Error')
            message = solution.get('mensaje_solver', 'No hay detalles.')
            self.story.append(Paragraph(f"<b>Estado: {status} ❌</b>", self.styles['PDFFail']))
            self.story.append(Spacer(1, 0.1 * inch))
            self.story.append(Paragraph(f"<b>Mensaje del Solver:</b> {message}", self.styles['PDFCode']))
        
        self.story.append(PageBreak()) # Salto de página antes de las tablas

    def _build_tableaus_section(self, tableaus: list):
        """Añade la sección de Tablas Intermedias."""
        self.story.append(Paragraph("3. Tablas Intermedias (Iteraciones)", self.styles['PDFHeading1']))
        
        if not tableaus:
            self.story.append(Paragraph("No se generaron tablas intermedias (el solver de visualización no pudo procesar el problema).", self.styles['Normal']))
            return

        for tableau_data in tableaus:
            title = tableau_data.get("title", "Tabla")
            table_list = tableau_data.get("table", [])
            
            if not table_list:
                continue

            self.story.append(Paragraph(title, self.styles['PDFHeading2']))
            
            t = Table(table_list, hAlign='LEFT', repeatRows=1)
            
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#343a40")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('FONTNAME', (1, 1), (-1, -1), 'Courier'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ])
            
            pivot = tableau_data.get("pivot")
            if pivot:
                row, col = pivot
                table_style.add('BACKGROUND', (col + 1, row + 1), (col + 1, row + 1), colors.HexColor("#fff0f0"))
                table_style.add('TEXTCOLOR', (col + 1, row + 1), (col + 1, row + 1), colors.red)
                table_style.add('FONTNAME', (col + 1, row + 1), (col + 1, row + 1), 'Courier-Bold')

            t.setStyle(table_style)
            
            self.story.append(t)
            self.story.append(Spacer(1, 0.25 * inch))