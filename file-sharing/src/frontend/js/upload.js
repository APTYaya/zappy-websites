export async function uploadChunked(file, formData, config, ui) {
  let uploadId = localStorage.getItem("upload_id");

  if (!uploadId) {
  uploadId = crypto.randomUUID();
  localStorage.setItem("upload_id", uploadId);
  }

  const totalChunks = Math.ceil(file.size / config.chunkSize);

  const statusRes = await fetch(`/upload/status/${uploadId}`);
  const statusData = await statusRes.json();
  const received = new Set(statusData.received_chunks || []);

  ui.progressBox.style.display = 'block';

  let totalUploaded = received.size * config.chunkSize;

  for (let i = 0; i < totalChunks; i++) {
    if (received.has(i)) continue;

    const start = i * config.chunkSize;
    const end = Math.min(start + config.chunkSize, file.size);
    const chunk = file.slice(start, end);

    const chunkForm = new FormData();
    chunkForm.append("upload_id", uploadId);
    chunkForm.append("chunk_number", i);
    chunkForm.append("file_type", config.fileType);
    chunkForm.append("chunk", chunk, file.name);

    await new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      const chunkStart = totalUploaded;
      const startTime = Date.now();

      xhr.upload.addEventListener("progress", (e) => {
        if (!e.lengthComputable) return;

        const currentUploaded = chunkStart + e.loaded;
        const pct = Math.round((currentUploaded / file.size) * 100);

        ui.progressBar.style.width = pct + '%';
        ui.progressPct.textContent = pct + '%';

        const elapsed = (Date.now() - startTime) / 1000;
        const speed = (e.loaded / elapsed / 1024).toFixed(1);

        ui.progressSpeed.textContent = speed + ' KB/s';
      });

      xhr.onload = () => {
        totalUploaded += (end - start);
        resolve();
      };

      xhr.onerror = reject;

      xhr.open("POST", config.chunkEndpoint);
      xhr.send(chunkForm);
    });
  }

  const completeForm = new FormData();
  completeForm.append("upload_id", uploadId);
  completeForm.append("filename", file.name);
  completeForm.append("file_type", config.fileType);
  completeForm.append("total_chunks", totalChunks);
  completeForm.append("expiration_hours", formData.get("expiration_hours"));
  completeForm.append("burn", formData.get("burn") || false);
  if (formData.get("password")) completeForm.append("password", formData.get("password"));

  const res = await fetch(config.completeEndpoint, { method: "POST", body: completeForm });
  const data = await res.json();

  localStorage.removeItem("upload_id");

  return data.url;
}
