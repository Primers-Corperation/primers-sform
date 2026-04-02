import os
import time
import tempfile
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

class SovereignReportGenerator:
    """
    Generates signed, exportable incident reports for government audit compliance.
    Every AI decision is traceable, timestamped, and formatted for official filing.
    """

    SOVEREIGN_RED = colors.HexColor('#cc2200')
    DARK = colors.HexColor('#0a0a0a')
    MID = colors.HexColor('#444444')
    LIGHT = colors.HexColor('#f5f5f5')

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._build_styles()

    def _build_styles(self):
        self.style_title = ParagraphStyle(
            'SovTitle', fontSize=18, fontName='Helvetica-Bold',
            textColor=self.SOVEREIGN_RED, spaceAfter=4, alignment=TA_LEFT
        )
        self.style_subtitle = ParagraphStyle(
            'SovSub', fontSize=9, fontName='Helvetica',
            textColor=self.MID, spaceAfter=2, alignment=TA_LEFT
        )
        self.style_section = ParagraphStyle(
            'SovSection', fontSize=11, fontName='Helvetica-Bold',
            textColor=self.DARK, spaceBefore=14, spaceAfter=6
        )
        self.style_body = ParagraphStyle(
            'SovBody', fontSize=9, fontName='Helvetica',
            textColor=self.DARK, spaceAfter=4, leading=14
        )
        self.style_mono = ParagraphStyle(
            'SovMono', fontSize=8, fontName='Courier',
            textColor=self.DARK, spaceAfter=3, leading=12
        )
        self.style_footer = ParagraphStyle(
            'SovFooter', fontSize=7, fontName='Helvetica',
            textColor=self.MID, alignment=TA_CENTER
        )

    def generate_incident_report(
        self,
        audit_log: List[Dict[str, Any]],
        triage_results: List[Dict[str, Any]],
        detr_results: List[Dict[str, Any]],
        operator: str = "GOV-DEF-01",
        incident_id: str = None
    ) -> str:
        """
        Generates a full incident PDF report.
        Returns the file path of the generated report in /tmp.
        """
        if not incident_id:
            incident_id = f"SIP-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        filename = os.path.join(tempfile.gettempdir(), f"SIP_Incident_{incident_id}.pdf")
        doc = SimpleDocTemplate(
            filename, pagesize=A4,
            leftMargin=20*mm, rightMargin=20*mm,
            topMargin=20*mm, bottomMargin=20*mm
        )

        story = []
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

        # Header
        story.append(Paragraph("SOVEREIGN INTELLIGENCE PLATFORM", self.style_title))
        story.append(Paragraph("PRIMERS S-FORM SOS — INCIDENT REPORT", self.style_subtitle))
        story.append(Paragraph(f"Classification: OFFICIAL SENSITIVE", self.style_subtitle))
        story.append(HRFlowable(width="100%", thickness=1.5, color=self.SOVEREIGN_RED, spaceAfter=10))

        # Metadata table
        meta = [
            ['Incident ID', incident_id, 'Generated', now],
            ['Operator', operator, 'Theater', 'Lagos, Nigeria (6.5244°N, 3.3792°E)'],
            ['Platform', 'SIP v2.2.0', 'Mode', 'SOVEREIGN — No external cloud dependencies'],
        ]
        meta_table = Table(meta, colWidths=[35*mm, 65*mm, 30*mm, 60*mm])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('TEXTCOLOR', (0,0), (-1,-1), self.DARK),
            ('BACKGROUND', (0,0), (-1,-1), self.LIGHT),
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [self.LIGHT, colors.white]),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 10))

        # Triage Results
        story.append(Paragraph("1. TRIAGE INTELLIGENCE OUTPUTS", self.style_section))
        if triage_results:
            triage_data = [['Priority', 'Category', 'Confidence', 'Engine']]
            for r in triage_results:
                triage_data.append([
                    r.get('priority', 'N/A'),
                    r.get('category', 'N/A'),
                    f"{float(r.get('confidence', 0)) * 100:.0f}%",
                    r.get('engine', 'BERT-Triage-v1')
                ])
            t = Table(triage_data, colWidths=[35*mm, 50*mm, 35*mm, 70*mm])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), self.DARK),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, self.LIGHT]),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(t)
        else:
            story.append(Paragraph("No triage events recorded in this session.", self.style_body))

        story.append(Spacer(1, 8))

        # DETR Results
        story.append(Paragraph("2. OPTICAL INTELLIGENCE — DETR VISION MATRIX", self.style_section))
        if detr_results:
            for scan in detr_results:
                story.append(Paragraph(
                    f"Threat Level: <b>{scan.get('threat_level','N/A')}</b> | "
                    f"Engine: {scan.get('engine','DETR')} | "
                    f"Objects: {', '.join(scan.get('detected_objects',[]))}",
                    self.style_body
                ))
        else:
            story.append(Paragraph("No optical scans recorded in this session.", self.style_body))

        story.append(Spacer(1, 8))

        # Audit Trail
        story.append(Paragraph("3. SOVEREIGN AUDIT TRAIL", self.style_section))
        story.append(Paragraph(
            "Full chronological record of all AI decisions and system events. "
            "Admissible for official government review and incident investigation.",
            self.style_body
        ))
        story.append(Spacer(1, 4))

        if audit_log:
            audit_data = [['Timestamp', 'Module', 'Severity', 'Event']]
            for entry in reversed(audit_log):
                audit_data.append([
                    entry.get('timestamp', ''),
                    entry.get('module', ''),
                    entry.get('severity', 'INFO'),
                    entry.get('event', '')
                ])
            a = Table(audit_data, colWidths=[25*mm, 22*mm, 18*mm, 125*mm])
            severity_colors = {'CRITICAL': colors.HexColor('#ffeeee'), 'WARNING': colors.HexColor('#fffbe6'), 'INFO': colors.white}
            row_styles = [
                ('BACKGROUND', (0,0), (-1,0), self.DARK),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTNAME', (0,1), (-1,-1), 'Courier'),
                ('FONTSIZE', (0,0), (-1,-1), 7),
                ('GRID', (0,0), (-1,-1), 0.3, colors.HexColor('#dddddd')),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('WORDWRAP', (3,1), (3,-1), True),
            ]
            for i, entry in enumerate(audit_log, 1):
                sev = entry.get('severity', 'INFO')
                if sev in severity_colors:
                    row_styles.append(('BACKGROUND', (0,i), (-1,i), severity_colors[sev]))
            a.setStyle(TableStyle(row_styles))
            story.append(a)
        else:
            story.append(Paragraph("No audit events recorded.", self.style_body))

        # Footer
        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", thickness=0.5, color=self.MID))
        story.append(Spacer(1, 4))
        story.append(Paragraph(
            f"SOVEREIGN INTELLIGENCE PLATFORM — AUTO-GENERATED INCIDENT REPORT | "
            f"{now} | Incident: {incident_id} | "
            f"This document is generated by a sovereign AI system with no external cloud dependencies.",
            self.style_footer
        ))

        doc.build(story)
        return filename
