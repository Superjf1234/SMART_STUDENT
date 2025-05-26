# Variables computadas para el modo de revisión
# Añadir después de la función eval_titulo_resultado

@rx.var
def current_review_user_answer(self) -> str:
    """Devuelve la respuesta del usuario para la pregunta actual en modo revisión."""
    idx = self.eval_current_idx
    if not (0 <= idx < len(self.eval_preguntas)):
        return "N/A"
        
    user_answer = self.eval_user_answers.get(idx)
    
    if user_answer is None:
        return "Sin respuesta"
        
    # Si es un conjunto (selección múltiple), formatear como string
    if isinstance(user_answer, set):
        if not user_answer:
            return "Sin respuesta"
        # Buscar los textos de las opciones seleccionadas
        opciones = self.get_current_question_options
        textos_seleccionados = [opt["texto"] for opt in opciones if opt["id"] in user_answer]
        if textos_seleccionados:
            return ", ".join(textos_seleccionados)
        else:
            # Si los IDs en user_answer no tienen textos correspondientes (raro), mostrar los IDs
            return ", ".join(sorted(list(user_answer)))

    # Si es una cadena, buscar el texto correspondiente si es una opción
    opciones = self.get_current_question_options
    for opcion in opciones:
        if opcion["id"].strip().lower() == str(user_answer).strip().lower():
            return opcion["texto"]
    
    # Si no coincide con ningún ID de opción (ej. V/F que no usa IDs, o respuesta directa)
    return str(user_answer) # Devolver el valor tal cual

@rx.var
def current_review_correct_answer(self) -> str:
    """Devuelve la respuesta correcta para la pregunta actual en modo revisión."""
    current_q = self.current_eval_question
    if not current_q:
        return "N/A"
        
    tipo_pregunta = current_q.get("tipo")
    
    if tipo_pregunta == "seleccion_multiple":
        correctas_list = current_q.get("correctas", current_q.get("respuestas_correctas", []))
        if isinstance(correctas_list, list):
            # Buscar los textos correspondientes a los IDs correctos
            opciones = self.get_current_question_options
            textos_correctos = [opt["texto"] for opt in opciones if opt["id"] in correctas_list]
            if textos_correctos:
                return ", ".join(textos_correctos)
            # Si no se encontraron textos, devolver los IDs correctos
            return ", ".join(map(str, correctas_list)) 
        return "Error en datos (correctas no es lista)"
        
    else: # Verdadero/Falso, Alternativas, Opción Múltiple (respuesta única)
        correcta_single = current_q.get("correcta", current_q.get("respuesta_correcta"))
        if correcta_single is None:
            return "N/A (Respuesta correcta no especificada)"

        # Manejo especial para booleanos de V/F si vinieran así
        if isinstance(correcta_single, bool):
             return "Verdadero" if correcta_single else "Falso"

        # Buscar el texto correspondiente si la respuesta correcta es un ID/letra
        opciones = self.get_current_question_options
        for opcion in opciones:
            if opcion["id"].strip().lower() == str(correcta_single).strip().lower():
                return opcion["texto"]
        
        # Si no coincide con ningún ID de opción
        return str(correcta_single) # Devolver el valor tal cual
        
@rx.var
def current_review_explanation(self) -> str:
    """Devuelve la explicación para la pregunta actual en modo revisión."""
    current_q = self.current_eval_question
    if not current_q:
        return "Explicación no disponible."
        
    explanation = current_q.get("explicacion")
    if explanation:
        return str(explanation)
    return "Explicación no disponible para esta pregunta."
    
@rx.var
def is_current_question_correct_in_review(self) -> Optional[bool]:
    """
    Indica si la respuesta del usuario para la pregunta actual fue correcta.
    Retorna True si es correcta, False si es incorrecta.
    """
    idx = self.eval_current_idx
    if not (0 <= idx < len(self.eval_preguntas)):
        return False # Fuera de rango o sin pregunta, se considera incorrecto para la revisión

    user_answer = self.eval_user_answers.get(idx)
    # Si no hay respuesta del usuario, se considera incorrecta
    if user_answer is None or (isinstance(user_answer, str) and user_answer == "") or (isinstance(user_answer, set) and not user_answer):
        return False 
        
    current_q = self.eval_preguntas[idx]
    tipo_pregunta = current_q.get("tipo")

    if tipo_pregunta == "seleccion_multiple":
        correctas_list = current_q.get("correctas", current_q.get("respuestas_correctas", []))
        if not isinstance(correctas_list, list):
            print(f"ERROR: Datos incorrectos para correctas_list en pregunta {idx}")
            return False # Error en datos

        # Convertir ambas a sets de strings normalizados para comparación
        user_set = {str(item).strip().lower() for item in (user_answer if isinstance(user_answer, set) else set())}
        correct_set = {str(item).strip().lower() for item in correctas_list}
        
        # Es correcta si el set del usuario coincide exactamente con el set de correctas
        # y si el usuario dio alguna respuesta (set no vacío) y el set de correctas no está vacío
        is_correct = user_set == correct_set and len(user_set) > 0

    else: # Verdadero/Falso, Alternativas, Opción Múltiple (respuesta única)
        correcta_single = current_q.get("correcta", current_q.get("respuesta_correcta"))
        if correcta_single is None:
            print(f"ERROR: Datos incorrectos para correcta_single en pregunta {idx}")
            return False # Error en datos

        # Manejo especial para booleanos de V/F si vinieran así en correcta_single
        if isinstance(correcta_single, bool):
            correcta_single = "verdadero" if correcta_single else "falso"

        # Comparación insensible a mayúsculas/minúsculas y espacios
        # Asegurarse de que u_ans no sea un set si se espera respuesta única
        user_answer_str = ""
        if isinstance(user_answer, str):
            user_answer_str = user_answer
        elif user_answer is not None: # Si es bool u otro tipo, convertir a str
            user_answer_str = str(user_answer)

        is_correct = user_answer_str.strip().lower() == str(correcta_single).strip().lower()

    return is_correct
