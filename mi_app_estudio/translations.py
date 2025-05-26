"""
Module for managing translations in the SMART_STUDENT app.
Contains dictionaries for different languages.
"""

# English translations
en_translations = {
    # General UI
    "sign_out": "Sign Out",
    "switch_language": "EN",
    "header_title": "SMART STUDENT",
    "app_tagline": "Learn, Create, and Shine",
    "login_title": "Login",
    "login_subtitle": "Access your learnings",
    "username": "Username",
    "password": "Password",
    "login_button": "Login",
    "forgot_password": "Forgot your password?",
    "logout_button": "Sign Out",
    
    # Profile tab
    "profile_heading": "Personal Profile",
    "profile_subtitle": "Here you can view your progress and manage your account.",
    "confirm_action": "Confirm action",
    "cancel_button": "Cancel",
    "confirm_button": "Confirm",
    "name_label": "Name:",
    "level_label": "Level:",
    "active_course_label": "Active Course:",
    "subjects_label": "Subjects:",
    "evaluations_completed_label": "Evaluations Completed:",
    "change_password_button": "Change Password",
    "download_history_button": "Download History",
    "delete_history_button": "Delete History",
    "learning_statistics": "Learning Statistics",
    "progress_by_subject": "Progress by Subject",
    "mathematics": "Mathematics",
    "science": "Science",
    "history": "History",
    "language": "Language",
    "evaluations_completed": "Evaluations Completed",
    "average_score": "Average Score",
    "maps_created": "Maps Created",
    "summaries_generated": "Summaries Generated",
    "evaluation_history": "Evaluation History",
    "evaluation_history_subtitle": "Check your progress! Each evaluation makes you stronger 💪",
    "date_column": "📅 Date",
    "book_column": "📖 Book",
    "topic_column": "📝 Topic",
    "score_column": "📝 Score",
    "points_column": "🏅 Pts",
    "review_button": "Review",
    "previous_button_page": "Previous",
    "next_button_page": "Next",
    "page_text": "Page",
    
    # Summary tab
    "intelligent_summaries_title": "Generate Intelligent Summaries",
    "intelligent_summaries_subtitle": "Simplify complex topics with AI-generated summaries to facilitate your understanding and study.",
    "specific_topic_placeholder": "Specific topic to summarize...",
    "include_key_points_switch": "Include key points",
    "generate_summary_button": "Generate Summary",
    "generating_summary_text": "Generating summary...",
    "summary_heading": "SUMMARY", 
    "key_points_heading": "Key Points",
    "create_map_button": "Create Map",
    "create_questionnaire_button": "Create Questionnaire",
    "create_evaluation_button": "Create Evaluation",
    
    # Questionnaire tab
    "questionnaire_challenge_heading": "Challenge Your Knowledge with Questionnaires!",
    "questionnaire_subtitle": "Generate custom tests to evaluate your comprehension and reinforce learning.",
    "select_course_questionnaire": "Select a Course...",
    "select_book_questionnaire": "Select a Book...",
    "questionnaire_topic_placeholder": "Write the topic for the questionnaire",
    "generating_questionnaire": "Generating questionnaire...",
    "generate_questionnaire_button": "Generate Questionnaire",
    "questionnaire_heading": "QUESTIONNAIRE",
    "question_number": "Question",
    "answer_label": "Answer:",
    "download_pdf_button": "Download PDF",
    
    # Evaluation tab
    "evaluation_heading": "Knowledge Assessment",
    "evaluation_subtitle": "Test your understanding of the topic with automatically generated questions.",
    "select_course_evaluation": "Select a Course...",
    "select_book_evaluation": "Select a Book...",
    "evaluation_topic_placeholder": "Specific topic to evaluate...",
    "generating_evaluation": "Generating evaluation...",
    "generate_evaluation_button": "Create Assessment",
    "question_text": "Question",
    "of_text": "of",
    "previous_button": "Previous",
    "next_button": "Next",
    "finish_evaluation_button": "Finish Evaluation",
    "finish_review_button": "Finish Review",
    "evaluation_completed": "Evaluation Completed!",
    "completed_text": "completed",
    "correct_answers_text": "You got",
    "of_questions_text": "of",
    "questions_text": "questions",
    "motivation_text_1": "Knowledge is built step by step.",
    "motivation_text_2": "Keep going!",
    "new_evaluation_button": "New Evaluation",
    "review_button": "Review",
    
    # Books tab
    "digital_library": "Digital Library",
    "digital_library_desc": "Access your collection of digital books to study and review academic content.",
    "select_course_placeholder": "Select a Course...",
    "select_book_placeholder": "Select a Book...",
    "download_pdf_button": "Download PDF",
    
    # Welcome section
    "welcome": "Welcome to SMART STUDENT",
    "welcome_subtitle": "Your AI-powered intelligent study assistant. Explore the tools to improve your learning.",
    
    # Tabs
    "tab_inicio": "Home",
    "tab_libros": "Books",
    "tab_resumen": "Summary",
    "tab_mapa": "Mind Map",
    "tab_cuestionario": "Questionnaire",
    "tab_evaluacion": "Evaluation",
    "tab_perfil": "Profile",
    "tab_ayuda": "Help",
    
    # Navigation
    "dashboard": "Home",
    "summaries": "Summaries",
    "mindmaps": "Mind Maps",
    "evaluations": "Evaluations",
    "statistics": "Statistics",
    "settings": "Settings",
    
    # Course selection
    "course_selection": "Course Selection",
    "select_course": "Select Course",
    "select_book": "Select Book",
    "select_topic": "Select Topic",
    
    # Feature sections
    "digital_books": "Digital Books",
    "digital_books_desc": "Access your digital books and study content",
    "view_books": "View Books",
    
    "intelligent_summaries": "Intelligent Summaries",
    "intelligent_summaries_desc": "Generate summaries and key points to study efficiently",
    "create_summary": "Create Summary",
    
    "concept_maps": "Concept Maps",
    "concept_maps_desc": "Visualize connections between concepts for better understanding",
    "create_map": "Create Map",
    
    "questionnaires": "Questionnaires",
    "questionnaires_desc": "Generate personalized study questionnaires with questions and answers",
    "create_questionnaire": "Create Questionnaire",
    
    "assessments": "Assessments",
    "assessments_desc": "Test your knowledge with automatically generated questions",
    "create_assessment": "Create Assessment",
    
    "popular_resources": "Popular Resources",
    
    # Summaries
    "generate_summary": "Generate Summary",
    "include_key_points": "Include Key Points",
    "summary_title": "Summary",
    "key_points": "Key Points",
    "generating_summary": "Generating summary, please wait...",
    "download_pdf": "Download as PDF",
    
    # Mind Maps
    "generate_mindmap": "Generate Mind Map",
    "generating_mindmap": "Generating mind map, please wait...",
    "map_viewer": "Map Viewer",
    "create_mind_maps_title": "Create Mind Maps",
    "mind_maps_subtitle": "Visualize relationships between concepts and strengthen your understanding with personalized concept maps.",
    "select_course_placeholder": "Select a Course...",
    "select_book_placeholder": "Select a Book...",
    "topic_placeholder": "Central topic for the map...",
    "horizontal_orientation": "Horizontal Orientation",
    "generating_map_text": "Generating map...",
    "generate_map_button": "Generate Map",
    "mind_map_heading": "MIND MAP",
    
    # Evaluations
    "start_evaluation": "Start Evaluation",
    "question": "Question",
    "of": "of",
    "true": "True",
    "false": "False",
    "next_question": "Next Question",
    "finish_evaluation": "Finish Evaluation",
    "correct_answer": "Correct Answer",
    "explanation": "Explanation",
    "correct_message": "Correct! Well done.",
    "incorrect_message": "Incorrect. Try again.",
    
    # Results
    "evaluation_results": "Evaluation Results",
    "score": "Score",
    "review_answers": "Review Answers",
    "return_to_dashboard": "Return to Home",
    
    # Statistics
    "user_statistics": "User Statistics",
    "date": "Date",
    "points": "Points",
    
    # Errors
    "login_error": "Invalid username or password",
    "loading_error": "Error loading data",
    "generation_error": "Error generating content",
    
    # Help tab
    "help_center": "Help Center",
    "help_subtitle": "Here you'll find answers to frequently asked questions as a Student.",
    "frequent_questions": "Frequently Asked Questions",
    "not_found_help": "Didn't find what you were looking for?",
    "contact_us": "Contact Us"
}

# Spanish translations
es_translations = {
    # General UI
    "sign_out": "Cerrar Sesión",
    "switch_language": "ES",
    "header_title": "SMART STUDENT",
    "app_tagline": "Aprende, Crea y Destaca",
    "login_title": "Iniciar Sesión",
    "login_subtitle": "Accede a tus aprendizajes",
    "username": "Usuario",
    "password": "Contraseña",
    "login_button": "Iniciar Sesión",
    "forgot_password": "¿Olvidaste tu contraseña?",
    "logout_button": "Cerrar Sesión",
    
    # Profile tab
    "profile_heading": "Perfil Personal",
    "profile_subtitle": "Aquí puedes ver tu progreso y gestionar tu cuenta.",
    "confirm_action": "Confirmar acción",
    "cancel_button": "Cancelar",
    "confirm_button": "Confirmar",
    "name_label": "Nombre:",
    "level_label": "Nivel:",
    "active_course_label": "Curso Activo:",
    "subjects_label": "Asignaturas:",
    "evaluations_completed_label": "Evaluaciones Completadas:",
    "change_password_button": "Cambiar Contraseña",
    "download_history_button": "Descargar Historial",
    "delete_history_button": "Borrar Historial",
    "learning_statistics": "Estadísticas de Aprendizaje",
    "progress_by_subject": "Progreso por Materia",
    "mathematics": "Matemáticas",
    "science": "Ciencias",
    "history": "Historia",
    "language": "Lenguaje",
    "evaluations_completed": "Evaluaciones Completadas",
    "average_score": "Promedio Puntuación",
    "maps_created": "Mapas Creados",
    "summaries_generated": "Resúmenes Generados",
    "evaluation_history": "Historial de Evaluaciones",
    "evaluation_history_subtitle": "¡Mira tu progreso! Cada evaluación te hace más fuerte 💪",
    "date_column": "📅 Fecha",
    "book_column": "📖 Libro",
    "topic_column": "📝 Tema",
    "score_column": "📝 Nota",
    "points_column": "🏅 Pts",
    "review_button": "Repasar",
    "previous_button_page": "Anterior",
    "next_button_page": "Siguiente",
    "page_text": "Página",
    
    # Summary tab
    "intelligent_summaries_title": "Genera Resúmenes Inteligentes",
    "intelligent_summaries_subtitle": "Simplifica temas complejos con resúmenes generados por IA para facilitar tu comprensión y estudio.",
    "specific_topic_placeholder": "Tema específico a resumir...",
    "include_key_points_switch": "Incluir puntos clave",
    "generate_summary_button": "Generar Resumen",
    "generating_summary_text": "Generando resumen...",
    "summary_heading": "RESUMEN",
    "key_points_heading": "Puntos Clave",
    "create_map_button": "Crear Mapa",
    "create_questionnaire_button": "Crear Cuestionario",
    "create_evaluation_button": "Crear Evaluación",
    
    # Questionnaire tab
    "questionnaire_challenge_heading": "¡Desafía tu Conocimiento con Cuestionarios!",
    "questionnaire_subtitle": "Genera pruebas personalizadas para evaluar tu comprensión y reforzar el aprendizaje.",
    "select_course_questionnaire": "Selecciona un Curso...",
    "select_book_questionnaire": "Selecciona un Libro...",
    "questionnaire_topic_placeholder": "Escribe el tema para el cuestionario",
    "generating_questionnaire": "Generando cuestionario...",
    "generate_questionnaire_button": "Generar Cuestionario",
    "questionnaire_heading": "CUESTIONARIO",
    "question_number": "Pregunta",
    "answer_label": "Respuesta:",
    "download_pdf_button": "Descargar PDF",
    
    # Evaluation tab
    "evaluation_heading": "Evaluación de Conocimientos",
    "evaluation_subtitle": "Pon a prueba tu comprensión del tema con preguntas generadas automáticamente.",
    "select_course_evaluation": "Selecciona un Curso...",
    "select_book_evaluation": "Selecciona un Libro...",
    "evaluation_topic_placeholder": "Tema específico a evaluar...",
    "generating_evaluation": "Generando evaluación...",
    "generate_evaluation_button": "Crear Evaluación",
    "question_text": "Pregunta",
    "of_text": "de",
    "previous_button": "Anterior",
    "next_button": "Siguiente",
    "finish_evaluation_button": "Terminar Evaluación",
    "finish_review_button": "Finalizar Revisión",
    "evaluation_completed": "¡Evaluación Completada!",
    "completed_text": "completado",
    "correct_answers_text": "Has acertado",
    "of_questions_text": "de",
    "questions_text": "preguntas",
    "motivation_text_1": "El conocimiento se construye paso a paso.",
    "motivation_text_2": "¡Sigue adelante!",
    "new_evaluation_button": "Nueva Evaluación",
    "review_button": "Repasar",
    "evaluation_completed": "¡Evaluación Completada!",
    "completed_text": "completado",
    "correct_answers_text": "Has acertado",
    "of_questions_text": "de",
    "questions_text": "preguntas",
    "motivation_text_1": "El conocimiento se construye paso a paso.",
    "motivation_text_2": "¡Sigue adelante!",
    "new_evaluation_button": "Nueva Evaluación",
    "review_button": "Repasar",
    
    # Books tab
    "digital_library": "Biblioteca Digital",
    "digital_library_desc": "Accede a tu colección de libros digitales para estudiar y repasar los contenidos académicos.",
    "select_course_placeholder": "Selecciona un Curso...",
    "select_book_placeholder": "Selecciona un Libro...",
    "download_pdf_button": "Descargar PDF",
    
    # Welcome section
    "welcome": "Bienvenido a SMART STUDENT",
    "welcome_subtitle": "Tu asistente de estudio inteligente potenciado por IA. Explora las herramientas para mejorar tu aprendizaje.",
    
    # Tabs
    "tab_inicio": "Inicio",
    "tab_libros": "Libros",
    "tab_resumen": "Resumen",
    "tab_mapa": "Mapa Mental",
    "tab_cuestionario": "Cuestionario",
    "tab_evaluacion": "Evaluación",
    "tab_perfil": "Perfil",
    "tab_ayuda": "Ayuda",
    
    # Navigation
    "dashboard": "Panel Principal",
    "summaries": "Resúmenes",
    "mindmaps": "Mapas Mentales",
    "evaluations": "Evaluaciones",
    "statistics": "Estadísticas",
    "settings": "Configuración",
    
    # Course selection
    "course_selection": "Selección de Curso",
    "select_course": "Seleccionar Curso",
    "select_book": "Seleccionar Libro",
    "select_topic": "Seleccionar Tema",
    
    # Feature sections
    "digital_books": "Libros Digitales",
    "digital_books_desc": "Accede a tus libros digitales y contenidos de estudio",
    "view_books": "Ver Libros",
    
    "intelligent_summaries": "Resúmenes Inteligentes",
    "intelligent_summaries_desc": "Genera resúmenes y puntos clave para estudiar de forma eficiente",
    "create_summary": "Crear Resumen",
    
    "concept_maps": "Mapas Conceptuales",
    "concept_maps_desc": "Visualiza conexiones entre conceptos para mejorar tu comprensión",
    "create_map": "Crear Mapa",
    
    "questionnaires": "Cuestionarios",
    "questionnaires_desc": "Genera cuestionarios de estudio personalizados con preguntas y respuestas",
    "create_questionnaire": "Crear Cuestionario",
    
    "assessments": "Evaluaciones",
    "assessments_desc": "Pon a prueba tu conocimiento con preguntas generadas automáticamente",
    "create_assessment": "Crear Evaluación",
    
    "popular_resources": "Recursos Populares",
    
    # Summaries
    "generate_summary": "Generar Resumen",
    "include_key_points": "Incluir Puntos Clave",
    "summary_title": "Resumen",
    "key_points": "Puntos Clave",
    "generating_summary": "Generando resumen, por favor espere...",
    "download_pdf": "Descargar como PDF",
    
    # Mind Maps
    "generate_mindmap": "Generar Mapa Mental",
    "generating_mindmap": "Generando mapa mental, por favor espere...",
    "map_viewer": "Visor de Mapas",
    "create_mind_maps_title": "Crea Mapas Conceptuales",
    "mind_maps_subtitle": "Visualiza relaciones entre conceptos y fortalece tu comprensión con mapas conceptuales personalizados.",
    "select_course_placeholder": "Selecciona un Curso...",
    "select_book_placeholder": "Selecciona un Libro...",
    "topic_placeholder": "Tema central del mapa...",
    "horizontal_orientation": "Orientación Horizontal",
    "generating_map_text": "Generando mapa...",
    "generate_map_button": "Generar Mapa",
    "mind_map_heading": "MAPA CONCEPTUAL",
    
    # Evaluations
    "start_evaluation": "Iniciar Evaluación",
    "question": "Pregunta",
    "of": "de",
    "true": "Verdadero",
    "false": "Falso",
    "next_question": "Siguiente Pregunta",
    "finish_evaluation": "Finalizar Evaluación",
    "correct_answer": "Respuesta Correcta",
    "explanation": "Explicación",
    "correct_message": "¡Correcto! Bien hecho.",
    "incorrect_message": "Incorrecto. Inténtalo de nuevo.",
    
    # Results
    "evaluation_results": "Resultados de la Evaluación",
    "score": "Puntuación",
    "review_answers": "Revisar Respuestas",
    "return_to_dashboard": "Volver al Panel Principal",
    
    # Statistics
    "user_statistics": "Estadísticas de Usuario",
    "date": "Fecha",
    "points": "Puntos",
    
    # Errors
    "login_error": "Usuario o contraseña inválidos",
    "loading_error": "Error cargando datos",
    "generation_error": "Error generando contenido",
    
    # Help tab
    "help_center": "Centro de Ayuda",
    "help_subtitle": "Aquí encontrarás respuestas a preguntas frecuentes que te harán como Student.",
    "frequent_questions": "Preguntas Frecuentes",
    "not_found_help": "¿No encontraste lo que buscabas?",
    "contact_us": "Contáctanos"
}

# Function to get translations dictionary based on language code
def get_translations(lang_code: str) -> dict:
    """Get the translations dictionary for the specified language code."""
    if lang_code == "en":
        return en_translations
    # Default to Spanish
    return es_translations