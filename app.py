from flask import Flask, render_template_string

app = Flask(__name__)

PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#1d0f4a">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<title>Dino Run — Cinematic 3D Edition</title>
<style>
  :root {
    --sky-top: #070a22;
    --sky-mid: #1d0f4a;
    --sky-bottom: #4a1450;
    --accent: #ffd166;
    --neon: #ff7a3d;
    --ground: #e7e2d6;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
  html, body {
    height: 100%;
    background: #05040c;
    color: #eee;
    font-family: "Segoe UI", system-ui, sans-serif;
    overflow: hidden;
    touch-action: manipulation;
    overscroll-behavior: none;
    -webkit-touch-callout: none;
  }

  /* ---------- POWER-OFF INTRO ---------- */
  #powerScreen {
    position: fixed; inset: 0; z-index: 100;
    background: #fff;
    display: flex; align-items: center; justify-content: center;
    animation: flicker 0.6s steps(2) 0s 1;
  }
  #powerScreen.collapse { animation: crtOff 0.9s ease-in forwards; }
  @keyframes flicker {
    0% { opacity: 1; } 20% { opacity: 0.2; } 40% { opacity: 1; }
    60% { opacity: 0.4; } 100% { opacity: 1; }
  }
  @keyframes crtOff {
    0% { transform: scale(1, 1); filter: brightness(1.5); }
    60% { transform: scale(1, 0.01); filter: brightness(3); }
    100% { transform: scale(0.001, 0.01); opacity: 0; }
  }
  #powerScreen::after {
    content: ""; position: absolute; inset: 0;
    background: repeating-linear-gradient(to bottom, rgba(0,0,0,0.12) 0 2px, transparent 2px 4px);
    pointer-events: none;
  }
  #powerScreen .msg {
    font-family: "Courier New", monospace; color: #111;
    font-size: clamp(14px, 2vw, 20px); letter-spacing: 3px;
  }

  /* ---------- POPUP CARD ---------- */
  #popup {
    position: fixed; inset: 0; z-index: 90;
    display: none; align-items: center; justify-content: center;
    background: radial-gradient(ellipse at center, rgba(10,6,30,0.85), rgba(0,0,0,0.97));
    backdrop-filter: blur(4px);
    perspective: 1200px;
    padding: 16px;
  }
  #popup.show { display: flex; animation: fadeUp 0.8s ease-out both; }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(30px) scale(0.96); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }
  .card {
    text-align: center; padding: 40px 48px;
    border: 1px solid rgba(255,209,102,0.35);
    border-radius: 18px;
    background: linear-gradient(160deg, rgba(40,20,80,0.6), rgba(10,8,25,0.9));
    box-shadow: 0 0 60px rgba(255,122,61,0.25), 0 30px 60px rgba(0,0,0,0.6);
    max-width: 480px;
    max-height: 92vh;
    overflow: auto;
    transform-style: preserve-3d;
    transition: transform .35s ease;
  }
  .card:hover { transform: rotateX(-5deg) rotateY(8deg) translateZ(20px); }
  .card h1 {
    font-size: clamp(28px, 5vw, 46px); letter-spacing: 4px;
    background: linear-gradient(90deg, #ffd166, #ff7a3d, #ff4d8d);
    -webkit-background-clip: text; background-clip: text; color: transparent;
    margin-bottom: 10px;
    text-shadow: 0 0 30px rgba(255,122,61,0.3);
  }
  .card p { color: #bfb8d9; margin-bottom: 24px; line-height: 1.5; }
  .btn {
    display: inline-block; cursor: pointer; border: none;
    padding: 14px 40px; border-radius: 999px;
    font-size: 16px; font-weight: 700; letter-spacing: 2px;
    color: #1a1030; background: linear-gradient(90deg, #ffd166, #ff7a3d);
    box-shadow: 0 8px 30px rgba(255,122,61,0.45), inset 0 -3px 0 rgba(0,0,0,0.2);
    transition: transform .15s ease, box-shadow .15s ease;
  }
  .btn:hover { transform: translateY(-2px) scale(1.04); box-shadow: 0 12px 40px rgba(255,122,61,0.6), inset 0 -3px 0 rgba(0,0,0,0.2); }
  .btn:active { transform: scale(0.97); }
  .hint { margin-top: 18px; font-size: 13px; color: #8d86ad; }

  /* ---------- GAME SCENE ---------- */
  #scene {
    position: fixed; inset: 0;
    background:
      radial-gradient(ellipse at 50% 100%, rgba(255,122,61,0.35), transparent 60%),
      linear-gradient(to bottom, var(--sky-top) 0%, var(--sky-mid) 55%, var(--sky-bottom) 100%);
    display: none; flex-direction: column; align-items: center; justify-content: center;
    perspective: 1100px;
    overflow: hidden;
    touch-action: none;
    user-select: none;
    -webkit-user-select: none;
  }
  #scene.show { display: flex; animation: fadeIn 1s ease both; }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

  /* Night tint (opacity set by JS for the day/night cycle) */
  #nightOverlay {
    position: absolute; inset: 0; z-index: 0; pointer-events: none;
    background: linear-gradient(to bottom, #02030f 0%, #0b0630 60%, #1a0830 100%);
    opacity: 0;
    transition: opacity .6s linear;
  }

  .stars { position: absolute; inset: 0; pointer-events: none; overflow: hidden; z-index: 0; transition: opacity .6s linear; }
  .star {
    position: absolute; width: 2px; height: 2px; background: #fff; border-radius: 50%;
    animation: twinkle 3s infinite ease-in-out;
    box-shadow: 0 0 6px rgba(255,255,255,0.8);
  }
  @keyframes twinkle { 0%,100% { opacity: .2; } 50% { opacity: 1; } }

  /* 3D striped retro sun */
  .sun3d {
    position: absolute; top: 12%; left: 50%;
    width: 240px; height: 240px; margin-left: -120px;
    border-radius: 50%;
    background: linear-gradient(180deg, #fff3b0 0%, #ffb347 38%, #ff4d8d 78%, #7b2ff7 100%);
    box-shadow: 0 0 140px 40px rgba(255,122,61,0.35), inset -20px -20px 60px rgba(0,0,0,0.25);
    overflow: hidden;
    animation: sunFloat 9s ease-in-out infinite;
    transform-style: preserve-3d;
    z-index: 0;
    pointer-events: none;
    transition: opacity .6s linear;
  }
  .sun3d::after {
    content: ""; position: absolute; inset: 0;
    background: repeating-linear-gradient(180deg, transparent 0 16px, #0b1030 16px 22px);
    clip-path: inset(58% 0 0 0);
    animation: bands 6s linear infinite alternate;
  }
  @keyframes sunFloat {
    0%,100% { transform: translateY(0) rotateY(-10deg) rotateX(8deg); }
    50%     { transform: translateY(-12px) rotateY(10deg) rotateX(-4deg); }
  }
  @keyframes bands { to { transform: translateY(-10px); } }

  /* Game stage: tilts with the mouse in 3D (desktop) */
  #gameWrap {
    position: relative; width: min(960px, 95vw); height: min(380px, 58vh);
    z-index: 2;
    transform-style: preserve-3d;
    transition: transform .25s ease-out;
  }
  /* 3D receding floor under the ground line */
  .floor {
    position: absolute; left: -40%; right: -40%;
    top: calc(100% - 40px); height: 320px;
    transform-origin: top center;
    transform: perspective(360px) rotateX(58deg);
    background-color: #1a0d3f;
    background-image:
      linear-gradient(to right, rgba(255,122,61,0.6) 2px, transparent 2px),
      linear-gradient(to bottom, rgba(255,122,61,0.6) 2px, transparent 2px);
    background-size: 70px 40px;
    -webkit-mask-image: linear-gradient(to bottom, #000 0%, #000 35%, transparent 100%);
            mask-image: linear-gradient(to bottom, #000 0%, #000 35%, transparent 100%);
    z-index: 1;
    pointer-events: none;
  }
  canvas#game {
    position: relative; z-index: 2;
    width: 100%; height: 100%; display: block;
  }

  #hud {
    position: absolute; top: 20px; left: 0; right: 0;
    display: flex; justify-content: space-between; padding: 0 40px;
    font-family: "Courier New", monospace; font-size: 18px; letter-spacing: 2px;
    color: var(--accent); text-shadow: 0 0 10px rgba(255,209,102,.6);
    z-index: 5;
    pointer-events: none;
  }

  /* Pause / sound buttons */
  .tools {
    position: absolute; top: 60px; right: 16px; z-index: 7;
    display: flex; gap: 8px;
  }
  .tool-btn {
    width: 44px; height: 44px; border-radius: 50%;
    border: 1px solid rgba(255,209,102,0.5);
    background: rgba(0,0,0,0.35); color: var(--accent);
    font-size: 16px; cursor: pointer;
  }

  #gameOver {
    position: absolute; inset: 0; display: none;
    align-items: center; justify-content: center; flex-direction: column;
    background: rgba(5,4,12,0.55); z-index: 6;
    backdrop-filter: blur(2px);
  }
  #gameOver.show { display: flex; animation: fadeIn .4s ease both; }
  #gameOver h2 {
    font-size: clamp(28px, 4vw, 44px); letter-spacing: 6px; color: #ff4d8d;
    text-shadow: 0 0 20px rgba(255,77,141,.6); margin-bottom: 16px;
  }
  #gameOver p { color: #ddd; margin-bottom: 20px; }

  /* Milestone toast */
  .toast {
    position: absolute; top: 34%; left: 50%;
    font-family: "Courier New", monospace; font-weight: bold;
    font-size: clamp(16px, 3vw, 26px); letter-spacing: 4px;
    color: var(--accent); text-shadow: 0 0 18px rgba(255,209,102,.8);
    opacity: 0; pointer-events: none; z-index: 8; white-space: nowrap;
  }
  .toast.show { animation: toastAnim 1.6s ease-out both; }
  @keyframes toastAnim {
    0%   { opacity: 0; transform: translate(-50%, -40%) scale(0.9); }
    15%  { opacity: 1; transform: translate(-50%, -50%) scale(1); }
    80%  { opacity: 1; transform: translate(-50%, -50%) scale(1); }
    100% { opacity: 0; transform: translate(-50%, -62%) scale(1); }
  }

  #flash {
    position: fixed; inset: 0; pointer-events: none; z-index: 20;
    background: radial-gradient(circle, rgba(255,77,141,0.45), rgba(255,77,141,0) 70%);
    opacity: 0;
  }
  #flash.hit { animation: flashAnim .6s ease-out; }
  @keyframes flashAnim { 0% { opacity: 1; } 100% { opacity: 0; } }

  .controls-hint {
    margin-top: 14px; font-size: 13px; color: #a79fcb; letter-spacing: 1px; z-index: 2;
    text-shadow: 0 0 8px rgba(0,0,0,0.6);
    pointer-events: none; text-align: center;
  }
  .exit {
    position: absolute; bottom: 16px; right: 20px; z-index: 6;
    background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.25); color: #aaa;
    padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 12px;
  }
  .exit:hover { color: #fff; border-color: #fff; }

  /* ---------- MOBILE / TOUCH LAYOUT ---------- */
  @media (max-width: 768px), (pointer: coarse) {
    #gameWrap { width: 98vw; height: min(340px, 50vh); }
    #hud {
      padding: 0 16px; font-size: 13px; letter-spacing: 1px;
      top: calc(12px + env(safe-area-inset-top, 0px));
    }
    .tools { top: calc(50px + env(safe-area-inset-top, 0px)); right: 12px; }
    .tool-btn { width: 40px; height: 40px; }
    .sun3d { width: 150px; height: 150px; margin-left: -75px; top: 9%; }
    .card { padding: 26px 22px; }
    .card p { font-size: 14px; }
    .btn { padding: 12px 30px; font-size: 14px; }
    .hint { font-size: 12px; }
    .controls-hint { font-size: 11px; padding: 0 12px; }
    .exit {
      bottom: calc(10px + env(safe-area-inset-bottom, 0px));
      right: 10px; padding: 5px 10px;
    }
    #gameOver h2 { letter-spacing: 3px; }
  }

  /* Phones in landscape: use most of the short screen height */
  @media (orientation: landscape) and (max-height: 500px) {
    #gameWrap { height: 66vh; width: min(96vw, 900px); }
    .sun3d { display: none; }
    #hud { top: 8px; }
    .tools { top: 8px; right: 60px; }
    .controls-hint { display: none; }
    .exit { bottom: 6px; }
  }
</style>
</head>
<body>

<!-- Power-off screen -->
<div id="powerScreen">
  <div class="msg">SIGNAL LOST — STANDBY</div>
</div>

<!-- Title card -->
<div id="popup">
  <div class="card">
    <h1>DINO RUN</h1>
    <p>Power failed. Survive the neon desert. Jump the cacti, duck the pterodactyls, and beat your best run.</p>
    <button class="btn" id="startBtn">START RUN</button>
    <div class="hint" id="popupHint">SPACE / ↑ jump &nbsp;·&nbsp; ↓ duck &nbsp;·&nbsp; P pause &nbsp;·&nbsp; M mute</div>
  </div>
</div>

<!-- Game scene -->
<div id="scene">
  <div id="nightOverlay"></div>
  <div class="stars" id="stars"></div>
  <div class="sun3d" id="sun"></div>

  <div id="hud">
    <span>SCORE <span id="score">00000</span></span>
    <span>HI <span id="hi">00000</span></span>
  </div>

  <div class="tools">
    <button class="tool-btn" id="pauseBtn" aria-label="Pause">❚❚</button>
    <button class="tool-btn" id="soundBtn" aria-label="Sound on or off">🔊</button>
  </div>

  <div id="gameWrap">
    <div class="floor" id="floor"></div>
    <canvas id="game"></canvas>
    <div id="gameOver">
      <h2>GAME OVER</h2>
      <p>Score: <span id="finalScore">0</span></p>
      <button class="btn" id="restartBtn">RUN AGAIN</button>
    </div>
  </div>

  <div class="toast" id="toast"></div>
  <div class="controls-hint" id="controlsHint">SPACE / ↑ jump &nbsp;·&nbsp; ↓ duck &nbsp;·&nbsp; P pause &nbsp;·&nbsp; M mute &nbsp;·&nbsp; move mouse for 3D tilt</div>
  <button class="exit" id="exitBtn">EXIT</button>
  <div id="flash"></div>
</div>

<script>
// ---------- Device detection ----------
const IS_TOUCH = window.matchMedia("(pointer: coarse)").matches || navigator.maxTouchPoints > 0;
if (IS_TOUCH) {
  document.getElementById("popupHint").textContent = "TAP to jump · SWIPE DOWN to duck · ❚❚ pause · 🔊 sound";
  document.getElementById("controlsHint").textContent = "TAP jump · SWIPE DOWN duck · ❚❚ pause · 🔊 sound";
}

// ---------- Safe storage (private mode can throw) ----------
const store = {
  get(key, fallback) {
    try { const v = localStorage.getItem(key); return v === null ? fallback : v; }
    catch (e) { return fallback; }
  },
  set(key, value) {
    try { localStorage.setItem(key, value); } catch (e) {}
  }
};

// ---------- Starfield ----------
const starsEl = document.getElementById("stars");
(function makeStars() {
  for (let i = 0; i < 120; i++) {
    const s = document.createElement("div");
    s.className = "star";
    s.style.left = Math.random() * 100 + "%";
    s.style.top = Math.random() * 60 + "%";
    s.style.width = s.style.height = (Math.random() < 0.2 ? 3 : 2) + "px";
    s.style.animationDelay = (Math.random() * 3) + "s";
    starsEl.appendChild(s);
  }
})();

// ---------- Power-off -> popup sequence ----------
const powerScreen = document.getElementById("powerScreen");
const popup = document.getElementById("popup");
setTimeout(() => powerScreen.classList.add("collapse"), 1400);
setTimeout(() => {
  powerScreen.style.display = "none";
  popup.classList.add("show");
}, 2300);

// ---------- Element refs ----------
const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const scene = document.getElementById("scene");
const gameWrap = document.getElementById("gameWrap");
const floorEl = document.getElementById("floor");
const gameOverEl = document.getElementById("gameOver");
const scoreEl = document.getElementById("score");
const hiEl = document.getElementById("hi");
const finalScoreEl = document.getElementById("finalScore");
const flashEl = document.getElementById("flash");
const pauseBtn = document.getElementById("pauseBtn");
const soundBtn = document.getElementById("soundBtn");
const sunEl = document.getElementById("sun");
const nightEl = document.getElementById("nightOverlay");
const toastEl = document.getElementById("toast");

// ---------- Canvas sizing (capped DPR saves battery on phones) ----------
const DPR = Math.min(window.devicePixelRatio || 1, 2);
let W = 0, H = 0, GROUND = 0;
function resize() {
  const r = canvas.getBoundingClientRect();
  if (!r.width || !r.height) return;   // scene hidden: nothing to size yet
  W = r.width; H = r.height;
  GROUND = H - 40;
  canvas.width = Math.round(W * DPR);
  canvas.height = Math.round(H * DPR);
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
}
window.addEventListener("resize", resize);
window.addEventListener("orientationchange", () => setTimeout(resize, 150));
if (window.ResizeObserver) new ResizeObserver(resize).observe(canvas);

// ---------- Constants & state ----------
const G = 0.65, JUMP_V = -12.5;
const STEP = 1000 / 60;   // fixed 60 Hz simulation, so 90/120 Hz phones don't run fast
let state, obstacles, clouds, particles, speed, frame, score, shake;
let paused = false, running = false, rafId = 0, lastTs = null, acc = 0;
let muted = store.get("dino_muted", "0") === "1";
let hi = parseInt(store.get("dino_hi", "0"), 10) || 0;
hiEl.textContent = String(hi).padStart(5, "0");
soundBtn.textContent = muted ? "🔇" : "🔊";

function resetGame() {
  state = { x: 70, y: 0, vy: 0, onGround: true, ducking: false, legPhase: 0, blink: 0 };
  obstacles = []; clouds = []; particles = [];
  speed = 6; frame = 0; score = 0; shake = 0;
  acc = 0; lastTs = null;
  setPaused(false);
  gameOverEl.classList.remove("show");
  scoreEl.textContent = "00000";
  updateNight();
}

function setPaused(value) {
  paused = value;
  pauseBtn.textContent = paused ? "▶" : "❚❚";
}

// ---------- Day / night cycle ----------
let night = 0;
function updateNight() {
  night = (1 - Math.cos(score / 450)) / 2;   // 0 = dusk, 1 = deep night
  nightEl.style.opacity = night.toFixed(3);
  starsEl.style.opacity = (0.35 + 0.65 * night).toFixed(3);
  sunEl.style.opacity = (1 - 0.55 * night).toFixed(3);
}

// ---------- Sound (WebAudio, no files needed) ----------
let audioCtx = null;
function beep(freq, dur, opts = {}) {
  if (muted) return;
  try {
    if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (audioCtx.state === "suspended") audioCtx.resume();
    const t = audioCtx.currentTime;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = opts.type || "square";
    osc.frequency.setValueAtTime(freq, t);
    if (opts.slideTo) osc.frequency.exponentialRampToValueAtTime(opts.slideTo, t + dur);
    gain.gain.setValueAtTime(opts.vol || 0.06, t);
    gain.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start(t);
    osc.stop(t + dur);
  } catch (e) {}
}
const sfx = {
  jump:      () => beep(420, 0.18, { slideTo: 880 }),
  land:      () => beep(160, 0.08, { type: "triangle", vol: 0.05 }),
  point:     () => beep(960, 0.09, { type: "sine", vol: 0.04 }),
  milestone: () => { beep(523, 0.12, { type: "triangle", vol: 0.08 });
                     setTimeout(() => beep(784, 0.2, { type: "triangle", vol: 0.08 }), 120); },
  crash:     () => beep(300, 0.5, { type: "sawtooth", slideTo: 40, vol: 0.09 })
};
function vibe(pattern) {
  try { if (navigator.vibrate) navigator.vibrate(pattern); } catch (e) {}
}

// ---------- Toast ----------
function toast(text) {
  toastEl.textContent = text;
  toastEl.classList.remove("show");
  void toastEl.offsetWidth;   // restart the animation
  toastEl.classList.add("show");
}

// ---------- Spawning ----------
function spawnObstacle() {
  const r = Math.random();
  if (r < 0.55) {
    const count = Math.random() < 0.3 ? 2 : 1;
    const h = 36 + Math.random() * 22;
    const w = 18 * count + (count - 1) * 6;
    obstacles.push({ type: "cactus", x: W + 10, w, h, y: GROUND - h, count });
  } else if (r < 0.8 && score > 200) {
    const heights = [GROUND - 40, GROUND - 70, GROUND - 100];
    obstacles.push({ type: "ptero", x: W + 10, w: 46, h: 26, y: heights[Math.floor(Math.random() * 3)], wing: 0 });
  } else {
    const h = 20 + Math.random() * 12;
    obstacles.push({ type: "rock", x: W + 10, w: 28, h, y: GROUND - h });
  }
}

function spawnCloud() {
  clouds.push({ x: W + 20, y: 20 + Math.random() * 90, s: 0.6 + Math.random() * 0.8, depth: Math.random() });
}

function burst(x, y, color, count = 14) {
  for (let i = 0; i < count; i++) {
    particles.push({
      x, y, vx: (Math.random() - 0.5) * 7, vy: (Math.random() - 1.2) * 6,
      life: 40 + Math.random() * 25, color, r: 1.5 + Math.random() * 2.5
    });
  }
}

// ---------- Collision & boxes ----------
function collides(a, b) {
  const pad = 4;
  return a.x + pad < b.x + b.w - pad && a.x + a.w - pad > b.x + pad &&
         a.y + pad < b.y + b.h - pad && a.y + a.h - pad > b.y + pad;
}

function dinoBox() {
  if (state.ducking && state.onGround) {
    return { x: state.x, y: GROUND - 26, w: 52, h: 26 };
  }
  return { x: state.x, y: GROUND - 46 + state.y, w: 40, h: 46 };
}

// ---------- 3D helpers ----------
function cylinderGrad(x, w, base, light) {
  const g = ctx.createLinearGradient(x, 0, x + w, 0);
  g.addColorStop(0, base);
  g.addColorStop(0.35, light);
  g.addColorStop(0.6, base);
  g.addColorStop(1, "rgba(0,0,0,0.45)");
  return g;
}

function drawShadow(cx, width, height) {
  const k = Math.max(0.25, 1 - height / 160);
  ctx.save();
  ctx.fillStyle = "rgba(0,0,0,0.4)";
  ctx.beginPath();
  ctx.ellipse(cx, GROUND + 4, (width / 2) * k, 4 * k, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

// ---------- Parallax mountain ridges ----------
function ridge(base, amp, period, factor, seed, color) {
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(0, GROUND);
  const off = (frame * speed * factor) % period;
  for (let x = -period; x <= W + period; x += 6) {
    const px = x - off;
    const h = amp * (0.55 * Math.abs(Math.sin(px * Math.PI / period + seed)) +
                     0.45 * Math.abs(Math.sin(px * Math.PI / (period * 0.43) + seed * 1.7)));
    ctx.lineTo(x, base - h);
  }
  ctx.lineTo(W, GROUND);
  ctx.closePath();
  ctx.fill();
}

function drawMountains() {
  ridge(GROUND - 10, 90, 340, 0.12, 0.5, "rgba(90,50,150,0.45)");
  ridge(GROUND - 4, 55, 230, 0.3, 1.3, "rgba(55,28,110,0.7)");
  ridge(GROUND, 28, 150, 0.6, 2.1, "rgba(28,14,70,0.95)");
}

// ---------- Sprites ----------
function drawDino() {
  const b = dinoBox();
  drawShadow(state.x + 22, 40, -state.y);

  ctx.save();
  ctx.shadowColor = "rgba(255,209,102,0.55)";
  ctx.shadowBlur = 14;

  const bodyGrad = ctx.createLinearGradient(0, b.y, 0, b.y + b.h);
  bodyGrad.addColorStop(0, "#ffffff");
  bodyGrad.addColorStop(0.6, "#e4ecff");
  bodyGrad.addColorStop(1, "#8fa3d6");
  ctx.fillStyle = bodyGrad;

  if (state.ducking && state.onGround) {
    ctx.fillRect(b.x, b.y + 6, 50, 14);
    ctx.fillRect(b.x + 40, b.y, 14, 12);
    ctx.fillStyle = "#0b1030";
    ctx.fillRect(b.x + 48, b.y + 3, 3, 3);
  } else {
    ctx.fillRect(b.x + 8, b.y + 8, 26, 26);     // body
    ctx.fillRect(b.x + 20, b.y, 22, 20);        // head
    ctx.fillRect(b.x + 34, b.y + 8, 10, 8);     // snout
    ctx.beginPath();                            // tail
    ctx.moveTo(b.x + 8, b.y + 20);
    ctx.lineTo(b.x, b.y + 14);
    ctx.lineTo(b.x + 8, b.y + 28);
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.fillStyle = "rgba(255,255,255,0.35)";   // belly highlight
    ctx.fillRect(b.x + 12, b.y + 10, 6, 18);
    ctx.fillStyle = "#0b1030";                  // eye
    if (state.blink <= 0) ctx.fillRect(b.x + 33, b.y + 4, 3, 3);
    ctx.fillStyle = bodyGrad;                   // legs
    ctx.shadowBlur = 14;
    if (state.onGround) {
      const phase = Math.floor(state.legPhase) % 2;
      if (phase === 0) {
        ctx.fillRect(b.x + 12, b.y + 34, 7, 12);
        ctx.fillRect(b.x + 24, b.y + 38, 7, 8);
      } else {
        ctx.fillRect(b.x + 12, b.y + 38, 7, 8);
        ctx.fillRect(b.x + 24, b.y + 34, 7, 12);
      }
    } else {
      ctx.fillRect(b.x + 14, b.y + 34, 7, 10);
      ctx.fillRect(b.x + 24, b.y + 34, 7, 10);
    }
  }
  ctx.restore();
}

function drawCactus(o) {
  drawShadow(o.x + o.w / 2, o.w, 0);
  ctx.save();
  ctx.shadowColor = "rgba(63,191,127,0.6)";
  ctx.shadowBlur = 12;
  for (let i = 0; i < o.count; i++) {
    const cx = o.x + i * 24;
    ctx.fillStyle = cylinderGrad(cx + 6, 6, "#1f8f5a", "#7dffb5");
    ctx.fillRect(cx + 6, o.y, 6, o.h);
    ctx.fillStyle = cylinderGrad(cx, 6, "#1f8f5a", "#7dffb5");
    ctx.fillRect(cx, o.y + o.h * 0.35, 6, 8);
    ctx.fillStyle = cylinderGrad(cx, 12, "#1f8f5a", "#7dffb5");
    ctx.fillRect(cx, o.y + o.h * 0.35, 12, 4);
    ctx.fillStyle = cylinderGrad(cx + 12, 6, "#1f8f5a", "#7dffb5");
    ctx.fillRect(cx + 12, o.y + o.h * 0.15, 6, 16);
    ctx.fillStyle = cylinderGrad(cx + 6, 12, "#1f8f5a", "#7dffb5");
    ctx.fillRect(cx + 6, o.y + o.h * 0.15, 12, 4);
  }
  ctx.restore();
}

function drawRock(o) {
  drawShadow(o.x + o.w / 2, o.w, 0);
  ctx.save();
  const cx = o.x + o.w / 2, cy = o.y + o.h / 2;
  const g = ctx.createRadialGradient(cx - o.w * 0.2, cy - o.h * 0.3, 2, cx, cy, o.w * 0.6);
  g.addColorStop(0, "#d6cdf0");
  g.addColorStop(0.5, "#8b7fb0");
  g.addColorStop(1, "#2c2050");
  ctx.fillStyle = g;
  ctx.shadowColor = "rgba(139,127,176,0.5)";
  ctx.shadowBlur = 10;
  ctx.beginPath();
  ctx.ellipse(cx, cy, o.w / 2, o.h / 2, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawPtero(o) {
  const up = Math.sin(o.wing) > 0;
  drawShadow(o.x + 23, 40, GROUND - (o.y + o.h));
  ctx.save();
  const g = ctx.createLinearGradient(o.x, o.y, o.x + 46, o.y + 20);
  g.addColorStop(0, "#ffb3d1");
  g.addColorStop(0.5, "#ff4d8d");
  g.addColorStop(1, "#7b1b4d");
  ctx.fillStyle = g;
  ctx.shadowColor = "rgba(255,77,141,0.6)";
  ctx.shadowBlur = 14;
  ctx.fillRect(o.x + 10, o.y + 8, 26, 10);      // body
  ctx.fillRect(o.x + 32, o.y + 6, 10, 8);       // head
  ctx.beginPath();                              // beak
  ctx.moveTo(o.x + 42, o.y + 9);
  ctx.lineTo(o.x + 50, o.y + 10);
  ctx.lineTo(o.x + 42, o.y + 12);
  ctx.fill();
  ctx.beginPath();                              // wing
  if (up) {
    ctx.moveTo(o.x + 16, o.y + 8);
    ctx.lineTo(o.x + 22, o.y - 8);
    ctx.lineTo(o.x + 28, o.y + 8);
  } else {
    ctx.moveTo(o.x + 16, o.y + 18);
    ctx.lineTo(o.x + 22, o.y + 30);
    ctx.lineTo(o.x + 28, o.y + 18);
  }
  ctx.fill();
  ctx.restore();
}

function drawGround() {
  ctx.save();
  ctx.shadowColor = "rgba(255,122,61,0.9)";
  ctx.shadowBlur = 16;
  ctx.fillStyle = "#ff9a5c";
  ctx.fillRect(0, GROUND, W, 2);
  ctx.restore();
  ctx.fillStyle = "rgba(231,226,214,0.35)";
  for (let i = 0; i < 14; i++) {
    const x = ((i * 97 - frame * speed * 0.5) % W + W) % W;
    ctx.fillRect(x, GROUND + 8 + (i % 3) * 6, 8 + (i % 4) * 4, 2);
  }
}

function drawClouds() {
  for (const c of clouds) {
    const alpha = 0.06 + 0.14 * c.depth;
    ctx.fillStyle = `rgba(255,190,220,${alpha})`;
    ctx.beginPath();
    ctx.ellipse(c.x, c.y, 34 * c.s, 10 * c.s, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(c.x + 18 * c.s, c.y - 6 * c.s, 22 * c.s, 9 * c.s, 0, 0, Math.PI * 2);
    ctx.fill();
  }
}

function drawSpeedLines() {
  if (speed < 9) return;
  const a = Math.min((speed - 9) / 10, 0.45);
  ctx.strokeStyle = `rgba(255,209,102,${a})`;
  ctx.lineWidth = 1.5;
  for (let i = 0; i < 6; i++) {
    const y = 30 + Math.random() * (GROUND - 60);
    const x = Math.random() * W;
    const len = 20 + Math.random() * 40;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + len, y);
    ctx.stroke();
  }
}

function drawParticles() {
  for (const p of particles) {
    ctx.globalAlpha = Math.max(Math.min(p.life / 40, 1), 0);
    ctx.fillStyle = p.color;
    ctx.shadowColor = p.color;
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.shadowBlur = 0;
  ctx.globalAlpha = 1;
}

// ---------- Update (runs at fixed 60 steps per second) ----------
function update() {
  frame++;
  speed = Math.min(6 + score / 300, 16);

  // dino physics
  if (!state.onGround) {
    state.vy += G;
    state.y += state.vy;
    if (state.y >= 0) {
      if (state.vy > 3) { burst(state.x + 20, GROUND, "#e7e2d6", 8); sfx.land(); }
      state.y = 0; state.vy = 0; state.onGround = true;
    }
  }
  if (state.onGround) {
    state.legPhase += speed * 0.05;
    if (frame % 6 === 0) {
      particles.push({ x: state.x + 14, y: GROUND, vx: -speed * 0.3, vy: -0.6,
                       life: 22, color: "#e7e2d6", r: 1.5 });
    }
  }
  if (state.blink > 0) state.blink--;
  else if (Math.random() < 0.005) state.blink = 6;

  // obstacles
  if (frame % Math.max(60 - Math.floor(speed * 2), 36) === 0 || (frame > 60 && Math.random() < 0.006)) {
    if (obstacles.length === 0 || obstacles[obstacles.length - 1].x < W - 220) spawnObstacle();
  }
  for (const o of obstacles) o.x -= speed;
  obstacles = obstacles.filter(o => o.x + o.w > -20);

  if (Math.random() < 0.008) spawnCloud();
  for (const c of clouds) c.x -= speed * (0.1 + 0.25 * c.depth);
  clouds = clouds.filter(c => c.x > -100);

  for (const p of particles) {
    p.x += p.vx; p.y += p.vy; p.vy += 0.2; p.life--;
  }
  particles = particles.filter(p => p.life > 0);

  // collision
  const db = dinoBox();
  for (const o of obstacles) {
    if (collides(db, o)) {
      endGame(db.x + 20, GROUND - 20);
      return;
    }
  }

  // scoring + milestones
  score++;
  if (score % 100 === 0) { sfx.point(); burst(W - 60, 40, "#ffd166", 20); }
  if (score % 500 === 0) { sfx.milestone(); vibe(20); toast("★ " + score); }
  scoreEl.textContent = String(score).padStart(5, "0");

  if (frame % 6 === 0) updateNight();

  // floor scroll (fake 3D motion)
  floorEl.style.backgroundPositionY = ((frame * speed * 2) % 40) + "px";
}

// ---------- Render ----------
function render() {
  ctx.save();
  if (shake > 0) {
    ctx.translate((Math.random() - 0.5) * shake, (Math.random() - 0.5) * shake);
    shake *= 0.88;
    if (shake < 0.5) shake = 0;
  }
  ctx.clearRect(-20, -20, W + 40, H + 40);
  drawMountains();
  drawClouds();
  drawSpeedLines();
  drawGround();
  for (const o of obstacles) {
    if (o.type === "cactus") drawCactus(o);
    else if (o.type === "rock") drawRock(o);
    else drawPtero(o);
  }
  drawDino();
  drawParticles();

  if (paused) {
    ctx.fillStyle = "rgba(0,0,0,0.45)";
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = "#ffd166";
    ctx.font = "bold 28px 'Courier New', monospace";
    ctx.textAlign = "center";
    ctx.shadowColor = "rgba(255,209,102,0.8)";
    ctx.shadowBlur = 18;
    ctx.fillText("PAUSED", W / 2, H / 2);
    ctx.textAlign = "start";
  }
  ctx.restore();
}

// ---------- Loop (time-based, so every refresh rate plays at the same speed) ----------
function loop(ts) {
  if (!running) return;
  if (lastTs === null) lastTs = ts;
  let dt = ts - lastTs;
  lastTs = ts;
  if (dt > 100) dt = 100;               // after a tab switch, don't jump ahead
  if (!paused) {
    acc += dt;
    while (acc >= STEP && running) {
      update();
      acc -= STEP;
    }
  }
  render();
  if (running) rafId = requestAnimationFrame(loop);
}

function startGame() {
  cancelAnimationFrame(rafId);
  resetGame();
  resize();
  running = true;
  rafId = requestAnimationFrame(loop);
}

function endGame(hx, hy) {
  running = false;
  cancelAnimationFrame(rafId);
  shake = 16;
  sfx.crash();
  vibe([60, 40, 120]);
  burst(hx, hy, "#ff4d8d", 26);
  flashEl.classList.remove("hit");
  void flashEl.offsetWidth;
  flashEl.classList.add("hit");

  if (score > hi) {
    hi = score;
    store.set("dino_hi", String(hi));
    hiEl.textContent = String(hi).padStart(5, "0");
  }
  finalScoreEl.textContent = score;
  gameOverEl.classList.add("show");
  settle();
}

// Keep shaking the crash frame after the game stops
function settle() {
  if (running) return;
  render();
  if (shake > 0) requestAnimationFrame(settle);
}

function togglePause() {
  if (!running) return;
  setPaused(!paused);
}

function toggleMute() {
  muted = !muted;
  store.set("dino_muted", muted ? "1" : "0");
  soundBtn.textContent = muted ? "🔇" : "🔊";
}

// ---------- Input (keyboard) ----------
function jump() {
  if (!running || paused) return;
  if (state.onGround && !state.ducking) {
    state.vy = JUMP_V;
    state.onGround = false;
    sfx.jump();
    vibe(8);
  }
}
function setDuck(on) {
  if (!running) return;
  if (on && state.onGround) state.ducking = true;
  if (!on) state.ducking = false;
}

document.addEventListener("keydown", (e) => {
  if (e.code === "Space" || e.code === "ArrowUp") {
    e.preventDefault();
    if (e.repeat) return;
    if (gameOverEl.classList.contains("show")) { startGame(); return; }
    jump();
  } else if (e.code === "ArrowDown") {
    e.preventDefault();
    setDuck(true);
  } else if (e.code === "KeyP") {
    togglePause();
  } else if (e.code === "KeyM") {
    toggleMute();
  }
});
document.addEventListener("keyup", (e) => {
  if (e.code === "ArrowDown") setDuck(false);
});

// Pause automatically when the phone locks or the tab is hidden
document.addEventListener("visibilitychange", () => {
  if (document.hidden && running && !paused) setPaused(true);
});
window.addEventListener("blur", () => {
  if (running && !paused) setPaused(true);
});

// ---------- Input (touch) ----------
// Tap = jump, swipe down = duck. Buttons are left alone so they still work.
let touchStartY = 0, touchDuck = false, touchMoved = false;

function onTouchStart(e) {
  if (e.target.closest("button")) return;
  e.preventDefault();
  touchStartY = e.touches[0].clientY;
  touchDuck = false;
  touchMoved = false;
}
function onTouchMove(e) {
  if (e.target.closest("button")) return;
  e.preventDefault();
  const dy = e.touches[0].clientY - touchStartY;
  if (Math.abs(dy) > 10) touchMoved = true;
  if (dy > 30 && !touchDuck) {
    touchDuck = true;
    setDuck(true);
  }
}
function onTouchEnd(e) {
  if (e.target.closest("button")) return;
  e.preventDefault();
  if (touchDuck) {
    setDuck(false);
  } else if (!touchMoved) {
    jump();
  }
  touchDuck = false;
  touchMoved = false;
}
function onTouchCancel() {
  touchDuck = false;
  touchMoved = false;
  setDuck(false);
}

scene.addEventListener("touchstart", onTouchStart, { passive: false });
scene.addEventListener("touchmove", onTouchMove, { passive: false });
scene.addEventListener("touchend", onTouchEnd, { passive: false });
scene.addEventListener("touchcancel", onTouchCancel);

// ---------- Mouse 3D tilt (desktop only) ----------
scene.addEventListener("mousemove", (e) => {
  const x = e.clientX / window.innerWidth - 0.5;
  const y = e.clientY / window.innerHeight - 0.5;
  gameWrap.style.transform = `rotateX(${(-y * 10).toFixed(2)}deg) rotateY(${(x * 14).toFixed(2)}deg)`;
});
scene.addEventListener("mouseleave", () => { gameWrap.style.transform = ""; });

// ---------- Buttons ----------
document.getElementById("startBtn").addEventListener("click", () => {
  popup.classList.remove("show");
  scene.classList.add("show");
  startGame();
});
document.getElementById("restartBtn").addEventListener("click", startGame);
pauseBtn.addEventListener("click", togglePause);
soundBtn.addEventListener("click", toggleMute);
document.getElementById("exitBtn").addEventListener("click", () => {
  running = false;
  cancelAnimationFrame(rafId);
  setPaused(false);
  gameOverEl.classList.remove("show");
  scene.classList.remove("show");
  popup.classList.add("show");
});
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE)


if __name__ == "__main__":
    app.run(debug=True)