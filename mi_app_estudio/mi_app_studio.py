def vista_pregunta_activa():
    """Componente que muestra la pregunta activa durante la evaluación."""

    # Usamos rx.cond para manejar el caso inicial donde current_eval_question puede ser None
    return rx.card(
        rx.vstack(
            # Encabezado (Progreso y Tiempo) - Siempre se muestra si estamos en esta vista
            rx.hstack(
                rx.text(f"Pregunta {EvaluationState.eval_current_idx + 1} de {EvaluationState.eval_total_q}"),
                rx.spacer(),
                rx.text(EvaluationState.eval_time_formatted, font_weight="bold", color=EvaluationState.eval_time_color),
                justify="between", width="100%", mb="1em"
            ),
            rx.progress(value=EvaluationState.eval_progress, width="100%", size="2", color_scheme=PRIMARY_COLOR_SCHEME, mb="1.5em"),

            # --- Contenido Condicional ---
            rx.cond(
                EvaluationState.current_eval_question != None, # La condición clave: ¿Ya tenemos la pregunta?
                # SI TENEMOS PREGUNTA: Muestra sus detalles
                rx.vstack(
                    rx.heading(EvaluationState.current_eval_question.pregunta, size="5", mb="1.5em", text_align="left", width="100%"),

                    # Lógica de Opciones (Asegúrate que las claves coincidan con tu backend: 'alternativas' o 'opciones')
                    # Ejemplo asumiendo que tus preguntas tienen una clave "alternativas" o "opciones" que es una lista de dicts {id:..., texto:...}
                    # OJO: Necesitarás lógica separada para checkboxes si tienes "seleccion_multiple"
                    rx.cond(
                        (EvaluationState.current_eval_question.tipo == "opcion_multiple") | (EvaluationState.current_eval_question.tipo == "alternativas") | (EvaluationState.current_eval_question.tipo == "verdadero_falso"),
                         rx.radio_group(
                             rx.vstack(
                                 rx.foreach(
                                     # Usamos la var computada que formatea las opciones
                                     EvaluationState.get_current_question_options,
                                     lambda opcion: rx.radio(opcion["texto"], value=opcion["id"], size="2", my="0.2em")
                                 ),
                                 spacing="2", align_items="start", width="100%"
                             ),
                             # Vincula el valor al diccionario de respuestas del usuario
                             value=EvaluationState.eval_user_answers.get(EvaluationState.eval_current_idx, ""),
                             on_change=EvaluationState.set_eval_answer, # Llama al event handler correcto
                             width="100%",
                         ),
                         # Aquí iría el rx.checkbox_group para seleccion_multiple
                         rx.text(f"UI para tipo '{EvaluationState.current_eval_question.tipo}' no implementada.")
                    ),
                    spacing="4", # Espaciado dentro del vstack de la pregunta
                    width="100%",
                    align_items="flex-start"
                ),

                # SI NO TENEMOS PREGUNTA (inicialmente es None): Muestra el spinner
                rx.center(rx.spinner(size="3"), height="200px") # Spinner mientras carga
            ),
            # --- Fin Contenido Condicional ---

            # Botones de Navegación (Siempre visibles si la eval está activa)
            rx.hstack(
                rx.button("Anterior", on_click=EvaluationState.prev_eval_question, is_disabled=EvaluationState.is_first_eval_question, variant="outline"),
                rx.spacer(),
                 rx.cond(
                     EvaluationState.is_last_eval_question,
                     rx.button("Terminar Evaluación", on_click=EvaluationState.calculate_eval_score, color_scheme="green"),
                     rx.button("Siguiente", on_click=EvaluationState.next_eval_question)
                 ),
                margin_top="2em", width="100%"
            ),
            # Mensaje de error específico
            error_callout(EvaluationState.eval_error_message),

            spacing="4", # Espaciado general del vstack principal del card
            width="100%",
            max_width="700px",
            align_items="center" # Centra los elementos del vstack principal
        ),
        padding="2em", width="100%", max_width="800px" # Estilos del card
    )