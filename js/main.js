import * as THREE from 'three';
import { RoomEnvironment } from '../vendor/RoomEnvironment.js';
import { buildWorld, buildRail, SUN_OFFSET } from './world.js';
import { EN } from './i18n.js';

// Replace with real contacts before going live.
const CONTACTS = {
  email: 'hello@example.com',
  phone: '+7 (000) 000-00-00',
  telegram: 'dunaeva_bureau',
};

const HOLD = .52;              // share of a section spent at its stops; the rest is the flight
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const isMobile = matchMedia('(max-width: 900px)').matches;

const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const smooth = (e0, e1, x) => { const t = clamp((x - e0) / (e1 - e0)); return t * t * (3 - 2 * t); };
const easeInOut = (t) => (t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
// stepped ease: lingers on each integer stop, glides between them
const plateau = (x) => Math.floor(x) + smooth(.22, .78, x - Math.floor(x));

/* ---------------- DOM ---------------- */

const slots = [...document.querySelectorAll('.slot')];
const navLinks = [...document.querySelectorAll('[data-goto]')];
const counterCur = document.getElementById('counterCur');
const counterName = document.getElementById('counterName');
const progressBar = document.getElementById('progressBar');
const rulerTrack = document.getElementById('rulerTrack');
const projectItems = [...document.querySelectorAll('#projectList li')];
const processItems = [...document.querySelectorAll('#processList li')];

let tops = [];
function layout() {
  slots.forEach((s) => { s.style.height = `${(+s.dataset.vh) * innerHeight / 100}px`; });
  tops = slots.map((s) => s.offsetTop);
  tops.push(document.documentElement.scrollHeight - innerHeight);
}

// scroll position expressed in sections: 2.4 = 40% through section 2
function sectionPosition() {
  const y = scrollY;
  for (let k = slots.length - 1; k >= 0; k--) {
    if (y >= tops[k]) {
      const span = Math.max(1, (k === slots.length - 1 ? tops[k + 1] : tops[k + 1]) - tops[k]);
      return Math.min(slots.length - 1 + .999, k + clamp((y - tops[k]) / span, 0, .999));
    }
  }
  return 0;
}

// ruler: tick numbers, like a scale running along the left edge
for (let i = 1; i <= 60; i++) {
  const d = document.createElement('div');
  d.textContent = i;
  if (i % 10 === 0) d.className = 'is-major';
  rulerTrack.appendChild(d);
}

/* ---------------- i18n ---------------- */

let lang = 'ru';
const RU = {};
document.querySelectorAll('[data-i18n]').forEach((el) => { RU[el.dataset.i18n] = el.textContent; });
document.querySelectorAll('[data-i18n-ph]').forEach((el) => { RU[el.dataset.i18nPh] = el.placeholder; });
RU['nav.hero'] = 'Интерьер';
const t = (k) => (lang === 'en' ? EN[k] : RU[k]) ?? RU[k] ?? k;

function applyLang() {
  document.documentElement.lang = lang;
  document.querySelectorAll('[data-i18n]').forEach((el) => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll('[data-i18n-ph]').forEach((el) => { el.placeholder = t(el.dataset.i18nPh); });
  document.getElementById('langBtn').textContent = lang === 'ru' ? 'English' : 'Русский';
  document.title = lang === 'ru' ? 'DUNAEVA BUREAU — бюро дизайна интерьеров' : 'DUNAEVA BUREAU — interior design studio';
  lastSection = -1;
}
document.getElementById('langBtn').addEventListener('click', () => { lang = lang === 'ru' ? 'en' : 'ru'; applyLang(); });

document.getElementById('contactLines').innerHTML =
  `<a href="mailto:${CONTACTS.email}">${CONTACTS.email}</a><br>` +
  `<a href="tel:${CONTACTS.phone.replace(/[^+\d]/g, '')}">${CONTACTS.phone}</a><br>` +
  `<a href="https://t.me/${CONTACTS.telegram}" target="_blank" rel="noopener">Telegram</a>`;

document.getElementById('contactForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  const body = `${f.get('name')}\n${f.get('contact')}\n\n${f.get('msg') || ''}`;
  location.href = `mailto:${CONTACTS.email}?subject=${encodeURIComponent('DUNAEVA BUREAU — заявка')}&body=${encodeURIComponent(body)}`;
});

/* ---------------- navigation ---------------- */

function goTo(k) {
  const top = tops[k] + (k === 0 ? 0 : (tops[k + 1] - tops[k]) * .12);
  scrollTo({ top, behavior: reduceMotion ? 'auto' : 'smooth' });
  document.body.classList.remove('menu-open');
}
navLinks.forEach((a) => a.addEventListener('click', (e) => { e.preventDefault(); goTo(+a.dataset.goto); }));
document.getElementById('burger').addEventListener('click', () => document.body.classList.toggle('menu-open'));

/* ---------------- three.js ---------------- */

const canvas = document.getElementById('scene');
let renderer = null;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
} catch (err) {
  document.body.classList.add('no-webgl');
}

const scene = new THREE.Scene();
const BG = new THREE.Color(0xefece6);
scene.background = BG;
scene.fog = new THREE.Fog(BG, 14, 58);

const camera = new THREE.PerspectiveCamera(48, innerWidth / innerHeight, .1, 200);
const rail = buildRail();
let world = null;
const sun = new THREE.DirectionalLight(0xfff4e4, 2.6);

if (renderer) {
  renderer.setPixelRatio(Math.min(devicePixelRatio, isMobile ? 1.5 : 1.75));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.NeutralToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;

  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), .04).texture;
  scene.environmentIntensity = .55;

  scene.add(new THREE.HemisphereLight(0xffffff, 0xd9d0c3, 1.1));
  sun.castShadow = true;
  sun.shadow.mapSize.set(isMobile ? 1024 : 2048, isMobile ? 1024 : 2048);
  Object.assign(sun.shadow.camera, { left: -18, right: 18, top: 18, bottom: -18, near: 1, far: 70 });
  sun.shadow.bias = -.0004;
  sun.shadow.normalBias = .02;
  sun.shadow.radius = 4;
  scene.add(sun, sun.target);
}

/* ---------------- state ---------------- */

const state = { hover: -1, projectFocus: -1 };
let G = 0, Gs = 0;                 // target / smoothed section position
let lastSection = -1;
const pointer = new THREE.Vector2(), pSmooth = new THREE.Vector2();
let intro = reduceMotion ? 1 : 0;
const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2(-9, -9);

addEventListener('pointermove', (e) => {
  pointer.set(e.clientX / innerWidth * 2 - 1, -(e.clientY / innerHeight) * 2 + 1);
  ndc.copy(pointer);
});

function railIndex(g) {
  const k = Math.min(slots.length - 1, Math.floor(g));
  const q = g - k;
  const { first, last } = rail.meta[k];
  const n = last - first;
  let idx, flight = 0;
  if (q < HOLD || k === slots.length - 1) {
    const u = k === slots.length - 1 ? q : q / HOLD;
    idx = first + (n ? plateau(clamp(u) * n * .999) : 0);
    if (n && u >= .999) idx = last;
    if (!n) idx = first;
  } else {
    const f = (q - HOLD) / (1 - HOLD);
    idx = last + 2 * easeInOut(f);
    flight = f;
  }
  return { k, q, idx: Math.min(idx, rail.count - 1), flight, hold: clamp(q / HOLD) };
}

const camPos = new THREE.Vector3(), camTgt = new THREE.Vector3(), tmp = new THREE.Vector3();

function updateDom(k, q, hold) {
  // per-section reveal: in on arrival, out as the flight starts
  slots.forEach((s, i) => {
    let o = 0;
    if (i === k) {
      const fadeIn = i === 0 ? 1 : smooth(0, .1, q);
      const fadeOut = i === slots.length - 1 ? 1 : 1 - smooth(HOLD - .1, HOLD + .04, q);
      o = Math.min(fadeIn, fadeOut) * (i === 0 ? intro : 1);
    }
    s.style.setProperty('--o', o.toFixed(3));
    s.classList.toggle('is-live', o > .001);
    s.classList.toggle('is-on', o > .6);
  });

  // projects & process highlight the item matching the camera stop
  const pIdx = k === 2 ? Math.round(hold * 3 * .999 + .0) : 0;
  projectItems.forEach((li) => li.classList.toggle('is-current', +li.dataset.step === pIdx));
  state.projectFocus = k === 2 && pIdx > 0 ? pIdx - 1 : -1;
  const sIdx = k === 3 ? Math.round(hold * 4) : 0;
  processItems.forEach((li) => li.classList.toggle('is-current', +li.dataset.step === sIdx));

  if (k !== lastSection) {
    lastSection = k;
    counterCur.textContent = String(k + 1).padStart(2, '0');
    counterName.textContent = t(slots[k].dataset.name);
    navLinks.forEach((a) => a.classList.toggle('is-active', +a.dataset.goto === k && k > 0));
  }
}

let last = performance.now(), introStart = 0;
function frame(now) {
  const dt = Math.min((now - last) / 1000, .05);
  last = now;
  const time = now / 1000;
  if (!introStart) introStart = now;
  if (intro < 1) intro = Math.min(1, (now - introStart) / 2600);

  G = sectionPosition();
  Gs += (G - Gs) * (reduceMotion ? 1 : 1 - Math.pow(.0009, dt));
  if (Math.abs(G - Gs) < 1e-4) Gs = G;

  const r = railIndex(Gs);
  updateDom(r.k, r.q, r.hold);
  progressBar.style.transform = `scaleX(${(scrollY / Math.max(1, tops[tops.length - 1])).toFixed(4)})`;
  rulerTrack.style.transform = `translateY(${-scrollY * .09}px)`;

  if (renderer && world) {
    const u = r.idx / (rail.count - 1);
    rail.pos.getPoint(u, camPos);
    rail.tgt.getPoint(u, camTgt);

    // opening shot: a slow dolly from far back
    const ei = 1 - Math.pow(1 - intro, 3);
    camPos.z += (1 - ei) * 12;
    camPos.y += (1 - ei) * 1.4;

    // parallax from the pointer
    pSmooth.lerp(pointer, 1 - Math.pow(.02, dt));
    if (!reduceMotion) {
      camPos.x += pSmooth.x * .45;
      camPos.y += pSmooth.y * .22;
    }
    camera.position.copy(camPos);
    camera.lookAt(camTgt);

    // flight dynamics: lens breathes wider, slight bank
    const flightAmt = reduceMotion ? 0 : Math.sin(Math.PI * r.flight);
    const baseFov = camera.aspect < 1 ? 66 : 48;
    camera.fov = baseFov + flightAmt * 16;
    camera.rotateZ(Math.sin(Math.PI * 2 * r.flight) * .035 * (r.k % 2 ? -1 : 1));
    camera.updateProjectionMatrix();

    // sun follows the action so shadows stay crisp
    tmp.copy(camTgt).lerp(camPos, .35);
    sun.target.position.copy(tmp);
    sun.position.copy(tmp).add(SUN_OFFSET);

    // hover over project dioramas
    state.hover = -1;
    if (r.k === 2 && !isMobile) {
      raycaster.setFromCamera(ndc, camera);
      const hit = raycaster.intersectObjects(world.hoverables, false)[0];
      if (hit) state.hover = hit.object.userData.diorama;
    }
    canvas.style.cursor = state.hover >= 0 ? 'pointer' : '';

    world.anim.forEach((fn) => fn(time, dt, state));
    renderer.render(scene, camera);
  }
  requestAnimationFrame(frame);
}

canvas.addEventListener('click', () => {
  if (state.hover >= 0) {
    const k = 2, span = tops[k + 1] - tops[k];
    scrollTo({ top: tops[k] + span * HOLD * (state.hover + 1) / 3 * .999, behavior: 'smooth' });
  }
});

function resize() {
  layout();
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  if (renderer) renderer.setSize(innerWidth, innerHeight, false);
}
addEventListener('resize', resize);

async function start() {
  try { await Promise.race([document.fonts.load('200 100px Jost'), new Promise((r) => setTimeout(r, 1500))]); } catch (e) { /* fonts optional */ }
  if (renderer) world = buildWorld(scene);
  resize();
  if (location.hash) {
    const k = slots.findIndex((s) => `#${s.id}` === location.hash);
    if (k > 0) { scrollTo(0, tops[k] + (tops[k + 1] - tops[k]) * .12); intro = 1; }
  }
  Gs = G = sectionPosition();
  if (renderer) renderer.compile(scene, camera);
  requestAnimationFrame(frame);
  setTimeout(() => document.getElementById('loader').classList.add('is-done'), 250);
}
start();
