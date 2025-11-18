"""
Professional PDF Report Generator for EDRS
Generates well-formatted PDF reports for document analysis and project summaries
"""
import io
import os
from datetime import datetime, timezone
from django.conf import settings
from django.http import FileResponse, HttpResponse
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, blue, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib import colors

class EDRSPDFGenerator:
    """Professional PDF generator for EDRS reports using ReportLab"""
    
    def __init__(self):
        self.pagesize = A4
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom styles for the PDF report"""
        # Header styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=6,
            textColor=HexColor('#3b82f6'),
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=HexColor('#6b7280'),
            spaceAfter=20
        )
        
        self.report_title_style = ParagraphStyle(
            'ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceBefore=20,
            spaceAfter=10,
            textColor=HexColor('#111827'),
            fontName='Helvetica-Bold'
        )
        
        self.section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=12,
            textColor=HexColor('#374151'),
            fontName='Helvetica-Bold'
        )
        
        self.subsection_style = ParagraphStyle(
            'SubsectionTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8,
            textColor=HexColor('#4b5563'),
            fontName='Helvetica-Bold'
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            textColor=HexColor('#1f2937')
        )
        
        self.footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=HexColor('#6b7280'),
            alignment=TA_CENTER
        )
    
    def _create_header_footer(self, canvas, doc):
        """Create header and footer for each page"""
        canvas.saveState()
        
        # Footer
        footer_text = f"Generated on {datetime.now(timezone.utc).strftime('%B %d, %Y at %H:%M UTC')} | Page {canvas.getPageNumber()}"
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(HexColor('#6b7280'))
        canvas.drawString(doc.pagesize[0] / 2.0 - 100, 30, footer_text)
        
        # Header line
        canvas.setStrokeColor(HexColor('#e5e7eb'))
        canvas.setLineWidth(1)
        canvas.line(50, doc.pagesize[1] - 50, doc.pagesize[0] - 50, doc.pagesize[1] - 50)
        
        canvas.restoreState()
    
    def _create_info_table(self, data, cols=2):
        """Create a styled information table"""
        # Organize data into rows
        items = list(data.items())
        rows = []
        
        for i in range(0, len(items), cols):
            row = []
            for j in range(cols):
                if i + j < len(items):
                    label, value = items[i + j]
                    cell = [
                        Paragraph(f"<b>{label}</b>", self.body_style),
                        Paragraph(str(value), self.body_style)
                    ]
                    row.extend(cell)
                else:
                    row.extend(['', ''])
            rows.append(row)
        
        # Create table
        if rows:
            col_widths = [1.5*inch, 2*inch] * cols
            table = Table(rows, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f9fafb')),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            return table
        return None
    
    def _create_stats_section(self, stats):
        """Create statistics section with colored boxes"""
        stats_data = []
        stats_row = []
        
        for label, value in stats.items():
            stats_row.extend([
                Paragraph(f"<b>{value}</b>", self.body_style),
                Paragraph(label, self.body_style)
            ])
        
        stats_data.append(stats_row)
        
        if stats_data[0]:  # Check if we have data
            table = Table(stats_data, colWidths=[1*inch] * len(stats_row))
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, -1), white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, white),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            return table
        return None
    
    def generate_document_analysis_report(self, document, analysis=None, format_type='pdf'):
        """Generate a professional document analysis report"""
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.pagesize,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build the document content
        story = []
        
        # Header
        story.append(Paragraph("Rejlers Abu Dhabi", self.title_style))
        story.append(Paragraph("Engineering Design & Review System", self.subtitle_style))
        story.append(Paragraph("Document Analysis Report", self.report_title_style))
        story.append(Paragraph(document.title, self.subsection_style))
        story.append(Spacer(1, 20))
        
        # Document Information Section
        story.append(Paragraph("Document Information", self.section_title_style))
        
        doc_info = {
            "Document Title": document.title,
            "File Name": document.original_filename,
            "Document Type": document.get_document_type_display(),
            "File Size": f"{document.file_size / (1024*1024):.2f} MB" if document.file_size else "Unknown",
            "Upload Date": document.uploaded_at.strftime("%B %d, %Y %H:%M"),
            "Status": document.get_status_display()
        }
        
        info_table = self._create_info_table(doc_info)
        if info_table:
            story.append(info_table)
        story.append(Spacer(1, 20))
        
        # Project Information Section
        story.append(Paragraph("Project Information", self.section_title_style))
        
        project_info = {
            "Project Name": document.project.name,
            "Project Type": document.project.get_project_type_display(),
            "Engineering Standard": document.project.get_engineering_standard_display(),
            "Project Status": document.project.get_status_display()
        }
        
        project_table = self._create_info_table(project_info)
        if project_table:
            story.append(project_table)
        story.append(Spacer(1, 20))
        
        # Analysis Results (if available)
        if analysis:
            story.append(Paragraph("Analysis Results", self.section_title_style))
            
            # Statistics
            stats = {
                "Equipment Items": getattr(analysis, 'equipment_count', 0),
                "Issues Found": getattr(analysis, 'issues_count', 0),
                "Confidence Level": getattr(analysis, 'confidence_level', 'Medium').title(),
                "Duration": f"{getattr(analysis, 'duration', 0):.2f}s"
            }
            
            stats_table = self._create_stats_section(stats)
            if stats_table:
                story.append(stats_table)
            story.append(Spacer(1, 20))
            
            # Analysis Summary
            story.append(Paragraph("Executive Summary", self.subsection_style))
            summary_text = getattr(analysis, 'summary', None) or "Analysis completed successfully. Detailed results are available in the sections below."
            story.append(Paragraph(summary_text, self.body_style))
            story.append(Spacer(1, 15))
            
            # Equipment List (mock data for demonstration)
            if getattr(analysis, 'equipment_count', 0) > 0:
                story.append(Paragraph("Equipment Identified", self.subsection_style))
                equipment_data = [
                    ['Tag', 'Description', 'Type'],
                    ['P-101', 'Centrifugal Pump', 'Pump'],
                    ['V-201', 'Storage Vessel', 'Vessel'],
                    ['HX-301', 'Heat Exchanger', 'Heat Exchanger'],
                    ['T-401', 'Distillation Tower', 'Tower'],
                ]
                
                equipment_table = Table(equipment_data, colWidths=[1.5*inch, 3*inch, 1.5*inch])
                equipment_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f3f4f6')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#374151')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), white),
                    ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb')),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 12),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                story.append(equipment_table)
                story.append(Spacer(1, 15))
            
            # Recommendations
            if getattr(analysis, 'issues_count', 0) > 0:
                story.append(Paragraph("Recommendations", self.subsection_style))
                
                rec_data = [
                    ['Priority', 'Recommendation', 'Description'],
                    ['High', 'Design Review Required', f'Review equipment sizing and piping arrangements according to {document.project.get_engineering_standard_display()} standards.'],
                    ['Medium', 'Documentation Update', 'Update P&ID legend and equipment specifications to ensure compliance with project standards.'],
                ]
                
                rec_table = Table(rec_data, colWidths=[1*inch, 2*inch, 3*inch])
                rec_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#fffbeb')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#92400e')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), white),
                    ('GRID', (0, 0), (-1, -1), 1, HexColor('#f59e0b')),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('LEFTPADDING', (0, 0), (-1, -1), 12),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(rec_table)
        
        # Build PDF
        doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)
        
        # Get PDF data
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_project_summary_report(self, project, documents=None, analyses=None, format_type='pdf'):
        """Generate a professional project summary report"""
        
        # Calculate project statistics
        total_documents = documents.count() if documents else 0
        total_analyses = analyses.count() if analyses else 0
        completed_analyses = analyses.filter(status='completed').count() if analyses else 0
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.pagesize,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build the document content
        story = []
        
        # Header
        story.append(Paragraph("Rejlers Abu Dhabi", self.title_style))
        story.append(Paragraph("Engineering Design & Review System", self.subtitle_style))
        story.append(Paragraph("Project Summary Report", self.report_title_style))
        story.append(Paragraph(project.name, self.subsection_style))
        story.append(Spacer(1, 20))
        
        # Project Overview Section
        story.append(Paragraph("Project Overview", self.section_title_style))
        
        project_info = {
            "Project Name": project.name,
            "Project Type": project.get_project_type_display(),
            "Engineering Standard": project.get_engineering_standard_display(),
            "Status": project.get_status_display(),
            "Created Date": project.created_at.strftime("%B %d, %Y"),
            "Last Updated": project.updated_at.strftime("%B %d, %Y %H:%M")
        }
        
        project_table = self._create_info_table(project_info)
        if project_table:
            story.append(project_table)
        story.append(Spacer(1, 15))
        
        # Description
        if project.description:
            story.append(Paragraph("Description", self.subsection_style))
            story.append(Paragraph(project.description, self.body_style))
            story.append(Spacer(1, 20))
        
        # Statistics Section
        story.append(Paragraph("Project Statistics", self.section_title_style))
        
        stats = {
            "Total Documents": total_documents,
            "Completed Analyses": completed_analyses,
            "Pending Analyses": total_documents - completed_analyses,
            "Total Analyses": total_analyses
        }
        
        stats_table = self._create_stats_section(stats)
        if stats_table:
            story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Documents List
        if documents and total_documents > 0:
            story.append(Paragraph("Documents", self.section_title_style))
            
            doc_data = [['Document Title', 'Type', 'File Size', 'Upload Date', 'Status']]
            
            for document in documents:
                doc_data.append([
                    document.title,
                    document.get_document_type_display(),
                    f"{document.file_size / (1024*1024):.2f} MB" if document.file_size else "Unknown",
                    document.uploaded_at.strftime("%b %d, %Y"),
                    document.get_status_display()
                ])
            
            doc_table = Table(doc_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            doc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f3f4f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#374151')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), white),
                ('GRID', (0, 0), (-1, -1), 1, HexColor('#e5e7eb')),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(doc_table)
        
        # Build PDF
        doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)
        
        # Get PDF data
        buffer.seek(0)
        return buffer.getvalue()


def generate_document_pdf_report(document, analysis=None):
    """Convenience function to generate document analysis PDF report"""
    generator = EDRSPDFGenerator()
    return generator.generate_document_analysis_report(document, analysis, 'pdf')


def generate_project_pdf_report(project, documents=None, analyses=None):
    """Convenience function to generate project summary PDF report"""
    generator = EDRSPDFGenerator()
    return generator.generate_project_summary_report(project, documents, analyses, 'pdf')