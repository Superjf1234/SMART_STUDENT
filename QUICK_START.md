# 🚀 Guía de Inicio Rápido - SMART STUDENT

## ⚡ Inicio Super Rápido (1 comando)

```bash
python final_port_fix.py
```

**¡Eso es todo!** Este comando hace todo automáticamente:
- 🔍 Encuentra puertos libres
- 🧹 Limpia conflictos
- 🚀 Inicia la aplicación
- 📱 Te muestra las URLs de acceso

## 📱 URLs de Acceso

Una vez iniciado, la aplicación estará disponible en:
- **Frontend (Interfaz Web)**: http://localhost:3001
- **Backend (API)**: http://localhost:8081

## 🔧 Si Tienes Problemas

### Problema: "Address already in use"
```bash
python aggressive_cleanup.py
python final_port_fix.py
```

### Problema: Puerto específico ocupado
```bash
python clean_port.py 8080
```

### Problema: Quiero usar puertos específicos
```bash
python -m reflex run --backend-port 8082 --frontend-port 3002
```

## 📋 Scripts Disponibles

| Script | Propósito | Uso |
|--------|-----------|-----|
| `final_port_fix.py` | **PRINCIPAL** - Solución automática completa | `python final_port_fix.py` |
| `aggressive_cleanup.py` | Limpieza robusta de todos los puertos | `python aggressive_cleanup.py` |
| `clean_port.py` | Limpiar un puerto específico | `python clean_port.py [puerto]` |
| `start_reflex_clean.py` | Inicio con limpieza visual | `python start_reflex_clean.py` |
| `start_reflex_smart.py` | Búsqueda inteligente de puertos | `python start_reflex_smart.py` |

## 🎯 Primera Ejecución

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/Superjf1234/SMART_STUDENT.git
   cd SMART_STUDENT
   ```

2. **Instala dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **¡Ejecuta la aplicación!**:
   ```bash
   python final_port_fix.py
   ```

4. **Abre tu navegador** en http://localhost:3001

## 💡 Consejos

- **Primer uso**: Si es tu primera vez, usa `final_port_fix.py`
- **Desarrollo**: Para desarrollo continuo, puedes usar `python -m reflex run`
- **Problemas**: Si hay conflictos, ejecuta `aggressive_cleanup.py` primero
- **Railway**: En Railway, todo funciona automáticamente con las variables de entorno

## 🆘 Soporte

Si tienes problemas:
1. Revisa `PORT_PROBLEM_SOLVED.md` para soluciones detalladas
2. Ejecuta `python aggressive_cleanup.py` para limpiar todo
3. Usa `final_port_fix.py` para reinicio automático
4. Verifica que tienes Python 3.12+ instalado

---
**¡Disfruta usando SMART STUDENT! 🎓**
