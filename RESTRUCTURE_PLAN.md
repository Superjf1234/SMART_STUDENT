# PLAN DE REESTRUCTURACIÓN PARA SMART_STUDENT

## PROBLEMAS ACTUALES:
1. Importaciones circulares: mi_app_estudio.py ↔ evaluaciones.py ↔ state.py
2. 67+ archivos de scripts y fixes acumulados
3. Configuración inconsistente en múltiples archivos
4. Dependencias complejas entre módulos

## ESTRUCTURA PROPUESTA:

```
/app/
├── rxconfig.py                 # Configuración Reflex (RAÍZ)
├── requirements.txt           # Dependencias mínimas
├── ultra_robust_start.py      # Script inicio (CORREGIDO)
├── .env.railway              # Variables Railway
├── 
├── smart_student/            # Aplicación principal
│   ├── __init__.py
│   ├── app.py               # Aplicación Reflex principal (EN LUGAR DE mi_app_estudio.py)
│   ├── config.py           # Configuración centralizada
│   ├── 
│   ├── core/               # Módulos centrales
│   │   ├── __init__.py
│   │   ├── state.py        # Estado base (SIN importaciones circulares)
│   │   ├── auth.py         # Autenticación
│   │   └── database.py     # Base de datos
│   │
│   ├── features/           # Características por módulo
│   │   ├── __init__.py
│   │   ├── evaluations/    # Evaluaciones
│   │   │   ├── __init__.py
│   │   │   ├── state.py
│   │   │   └── components.py
│   │   ├── summaries/      # Resúmenes
│   │   └── maps/          # Mapas conceptuales
│   │
│   ├── ui/                # Componentes UI
│   │   ├── __init__.py
│   │   ├── pages/         # Páginas
│   │   └── components/    # Componentes reutilizables
│   │
│   └── utils/             # Utilidades
│       ├── __init__.py
│       ├── translations.py
│       └── helpers.py
│
└── backend/               # Lógica de negocio (MANTENER)
    ├── __init__.py
    ├── config_logic.py
    ├── db_logic.py
    └── ...
```

## BENEFICIOS:
1. ✅ Sin importaciones circulares
2. ✅ Módulos independientes y testeable
3. ✅ Estructura escalable
4. ✅ Separación clara de responsabilidades
5. ✅ Fácil mantenimiento

## MIGRACIÓN GRADUAL:
1. Crear nueva estructura
2. Migrar módulo por módulo
3. Mantener funcionalidad existente
4. Eliminar archivos obsoletos
