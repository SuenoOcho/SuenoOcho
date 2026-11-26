(function () {
  'use strict';

  var root = document.documentElement;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  var loader = document.getElementById('loader');
  var loaderFill = document.getElementById('loaderFill');
  var loaderPercent = document.getElementById('loaderPercent');
  var toast = document.getElementById('toast');
  var toastTitle = document.getElementById('toastTitle');
  var toastText = document.getElementById('toastText');
  var toastClose = document.getElementById('toastClose');
  var navToggle = document.getElementById('navToggle');
  var nav = document.getElementById('siteNav');
  var year = document.getElementById('year');

  var toastTimer;
  var finished = false;

  function showToast(title, text) {
    if (!toast) return;
    if (toastTitle) toastTitle.textContent = title;
    if (toastText) toastText.textContent = text;
    toast.hidden = false;
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(hideToast, 6000);
  }

  function hideToast() {
    if (!toast) return;
    toast.hidden = true;
    window.clearTimeout(toastTimer);
  }

  if (toastClose) toastClose.addEventListener('click', hideToast);

  function setProgress(value) {
    if (loaderFill) loaderFill.style.width = value + '%';
    if (loaderPercent) loaderPercent.textContent = value + '%';
  }

  function finishLoader() {
    if (finished) return;
    finished = true;
    setProgress(100);
    window.setTimeout(function () {
      if (loader) loader.classList.add('is-done');
      showToast('Welcome, explorer!', 'Your world is ready. Use the map to start exploring.');
    }, reduceMotion.matches ? 0 : 260);
  }

  if (loader) {
    var progress = 0;
    var pageLoaded = document.readyState === 'complete';
    var duration = reduceMotion.matches ? 60 : 900;
    var start = performance.now();

    window.addEventListener('load', function () {
      pageLoaded = true;
      progress = Math.max(progress, 92);
    });

    window.setTimeout(function () {
      pageLoaded = true;
      progress = 100;
    }, reduceMotion.matches ? 80 : 1800);

    function tick(now) {
      var target = pageLoaded ? 100 : Math.min(92, Math.round(((now - start) / duration) * 92));
      progress = Math.max(progress, target);
      setProgress(progress);
      if (progress >= 100) finishLoader();
      else window.requestAnimationFrame(tick);
    }

    window.requestAnimationFrame(tick);
  }

  root.setAttribute('data-theme', 'night');
  var themeMeta = document.querySelector('meta[name="theme-color"]');
  if (themeMeta) themeMeta.setAttribute('content', '#0b1a10');

  function setNav(open) {
    if (!nav || !navToggle) return;
    nav.classList.toggle('is-open', open);
    navToggle.setAttribute('aria-expanded', String(open));
    navToggle.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
  }

  if (navToggle && nav) {
    navToggle.addEventListener('click', function () {
      setNav(!nav.classList.contains('is-open'));
    });

    nav.addEventListener('click', function (event) {
      if (event.target.closest('a')) setNav(false);
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && nav.classList.contains('is-open')) {
        setNav(false);
        navToggle.focus();
      }
    });

    document.addEventListener('click', function (event) {
      if (nav.classList.contains('is-open') && !nav.contains(event.target) && !navToggle.contains(event.target)) {
        setNav(false);
      }
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 900) setNav(false);
    });
  }

  var reveals = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  function showAll() {
    reveals.forEach(function (element) { element.classList.add('is-visible'); });
  }

  if (!('IntersectionObserver' in window) || reduceMotion.matches) {
    showAll();
  } else {
    var revealObserver = new IntersectionObserver(function (entries, observer) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    reveals.forEach(function (element) { revealObserver.observe(element); });
  }

  if ('IntersectionObserver' in window) {
    var sections = Array.prototype.slice.call(document.querySelectorAll('main section[id]'));
    var navLinks = nav ? Array.prototype.slice.call(nav.querySelectorAll('a[href^="#"]')) : [];
    var sectionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        navLinks.forEach(function (link) {
          link.classList.toggle('is-active', link.getAttribute('href') === '#' + entry.target.id);
        });
      });
    }, { rootMargin: '-42% 0px -52% 0px' });

    sections.forEach(function (section) { sectionObserver.observe(section); });
  }

  if (reduceMotion.addEventListener) {
    reduceMotion.addEventListener('change', function () {
      if (reduceMotion.matches) showAll();
      if (reduceMotion.matches && loader) loader.classList.add('is-done');
    });
  }

  var projectGrid = document.getElementById('projectGrid');
  var projectsNoticeText = document.getElementById('projectsNoticeText');
  var projectsSubtitle = document.getElementById('projectsSubtitle');

  function createRepoCard(repo) {
    var card = document.createElement('li');
    card.className = 'project-card reveal is-visible';

    var icon = document.createElement('div');
    icon.className = 'project-icon';
    icon.setAttribute('aria-hidden', 'true');
    icon.textContent = repo.fork ? '⑂' : '▦';

    var badge = document.createElement('span');
    badge.className = 'project-badge is-live';
    badge.textContent = repo.fork ? 'FORKED REPO' : 'PUBLIC REPO';

    var title = document.createElement('h3');
    title.textContent = String(repo.name || 'untitled-repo').replace(/-/g, ' ');

    var description = document.createElement('p');
    description.textContent = repo.description || 'No description added on GitHub yet.';

    var tags = document.createElement('ul');
    tags.className = 'tag-list';
    if (repo.language) {
      var language = document.createElement('li');
      language.textContent = repo.language;
      tags.appendChild(language);
    }
    var stars = document.createElement('li');
    stars.textContent = '★ ' + (repo.stargazers_count || 0);
    tags.appendChild(stars);

    var link = document.createElement('a');
    link.className = 'link-slot';
    link.href = /^https:\/\/github\.com\//.test(repo.html_url || '') ? repo.html_url : 'https://github.com/SuenoOcho';
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.textContent = 'OPEN REPOSITORY ↗';

    card.appendChild(icon);
    card.appendChild(badge);
    card.appendChild(title);
    card.appendChild(description);
    card.appendChild(tags);
    card.appendChild(link);
    return card;
  }

  function loadRepos() {
    if (!projectGrid || !window.fetch) return;

    if (projectsNoticeText) {
      projectsNoticeText.innerHTML = '<strong>LOADING BUILDS:</strong> gathering the receipts...';
    }

    fetch('https://api.github.com/users/SuenoOcho/repos?per_page=100&sort=updated', {
      headers: { 'Accept': 'application/vnd.github+json' }
    })
      .then(function (response) {
        if (!response.ok) throw new Error('GitHub API returned ' + response.status);
        return response.json();
      })
      .then(function (repos) {
        if (!Array.isArray(repos)) return;
        var builds = repos.filter(function (repo) {
          return !repo.archived && repo.name.toLowerCase() !== 'suenoocho';
        }).slice(0, 6);
        if (!builds.length) return;

        while (projectGrid.firstChild) projectGrid.removeChild(projectGrid.firstChild);
        builds.forEach(function (repo) { projectGrid.appendChild(createRepoCard(repo)); });

        if (projectsNoticeText) {
          projectsNoticeText.innerHTML = '<strong>PROOF OF WORK:</strong> the repo doesn\'t lie.';
        }
        if (projectsSubtitle) {
          projectsSubtitle.textContent = 'Proof lives in the repo.';
        }
      })
      .catch(function () {
        if (projectsNoticeText) {
          projectsNoticeText.innerHTML = '<strong>NO DRAFTS HERE:</strong> even the connection needs a warm-up.';
        }
      });
  }

  loadRepos();

  if (year) year.textContent = String(new Date().getFullYear());
})();
