import os
import json
import math
import subprocess
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Lock working directory to the folder where app.py is saved
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# All 9 species specified by Dr. Gagan Raj Gupta (IIT Bhilai CSE)
SPECIES_DATA = {
    "mango": {
        "name": "Mango",
        "scientific": "Mangifera indica",
        "habit": "Evergreen (Continuous Leaf Turnover)",
        "max_height": 13.5,
        "max_radius": 6.2,
        "base_density": 0.90,
        "min_density": 0.76,
        "shed_day": 75,
        "blend_file": "Mango.blend"
    },
    "banana": {
        "name": "Banana",
        "scientific": "Musa acuminata",
        "habit": "Herbaceous Perennial (Continuous Frond Replacement)",
        "max_height": 4.8,
        "max_radius": 2.9,
        "base_density": 0.78,
        "min_density": 0.62,
        "shed_day": 110,
        "blend_file": "Banana.blend"
    },
    "amla": {
        "name": "Amla (Indian Gooseberry)",
        "scientific": "Phyllanthus emblica",
        "habit": "Semi-Deciduous (Spring Branchlet Shedding)",
        "max_height": 9.5,
        "max_radius": 4.2,
        "base_density": 0.68,
        "min_density": 0.28,
        "shed_day": 80,
        "blend_file": "Amla.blend"
    },
    "sheesham": {
        "name": "Sheesham (Indian Rosewood)",
        "scientific": "Dalbergia sissoo",
        "habit": "Deciduous (Winter Shedding & Spring Flush)",
        "max_height": 14.0,
        "max_radius": 4.8,
        "base_density": 0.75,
        "min_density": 0.18,
        "shed_day": 45,
        "blend_file": "sheesham.blend"
    },
    "sagvan": {
        "name": "Sagvan (Teak)",
        "scientific": "Tectona grandis",
        "habit": "Deciduous (Dry-Season Leaf Shedding)",
        "max_height": 15.5,
        "max_radius": 5.4,
        "base_density": 0.85,
        "min_density": 0.14,
        "shed_day": 85,
        "blend_file": "sagvan.blend"
    },
    "kathal": {
        "name": "Kathal (Jackfruit)",
        "scientific": "Artocarpus heterophyllus",
        "habit": "Evergreen (Continuous Leaf Fall & Regrowth)",
        "max_height": 12.5,
        "max_radius": 5.6,
        "base_density": 0.92,
        "min_density": 0.80,
        "shed_day": 65,
        "blend_file": "kathal.blend"
    },
    "jamun": {
        "name": "Jamun (Malabar Plum)",
        "scientific": "Syzygium cumini",
        "habit": "Evergreen (Spring Leaf Renewal)",
        "max_height": 14.5,
        "max_radius": 5.2,
        "base_density": 0.86,
        "min_density": 0.70,
        "shed_day": 60,
        "blend_file": "Jamun.blend"
    },
    "ber": {
        "name": "Ber (Indian Jujube)",
        "scientific": "Ziziphus mauritiana",
        "habit": "Semi-Deciduous (Summer Leaf Shedding)",
        "max_height": 8.5,
        "max_radius": 4.3,
        "base_density": 0.72,
        "min_density": 0.30,
        "shed_day": 135,
        "blend_file": "Ber.blend"
    },
    "papaya": {
        "name": "Papaya",
        "scientific": "Carica papaya",
        "habit": "Rosette Perennial (Continuous Lower-Leaf Drop)",
        "max_height": 6.2,
        "max_radius": 2.3,
        "base_density": 0.62,
        "min_density": 0.48,
        "shed_day": 95,
        "blend_file": "Papaya.blend"
    }
}

def auto_convert_blend_files():
    """Optional: exports .blend files to static/models/*.glb if Blender is installed."""
    os.makedirs("static/models", exist_ok=True)
    os.makedirs("animations", exist_ok=True)
    blender_paths = ["/Applications/Blender.app/Contents/MacOS/Blender", "blender"]
    blender_bin = next((p for p in blender_paths if os.path.exists(p)), None)
    if not blender_bin:
        return
    for key, info in SPECIES_DATA.items():
        candidates = [
            os.path.join("animations", info["blend_file"]),
            os.path.join("animations", info["blend_file"].lower()),
            info["blend_file"],
            info["blend_file"].lower()
        ]
        blend_path = next((p for p in candidates if os.path.exists(p)), None)
        glb_path = os.path.abspath(os.path.join("static/models", f"{key}.glb"))
        if blend_path and not os.path.exists(glb_path):
            expr = f"import bpy; bpy.ops.export_scene.gltf(filepath=r'{glb_path}', export_format='GLB', export_animations=True)"
            try:
                subprocess.run([blender_bin, "-b", blend_path, "--python-expr", expr], check=True)
            except Exception:
                pass

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tree Growth, Leaf Phenology & Solar Shading Simulator</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        :root { color-scheme: light; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f1f5f9;
            color: #0f172a;
            display: grid;
            grid-template-columns: 325px 1fr 350px;
            height: 100vh;
            overflow: hidden;
        }
        .sidebar {
            background: #ffffff;
            border-right: 1px solid #cbd5e1;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 11px;
            overflow-y: auto;
        }
        .brand h1 { font-size: 16px; font-weight: 700; color: #065f46; }
        .brand p { font-size: 11.5px; color: #475569; margin-top: 2px; }
        .control-box {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 10px 12px;
            display: flex;
            flex-direction: column;
            gap: 7px;
        }
        .field { display: flex; flex-direction: column; gap: 3px; }
        label { font-size: 11.5px; font-weight: 600; color: #334155; display: flex; justify-content: space-between; }
        label span { color: #059669; font-weight: 700; }
        select {
            padding: 7px 8px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            background: #ffffff;
            color: #0f172a;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
        }
        input[type="range"] { width: 100%; accent-color: #059669; cursor: pointer; }
        .btn-row { display: flex; gap: 6px; }
        button {
            flex: 1;
            padding: 7px 8px;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            background: #ffffff;
            color: #1e293b;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.15s;
        }
        button:hover { background: #f1f5f9; }
        button.primary { background: #059669; color: #ffffff; border-color: #059669; }
        button.primary:hover { background: #047857; }
        .center-stage { display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        .metrics-bar {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            padding: 12px 16px;
            background: #ffffff;
            border-bottom: 1px solid #cbd5e1;
        }
        .metric-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 9px 11px;
        }
        .metric-card .lbl { font-size: 10.5px; color: #64748b; text-transform: uppercase; font-weight: 700; }
        .metric-card .val { font-size: 17px; font-weight: 700; color: #0f172a; margin-top: 2px; }
        .metric-card .sub { font-size: 11px; color: #059669; margin-top: 2px; font-weight: 600; }
        .viewport-wrap { flex: 1; position: relative; background: #dbeafe; overflow: hidden; }
        #canvas-holder { width: 100%; height: 100%; display: block; }
        .overlay-top { position: absolute; top: 12px; left: 12px; display: flex; gap: 8px; flex-wrap: wrap; pointer-events: none; }
        .pill {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid #cbd5e1;
            padding: 5px 11px;
            border-radius: 20px;
            font-size: 11.5px;
            font-weight: 600;
            color: #065f46;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }
        .pill.amber { color: #92400e; background: rgba(254, 243, 199, 0.95); border-color: #fde68a; }
        .cam-bar { position: absolute; bottom: 12px; left: 12px; display: flex; gap: 6px; }
        .cam-bar button { padding: 6px 10px; background: rgba(255,255,255,0.92); }
        .right-panel {
            background: #ffffff;
            border-left: 1px solid #cbd5e1;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            overflow-y: auto;
        }
        .diagram-card {
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 9px;
            background: #f8fafc;
        }
        .diagram-card h3 {
            font-size: 11.5px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 5px;
            display: flex;
            justify-content: space-between;
        }
        .diagram-card h3 span { color: #64748b; font-weight: 500; }
        canvas.diagram-2d {
            width: 100%;
            height: 155px;
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            display: block;
        }
        .formula-box {
            font-size: 11px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 9px;
            line-height: 1.5;
            color: #334155;
        }
        .formula-box code {
            font-family: ui-monospace, Menlo, monospace;
            background: #e2e8f0;
            padding: 1px 4px;
            border-radius: 3px;
            font-size: 10.5px;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="brand">
            <h1>Tree Shading & Phenology Lab</h1>
            <p>3D Growth, Leaf Fall & Solar Shadow Model</p>
        </div>

        <div class="control-box">
            <div class="field">
                <label for="species">Tree Species (All 9 Required)</label>
                <select id="species">
                    <option value="mango">1. Mango (Mangifera indica)</option>
                    <option value="banana">2. Banana (Musa acuminata)</option>
                    <option value="amla">3. Amla (Phyllanthus emblica)</option>
                    <option value="sheesham">4. Sheesham (Dalbergia sissoo)</option>
                    <option value="sagvan">5. Sagvan / Teak (Tectona grandis)</option>
                    <option value="kathal">6. Kathal / Jackfruit (Artocarpus)</option>
                    <option value="jamun">7. Jamun (Syzygium cumini)</option>
                    <option value="ber">8. Ber / Jujube (Ziziphus mauritiana)</option>
                    <option value="papaya">9. Papaya (Carica papaya)</option>
                </select>
            </div>
        </div>

        <div class="control-box">
            <div class="field">
                <label>Tree Growth (Sapling → Maturity) <span id="growthLbl">85%</span></label>
                <input type="range" id="growth" min="5" max="100" value="85">
            </div>
            <div class="btn-row">
                <button id="playGrowthBtn" class="primary">▶ Animate Growth</button>
                <button id="resetGrowthBtn">Sapling (10%)</button>
            </div>
        </div>

        <div class="control-box">
            <div class="field">
                <label>Time of Day (Solar Angle) <span id="hourLbl">13:30</span></label>
                <input type="range" id="hour" min="6.5" max="17.5" step="0.1" value="13.5">
            </div>
            <div class="btn-row">
                <button id="playSunBtn">☀ Animate Daily Sun</button>
            </div>
        </div>

        <div class="control-box">
            <div class="field">
                <label>Day of Year (Leaf Shed & Season) <span id="dayLbl">Day 172 (Jun)</span></label>
                <input type="range" id="day" min="1" max="365" value="172">
            </div>
            <div class="btn-row">
                <button id="playYearBtn" class="primary">🍂 Play Full Year (Leaf Cycle)</button>
            </div>
            <div class="btn-row">
                <button onclick="setDay(75)">Spring Shed</button>
                <button onclick="setDay(172)">Summer Lush</button>
                <button onclick="setDay(355)">Winter</button>
            </div>
        </div>

        <div class="control-box">
            <div class="field">
                <label>Latitude (°N - Bhilai Default) <span id="latLbl">21.2°N</span></label>
                <input type="range" id="lat" min="8" max="35" step="0.1" value="21.2">
            </div>
            <button id="exportCsvBtn">⬇ Export Data Table (CSV)</button>
        </div>

        <div class="formula-box">
            <strong>Mathematical Model:</strong><br>
            • Declination: <code>δ = 23.45° sin(360/365 × (284+N))</code><br>
            • Elevation: <code>sin(θ) = sin(Φ)sin(δ) + cos(Φ)cos(δ)cos(ω)</code><br>
            • Shadow Length: <code>L = H(t) / tan(θ)</code><br>
            • Effective Shade: <code>A_eff = π(R + L/2)R × η_leaf(N)</code>
        </div>
    </div>

    <div class="center-stage">
        <div class="metrics-bar">
            <div class="metric-card">
                <div class="lbl">Tree Size (H × 2R)</div>
                <div class="val" id="outH">12.4 m</div>
                <div class="sub" id="outR">Crown Radius: 5.5 m</div>
            </div>
            <div class="metric-card">
                <div class="lbl">Solar Angles (θ, δ)</div>
                <div class="val" id="outElev">68.5°</div>
                <div class="sub" id="outDec">Declination δ: +23.4°</div>
            </div>
            <div class="metric-card">
                <div class="lbl">Canopy Foliage & Shedding</div>
                <div class="val" id="outLeaf">100% Foliage</div>
                <div class="sub" id="outHabit">Continuous Leaf Fall</div>
            </div>
            <div class="metric-card">
                <div class="lbl">Land Area Shaded</div>
                <div class="val" id="outEff">112.4 m²</div>
                <div class="sub" id="outArea">Geometric Footprint: 128.0 m²</div>
            </div>
        </div>

        <div class="viewport-wrap">
            <div class="overlay-top">
                <div class="pill" id="phaseBadge">Stage 3: Full Maturity</div>
                <div class="pill amber" id="phenoBadge">Full Canopy (Continuous Leaf Fall)</div>
            </div>
            <div id="canvas-holder"></div>
            <div class="cam-bar">
                <button onclick="setCameraView(20, 13, 24)">3D Perspective</button>
                <button onclick="setCameraView(0.1, 36, 0.1)">Top-Down Map</button>
                <button onclick="setCameraView(0, 6, 28)">Side Elevation</button>
            </div>
        </div>
    </div>

    <div class="right-panel">
        <div class="diagram-card">
            <h3>1. 2D Solar Ray & Shadow Geometry <span>Side Profile</span></h3>
            <canvas id="sideCanvas" class="diagram-2d" width="315" height="155"></canvas>
        </div>
        <div class="diagram-card">
            <h3>2. 2D Land Shaded Area Footprint <span>Top-Down Plan</span></h3>
            <canvas id="topCanvas" class="diagram-2d" width="315" height="155"></canvas>
        </div>
        <div class="diagram-card">
            <h3>3. Diurnal & Annual Leaf-Shade Curves <span>Day & Year</span></h3>
            <canvas id="curveCanvas" class="diagram-2d" width="315" height="155"></canvas>
        </div>
    </div>

    <script>
        const SPECIES = {
            mango: { name: "Mango", sci: "Mangifera indica", habit: "Evergreen (Continuous Turnover)", maxH: 13.5, maxR: 6.2, baseD: 0.90, minD: 0.76, shedDay: 75, bark: 0x4a3525, leaf: 0x1e5622, flush: 0x7cb518, dry: 0xb58328 },
            banana: { name: "Banana", sci: "Musa acuminata", habit: "Herbaceous (Frond Replacement)", maxH: 4.8, maxR: 2.9, baseD: 0.78, minD: 0.62, shedDay: 110, bark: 0x6b8e23, leaf: 0x559e24, flush: 0x8ac926, dry: 0xc29b38 },
            amla: { name: "Amla", sci: "Phyllanthus emblica", habit: "Semi-Deciduous (Spring Shed)", maxH: 9.5, maxR: 4.2, baseD: 0.68, minD: 0.28, shedDay: 80, bark: 0x6e5d4f, leaf: 0x5c9436, flush: 0x80b918, dry: 0xc98a2c },
            sheesham: { name: "Sheesham", sci: "Dalbergia sissoo", habit: "Deciduous (Winter Leaf Drop)", maxH: 14.0, maxR: 4.8, baseD: 0.75, minD: 0.18, shedDay: 45, bark: 0x523824, leaf: 0x3b7a33, flush: 0x70e000, dry: 0xd97706 },
            sagvan: { name: "Sagvan (Teak)", sci: "Tectona grandis", habit: "Deciduous (Dry-Season Shedding)", maxH: 15.5, maxR: 5.4, baseD: 0.85, minD: 0.14, shedDay: 85, bark: 0x594433, leaf: 0x4d8228, flush: 0x84cc16, dry: 0xb45309 },
            kathal: { name: "Kathal (Jackfruit)", sci: "Artocarpus heterophyllus", habit: "Evergreen (Continuous Fall)", maxH: 12.5, maxR: 5.6, baseD: 0.92, minD: 0.80, shedDay: 65, bark: 0x382414, leaf: 0x164a1d, flush: 0x55a630, dry: 0xa16207 },
            jamun: { name: "Jamun", sci: "Syzygium cumini", habit: "Evergreen (Spring Renewal)", maxH: 14.5, maxR: 5.2, baseD: 0.86, minD: 0.70, shedDay: 60, bark: 0x5c5346, leaf: 0x265c2b, flush: 0x6ede8a, dry: 0xb45309 },
            ber: { name: "Ber (Jujube)", sci: "Ziziphus mauritiana", habit: "Semi-Deciduous (Summer Shed)", maxH: 8.5, maxR: 4.3, baseD: 0.72, minD: 0.30, shedDay: 135, bark: 0x473323, leaf: 0x48732e, flush: 0x80b918, dry: 0xca8a04 },
            papaya: { name: "Papaya", sci: "Carica papaya", habit: "Rosette (Lower-Leaf Drop)", maxH: 6.2, maxR: 2.3, baseD: 0.62, minD: 0.48, shedDay: 95, bark: 0x768064, leaf: 0x347d2c, flush: 0x70e000, dry: 0xd97706 }
        };

        const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        function dayToMonthStr(d) {
            const m = Math.min(11, Math.floor((d - 1) / 30.45));
            return `Day ${d} (${MONTHS[m]})`;
        }

        // Synchronous client+server math calculation
        function calculateMetrics(speciesKey, growthPct, hour, day, lat) {
            const sp = SPECIES[speciesKey] || SPECIES.mango;
            let phase, scaleH, scaleR;
            if (growthPct <= 30) {
                phase = "Stage 1: Sapling";
                scaleH = 0.12 + (growthPct / 30.0) * 0.23;
                scaleR = 0.10 + (growthPct / 30.0) * 0.20;
            } else if (growthPct <= 75) {
                phase = "Stage 2: Juvenile Tree";
                scaleH = 0.35 + ((growthPct - 30.0) / 45.0) * 0.45;
                scaleR = 0.30 + ((growthPct - 30.0) / 45.0) * 0.45;
            } else {
                phase = "Stage 3: Mature Tree";
                scaleH = 0.80 + ((growthPct - 75.0) / 25.0) * 0.20;
                scaleR = 0.75 + ((growthPct - 75.0) / 25.0) * 0.25;
            }

            const H = +(sp.maxH * scaleH).toFixed(2);
            const R = +(sp.maxR * scaleR).toFixed(2);

            // Annual Leaf Phenology (Shedding, Regrowth & Continuous Turnover)
            const diff = Math.abs(day - sp.shedDay);
            const circDiff = Math.min(diff, 365 - diff);
            const shedFactor = Math.exp(-Math.pow(circDiff / 36.0, 2));
            const currentDensity = sp.baseD - (sp.baseD - sp.minD) * shedFactor;
            const leafPct = Math.round((currentDensity / sp.baseD) * 100);

            let phenologyState;
            if (leafPct < 55) {
                phenologyState = "Seasonal Leaf Shedding (Bare Limbs)";
            } else if (shedFactor > 0.48) {
                phenologyState = "Active Leaf Shedding & Renewal";
            } else if (day > sp.shedDay && circDiff < 65) {
                phenologyState = "New Leaf Flushing & Regrowth";
            } else {
                phenologyState = "Full Canopy (Continuous Leaf Fall)";
            }

            // Cooper's Equation for Solar Declination & Elevation
            const dec = 23.45 * Math.sin((Math.PI / 180) * ((360 / 365) * (284 + day)));
            const ha = 15.0 * (hour - 12.0);
            const latR = lat * Math.PI / 180;
            const decR = dec * Math.PI / 180;
            const haR = ha * Math.PI / 180;

            const sinElev = Math.max(-1, Math.min(1, Math.sin(latR) * Math.sin(decR) + Math.cos(latR) * Math.cos(decR) * Math.cos(haR)));
            const elev = Math.max(3.0, Math.asin(sinElev) * 180 / Math.PI);

            const shadowLen = +Math.min(60.0, H / Math.tan(elev * Math.PI / 180)).toFixed(2);
            const semiMajor = R + shadowLen * 0.5;
            const semiMinor = R;
            const geomArea = +(Math.PI * semiMajor * semiMinor).toFixed(2);
            const effArea = +(geomArea * currentDensity).toFixed(2);

            const azRad = ((hour - 6.0) / 12.0) * Math.PI;
            const elRad = Math.max(6.0, elev) * Math.PI / 180;

            return {
                speciesKey,
                speciesName: sp.name,
                sciName: sp.sci,
                habit: sp.habit,
                phase,
                phenologyState,
                leafPct,
                shedFactor,
                currentDensity: +currentDensity.toFixed(2),
                scaleH,
                scaleR,
                H,
                R,
                dec: +dec.toFixed(2),
                elev: +elev.toFixed(2),
                shadowLen,
                geomArea,
                effArea,
                sunX: +(Math.cos(azRad) * Math.cos(elRad) * 30).toFixed(2),
                sunY: +(Math.sin(elRad) * 30).toFixed(2),
                sunZ: +(Math.sin(decR) * 12).toFixed(2)
            };
        }

        // --- THREE.JS SCENE & BUILT-IN ORBIT CONTROLLER ---
        const holder = document.getElementById('canvas-holder');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xdbeafe);

        const camera = new THREE.PerspectiveCamera(45, holder.clientWidth / holder.clientHeight, 0.1, 500);
        let camRadius = 30, camTheta = 0.72, camPhi = 1.12;
        const camTarget = new THREE.Vector3(0, 4.5, 0);

        function updateCameraPosition() {
            camera.position.x = camTarget.x + camRadius * Math.sin(camPhi) * Math.sin(camTheta);
            camera.position.y = camTarget.y + camRadius * Math.cos(camPhi);
            camera.position.z = camTarget.z + camRadius * Math.sin(camPhi) * Math.cos(camTheta);
            camera.lookAt(camTarget);
        }
        updateCameraPosition();

        function setCameraView(x, y, z) {
            const dx = x - camTarget.x, dy = y - camTarget.y, dz = z - camTarget.z;
            camRadius = Math.sqrt(dx * dx + dy * dy + dz * dz);
            camPhi = Math.acos(Math.max(-0.99, Math.min(0.99, dy / camRadius)));
            camTheta = Math.atan2(dx, dz);
            updateCameraPosition();
        }

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(holder.clientWidth, holder.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        holder.appendChild(renderer.domElement);

        // Built-in Mouse Drag Orbit + Scroll Wheel Zoom
        let isDragging = false, prevX = 0, prevY = 0;
        renderer.domElement.addEventListener('mousedown', (e) => { isDragging = true; prevX = e.clientX; prevY = e.clientY; });
        window.addEventListener('mouseup', () => { isDragging = false; });
        window.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const dx = e.clientX - prevX, dy = e.clientY - prevY;
            prevX = e.clientX; prevY = e.clientY;
            camTheta -= dx * 0.008;
            camPhi = Math.max(0.12, Math.min(Math.PI / 2 - 0.04, camPhi - dy * 0.008));
            updateCameraPosition();
        });
        renderer.domElement.addEventListener('wheel', (e) => {
            e.preventDefault();
            camRadius = Math.max(10, Math.min(75, camRadius + e.deltaY * 0.025));
            updateCameraPosition();
        }, { passive: false });

        // Lighting & Sun
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.58);
        scene.add(ambientLight);

        const sunLight = new THREE.DirectionalLight(0xfffbeb, 1.35);
        sunLight.castShadow = true;
        sunLight.shadow.mapSize.width = 2048;
        sunLight.shadow.mapSize.height = 2048;
        sunLight.shadow.camera.left = -35;
        sunLight.shadow.camera.right = 35;
        sunLight.shadow.camera.top = 35;
        sunLight.shadow.camera.bottom = -35;
        scene.add(sunLight);

        const sunOrb = new THREE.Mesh(
            new THREE.SphereGeometry(1.1, 16, 16),
            new THREE.MeshBasicMaterial({ color: 0xf59e0b })
        );
        scene.add(sunOrb);

        // Ground Terrain, Grid, Compass Ring & Shadow Measurement Ellipse
        const ground = new THREE.Mesh(
            new THREE.PlaneGeometry(110, 110),
            new THREE.MeshStandardMaterial({ color: 0xcbd5e1, roughness: 0.95 })
        );
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        scene.add(ground);

        const grid = new THREE.GridHelper(100, 50, 0x94a3b8, 0xbec8d4);
        grid.position.y = 0.01;
        scene.add(grid);

        const shadeEllipse = new THREE.Mesh(
            new THREE.CircleGeometry(1, 40),
            new THREE.MeshBasicMaterial({ color: 0x059669, transparent: true, opacity: 0.20, side: THREE.DoubleSide })
        );
        shadeEllipse.rotation.x = -Math.PI / 2;
        shadeEllipse.position.y = 0.02;
        scene.add(shadeEllipse);

        // --- HANDCRAFTED 3D TREE MODEL + CONTINUOUS FALLING LEAVES ---
        let treeRoot = null;
        let woodyGroup = null;
        let foliageMeshes = [];
        let fallingLeaves = [];
        let groundLitter = [];
        let leafMat = null;

        function makeBranch(p1, p2, rBot, rTop, mat) {
            const dir = new THREE.Vector3().subVectors(p2, p1);
            const len = dir.length();
            const geo = new THREE.CylinderGeometry(rTop, rBot, len, 7);
            geo.translate(0, len / 2, 0);
            geo.rotateX(Math.PI / 2);
            const mesh = new THREE.Mesh(geo, mat);
            mesh.position.copy(p1);
            mesh.lookAt(p2);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            return mesh;
        }

        function buildSpecies3DModel(speciesKey) {
            if (treeRoot) scene.remove(treeRoot);
            treeRoot = new THREE.Group();
            woodyGroup = new THREE.Group();
            foliageMeshes = [];
            fallingLeaves = [];
            groundLitter = [];

            const sp = SPECIES[speciesKey] || SPECIES.mango;
            const barkMat = new THREE.MeshStandardMaterial({ color: sp.bark, roughness: 0.92 });
            leafMat = new THREE.MeshStandardMaterial({ color: sp.leaf, roughness: 0.68, flatShading: true });

            if (speciesKey === "banana" || speciesKey === "papaya") {
                // Pseudostem / Unbranched Rosette Trunk
                const topY = speciesKey === "banana" ? 3.6 : 4.8;
                const rBase = speciesKey === "banana" ? 0.34 : 0.28;
                const stem = makeBranch(new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, topY, 0), rBase, rBase * 0.65, barkMat);
                woodyGroup.add(stem);

                // Fruit clusters (Banana bunch or Papaya ring under crown)
                const fruitMat = new THREE.MeshStandardMaterial({ color: speciesKey === "banana" ? 0x84a92c : 0xeab308, roughness: 0.6 });
                for (let i = 0; i < 5; i++) {
                    const a = (i / 5) * Math.PI * 2;
                    const f = new THREE.Mesh(new THREE.SphereGeometry(0.22, 8, 8), fruitMat);
                    f.scale.set(0.8, 1.5, 0.8);
                    f.position.set(Math.cos(a) * 0.3, topY - 0.45, Math.sin(a) * 0.3);
                    f.castShadow = true;
                    woodyGroup.add(f);
                }

                // Radiating arching fronds / palmate leaves
                const frondCount = speciesKey === "banana" ? 10 : 12;
                for (let i = 0; i < frondCount; i++) {
                    const angle = (i / frondCount) * Math.PI * 2 + (i % 2) * 0.2;
                    const tier = (i % 3) * 0.18;
                    const frondGroup = new THREE.Group();
                    frondGroup.position.set(0, topY - tier, 0);
                    frondGroup.rotation.y = angle;

                    const len = speciesKey === "banana" ? 2.5 : 1.8;
                    const wid = speciesKey === "banana" ? 0.72 : 0.55;
                    const blade = new THREE.Mesh(new THREE.BoxGeometry(len, 0.06, wid), leafMat);
                    blade.position.set(len * 0.48, 0.1, 0);
                    blade.rotation.z = -0.25 - (i % 3) * 0.12;
                    blade.castShadow = true;
                    blade.receiveShadow = true;
                    frondGroup.add(blade);

                    frondGroup.userData = { baseScale: 1.0, threshold: (i / frondCount) * 0.85 };
                    foliageMeshes.push(frondGroup);
                    treeRoot.add(frondGroup);
                }
            } else {
                // Woody Branching Trees (Mango, Sagvan, Sheesham, Kathal, Jamun, Amla, Ber)
                const trunkTop = speciesKey === "ber" ? 3.0 : (speciesKey === "amla" ? 3.6 : 4.6);
                const rBot = speciesKey === "kathal" || speciesKey === "mango" ? 0.65 : 0.48;
                const rTop = rBot * 0.68;

                // Root flares
                for (let r = 0; r < 4; r++) {
                    const ra = (r / 4) * Math.PI * 2;
                    woodyGroup.add(makeBranch(
                        new THREE.Vector3(Math.cos(ra) * rBot * 1.1, 0, Math.sin(ra) * rBot * 1.1),
                        new THREE.Vector3(0, 1.1, 0),
                        rBot * 0.45, rBot * 0.25, barkMat
                    ));
                }

                // Main trunk
                const pTop = new THREE.Vector3(0, trunkTop, 0);
                woodyGroup.add(makeBranch(new THREE.Vector3(0, 0, 0), pTop, rBot, rTop, barkMat));

                // Kathal cauliflorous jackfruits on trunk
                if (speciesKey === "kathal") {
                    const jfMat = new THREE.MeshStandardMaterial({ color: 0x657d22, roughness: 0.75 });
                    [[0.48, 2.0, 0.1], [-0.42, 2.6, 0.22], [0.1, 3.1, -0.45], [-0.2, 1.6, -0.4]].forEach(([x, y, z]) => {
                        const jf = new THREE.Mesh(new THREE.IcosahedronGeometry(0.32, 1), jfMat);
                        jf.scale.set(0.85, 1.45, 0.85);
                        jf.position.set(x, y, z);
                        jf.castShadow = true;
                        woodyGroup.add(jf);
                    });
                }

                // Primary & Secondary 3D Wooden Branches + Leaf Clusters
                const limbCount = 6;
                const spread = speciesKey === "mango" ? 3.6 : (speciesKey === "sagvan" ? 2.8 : 3.2);
                const crownH = speciesKey === "sagvan" || speciesKey === "jamun" ? 4.2 : 3.4;

                for (let i = 0; i < limbCount; i++) {
                    const a = (i / limbCount) * Math.PI * 2 + 0.3;
                    const pMid = new THREE.Vector3(
                        Math.cos(a) * spread * 0.65,
                        trunkTop + crownH * 0.48,
                        Math.sin(a) * spread * 0.65
                    );
                    woodyGroup.add(makeBranch(new THREE.Vector3(0, trunkTop - 0.3, 0), pMid, rTop * 0.72, rTop * 0.42, barkMat));

                    // Two secondary fork twigs per primary branch
                    for (let sub = -1; sub <= 1; sub += 2) {
                        const subA = a + sub * 0.42;
                        const pTip = new THREE.Vector3(
                            Math.cos(subA) * spread,
                            trunkTop + crownH * (0.72 + (i % 2) * 0.2),
                            Math.sin(subA) * spread
                        );
                        woodyGroup.add(makeBranch(pMid, pTip, rTop * 0.40, rTop * 0.18, barkMat));

                        // Leaf cluster at twig tip
                        const cRadius = speciesKey === "amla" || speciesKey === "ber" ? 1.45 : 1.85;
                        const cGeo = new THREE.IcosahedronGeometry(cRadius, 1);
                        const cluster = new THREE.Mesh(cGeo, leafMat);
                        cluster.position.copy(pTip);
                        cluster.scale.set(1.15, 0.78, 1.15);
                        cluster.castShadow = true;
                        cluster.receiveShadow = true;
                        cluster.userData = { baseScale: 1.0, threshold: ((i * 2 + (sub > 0 ? 1 : 0)) / 12) * 0.88 };
                        foliageMeshes.push(cluster);
                        treeRoot.add(cluster);
                    }
                }

                // Top central crown dome clusters
                [[0, trunkTop + crownH + 0.6, 0, 2.2], [0.9, trunkTop + crownH, 0.7, 1.7], [-0.9, trunkTop + crownH, -0.7, 1.7]].forEach(([x, y, z, rad], idx) => {
                    const topCluster = new THREE.Mesh(new THREE.IcosahedronGeometry(rad, 1), leafMat);
                    topCluster.position.set(x, y, z);
                    topCluster.scale.set(1.1, 0.82, 1.1);
                    topCluster.castShadow = true;
                    topCluster.receiveShadow = true;
                    topCluster.userData = { baseScale: 1.0, threshold: 0.75 + idx * 0.08 };
                    foliageMeshes.push(topCluster);
                    treeRoot.add(topCluster);
                });
            }

            treeRoot.add(woodyGroup);

            // Continuous Falling Leaves + Ground Leaf Litter Ring
            const fallMat = new THREE.MeshStandardMaterial({ color: 0xd97706, side: THREE.DoubleSide });
            const fallGeo = new THREE.PlaneGeometry(0.28, 0.18);
            for (let i = 0; i < 28; i++) {
                const fl = new THREE.Mesh(fallGeo, fallMat);
                const angle = Math.random() * Math.PI * 2;
                const dist = 0.5 + Math.random() * 3.2;
                fl.position.set(Math.cos(angle) * dist, 1.0 + Math.random() * 6.0, Math.sin(angle) * dist);
                fl.rotation.set(Math.random() * 3, Math.random() * 3, Math.random() * 3);
                fl.userData = { speed: 0.02 + Math.random() * 0.03, sway: Math.random() * 6.28, radius: dist, angle };
                fallingLeaves.push(fl);
                treeRoot.add(fl);
            }

            for (let i = 0; i < 45; i++) {
                const gl = new THREE.Mesh(fallGeo, fallMat);
                const angle = Math.random() * Math.PI * 2;
                const dist = 0.6 + Math.random() * 4.2;
                gl.position.set(Math.cos(angle) * dist, 0.03, Math.sin(angle) * dist);
                gl.rotation.x = -Math.PI / 2;
                gl.rotation.z = Math.random() * Math.PI;
                groundLitter.push(gl);
                treeRoot.add(gl);
            }

            scene.add(treeRoot);
        }

        // --- 2D SUMMARY DIAGRAMS ---
        function drawAll2DDiagrams(data, hour, day, growth, lat) {
            // 1. Side Profile Solar Ray & Shadow Geometry
            const sCanvas = document.getElementById('sideCanvas');
            const sCtx = sCanvas.getContext('2d');
            sCtx.clearRect(0, 0, sCanvas.width, sCanvas.height);

            const gY = 132, tX = 72, scale = 5.0;
            const hPx = Math.min(92, data.H * scale);
            const rPx = Math.max(6, data.R * scale * 0.55);
            const lPx = Math.min(210, data.shadowLen * scale);

            sCtx.strokeStyle = '#94a3b8'; sCtx.lineWidth = 2;
            sCtx.beginPath(); sCtx.moveTo(12, gY); sCtx.lineTo(302, gY); sCtx.stroke();

            // Ground shadow bar
            sCtx.strokeStyle = '#0f172a'; sCtx.lineWidth = 5;
            sCtx.beginPath(); sCtx.moveTo(tX, gY); sCtx.lineTo(tX + lPx, gY); sCtx.stroke();

            // Trunk & branches
            sCtx.strokeStyle = '#78350f'; sCtx.lineWidth = 4;
            sCtx.beginPath(); sCtx.moveTo(tX, gY); sCtx.lineTo(tX, gY - hPx * 0.75); sCtx.stroke();

            // Canopy with seasonal opacity
            sCtx.fillStyle = `rgba(21, 128, 61, ${Math.max(0.2, data.currentDensity)})`;
            sCtx.beginPath(); sCtx.arc(tX, gY - hPx * 0.72, rPx, 0, Math.PI * 2); sCtx.fill();

            // Sun Ray
            sCtx.strokeStyle = '#f59e0b'; sCtx.setLineDash([4, 3]); sCtx.lineWidth = 2;
            sCtx.beginPath(); sCtx.moveTo(tX - 25, gY - hPx - 18); sCtx.lineTo(tX + lPx, gY); sCtx.stroke();
            sCtx.setLineDash([]);

            sCtx.fillStyle = '#0f172a'; sCtx.font = '600 11px sans-serif';
            sCtx.fillText(`H = ${data.H}m`, 10, gY - hPx * 0.5);
            sCtx.fillText(`L = ${data.shadowLen}m`, tX + lPx * 0.35, gY + 15);
            sCtx.fillText(`θ = ${data.elev}°`, tX + Math.min(165, lPx) - 20, gY - 8);

            // 2. Top-Down Plan View
            const tCanvas = document.getElementById('topCanvas');
            const tCtx = tCanvas.getContext('2d');
            tCtx.clearRect(0, 0, tCanvas.width, tCanvas.height);

            const cx = 157, cy = 78;
            tCtx.strokeStyle = '#e2e8f0'; tCtx.lineWidth = 1;
            [24, 48, 70].forEach(r => { tCtx.beginPath(); tCtx.arc(cx, cy, r, 0, Math.PI * 2); tCtx.stroke(); });

            const sunAngle = ((hour - 6) / 12) * Math.PI;
            const crPx = Math.max(5, data.R * 3.1);
            const shPx = Math.min(68, data.shadowLen * 2.4);

            tCtx.save();
            tCtx.translate(cx, cy);
            tCtx.rotate(-(sunAngle + Math.PI));
            tCtx.fillStyle = `rgba(15, 23, 42, ${0.15 + data.currentDensity * 0.28})`;
            tCtx.beginPath(); tCtx.ellipse(shPx / 2, 0, crPx + shPx / 2, crPx, 0, 0, Math.PI * 2); tCtx.fill();
            tCtx.restore();

            tCtx.fillStyle = `rgba(22, 163, 74, ${Math.max(0.25, data.currentDensity)})`;
            tCtx.beginPath(); tCtx.arc(cx, cy, crPx, 0, Math.PI * 2); tCtx.fill();
            tCtx.fillStyle = '#78350f';
            tCtx.beginPath(); tCtx.arc(cx, cy, 3, 0, Math.PI * 2); tCtx.fill();

            tCtx.fillStyle = '#475569'; tCtx.font = '600 10px sans-serif';
            tCtx.fillText('N', cx - 4, 12); tCtx.fillText('S', cx - 4, 150);
            tCtx.fillText('W', 8, cy + 3); tCtx.fillText('E', 298, cy + 3);
            tCtx.fillText(`Eff. Shade: ${data.effArea} m²`, 10, 148);

            // 3. Combined Diurnal (Green) & Annual Leaf Phenology (Amber) Curves
            const cCanvas = document.getElementById('curveCanvas');
            const cCtx = cCanvas.getContext('2d');
            cCtx.clearRect(0, 0, cCanvas.width, cCanvas.height);

            cCtx.strokeStyle = '#cbd5e1'; cCtx.lineWidth = 1;
            cCtx.beginPath(); cCtx.moveTo(28, 126); cCtx.lineTo(298, 126); cCtx.stroke();

            // Annual Leaf Density Curve (Jan-Dec)
            cCtx.strokeStyle = '#d97706'; cCtx.lineWidth = 2;
            cCtx.beginPath();
            for (let d = 1; d <= 365; d += 8) {
                const m = calculateMetrics(data.speciesKey, growth, 12, d, lat);
                const x = 28 + ((d - 1) / 364) * 268;
                const y = 122 - (m.leafPct / 100) * 85;
                if (d === 1) cCtx.moveTo(x, y); else cCtx.lineTo(x, y);
            }
            cCtx.stroke();

            // Diurnal Effective Shade Area Curve (7 AM - 5 PM)
            cCtx.strokeStyle = '#059669'; cCtx.lineWidth = 2;
            cCtx.beginPath();
            for (let h = 7; h <= 17; h += 0.5) {
                const m = calculateMetrics(data.speciesKey, growth, h, day, lat);
                const x = 28 + ((h - 7) / 10) * 268;
                const y = 122 - Math.min(95, m.effArea * 0.25);
                if (h === 7) cCtx.moveTo(x, y); else cCtx.lineTo(x, y);
            }
            cCtx.stroke();

            // Markers for current Day and Hour
            const dayX = 28 + ((day - 1) / 364) * 268;
            const dayY = 122 - (data.leafPct / 100) * 85;
            cCtx.fillStyle = '#d97706';
            cCtx.beginPath(); cCtx.arc(dayX, dayY, 4, 0, Math.PI * 2); cCtx.fill();

            const hrX = 28 + ((hour - 7) / 10) * 268;
            const hrY = 122 - Math.min(95, data.effArea * 0.25);
            cCtx.fillStyle = '#059669';
            cCtx.beginPath(); cCtx.arc(hrX, hrY, 4, 0, Math.PI * 2); cCtx.fill();

            cCtx.fillStyle = '#059669'; cCtx.font = '600 10px sans-serif';
            cCtx.fillText('― Daily Shade (m²)', 30, 16);
            cCtx.fillStyle = '#d97706';
            cCtx.fillText('― Annual Leaf Foliage (%)', 155, 16);
            cCtx.fillStyle = '#64748b';
            cCtx.fillText('Jan / 7AM', 26, 142);
            cCtx.fillText('Jun / Noon', 135, 142);
            cCtx.fillText('Dec / 5PM', 252, 142);
        }

        let currentSpecies = 'mango';
        let latestData = null;

        function syncSimulation() {
            const species = document.getElementById('species').value;
            if (species !== currentSpecies || !treeRoot) {
                currentSpecies = species;
                buildSpecies3DModel(species);
            }

            const growth = parseFloat(document.getElementById('growth').value);
            const hour = parseFloat(document.getElementById('hour').value);
            const day = parseInt(document.getElementById('day').value);
            const lat = parseFloat(document.getElementById('lat').value);

            document.getElementById('growthLbl').innerText = `${Math.round(growth)}%`;
            const hr = Math.floor(hour);
            const min = Math.round((hour - hr) * 60).toString().padStart(2, '0');
            document.getElementById('hourLbl').innerText = `${hr}:${min}`;
            document.getElementById('dayLbl').innerText = dayToMonthStr(day);
            document.getElementById('latLbl').innerText = `${lat}°N`;

            const data = calculateMetrics(species, growth, hour, day, lat);
            latestData = { growth, hour, day, lat, ...data };

            // Update DOM Cards
            document.getElementById('phaseBadge').innerText = data.phase;
            document.getElementById('phenoBadge').innerText = `${data.phenologyState} (${data.leafPct}% Leaves)`;
            document.getElementById('outH').innerText = `${data.H} m`;
            document.getElementById('outR').innerText = `Crown Radius: ${data.R} m`;
            document.getElementById('outElev').innerText = `${data.elev}°`;
            document.getElementById('outDec').innerText = `Declination δ: ${data.dec}°`;
            document.getElementById('outLeaf').innerText = `${data.leafPct}% Foliage`;
            document.getElementById('outHabit').innerText = data.habit;
            document.getElementById('outEff').innerText = `${data.effArea} m²`;
            document.getElementById('outArea').innerText = `Geometric Footprint: ${data.geomArea} m²`;

            // Update 3D Tree Growth Scaling
            if (treeRoot) {
                treeRoot.scale.set(data.scaleR, data.scaleH, data.scaleR);
            }

            // Update Seasonal Leaf Color & Shedding on 3D Crown
            const sp = SPECIES[species];
            if (leafMat) {
                if (data.shedFactor > 0.45) {
                    leafMat.color.setHex(sp.dry);
                } else if (day > sp.shedDay && Math.abs(day - sp.shedDay) < 55) {
                    leafMat.color.setHex(sp.flush);
                } else {
                    leafMat.color.setHex(sp.leaf);
                }
            }

            const leafRatio = data.leafPct / 100.0;
            foliageMeshes.forEach((mesh) => {
                const s = Math.max(0.08, leafRatio);
                mesh.scale.set(s * 1.1, s * 0.82, s * 1.1);
                mesh.visible = leafRatio > 0.18 || mesh.userData.threshold < leafRatio;
            });

            // Show more ground leaf litter during shedding season
            const activeLitterCount = Math.floor(12 + data.shedFactor * 33);
            groundLitter.forEach((gl, idx) => { gl.visible = idx < activeLitterCount; });

            // Update 3D Sun & Ground Shadow Footprint
            sunLight.position.set(data.sunX, data.sunY, data.sunZ);
            sunOrb.position.copy(sunLight.position);

            const sunAz = ((hour - 6.0) / 12.0) * Math.PI;
            const semiMajor = Math.max(0.5, data.R + data.shadowLen * 0.5);
            const semiMinor = Math.max(0.5, data.R);
            shadeEllipse.scale.set(semiMajor, semiMinor, 1);
            shadeEllipse.rotation.z = -sunAz;
            shadeEllipse.position.set(
                -Math.cos(sunAz) * (data.shadowLen * 0.48),
                0.02,
                -Math.sin(sunAz) * (data.shadowLen * 0.48)
            );

            drawAll2DDiagrams(data, hour, day, growth, lat);

            // Sync asynchronously with Python backend
            fetch('/api/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ species, growth, hour, day, lat })
            }).catch(() => {});
        }

        function setDay(d) {
            document.getElementById('day').value = d;
            syncSimulation();
        }

        // Animation Timers (Growth, Daily Sun, Annual Leaf Cycle)
        let growthTimer = null, sunTimer = null, yearTimer = null;

        document.getElementById('playGrowthBtn').addEventListener('click', (e) => {
            if (growthTimer) { clearInterval(growthTimer); growthTimer = null; e.target.innerText = '▶ Animate Growth'; }
            else {
                e.target.innerText = '⏸ Pause Growth';
                growthTimer = setInterval(() => {
                    const el = document.getElementById('growth');
                    el.value = parseFloat(el.value) >= 100 ? 5 : parseFloat(el.value) + 1;
                    syncSimulation();
                }, 55);
            }
        });

        document.getElementById('resetGrowthBtn').addEventListener('click', () => {
            document.getElementById('growth').value = 10;
            syncSimulation();
        });

        document.getElementById('playSunBtn').addEventListener('click', (e) => {
            if (sunTimer) { clearInterval(sunTimer); sunTimer = null; e.target.innerText = '☀ Animate Daily Sun'; }
            else {
                e.target.innerText = '⏸ Pause Sun';
                sunTimer = setInterval(() => {
                    const el = document.getElementById('hour');
                    el.value = parseFloat(el.value) >= 17.5 ? 6.5 : +(parseFloat(el.value) + 0.12).toFixed(2);
                    syncSimulation();
                }, 60);
            }
        });

        document.getElementById('playYearBtn').addEventListener('click', (e) => {
            if (yearTimer) { clearInterval(yearTimer); yearTimer = null; e.target.innerText = '🍂 Play Full Year (Leaf Cycle)'; }
            else {
                e.target.innerText = '⏸ Pause Year Cycle';
                yearTimer = setInterval(() => {
                    const el = document.getElementById('day');
                    el.value = parseInt(el.value) >= 365 ? 1 : parseInt(el.value) + 2;
                    syncSimulation();
                }, 50);
            }
        });

        document.getElementById('exportCsvBtn').addEventListener('click', () => {
            if (!latestData) return;
            const nl = String.fromCharCode(10);
            const headers = "Species,Scientific Name,Growth %,Phase,Day of Year,Phenology,Foliage %,Hour,Latitude,Height (m),Radius (m),Elevation (deg),Shadow Length (m),Geometric Area (m2),Effective Shaded Area (m2)" + nl;
            const row = `"${latestData.speciesName}","${latestData.sciName}",${latestData.growth},"${latestData.phase}",${latestData.day},"${latestData.phenologyState}",${latestData.leafPct},${latestData.hour},${latestData.lat},${latestData.H},${latestData.R},${latestData.elev},${latestData.shadowLen},${latestData.geomArea},${latestData.effArea}` + nl;
            const blob = new Blob([headers + row], { type: 'text/csv' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `${latestData.speciesKey}_shading_summary.csv`;
            a.click();
        });

        document.getElementById('species').addEventListener('change', syncSimulation);
        ['growth', 'hour', 'day', 'lat'].forEach(id => {
            document.getElementById(id).addEventListener('input', syncSimulation);
        });

        // Initial render + continuous falling leaf animation loop
        buildSpecies3DModel('mango');
        syncSimulation();

        let clock = 0;
        function animate() {
            requestAnimationFrame(animate);
            clock += 0.03;

            // Continuous leaf fall animation ("Leaves coming falling will continue")
            const shedBoost = latestData ? (1.0 + latestData.shedFactor * 2.2) : 1.0;
            fallingLeaves.forEach((fl) => {
                fl.position.y -= fl.userData.speed * shedBoost;
                fl.position.x += Math.sin(clock + fl.userData.sway) * 0.012;
                fl.rotation.x += 0.03;
                fl.rotation.z += 0.02;
                if (fl.position.y < 0.05) {
                    fl.position.y = 2.5 + Math.random() * 4.2;
                }
            });

            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            camera.aspect = holder.clientWidth / holder.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(holder.clientWidth, holder.clientHeight);
        });
    </script>
</body>
</html>"""

def compute_simulation(data):
    species_key = data.get("species", "mango")
    growth_pct = float(data.get("growth", 85))
    hour = float(data.get("hour", 13.5))
    day_of_year = int(data.get("day", 172))
    lat = float(data.get("lat", 21.20))

    sp = SPECIES_DATA.get(species_key, SPECIES_DATA["mango"])
    if growth_pct <= 30:
        phase = "Stage 1: Sapling"
        scale_h = 0.12 + (growth_pct / 30.0) * 0.23
        scale_r = 0.10 + (growth_pct / 30.0) * 0.20
    elif growth_pct <= 75:
        phase = "Stage 2: Juvenile Tree"
        scale_h = 0.35 + ((growth_pct - 30.0) / 45.0) * 0.45
        scale_r = 0.30 + ((growth_pct - 30.0) / 45.0) * 0.45
    else:
        phase = "Stage 3: Mature Tree"
        scale_h = 0.80 + ((growth_pct - 75.0) / 25.0) * 0.20
        scale_r = 0.75 + ((growth_pct - 75.0) / 25.0) * 0.25

    current_height = round(sp["max_height"] * scale_h, 2)
    current_radius = round(sp["max_radius"] * scale_r, 2)

    diff = abs(day_of_year - sp["shed_day"])
    circ_diff = min(diff, 365 - diff)
    shed_factor = math.exp(-((circ_diff / 36.0) ** 2))
    current_density = sp["base_density"] - (sp["base_density"] - sp["min_density"]) * shed_factor
    leaf_pct = int(round((current_density / sp["base_density"]) * 100))

    declination = 23.45 * math.sin(math.radians((360.0 / 365.0) * (284 + day_of_year)))
    hour_angle = 15.0 * (hour - 12.0)

    lat_rad, dec_rad, ha_rad = math.radians(lat), math.radians(declination), math.radians(hour_angle)
    sin_elev = max(-1.0, min(1.0, math.sin(lat_rad) * math.sin(dec_rad) + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad)))
    elevation_deg = max(3.0, math.degrees(math.asin(sin_elev)))

    shadow_length = round(min(current_height / math.tan(math.radians(elevation_deg)), 60.0), 2)
    shaded_area = round(math.pi * (current_radius + shadow_length * 0.5) * current_radius, 2)
    effective_shade = round(shaded_area * current_density, 2)

    return {
        "species_name": sp["name"],
        "scientific_name": sp["scientific"],
        "phase": phase,
        "leaf_pct": leaf_pct,
        "height_m": current_height,
        "canopy_radius_m": current_radius,
        "declination_deg": round(declination, 2),
        "elevation_deg": round(elevation_deg, 2),
        "shadow_length_m": shadow_length,
        "shaded_area_sq_m": shaded_area,
        "effective_shade_sq_m": effective_shade
    }

class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True

class LabHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index.html"):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/calculate":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
            result = compute_simulation(body)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))

if __name__ == "__main__":
    auto_convert_blend_files()
    os.makedirs("templates", exist_ok=True)
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(HTML_PAGE)

    port = 5000
    while port < 5015:
        try:
            server = ReusableHTTPServer(("127.0.0.1", port), LabHandler)
            break
        except OSError:
            port += 1

    url = f"http://127.0.0.1:{port}"
    print(f"Server running! Opening {url} in your browser...")
    webbrowser.open(url)
    server.serve_forever()