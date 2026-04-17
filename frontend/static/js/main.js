/**
 * CV Resume Screener — Frontend Interactivity
 * Handles drag-and-drop, file validation, animations, and form submission.
 */

document.addEventListener('DOMContentLoaded', () => {
    initDropzones();
    initFileInputs();
    initFormSubmission();
    initProgressBars();
    initStatCounters();
    initFlashMessages();
    initCharCount();
});

/* ═══════════════════════════════════════════════════════════════════════════
   Drag & Drop File Upload
   ═══════════════════════════════════════════════════════════════════════════ */

function initDropzones() {
    // Main upload page dropzone
    setupDropzone('dropzone', 'file-input', 'file-list', 'file-items', 'classify-btn');

    // Match page dropzone
    setupDropzone('match-dropzone', 'match-file-input', 'match-file-list', 'match-file-items', 'match-btn');
}

function setupDropzone(dropzoneId, inputId, listId, itemsId, btnId) {
    const dropzone = document.getElementById(dropzoneId);
    const input = document.getElementById(inputId);
    const fileList = document.getElementById(listId);
    const fileItems = document.getElementById(itemsId);
    const submitBtn = document.getElementById(btnId);

    if (!dropzone || !input) return;

    // Click to open file dialog
    dropzone.addEventListener('click', (e) => {
        if (e.target.tagName !== 'BUTTON') {
            input.click();
        }
    });

    // Drag events
    ['dragenter', 'dragover'].forEach(event => {
        dropzone.addEventListener(event, (e) => {
            e.preventDefault();
            dropzone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(event => {
        dropzone.addEventListener(event, (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-over');
        });
    });

    // Handle drop
    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length) {
            input.files = files;
            displayFiles(input, fileList, fileItems, submitBtn);
        }
    });

    // Handle file input change
    input.addEventListener('change', () => {
        displayFiles(input, fileList, fileItems, submitBtn);
    });
}

function displayFiles(input, fileList, fileItems, submitBtn) {
    if (!fileList || !fileItems) return;

    const files = input.files;
    fileItems.innerHTML = '';

    if (files.length === 0) {
        fileList.style.display = 'none';
        if (submitBtn) submitBtn.disabled = true;
        return;
    }

    fileList.style.display = 'block';

    Array.from(files).forEach((file, index) => {
        const isValid = isAllowedFile(file.name);
        const item = document.createElement('div');
        item.className = 'file-item';
        item.style.animationDelay = `${index * 0.1}s`;

        const ext = file.name.split('.').pop().toUpperCase();
        const size = formatFileSize(file.size);

        item.innerHTML = `
            <div class="file-item-info">
                <span style="font-size: 1.2rem">${ext === 'PDF' ? '📄' : '📝'}</span>
                <div>
                    <div class="file-item-name" style="color: ${isValid ? 'var(--text-primary)' : 'var(--accent-danger)'}">${file.name}</div>
                    <div class="file-item-size">${size} ${!isValid ? '— Unsupported format' : ''}</div>
                </div>
            </div>
        `;

        fileItems.appendChild(item);
    });

    // Enable/disable submit button
    const hasValidFiles = Array.from(files).some(f => isAllowedFile(f.name));
    if (submitBtn) {
        submitBtn.disabled = !hasValidFiles;

        // Also check if match form needs JD text
        const jdInput = document.getElementById('jd-input');
        if (jdInput) {
            submitBtn.disabled = !hasValidFiles || !jdInput.value.trim();
        }
    }
}

function isAllowedFile(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    return ['pdf', 'docx'].includes(ext);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

/* ═══════════════════════════════════════════════════════════════════════════
   File Input Sync
   ═══════════════════════════════════════════════════════════════════════════ */

function initFileInputs() {
    // Match page: enable button when both JD and files are provided
    const jdInput = document.getElementById('jd-input');
    const matchBtn = document.getElementById('match-btn');
    const matchFileInput = document.getElementById('match-file-input');

    if (jdInput && matchBtn) {
        jdInput.addEventListener('input', () => {
            const hasFiles = matchFileInput && matchFileInput.files.length > 0;
            const hasJD = jdInput.value.trim().length > 0;
            matchBtn.disabled = !(hasFiles && hasJD);
        });
    }
}

/* ═══════════════════════════════════════════════════════════════════════════
   Form Submission with Loading State
   ═══════════════════════════════════════════════════════════════════════════ */

function initFormSubmission() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const btn = form.querySelector('.btn-primary');
            if (!btn) return;

            const btnText = btn.querySelector('.btn-text');
            const btnLoading = btn.querySelector('.btn-loading');

            if (btnText && btnLoading) {
                btnText.style.display = 'none';
                btnLoading.style.display = 'inline-flex';
                btn.disabled = true;
            }
        });
    });
}

/* ═══════════════════════════════════════════════════════════════════════════
   Progress Bar Animations
   ═══════════════════════════════════════════════════════════════════════════ */

function initProgressBars() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const fill = entry.target;
                const width = fill.dataset.width;
                if (width) {
                    setTimeout(() => {
                        fill.style.width = width;
                    }, 200);
                }
                observer.unobserve(fill);
            }
        });
    }, { threshold: 0.3 });

    document.querySelectorAll('.progress-fill').forEach(fill => {
        observer.observe(fill);
    });
}

/* ═══════════════════════════════════════════════════════════════════════════
   Animated Stat Counters
   ═══════════════════════════════════════════════════════════════════════════ */

function initStatCounters() {
    const counters = document.querySelectorAll('.stat-value[data-count]');
    if (!counters.length) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => observer.observe(counter));
}

function animateCounter(element) {
    const target = parseInt(element.dataset.count);
    const duration = 2000;
    const start = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - start;
        const progress = Math.min(elapsed / duration, 1);

        // Ease out quad
        const eased = 1 - (1 - progress) * (1 - progress);
        const current = Math.round(eased * target);

        element.textContent = current.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = target.toLocaleString();
        }
    }

    requestAnimationFrame(update);
}

/* ═══════════════════════════════════════════════════════════════════════════
   Flash Messages Auto-dismiss
   ═══════════════════════════════════════════════════════════════════════════ */

function initFlashMessages() {
    const messages = document.querySelectorAll('.flash-message');
    messages.forEach(msg => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(100px)';
            setTimeout(() => msg.remove(), 400);
        }, 5000);
    });
}

/* ═══════════════════════════════════════════════════════════════════════════
   Character Count for JD Textarea
   ═══════════════════════════════════════════════════════════════════════════ */

function initCharCount() {
    const textarea = document.getElementById('jd-input');
    const counter = document.getElementById('char-count');

    if (textarea && counter) {
        textarea.addEventListener('input', () => {
            counter.textContent = textarea.value.length.toLocaleString();
        });
    }
}
