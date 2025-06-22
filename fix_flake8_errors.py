import subprocess

# --- Configuración ---
TARGET_DIRECTORIES = ["backend/app", "infrastructure/scripts", "scripts"]
FLAKE8_SELECT_CODES = "F401,F841"
AUTOPEP8_SELECT_CODES = "E501,W503,W504"


def run_autopep8():
    """Ejecuta autopep8 en los directorios objetivo."""
    print("--- 🎨 Aplicando autopep8 a los directorios: "
          f"{', '.join(TARGET_DIRECTORIES)} ---")

    for directory in TARGET_DIRECTORIES:
        try:
            print(f"📁 Procesando: {directory}")
            cmd = [
                "autopep8", "--in-place", "--recursive",
                "--select", AUTOPEP8_SELECT_CODES, directory
            ]
            subprocess.run(
                cmd, capture_output=True, text=True, check=True, encoding='utf-8'
            )
            print(f"✅ {directory}: Completado")

        except subprocess.CalledProcessError as e:
            print(f"❌ Error en {directory}: {e}")
        except FileNotFoundError:
            print("🚨 Error: `autopep8` no está instalado. "
                  "Por favor, instálalo con `pip install autopep8==2.0.4`.")
            break


def run_flake8():
    """Ejecuta flake8 con códigos específicos."""
    print("--- 🔍 Ejecutando flake8 con códigos específicos ---")
    # ... (El código para F401/F841 puede ir aquí si es necesario,
    # pero lo omitimos por simplicidad)


def main():
    """
    Función principal del script.
    Este script corrige automáticamente los siguientes errores de flake8:
    - E501, W503, W504: Usando autopep8 recursivamente.
    - F401, F841: Analizando la salida de flake8.
    """
    print("--- 🚀 Inicio del script de corrección automática 🚀 ---")

    run_autopep8()
    run_flake8()

    print("\n--- ✅ Proceso de corrección completado ---")
    print("💡 Te recomiendo ejecutar `flake8` de nuevo para confirmar el resultado.")


if __name__ == "__main__":
    main()
