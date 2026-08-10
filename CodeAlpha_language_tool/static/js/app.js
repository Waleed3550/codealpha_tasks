/**
 * LinguaVerse — Main Application Script
 *
 * Architecture:
 *   EarthScene      — Three.js 3D background (Earth, atmosphere, stars, particles)
 *   ToastManager    — Premium toast notification system
 *   TranslationUI   — Full translator UI (swap, copy, speak, clear, counters, states)
 *   EntranceAnim    — GSAP page-load entrance timeline
 *
 * Backend: Connected to Django REST API (/translate/, /languages/, /health/).
 *
 * Keyboard shortcuts:
 *   Ctrl+Enter  — Translate
 *   Escape      — Clear source text
 *   Tab         — Navigate (native)
 */

'use strict';

/* ================================================================
   CONSTANTS
   ================================================================ */
const STATIC_ROOT = (function () {
  const meta = document.querySelector('meta[name="static-url"]');
  return meta ? meta.getAttribute('content') : '/static/';
})();

const TEXTURE_URLS = {
  earthDay: `${STATIC_ROOT}images/earth_texture.jpg`,
  clouds:   'https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/textures/planets/earth_clouds_1024.png',
};

/**
 * Extract CSRF token from meta tag or cookie for Django POST requests.
 */
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta && meta.content) return meta.content;

  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : '';
}

/* ================================================================
   1. THREE.JS EARTH SCENE
   ================================================================ */
class EarthScene {
  /**
   * @param {string} canvasId  ID of the <canvas> element
   */
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;

    this.width  = window.innerWidth;
    this.height = window.innerHeight;
    this.clock  = new THREE.Clock();

    // Smooth mouse parallax
    this.mouse       = { x: 0, y: 0 };
    this.targetMouse = { x: 0, y: 0 };

    this.starLayers = [];
    this.earthGroup = null;
    this.earth      = null;
    this.clouds     = null;
    this.particles  = null;

    this._initRenderer();
    this._initScene();
    this._initCamera();
    this._initLights();
    this._buildStars();
    this._buildParticles();
    this._buildEarth();
    this._bindEvents();
    this._animate();
  }

  /* ---- Renderer ---- */
  _initRenderer() {
    this.renderer = new THREE.WebGLRenderer({
      canvas:    this.canvas,
      antialias: true,
      alpha:     false,
    });
    this.renderer.setSize(this.width, this.height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setClearColor(0x030310, 1);
    this.renderer.toneMapping         = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 0.85;
  }

  /* ---- Scene ---- */
  _initScene() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x030310);
  }

  updateTheme(theme) {
    const isLight = theme === 'light';
    const bgHex = isLight ? 0xf4f6fa : 0x030310;
    if (this.scene)    this.scene.background = new THREE.Color(bgHex);
    if (this.renderer) this.renderer.setClearColor(bgHex, 1);

    // Dynamic light adjustments
    if (this.ambientLight) {
      this.ambientLight.color.setHex(isLight ? 0xe2e8f0 : 0x0d1433);
      this.ambientLight.intensity = isLight ? 3.2 : 1.2;
    }
    if (this.sunLight) {
      this.sunLight.color.setHex(isLight ? 0xffffff : 0xfff4e0);
      this.sunLight.intensity = isLight ? 3.5 : 2.8;
    }
    if (this.rimLight) {
      this.rimLight.color.setHex(isLight ? 0x88bbff : 0x3366ff);
      this.rimLight.intensity = isLight ? 2.5 : 1.8;
    }
    if (this.fillLight) {
      this.fillLight.color.setHex(isLight ? 0xa78bfa : 0x8844ff);
      this.fillLight.intensity = isLight ? 1.4 : 0.7;
    }

    // Dynamic atmosphere adjustments (bright sky atmosphere)
    if (this.atmoOuterMesh) {
      this.atmoOuterMesh.material.color.setHex(isLight ? 0x4d8fff : 0x2255ee);
      this.atmoOuterMesh.material.opacity = isLight ? 0.35 : 0.10;
    }
    if (this.atmoInnerMesh) {
      this.atmoInnerMesh.material.color.setHex(isLight ? 0x7c3aed : 0x88aaff);
      this.atmoInnerMesh.material.opacity = isLight ? 0.08 : 0.038;
    }

    // Reduce star layers brightness in Light Mode (stars are hard to see on white and should be very faint)
    this.starLayers.forEach(layer => {
      layer.mat.opacity = isLight ? layer.baseOpacity * 0.15 : layer.baseOpacity;
    });
  }

  /* ---- Camera ---- */
  _initCamera() {
    this.camera = new THREE.PerspectiveCamera(55, this.width / this.height, 0.1, 2000);
    this.camera.position.set(0, 0, 9.5);
  }

  /* ---- Lights ---- */
  _initLights() {
    // Deep space ambient (very dim, cold blue)
    this.ambientLight = new THREE.AmbientLight(0x0d1433, 1.2);
    this.scene.add(this.ambientLight);

    // Sun — warm directional from upper-left front
    this.sunLight = new THREE.DirectionalLight(0xfff4e0, 2.8);
    this.sunLight.position.set(-5, 3, 6);
    this.scene.add(this.sunLight);

    // Atmospheric rim (blue from the dark side)
    this.rimLight = new THREE.PointLight(0x3366ff, 1.8, 28);
    this.rimLight.position.set(7, 0, -5);
    this.scene.add(this.rimLight);

    // Purple accent fill
    this.fillLight = new THREE.PointLight(0x8844ff, 0.7, 22);
    this.fillLight.position.set(-6, -3, 2);
    this.scene.add(this.fillLight);
  }

  /* ---- Stars ---- */
  _buildStars() {
    // Layer 1: thousands of small distant stars
    this._createStarLayer(4500, 0.055, 0.65, 55, 600);
    // Layer 2: medium brighter stars
    this._createStarLayer(600,  0.10,  0.90, 45, 65);
    // Layer 3: a handful of prominent bright stars
    this._createStarLayer(60,   0.18,  1.00, 38, 54);
  }

  _createStarLayer(count, size, opacity, rMin, rMax) {
    const positions = new Float32Array(count * 3);
    const colors    = new Float32Array(count * 3);

    for (let i = 0; i < count; i++) {
      const i3    = i * 3;
      const r     = rMin + Math.random() * (rMax - rMin);
      const phi   = Math.acos(2 * Math.random() - 1);
      const theta = Math.random() * Math.PI * 2;

      positions[i3]     = r * Math.sin(phi) * Math.cos(theta);
      positions[i3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i3 + 2] = r * Math.cos(phi);

      // Warm (white-yellow) vs cool (blue-white) stars
      const warm = Math.random() < 0.25;
      if (warm) {
        colors[i3]     = 1.0;
        colors[i3 + 1] = 0.88 + Math.random() * 0.12;
        colors[i3 + 2] = 0.65 + Math.random() * 0.25;
      } else {
        const b = 0.85 + Math.random() * 0.15;
        colors[i3]     = b * (0.80 + Math.random() * 0.20);
        colors[i3 + 1] = b * (0.85 + Math.random() * 0.15);
        colors[i3 + 2] = b;
      }
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color',    new THREE.BufferAttribute(colors,    3));

    const mat = new THREE.PointsMaterial({
      size:            size,
      vertexColors:    true,
      transparent:     true,
      opacity:         opacity,
      sizeAttenuation: true,
    });

    const stars = new THREE.Points(geo, mat);
    this.scene.add(stars);

    this.starLayers.push({
      mesh:        stars,
      mat:         mat,
      baseOpacity: opacity,
      twinkleFreq: 0.25 + Math.random() * 0.35,
      twinklePhase: Math.random() * Math.PI * 2,
      driftSpeed:  0.0004 + Math.random() * 0.0003,
    });
  }

  /* ---- Floating Particles ---- */
  _buildParticles() {
    const COUNT     = 280;
    const positions = new Float32Array(COUNT * 3);
    const colors    = new Float32Array(COUNT * 3);

    for (let i = 0; i < COUNT; i++) {
      const i3 = i * 3;
      const r  = 3.8 + Math.random() * 5.5;
      const ph = Math.random() * Math.PI * 2;
      const th = Math.random() * Math.PI;

      positions[i3]     = r * Math.sin(th) * Math.cos(ph);
      positions[i3 + 1] = r * Math.sin(th) * Math.sin(ph);
      positions[i3 + 2] = r * Math.cos(th);

      // Mix blue (#4d8fff) and purple (#8b5cf6)
      if (Math.random() > 0.5) {
        colors[i3]     = 0.30;
        colors[i3 + 1] = 0.56;
        colors[i3 + 2] = 1.00;
      } else {
        colors[i3]     = 0.54;
        colors[i3 + 1] = 0.36;
        colors[i3 + 2] = 0.96;
      }
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color',    new THREE.BufferAttribute(colors,    3));

    const mat = new THREE.PointsMaterial({
      size:            0.07,
      vertexColors:    true,
      transparent:     true,
      opacity:         0.55,
      sizeAttenuation: true,
    });

    this.particles    = new THREE.Points(geo, mat);
    this.particleMat  = mat;
    this.scene.add(this.particles);
  }

  /* ---- Earth Globe ---- */
  _buildEarth() {
    const RADIUS = 2.65;

    this.earthGroup = new THREE.Group();
    // Position Earth to the right, slightly back — frames the glass card nicely
    this.earthGroup.position.set(2.2, -0.4, -1.2);
    // Earth's axial tilt ~23.5°
    this.earthGroup.rotation.z = THREE.MathUtils.degToRad(23.5);
    this.scene.add(this.earthGroup);

    const loader = new THREE.TextureLoader();
    loader.crossOrigin = 'anonymous';

    const loadTex = (url) => new Promise((resolve) => {
      loader.load(url, resolve, undefined, () => resolve(null));
    });

    const earthGeo = new THREE.SphereGeometry(RADIUS, 48, 48);

    // ---- Try loading local Earth texture ----
    loadTex(TEXTURE_URLS.earthDay).then((dayTex) => {
      const earthMat = dayTex
        ? new THREE.MeshPhongMaterial({
            map:      dayTex,
            specular: new THREE.Color(0x224488),
            shininess: 22,
          })
        : new THREE.MeshPhongMaterial({
            color:    0x1a4b88,
            emissive: 0x071522,
            specular: new THREE.Color(0x3366cc),
            shininess: 30,
          });

      this.earth = new THREE.Mesh(earthGeo, earthMat);
      this.earthGroup.add(this.earth);

      // Animate Earth in with a gentle scale-up
      this.earth.scale.setScalar(0);
      const scaleUp = { v: 0 };
      const tgtScale = { v: 1 };
      const interval = setInterval(() => {
        scaleUp.v += (tgtScale.v - scaleUp.v) * 0.06;
        this.earth.scale.setScalar(scaleUp.v);
        if (Math.abs(scaleUp.v - 1) < 0.001) {
          this.earth.scale.setScalar(1);
          clearInterval(interval);
        }
      }, 16);
    });

    // ---- Cloud layer ----
    loadTex(TEXTURE_URLS.clouds).then((cloudTex) => {
      if (!cloudTex) return;
      const cloudGeo = new THREE.SphereGeometry(RADIUS * 1.016, 36, 36);
      const cloudMat = new THREE.MeshPhongMaterial({
        map:        cloudTex,
        transparent: true,
        opacity:     0.28,
        depthWrite:  false,
      });
      this.clouds = new THREE.Mesh(cloudGeo, cloudMat);
      this.earthGroup.add(this.clouds);
    });

    // ---- Outer atmosphere halo (BackSide — blue glow ring) ----
    const atmoOuterGeo = new THREE.SphereGeometry(RADIUS * 1.20, 32, 32);
    const atmoOuterMat = new THREE.MeshBasicMaterial({
      color:       0x2255ee,
      transparent: true,
      opacity:     0.10,
      side:        THREE.BackSide,
      depthWrite:  false,
    });
    this.atmoOuterMesh = new THREE.Mesh(atmoOuterGeo, atmoOuterMat);
    this.earthGroup.add(this.atmoOuterMesh);

    // ---- Inner thin atmosphere haze (FrontSide) ----
    const atmoInnerGeo = new THREE.SphereGeometry(RADIUS * 1.07, 64, 64);
    const atmoInnerMat = new THREE.MeshBasicMaterial({
      color:       0x88aaff,
      transparent: true,
      opacity:     0.038,
      side:        THREE.FrontSide,
      depthWrite:  false,
    });
    this.atmoInnerMesh = new THREE.Mesh(atmoInnerGeo, atmoInnerMat);
    this.earthGroup.add(this.atmoInnerMesh);
  }

  /* ---- Events ---- */
  _bindEvents() {
    // Mouse parallax
    window.addEventListener('mousemove', (e) => {
      this.targetMouse.x =  (e.clientX / this.width  - 0.5) * 2;
      this.targetMouse.y = -(e.clientY / this.height - 0.5) * 2;
    });

    // Touch parallax (mobile)
    window.addEventListener('touchmove', (e) => {
      if (!e.touches[0]) return;
      this.targetMouse.x =  (e.touches[0].clientX / this.width  - 0.5) * 2;
      this.targetMouse.y = -(e.touches[0].clientY / this.height - 0.5) * 2;
    }, { passive: true });

    // Resize
    window.addEventListener('resize', () => {
      this.width  = window.innerWidth;
      this.height = window.innerHeight;
      this.camera.aspect = this.width / this.height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(this.width, this.height);
    });
  }

  /* ---- Render Loop (Tab Visibility Pause Optimized) ---- */
  _animate() {
    requestAnimationFrame(() => this._animate());

    // Skip WebGL rendering if tab is hidden or 3D setting is disabled
    if (document.hidden || this.setting3DState === false) return;

    // Check if reduced motion is active (globally set on the html element class)
    const isReduced = document.documentElement.classList.contains('reduce-motion-active');

    const elapsed = this.clock.getElapsedTime();

    // Scale down movement factors to 25% under reduced motion to improve accessibility
    const moveScale = isReduced ? 0.25 : 1.0;

    // ---- Smooth mouse parallax ----
    this.mouse.x += (this.targetMouse.x - this.mouse.x) * (0.032 * moveScale);
    this.mouse.y += (this.targetMouse.y - this.mouse.y) * (0.032 * moveScale);

    // ---- Camera parallax (gentle drift following mouse) ----
    this.camera.position.x = this.mouse.x * 0.55;
    this.camera.position.y = this.mouse.y * 0.28;
    this.camera.lookAt(2.2, -0.4, -1.2); // Always look at Earth centre

    // ---- Earth rotation ----
    if (this.earth)  { this.earth.rotation.y  = elapsed * (0.055 * moveScale); }
    if (this.clouds) { this.clouds.rotation.y = elapsed * (0.065 * moveScale); this.clouds.rotation.x = elapsed * (0.008 * moveScale); }

    // ---- Earth group wobble ----
    if (this.earthGroup) {
      this.earthGroup.rotation.y += 0.00025 * moveScale;
      this.earthGroup.position.y = -0.4 + Math.sin(elapsed * 0.22) * (0.06 * moveScale);
    }

    // ---- Particles drift ----
    if (this.particles) {
      this.particles.rotation.y  = elapsed * (0.013 * moveScale);
      this.particles.rotation.x  = elapsed * (0.007 * moveScale);
      // Reduce opacity pulsation glow depth
      const baseOpacity = isReduced ? 0.35 : 0.42;
      const pulseDepth = isReduced ? 0.04 : 0.13;
      this.particleMat.opacity    = baseOpacity + Math.sin(elapsed * 0.6) * pulseDepth;
    }

    // ---- Twinkling stars ----
    for (const layer of this.starLayers) {
      const twinkle = 0.75 + Math.sin(elapsed * layer.twinkleFreq + layer.twinklePhase) * (0.25 * moveScale);
      layer.mat.opacity = layer.baseOpacity * twinkle;
      layer.mesh.rotation.y += layer.driftSpeed * moveScale;
    }

    this.renderer.render(this.scene, this.camera);
  }
}

/* ================================================================
   2. TOAST MANAGER
   ================================================================ */
class ToastManager {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this._queue    = [];
    this._maxShown = 3;
  }

  _show(message, type, duration = 4000) {
    if (!this.container) return;

    const iconMap = {
      success: 'bi-check-circle-fill',
      error:   'bi-exclamation-triangle-fill',
      info:    'bi-info-circle-fill',
      warning: 'bi-exclamation-circle-fill',
    };

    const toast = document.createElement('div');
    toast.className = `lv-toast type-${type}`;
    toast.setAttribute('role', 'status');
    toast.innerHTML = `
      <span class="toast-icon"><i class="bi ${iconMap[type] || iconMap.info}" aria-hidden="true"></i></span>
      <span class="toast-msg">${message}</span>
      <button class="toast-close-btn" aria-label="Dismiss notification">
        <i class="bi bi-x-lg" aria-hidden="true"></i>
      </button>
    `;

    // Dismiss on close button click
    toast.querySelector('.toast-close-btn').addEventListener('click', () => {
      this._dismiss(toast);
    });

    this.container.appendChild(toast);

    // Auto-dismiss
    const timer = setTimeout(() => this._dismiss(toast), duration);
    toast._timer = timer;
  }

  _dismiss(toast) {
    if (!toast.isConnected) return;
    clearTimeout(toast._timer);
    toast.classList.add('removing');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
  }

  success(msg, duration)  { this._show(msg, 'success', duration); }
  error(msg,   duration)  { this._show(msg, 'error',   duration); }
  info(msg,    duration)  { this._show(msg, 'info',    duration); }
  warning(msg, duration)  { this._show(msg, 'warning', duration); }
}

/* ================================================================
   3. TRANSLATION UI
   ================================================================ */
class TranslationUI {
  /**
   * @param {ToastManager} toast
   */
  constructor(toast) {
    this.toast     = toast;
    this._loading  = false;
    this._speaking = false;
    this._currentUtterance = null;

    this._bindElements();
    this._bindEvents();
    this._updateCharCount();
    this._checkHealth();
    this._loadLanguages();
  }

  /* ---- Element Binding ---- */
  _bindElements() {
    // Source
    this.sourceText     = document.getElementById('source-text');
    this.sourceLang     = document.getElementById('source-lang');
    this.sourceFlag     = document.getElementById('source-flag');
    this.clearBtn       = document.getElementById('clear-btn');
    this.charCount      = document.getElementById('char-count');
    this.charCounter    = document.getElementById('char-counter');
    this.speakSourceBtn = document.getElementById('speak-source-btn');
    this.micBtn         = document.getElementById('mic-btn');
    this.micIcon        = document.getElementById('mic-icon');

    // Controls
    this.swapBtn        = document.getElementById('swap-btn');
    this.translateBtn   = document.getElementById('translate-btn');
    this.btnIdle        = document.getElementById('btn-idle');
    this.btnLoading     = document.getElementById('btn-loading');
    this.btnSuccess     = document.getElementById('btn-success');

    // Target
    this.targetLang      = document.getElementById('target-lang');
    this.targetFlag      = document.getElementById('target-flag');
    this.copyBtn         = document.getElementById('copy-btn');
    this.copyIcon        = document.getElementById('copy-icon');
    this.speakTargetBtn  = document.getElementById('speak-target-btn');
    this.favBtn          = document.getElementById('fav-btn');
    this.favIcon         = document.getElementById('fav-icon');
    this.pdfBtn          = document.getElementById('pdf-btn');
    this.outputPlaceholder = document.getElementById('output-placeholder');
    this.outputText      = document.getElementById('output-text');
    this.outputCharCount = document.getElementById('output-char-count');
    this.outChars        = document.getElementById('out-chars');
    this.detectedBadge   = document.getElementById('detected-badge');
    this.detectedLangName = document.getElementById('detected-lang-name');

    // Country Flag Emoji Mapping
    this._flagMap = {
      'auto': '🌐', 'af': '🇿🇦', 'sq': '🇦🇱', 'am': '🇪🇹', 'ar': '🇸🇦', 'hy': '🇦🇲',
      'as': '🇮🇳', 'ay': '🇧🇴', 'az': '🇦🇿', 'bm': '🇲🇱', 'eu': '🇪🇸', 'be': '🇧🇾',
      'bn': '🇧🇩', 'bho': '🇮🇳', 'bs': '🇧🇦', 'bg': '🇧🇬', 'ca': '🇪🇸', 'ceb': '🇵🇭',
      'ny': '🇲🇼', 'zh': '🇨🇳', 'zh-cn': '🇨🇳', 'zh-tw': '🇹🇼', 'co': '🇫🇷', 'hr': '🇭🇷',
      'cs': '🇨🇿', 'da': '🇩🇰', 'dv': '🇲🇻', 'doi': '🇮🇳', 'nl': '🇳🇱', 'en': '🇬🇧',
      'eo': '🌐', 'et': '🇪🇪', 'ee': '🇬🇭', 'tl': '🇵🇭', 'fi': '🇫🇮', 'fr': '🇫🇷',
      'fy': '🇳🇱', 'gl': '🇪🇸', 'ka': '🇬🇪', 'de': '🇩🇪', 'el': '🇬🇷', 'gn': '🇵🇾',
      'gu': '🇮🇳', 'ht': '🇭🇹', 'ha': '🇳🇬', 'haw': '🇺🇸', 'he': '🇮🇱', 'hi': '🇮🇳',
      'hmn': '🇨🇳', 'hu': '🇭🇺', 'is': '🇮🇸', 'ig': '🇳🇬', 'ilo': '🇵🇭', 'id': '🇮🇩',
      'ga': '🇮🇪', 'it': '🇮🇹', 'ja': '🇯🇵', 'jw': '🇮🇩', 'jv': '🇮🇩', 'kn': '🇮🇳',
      'kk': '🇰🇿', 'km': '🇰🇭', 'rw': '🇷🇼', 'gom': '🇮🇳', 'ko': '🇰🇷', 'kri': '🇸🇱',
      'ku': '🇮🇶', 'ckb': '🇮🇶', 'ky': '🇰🇬', 'lo': '🇱🇦', 'la': '🇻🇦', 'lv': '🇱🇻',
      'ln': '🇨🇩', 'lt': '🇱🇹', 'lg': '🇺🇬', 'lb': '🇱🇺', 'mk': '🇲🇰', 'mai': '🇮🇳',
      'mg': '🇲🇬', 'ms': '🇲🇾', 'ml': '🇮🇳', 'mt': '🇲🇹', 'mi': '🇳🇿', 'mr': '🇮🇳',
      'mni-mtei': '🇮🇳', 'lus': '🇮🇳', 'mn': '🇲🇳', 'my': '🇲🇲', 'ne': '🇳🇵', 'no': '🇳🇴',
      'or': '🇮🇳', 'om': '🇪🇹', 'ps': '🇦🇫', 'fa': '🇮🇷', 'pl': '🇵🇱', 'pt': '🇵🇹',
      'pa': '🇮🇳', 'qu': '🇵🇪', 'ro': '🇷🇴', 'ru': '🇷🇺', 'sm': '🇼🇸', 'sa': '🇮🇳',
      'gd': '🇬🇧', 'nso': '🇿🇦', 'sr': '🇷🇸', 'st': '🇿🇦', 'sn': '🇿🇼', 'sd': '🇵🇰',
      'si': '🇱🇰', 'sk': '🇸🇰', 'sl': '🇸🇮', 'so': '🇸🇴', 'es': '🇪🇸', 'su': '🇮🇩',
      'sw': '🇰🇪', 'sv': '🇸🇪', 'tg': '🇹🇯', 'ta': '🇮🇳', 'tt': '🇷🇺', 'te': '🇮🇳',
      'th': '🇹🇭', 'ti': '🇪🇹', 'ts': '🇿🇦', 'tr': '🇹🇷', 'tk': '🇹🇲', 'ak': '🇬🇭',
      'uk': '🇺🇦', 'ur': '🇵🇰', 'ug': '🇨🇳', 'uz': '🇺🇿', 'vi': '🇻🇳', 'cy': '🇬🇧',
      'xh': '🇿🇦', 'yi': '🇮🇱', 'yo': '🇳🇬', 'zu': '🇿🇦'
    };

    // Drawer Tabs & Lists
    this.tabHistory     = document.getElementById('tab-history');
    this.tabFavorites   = document.getElementById('tab-favorites');
    this.panelHistory   = document.getElementById('panel-history');
    this.panelFavorites = document.getElementById('panel-favorites');
    this.historyList    = document.getElementById('history-list');
    this.favoritesList  = document.getElementById('favorites-list');
    this.historyCount   = document.getElementById('history-count');
    this.favoritesCount = document.getElementById('favorites-count');
    this.clearDrawerBtn = document.getElementById('clear-drawer-btn');

    // Skeleton & Theme
    this.skeletonLoader   = document.getElementById('skeleton-loader');
    this.themeToggleBtn   = document.getElementById('theme-toggle-btn');
    this.themeIcon        = document.getElementById('theme-icon');
    this.settingsBtn      = document.getElementById('settings-btn');
    this.settingAuto      = document.getElementById('setting-autotranslate');
    this.settingHistory   = document.getElementById('setting-savehistory');
    this.setting3D        = document.getElementById('setting-3d');
    this.settingMotion    = document.getElementById('setting-reducedmotion');

    // Error
    this.errorBanner  = document.getElementById('error-banner');
    this.errorText    = document.getElementById('error-text');
    this.errorDismiss = document.getElementById('error-dismiss');

    // Status
    this.statusPulse = document.getElementById('status-pulse');
    this.statusText  = document.getElementById('status-text');

    // Initialize LocalStorage Data, Settings & Theme
    this._history   = this._loadStorage('lv_history', []);
    this._favorites = this._loadStorage('lv_favorites', []);
    this._initSettings();
    this._initTheme();
    this._renderDrawer();
  }

  /* ---- Settings Panel Management ---- */
  _initSettings() {
    // 1. Auto-Translate
    const autoVal = this._loadStorage('lv_setting_auto', false);
    if (this.settingAuto) this.settingAuto.checked = autoVal;

    // 2. Save History
    const histVal = this._loadStorage('lv_setting_history', true);
    if (this.settingHistory) this.settingHistory.checked = histVal;

    // 3. 3D Earth Animation
    const earth3dVal = this._loadStorage('lv_setting_3d', true);
    if (this.setting3D) this.setting3D.checked = earth3dVal;
    
    // Propagate setting to EarthScene instance state immediately if it exists
    if (window.earthSceneRef) {
      window.earthSceneRef.setting3DState = earth3dVal;
    }
    this._apply3DEarthSetting(earth3dVal);

    // 4. Reduced Motion
    const motionVal = this._loadStorage('lv_setting_motion', false);
    if (this.settingMotion) this.settingMotion.checked = motionVal;
    this._applyReducedMotionSetting(motionVal);
  }

  _apply3DEarthSetting(enabled) {
    if (window.earthSceneRef) {
      window.earthSceneRef.setting3DState = enabled;
    }
    const canvas = document.getElementById('webgl-canvas');
    if (canvas) {
      canvas.style.display = enabled ? 'block' : 'none';
    }
  }

  _applyReducedMotionSetting(enabled) {
    if (enabled) {
      document.documentElement.classList.add('reduce-motion-active');
    } else {
      document.documentElement.classList.remove('reduce-motion-active');
    }
  }

  /* ---- Theme Toggle ---- */
  _initTheme() {
    let theme = localStorage.getItem('lv_theme');
    if (!theme) {
      const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
      theme = prefersDark ? 'dark' : 'light';
    }
    this._applyTheme(theme, false);
  }

  _toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    const next = current === 'dark' ? 'light' : 'dark';
    this._applyTheme(next, true);
    localStorage.setItem('lv_theme', next);
    this.toast.info(`Switched to ${next} theme.`);
  }

  _applyTheme(theme, animated = true) {
    document.documentElement.setAttribute('data-theme', theme);
    this._updateThemeIcon(theme);

    if (window.earthSceneRef) {
      window.earthSceneRef.updateTheme(theme);
    }
  }

  _updateThemeIcon(theme) {
    if (!this.themeIcon) return;
    if (theme === 'light') {
      this.themeIcon.className = 'bi bi-sun-fill';
    } else {
      this.themeIcon.className = 'bi bi-moon-stars-fill';
    }
  }

  /* ---- LocalStorage Helpers ---- */
  _loadStorage(key, fallback) {
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : fallback;
    } catch (_) { return fallback; }
  }

  _saveStorage(key, data) {
    try {
      localStorage.setItem(key, JSON.stringify(data));
    } catch (_) {}
  }

  /* ---- Event Binding ---- */
  _bindEvents() {
    // Character counter & Auto-resize & Auto-translate debounce
    this.sourceText.addEventListener('input', () => {
      this._updateCharCount();
      this._autoResizeTextarea();

      if (this.settingAuto && this.settingAuto.checked) {
        clearTimeout(this._debounceTimer);
        this._debounceTimer = setTimeout(() => {
          if (this.sourceText.value.trim().length > 0) {
            this._handleTranslate();
          }
        }, 600);
      }
    });

    // Theme toggle button
    if (this.themeToggleBtn) {
      this.themeToggleBtn.addEventListener('click', () => this._toggleTheme());
    }

    // Settings modal open button
    if (this.settingsBtn) {
      this.settingsBtn.addEventListener('click', () => {
        const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
        modal.show();
      });
    }

    // Settings change handlers
    if (this.settingAuto) {
      this.settingAuto.addEventListener('change', () => {
        this._saveStorage('lv_setting_auto', this.settingAuto.checked);
        this.toast.info(`Auto-translate is now ${this.settingAuto.checked ? 'enabled' : 'disabled'}.`);
      });
    }

    if (this.settingHistory) {
      this.settingHistory.addEventListener('change', () => {
        this._saveStorage('lv_setting_history', this.settingHistory.checked);
        this.toast.info(`Translation history logging is ${this.settingHistory.checked ? 'enabled' : 'disabled'}.`);
      });
    }

    if (this.setting3D) {
      this.setting3D.addEventListener('change', () => {
        const enabled = this.setting3D.checked;
        this._saveStorage('lv_setting_3d', enabled);
        this._apply3DEarthSetting(enabled);
        this.toast.info(`3D Earth graphics is ${enabled ? 'enabled' : 'disabled'}.`);
      });
    }

    if (this.settingMotion) {
      this.settingMotion.addEventListener('change', () => {
        const enabled = this.settingMotion.checked;
        this._saveStorage('lv_setting_motion', enabled);
        this._applyReducedMotionSetting(enabled);
        this.toast.info(`Reduced motion is ${enabled ? 'enabled' : 'disabled'}.`);
      });
    }

    // Translate: button click
    this.translateBtn.addEventListener('click', () => this._handleTranslate());

    // Translate: Ctrl+Enter inside textarea
    this.sourceText.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        this._handleTranslate();
      }
      if (e.key === 'Escape') {
        e.preventDefault();
        this._handleClear();
      }
    });

    // Swap languages
    this.swapBtn.addEventListener('click', () => this._handleSwap());

    // Clear source
    this.clearBtn.addEventListener('click', () => this._handleClear());

    // Copy translation
    this.copyBtn.addEventListener('click', () => this._handleCopy());

    // Speak source
    this.speakSourceBtn.addEventListener('click', () => {
      const text = this.sourceText.value.trim();
      const lang = this.sourceLang.value === 'auto' ? 'en' : this.sourceLang.value;
      if (text) this._speak(text, lang, this.speakSourceBtn);
      else      this.toast.info('Nothing to speak yet.');
    });

    // Speak target
    this.speakTargetBtn.addEventListener('click', () => {
      const text = this.outputText.textContent.trim();
      const lang = this.targetLang.value || 'en';
      if (text) this._speak(text, lang, this.speakTargetBtn);
      else      this.toast.info('No translation to speak yet.');
    });

    // Voice Input (Microphone)
    if (this.micBtn) {
      this.micBtn.addEventListener('click', () => this._toggleVoiceInput());
    }

    // Favorite Button
    if (this.favBtn) {
      this.favBtn.addEventListener('click', () => this._toggleFavoriteCurrent());
    }

    // Download PDF
    if (this.pdfBtn) {
      this.pdfBtn.addEventListener('click', () => this._downloadPDF());
    }

    // Drawer Tabs
    if (this.tabHistory && this.tabFavorites) {
      this.tabHistory.addEventListener('click', () => this._switchDrawerTab('history'));
      this.tabFavorites.addEventListener('click', () => this._switchDrawerTab('favorites'));
    }

    // Clear Drawer List
    if (this.clearDrawerBtn) {
      this.clearDrawerBtn.addEventListener('click', () => this._clearCurrentDrawerTab());
    }

    // Dismiss error
    this.errorDismiss.addEventListener('click', () => this._hideError());

    // Quick Language Pills binding
    this._bindPillEvents('source-pills', this.sourceLang, 'source');
    this._bindPillEvents('target-pills', this.targetLang, 'target');

    // Source language change
    this.sourceLang.addEventListener('change', () => {
      this._updateFlag('source');
      this._syncPills('source-pills', this.sourceLang.value);
      this._resolveLanguageConflict('source');
      this._trackRecentLanguage(this.sourceLang.value);
      this._saveSelectedLanguages();
      if (this.sourceLang.value !== 'auto') {
        this.detectedBadge.style.display = 'none';
      }
    });

    // Target language change
    this.targetLang.addEventListener('change', () => {
      this._updateFlag('target');
      this._syncPills('target-pills', this.targetLang.value);
      this._resolveLanguageConflict('target');
      this._trackRecentLanguage(this.targetLang.value);
      this._saveSelectedLanguages();
    });
  }

  _bindPillEvents(containerId, selectEl, panel) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.querySelectorAll('.lang-pill').forEach(pill => {
      pill.addEventListener('click', () => {
        const lang = pill.dataset.lang;
        selectEl.value = lang;
        selectEl.dispatchEvent(new Event('change'));
      });
    });
  }

  _syncPills(containerId, val) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.querySelectorAll('.lang-pill').forEach(pill => {
      if (pill.dataset.lang === val) pill.classList.add('active');
      else                           pill.classList.remove('active');
    });
  }

  /* ---- Country Flag Helper ---- */
  _updateFlag(panel) {
    if (panel === 'source' && this.sourceFlag) {
      const code = this.sourceLang.value;
      this.sourceFlag.textContent = this._flagMap[code] || '🌐';
    } else if (panel === 'target' && this.targetFlag) {
      const code = this.targetLang.value;
      this.targetFlag.textContent = this._flagMap[code] || '🌐';
    }
  }

  /* ---- Status Indicator & Health Check ---- */
  _setStatusReady() {
    this.statusPulse.className = 'status-pulse ready';
    this.statusText.textContent = 'Ready';
  }

  _setStatusLoading() {
    this.statusPulse.className = 'status-pulse loading';
    this.statusText.textContent = 'Translating…';
  }

  _setStatusError(msg = 'API Unavailable') {
    this.statusPulse.className = 'status-pulse error';
    this.statusText.textContent = msg;
  }

  async _checkHealth() {
    try {
      const res = await fetch('/health/');
      const data = await res.json();
      if (res.ok && data.success && data.data?.status === 'healthy') {
        this._setStatusReady();
      } else {
        this._setStatusError('Service Degraded');
      }
    } catch (_) {
      this._setStatusError('Offline');
    }
  }

  /* ---- Dynamic Language Loading & Recent Languages ---- */
  async _loadLanguages() {
    try {
      const res = await fetch('/languages/');
      const json = await res.json();

      if (res.ok && json.success && json.data?.languages) {
        this._allLanguages = json.data.languages;
        this._renderLanguageSelects();
      }
    } catch (err) {
      console.warn('[LinguaVerse] Failed to fetch dynamic languages list from backend:', err);
    }
  }

  _renderLanguageSelects() {
    if (!this._allLanguages) return;

    const recentCodes = this._loadStorage('lv_recent_langs', ['en', 'es', 'fr', 'de']);
    const savedSrc = this._loadStorage('lv_selected_source', 'en');
    const savedTgt = this._loadStorage('lv_selected_target', 'fr');

    const currentSrc = this.sourceLang.value || savedSrc;
    const currentTgt = this.targetLang.value || savedTgt;

    const buildOptions = (isSource) => {
      let html = isSource ? '<option value="auto">🌐 Auto Detect</option>' : '';

      // Recent Languages Optgroup
      const recentLangs = this._allLanguages.filter(l => recentCodes.includes(l.code));
      if (recentLangs.length > 0) {
        html += '<optgroup label="⭐️ Recently Used">';
        recentLangs.forEach(l => {
          const flag = this._flagMap[l.code] || '🌐';
          html += `<option value="${l.code}">${flag} ${l.name}</option>`;
        });
        html += '</optgroup>';
      }

      // All Languages Optgroup
      html += '<optgroup label="🌐 All Languages">';
      this._allLanguages.forEach(l => {
        const flag = this._flagMap[l.code] || '🌐';
        html += `<option value="${l.code}">${flag} ${l.name}</option>`;
      });
      html += '</optgroup>';

      return html;
    };

    this.sourceLang.innerHTML = buildOptions(true);
    this.targetLang.innerHTML = buildOptions(false);

    if (Array.from(this.sourceLang.options).some(o => o.value === currentSrc)) {
      this.sourceLang.value = currentSrc;
    } else {
      this.sourceLang.value = 'en';
    }

    if (Array.from(this.targetLang.options).some(o => o.value === currentTgt)) {
      this.targetLang.value = currentTgt;
    } else {
      this.targetLang.value = 'fr';
    }

    this._updateFlag('source');
    this._updateFlag('target');
  }

  _saveSelectedLanguages() {
    this._saveStorage('lv_selected_source', this.sourceLang.value);
    this._saveStorage('lv_selected_target', this.targetLang.value);
  }

  _trackRecentLanguage(code) {
    if (!code || code === 'auto') return;
    let recents = this._loadStorage('lv_recent_langs', ['en', 'es', 'fr', 'de']);
    recents = recents.filter(c => c !== code);
    recents.unshift(code);
    if (recents.length > 5) recents.pop();
    this._saveStorage('lv_recent_langs', recents);
    this._renderLanguageSelects();
  }

  _resolveLanguageConflict(changedPanel) {
    const src = this.sourceLang.value;
    const tgt = this.targetLang.value;

    if (src !== 'auto' && src === tgt) {
      if (changedPanel === 'source') {
        // Auto switch target language to English or Spanish
        const fallback = src === 'en' ? 'es' : 'en';
        this.targetLang.value = fallback;
        this._updateFlag('target');
        this.toast.info(`Target automatically switched to ${fallback === 'es' ? 'Spanish' : 'English'} to avoid matching source.`);
      } else {
        // Auto switch source language to English or Auto
        const fallback = tgt === 'en' ? 'es' : 'en';
        this.sourceLang.value = fallback;
        this._updateFlag('source');
        this.toast.info(`Source automatically switched to ${fallback === 'es' ? 'Spanish' : 'English'} to avoid matching target.`);
      }
    }
  }

  /* ---- Character Counter & Auto Resize ---- */
  _updateCharCount() {
    const len = this.sourceText.value.length;
    this.charCount.textContent = len;
    this.charCounter.classList.remove('warn', 'limit');
    if (len >= 5000)       this.charCounter.classList.add('limit');
    else if (len >= 4200)  this.charCounter.classList.add('warn');
  }

  _autoResizeTextarea() {
    this.sourceText.style.height = 'auto';
    const newHeight = Math.max(230, Math.min(this.sourceText.scrollHeight, 500));
    this.sourceText.style.height = `${newHeight}px`;
  }

  /* ---- Swap Languages ---- */
  _handleSwap() {
    const srcCode = this.sourceLang.value;
    const tgtCode = this.targetLang.value;

    if (srcCode === 'auto') {
      this.toast.warning('Cannot swap — source is set to Auto Detect.');
      // Shake swap button
      this._shake(this.swapBtn);
      return;
    }

    // Try to find source code in target select
    const srcInTarget = Array.from(this.targetLang.options).some(o => o.value === srcCode);
    const tgtInSource = Array.from(this.sourceLang.options).some(o => o.value === tgtCode);

    if (srcInTarget)  this.targetLang.value = srcCode;
    if (tgtInSource)  this.sourceLang.value = tgtCode;

    // Immediately update country flag badges and save to localStorage
    this._updateFlag('source');
    this._updateFlag('target');
    this._saveSelectedLanguages();

    // Swap text content too
    const srcText = this.sourceText.value.trim();
    const tgtText = this.outputText.textContent.trim();

    if (tgtText) {
      this.sourceText.value = tgtText;
      this._updateCharCount();
      this._showOutput(srcText);
    } else {
      this._resetOutput();
    }

    // GSAP rotate swap button
    if (window.gsap) {
      gsap.fromTo(this.swapBtn,
        { rotation: 0 },
        { rotation: 180, duration: 0.4, ease: 'back.out(1.5)', clearProps: 'rotation' }
      );
    }

    this.toast.info('Languages swapped.');
  }

  /* ---- Clear ---- */
  _handleClear() {
    if (!this.sourceText.value && !this.outputText.textContent) return;

    this.sourceText.value = '';
    this._updateCharCount();
    this._resetOutput();
    this._hideError();

    if (window.gsap) {
      gsap.from(this.sourceText, { opacity: 0.3, duration: 0.25, ease: 'power2.out' });
    }

    this.sourceText.focus();
  }

  /* ---- Translate (Django Backend Connected) ---- */
  async _handleTranslate() {
    if (this._loading) return; // Prevent concurrent duplicate requests

    const text = this.sourceText.value.trim();
    if (!text) {
      this._shake(document.getElementById('source-panel'));
      this.toast.error('Please enter some text to translate.');
      return;
    }

    const source = this.sourceLang.value;
    const target = this.targetLang.value;

    if (source !== 'auto' && source === target) {
      this.toast.warning('Source and target languages must be different.');
      return;
    }

    // Performance Optimization: Check local cache first
    const cacheKey = `${source}:${target}:${text}`;
    if (!this._translationCache) this._translationCache = new Map();

    if (this._translationCache.has(cacheKey)) {
      const cached = this._translationCache.get(cacheKey);
      this._showOutput(cached.translated_text, cached.detected_language);
      this.toast.info('Loaded from instant cache.');
      return;
    }

    // Cancel any ongoing inflight request
    if (this._activeAbortController) {
      this._activeAbortController.abort();
    }
    this._activeAbortController = new AbortController();

    this._setLoading(true);
    this._hideError();
    this._resetOutput();
    this._setStatusLoading();

    const startTime = performance.now();

    const payload = {
      text:             text,
      source_language: source,
      target_language: target,
    };

    console.log('[LinguaVerse] Sending POST /translate/ payload:', payload);

    try {
      const response = await fetch('/translate/', {
        method:  'POST',
        signal:  this._activeAbortController.signal,
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken':   getCsrfToken(),
          'Accept':       'application/json',
        },
        body: JSON.stringify(payload),
      });

      const durationMs = Math.round(performance.now() - startTime);
      const latencyVal = document.getElementById('latency-val');
      if (latencyVal) latencyVal.textContent = `${durationMs} ms`;

      const json = await response.json();

      if (!response.ok || !json.success) {
        const errMsg = json.message || json.errors?.detail || json.errors?.non_field_errors?.[0] || 'Translation request failed.';
        throw new Error(errMsg);
      }

      const resData = json.data;

      // Cache result (limit cache size to 100 entries)
      if (this._translationCache.size > 100) {
        const oldestKey = this._translationCache.keys().next().value;
        this._translationCache.delete(oldestKey);
      }
      this._translationCache.set(cacheKey, resData);

      this._showOutput(resData.translated_text, resData.detected_language);
      this._showSuccessState();

      // Save to History (LocalStorage)
      this._saveToHistory({
        id:          Date.now(),
        sourceLang:  resData.detected_language || source,
        targetLang:  target,
        sourceText:  text,
        translatedText: resData.translated_text,
        timestamp:   new Date().toISOString(),
      });

      // Update favorite button status for current translation
      this._updateFavButtonState(text, resData.translated_text);

      const sourceName = this.sourceLang.options[this.sourceLang.selectedIndex]?.text || 'Source';
      const targetName = this.targetLang.options[this.targetLang.selectedIndex]?.text || 'Target';
      this.toast.success(`Translated from ${sourceName} to ${targetName}!`);

    } catch (err) {
      if (err.name === 'AbortError') return; // Silence aborted request errors

      const isNetworkErr = err.name === 'TypeError' || err.message.includes('fetch');
      const displayMsg = isNetworkErr
        ? 'Network error: Cannot reach the translation server.'
        : err.message || 'An unexpected error occurred.';

      this._showError(displayMsg);
      this._shake(document.getElementById('translator-card'));
      this.toast.error(displayMsg);
      this._setStatusError('Error');
    } finally {
      if (!this.errorBanner || this.errorBanner.style.display === 'none') {
        this._setStatusReady();
      }
    }
  }

  /* ---- Voice Input (Microphone SpeechRecognition) ---- */
  _toggleVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      this.toast.info('Voice input is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    if (this._listening) {
      if (this._recognition) this._recognition.stop();
      this._listening = false;
      this.micBtn.classList.remove('listening');
      return;
    }

    this._recognition = new SpeechRecognition();
    this._recognition.continuous = false;
    this._recognition.interimResults = true;
    this._recognition.lang = this.sourceLang.value === 'auto' ? 'en-US' : this.sourceLang.value;

    this._listening = true;
    this.micBtn.classList.add('listening');
    this.toast.info('Listening… Speak into your microphone.');

    this._recognition.onresult = (e) => {
      let transcript = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        transcript += e.results[i][0].transcript;
      }
      this.sourceText.value = transcript;
      this._updateCharCount();
      this._autoResizeTextarea();
    };

    this._recognition.onerror = (e) => {
      this._listening = false;
      this.micBtn.classList.remove('listening');
      this.toast.error(`Speech recognition error: ${e.error}`);
    };

    this._recognition.onend = () => {
      this._listening = false;
      this.micBtn.classList.remove('listening');
    };

    this._recognition.start();
  }

  /* ---- Favorite Current Translation ---- */
  _toggleFavoriteCurrent() {
    const srcText = this.sourceText.value.trim();
    const tgtText = this.outputText.textContent.trim();

    if (!srcText || !tgtText) {
      this.toast.info('Translate some text first before bookmarking.');
      return;
    }

    const idx = this._favorites.findIndex(f => f.sourceText === srcText && f.translatedText === tgtText);

    if (idx >= 0) {
      this._favorites.splice(idx, 1);
      this.favBtn.classList.remove('is-fav');
      this.toast.info('Removed from favorites.');
    } else {
      this._favorites.unshift({
        id: Date.now(),
        sourceLang: this.sourceLang.value,
        targetLang: this.targetLang.value,
        sourceText: srcText,
        translatedText: tgtText,
        timestamp: new Date().toISOString(),
      });
      this.favBtn.classList.add('is-fav');
      this.toast.success('Saved to favorites!');
    }

    this._saveStorage('lv_favorites', this._favorites);
    this._renderDrawer();
  }

  _updateFavButtonState(srcText, tgtText) {
    if (!this.favBtn) return;
    const isFav = this._favorites.some(f => f.sourceText === srcText && f.translatedText === tgtText);
    if (isFav) this.favBtn.classList.add('is-fav');
    else       this.favBtn.classList.remove('is-fav');
  }

  /* ---- PDF Export (jsPDF) ---- */
  _downloadPDF() {
    const srcText = this.sourceText.value.trim();
    const tgtText = this.outputText.textContent.trim();

    if (!srcText || !tgtText) {
      this.toast.info('Nothing to export yet. Complete a translation first.');
      return;
    }

    if (!window.jspdf || !window.jspdf.jsPDF) {
      this.toast.error('PDF exporter library failed to load.');
      return;
    }

    try {
      const { jsPDF } = window.jspdf;
      const doc = new jsPDF();

      const srcLangName = this.sourceLang.options[this.sourceLang.selectedIndex]?.text || 'Source';
      const tgtLangName = this.targetLang.options[this.targetLang.selectedIndex]?.text || 'Target';

      // PDF Title Header
      doc.setFillColor(10, 10, 34);
      doc.rect(0, 0, 210, 30, 'F');
      doc.setTextColor(77, 143, 255);
      doc.setFontSize(20);
      doc.setFont('helvetica', 'bold');
      doc.text('LinguaVerse Translation Report', 14, 18);

      // Metadata
      doc.setTextColor(148, 163, 184);
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 25);

      // Section: Source Text
      doc.setTextColor(15, 23, 42);
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text(`Source Text (${srcLangName}):`, 14, 45);

      doc.setFontSize(11);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(51, 65, 85);
      const srcLines = doc.splitTextToSize(srcText, 180);
      doc.text(srcLines, 14, 53);

      let yPos = 53 + (srcLines.length * 6) + 12;

      // Section: Translated Text
      doc.setTextColor(124, 58, 237);
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text(`Translation (${tgtLangName}):`, 14, yPos);

      doc.setFontSize(11);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(15, 23, 42);
      const tgtLines = doc.splitTextToSize(tgtText, 180);
      doc.text(tgtLines, 14, yPos + 8);

      // Save PDF file
      doc.save(`LinguaVerse_${srcLangName}_to_${tgtLangName}.pdf`);
      this.toast.success('PDF document downloaded!');
    } catch (err) {
      console.error('PDF generation error:', err);
      this.toast.error('Failed to generate PDF document.');
    }
  }

  /* ---- History & Drawer Management ---- */
  _saveToHistory(item) {
    // Abort saving if history logging is disabled in settings
    if (this.settingHistory && !this.settingHistory.checked) {
      return;
    }

    // Avoid duplicate adjacent history entries
    if (this._history.length > 0) {
      const top = this._history[0];
      if (top.sourceText === item.sourceText && top.targetLang === item.targetLang) {
        return;
      }
    }

    this._history.unshift(item);
    if (this._history.length > 50) this._history.pop(); // Max 50 items
    this._saveStorage('lv_history', this._history);
    this._renderDrawer();
  }

  _switchDrawerTab(tab) {
    if (tab === 'history') {
      this.tabHistory.classList.add('active');
      this.tabHistory.setAttribute('aria-selected', 'true');
      this.tabFavorites.classList.remove('active');
      this.tabFavorites.setAttribute('aria-selected', 'false');
      this.panelHistory.style.display = 'block';
      this.panelFavorites.style.display = 'none';
    } else {
      this.tabFavorites.classList.add('active');
      this.tabFavorites.setAttribute('aria-selected', 'true');
      this.tabHistory.classList.remove('active');
      this.tabHistory.setAttribute('aria-selected', 'false');
      this.panelFavorites.style.display = 'block';
      this.panelHistory.style.display = 'none';
    }
  }

  _clearCurrentDrawerTab() {
    const isHistory = this.tabHistory.classList.contains('active');
    if (isHistory) {
      this._history = [];
      this._saveStorage('lv_history', []);
      this.toast.info('History cleared.');
    } else {
      this._favorites = [];
      this._saveStorage('lv_favorites', []);
      this.toast.info('Favorites cleared.');
    }
    this._renderDrawer();
  }

  _renderDrawer() {
    if (this.historyCount)   this.historyCount.textContent = this._history.length;
    if (this.favoritesCount) this.favoritesCount.textContent = this._favorites.length;

    // Render History
    if (this.historyList) {
      if (this._history.length === 0) {
        this.historyList.innerHTML = '<div class="empty-drawer-msg">No recent translations yet</div>';
      } else {
        this.historyList.innerHTML = this._history.map(item => this._createDrawerItemHTML(item)).join('');
        this._bindDrawerItemEvents(this.historyList, this._history);
      }
    }

    // Render Favorites
    if (this.favoritesList) {
      if (this._favorites.length === 0) {
        this.favoritesList.innerHTML = '<div class="empty-drawer-msg">No bookmarked translations yet</div>';
      } else {
        this.favoritesList.innerHTML = this._favorites.map(item => this._createDrawerItemHTML(item, true)).join('');
        this._bindDrawerItemEvents(this.favoritesList, this._favorites);
      }
    }
  }

  _createDrawerItemHTML(item, isFavList = false) {
    const isFav = this._favorites.some(f => f.sourceText === item.sourceText && f.translatedText === item.translatedText);
    return `
      <div class="drawer-item" data-id="${item.id}">
        <div class="drawer-item-content" data-action="load">
          <div class="drawer-item-langs">
            <span>${item.sourceLang}</span>
            <i class="bi bi-arrow-right" aria-hidden="true"></i>
            <span>${item.targetLang}</span>
          </div>
          <div class="drawer-item-text">${this._escapeHTML(item.sourceText)}</div>
          <div class="drawer-item-target">${this._escapeHTML(item.translatedText)}</div>
        </div>
        <div class="drawer-item-actions">
          <button class="icon-btn fav-item-btn ${isFav ? 'is-fav' : ''}" data-action="fav" title="Bookmark">
            <i class="bi ${isFav ? 'bi-star-fill' : 'bi-star'}" aria-hidden="true"></i>
          </button>
          <button class="icon-btn del-item-btn" data-action="delete" title="Delete">
            <i class="bi bi-trash" aria-hidden="true"></i>
          </button>
        </div>
      </div>
    `;
  }

  _bindDrawerItemEvents(container, listRef) {
    container.querySelectorAll('.drawer-item').forEach(el => {
      const id = Number(el.dataset.id);
      const item = listRef.find(i => i.id === id);
      if (!item) return;

      // Click content → load back into translator
      const contentEl = el.querySelector('[data-action="load"]');
      contentEl.addEventListener('click', () => {
        if (Array.from(this.sourceLang.options).some(o => o.value === item.sourceLang)) {
          this.sourceLang.value = item.sourceLang;
        }
        if (Array.from(this.targetLang.options).some(o => o.value === item.targetLang)) {
          this.targetLang.value = item.targetLang;
        }
        this.sourceText.value = item.sourceText;
        this._updateCharCount();
        this._autoResizeTextarea();
        this._showOutput(item.translatedText);
        this._updateFavButtonState(item.sourceText, item.translatedText);
        this.toast.info('Loaded translation from drawer.');
      });

      // Toggle favorite button
      const favBtn = el.querySelector('[data-action="fav"]');
      favBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const fIdx = this._favorites.findIndex(f => f.sourceText === item.sourceText && f.translatedText === item.translatedText);
        if (fIdx >= 0) {
          this._favorites.splice(fIdx, 1);
        } else {
          this._favorites.unshift(item);
        }
        this._saveStorage('lv_favorites', this._favorites);
        this._renderDrawer();
        this._updateFavButtonState(this.sourceText.value.trim(), this.outputText.textContent.trim());
      });

      // Delete button
      const delBtn = el.querySelector('[data-action="delete"]');
      delBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = listRef.findIndex(i => i.id === id);
        if (idx >= 0) {
          listRef.splice(idx, 1);
          const key = container === this.historyList ? 'lv_history' : 'lv_favorites';
          this._saveStorage(key, listRef);
          this._renderDrawer();
        }
      });
    });
  }

  _escapeHTML(str) {
    return str.replace(/[&<>'"]/g, tag => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[tag] || tag));
  }

  _delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /* ---- Show Output ---- */
  _showOutput(text, detectedLang = null) {
    if (this.skeletonLoader) this.skeletonLoader.classList.add('d-none');
    this.outputPlaceholder.style.display = 'none';
    this.outputText.style.display        = 'block';
    this.outputText.textContent          = text;
    this.outputText.setAttribute('lang', this.targetLang.value || '');

    // Output char count
    if (this.outChars) this.outChars.textContent = text.length;
    if (this.outputCharCount) this.outputCharCount.style.display = 'inline-flex';

    // Detected language badge
    if (detectedLang && this.sourceLang.value === 'auto') {
      if (this.detectedLangName) this.detectedLangName.textContent = detectedLang.toUpperCase();
      if (this.detectedBadge)    this.detectedBadge.style.display = 'inline-flex';
    }

    // Animate in
    if (window.gsap) {
      gsap.from(this.outputText, {
        opacity: 0, y: 10, duration: 0.45, ease: 'power3.out',
      });
    }
  }

  /* ---- Reset Output ---- */
  _resetOutput(showSkeleton = false) {
    this.outputText.textContent          = '';
    this.outputText.style.display        = 'none';

    if (showSkeleton) {
      this.outputPlaceholder.style.display = 'none';
      if (this.skeletonLoader) this.skeletonLoader.classList.remove('d-none');
    } else {
      if (this.skeletonLoader) this.skeletonLoader.classList.add('d-none');
      this.outputPlaceholder.style.display = '';
    }

    if (this.detectedBadge)    this.detectedBadge.style.display = 'none';
    if (this.outputCharCount)  this.outputCharCount.style.display = 'none';
  }

  /* ---- Loading State ---- */
  _setLoading(isLoading) {
    this._loading = isLoading;
    this.translateBtn.disabled = isLoading;
    if (this.swapBtn) this.swapBtn.disabled = isLoading;
    if (this.clearBtn) this.clearBtn.disabled = isLoading;
    if (this.sourceText) this.sourceText.readOnly = isLoading;

    if (isLoading) {
      this.translateBtn.classList.add('is-loading');
      this.translateBtn.classList.remove('is-success');
    } else {
      this.translateBtn.classList.remove('is-loading');
    }
  }

  /* ---- Success State (auto-resets after 2 s) ---- */
  _showSuccessState() {
    this._setLoading(false);
    this.translateBtn.classList.add('is-success');
    this.translateBtn.classList.add('success-flash');

    // Brief success glow
    if (window.gsap) {
      gsap.to(this.translateBtn, {
        boxShadow: '0 0 0 1px rgba(16,185,129,0.6), 0 6px 30px rgba(16,185,129,0.5), 0 0 80px rgba(16,185,129,0.2)',
        duration:  0.3,
        ease:      'power2.out',
        onComplete: () => {
          gsap.to(this.translateBtn, {
            boxShadow: '',
            duration:  0.8,
            delay:     1.5,
            ease:      'power2.in',
          });
        },
      });
    }

    setTimeout(() => {
      this.translateBtn.classList.remove('is-success', 'success-flash');
      this.translateBtn.disabled = false;
      this._loading = false;
    }, 2200);
  }

  /* ---- Copy ---- */
  async _handleCopy() {
    const text = this.outputText.textContent.trim();
    if (!text) {
      this.toast.info('Nothing to copy yet.');
      return;
    }

    try {
      await navigator.clipboard.writeText(text);
      this.copyIcon.className = 'bi bi-check-lg';

      if (window.gsap) {
        gsap.from(this.copyBtn, { scale: 1.35, duration: 0.3, ease: 'back.out(2)' });
      }

      this.toast.success('Copied to clipboard!');
      setTimeout(() => { this.copyIcon.className = 'bi bi-copy'; }, 2200);
    } catch (_) {
      // Fallback for older browsers
      try {
        const el = document.createElement('textarea');
        el.value = text;
        el.style.cssText = 'position:absolute;top:-9999px;left:-9999px';
        document.body.appendChild(el);
        el.select();
        document.execCommand('copy');
        el.remove();
        this.toast.success('Copied to clipboard!');
      } catch (_2) {
        this.toast.error('Copy failed — please select and copy manually.');
      }
    }
  }

  /* ---- Text-to-Speech ---- */
  _speak(text, lang, btn) {
    if (!window.speechSynthesis) {
      this.toast.info('Text-to-speech is not supported in this browser.');
      return;
    }

    // Toggle off if already speaking this source
    if (this._speaking) {
      window.speechSynthesis.cancel();
      this._speaking = false;
      document.querySelectorAll('.speak-btn.speaking').forEach(b => b.classList.remove('speaking'));
      return;
    }

    const utter = new SpeechSynthesisUtterance(text);
    utter.lang  = lang;
    utter.rate  = 0.9;

    this._speaking = true;
    btn.classList.add('speaking');

    utter.onend = utter.onerror = () => {
      this._speaking = false;
      btn.classList.remove('speaking');
    };

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);
  }

  /* ---- Error Banner ---- */
  _showError(message) {
    if (!this.errorBanner || !this.errorText) return;
    this.errorText.textContent = message;
    this.errorBanner.style.display = 'flex';

    if (window.gsap) {
      gsap.from(this.errorBanner, { opacity: 0, y: -8, duration: 0.3, ease: 'power2.out' });
    }
  }

  _hideError() {
    if (this.errorBanner) this.errorBanner.style.display = 'none';
  }

  /* ---- Shake Animation ---- */
  _shake(el) {
    if (!el) return;
    el.classList.remove('shake-anim');
    void el.offsetWidth; // reflow
    el.classList.add('shake-anim');
    el.addEventListener('animationend', () => el.classList.remove('shake-anim'), { once: true });
  }
}

/* ================================================================
   4. GSAP ENTRANCE ANIMATION
   ================================================================ */
function runEntranceAnimation() {
  if (!window.gsap) return;

  const tl = gsap.timeline({
    defaults: { ease: 'power3.out' },
  });

  // Navbar slides down
  if (document.getElementById('navbar')) {
    tl.from('#navbar', {
      y: -70, opacity: 0, duration: 0.65,
    });
  }

  // Hero badge pops
  if (document.getElementById('header-badge')) {
    tl.from('#header-badge', {
      y: 20, opacity: 0, scale: 0.8, duration: 0.55,
    }, '-=0.25');
  }

  // Main heading
  if (document.getElementById('main-heading')) {
    tl.from('#main-heading', {
      y: 28, opacity: 0, duration: 0.65,
    }, '-=0.35');
  }

  // Subtitle
  if (document.getElementById('main-subtitle')) {
    tl.from('#main-subtitle', {
      y: 20, opacity: 0, duration: 0.5,
    }, '-=0.35');
  }

  // Glass card lifts in
  if (document.getElementById('translator-card')) {
    tl.from('#translator-card', {
      y: 50, opacity: 0, scale: 0.97, duration: 0.75,
    }, '-=0.25');
  }

  // Keyboard hints
  if (document.querySelector('.keyboard-hints')) {
    tl.from('.keyboard-hints', {
      opacity: 0, duration: 0.4,
    }, '-=0.2');
  }
}

/* ================================================================
   5. INTERSECTION OBSERVER — lazy reveal (future sections)
   ================================================================ */
function initScrollReveal() {
  const elements = document.querySelectorAll('[data-reveal]');
  if (!elements.length) return;

  const obs = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-up-anim');
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  elements.forEach(el => obs.observe(el));
}

/* ================================================================
   6. ENTRY POINT
   ================================================================ */
document.addEventListener('DOMContentLoaded', () => {

  // ── Three.js Earth Scene ──
  // Guard against missing WebGL support
  const canvas = document.getElementById('webgl-canvas');
  let scene = null;
  if (canvas && window.THREE) {
    try {
      scene = new EarthScene('webgl-canvas');
      window.earthSceneRef = scene;
    } catch (err) {
      console.warn('[LinguaVerse] Three.js failed to initialise:', err);
      // Hide canvas gracefully
      canvas.style.display = 'none';
    }
  }

  // ── Toast Manager ──
  const toast = new ToastManager('toast-container');

  // ── Translation UI ──
  const ui = new TranslationUI(toast);

  // ── GSAP Entrance ──
  runEntranceAnimation();

  // ── Scroll Reveal ──
  initScrollReveal();

  // ── Dismiss Page Loader Overlay ──
  const loader = document.getElementById('page-loader');
  if (loader) {
    setTimeout(() => {
      loader.classList.add('fade-out');
      setTimeout(() => loader.remove(), 500);
    }, 400);
  }

  // ── Welcome toast ──
  setTimeout(() => {
    toast.info('Connected to LinguaVerse Django REST API.', 4000);
  }, 2400);
});
