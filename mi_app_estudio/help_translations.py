"""
Module for help questions and answers translations in the SMART_STUDENT app.
Contains dictionaries for different languages.
"""

# English translations
en_help_questions_answers = [
    {
        "pregunta": "How to register in your Student account?", 
        "respuesta": "To register, click on the 'Create account' button on the login page. Complete the form with your personal and academic information. You will receive a confirmation email to activate your account. Once activated, you can log in with your username and password."
    },
    {
        "pregunta": "To start using Student:", 
        "respuesta": "After logging in, explore the different tabs of the application. Start by selecting a course and a book in the 'Books' tab. Then, use the features like summaries, concept maps, or evaluations to enhance your learning. Remember to personalize your profile for a better experience."
    },
    {
        "pregunta": "How to choose a course?", 
        "respuesta": "Navigate to the 'Books' tab or any feature that requires course selection. Use the dropdown menu to see the available courses according to your academic level. Select the course you need to study. Once selected, you will be able to access the books and materials associated with that specific course."
    },
    {
        "pregunta": "Configure schedules, grades, etc:", 
        "respuesta": "In the 'Profile' tab, you'll find options to set up your personalized study schedule. You can set reminders, schedule study sessions, and track your grades. The analysis section will allow you to visualize your academic progress and areas for improvement. Customize these options according to your specific needs."
    },
    {
        "pregunta": "How to explore materials and resources?", 
        "respuesta": "In the 'Books' tab, you'll find all materials organized by course and subject. You can download PDFs, create summaries, or concept maps from these contents. The search bar allows you to quickly find specific topics. Also explore the 'Popular Resources' section on the home page to access the most used materials by students at your level."
    },
    {
        "pregunta": "Adding classmates, it's easy!", 
        "respuesta": "To collaborate with classmates, go to your profile and select the 'Study Partners' option. Search for your friends by username or email. Send connection requests and wait for their confirmation. Once connected, you will be able to share resources, create study groups, and collaborate in real-time on various academic activities."
    },
    {
        "pregunta": "Working in a team, it's fun!", 
        "respuesta": "Student offers tools for collaborative work. Create study groups, share summaries and concept maps with your classmates, conduct group evaluations, and discuss results. Use the chat function to communicate in real-time while studying together. Create shared documents where everyone can contribute their ideas and knowledge."
    },
    {
        "pregunta": "What functions does the application offer for learning?", 
        "respuesta": "Student has multiple tools to enhance your learning: AI-generated intelligent summaries, interactive concept maps, personalized assessments, practice questionnaires, digital library with materials by course, progress tracking with statistics and performance analysis, and collaborative functions to study with classmates. Explore each tab to discover all the available features."
    }
]

# Spanish translations
es_help_questions_answers = [
    {
        "pregunta": "¿Cómo registrarse en tu cuenta de Student?", 
        "respuesta": "Para registrarte, haz clic en el botón 'Crear cuenta' en la página de inicio de sesión. Completa el formulario con tu información personal y académica. Recibirás un correo de confirmación para activar tu cuenta. Una vez activada, podrás iniciar sesión con tu nombre de usuario y contraseña."
    },
    {
        "pregunta": "Para comenzar a usar Student:", 
        "respuesta": "Después de iniciar sesión, explora las diferentes pestañas de la aplicación. Comienza seleccionando un curso y un libro en la pestaña 'Libros'. Luego, utiliza las funcionalidades de resúmenes, mapas conceptuales o evaluaciones para potenciar tu aprendizaje. Recuerda personalizar tu perfil para una mejor experiencia."
    },
    {
        "pregunta": "¿Cómo elegir un curso?", 
        "respuesta": "Navega a la pestaña 'Libros' o a cualquier funcionalidad que requiera selección de curso. Utiliza el menú desplegable para ver los cursos disponibles según tu nivel académico. Selecciona el curso que necesites estudiar. Una vez seleccionado, podrás acceder a los libros y materiales asociados a ese curso específico."
    },
    {
        "pregunta": "Configurar horarios, calificaciones, etc:", 
        "respuesta": "En la pestaña 'Perfil', encontrarás opciones para configurar tu horario de estudio personalizado. Puedes establecer recordatorios, programar sesiones de estudio y dar seguimiento a tus calificaciones. La sección de análisis te permitirá visualizar tu progreso académico y áreas de mejora. Personaliza estas opciones según tus necesidades específicas."
    },
    {
        "pregunta": "¿Cómo explorar materiales y recursos?", 
        "respuesta": "En la pestaña 'Libros' encontrarás todos los materiales organizados por curso y asignatura. Puedes descargar PDFs, crear resúmenes o mapas conceptuales a partir de estos contenidos. La barra de búsqueda te permite encontrar rápidamente temas específicos. Explora también la sección 'Recursos Populares' en la página de inicio para acceder a los materiales más utilizados por estudiantes de tu nivel."
    },
    {
        "pregunta": "Añadir a compañeros, ¡es sencillo!", 
        "respuesta": "Para colaborar con compañeros, ve a tu perfil y selecciona la opción 'Compañeros de estudio'. Busca a tus amigos por nombre de usuario o correo electrónico. Envía solicitudes de conexión y espera su confirmación. Una vez conectados, podrán compartir recursos, crear grupos de estudio y colaborar en tiempo real en diversas actividades académicas."
    },
    {
        "pregunta": "Trabajar en equipo, ¡es divertido!", 
        "respuesta": "Student ofrece herramientas para el trabajo colaborativo. Crea grupos de estudio, comparte resúmenes y mapas conceptuales con tus compañeros, realiza evaluaciones en grupo y discute resultados. Utiliza la función de chat para comunicarte en tiempo real mientras estudian juntos. Crea documentos compartidos donde todos puedan contribuir con sus ideas y conocimientos."
    },
    {
        "pregunta": "¿Qué funciones ofrece la aplicación para aprender?", 
        "respuesta": "Student cuenta con múltiples herramientas para potenciar tu aprendizaje: Resúmenes inteligentes generados por IA, mapas conceptuales interactivos, evaluaciones personalizadas, cuestionarios de práctica, biblioteca digital con materiales por curso, seguimiento de progreso con estadísticas y análisis de rendimiento, y funciones colaborativas para estudiar con compañeros. Explora cada pestaña para descubrir todas las funcionalidades disponibles."
    }
]

# Function to get translations dictionary based on language code
def get_help_questions(lang_code: str) -> list:
    """Get the help questions and answers for the specified language code."""
    if lang_code == "en":
        return en_help_questions_answers
    # Default to Spanish
    return es_help_questions_answers


# Simple self-test when this file is run directly
if __name__ == "__main__":
    print("Testing help translations functionality")
    
    # Test Spanish questions
    es_questions = get_help_questions("es")
    print(f"\nSpanish questions count: {len(es_questions)}")
    print("First 3 Spanish questions:")
    for i, q in enumerate(es_questions[:3]):
        print(f"{i+1}. {q['pregunta']}")
    
    # Test English questions
    en_questions = get_help_questions("en")
    print(f"\nEnglish questions count: {len(en_questions)}")
    print("First 3 English questions:")
    for i, q in enumerate(en_questions[:3]):
        print(f"{i+1}. {q['pregunta']}")
    
    print("\nTest completed successfully!")
