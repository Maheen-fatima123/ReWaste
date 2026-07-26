// ReWaste — main.js
// Lightweight utilities, no framework needed.

// ── Mobile nav toggle ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('menuToggle');
  const menu = document.getElementById('mobileMenu');
  const iconOpen = document.getElementById('menuIconOpen');
  const iconClose = document.getElementById('menuIconClose');

  if (toggle && menu) {
    toggle.addEventListener('click', () => {
      const isHidden = menu.classList.contains('hidden');
      menu.classList.toggle('hidden');
      toggle.setAttribute('aria-expanded', String(isHidden));
      if (iconOpen && iconClose) {
        iconOpen.classList.toggle('hidden');
        iconClose.classList.toggle('hidden');
      }
    });
  }
});

// ── Auto-dismiss flash toasts after 4 seconds ───────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach((flash, i) => {
    setTimeout(() => {
      flash.style.transition = 'opacity 0.4s, transform 0.4s';
      flash.style.opacity = '0';
      flash.style.transform = 'translateX(12px)';
      setTimeout(() => flash.remove(), 400);
    }, 4000 + i * 150);
  });
});

// ── File inputs: show selected filename next to the field hint ─────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('input[type="file"]').forEach((fileInput) => {
    fileInput.addEventListener('change', () => {
      const hint = fileInput.parentElement.querySelector('.field-hint');
      if (hint && fileInput.files[0]) {
        hint.textContent = 'Selected: ' + fileInput.files[0].name;
      }
    });
  });
});

// ── Sticky nav shadow on scroll ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const header = document.querySelector('header');
  if (!header) return;
  window.addEventListener('scroll', () => {
    if (window.scrollY > 4) {
      header.classList.add('shadow-sm');
    } else {
      header.classList.remove('shadow-sm');
    }
  });
});
