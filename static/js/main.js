// LoopBack — main.js
// Lightweight utilities, no framework needed.

// ── Auto-dismiss flash messages after 4 seconds ───────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(flash => {
    setTimeout(() => {
      flash.style.transition = 'opacity 0.4s';
      flash.style.opacity = '0';
      setTimeout(() => flash.remove(), 400);
    }, 4000);
  });
});

// ── File input: show selected filename ───────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.querySelector('input[type="file"]');
  if (fileInput) {
    fileInput.addEventListener('change', () => {
      const hint = fileInput.nextElementSibling;
      if (hint && hint.classList.contains('field-hint') && fileInput.files[0]) {
        hint.textContent = 'Selected: ' + fileInput.files[0].name;
      }
    });
  }
});
