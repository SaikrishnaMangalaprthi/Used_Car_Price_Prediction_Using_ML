/* ===== COUNT-UP ANIMATION ===== */
function animateCount(el, target, duration=1800) {
  const isFloat = target % 1 !== 0;
  const start = performance.now();
  function tick(now) {
    const p = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - p, 3);
    const val = target * eased;
    el.textContent = isFloat ? val.toFixed(2) : Math.floor(val).toLocaleString('en-IN');
    if (p < 1) requestAnimationFrame(tick);
    else el.textContent = isFloat ? target.toFixed(2) : target.toLocaleString('en-IN');
  }
  requestAnimationFrame(tick);
}

/* ===== HERO COUNTERS (run on load) ===== */
document.querySelectorAll('.hero .metric-card .value').forEach(el => {
  const target = parseFloat(el.dataset.count);
  const unit = el.querySelector('.unit');
  const span = document.createElement('span');
  el.innerHTML = '';
  el.appendChild(span);
  if (unit) el.appendChild(unit);
  animateCount(span, target);
});

/* ===== SCROLL REVEAL ===== */
const io = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('show');
      // Trigger count-up inside live metrics
      entry.target.querySelectorAll('[data-count]').forEach(el => {
        if (!el.dataset.done) {
          el.dataset.done = "1";
          animateCount(el, parseFloat(el.dataset.count));
        }
      });
      // Trigger progress bars
      entry.target.querySelectorAll('.fill').forEach(el => {
        el.style.width = el.dataset.fill + '%';
      });
    }
  });
}, { threshold: 0.15 });

document.querySelectorAll('.reveal').forEach(el => io.observe(el));