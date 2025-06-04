import os
import sys
import configparser
from PIL import Image
import pytesseract

# =============================
# Configuración y constantes
# =============================
CONFIG_FILE = 'config.ini'
DEFAULT_CONFIG = {
    'General': {
        'input_root': 'Orden',
        'output_root': 'Orden/resultados',
        'max_image_mp': '5',
        'lang': 'spa',
        'log_level': 'INFO',
        'log_file': 'log.txt',
        'resize_threshold': '2000',
    }
}
SUPPORTED_EXT = ('.jpg', '.jpeg', '.png', '.bmp')
SUBFOLDERS = ['Gastos', 'Ganancias']

# =============================
# Utilidades de configuración
# =============================
def create_default_config(path):
    config = configparser.ConfigParser()
    config.read_dict(DEFAULT_CONFIG)
    with open(path, 'w', encoding='utf-8') as f:
        config.write(f)
    print(f"Archivo de configuración creado: {path}")
    return config

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return create_default_config(CONFIG_FILE)
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding='utf-8')
    return config

# =============================
# Utilidades de logging
# =============================
def log(msg, config, level='INFO'):
    log_file = config['General'].get('log_file', 'log.txt')
    log_level = config['General'].get('log_level', 'INFO')
    levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    if levels.index(level) >= levels.index(log_level):
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{level}] {msg}\n")
    if log_level in ['DEBUG', 'INFO']:
        print(f"[{level}] {msg}")

# =============================
# Procesamiento de imágenes
# =============================
def downsample_image(img, max_mp):
    # Redimensiona si la imagen supera el umbral de megapíxeles
    w, h = img.size
    mp = (w * h) / 1_000_000
    if mp > max_mp:
        scale = (max_mp / mp) ** 0.5
        new_size = (int(w * scale), int(h * scale))
        return img.resize(new_size, Image.LANCZOS)
    return img

def ocr_image(img_path, config):
    try:
        from PIL import Image
        import pytesseract
        import cv2
        img = cv2.imread(img_path)
        if img is None:
            raise Exception('No se pudo leer la imagen con OpenCV')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        pil_img = Image.fromarray(gray)
        text = pytesseract.image_to_string(pil_img, lang=config['General'].get('lang', 'spa'))
        return text
    except Exception as e:
        log(f"Error procesando imagen {img_path}: {e}", config, level='ERROR')
        return None

# =============================
# Procesamiento principal
# =============================
def process_folder(input_root, output_root, config):
    print(f"[DEBUG] SUBFOLDERS: {SUBFOLDERS}")
    for subfolder in SUBFOLDERS:
        in_dir = os.path.join(input_root, subfolder)
        out_dir = os.path.join(output_root, subfolder)
        print(f"[DEBUG] Revisando subcarpeta: {in_dir}")
        if not os.path.exists(in_dir):
            print(f"[WARNING] Subcarpeta no encontrada: {in_dir}")
            log(f"Subcarpeta no encontrada: {in_dir}", config, level='WARNING')
            continue
        os.makedirs(out_dir, exist_ok=True)
        archivos = os.listdir(in_dir)
        print(f"[DEBUG] Archivos encontrados en {in_dir}: {archivos}")
        hay_imagenes = False
        for fname in archivos:
            if not fname.lower().endswith(SUPPORTED_EXT):
                continue
            hay_imagenes = True
            in_path = os.path.join(in_dir, fname)
            out_name = os.path.splitext(fname)[0] + '.txt'
            out_path = os.path.join(out_dir, out_name)
            print(f"[DEBUG] Procesando imagen: {in_path} -> {out_path}")
            log(f"Procesando imagen: {in_path}", config, level='DEBUG')
            text = ocr_image(in_path, config)
            if text is None:
                print(f"[WARNING] OCR fallido o error en: {in_path}")
                log(f"OCR fallido o error en: {in_path}", config, level='WARNING')
                continue
            print(f"[DEBUG] Texto extraído ({len(text)} caracteres) de {in_path}: '{text.strip()[:50]}'")
            log(f"Texto extraído ({len(text)} caracteres) de {in_path}: '{text.strip()[:50]}'", config, level='DEBUG')
            try:
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"[DEBUG] Archivo generado: {out_path}")
                log(f"Archivo generado: {out_path}", config, level='INFO')
                if not text.strip():
                    print(f"[WARNING] El texto extraído de {in_path} está vacío.")
                    log(f"ADVERTENCIA: El texto extraído de {in_path} está vacío.", config, level='WARNING')
            except Exception as e:
                print(f"[ERROR] Error guardando {out_path}: {e}")
                log(f"Error guardando {out_path}: {e}", config, level='ERROR')
        if not hay_imagenes:
            print(f"[WARNING] No se detectaron imágenes soportadas en {in_dir}")
            log(f"No se detectaron imágenes soportadas en {in_dir}", config, level='WARNING')
    print(f"[DEBUG] Procesamiento de carpeta completado: {input_root}")
    log(f"Procesamiento de carpeta completado: {input_root}", config, level='DEBUG')

# =============================
# Main
# =============================
def main():
    print("[DEBUG] Iniciando main()...")
    config = load_config()
    print("[DEBUG] Configuración cargada")
    log("Inicio de main()", config, level='DEBUG')
    input_root = config['General'].get('input_root', 'Orden')
    output_root = config['General'].get('output_root', 'Orden/resultados')
    print(f"[DEBUG] input_root: {input_root}, output_root: {output_root}")
    log(f"input_root: {input_root}, output_root: {output_root}", config, level='DEBUG')
    if not os.path.exists(input_root):
        print(f"[ERROR] Carpeta raíz no encontrada: {input_root}")
        log(f"Carpeta raíz no encontrada: {input_root}", config, level='ERROR')
        sys.exit(1)
    os.makedirs(output_root, exist_ok=True)
    print(f"[DEBUG] Carpeta de resultados creada/existente: {output_root}")
    log(f"Carpeta de resultados creada/existente: {output_root}", config, level='DEBUG')
    print("[DEBUG] Iniciando procesamiento de carpetas")
    log("Iniciando procesamiento de carpetas", config, level='DEBUG')
    process_folder(input_root, output_root, config)
    print("[DEBUG] Procesamiento completado.")
    log("Procesamiento completado.", config, level='INFO')

if __name__ == '__main__':
    main()
