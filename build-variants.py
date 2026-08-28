#!/usr/bin/env python3
"""
Generate the atmosphere variants from index.html.

index.html stays the single source of truth. Each variant is that file with one
self-contained CSS+JS block injected — nothing else differs. Re-run after any
edit to the base:  python3 build-variants.py
"""
import os, shutil, pathlib

ROOT = pathlib.Path(__file__).parent
BASE = (ROOT / "index.html").read_text()
OUT  = ROOT / "variants"

# ---------------------------------------------------------------- 1. TILT
TILT_CSS = """
/* ---- atmosphere: tilt parallax ---- */
.dust{display:none}
/* the key light follows the pointer / device tilt */
.lighting{
  background:
    radial-gradient(72% 54% at var(--lx,50%) var(--ly,26%),
                    rgba(255,244,222,.26) 0%, transparent 62%),
    radial-gradient(130% 110% at 50% 45%, transparent 42%, rgba(28,18,8,.42) 100%);
}
/* the seal's shadow swings to match the light */
.seal img{
  filter:drop-shadow(calc(var(--sx,0px) * .28) calc(var(--sy,2px) * .22) 2px rgba(48,16,18,.48))
         drop-shadow(var(--sx,0px) var(--sy,9px) 16px rgba(48,16,18,.34));
}
/* and so does the sheen raking across the flap */
.env-flap .stock{background-position:calc(50% + var(--sheen,0%)) 0, calc(50% - var(--sheen,0%)) 0}
"""

TILT_JS = """
/* ---- atmosphere: tilt parallax ---- */
(function(){
  const cover = document.getElementById('cover');
  const tilt  = document.querySelector('.env-tilt');
  if (!tilt || matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const MAX = 3.2;                 // degrees of rotation at full deflection
  let tx = 0, ty = 0;              // target,  -1 .. 1
  let cx = 0, cy = 0;              // current, eased toward the target

  (function frame(){
    cx += (tx - cx) * .075;
    cy += (ty - cy) * .075;
    tilt.style.transform = `rotateX(${(-cy*MAX).toFixed(3)}deg) rotateY(${(cx*MAX).toFixed(3)}deg)`;
    cover.style.setProperty('--lx',    (50 + cx*17).toFixed(2) + '%');
    cover.style.setProperty('--ly',    (26 + cy*13).toFixed(2) + '%');
    cover.style.setProperty('--sx',    (-cx*8).toFixed(2) + 'px');
    cover.style.setProperty('--sy',    (9 - cy*8).toFixed(2) + 'px');
    cover.style.setProperty('--sheen', (cx*14).toFixed(2) + '%');
    requestAnimationFrame(frame);
  })();

  const clamp = v => Math.max(-1, Math.min(1, v));

  addEventListener('pointermove', e => {
    tx = clamp((e.clientX / innerWidth  - .5) * 2);
    ty = clamp((e.clientY / innerHeight - .5) * 2);
  }, {passive:true});

  document.addEventListener('pointerleave', () => { tx = 0; ty = 0; });

  // phone tilt: gamma = left/right, beta = front/back (45deg = held upright-ish)
  addEventListener('deviceorientation', e => {
    if (e.gamma == null) return;
    tx = clamp(e.gamma / 26);
    ty = clamp(((e.beta == null ? 45 : e.beta) - 45) / 26);
  }, {passive:true});
})();
"""

# ---------------------------------------------------------------- 2. GOLD LEAF
GOLD_CSS = """
/* ---- atmosphere: gold-leaf inclusions ---- */
.dust{display:none}
.leaf{position:absolute; inset:0; pointer-events:none; overflow:hidden}
.leaf i{
  position:absolute; display:block;
  border-radius:50%;
  background:linear-gradient(118deg,#f9ecc4 0%,#d3ae66 48%,#8d7232 100%);
  box-shadow:0 0 1px rgba(255,240,205,.55);
}
/* only a quarter of the flecks ever catch the light, and rarely */
.leaf i.g{animation:glint 11s ease-in-out infinite}
@keyframes glint{
  0%,90%,100%{filter:brightness(1)}
  95%{filter:brightness(2.8) saturate(1.2)}
}
"""

GOLD_JS = """
/* ---- atmosphere: gold-leaf inclusions ---- */
(function(){
  // flecks live inside each panel, so they are clipped by it and travel with it
  const panels = [['.env-pocket',64], ['.env-flap',46], ['.env-sheet',26], ['.letter',22]];
  for (const [sel, count] of panels){
    const panel = document.querySelector(sel);
    if (!panel) continue;
    const layer = document.createElement('div');
    layer.className = 'leaf';
    for (let i = 0; i < count; i++){
      const f = document.createElement('i');
      const w = 1.1 + Math.random()*3.2;             // a sliver, not a dot
      f.style.width  = w.toFixed(2) + 'px';
      f.style.height = (w * (.32 + Math.random()*.42)).toFixed(2) + 'px';
      f.style.left   = (Math.random()*100).toFixed(2) + '%';
      f.style.top    = (Math.random()*100).toFixed(2) + '%';
      f.style.transform = `rotate(${(Math.random()*180).toFixed(1)}deg)`;
      f.style.opacity   = (.22 + Math.random()*.46).toFixed(2);
      if (Math.random() < .26){
        f.classList.add('g');
        f.style.animationDelay = (-Math.random()*11).toFixed(2) + 's';
      }
      layer.appendChild(f);
    }
    panel.appendChild(layer);
  }
})();
"""

# ---------------------------------------------------------------- 3. SHIMMER
SHIMMER_CSS = """
/* ---- atmosphere: foil shimmer sweep ---- */
.dust{display:none}

/* the band is masked by the seal's own alpha, so it only lights the wax */
.seal::after{
  content:""; position:absolute; inset:0; pointer-events:none;
  -webkit-mask-image:url("assets/seal.png");  mask-image:url("assets/seal.png");
  -webkit-mask-size:contain;   mask-size:contain;
  -webkit-mask-repeat:no-repeat; mask-repeat:no-repeat;
  -webkit-mask-position:center; mask-position:center;
  background:linear-gradient(102deg,
      transparent 40%, rgba(255,236,208,.78) 50%, transparent 60%);
  background-size:300% 100%;
  background-position:150% 0;
  mix-blend-mode:screen;
}
.seal.sweep::after{animation:sweep 1.6s cubic-bezier(.36,0,.2,1)}

/* the same band travelling the foil rules — masked to the border only */
.foil-frame::before{
  content:""; position:absolute; inset:0; pointer-events:none;
  padding:1px;
  background:linear-gradient(102deg,
      transparent 42%, rgba(255,240,214,.9) 50%, transparent 58%);
  background-size:300% 100%;
  background-position:150% 0;
  -webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite:xor;  mask-composite:exclude;
}
.foil-frame.sweep::before{animation:sweep 1.6s cubic-bezier(.36,0,.2,1)}

@keyframes sweep{
  from{background-position:150% 0}
  to  {background-position:-70% 0}
}
"""

SHIMMER_JS = """
/* ---- atmosphere: foil shimmer sweep ---- */
(function(){
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const targets = [document.getElementById('seal'), document.querySelector('.foil-frame')]
                    .filter(Boolean);
  function sweep(){
    for (const t of targets){
      t.classList.remove('sweep');
      void t.offsetWidth;            // restart the animation
      t.classList.add('sweep');
    }
  }
  setTimeout(sweep, 900);
  setInterval(sweep, 12000);
})();
"""

# ---------------------------------------------------------------- 4. CANDLELIGHT
CANDLE_CSS = """
/* ---- atmosphere: candlelight ---- */
.dust{display:none}
#cover{background:#100d0a}
.lighting{background:
  radial-gradient(70% 50% at 50% 24%, rgba(255,238,206,.14) 0%, transparent 60%),
  radial-gradient(130% 110% at 50% 45%, transparent 34%, rgba(24,14,6,.56) 100%)}

.candle{
  position:absolute; inset:-25%; pointer-events:none; z-index:8;
  background:radial-gradient(36% 30% at 50% 26%,
      rgba(255,216,152,.46) 0%, rgba(255,188,116,.18) 44%, transparent 72%);
  mix-blend-mode:soft-light;
  will-change:transform,opacity;
  animation:candleDrift 34s ease-in-out infinite alternate,
            candleFlicker 6.5s ease-in-out infinite;
}
/* a second, tighter core that breathes against the drift */
.candle::after{
  content:""; position:absolute; inset:0;
  background:radial-gradient(18% 15% at 50% 24%, rgba(255,228,178,.4), transparent 70%);
  animation:candleFlicker 4.1s ease-in-out infinite reverse;
}

@keyframes candleDrift{
  0%  {transform:translate(-4.5%,-2%)  scale(1)}
  50% {transform:translate(3.5%, 2.5%) scale(1.07)}
  100%{transform:translate(-1.5%,3.5%) scale(1.02)}
}
/* uneven stops — a real flame never flickers on a metronome */
@keyframes candleFlicker{
  0%{opacity:.93}   7%{opacity:1}    11%{opacity:.85}  16%{opacity:.99}
  23%{opacity:.89}  31%{opacity:1}   38%{opacity:.87}  44%{opacity:.97}
  55%{opacity:.91}  63%{opacity:1}   71%{opacity:.86}  79%{opacity:.98}
  88%{opacity:.92} 100%{opacity:.95}
}
"""

CANDLE_JS = """
/* ---- atmosphere: candlelight ---- */
(function(){
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const el = document.createElement('div');
  el.className = 'candle';
  document.getElementById('cover').appendChild(el);
})();
"""

VARIANTS = {
  "tilt":    ("Tilt parallax",         TILT_CSS,    TILT_JS),
  "gold":    ("Gold-leaf inclusions",  GOLD_CSS,    GOLD_JS),
  "shimmer": ("Foil shimmer sweep",    SHIMMER_CSS, SHIMMER_JS),
  "candle":  ("Candlelight",           CANDLE_CSS,  CANDLE_JS),
}

# a small corner badge so you always know which one you are looking at
BADGE_CSS = """
.fx-badge{
  position:fixed; left:14px; bottom:14px; z-index:999;
  font:400 9.5px/1 "Jost",sans-serif; letter-spacing:.3em; text-transform:uppercase;
  color:rgba(246,241,232,.42); background:rgba(0,0,0,.32);
  padding:8px 12px; border:1px solid rgba(246,241,232,.14); border-radius:2px;
  pointer-events:none; backdrop-filter:blur(4px);
}
"""

if OUT.exists():
    shutil.rmtree(OUT)

for key, (label, css, js) in VARIANTS.items():
    d = OUT / key
    d.mkdir(parents=True)

    html = BASE
    head = f"<script>window.FX_NO_DUST=true</script>\n<style>{css}{BADGE_CSS}</style>\n</head>"
    html = html.replace("</head>", head, 1)
    html = html.replace("</body>", f'<div class="fx-badge">{label}</div>\n<script>{js}</script>\n</body>', 1)

    (d / "index.html").write_text(html)

    # share one copy of the assets rather than duplicating the seal four times
    link = d / "assets"
    if not link.exists():
        os.symlink("../../assets", link)

    print(f"  variants/{key}/  — {label}")

print(f"\nBuilt {len(VARIANTS)} variants from index.html")
