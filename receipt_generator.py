from fpdf import FPDF
from datetime import datetime
import os

class ReceiptGenerator:
    def __init__(self):
        pass

    def generate_receipt(self, tenant, property_obj):
        pdf = FPDF()
        pdf.add_page()
        
        # Colors (Dark Blue Theme for PDF header)
        pdf.set_fill_color(31, 41, 55) # #1f2937
        pdf.rect(0, 0, 210, 40, 'F')
        
        # Header Text
        pdf.set_font("Arial", "B", 24)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 20, "RECIBO DE ALQUILER", align="C", ln=True)
        pdf.ln(10)
        
        # Reset Text Color
        pdf.set_text_color(0, 0, 0)
        
        # Date & ID
        current_date = datetime.now().strftime("%d/%m/%Y")
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Fecha: {current_date}", ln=True, align="R")
        pdf.cell(0, 10, f"Referencia: {property_obj.id[:8].upper()}", ln=True, align="R")
        pdf.ln(20)
        
        # Property Info
        pdf.set_font("Arial", "B", 14)
        pdf.set_fill_color(229, 231, 235) # Light gray
        pdf.cell(0, 10, "  Detalles de la Propiedad", ln=True, fill=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Dirección: {property_obj.address}", ln=True)
        pdf.cell(0, 10, f"Ciudad: {property_obj.city}, {property_obj.zip_code}", ln=True)
        pdf.ln(10)
        
        # Tenant Info
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "  Inquilino", ln=True, fill=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Nombre: {tenant.name}", ln=True)
        pdf.ln(10)
        
        # Concept & Amount
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "  Concepto", ln=True, fill=True)
        pdf.set_font("Arial", "", 12)
        
        # Table Header
        pdf.set_font("Arial", "B", 12)
        pdf.cell(140, 10, "Descripción", border=1)
        pdf.cell(50, 10, "Importe", border=1, align="R")
        pdf.ln()
        
        # Table Row
        pdf.set_font("Arial", "", 12)
        month = datetime.now().strftime("%B %Y")
        pdf.cell(140, 10, f"Alquiler Mensual - {month}", border=1)
        pdf.cell(50, 10, f"{tenant.rent:.2f} EUR", border=1, align="R")
        pdf.ln()
        
        # Total
        pdf.set_font("Arial", "B", 14)
        pdf.cell(140, 10, "TOTAL A PAGAR", border=0, align="R")
        pdf.cell(50, 10, f"{tenant.rent:.2f} EUR", border=1, align="R", fill=True)
        
        # Footer
        pdf.set_y(-30)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 10, "Gracias por su pago.", align="C")

        # Save
        filename = f"Recibo_{tenant.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m')}.pdf"
        # Save to Desktop or Downloads? User didn't specify, saving to current dir for now
        # Actually user has blocked access to non-workspace. Let's save in project root.
        pdf.output(filename)
        return os.path.abspath(filename)
