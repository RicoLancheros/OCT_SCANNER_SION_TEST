// JS para el Filtrador de Texto OCR
const filterForm = document.getElementById('filter-form');
const txtInput = document.getElementById('txt-input');
const filterStatus = document.getElementById('filter-status');

filterForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  filterStatus.textContent = 'Preparando archivos...';
  const files = txtInput.files;
  if (!files.length) {
    filterStatus.textContent = 'Selecciona al menos un archivo .txt.';
    return;
  }
  const formData = new FormData();
  for (const file of files) {
    formData.append('txt_files', file, file.name);
  }
  filterStatus.textContent = 'Filtrando y extrayendo datos...';
  const response = await fetch('/filtrar_textos', {
    method: 'POST',
    body: formData
  });
  if (response.ok) {
    // Mostrar gestión de errores si existen
    const erroresHeader = response.headers.get('X-Filtrado-Errores');
    let erroresMsg = '';
    if (erroresHeader) {
      try {
        const resumen = JSON.parse(erroresHeader);
        if (resumen.sin_total_count > 0) {
          erroresMsg = `⚠️ ${resumen.sin_total_count} archivo(s) sin TOTAL detectado(s):\n` + resumen.sin_total_files.join('\n');
        }
      } catch (e) {}
    }
    filterStatus.textContent = 'Descargando resultados...' + (erroresMsg ? '\n' + erroresMsg : '');
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'filtrado_resultados.zip';
    document.body.appendChild(a);
    a.click();
    a.remove();
    filterStatus.textContent = '¡Descarga completada!' + (erroresMsg ? '\n' + erroresMsg : '');
  } else {
    filterStatus.textContent = 'Error en el filtrado.';
  }
});
