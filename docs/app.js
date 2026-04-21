// All-to-All Static Edition — client-side converter
// Supports: image ↔ image (Canvas), image → PDF (jsPDF), PDF → image (pdf.js)
// Larger video/audio/HTML jobs are directed to the local server edition.

(() => {
  const IMAGE_EXTS = ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif'];
  const SUPPORTED_SRC = [...IMAGE_EXTS, '.pdf'];

  const TARGETS_IMAGE = [
    { ext: '.png',  name: 'PNG',  desc: '투명 배경 지원' },
    { ext: '.jpg',  name: 'JPG',  desc: '용량 줄이기' },
    { ext: '.webp', name: 'WEBP', desc: '웹 최적화' },
    { ext: '.pdf',  name: 'PDF',  desc: '문서로 제출' },
  ];
  const TARGETS_PDF = [
    { ext: '.png',  name: 'PNG',  desc: '페이지별 PNG' },
    { ext: '.jpg',  name: 'JPG',  desc: '페이지별 JPG' },
    { ext: '.webp', name: 'WEBP', desc: '페이지별 WEBP' },
  ];

  const $ = (id) => document.getElementById(id);
  const dropzone = $('dropzone');
  const fileInput = $('fileInput');
  const fileListEl = $('fileList');
  const fileItems = $('fileItems');
  const fileCount = $('fileCount');
  const clearBtn = $('clearBtn');
  const formatSection = $('formatSection');
  const formatLabel = $('formatLabel');
  const formatGrid = $('formatGrid');
  const convertBtn = $('convertBtn');
  const progress = $('progress');
  const progressText = $('progressText');
  const result = $('result');
  const resultIcon = $('resultIcon');
  const resultMsg = $('resultMsg');
  const againBtn = $('againBtn');
  const unsupported = $('unsupported');

  let files = [];
  let selectedFormat = null;
  let pdfjsLib = null;

  const getExt = (name) => {
    const i = name.lastIndexOf('.');
    return i >= 0 ? name.substring(i).toLowerCase() : '';
  };
  const normalizeExt = (e) => e === '.jpeg' ? '.jpg' : e;
  const fmtBytes = (b) => {
    if (b < 1024) return b + ' B';
    if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
    return (b / 1048576).toFixed(1) + ' MB';
  };

  // ── Drop zone wiring ────────────────────────────────
  dropzone.addEventListener('click', () => fileInput.click());
  dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('drag-over'); });
  dropzone.addEventListener('dragleave', () => dropzone.classList.remove('drag-over'));
  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('drag-over');
    addFiles(Array.from(e.dataTransfer.files));
  });
  fileInput.addEventListener('change', () => {
    addFiles(Array.from(fileInput.files));
    fileInput.value = '';
  });
  clearBtn.addEventListener('click', reset);
  againBtn.addEventListener('click', reset);

  function reset() {
    files = [];
    selectedFormat = null;
    fileListEl.classList.remove('show');
    formatSection.classList.remove('show');
    convertBtn.classList.remove('show');
    progress.classList.remove('show');
    result.classList.remove('show');
    unsupported.classList.remove('show');
    dropzone.style.display = '';
    fileItems.innerHTML = '';
  }

  function addFiles(newFiles) {
    // Validate: if any file is a server-only type, show notice
    const unsupportedExts = newFiles
      .map((f) => normalizeExt(getExt(f.name)))
      .filter((e) => e && !SUPPORTED_SRC.includes(e));
    if (unsupportedExts.length > 0) {
      const list = [...new Set(unsupportedExts)].join(', ');
      showUnsupported(`감지된 지원 불가 포맷: ${list}`);
      return;
    }
    files = files.concat(newFiles);
    renderFileList();
    pickFormats();
  }

  function removeFile(idx) {
    files.splice(idx, 1);
    if (files.length === 0) { reset(); return; }
    renderFileList();
    pickFormats();
  }

  function renderFileList() {
    dropzone.style.display = 'none';
    result.classList.remove('show');
    progress.classList.remove('show');
    unsupported.classList.remove('show');

    const total = files.reduce((s, f) => s + f.size, 0);
    fileCount.innerHTML = `<strong>${files.length}개</strong> 파일 · ${fmtBytes(total)}`;
    fileItems.innerHTML = '';

    files.forEach((f, i) => {
      const ext = getExt(f.name).replace('.', '');
      const div = document.createElement('div');
      div.className = 'file-item';
      const extClass = ext === 'pdf' ? 'document' : '';
      div.innerHTML = `
        <div class="file-ext ${extClass}">${ext.toUpperCase()}</div>
        <div class="file-item-name"></div>
        <div class="file-item-size">${fmtBytes(f.size)}</div>
        <button class="file-item-remove" aria-label="Remove">&times;</button>
      `;
      div.querySelector('.file-item-name').textContent = f.name;
      div.querySelector('.file-item-remove').addEventListener('click', () => removeFile(i));
      fileItems.appendChild(div);
    });
    fileListEl.classList.add('show');
  }

  function pickFormats() {
    if (!files.length) return;
    selectedFormat = null;
    convertBtn.classList.remove('show');

    const firstExt = normalizeExt(getExt(files[0].name));
    const targets = firstExt === '.pdf' ? TARGETS_PDF : TARGETS_IMAGE;
    const filtered = targets.filter((t) => t.ext !== firstExt);

    formatLabel.textContent = `${files.length}개 파일을 어떤 포맷으로?`;
    formatGrid.innerHTML = '';
    filtered.forEach((t) => {
      const btn = document.createElement('button');
      btn.className = 'fmt-btn';
      btn.innerHTML = `<span class="fmt-name">${t.name}</span><span class="fmt-desc">${t.desc}</span>`;
      btn.addEventListener('click', () => {
        document.querySelectorAll('.fmt-btn').forEach((b) => b.classList.remove('selected'));
        btn.classList.add('selected');
        selectedFormat = t.ext;
        convertBtn.textContent = `${files.length}개 파일 → ${t.name} 변환하기`;
        convertBtn.classList.add('show');
      });
      formatGrid.appendChild(btn);
    });
    formatSection.classList.add('show');
  }

  function showUnsupported(msg) {
    unsupported.classList.add('show');
    $('unsupportedTitle').textContent = msg;
    fileListEl.classList.remove('show');
    formatSection.classList.remove('show');
    convertBtn.classList.remove('show');
    dropzone.style.display = '';
  }

  function showResult(ok, msg) {
    progress.classList.remove('show');
    result.className = 'result show ' + (ok ? 'success' : 'error');
    resultIcon.textContent = ok ? '✓' : '✕';
    resultMsg.textContent = msg;
  }

  // ── Conversions ─────────────────────────────────────

  const mimeFor = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
  };

  async function fileToImage(file) {
    const url = URL.createObjectURL(file);
    try {
      const img = new Image();
      img.decoding = 'async';
      await new Promise((res, rej) => {
        img.onload = () => res();
        img.onerror = () => rej(new Error('이미지 로드 실패'));
        img.src = url;
      });
      return img;
    } finally {
      // revoke after use by caller; keep url for now is fine as image is decoded
      setTimeout(() => URL.revokeObjectURL(url), 30000);
    }
  }

  async function imageToImage(file, targetExt) {
    const img = await fileToImage(file);
    const canvas = document.createElement('canvas');
    canvas.width = img.naturalWidth;
    canvas.height = img.naturalHeight;
    const ctx = canvas.getContext('2d');

    // JPEG/BMP: white background (alpha flatten)
    if (targetExt === '.jpg' || targetExt === '.jpeg') {
      ctx.fillStyle = '#fff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }
    ctx.drawImage(img, 0, 0);

    const mime = mimeFor[targetExt] || 'image/png';
    const quality = targetExt === '.webp' ? 0.9 : (targetExt === '.jpg' || targetExt === '.jpeg') ? 0.95 : undefined;

    return await new Promise((resolve, reject) => {
      canvas.toBlob(
        (blob) => blob ? resolve(blob) : reject(new Error('Canvas 변환 실패')),
        mime,
        quality,
      );
    });
  }

  async function imageToPdf(file) {
    const img = await fileToImage(file);
    const { jsPDF } = window.jspdf;

    const W = img.naturalWidth;
    const H = img.naturalHeight;
    const orientation = W >= H ? 'landscape' : 'portrait';

    // Use custom size to match image pixels @ 72dpi for 1:1 fidelity
    const pdf = new jsPDF({
      orientation,
      unit: 'px',
      format: [W, H],
      hotfixes: ['px_scaling'],
    });

    const canvas = document.createElement('canvas');
    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, W, H);
    ctx.drawImage(img, 0, 0);
    const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
    pdf.addImage(dataUrl, 'JPEG', 0, 0, W, H);
    return pdf.output('blob');
  }

  async function loadPdfJs() {
    if (pdfjsLib) return pdfjsLib;
    const mod = await import('https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/build/pdf.min.mjs');
    mod.GlobalWorkerOptions.workerSrc = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.0.379/build/pdf.worker.min.mjs';
    pdfjsLib = mod;
    return mod;
  }

  async function pdfToImages(file, targetExt) {
    const lib = await loadPdfJs();
    const buf = await file.arrayBuffer();
    const doc = await lib.getDocument({ data: buf }).promise;
    const mime = mimeFor[targetExt] || 'image/png';
    const quality = targetExt === '.webp' ? 0.9 : (targetExt === '.jpg' ? 0.95 : undefined);
    const results = [];

    for (let p = 1; p <= doc.numPages; p++) {
      const page = await doc.getPage(p);
      const scale = 2; // ~200dpi for readable output
      const viewport = page.getViewport({ scale });
      const canvas = document.createElement('canvas');
      canvas.width = Math.ceil(viewport.width);
      canvas.height = Math.ceil(viewport.height);
      const ctx = canvas.getContext('2d');
      if (targetExt === '.jpg' || targetExt === '.jpeg') {
        ctx.fillStyle = '#fff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }
      await page.render({ canvasContext: ctx, viewport }).promise;
      const blob = await new Promise((res, rej) =>
        canvas.toBlob((b) => b ? res(b) : rej(new Error('Canvas 변환 실패')), mime, quality)
      );
      results.push({
        page: p,
        total: doc.numPages,
        blob,
      });
    }
    return results;
  }

  async function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  // Build a zip via native support check → fallback: sequential downloads
  async function downloadMany(entries) {
    // Sequential download is simplest and most compatible (no JSZip dep)
    for (let i = 0; i < entries.length; i++) {
      await downloadBlob(entries[i].blob, entries[i].name);
      // Small delay so browser doesn't block
      if (i < entries.length - 1) await new Promise((r) => setTimeout(r, 200));
    }
  }

  convertBtn.addEventListener('click', async () => {
    if (!files.length || !selectedFormat) return;

    convertBtn.classList.remove('show');
    formatSection.classList.remove('show');
    fileListEl.classList.remove('show');
    result.classList.remove('show');
    progress.classList.add('show');

    const t = selectedFormat;
    const outputs = [];

    try {
      for (let i = 0; i < files.length; i++) {
        const f = files[i];
        progressText.textContent = `${i + 1}/${files.length} 변환 중... ${f.name}`;
        const srcExt = normalizeExt(getExt(f.name));
        const stem = f.name.replace(/\.[^.]+$/, '');

        if (srcExt === '.pdf') {
          // PDF → image
          const pages = await pdfToImages(f, t);
          if (pages.length === 1) {
            outputs.push({ blob: pages[0].blob, name: `${stem}${t}` });
          } else {
            for (const p of pages) {
              outputs.push({
                blob: p.blob,
                name: `${stem}_p${String(p.page).padStart(3, '0')}${t}`,
              });
            }
          }
        } else if (t === '.pdf') {
          // image → PDF
          const blob = await imageToPdf(f);
          outputs.push({ blob, name: `${stem}.pdf` });
        } else {
          // image → image
          const blob = await imageToImage(f, t);
          outputs.push({ blob, name: `${stem}${t}` });
        }
      }

      progressText.textContent = `${outputs.length}개 파일 다운로드 중...`;
      await downloadMany(outputs);
      showResult(true, `${outputs.length}개 파일 다운로드 완료`);
    } catch (err) {
      console.error(err);
      showResult(false, `변환 실패: ${err.message || err}`);
    }
  });
})();
