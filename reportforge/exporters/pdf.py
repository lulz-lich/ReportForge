"""PDF export support."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from reportforge.core.scoring import severity_counts, severity_label, sorted_findings, status_label
from reportforge.schemas import Report, Severity


def export_pdf(report: Report) -> bytes:
    """Render a report as PDF bytes."""

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=report.title,
        author=report.prepared_by,
    )
    styles = _styles()
    story = [
        Paragraph(report.title, styles["Title"]),
        Paragraph(f"{report.client} | {report.assessment_type}", styles["Subtitle"]),
        Paragraph(f"Classification: {report.classification.value.title()} | Version {report.report_version}", styles["Muted"]),
        Spacer(1, 0.25 * inch),
        Paragraph("Executive Summary" if report.language.value == "en" else "Resumo Executivo", styles["Heading2"]),
        Paragraph(report.executive_summary, styles["Body"]),
        Spacer(1, 0.18 * inch),
        _severity_table(report),
        PageBreak(),
    ]

    heading = "Technical Findings" if report.language.value == "en" else "Achados Tecnicos"
    story.append(Paragraph(heading, styles["Heading2"]))
    for finding in sorted_findings(report.findings):
        story.extend(
            [
                Paragraph(f"{finding.id} - {finding.title}", styles["Heading3"]),
                Paragraph(
                    (
                        f"Severity: {severity_label(finding.severity, report.language.value)} | "
                        f"Likelihood: {severity_label(finding.likelihood, report.language.value)} | "
                        f"Status: {status_label(finding.status, report.language.value)}"
                    ),
                    styles["Muted"],
                ),
                Paragraph(f"<b>Affected Asset:</b> {finding.affected_asset}", styles["Body"]),
                Paragraph("<b>Description</b>", styles["SmallHeading"]),
                Paragraph(finding.description, styles["Body"]),
                Paragraph("<b>Impact</b>", styles["SmallHeading"]),
                Paragraph(finding.impact, styles["Body"]),
                Paragraph("<b>Recommendation</b>", styles["SmallHeading"]),
                Paragraph(finding.recommendation, styles["Body"]),
                Spacer(1, 0.15 * inch),
            ]
        )
    doc.build(story)
    return buffer.getvalue()


def _severity_table(report: Report) -> Table:
    counts = severity_counts(report)
    rows = [["Severity", "Count"]]
    rows.extend(
        [severity_label(severity, report.language.value), str(counts[severity])]
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
    )
    table = Table(rows, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d1c18")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#2ff58f")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#1f4a3c")),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#1c2d27")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "Title": ParagraphStyle("Title", parent=base["Title"], fontSize=22, leading=26, textColor=colors.HexColor("#0d3b2e")),
        "Subtitle": ParagraphStyle("Subtitle", parent=base["BodyText"], fontSize=11, leading=15, textColor=colors.HexColor("#376154")),
        "Muted": ParagraphStyle("Muted", parent=base["BodyText"], fontSize=9, leading=13, textColor=colors.HexColor("#53766a")),
        "Heading2": ParagraphStyle("Heading2", parent=base["Heading2"], textColor=colors.HexColor("#0d3b2e")),
        "Heading3": ParagraphStyle("Heading3", parent=base["Heading3"], textColor=colors.HexColor("#365c0a")),
        "SmallHeading": ParagraphStyle("SmallHeading", parent=base["BodyText"], fontName="Helvetica-Bold", spaceBefore=8),
        "Body": ParagraphStyle("Body", parent=base["BodyText"], fontSize=10, leading=14),
    }
