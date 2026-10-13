/* The page's own drawings on /reference-architecture draw themselves in once,
   the way the talk deck's do: the boundaries' outlines trace in ink and turn
   the accent as the drawing comes into view, then stay. Deferred and
   external, like tabs.js: the deployment CSP allows script-src 'self' and
   nothing inline.

   A progressive enhancement. The drawings ship finished; this script only
   adds .is-armed (which the page's CSS uses, on screens and only without
   reduced motion, to start the outlines undrawn) and then .is-drawn when a
   drawing is a third in view. Readers who ask for reduced motion, and
   browsers without IntersectionObserver, get the finished drawing and no
   script work. */
(function () {
  if (!('IntersectionObserver' in window)) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var figs = document.querySelectorAll('[data-draw]');
  if (!figs.length) return;
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-drawn');
      io.unobserve(e.target);
    });
  }, { threshold: 0.33 });
  Array.prototype.forEach.call(figs, function (f) {
    f.classList.add('is-armed');
    io.observe(f);
  });
})();
