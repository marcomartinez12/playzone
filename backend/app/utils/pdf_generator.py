"""
Generador de Reportes PDF
Genera reportes profesionales con branding de PlayZone
"""
from datetime import datetime
from typing import List
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


class PDFGenerator:
    """Generador de PDFs profesionales para PlayZone"""

    # Colores del branding de PlayZone
    COLOR_PRIMARIO = colors.HexColor('#0066cc')
    COLOR_SECUNDARIO = colors.HexColor('#00304D')
    COLOR_TEXTO = colors.HexColor('#1a1a2e')
    COLOR_GRIS = colors.HexColor('#666666')

    @staticmethod
    def generar_reporte_ventas(ventas_data: List[dict]) -> BytesIO:
        """
        Genera un reporte profesional de ventas en formato PDF

        Args:
            ventas_data: Lista de ventas con sus datos completos

        Returns:
            BytesIO: Buffer con el PDF generado
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )

        # Contenedor de elementos del PDF
        elements = []
        styles = getSampleStyleSheet()

        # Estilo personalizado para el título
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=PDFGenerator.COLOR_SECUNDARIO,
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        # Estilo para subtítulo
        subtitulo_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=PDFGenerator.COLOR_PRIMARIO,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        # Estilo para fecha
        fecha_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=PDFGenerator.COLOR_GRIS,
            spaceAfter=20,
            alignment=TA_RIGHT,
            fontName='Helvetica'
        )

        # ENCABEZADO
        titulo = Paragraph("PLAYZONE", titulo_style)
        elements.append(titulo)

        subtitulo = Paragraph("REPORTE DE VENTAS", subtitulo_style)
        elements.append(subtitulo)

        # Fecha de generación
        fecha_actual = datetime.now().strftime('%d de %B de %Y - %H:%M:%S')
        meses_es = {
            'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
            'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
            'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
            'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
        }
        for en, es in meses_es.items():
            fecha_actual = fecha_actual.replace(en, es)

        fecha_gen = Paragraph(f"<b>Fecha de generación:</b> {fecha_actual}", fecha_style)
        elements.append(fecha_gen)

        elements.append(Spacer(1, 0.3*inch))

        # RESUMEN ESTADÍSTICO
        total_ventas = len(ventas_data)
        total_monto = sum(venta['total'] for venta in ventas_data)
        total_productos = sum(venta.get('total_productos', 0) for venta in ventas_data)

        # Tabla de resumen
        resumen_data = [
            ['RESUMEN GENERAL', '', ''],
            ['Total de Ventas:', str(total_ventas), 'ventas'],
            ['Monto Total:', f"${total_monto:,.2f}", 'COP'],
            ['Productos Vendidos:', str(total_productos), 'unidades']
        ]

        resumen_table = Table(resumen_data, colWidths=[3.5*inch, 1.5*inch, 1*inch])
        resumen_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), PDFGenerator.COLOR_PRIMARIO),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('SPAN', (0, 0), (-1, 0)),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),

            # Contenido
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 1), (0, -1), PDFGenerator.COLOR_TEXTO),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        elements.append(resumen_table)
        elements.append(Spacer(1, 0.4*inch))

        # TABLA DE VENTAS DETALLADAS
        # Encabezados
        tabla_data = [
            ['ID', 'Cliente', 'Productos', 'Total', 'Fecha', 'Usuario']
        ]

        # Datos de ventas
        for venta in ventas_data:
            fecha_venta = venta['fecha_venta']
            if isinstance(fecha_venta, str):
                try:
                    fecha_venta = datetime.fromisoformat(fecha_venta.replace('Z', '+00:00'))
                except:
                    pass

            if isinstance(fecha_venta, datetime):
                fecha_str = fecha_venta.strftime('%d/%m/%Y')
            else:
                fecha_str = str(fecha_venta)

            tabla_data.append([
                str(venta['id_venta']),
                venta['nombre_cliente'][:20] + '...' if len(venta['nombre_cliente']) > 20 else venta['nombre_cliente'],
                str(venta.get('total_productos', 0)),
                f"${venta['total']:,.2f}",
                fecha_str,
                venta['nombre_usuario'][:15] + '...' if len(venta['nombre_usuario']) > 15 else venta['nombre_usuario']
            ])

        # Crear tabla
        ventas_table = Table(
            tabla_data,
            colWidths=[0.5*inch, 1.8*inch, 0.8*inch, 1.2*inch, 1*inch, 1.2*inch]
        )

        ventas_table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), PDFGenerator.COLOR_SECUNDARIO),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),

            # Contenido
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), PDFGenerator.COLOR_TEXTO),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # ID centrado
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Productos centrado
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Total alineado derecha
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Fecha centrado
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),

            # Alternar colores de filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9ff')]),

            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, PDFGenerator.COLOR_SECUNDARIO),
        ]))

        elements.append(ventas_table)
        elements.append(Spacer(1, 0.5*inch))

        # PIE DE PÁGINA
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=PDFGenerator.COLOR_GRIS,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        )

        footer_text = Paragraph(
            "Este reporte ha sido generado automáticamente por el Sistema de Inventario PlayZone<br/>"
            "Para más información, contacte al administrador del sistema",
            footer_style
        )
        elements.append(footer_text)

        # Construir PDF
        doc.build(elements)

        # Mover el puntero al inicio del buffer
        buffer.seek(0)
        return buffer
