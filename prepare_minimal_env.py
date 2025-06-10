#!/usr/bin/env python3
"""
Script de preparación para Railway - Evita problemas de memoria y build
"""
import os
import shutil
import json

def prepare_minimal_environment():
    """Preparar entorno mínimo para Railway"""
    
    print("🔧 Preparando entorno mínimo para Railway...")
    
    # 1. Limpiar directorios problemáticos
    problematic_dirs = ['.web', '.reflex', 'node_modules', '__pycache__', '.next']
    
    for dir_name in problematic_dirs:
        if os.path.exists(dir_name):
            try:
                if os.path.isdir(dir_name):
                    shutil.rmtree(dir_name)
                else:
                    os.remove(dir_name)
                print(f"✓ Eliminado: {dir_name}")
            except Exception as e:
                print(f"⚠ Error eliminando {dir_name}: {e}")
    
    # 2. Crear .web directory mínimo si no existe
    os.makedirs('.web', exist_ok=True)
    
    # 3. Crear package.json mínimo en .web
    minimal_package = {
        "name": "smart-student-dev",
        "version": "1.0.0",
        "private": True,
        "scripts": {
            "dev": "echo 'Dev mode active'",
            "build": "echo 'No build needed in dev mode'",
            "start": "echo 'Dev server running'"
        },
        "dependencies": {},
        "engines": {
            "node": ">=16"
        }
    }
    
    with open('.web/package.json', 'w') as f:
        json.dump(minimal_package, f, indent=2)
    
    print("✓ package.json mínimo creado")
    
    # 4. Crear archivos de configuración mínimos
    config_files = {
        '.web/next.config.js': '''
module.exports = {
  output: 'standalone',
  trailingSlash: true,
  images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true },
  experimental: { 
    appDir: false,
    esmExternals: false
  }
}
''',
        '.web/tsconfig.json': '''
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": false,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "incremental": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve"
  },
  "include": ["**/*"],
  "exclude": ["node_modules"]
}
'''
    }
    
    for file_path, content in config_files.items():
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✓ Creado: {file_path}")
        except Exception as e:
            print(f"⚠ Error creando {file_path}: {e}")
    
    print("✅ Entorno mínimo preparado correctamente")

if __name__ == "__main__":
    prepare_minimal_environment()
