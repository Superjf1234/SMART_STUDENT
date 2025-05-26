"""
Componentes para mensajes de revisión con colores reforzados.
Este archivo proporciona componentes optimizados para mostrar los mensajes
de respuesta correcta e incorrecta con colores adecuados en el modo de revisión.
"""
import reflex as rx

def mensaje_respuesta_correcta():
    """Componente que muestra "¡Respuesta correcta!" con color verde garantizado."""
    return rx.html(
        """
        <div style="
            color: #22C55E; 
            font-weight: bold; 
            font-size: 1.1em; 
            text-shadow: 0px 0px 1px rgba(0,0,0,0.1);
            margin: 0.5em 0;
            display: inline-block;
        ">
            ¡Respuesta correcta!
        </div>
        """
    )

def mensaje_respuesta_incorrecta():
    """Componente que muestra "Respuesta incorrecta" con color rojo garantizado."""
    return rx.html(
        """
        <div style="
            color: #E53E3E; 
            font-weight: bold; 
            font-size: 1.1em; 
            text-shadow: 0px 0px 1px rgba(0,0,0,0.1);
            margin: 0.5em 0;
            display: inline-block;
        ">
            Respuesta incorrecta
        </div>
        """
    )
