// Frontend para subir la carpeta Orden como ZIP y descargar resultados
const uploadForm = document.getElementById('upload-form');
const fileInput = document.getElementById('folder-input');
const statusDiv = document.getElementById('status');

uploadForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  statusDiv.textContent = 'Comprimiendo carpeta...';
  const files = fileInput.files;
  if (!files.length) {
    statusDiv.textContent = 'Selecciona la carpeta Orden.';
    return;
  }
  // Crear ZIP en el navegador
  const zip = new JSZip();
  for (const file of files) {
    // file.webkitRelativePath incluye la ruta relativa dentro de la carpeta
    zip.file(file.webkitRelativePath, file);
  }
  const blob = await zip.generateAsync({ type: 'blob' });
  statusDiv.textContent = 'Subiendo carpeta al servidor...';

  // Subir ZIP al backend
  const formData = new FormData();
  formData.append('file', blob, 'orden.zip');
  const response = await fetch('/upload', {
    method: 'POST',
    body: formData
  });
  if (response.ok) {
    statusDiv.textContent = 'Procesando OCR. Descargando resultados...';
    const resultBlob = await response.blob();
    const url = window.URL.createObjectURL(resultBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'resultados.zip';
    document.body.appendChild(a);
    a.click();
    a.remove();
    statusDiv.textContent = '¡Procesamiento completado! Descarga iniciada.';
  } else {
    statusDiv.textContent = 'Error en el procesamiento.';
  }
});
