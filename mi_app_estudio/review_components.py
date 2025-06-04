"""
Review components for SMART_STUDENT application.
Contains UI components for showing review feedback messages.
"""

import reflex as rx
from .state import PRIMARY_COLOR_SCHEME, ACCENT_COLOR_SCHEME


def mensaje_respuesta_correcta():
    """Component that displays a success message for correct answers."""
    return rx.box(
        rx.hstack(
            rx.icon(
                tag="check_circle",
                color="green.500",
                size="20px"
            ),
            rx.text(
                "¡Correcto! / Correct!",
                color="green.600",
                font_weight="semibold",
                font_size="sm"
            ),
            spacing="2",
            align="center"
        ),
        bg="green.50",
        border="1px solid",
        border_color="green.200",
        border_radius="md",
        padding="3",
        margin_top="2"
    )


def mensaje_respuesta_incorrecta():
    """Component that displays an error message for incorrect answers."""
    return rx.box(
        rx.hstack(
            rx.icon(
                tag="x_circle",
                color="red.500",
                size="20px"
            ),
            rx.text(
                "Incorrecto / Incorrect",
                color="red.600",
                font_weight="semibold",
                font_size="sm"
            ),
            spacing="2",
            align="center"
        ),
        bg="red.50",
        border="1px solid",
        border_color="red.200",
        border_radius="md",
        padding="3",
        margin_top="2"
    )
