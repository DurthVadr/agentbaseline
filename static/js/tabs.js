/* Tabs for the levels of autonomy on /reference-architecture. Deferred and
   external, like logo-menu.js: the deployment CSP allows script-src 'self'
   and nothing inline.

   A progressive enhancement. The markup ships every level as its own
   section, under its own heading, with the row of steps hidden; without
   this script (and in print) the levels read stacked. This script shows the
   steps, gives them and the sections their tab roles, and shows one level
   at a time.

   The tabs follow the ARIA tabs pattern with automatic activation: arrow
   keys move between the steps and select as they go, Home and End go to
   the first and last, and only the selected step is in the tab order. */
(function () {
  var roots = document.querySelectorAll('[data-tabs]');
  Array.prototype.forEach.call(roots, function (root) {
    var list = root.querySelector('[data-tablist]');
    if (!list) return;
    var tabs = Array.prototype.slice.call(list.querySelectorAll('[data-tab]'));
    var panels = tabs.map(function (t) {
      return document.getElementById(t.getAttribute('aria-controls'));
    });
    /* A step without its section would select nothing; leave the stacked
       levels alone rather than half-build the tabs. */
    if (!tabs.length || panels.some(function (p) { return !p; })) return;

    list.setAttribute('role', 'tablist');
    tabs.forEach(function (tab, i) {
      tab.setAttribute('role', 'tab');
      var panel = panels[i];
      panel.setAttribute('role', 'tabpanel');
      panel.setAttribute('aria-labelledby', tab.id);
      panel.tabIndex = 0;
      tab.addEventListener('click', function () { select(i, false); });
      tab.addEventListener('keydown', function (e) {
        var to = null, last = tabs.length - 1;
        if (e.key === 'ArrowRight') to = i === last ? 0 : i + 1;
        else if (e.key === 'ArrowLeft') to = i === 0 ? last : i - 1;
        else if (e.key === 'Home') to = 0;
        else if (e.key === 'End') to = last;
        if (to === null) return;
        e.preventDefault();
        select(to, true);
      });
    });

    function select(n, focus) {
      tabs.forEach(function (tab, i) {
        var on = i === n;
        tab.setAttribute('aria-selected', on ? 'true' : 'false');
        tab.tabIndex = on ? 0 : -1;
        panels[i].hidden = !on;
      });
      if (focus) tabs[n].focus();
    }

    select(0, false);
    list.hidden = false;
    root.classList.add('is-tabbed');
  });
})();
