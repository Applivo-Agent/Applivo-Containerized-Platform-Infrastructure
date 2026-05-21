import os
from datetime import datetime

import structlog
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

logger = structlog.get_logger()


class InvoiceService:
    """Service for generating premium invoice PDFs."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._register_fonts()
        self._setup_custom_styles()

    def _register_fonts(self):
        """Register Geist if present, fallback to Helvetica."""
        try:
            font_path = os.path.join(
                os.getcwd(), "frontend/node_modules/next/dist/compiled/@vercel/og/Geist-Regular.ttf"
            )
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont("Geist", font_path))
                self.main_font = "Geist"
                logger.info("Registered Geist font for invoices")
            else:
                self.main_font = "Helvetica"
                logger.warning("Geist font not found, using Helvetica")
        except Exception as exc:
            logger.warning("Font registration failed, using Helvetica", error=str(exc))
            self.main_font = "Helvetica"

    def _setup_custom_styles(self):
        self.blue = colors.HexColor("#3558e6")
        self.blue_dark = colors.HexColor("#1f3fbf")
        self.blue_soft = colors.HexColor("#eef2ff")
        self.card_border = colors.HexColor("#d8e1ff")
        self.text_dark = colors.HexColor("#1f2a44")
        self.text_muted = colors.HexColor("#667085")
        self.text_light = colors.HexColor("#dbe6ff")
        self.success = colors.HexColor("#10b981")

        self.brand_name_style = ParagraphStyle(
            "BrandName",
            parent=self.styles["Normal"],
            fontName=self.main_font,
            fontSize=20,
            textColor=colors.white,
            leading=22,
            alignment=TA_LEFT,
        )

        self.brand_subtitle_style = ParagraphStyle(
            "BrandSubtitle",
            parent=self.styles["Normal"],
            fontName=self.main_font,
            fontSize=8,
            textColor=self.text_light,
            leading=10,
            alignment=TA_LEFT,
        )

        self.invoice_title_style = ParagraphStyle(
            "InvoiceTitle",
            parent=self.styles["Normal"],
            fontName=self.main_font,
            fontSize=30,
            textColor=self.blue_dark,
            leading=32,
            alignment=TA_CENTER,
        )

        self.detail_label_style = ParagraphStyle(
            "DetailLabel",
            parent=self.styles["Normal"],
            fontName=self.main_font,
            fontSize=8,
            textColor=self.text_muted,
            leading=10,
            alignment=TA_LEFT,
        )

        self.detail_value_style = ParagraphStyle(
            "DetailValue",
            parent=self.styles["Normal"],
            fontName=self.main_font,
            fontSize=9,
            textColor=self.text_dark,
            leading=13,
            alignment=TA_LEFT,
        )

        self.bill_name_style = ParagraphStyle(
            "BillName",
            parent=self.styles["Normal"],
            fontName=self.main_font,
            fontSize=14,
            textColor=self.text_dark,
            leading=16,
            alignment=TA_LEFT,
        )

        self.table_header_style = ParagraphStyle(
            "TableHeader",
            parent=self.styles["Normal"],
            fontName=self.main_font,
            fontSize=10,
            textColor=self.blue_dark,
            leading=12,
            alignment=TA_LEFT,
        )

        self.total_label_style = ParagraphStyle(
            "TotalLabel",
            parent=self.styles["Normal"],
            fontName=self.main_font,
            fontSize=10,
            textColor=self.text_muted,
            leading=12,
            alignment=TA_RIGHT,
        )

        self.total_value_style = ParagraphStyle(
            "TotalValue",
            parent=self.styles["Normal"],
            fontName=self.main_font,
            fontSize=11,
            textColor=self.text_dark,
            leading=12,
            alignment=TA_RIGHT,
        )

        self.badge_style = ParagraphStyle(
            "Badge",
            parent=self.styles["Normal"],
            fontName=self.main_font,
            fontSize=10,
            textColor=colors.white,
            leading=12,
            alignment=TA_CENTER,
        )

        self.footer_style = ParagraphStyle(
            "Footer",
            parent=self.styles["Normal"],
            fontName=self.main_font,
            fontSize=8,
            textColor=self.text_muted,
            leading=11,
            alignment=TA_CENTER,
        )

    def _get_logo(self):
        logo_path = os.path.join(os.getcwd(), "frontend/public/logo.png")
        if os.path.exists(logo_path):
            try:
                return Image(logo_path, width=0.72 * inch, height=0.72 * inch)
            except Exception as exc:
                logger.warning("Could not load logo", error=str(exc))
        return None

    async def generate_invoice(
        self,
        payment_id: str,
        order_id: str,
        razorpay_payment_id: str,
        full_name: str,
        email: str,
        user_id: str,
        amount: float,
        plan_name: str,
        date: str = None,
    ) -> str:
        if not date:
            date = datetime.now().strftime("%B %d, %Y")

        # Razorpay stores amounts in paise (1 INR = 100 paise). Convert to rupees for display.
        amount_rupees = amount / 100

        invoices_dir = os.path.join(os.getcwd(), "storage", "invoices")
        os.makedirs(invoices_dir, exist_ok=True)
        output_path = os.path.join(invoices_dir, f"invoice_{payment_id}.pdf")

        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=32,
                leftMargin=32,
                topMargin=28,
                bottomMargin=28,
            )
            elements = []

            # Header block
            logo = self._get_logo()
            brand_cell = Paragraph("<b>Applivo</b>", self.brand_name_style)
            if logo:
                brand_table = Table([[logo, brand_cell]], colWidths=[0.8 * inch, 3.4 * inch])
            else:
                brand_table = Table([[brand_cell]], colWidths=[4.2 * inch])
            brand_table.setStyle(TableStyle([
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))

            left_header = Table([
                [brand_table],
                [Paragraph("Applivo AI Job Automation", self.brand_subtitle_style)],
                [Paragraph("Tamil Nadu, India", self.brand_subtitle_style)],
                [Paragraph("applivoagent@gmail.com", self.brand_subtitle_style)],
            ], colWidths=[4.2 * inch])
            left_header.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), self.blue),
                ("LEFTPADDING", (0, 0), (-1, -1), 16),
                ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ]))

            right_header = Table([
                [Paragraph(f"Invoice #: <b>{payment_id}</b>", self.detail_value_style)],
                [Paragraph(f"Date: <b>{date}</b>", self.detail_value_style)],
                [Paragraph(f"Order ID: <b>{order_id}</b>", self.detail_value_style)],
                [Paragraph(f"Payment ID: <b>{razorpay_payment_id or '-'} </b>", self.detail_value_style)],
            ], colWidths=[2.9 * inch])
            right_header.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.8, self.card_border),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]))

            hero = Table([[left_header, right_header]], colWidths=[4.25 * inch, 2.95 * inch])
            hero.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), self.blue),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
            elements.append(hero)
            elements.append(Spacer(1, 0.22 * inch))

            elements.append(Paragraph("INVOICE", self.invoice_title_style))
            elements.append(Spacer(1, 0.18 * inch))

            bill_to = Table([
                [Paragraph("BILL TO", self.detail_label_style)],
                [Paragraph(f"<b>{full_name}</b>", self.bill_name_style)],
                [Paragraph(email, self.detail_value_style)],
                [Paragraph(f"User ID: {user_id}", self.detail_value_style)],
            ], colWidths=[3.9 * inch])
            bill_to.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.8, self.card_border),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]))

            payment_info = Table([
                [Paragraph("PAYMENT DETAILS", self.detail_label_style)],
                [Paragraph("<b>Method:</b> Razorpay Secure", self.detail_value_style)],
                [Paragraph("<b>Currency:</b> INR (Rs)", self.detail_value_style)],
            ], colWidths=[2.35 * inch])
            payment_info.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.8, self.card_border),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ]))

            paid_badge = Table([[Paragraph("<b>PAID</b>", self.badge_style)]], colWidths=[0.95 * inch])
            paid_badge.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), self.success),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))

            billing_row = Table([[bill_to, payment_info, paid_badge]], colWidths=[4.0 * inch, 2.25 * inch, 0.95 * inch])
            billing_row.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
            elements.append(billing_row)
            elements.append(Spacer(1, 0.2 * inch))

            items = Table([
                [
                    Paragraph("Description", self.table_header_style),
                    Paragraph("Qty", self.table_header_style),
                    Paragraph("Amount", self.table_header_style),
                ],
                [
                    Paragraph(
                        f"<b>Applivo {plan_name.upper()} Plan</b><br/><font color='#6b7280' size='8'>Premium AI job search and auto-application services</font>",
                        self.detail_value_style,
                    ),
                    Paragraph("1", self.detail_value_style),
                    Paragraph(f"Rs {amount_rupees:,.2f}", self.detail_value_style),
                ],
            ], colWidths=[4.15 * inch, 0.75 * inch, 2.1 * inch])
            items.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), self.blue_soft),
                ("ALIGN", (1, 0), (2, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOX", (0, 0), (-1, -1), 0.8, self.card_border),
                ("LINEBELOW", (0, 0), (-1, -1), 0.6, self.card_border),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ]))
            elements.append(items)
            elements.append(Spacer(1, 0.12 * inch))

            totals = Table([
                [Paragraph("Subtotal", self.total_label_style), Paragraph(f"Rs {amount_rupees:,.2f}", self.total_value_style)],
                [Paragraph("GST (0%)", self.total_label_style), Paragraph("Rs 0.00", self.total_value_style)],
                [
                    Paragraph("Total Amount Paid", self.total_label_style),
                    Paragraph(f"<font color='#1f3fbf'><b>Rs {amount_rupees:,.2f}</b></font>", self.total_value_style),
                ],
            ], colWidths=[1.9 * inch, 1.4 * inch])
            totals.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("LINEABOVE", (0, 2), (-1, 2), 1.3, self.blue),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))

            totals_wrap = Table([[Spacer(1, 0.1 * inch), totals]], colWidths=[4.25 * inch, 2.95 * inch])
            totals_wrap.setStyle(TableStyle([
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
            elements.append(totals_wrap)

            elements.append(Spacer(1, 0.5 * inch))
            footer = Table([[
                Paragraph(
                    "<b>Applivo AI</b> - Accelerating Career Growth with Intelligence in Tamil Nadu.<br/>"
                    "Registration Number: APPL_AI-56291 | applivoagent@gmail.com<br/>"
                    "This is a computer-generated document. No signature required.",
                    self.footer_style,
                )
            ]], colWidths=[7.2 * inch])
            footer.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), self.blue_soft),
                ("BOX", (0, 0), (-1, -1), 0.6, self.card_border),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]))
            elements.append(footer)

            doc.build(elements)
            logger.info("Invoice PDF generated", path=output_path, payment_id=payment_id)
            return output_path

        except Exception as exc:
            logger.error("Failed to generate invoice PDF", error=str(exc), payment_id=payment_id)
            raise RuntimeError(f"Invoice generation failed: {str(exc)}")


invoice_service = InvoiceService()
