(function () {
  'use strict';

  var TG = 'dunai_dunai';
  var TG_URL = 'https://t.me/' + TG;

  var root = document.documentElement;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var clamp = function (v, a, b) { return Math.min(b === undefined ? 1 : b, Math.max(a || 0, v)); };
  var ease = function (t) { return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
  var lang = function () { return root.getAttribute('data-lang') === 'en' ? 'en' : 'ru'; };
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------- language ---------- */
  function setLang(l) {
    root.setAttribute('data-lang', l);
    root.setAttribute('lang', l);
    document.title = l === 'en' ? 'Interior design for flats in Moscow — DUNAEVA BUREAU' : 'Дизайн интерьера квартир в Москве — DUNAEVA BUREAU';
    try { localStorage.setItem('db-lang', l); } catch (e) { /* storage unavailable */ }
    document.dispatchEvent(new Event('langchange'));
  }
  try { var saved = localStorage.getItem('db-lang'); if (saved === 'en' || saved === 'ru') setLang(saved); } catch (e) { /* storage unavailable */ }
  $('#lang').addEventListener('click', function () { setLang(lang() === 'ru' ? 'en' : 'ru'); });

  /* ---------- menu ---------- */
  var burger = $('#burger');
  burger.addEventListener('click', function () {
    var open = document.body.classList.toggle('menu-open');
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  $$('#nav a').forEach(function (a) { a.addEventListener('click', function () { document.body.classList.remove('menu-open'); burger.setAttribute('aria-expanded', 'false'); }); });

  /* ---------- copy text, then open Telegram ---------- */
  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text).then(function () { return true; }, function () { return false; });
    try {
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      var ok = document.execCommand('copy');
      document.body.removeChild(ta);
      return Promise.resolve(ok);
    } catch (e) { return Promise.resolve(false); }
  }
  function sendToTelegram(text, noteEl) {
    // A personal chat link can't carry text, so the message goes to the clipboard first,
    // started inside the click so the browser allows it, then Telegram opens.
    var copied = copy(text);
    var win = window.open(TG_URL, '_blank');
    if (win) win.opener = null;
    copied.then(function (ok) {
      if (noteEl) {
        noteEl.hidden = false;
        noteEl.textContent = ok
          ? (lang() === 'en' ? 'The message is copied — paste it into the chat with @' + TG + '.' : 'Текст заявки скопирован — вставьте его в чат с @' + TG + '.')
          : (lang() === 'en' ? 'Copy this text and send it to @' + TG + ':\n\n' + text : 'Скопируйте этот текст и отправьте @' + TG + ':\n\n' + text);
      }
      if (!win) location.href = TG_URL;
    });
  }

  /* ---------- intro: the camera walks through the doorway of the mark ---------- */
  var intro = $('.intro'), stage = $('#introStage'), mark = $('#introMark'), words = $('#introWords'), doorLight = $('#doorLight'), scrollHint = $('#introScroll');
  var hd = $('#hd'), fab = $('#fab'), figWrap = $('#figWrap');
  var zoomMax = 10;
  mark.classList.add('play');

  function measureIntro() {
    mark.style.transform = 'none';
    var r = mark.getBoundingClientRect();
    // the doorway is 72×56 of the 120×72 viewBox, centred on the mark's centre
    var doorW = r.width * 72 / 120, doorH = r.height * 56 / 72;
    zoomMax = Math.max(innerWidth / doorW, innerHeight / doorH) * 1.25;
    markOffset = innerHeight / 2 - (r.top + r.height / 2);
  }
  var markOffset = 0;

  function drawAxes() {
    var axes = $('#axes'); axes.innerHTML = '';
    var w = stage.clientWidth, h = stage.clientHeight, L = 'ABCDEFGHIJ', k = 0, n = 1, x, y, d;
    for (x = 200; x < w - 30; x += 200) { d = document.createElement('div'); d.className = 'axis'; d.style.left = (x - 11) + 'px'; d.style.top = (h - 44) + 'px'; d.textContent = L[k++ % L.length]; axes.appendChild(d); }
    for (y = 200; y < h - 70; y += 200) { d = document.createElement('div'); d.className = 'axis'; d.style.left = '20px'; d.style.top = (y - 11) + 'px'; d.textContent = n++; axes.appendChild(d); }
  }

  function introProgress() {
    var span = intro.offsetHeight - innerHeight;
    return span > 0 ? clamp(scrollY / span) : 1;
  }

  function updateIntro() {
    var p = reduce ? 0 : introProgress();
    // 1. words step back
    var w = clamp(p / .22);
    words.style.opacity = String(1 - w);
    words.style.transform = 'translate3d(0,' + (w * 40) + 'px,0) scale(' + (1 - w * .06) + ')';
    scrollHint.style.opacity = String(1 - clamp(p / .1));
    // the figure steps aside as we pass the doorway
    figWrap.setAttribute('opacity', (1 - clamp((p - .5) / .25)).toFixed(3));
    // 2. light comes on in the doorway
    doorLight.setAttribute('opacity', (clamp((p - .08) / .3) * 1).toFixed(3));
    // 3. walk through: geometric zoom feels like constant speed
    var z = ease(clamp((p - .12) / .8));
    var s = Math.pow(zoomMax, z);
    mark.style.transform = 'translate3d(0,' + (markOffset * clamp(z * 3)) + 'px,0) scale(' + s.toFixed(4) + ')';
    // header turns solid once we are through
    var past = p >= .97 || scrollY > intro.offsetHeight - innerHeight;
    hd.classList.toggle('is-solid', past);
    hd.classList.toggle('show-logo', past);
  }

  /* ---------- scroll-driven bits ---------- */
  var opens = $$('[data-open]');
  var texs = $$('.tex');
  var frames = $$('.viewer__frame');
  var stagesEl = $('#stages'), stageItems = $$('.st');
  var contact = $('#contact');
  var sections = $$('main section[id]');
  var navLinks = $$('#nav a');

  function onScroll() {
    updateIntro();
    var vh = innerHeight;

    // indigo bands open like a door: from a slit to full width
    opens.forEach(function (el) {
      var r = el.getBoundingClientRect();
      var t = reduce ? 1 : ease(clamp((vh - r.top) / (vh * .75)));
      el.style.setProperty('--cx', ((1 - t) * 38).toFixed(2) + '%');
      el.style.setProperty('--cy', ((1 - t) * 6).toFixed(2) + '%');
    });

    // project images drift inside their frames — depth
    if (!reduce) frames.forEach(function (f) {
      var r = f.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      var k = (r.top + r.height / 2 - vh / 2) / vh;
      f.style.setProperty('--py', (k * -40).toFixed(1) + 'px');
      $$('.v-img', f).forEach(function (i) { i.style.setProperty('--py', (k * -40).toFixed(1) + 'px'); });
    });

    // textures float at different depths
    if (!reduce && innerWidth > 860) texs.forEach(function (t) {
      var r = t.getBoundingClientRect();
      if (r.bottom < -200 || r.top > vh + 200) return;
      var k = (r.top + r.height / 2 - vh / 2);
      t.style.transform = 'translate3d(0,' + (k * -(+t.dataset.depth || 0)).toFixed(1) + 'px,0)';
    });

    // the route through the stages draws as you read
    if (stagesEl) {
      var sr = stagesEl.getBoundingClientRect();
      var prog = clamp((vh * .6 - sr.top) / sr.height);
      stagesEl.style.setProperty('--route', prog.toFixed(3));
      stageItems.forEach(function (li) { li.classList.toggle('on', li.getBoundingClientRect().top < vh * .6); });
    }

    // sticky Telegram button: after the intro, hidden over the contact block
    var cr = contact.getBoundingClientRect();
    fab.classList.toggle('show', scrollY > intro.offsetHeight - vh * .5 && cr.top > vh * .7);

    // active menu item
    var cur = null;
    sections.forEach(function (s) { if (s.getBoundingClientRect().top < vh * .4) cur = s.id; });
    navLinks.forEach(function (a) { a.classList.toggle('on', a.getAttribute('href') === '#' + cur); });
  }

  var ticking = false;
  addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(function () { ticking = false; onScroll(); }); }
  }, { passive: true });
  addEventListener('resize', function () { measureIntro(); drawAxes(); onScroll(); });

  /* ---------- reveal on enter ---------- */
  var revealEls = $$('.rv, [data-scene], [data-reveal]');
  if ('IntersectionObserver' in window && !reduce) {
    // a fully clipped element has no visible area, so clipped ones are watched through a wrapper
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { (e.target._rv || e.target).classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: .18, rootMargin: '0px 0px -6% 0px' });
    revealEls.forEach(function (el) {
      if (el.hasAttribute('data-reveal')) { var w = el.parentElement; w._rv = el; io.observe(w); }
      else io.observe(el);
    });
    // stagger siblings a little
    $$('.terms, .refs-row, .balance, .facts').forEach(function (g) { $$('.rv', g).forEach(function (el, i) { el.style.transitionDelay = (i * .09) + 's'; }); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  // the figure walks into the doorway again at the contact block — an invitation
  var cMark = $('#contactMark');
  if ('IntersectionObserver' in window) {
    var io2 = new IntersectionObserver(function (es) {
      if (es[0].isIntersecting) { cMark.classList.add('play'); io2.disconnect(); }
    }, { threshold: .5 });
    io2.observe(cMark);
  } else cMark.classList.add('play');

  /* ---------- project viewers: images wipe in ---------- */
  $$('[data-viewer]').forEach(function (v) {
    var tabs = $$('.tab', v), imgs = $$('.v-img', v);
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () {
        if (t.classList.contains('on')) return;
        tabs.forEach(function (o) { o.classList.remove('on'); o.setAttribute('aria-selected', 'false'); });
        t.classList.add('on'); t.setAttribute('aria-selected', 'true');
        imgs.forEach(function (im) { im.classList.remove('out'); if (im.classList.contains('on')) { im.classList.remove('on'); im.classList.add('out'); } });
        imgs[i].classList.add('on');
      });
    });
  });

  /* ---------- one day on the plan ---------- */
  var TL = {"A": {"stops": [0.0, 0.030040205655762733, 0.31440181112063686, 0.5334374675573228, 0.7614558664911423, 0.8568489503411552, 0.9464018313472611, 0.9999999999999999], "walk": 7.0}, "B": {"stops": [0.0, 0.04320913778258707, 0.12140823717197209, 0.35718603277620187, 0.4591129976836619, 0.5068240847060064, 0.7513235533574025, 1.0], "walk": 9.0}, "LM": [["7:00", "подъём", "wake up"], ["7:05", "шторы", "curtains"], ["7:10", "душ", "shower"], ["7:30", "кофе", "coffee"], ["7:45", "макияж", "make-up"], ["7:55", "гардеробная", "dressing"], ["8:05", "обувь", "shoes"], ["8:10", "выход", "out"]], "LE": [null, ["19:00", "дома", "home"], ["19:10", "переодеться", "change"], ["19:40", "ужин", "dinner"], ["21:00", "кино", "a film"], ["22:00", "книга", "a book"], ["22:40", "душ", "shower"], ["23:00", "сон", "sleep"]]};
  (function () {
    var svg = $('.band .plan'); if (!svg) return;
    var band = $('#dayBand'), walker = $('#walker');
    var paths = [$('#routeA'), $('#routeB')];
    var lens = paths.map(function (p) { return p.getTotalLength(); });
    var tails = [svg.querySelectorAll('.tail[data-r="0"]'), svg.querySelectorAll('.tail[data-r="1"]')];
    var clockT = $('#clockTime'), clockA = $('#clockAct'), track = $('#track');
    var routes = [{ stops: TL.A.stops, walk: TL.A.walk * .9, lab: TL.LM }, { stops: TL.B.stops, walk: TL.B.walk * .9, lab: TL.LE }];
    var PAUSE = .45, GAP = .45;
    var items = [];
    routes.forEach(function (R, r) {
      if (r === 1) { var g = document.createElement('li'); g.className = 'gap'; g.setAttribute('aria-hidden', 'true'); g.textContent = '···'; track.appendChild(g); }
      R.lab.forEach(function (l, i) {
        if (!l) return;
        var li = document.createElement('li');
        li.innerHTML = '<span class="t">' + l[0] + '</span><span class="w"><span class="ru">' + l[1] + '</span><span class="en">' + l[2] + '</span></span>';
        li.setAttribute('role', 'button'); li.tabIndex = 0; li.setAttribute('aria-label', l[0] + ' ' + l[1]);
        li.addEventListener('click', function () { jumpTo(r, i); });
        li.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); jumpTo(r, i); } });
        track.appendChild(li); items.push({ r: r, i: i, el: li });
      });
    });
    function each(list, fn) { Array.prototype.forEach.call(list, fn); }
    function pos(r, f) { var pt = paths[r].getPointAtLength(f * lens[r]); walker.setAttribute('cx', pt.x); walker.setAttribute('cy', pt.y); }
    function trail(r, f) {
      for (var q = 0; q < 2; q++) each(tails[q], function (t) {
        if (q !== r) { t.setAttribute('stroke-dasharray', '0 2'); return; }
        var w = +t.getAttribute('data-w'), d = Math.min(w, f);
        t.setAttribute('stroke-dasharray', d + ' 2'); t.setAttribute('stroke-dashoffset', String(d - f));
      });
    }
    function setClock(t, ru, en) { clockT.textContent = t; clockA.innerHTML = '<span class="ru">' + ru + '</span><span class="en">' + en + '</span>'; }
    function jumpTo(r, i) {
      if (raf) { cancelAnimationFrame(raf); raf = null; }
      var f = routes[r].stops[i], l = routes[r].lab[i];
      pos(r, f); trail(r, f); walker.setAttribute('opacity', '1');
      each(svg.querySelectorAll('.tl'), function (g) { g.style.opacity = (+g.getAttribute('data-r') === r && +g.getAttribute('data-i') === i) ? '1' : '.4'; });
      if (l) setClock(l[0], l[1], l[2]);
      items.forEach(function (it) { it.el.classList.add('on'); it.el.classList.toggle('now', it.r === r && it.i === i); });
    }
    var phases = [];
    routes.forEach(function (R, r) {
      if (r === 1) phases.push({ type: 'gap', dur: GAP });
      R.stops.forEach(function (f, i) {
        if (i > 0) phases.push({ type: 'move', r: r, i: i, f0: R.stops[i - 1], f1: f, dur: Math.max(.2, (f - R.stops[i - 1]) * R.walk) });
        phases.push({ type: 'hold', r: r, i: i, dur: PAUSE });
      });
    });
    function arrive(r, i) {
      var l = routes[r].lab[i]; if (!l) return;
      each(svg.querySelectorAll('.tl'), function (g) { if (g.style.opacity === '1') g.style.opacity = '.4'; });
      var g = svg.querySelector('.tl[data-r="' + r + '"][data-i="' + i + '"]'); if (g) g.style.opacity = '1';
      setClock(l[0], l[1], l[2]);
      items.forEach(function (it) { it.el.classList.remove('now'); if (it.r === r && it.i === i) it.el.classList.add('on', 'now'); });
    }
    function reset() {
      each(svg.querySelectorAll('.tl'), function (g) { g.style.opacity = '0'; });
      tails.forEach(function (T) { each(T, function (t) { t.setAttribute('stroke-dasharray', '0 2'); }); });
      items.forEach(function (it) { it.el.classList.remove('on', 'now'); });
      walker.setAttribute('opacity', '0');
    }
    function finish() {
      each(svg.querySelectorAll('.tl'), function (g) { g.style.opacity = '1'; });
      tails.forEach(function (T) { each(T, function (t) { t.setAttribute('stroke-dasharray', '0 2'); }); });
      items.forEach(function (it) { it.el.classList.add('on'); it.el.classList.remove('now'); });
      if (items.length) items[items.length - 1].el.classList.add('now');
      pos(1, 1); walker.setAttribute('opacity', '1');
      var l = routes[1].lab[routes[1].lab.length - 1]; setClock(l[0], l[1], l[2]);
    }
    var raf = null, t0 = 0, k = 0, arrived = -1;
    function frame(now) {
      if (!t0) t0 = now; var t = (now - t0) / 1000;
      while (k < phases.length && t > phases[k].dur) { t -= phases[k].dur; t0 += phases[k].dur * 1000; k++; }
      if (k >= phases.length) { raf = null; walker.setAttribute('opacity', '1'); trail(1, 1); return; }
      var ph = phases[k];
      if (ph.type === 'hold') {
        var f = routes[ph.r].stops[ph.i]; pos(ph.r, f); trail(ph.r, f);
        if (arrived !== k) { arrived = k; arrive(ph.r, ph.i); }
        walker.setAttribute('opacity', '1');
      } else if (ph.type === 'move') {
        var e = t / ph.dur; e = e < .5 ? 2 * e * e : 1 - Math.pow(-2 * e + 2, 2) / 2;
        var f2 = ph.f0 + (ph.f1 - ph.f0) * e; pos(ph.r, f2); trail(ph.r, f2); walker.setAttribute('opacity', '1');
      } else {
        var u = t / ph.dur; walker.setAttribute('opacity', String(Math.abs(1 - 2 * u))); trail(0, 1.5); if (u > .5) pos(1, 0);
        if (arrived !== k) { arrived = k; setClock('8:10 – 19:00', 'в городе', 'out in the city'); items.forEach(function (it) { it.el.classList.remove('now'); }); }
      }
      raf = requestAnimationFrame(frame);
    }
    function play() { if (raf) cancelAnimationFrame(raf); reset(); if (reduce) { finish(); return; } t0 = 0; k = 0; arrived = -1; raf = requestAnimationFrame(frame); }
    $('#replay').addEventListener('click', play);
    if (reduce) finish();
    else if ('IntersectionObserver' in window) {
      var io3 = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { play(); io3.disconnect(); } }); }, { threshold: .35 });
      io3.observe(band);
    } else play();
  })();

  /* ---------- fee calculator (all prices live here) ---------- */
  (function () {
    var PRICES = {
      min: 60000,                               // minimum project fee, ₽
      supervision: { perM2: 400, min: 35000 },  // per month, Moscow and region only
      tariffs: [
        { id: 'plan', price: 1500, online: true, ru: 'Сценарий и планировка', en: 'Scenario and layout',
          dru: 'Анкета, обмер, сценарий жизни, варианты планировки и расстановка мебели с размерами.', den: 'Questionnaire, survey, scenario of life, layout options and a dimensioned furniture plan.',
          inc: [['Анкета, встреча и обмер', 'Questionnaire, meeting and survey'], ['Сценарий жизни: как проходит день в доме', 'Scenario of life: how a day unfolds at home'], ['2–3 варианта планировки', '2–3 layout options'], ['Расстановка мебели с размерами', 'Dimensioned furniture plan']],
          incOnline: [['Анкета и видеовстреча', 'Questionnaire and a video call'], ['Сценарий жизни: как проходит день в доме', 'Scenario of life: how a day unfolds at home'], ['2–3 варианта планировки', '2–3 layout options'], ['Расстановка мебели с размерами', 'Dimensioned furniture plan']],
          stages: [[1, 'Сценарий и планировка', 'Scenario and layout']] },
        { id: 'concept', price: 3500, online: true, ru: 'Концепция', en: 'Concept',
          dru: 'Всё из планировки плюс образ интерьера: коллажи в технике бюро, материалы, цвет и свет.', den: 'Everything in the layout plus the look: collages in the bureau’s technique, materials, colour and light.',
          inc: [['Всё из этапа «Сценарий и планировка»', 'Everything in “Scenario and layout”'], ['Мудборд и коллажи в технике бюро', 'Moodboard and collages in the bureau’s technique'], ['Подбор материалов, фактур и цвета', 'Materials, textures and colour'], ['Концепция света и подбор мебели', 'Lighting concept and furniture selection']],
          stages: [[.5, 'Сценарий и планировка', 'Scenario and layout'], [.5, 'Концепция', 'Concept']] },
        { id: 'full', price: 5500, ru: 'Полный проект', en: 'Full project',
          dru: 'Концепция и рабочие чертежи, по которым строители сделают ровно то, что задумано.', den: 'Concept plus working drawings, so the builders deliver exactly what was designed.',
          inc: [['Всё из этапа «Концепция»', 'Everything in “Concept”'], ['Обмерный, демонтажный и монтажный планы', 'Survey, demolition and construction plans'], ['Полы, потолки, электрика, свет и сантехника', 'Floors, ceilings, electrics, lighting and plumbing'], ['Развёртки стен и раскладка плитки', 'Wall elevations and tile layouts'], ['Ведомость отделочных материалов', 'Finishes schedule']],
          stages: [[.3, 'Сценарий и планировка', 'Scenario and layout'], [.3, 'Концепция', 'Concept'], [.4, 'Рабочие чертежи', 'Working drawings']] },
        { id: 'max', price: 7500, ru: 'Проект с комплектацией', en: 'Project with procurement plan',
          dru: 'Полный проект и подробные спецификации мебели, света и материалов с артикулами.', den: 'The full project plus detailed specifications of furniture, lighting and materials with item codes.',
          inc: [['Всё из «Полного проекта»', 'Everything in the “Full project”'], ['Спецификации мебели и света с артикулами', 'Furniture and lighting specifications with item codes'], ['Узлы и чертежи мебели на заказ', 'Details and drawings of custom furniture'], ['Ориентир бюджета на комплектацию', 'Procurement budget guide']],
          stages: [[.3, 'Сценарий и планировка', 'Scenario and layout'], [.3, 'Концепция', 'Concept'], [.4, 'Рабочие чертежи и спецификации', 'Drawings and specifications']] },
        { id: 'custom', price: null, online: true, ru: 'Собрать свой состав', en: 'Build your own scope', dru: 'Выберите только нужные разделы.', den: 'Pick only the parts you need.' }
      ],
      services: [
        { id: 'survey', price: 300, online: true, ru: 'Анкета, обмер и сценарий жизни', en: 'Questionnaire, survey and scenario of life' },
        { id: 'layout', price: 1200, online: true, ru: 'Планировка и расстановка мебели', en: 'Layout and furniture plan' },
        { id: 'collage', price: 1800, online: true, ru: 'Концепция и коллажи', en: 'Concept and collages', dru: 'мудборд, материалы, цвет', den: 'moodboard, materials, colour' },
        { id: 'light', price: 400, online: true, ru: 'Концепция света', en: 'Lighting concept' },
        { id: 'drawings', price: 2000, ru: 'Рабочие чертежи', en: 'Working drawings', dru: 'полы, потолки, электрика, сантехника', den: 'floors, ceilings, electrics, plumbing' },
        { id: 'elev', price: 600, ru: 'Развёртки стен и раскладка плитки', en: 'Wall elevations and tile layouts' },
        { id: 'spec', price: 800, ru: 'Ведомости и спецификации', en: 'Schedules and specifications' }
      ]
    };
    var fmtN = function (n) { return Math.round(n).toLocaleString('ru-RU').replace(/ /g, ' '); };
    var fmt = function (n) { return fmtN(n) + ' ₽'; };
    var st = { region: 'msk', area: 45, tariff: 'full', svc: { survey: true, layout: true }, sup: false, months: 4 };
    var tWrap = $('#tariffs'), sWrap = $('#services');
    PRICES.tariffs.forEach(function (t) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'tariff'; b.setAttribute('role', 'radio'); b.dataset.id = t.id;
      b.innerHTML = '<span class="dot" aria-hidden="true"></span><span><span class="t-name"><span class="ru">' + t.ru + '</span><span class="en">' + t.en + '</span></span><span class="t-desc"><span class="ru">' + t.dru + '</span><span class="en">' + t.den + '</span></span></span><span class="t-price">' + (t.price ? fmtN(t.price) + ' ₽/м²' : '') + '</span>';
      b.addEventListener('click', function () { st.tariff = t.id; render(); });
      tWrap.appendChild(b);
    });
    PRICES.services.forEach(function (v) {
      var l = document.createElement('label'); l.className = 'svc'; l.dataset.id = v.id;
      l.innerHTML = '<input type="checkbox"><span><span class="s-name"><span class="ru">' + v.ru + '</span><span class="en">' + v.en + '</span></span>' + (v.dru ? '<span class="s-desc"><span class="ru">' + v.dru + '</span><span class="en">' + v.den + '</span></span>' : '') + '</span><span class="s-price">' + fmtN(v.price) + ' ₽/м²</span>';
      var cb = l.querySelector('input'); cb.checked = !!st.svc[v.id];
      cb.addEventListener('change', function () { st.svc[v.id] = cb.checked; render(); });
      sWrap.appendChild(l);
    });
    var range = $('#areaRange'), num = $('#area');
    range.addEventListener('input', function () { st.area = +range.value; num.value = range.value; render(); });
    num.addEventListener('input', function () { var v = Math.max(0, +num.value || 0); st.area = v; range.value = Math.min(250, Math.max(15, v)); render(); });
    $$('[data-region]').forEach(function (b) { b.addEventListener('click', function () { st.region = b.dataset.region; render(); }); });
    var sup = $('#supervision'), months = $('#months');
    sup.addEventListener('change', function () { st.sup = sup.checked; render(); });
    months.addEventListener('input', function () { st.months = Math.max(1, +months.value || 1); render(); });

    var last = '';
    function render() {
      var L = lang(), online = st.region === 'online';
      // online covers layout and concept only
      var allowed = PRICES.tariffs.filter(function (x) { return !online || x.online; });
      if (!allowed.some(function (x) { return x.id === st.tariff; })) st.tariff = 'concept';
      var t = PRICES.tariffs.filter(function (x) { return x.id === st.tariff; })[0];
      Array.prototype.forEach.call(tWrap.children, function (b) {
        var on = b.dataset.id === st.tariff, ok = allowed.some(function (x) { return x.id === b.dataset.id; });
        b.hidden = !ok; b.classList.toggle('on', on); b.setAttribute('aria-checked', on ? 'true' : 'false');
      });
      Array.prototype.forEach.call(sWrap.children, function (l) {
        var v = PRICES.services.filter(function (x) { return x.id === l.dataset.id; })[0];
        l.hidden = online && !v.online;
      });
      $$('[data-region]').forEach(function (b) { var on = b.dataset.region === st.region; b.classList.toggle('on', on); b.setAttribute('aria-checked', on ? 'true' : 'false'); });
      $('#regionHint').innerHTML = online
        ? '<span class="ru">Для других городов работаем онлайн: планировка и концепция, встречи — по видеосвязи.</span><span class="en">For other cities we work online: layout and concept, meetings by video call.</span>'
        : '<span class="ru">В Москве и Подмосковье — любой состав проекта, выезд на обмер и авторский надзор.</span><span class="en">In Moscow and the region — any scope, an on-site survey and design supervision.</span>';
      $('#customBox').hidden = st.tariff !== 'custom';
      $('#supBox').hidden = online;
      var useSup = st.sup && !online;
      $('#supMonths').hidden = !useSup;

      var perM2, inc = [], stages;
      if (t.id === 'custom') {
        perM2 = 0;
        PRICES.services.forEach(function (v) { if (st.svc[v.id] && (!online || v.online)) { perM2 += v.price; inc.push([v.ru, v.en]); } });
        stages = [[1, 'Проект', 'Project']];
      } else { perM2 = t.price; inc = (online && t.incOnline) || t.inc; stages = t.stages; }
      var raw = perM2 * st.area, total = Math.max(raw, perM2 > 0 ? PRICES.min : 0), minApplied = perM2 > 0 && raw < PRICES.min;
      $('#rTotal').textContent = fmt(total);
      var name = L === 'en' ? t.en : t.ru;
      var where = online ? (L === 'en' ? 'online' : 'онлайн') : (L === 'en' ? 'Moscow' : 'Москва');
      $('#rMeta').textContent = name + ' · ' + st.area + ' м² · ' + where + ' · ' + fmtN(perM2) + ' ₽/м²' + (minApplied ? (L === 'en' ? ' · minimum fee applied' : ' · применена минимальная стоимость') : '');
      $('#rIncludes').innerHTML = inc.map(function (i) { return '<li><span class="ru">' + i[0] + '</span><span class="en">' + i[1] + '</span></li>'; }).join('');
      $('#rStages').innerHTML = stages.length > 1 ? stages.map(function (g) { return '<div><span><span class="ru">' + g[1] + '</span><span class="en">' + g[2] + '</span> · ' + Math.round(g[0] * 100) + '%</span><span>' + fmt(total * g[0]) + '</span></div>'; }).join('') : '';
      var supBox = $('#rSup'), supCost = 0, supM = 0;
      if (useSup) {
        supM = Math.max(PRICES.supervision.min, PRICES.supervision.perM2 * st.area); supCost = supM * st.months;
        supBox.hidden = false;
        supBox.innerHTML = '<span><span class="ru">Авторский надзор, ' + st.months + ' мес.</span><span class="en">Supervision, ' + st.months + ' mo.</span></span><span>' + fmt(supM) + ' / ' + (L === 'en' ? 'mo' : 'мес') + '</span>';
      } else supBox.hidden = true;
      last = [
        (L === 'en' ? 'Hello! My estimate from the DUNAEVA BUREAU site:' : 'Здравствуйте! Мой расчёт с сайта DUNAEVA BUREAU:'),
        name + ', ' + st.area + ' м², ' + where,
        (L === 'en' ? 'Price per m²: ' : 'Цена за м²: ') + fmt(perM2),
        (L === 'en' ? 'Project fee: ' : 'Стоимость проекта: ') + fmt(total)
      ].concat(useSup ? [(L === 'en' ? 'Supervision: ' : 'Авторский надзор: ') + fmt(supM) + (L === 'en' ? ' / month × ' : ' / мес × ') + st.months + ' = ' + fmt(supCost)] : []).join('\n');
    }
    $('#sendCalc').addEventListener('click', function () { sendToTelegram(last, $('#rNote')); });
    $('#copyCalc').addEventListener('click', function () {
      var btn = this;
      copy(last).then(function (ok) {
        var L = lang();
        btn.textContent = ok ? (L === 'en' ? 'Copied' : 'Скопировано') : (L === 'en' ? 'Copy failed' : 'Не удалось скопировать');
        setTimeout(function () { btn.innerHTML = '<span class="ru">Скопировать расчёт</span><span class="en">Copy estimate</span>'; }, 2200);
      });
    });
    document.addEventListener('langchange', render);
    render();
  })();

  /* ---------- request form → Telegram ---------- */
  (function () {
    var form = $('#form'), note = $('#formNote');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = form.elements, bad = false;
      ['name', 'contact'].forEach(function (n) { var v = f[n].value.trim(); f[n].classList.toggle('err', !v); if (!v) bad = true; });
      if (bad) { f[f.name.value.trim() ? 'contact' : 'name'].focus(); return; }
      var L = lang();
      var lines = [
        L === 'en' ? 'Hello! A request from the DUNAEVA BUREAU site.' : 'Здравствуйте! Заявка с сайта DUNAEVA BUREAU.',
        (L === 'en' ? 'Name: ' : 'Имя: ') + f.name.value.trim(),
        (L === 'en' ? 'Contact: ' : 'Контакт: ') + f.contact.value.trim()
      ];
      if (f.area.value.trim()) lines.push((L === 'en' ? 'Area: ' : 'Площадь: ') + f.area.value.trim() + ' м²');
      if (f.city.value.trim()) lines.push((L === 'en' ? 'City: ' : 'Город: ') + f.city.value.trim());
      if (f.msg.value.trim()) lines.push((L === 'en' ? 'About the flat: ' : 'О квартире: ') + f.msg.value.trim());
      sendToTelegram(lines.join('\n'), note);
    });
  })();

  /* ---------- start ---------- */
  measureIntro();
  drawAxes();
  onScroll();
})();
