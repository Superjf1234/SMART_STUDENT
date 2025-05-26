#!/usr/bin/env python3

import sys
sys.path.append('/workspaces/SMART_STUDENT')

from mi_app_estudio.state import AppState

methods = ['generate_summary', 'download_pdf', 'download_resumen_pdf', 'download_map_pdf', 'download_cuestionario_pdf']

for method in methods:
    print(f'{method} exists: {hasattr(AppState, method)}')
