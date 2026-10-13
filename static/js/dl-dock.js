/* The reference architecture's download button. The title block carries it
   top right; once that copy has scrolled up under the bar, the bar shows its
   own (a.dl-btn.dock), and hides it again on the way back up. Only when the
   title block's button is above the bar's edge, not below the viewport, so a
   reader who lands on #authors and scrolls up does not see two.

   Measured against the observer's own top edge (the bar's bottom), not the
   viewport's: the button leaves the observed area while still a few pixels
   below the viewport top, under the bar, and that is the last callback it
   gets on the way up. The bar wraps to more rows on narrow screens, so the
   observer is rebuilt with the bar's new height on resize.

   External, not inline, because the deployment CSP allows script-src 'self'
   only. */
(function () {
  addEventListener('DOMContentLoaded', function () {
    var src = document.getElementById('dl-paper');
    var dock = document.querySelector('.utility a.dl-btn.dock');
    if (!src || !dock || !('IntersectionObserver' in window)) return;
    var bar = document.querySelector('nav.utility');
    var io, h = -1;
    function watch() {
      var nh = bar ? bar.offsetHeight : 0;
      if (nh === h) return;
      h = nh;
      if (io) io.disconnect();
      io = new IntersectionObserver(function (entries) {
        var en = entries[entries.length - 1];
        var edge = en.rootBounds ? en.rootBounds.top : h;
        dock.hidden = en.isIntersecting || en.boundingClientRect.top > edge;
      }, { rootMargin: '-' + h + 'px 0px 0px 0px' });
      io.observe(src);
    }
    watch();
    addEventListener('resize', watch);
  });
})();
