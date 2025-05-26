#!/usr/bin/env python
"""
Script para probar la funcionalidad de descarga de PDF en una aplicación simplificada
"""
import reflex as rx
import os
import datetime
import sys
import traceback

# Importar funciones de utilidad
from mi_app_estudio.state import get_safe_var_value, get_safe_var_list

# Estado de prueba simplificado
class TestPDFState(rx.State):
    """Estado de prueba para verificar la descarga de PDF"""
    
    # Variables de estado
    pdf_url: str = ""
    pdf_filename: str = ""
    is_loading: bool = False
    error_message: str = ""
    success_message: str = ""
    
    # Preguntas de ejemplo para el cuestionario
    cuestionario_tema: str = "Sistema Nervioso Central"
    cuestionario_libro: str = "Biología"
    cuestionario_curso: str = "2º Medio"
    cuestionario_preguntas: list = [
        {
            "pregunta": "¿Cuál es la unidad básica funcional del sistema nervioso?",
            "correcta": "b",
            "explicacion": "La neurona es la célula especializada que transmite impulsos nerviosos."
        },
        {
            "pregunta": "¿Qué protege al encéfalo?",
            "correcta": "a",
            "explicacion": "El cráneo y las meninges protegen al encéfalo de golpes y lesiones."
        }
    ]
    
    def generate_pdf(self):
        """Genera un PDF de prueba"""
        self.is_loading = True
        self.error_message = ""
        self.success_message = ""
        yield
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"test_cuestionario_{timestamp}.pdf"
            pdf_path = os.path.join("assets", "pdfs", filename)
            
            # Asegurarse de que el directorio existe
            os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
            
            # Crear un PDF de prueba simple
            with open(pdf_path, 'wb') as f:
                f.write(b"%PDF-1.4\n%\xE2\xE3\xCF\xD3\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type/Pages/Kids[]/Count 0>>\nendobj\nxref\n0 3\n0000000000 65535 f \n0000000015 00000 n \n0000000060 00000 n \ntrailer\n<</Size 3/Root 1 0 R>>\nstartxref\n110\n%%EOF\n")
            
            # También copiarlo a .web/public para acceso desde el navegador
            try:
                public_path = os.path.join(".web", "public", "assets", "pdfs", filename)
                os.makedirs(os.path.dirname(public_path), exist_ok=True)
                
                import shutil
                shutil.copy2(pdf_path, public_path)
                print(f"PDF copiado a {public_path}")
            except Exception as e:
                print(f"Error copiando PDF: {e}")
            
            # Establecer la URL relativa
            self.pdf_url = f"/assets/pdfs/{filename}"
            self.pdf_filename = filename
            self.success_message = f"PDF generado correctamente: {filename}"
            print(f"PDF generado: {pdf_path}, URL: {self.pdf_url}")
            
        except Exception as e:
            print(f"Error generando PDF: {e}")
            traceback.print_exc()
            self.error_message = f"Error: {str(e)}"
        finally:
            self.is_loading = False
            yield
    
    async def download_pdf(self):
        """Descarga el PDF generado"""
        self.is_loading = True
        self.error_message = ""
        self.success_message = ""
        yield
        
        try:
            if not self.pdf_url:
                self.error_message = "No hay PDF para descargar. Genera primero un PDF."
                self.is_loading = False
                yield
                return
            
            # Limpiar URL
            clean_url = self.pdf_url.split('?')[0]
            pdf_path = clean_url.lstrip('/')
            
            # Verificar rutas alternativas
            found = False
            if os.path.exists(pdf_path) and os.path.isfile(pdf_path):
                found = True
            else:
                print(f"No se encontró PDF en: {pdf_path}")
                # Probar en assets/
                assets_path = os.path.join("assets", "pdfs", os.path.basename(pdf_path))
                if os.path.exists(assets_path) and os.path.isfile(assets_path):
                    pdf_path = assets_path
                    found = True
                else:
                    # Probar en .web/public
                    public_path = os.path.join(".web", "public", pdf_path)
                    if os.path.exists(public_path) and os.path.isfile(public_path):
                        pdf_path = public_path
                        found = True
            
            if found:
                try:
                    with open(pdf_path, 'rb') as f:
                        pdf_bytes = f.read()
                    if pdf_bytes and pdf_bytes.startswith(b"%PDF"):
                        print(f"Descargando PDF: {pdf_path}")
                        yield rx.download(data=pdf_bytes, filename=self.pdf_filename)
                        self.success_message = "PDF descargado correctamente"
                    else:
                        self.error_message = "El archivo no es un PDF válido"
                except Exception as e:
                    print(f"Error leyendo PDF: {e}")
                    traceback.print_exc()
                    self.error_message = f"Error leyendo PDF: {str(e)}"
            else:
                self.error_message = f"No se pudo encontrar el PDF en ninguna ubicación"
        except Exception as e:
            print(f"Error descargando PDF: {e}")
            traceback.print_exc()
            self.error_message = f"Error: {str(e)}"
        finally:
            self.is_loading = False
            yield

# Interfaz de usuario
def index():
    return rx.center(
        rx.vstack(
            rx.heading("Test de Descarga de PDF", size="lg"),
            rx.divider(),
            rx.box(
                rx.vstack(
                    rx.heading("Estado", size="md"),
                    rx.text(f"URL del PDF: ", TestPDFState.pdf_url),
                    rx.text(f"Nombre del PDF: ", TestPDFState.pdf_filename),
                    rx.cond(
                        TestPDFState.error_message != "",
                        rx.callout(
                            TestPDFState.error_message,
                            icon="alert_triangle",
                            color_scheme="red",
                            role="alert",
                            width="100%",
                        ),
                        rx.text(""),
                    ),
                    rx.cond(
                        TestPDFState.success_message != "",
                        rx.callout(
                            TestPDFState.success_message,
                            icon="check_circle",
                            color_scheme="green",
                            role="status",
                            width="100%",
                        ),
                        rx.text(""),
                    ),
                    spacing="3",
                    width="100%",
                ),
                padding="4",
                border_radius="md",
                border_width="1px",
                width="100%",
            ),
            rx.hstack(
                rx.button(
                    "Generar PDF",
                    on_click=TestPDFState.generate_pdf,
                    color_scheme="blue",
                    is_loading=TestPDFState.is_loading,
                ),
                rx.button(
                    "Descargar PDF",
                    on_click=TestPDFState.download_pdf,
                    color_scheme="green",
                    is_loading=TestPDFState.is_loading,
                    is_disabled=TestPDFState.pdf_url == "",
                ),
                width="100%",
                justify="space-between",
            ),
            width="800px",
            spacing="4",
            padding="6",
        ),
        height="100vh",
    )

# Configuración de la aplicación
app = rx.App()
app.add_page(index)

# Ejecutar si se llama directamente
if __name__ == "__main__":
    app.compile()
