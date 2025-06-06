# 🎓 SMART_STUDENT

**Aplicación educativa inteligente para generar resúmenes, mapas conceptuales y evaluaciones**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/Superjf1234/SMART_STUDENT)
[![Python](https://img.shields.io/badge/Python-3.12-green)](https://www.python.org/)
[![Reflex](https://img.shields.io/badge/Reflex-0.3.6+-purple)](https://reflex.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🚀 Características Principales

- 📚 **Generación de Resúmenes**: Crea resúmenes inteligentes de contenido educativo
- 🗺️ **Mapas Conceptuales**: Genera mapas mentales interactivos 
- 📝 **Evaluaciones Automáticas**: Sistema de cuestionarios adaptativos
- 👤 **Gestión de Usuarios**: Sistema de autenticación y perfiles
- 📊 **Seguimiento de Progreso**: Estadísticas detalladas del aprendizaje
- 🌐 **Interfaz Bilingüe**: Soporte para español e inglés

## 🛠️ Tecnologías Utilizadas

- **Frontend**: Reflex (React + Python)
- **Backend**: Python 3.12
- **Base de Datos**: SQLite
- **PDF Processing**: PyPDF
- **Authentication**: bcrypt + passlib
- **Deployment**: Docker, Railway, Vercel, Heroku

## 📦 Instalación

### Prerrequisitos
- Python 3.12+
- Git

### Instalación Local

```bash
# Clonar el repositorio
git clone https://github.com/Superjf1234/SMART_STUDENT.git
cd SMART_STUDENT

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus claves API

# Ejecutar la aplicación
python -m reflex run
```

### Instalación con Docker

```bash
# Construir imagen
docker build -t smart-student .

# Ejecutar contenedor
docker run -p 3000:3000 -p 8001:8001 smart-student
```

## 🚀 Deployment

### Railway
```bash
railway login
railway link
railway up
```

### Vercel
```bash
vercel --prod
```

### Heroku
```bash
heroku create tu-app-name
git push heroku main
```

## 📁 Estructura del Proyecto

```
SMART_STUDENT/
├── mi_app_estudio/          # Aplicación principal Reflex
│   ├── state.py            # Estado de la aplicación
│   ├── mi_app_estudio.py   # Componentes UI principales
│   ├── evaluaciones.py     # Sistema de evaluaciones
│   ├── cuestionario.py     # Componente de cuestionarios
│   └── backend/            # Lógica de backend específica
├── backend/                # Backend compartido
│   ├── db_logic.py         # Lógica de base de datos
│   ├── config_logic.py     # Configuración del sistema
│   ├── eval_logic.py       # Lógica de evaluaciones
│   ├── map_logic.py        # Generación de mapas
│   └── resumen_logic.py    # Generación de resúmenes
├── assets/                 # Archivos estáticos
│   ├── pdfs/              # Documentos educativos
│   └── mapas/             # Mapas generados
├── requirements.txt        # Dependencias Python
├── Dockerfile             # Configuración Docker
├── reflex.json            # Configuración Reflex
└── rxconfig.py            # Configuración Python
```

## ⚙️ Configuración

### Variables de Entorno
Crea un archivo `.env` basado en `.env.example`:

```env
GEMINI_API_KEY=tu_api_key_aqui
```

### Base de Datos
La aplicación usa SQLite y se inicializa automáticamente al primer ejecutar.

## 📝 Uso

1. **Iniciar Sesión**: Usar credenciales de prueba o crear cuenta
2. **Seleccionar Contenido**: Elegir curso, libro y tema
3. **Generar Resumen**: Crear resumen automático del contenido
4. **Crear Mapa Conceptual**: Generar mapa mental interactivo  
5. **Realizar Evaluación**: Responder cuestionario adaptativo
6. **Ver Progreso**: Revisar estadísticas en el perfil

## 🔧 Desarrollo

### Ejecutar en Desarrollo
```bash
python -m reflex run --backend-host 0.0.0.0 --backend-port 3000
```

### Ejecutar Tests
```bash
python -m pytest
```

### Lint Code
```bash
flake8 --exclude=.venv,node_modules .
```

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- **SMART_STUDENT Team** - *Desarrollo inicial* - [Superjf1234](https://github.com/Superjf1234)

## 📞 Soporte

Para soporte y preguntas:
- Abrir un [Issue](https://github.com/Superjf1234/SMART_STUDENT/issues)
- Contactar: [GitHub Profile](https://github.com/Superjf1234)

## 🎯 Roadmap

- [ ] Integración con más APIs de IA
- [ ] Soporte para más formatos de documentos
- [ ] Modo offline
- [ ] Aplicación móvil
- [ ] Integración con LMS

---

⭐ **¡Si te gusta este proyecto, dale una estrella!** ⭐