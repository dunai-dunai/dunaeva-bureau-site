// Procedural architecture: a chain of white halls joined by doorways.
// Each hall stages one section of the site; the camera flies through the doorways.
import * as THREE from 'three';
import { RoundedBoxGeometry } from '../vendor/RoundedBoxGeometry.js';

export const D = 26;          // hall depth (z)
export const W = 18;          // hall width (x)
export const H = 8;           // ceiling height
export const zc = (i) => -i * D;
export const zw = (i) => zc(i) - D / 2;   // partition wall behind hall i
export const DOOR = { w: 3.6, h: 5.4 };
export const SUN_OFFSET = new THREE.Vector3(-12, 16, 8);
export const SUN_DIR = SUN_OFFSET.clone().negate().normalize();

export const COLORS = {
  wall: 0xf3f1ec,
  floor: 0xe4dfd7,
  accent: 0xc4452c,
  oak: 0xb8956a,
  linen: 0xe7e0d4,
  graphite: 0x3a3936,
  walnut: 0x6b4a33,
  brass: 0xb8924a,
  sage: 0x9aa38d,
  birch: 0xd9c4a0,
  ink: 0x1d1c1a,
};

/* ---------------- textures ---------------- */

function canvasTex(size, draw, repeat = 1) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  draw(c.getContext('2d'), size);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(repeat, repeat);
  t.anisotropy = 8;
  return t;
}

function noise(ctx, s, base, amp, count) {
  ctx.fillStyle = base;
  ctx.fillRect(0, 0, s, s);
  for (let i = 0; i < count; i++) {
    const v = Math.random() * amp;
    ctx.fillStyle = `rgba(${Math.random() > .5 ? '255,255,255' : '80,70,60'},${v})`;
    const r = Math.random() * 3 + .5;
    ctx.fillRect(Math.random() * s, Math.random() * s, r, r);
  }
}

const microcement = () => canvasTex(512, (ctx, s) => {
  noise(ctx, s, '#e9e7e3', .07, 26000);
  for (let i = 0; i < 40; i++) {
    const g = ctx.createRadialGradient(Math.random() * s, Math.random() * s, 0, Math.random() * s, Math.random() * s, 140);
    g.addColorStop(0, 'rgba(120,105,90,.05)');
    g.addColorStop(1, 'rgba(120,105,90,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, s, s);
  }
});

const travertine = () => canvasTex(512, (ctx, s) => {
  noise(ctx, s, '#dccfb9', .05, 9000);
  for (let i = 0; i < 90; i++) {
    const y = Math.random() * s;
    ctx.strokeStyle = `rgba(${140 + Math.random() * 40},${118 + Math.random() * 30},90,${.08 + Math.random() * .18})`;
    ctx.lineWidth = Math.random() * 3 + .4;
    ctx.beginPath();
    ctx.moveTo(0, y);
    for (let x = 0; x <= s; x += 32) ctx.lineTo(x, y + Math.sin(x * .02 + i) * 3);
    ctx.stroke();
  }
});

const wood = (base) => canvasTex(256, (ctx, s) => {
  ctx.fillStyle = base;
  ctx.fillRect(0, 0, s, s);
  for (let i = 0; i < 60; i++) {
    const x = Math.random() * s;
    ctx.strokeStyle = `rgba(40,25,10,${Math.random() * .12})`;
    ctx.lineWidth = Math.random() * 2 + .3;
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.bezierCurveTo(x + 6, s * .3, x - 6, s * .6, x + 3, s);
    ctx.stroke();
  }
});

export function label(text, { px = 220, color = '#1d1c1a', weight = 200, height = .5 } = {}) {
  const c = document.createElement('canvas');
  const ctx = c.getContext('2d');
  const font = `${weight} ${px}px Jost, Helvetica, Arial, sans-serif`;
  ctx.font = font;
  const w = Math.ceil(ctx.measureText(text).width) + 20;
  c.width = w; c.height = Math.ceil(px * 1.25);
  ctx.font = font;
  ctx.fillStyle = color;
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 10, c.height / 2);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  const m = new THREE.Mesh(
    new THREE.PlaneGeometry(height * w / c.height, height),
    new THREE.MeshBasicMaterial({ map: t, transparent: true, depthWrite: false, toneMapped: false }),
  );
  return m;
}

/* ---------------- helpers ---------------- */

const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: .85, metalness: 0, ...o });

function put(parent, geo, mat, x, y, z, { cast = true, receive = true } = {}) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  m.castShadow = cast;
  m.receiveShadow = receive;
  parent.add(m);
  return m;
}
const box = (p, w, h, d, mat, x, y, z, o) => put(p, new THREE.BoxGeometry(w, h, d), mat, x, y, z, o);
const rbox = (p, w, h, d, r, mat, x, y, z, o) => put(p, new RoundedBoxGeometry(w, h, d, 3, r), mat, x, y, z, o);

/* ---------------- furniture ---------------- */

function sofa(p, mat, x, z, len = 1.4) {
  const g = new THREE.Group();
  rbox(g, len, .22, .62, .06, mat, 0, .2, 0);
  rbox(g, len, .42, .16, .06, mat, 0, .42, -.24);
  rbox(g, .16, .32, .62, .06, mat, -len / 2 + .08, .34, 0);
  rbox(g, .16, .32, .62, .06, mat, len / 2 - .08, .34, 0);
  rbox(g, len / 2 - .2, .1, .46, .04, mat, -len / 4 + .02, .35, .05);
  rbox(g, len / 2 - .2, .1, .46, .04, mat, len / 4 - .02, .35, .05);
  g.position.set(x, 0, z);
  p.add(g);
  return g;
}

function lamp(p, x, z, h = 1.25, shade = 0xf2ece0) {
  const metal = std(COLORS.ink, { roughness: .4, metalness: .6 });
  put(p, new THREE.CylinderGeometry(.13, .13, .02, 24), metal, x, .01, z);
  put(p, new THREE.CylinderGeometry(.012, .012, h, 8), metal, x, h / 2, z);
  const s = put(p, new THREE.ConeGeometry(.2, .24, 32, 1, true),
    std(shade, { side: THREE.DoubleSide, emissive: 0xffd9a0, emissiveIntensity: .55 }), x, h, z);
  return s;
}

function plant(p, x, z, s = 1) {
  put(p, new THREE.CylinderGeometry(.13 * s, .1 * s, .28 * s, 20), std(0xd6cfc4), x, .14 * s, z);
  const leaf = std(0x5d6b4a, { roughness: .7, flatShading: true });
  [[0, .52, 0, .2], [.1, .7, .05, .15], [-.09, .64, -.04, .14], [.03, .86, -.02, .11]].forEach(([dx, dy, dz, r]) =>
    put(p, new THREE.IcosahedronGeometry(r * s, 0), leaf, x + dx * s, dy * s, z + dz * s));
}

/* A cut-away room on a plinth: a "3D picture" of a project */
function diorama(pal) {
  const g = new THREE.Group();
  const inner = new THREE.Group();
  g.add(inner);
  const W2 = 3.2, D2 = 2.4;
  const floorMat = std(0xffffff, { map: wood(pal.floor) });
  rbox(inner, W2, .12, D2, .03, floorMat, 0, -.06, 0);
  const wallMat = std(pal.wall);
  box(inner, W2, 2, .08, wallMat, 0, 1, -D2 / 2 + .04);
  box(inner, .08, 2, D2, wallMat, -W2 / 2 + .04, 1, 0);
  // window light in the back wall
  put(inner, new THREE.PlaneGeometry(.8, 1.2), new THREE.MeshBasicMaterial({ color: 0xfff6e6, toneMapped: false }),
    .75, 1.15, -D2 / 2 + .085, { cast: false });
  box(inner, .9, .05, .1, std(pal.trim), .75, .53, -D2 / 2 + .1);
  // art piece on side wall
  box(inner, .03, .6, .8, std(pal.art), -W2 / 2 + .1, 1.25, -.2);
  // rug, sofa, table
  rbox(inner, 1.7, .016, 1.15, .005, std(pal.rug), -.15, .008, .2);
  sofa(inner, std(pal.sofa, { roughness: .95 }), -.25, -.35, 1.45);
  put(inner, new THREE.CylinderGeometry(.3, .3, .05, 40), std(pal.table, { roughness: .4, metalness: pal.metal || 0 }), -.2, .3, .38);
  put(inner, new THREE.CylinderGeometry(.04, .06, .28, 16), std(pal.table, { roughness: .4, metalness: pal.metal || 0 }), -.2, .14, .38);
  lamp(inner, .9, -.55, 1.15);
  plant(inner, -1.25, -.8, 1.1);
  // shelf on side wall
  for (let i = 0; i < 3; i++) box(inner, .26, .03, .9, std(pal.trim), -W2 / 2 + .21, .55 + i * .38, .55);
  // a few books
  for (let i = 0; i < 5; i++) box(inner, .18, .2 + Math.random() * .06, .04, std([pal.art, pal.rug, 0xe8e2d6, pal.sofa][i % 4]), -W2 / 2 + .2, .67, .25 + i * .06);
  // armchair
  const chair = sofa(inner, std(pal.chair, { roughness: .95 }), 1.0, .55, .62);
  chair.rotation.y = -Math.PI / 2.4;
  inner.scale.setScalar(1);
  return { g, inner };
}

/* ---------------- world ---------------- */

export function buildWorld(scene) {
  const anim = [];          // per-frame callbacks (t, dt)
  const hoverables = [];    // meshes that lift under the pointer

  const wallMat = std(COLORS.wall, { roughness: .95 });
  const floorTex = microcement();
  floorTex.repeat.set(6, 60);
  const floorMat = std(0xffffff, { map: floorTex, roughness: .55 });
  const ceilMat = std(0xf6f4f0, { roughness: 1, emissive: 0xf3efe8, emissiveIntensity: .55 });
  const glow = new THREE.MeshBasicMaterial({ color: 0xffffff, toneMapped: false });
  const accent = std(COLORS.accent, { roughness: .6 });

  const N = 7;
  const totalLen = N * D + 40;
  const floor = put(scene, new THREE.PlaneGeometry(W, totalLen), floorMat, 0, 0, -totalLen / 2 + D / 2 + 20, { cast: false });
  floor.rotation.x = -Math.PI / 2;
  const ceil = put(scene, new THREE.PlaneGeometry(W, totalLen), ceilMat, 0, H, floor.position.z, { cast: false });
  ceil.rotation.x = Math.PI / 2;

  for (let i = 0; i < N; i++) {
    const z = zc(i);
    // side walls (only the window wall of hall 5 casts shadows)
    if (i !== 5) box(scene, .5, H, D, wallMat, -W / 2 - .25, H / 2, z, { cast: false });
    box(scene, .5, H, D, wallMat, W / 2 + .25, H / 2, z, { cast: false });
    // ceiling light strips
    box(scene, .14, .04, D - 6, glow, -3.2, H - .02, z, { cast: false, receive: false });
    box(scene, .14, .04, D - 6, glow, 3.2, H - .02, z, { cast: false, receive: false });
    // partition with a doorway
    if (i < N - 1) {
      const zz = zw(i), side = (W - DOOR.w) / 2, t = .6;
      box(scene, side, H, t, wallMat, -W / 2 + side / 2, H / 2, zz, { cast: false });
      box(scene, side, H, t, wallMat, W / 2 - side / 2, H / 2, zz, { cast: false });
      box(scene, DOOR.w, H - DOOR.h, t, wallMat, 0, DOOR.h + (H - DOOR.h) / 2, zz, { cast: false });
      // thin accent reveal inside the jamb
      box(scene, .04, DOOR.h, t + .02, accent, -DOOR.w / 2 + .02, DOOR.h / 2, zz, { cast: false });
    }
  }
  // the front wall behind the opening shot
  box(scene, W, H, .5, wallMat, 0, H / 2, D / 2 + 18, { cast: false });

  /* ---- 0 · hero: the red monolith ---- */
  {
    const z = zc(0);
    rbox(scene, 4.2, .24, 4.2, .04, std(0xf7f5f1), 2.8, .12, z - 3);
    const mono = rbox(scene, .72, 5.6, .72, .02, accent, 2.8, 3.1, z - 3);
    const ring = put(scene, new THREE.TorusGeometry(1.25, .015, 8, 120), std(COLORS.ink), 2.8, 3.1, z - 3);
    anim.push((t) => {
      mono.rotation.y = t * .18;
      mono.position.y = 3.1 + Math.sin(t * .8) * .08;
      ring.rotation.x = Math.PI / 2 + Math.sin(t * .5) * .3;
      ring.rotation.y = t * .25;
      ring.position.y = mono.position.y;
    });
    // chair + lamp for scale
    sofa(scene, std(COLORS.linen, { roughness: .95 }), -4.4, z - 4, 2.4).rotation.y = .35;
    lamp(scene, -6.6, z - 5.6, 2.1);
    plant(scene, -2.2, z - 6.5, 2.2);
  }

  /* ---- 1 · approach: light / material / proportion ---- */
  {
    const z = zc(1) - 3;
    const plinth = std(0xf7f5f1);
    [-5, 0, 5].forEach((x) => rbox(scene, 2.2, 1, 2.2, .03, plinth, x, .5, z));
    // light
    const orb = put(scene, new THREE.SphereGeometry(.75, 64, 32),
      new THREE.MeshStandardMaterial({ color: 0xfff1d6, emissive: 0xffc77a, emissiveIntensity: 1.6, roughness: .3 }), -5, 2.3, z, { cast: false });
    const pl = new THREE.PointLight(0xffc77a, 9, 9, 1.6);
    pl.position.set(-5, 2.3, z);
    scene.add(pl);
    // material
    const block = rbox(scene, 1.5, 1.5, 1.5, .04, std(0xffffff, { map: travertine(), roughness: .7 }), 0, 1.75, z);
    // proportion: golden stack
    const stack = new THREE.Group();
    stack.position.set(5, 1, z);
    scene.add(stack);
    const phi = 1.618;
    let y = 0, s = 1.4;
    [COLORS.oak, 0xf7f5f1, COLORS.accent, COLORS.graphite].forEach((c, i) => {
      const h = s / phi * .55;
      const m = rbox(stack, s, h, s, .02, std(c, { roughness: .7 }), 0, y + h / 2, 0);
      m.rotation.y = i * .32;
      y += h; s /= phi;
    });
    anim.push((t) => {
      orb.position.y = 2.3 + Math.sin(t * 1.1) * .12;
      pl.position.y = orb.position.y;
      block.rotation.y = t * .22;
      block.rotation.x = Math.sin(t * .4) * .12;
      stack.rotation.y = -t * .16;
    });
  }

  /* ---- 2 · projects: three dioramas ---- */
  const palettes = [
    { floor: '#b8956a', wall: 0xf1ece4, trim: 0xe8e0d2, art: COLORS.accent, rug: 0xd9cbb6, sofa: COLORS.linen, chair: 0xc7a98a, table: COLORS.oak },
    { floor: '#5c4030', wall: 0x4a4845, trim: 0x2f2e2c, art: COLORS.brass, rug: 0x7c7368, sofa: 0x8b8378, chair: 0x6b4a33, table: COLORS.brass, metal: .8 },
    { floor: '#e2cfae', wall: 0xf8f7f4, trim: 0xffffff, art: COLORS.sage, rug: 0xe6e4dc, sofa: 0xcfd3c6, chair: COLORS.sage, table: 0xf3efe7 },
  ];
  const dioramas = [];
  {
    const z = zc(2) - 2;
    palettes.forEach((pal, i) => {
      const x = (i - 1) * 5.6;
      rbox(scene, 3.8, 1, 3, .03, std(0xf7f5f1), x, .5, z);
      const d = diorama(pal);
      d.g.position.set(x, 1.06, z);
      scene.add(d.g);
      d.g.traverse((o) => { if (o.isMesh) { o.userData.diorama = i; hoverables.push(o); } });
      const lbl = label(`0${i + 1}`, { px: 160, height: .34, color: '#c4452c', weight: 300 });
      lbl.position.set(x - 1.45, .55, z + 1.51);
      scene.add(lbl);
      dioramas.push({ ...d, base: i * 1.3, lift: 0, focus: 0 });
    });
    anim.push((t, dt, state) => {
      dioramas.forEach((d, i) => {
        const want = (state.hover === i ? 1 : 0) + (state.projectFocus === i ? .6 : 0);
        d.lift += (want - d.lift) * Math.min(1, dt * 4);
        d.g.position.y = 1.06 + d.lift * .35;
        d.g.rotation.y = .45 + Math.sin(t * .35 + d.base) * .22 - d.lift * .25;
        d.inner.rotation.x = d.lift * .08;
      });
    });
  }

  /* ---- 3 · process: a staircase of five stages ---- */
  {
    const z0 = zc(3) + 5, step = 2.2, rise = .55;
    const mats = [0xf7f5f1, 0xf3efe8, 0xeee9e0, 0xe9e3d9, COLORS.accent].map((c) => std(c, { roughness: .8 }));
    for (let i = 0; i < 5; i++) {
      const h = rise * (i + 1);
      rbox(scene, 7, h, step, .02, mats[i], 0, h / 2, z0 - step * i - step / 2);
      const l = label(`0${i + 1}`, { px: 160, height: .32, color: i === 4 ? '#f7f1e8' : '#1d1c1a', weight: 300 });
      l.position.set(-2.9, rise * i + rise / 2, z0 - step * i + .012);
      scene.add(l);
    }
    // landing objects
    const zTop = z0 - step * 5;
    rbox(scene, 7, rise * 5, 3, .02, std(0xf7f5f1), 0, rise * 5 / 2, zTop - 1.5);
    const key = rbox(scene, .5, 2.6, .5, .02, accent, 1.8, rise * 5 + 1.3, zTop - 1.5);
    anim.push((t) => { key.rotation.y = t * .3; });
  }

  /* ---- 4 · pricing: plinths A / B / C ---- */
  {
    const z = zc(4) - 2;
    const hs = [1, 1.7, 2.4];
    hs.forEach((h, i) => {
      const x = (i - 1) * 5;
      rbox(scene, 2.4, h, 2.4, .03, std(0xf7f5f1), x, h / 2, z);
      const l = label('ABC'[i], { px: 200, height: .5, color: '#c4452c', weight: 300 });
      l.position.set(x, h - .45, z + 1.205);
      scene.add(l);
    });
    const objs = [];
    objs.push(rbox(scene, .8, .8, .8, .02, std(COLORS.oak), -5, 1 + .4, z));
    objs.push(rbox(scene, .8, .8, .8, .02, std(COLORS.oak), 0, 1.7 + .4, z));
    objs.push(put(scene, new THREE.SphereGeometry(.38, 48, 24), std(0xf7f5f1, { roughness: .3 }), 0, 1.7 + 1.2, z));
    objs.push(rbox(scene, .8, .8, .8, .02, std(COLORS.oak), 5, 2.4 + .4, z));
    objs.push(put(scene, new THREE.SphereGeometry(.38, 48, 24), std(0xf7f5f1, { roughness: .3 }), 5, 2.4 + 1.2, z));
    objs.push(rbox(scene, .18, 1.3, .18, .01, accent, 5, 2.4 + 2.2, z));
    anim.push((t) => {
      objs.forEach((o, i) => { o.rotation.y = t * (.2 + i * .03) + i; });
      objs[5].position.y = 2.4 + 2.2 + Math.sin(t) * .06;
    });
  }

  /* ---- 5 · about: hall with tall windows, light shafts ---- */
  {
    const z = zc(5), x = -W / 2 - .25;
    const wins = [-6, -1, 4];          // window centers (z offsets)
    const ww = 2.4, y0 = 1.1, y1 = 6.6;
    let last = z + D / 2;
    wins.forEach((wz) => {
      const a = z + wz + ww / 2, b = z + wz - ww / 2;
      box(scene, .5, H, last - a, wallMat, x, H / 2, (last + a) / 2);
      box(scene, .5, y0, ww, wallMat, x, y0 / 2, z + wz);
      box(scene, .5, H - y1, ww, wallMat, x, (y1 + H) / 2, z + wz);
      box(scene, .5, y1 - y0, .06, std(COLORS.ink), x, (y0 + y1) / 2, z + wz);
      // bright outside
      put(scene, new THREE.PlaneGeometry(ww, y1 - y0), new THREE.MeshBasicMaterial({ color: 0xffffff, toneMapped: false }),
        x - .4, (y0 + y1) / 2, z + wz, { cast: false }).rotation.y = Math.PI / 2;
      last = b;
    });
    box(scene, .5, H, last - (z - D / 2), wallMat, x, H / 2, (last + z - D / 2) / 2);
    // light shafts: window rectangles extruded along the sun direction
    const beamMat = new THREE.ShaderMaterial({
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
      uniforms: { uColor: { value: new THREE.Color(0xfff0d2) }, uOpacity: { value: .22 } },
      vertexShader: 'varying float vX; void main(){ vX = position.x + .5; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); }',
      fragmentShader: 'uniform vec3 uColor; uniform float uOpacity; varying float vX; void main(){ float a = smoothstep(0.,.12,vX) * pow(1.-vX, 1.4); gl_FragColor = vec4(uColor * a * uOpacity, 1.); }',
    });
    const L = 11;
    wins.forEach((wz) => {
      const geo = new THREE.BoxGeometry(1, 1, 1);
      const m = new THREE.Mesh(geo, beamMat);
      const shear = new THREE.Matrix4().makeBasis(SUN_DIR.clone().multiplyScalar(L), new THREE.Vector3(0, y1 - y0, 0), new THREE.Vector3(0, 0, ww));
      m.matrixAutoUpdate = false;
      const origin = new THREE.Vector3(x + .3, (y0 + y1) / 2, z + wz).addScaledVector(SUN_DIR, L / 2);
      m.matrix.copy(shear).setPosition(origin);
      m.renderOrder = 5;
      scene.add(m);
    });
    // reading corner
    rbox(scene, 3.4, .06, 1.1, .02, std(COLORS.walnut, { map: wood('#7a5638') }), -3, .78, z - 3);
    [[-1.6, -.45], [1.6, -.45], [-1.6, .45], [1.6, .45]].forEach(([dx, dz]) =>
      box(scene, .06, .76, .06, std(COLORS.ink), -3 + dx, .38, z - 3 + dz));
    for (let i = 0; i < 4; i++) box(scene, .5, .06, .34, std([COLORS.accent, 0xe8e2d6, COLORS.sage, COLORS.graphite][i]), -2.1, .84 + i * .06, z - 3.1);
    sofa(scene, std(COLORS.oak, { roughness: .9 }), -4.8, z - 1, .9).rotation.y = .6;
    plant(scene, -6.5, z - 9, 2.6);
    lamp(scene, 3.8, z - 4.4, 1.8);
  }

  /* ---- 6 · contacts: opening to light ---- */
  {
    const z = zc(6), zz = z - D / 2;
    const ow = 6.5, oh = 6.4;
    const side = (W - ow) / 2;
    box(scene, side, H, .6, wallMat, -W / 2 + side / 2, H / 2, zz, { cast: false });
    box(scene, side, H, .6, wallMat, W / 2 - side / 2, H / 2, zz, { cast: false });
    box(scene, ow, H - oh, .6, wallMat, 0, oh + (H - oh) / 2, zz, { cast: false });
    put(scene, new THREE.PlaneGeometry(40, 30), new THREE.MeshBasicMaterial({ color: 0xffffff, toneMapped: false }), 0, 6, zz - 6, { cast: false });
    // the monolith returns, laid down as a bench
    rbox(scene, 4.2, .5, .72, .02, accent, 0, .25, z - 4);
    const halo = put(scene, new THREE.TorusGeometry(2.2, .012, 8, 160), std(COLORS.ink), 0, 3.2, zz + 1.2, { cast: false });
    anim.push((t) => { halo.rotation.y = Math.sin(t * .3) * .5; halo.rotation.x = Math.cos(t * .23) * .3; });
  }

  return { anim, hoverables, dioramas };
}

/* ---------------- camera rail ---------------- */
// Each section owns one or more "stops" (camera, target). Between sections
// the rail threads through the doorway in the partition wall.
export function buildRail() {
  const v = (x, y, z) => new THREE.Vector3(x, y, z);
  const sections = [
    [[v(0, 2.0, zc(0) + 11), v(.8, 2.6, zc(0) - 4)], [v(-.6, 2.1, zc(0) + 7.5), v(1.2, 2.5, zc(0) - 4)]],
    [[v(0, 2.3, zc(1) + 8.5), v(0, 1.6, zc(1) - 3)], [v(0, 2.1, zc(1) + 6), v(0, 1.7, zc(1) - 3)]],
    [
      [v(0, 3.0, zc(2) + 9), v(0, 1.5, zc(2) - 2)],
      [v(-6.4, 2.7, zc(2) + 4.2), v(-7.6, 1.7, zc(2) - 2)],
      [v(-0.8, 2.7, zc(2) + 4.2), v(-2.0, 1.7, zc(2) - 2)],
      [v(4.8, 2.7, zc(2) + 4.2), v(3.6, 1.7, zc(2) - 2)],
    ],
    [0, 1, 2, 3, 4].map((i) => [v(-4.2 + i * .3, 2.0 + .55 * i, zc(3) + 10 - i * 2.2), v(.5, .55 * (i + 1), zc(3) + 5 - i * 2.2 - 2.4)]),
    [[v(0, 2.6, zc(4) + 9.5), v(0, 1.7, zc(4) - 2)], [v(0, 2.4, zc(4) + 7), v(0, 1.8, zc(4) - 2)]],
    [[v(4, 2.2, zc(5) + 8), v(-3, 1.6, zc(5) - 2)], [v(3, 1.9, zc(5) + 3), v(-5, 1.4, zc(5) - 5)]],
    [[v(0, 2.0, zc(6) + 9), v(0, 2.6, zc(6) - 13)], [v(0, 2.1, zc(6) + 2), v(0, 2.8, zc(6) - 14)]],
  ];
  const pos = [], tgt = [], meta = [];
  sections.forEach((stops, k) => {
    const first = pos.length;
    stops.forEach(([p, t]) => { pos.push(p); tgt.push(t); });
    meta.push({ first, last: pos.length - 1 });
    if (k < sections.length - 1) {
      const y = k === 3 ? 3.6 : 2.5;
      pos.push(v(0, y, zw(k) + .4));
      tgt.push(v(0, y - .2, zw(k) - 10));
    }
  });
  return {
    pos: new THREE.CatmullRomCurve3(pos, false, 'centripetal'),
    tgt: new THREE.CatmullRomCurve3(tgt, false, 'centripetal'),
    count: pos.length,
    meta,
  };
}
