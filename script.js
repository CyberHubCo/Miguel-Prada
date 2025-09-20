// Violet Bridge Security LLC — Site Scripts
// Lightweight, no dependencies.

// 1) Current year in footer
(function setYear() {
  const y = document.getElementById('year');
  if (y) y.textContent = new Date().getFullYear();
})();

// 2) Mobile nav toggle
(function mobileNav() {
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.getElementById('site-nav');
  if (!toggle || !nav) return;

  function update(state) {
    const open = state ?? nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
    nav.classList.toggle('open', open);
  }

  toggle.addEventListener('click', () => update());
  // Close menu when clicking a link
  nav.addEventListener('click', (e) => {
    if (e.target instanceof HTMLAnchorElement) update(false);
  });
})();

// 3) Reveal on scroll
(function revealOnScroll() {
  const items = document.querySelectorAll('.reveal');
  if (!('IntersectionObserver' in window) || !items.length) {
    items.forEach(el => el.classList.add('in'));
    return;
  }
  const io = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (entry.isIntersecting) {
        entry.target.classList.add('in');
        io.unobserve(entry.target);
      }
    }
  }, { threshold: 0.1 });
  items.forEach(el => io.observe(el));
})();

// 4) Back to top button
(function backToTop() {
  const btn = document.getElementById('backToTop');
  if (!btn) return;

  const onScroll = () => {
    const y = window.scrollY || document.documentElement.scrollTop;
    btn.classList.toggle('show', y > 400);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();

// 5) Optional: smooth anchor scroll for same-page links
(function smoothAnchors() {
  const links = document.querySelectorAll('a[href^="#"]');
  links.forEach(link => {
    link.addEventListener('click', (e) => {
      const id = decodeURIComponent(link.getAttribute('href') || '').slice(1);
      if (!id) return;
      const target = document.getElementById(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        history.replaceState(null, '', `#${id}`);
      }
    });
  });
})();

