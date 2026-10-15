(() => {
  const tabs = [...document.querySelectorAll('.compare-tab')];
  const panels = [...document.querySelectorAll('.tab-panel')];

  function showTab(name) {
    tabs.forEach((tab) => {
      const active = tab.dataset.tab === name;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
    });
    panels.forEach((panel) => {
      const active = panel.id === `panel-${name}`;
      panel.classList.toggle('is-active', active);
      panel.hidden = !active;
    });
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => showTab(tab.dataset.tab));
    tab.addEventListener('keydown', (event) => {
      if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
      event.preventDefault();
      const next = event.key === 'ArrowRight' ? (index + 1) % tabs.length : (index - 1 + tabs.length) % tabs.length;
      tabs[next].focus();
      showTab(tabs[next].dataset.tab);
    });
  });

  const bars = [...document.querySelectorAll('.chart-bar')];
  const revealBars = () => bars.forEach((bar) => bar.classList.add('is-visible'));
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries, instance) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        revealBars();
        instance.disconnect();
      }
    }, { threshold: 0.35 });
    const chart = document.querySelector('.effect-chart');
    if (chart) observer.observe(chart);
  } else {
    revealBars();
  }

  const navLinks = [...document.querySelectorAll('.top-nav a')];
  const sections = navLinks
    .map((link) => document.querySelector(link.getAttribute('href')))
    .filter(Boolean);
  if ('IntersectionObserver' in window && sections.length) {
    const sectionObserver = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        navLinks.forEach((link) => link.classList.toggle('is-current', link.getAttribute('href') === `#${entry.target.id}`));
      });
    }, { rootMargin: '-28% 0px -62% 0px', threshold: 0 });
    sections.forEach((section) => sectionObserver.observe(section));
  }
})();
