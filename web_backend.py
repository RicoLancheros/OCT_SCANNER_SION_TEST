import os
import shutil
import tempfile
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
import zipfile
from app import process_folder, load_config

app = Flask(__name__)
UPLOAD_FOLDER = tempfile.gettempdir()
RESULTS_FOLDER = os.path.join(UPLOAD_FOLDER, 'ocr_resultados')

@app.route('/upload', methods=['POST'])
def upload_zip():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    temp_zip_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(temp_zip_path)

    # Extraer ZIP
    temp_extract_dir = os.path.join(UPLOAD_FOLDER, 'ocr_input')
    if os.path.exists(temp_extract_dir):
        shutil.rmtree(temp_extract_dir)
    os.makedirs(temp_extract_dir, exist_ok=True)
    with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_dir)

    # Procesar OCR
    config = load_config()
    input_root = os.path.join(temp_extract_dir, 'Orden')
    output_root = os.path.join(RESULTS_FOLDER, 'resultados')
    if os.path.exists(RESULTS_FOLDER):
        shutil.rmtree(RESULTS_FOLDER)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    process_folder(input_root, output_root, config)

    # Comprimir resultados
    result_zip_path = os.path.join(UPLOAD_FOLDER, 'ocr_resultados.zip')
    with zipfile.ZipFile(result_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_root):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, output_root)
                zipf.write(abs_path, arcname=rel_path)
    # Limpiar archivos temporales
    os.remove(temp_zip_path)
    shutil.rmtree(temp_extract_dir)
    shutil.rmtree(RESULTS_FOLDER)
    return send_file(result_zip_path, as_attachment=True, download_name='resultados.zip')

from flask import render_template, redirect, url_for

@app.route('/')
def index():
    return redirect(url_for('ocr'))

@app.route('/ocr')
def ocr():
    return render_template('ocr.html')

@app.route('/filtrador')
def filtrador():
    return render_template('filtrador.html')

import re
import json
import io

@app.route('/filtrar_textos', methods=['POST'])
def filtrar_textos():
    if 'txt_files' not in request.files:
        return jsonify({'error': 'No se enviaron archivos .txt'}), 400
    files = request.files.getlist('txt_files')
    resultados = []
    no_total_files = []  # Lista de (nombre, contenido) para los que no tienen total
    for file in files:
        nombre = file.filename
        contenido = file.read().decode('utf-8', errors='ignore')
        # Regex mejoradas para Total, IVA, NIT/Factura
        total = re.search(r'(total(\s*(a\s*pagar|de\s*la\s*factura|factura|importe)?|\s*final)?\s*[:=]?\s*\$?\s*)([\d.,]+)', contenido, re.IGNORECASE)
        iva = re.search(r'(iva(\s*incluido)?\s*[:=]?\s*\$?\s*)([\d.,]+)', contenido, re.IGNORECASE)
        nit = re.search(r'(nit|n\.i\.t\.|numero\s*de\s*factura|número\s*de\s*factura|factura\s*nro|factura\s*no\.?|factura\s*#)\s*[:=]?\s*([\w-]+)', contenido, re.IGNORECASE)
        resultados.append({
            'archivo': nombre,
            'total': total.group(4) if total else None,
            'iva': iva.group(3) if iva else None,
            'nit_o_factura': nit.group(2) if nit else None
        })
        if not total:
            no_total_files.append((nombre, contenido))
    # Generar JSON
    json_data = json.dumps(resultados, ensure_ascii=False, indent=2)
    # Guardar en TXT
    txt_buffer = io.StringIO()
    txt_buffer.write(json_data)
    txt_buffer.seek(0)
    # Comprimir en ZIP
    import zipfile
    import tempfile
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('filtrado_resultados.txt', txt_buffer.getvalue())
        # Agregar los archivos sin total en una carpeta aparte
        for nombre, contenido in no_total_files:
            zipf.writestr(f'no_total/{nombre}', contenido)
    temp_zip.close()
    # Resumen de errores para el frontend
    resumen = {
        'sin_total_count': len(no_total_files),
        'sin_total_files': [nombre for nombre, _ in no_total_files]
    }
    response = send_file(temp_zip.name, as_attachment=True, download_name='filtrado_resultados.zip')
    response.headers['X-Filtrado-Errores'] = json.dumps(resumen, ensure_ascii=False)
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)
