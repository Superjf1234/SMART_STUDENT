def obtener_directorio_pdf(curso):
    """Obtiene el directorio para los PDFs de un curso."""
    curso_folder_name = "".join(
        c if c.isalnum() else "_" for c in curso.lower()
    ).strip("_")
    return os.path.join("assets", "pdfs", curso_folder_name)

# ...existing code...