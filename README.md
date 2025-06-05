# OCR SOFTWARE:

# Guía de Instalación y Uso

## Requisitos Previos
- Python 3.6 o superior
- Tesseract OCR instalado localmente
- pip (gestor de paquetes de Python)

## Instalación de dependencias Python
```sh
pip install -r requirements.txt
pip install flask
pip install opencv-python numpy
```

## Instalación de Tesseract OCR
### Windows
1. Descarga el instalador desde: https://github.com/tesseract-ocr/tesseract
2. Instala y agrega la ruta de Tesseract (`tesseract.exe`) al PATH del sistema.
3. (Opcional) Descarga el paquete de idioma español (`spa.traineddata`) si no está incluido.

### Linux (Debian/Ubuntu)
```sh
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-spa
```

### macOS
```sh
brew install tesseract
brew install tesseract-lang
```

## Estructura de Carpetas
```
Orden/
├── Gastos/
│   ├── img1.jpg
│   └── img2.png
├── Ganancias/
│   ├── recibo1.jpg
│   └── factura.png
```

## Uso
1. Coloca tus imágenes en las carpetas `Orden/Gastos` y `Orden/Ganancias`.
2. Ejecuta el script principal:

```sh
python web_backend.py
```
3. Los resultados aparecerán en se decargan en un archivo .zip

## Personalización
- Ajusta parámetros en `config.ini` según tus necesidades.
- Consulta el archivo `log.txt` para mensajes y errores.

## Notas
- El procesamiento es secuencial y optimizado para hardware limitado.
- El tamaño máximo de imagen es de 5MP (redimensionado automático).
- Solo imágenes JPG, PNG y BMP están soportadas en la versión inicial.
