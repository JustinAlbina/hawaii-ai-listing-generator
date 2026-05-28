/* ── AlohaAgent Shared JS ── */
(function () {
  'use strict';

  /* ── Task 4: Cinematic Results Reveal ── */
  function initReveal() {
    var sections = document.querySelectorAll('.reveal-section');
    if (!sections.length) return;
    sections.forEach(function (el, i) {
      setTimeout(function () {
        el.classList.add('revealed');
      }, i * 300);
    });
  }

  /* ── Task 5: Form Field Fade-in via IntersectionObserver ── */
  function initFieldFadeIn() {
    var forms = document.querySelectorAll('.aloha-form');
    if (!forms.length) return;

    document.body.classList.add('aa-anim');

    if (!('IntersectionObserver' in window)) {
      // Fallback: show all fields immediately
      document.querySelectorAll('.aloha-form .form-group').forEach(function (g) {
        g.classList.add('field-visible');
      });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('field-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -40px 0px', threshold: 0.05 });

    document.querySelectorAll('.aloha-form .form-group').forEach(function (g) {
      observer.observe(g);
    });
  }

  /* ── Task 5: Gold Checkmark + Button Pulse ── */
  function initFormFeedback() {
    var forms = document.querySelectorAll('.aloha-form');
    if (!forms.length) return;

    forms.forEach(function (form) {
      // Inject checkmark span into every form-group
      form.querySelectorAll('.form-group').forEach(function (group) {
        var check = document.createElement('span');
        check.className = 'field-checkmark';
        check.setAttribute('aria-hidden', 'true');
        check.textContent = '✓';
        group.appendChild(check);
      });

      // Field validity check
      function isFieldValid(field) {
        if (field.type === 'hidden' || field.type === 'file') return false;
        if (field.type === 'checkbox') return field.checked;
        return field.value.trim() !== '';
      }

      function updateGroup(field) {
        var group = field.closest('.form-group');
        if (!group) return;
        var valid = isFieldValid(field);
        group.classList.toggle('field-valid', valid);
      }

      function updateButton() {
        var btn = form.querySelector('.btn-submit');
        if (!btn) return;
        var allFilled = true;
        form.querySelectorAll('[required]').forEach(function (field) {
          if (!isFieldValid(field)) allFilled = false;
        });
        btn.classList.toggle('btn-ready', allFilled);
      }

      // Watch all fields
      form.querySelectorAll('input, select, textarea').forEach(function (field) {
        field.addEventListener('input', function () { updateGroup(field); updateButton(); });
        field.addEventListener('change', function () { updateGroup(field); updateButton(); });
        // Run once on load in case of pre-filled values
        updateGroup(field);
      });
      updateButton();

      // Loading state on submit
      form.addEventListener('submit', function () {
        var btn = form.querySelector('.btn-submit');
        if (btn) {
          btn.classList.remove('btn-ready');
          btn.classList.add('btn-loading');
          btn.disabled = true;
        }
      });
    });
  }

  /* ── Task 5: Photo Upload Enhancements ── */
  function initPhotoEnhancements() {
    var dropZone = document.getElementById('photo-drop-zone');
    var thumbsContainer = document.getElementById('photo-thumbs');
    if (!dropZone || !thumbsContainer) return;

    // Enhanced drag-over (already handles .drag-over in CSS; ensure the class toggling is present)
    // The existing listing.html JS handles drag events — we piggyback on MutationObserver
    // to add entrance animation to newly created thumbnails
    var mo = new MutationObserver(function (mutations) {
      mutations.forEach(function (m) {
        m.addedNodes.forEach(function (node) {
          if (node.nodeType === 1 && node.classList.contains('photo-thumb')) {
            node.classList.add('thumb-enter');
            // Add file-size label if not already present
            if (!node.querySelector('.thumb-size')) {
              var sizeEl = document.createElement('div');
              sizeEl.className = 'thumb-size';
              // Get size from data attribute if available
              var kb = node.dataset.kb;
              sizeEl.textContent = kb ? kb + ' KB' : '';
              node.parentNode.insertBefore(sizeEl, node.nextSibling);
            }
          }
        });
      });
    });
    mo.observe(thumbsContainer, { childList: true });
  }

  /* ── Boot ── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  function boot() {
    initReveal();
    initFieldFadeIn();
    initFormFeedback();
    initPhotoEnhancements();
  }
})();
