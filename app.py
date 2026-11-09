import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Botanical Shade Analysis</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        :root { --bg: #f4f6f8; --panel: #ffffff; --text: #1a1a1a; --sub: #5f6368; --border: #dadce0; --accent: #1a73e8; --accent-hover: #1557b0; }
        body { font-family: 'Roboto Mono', monospace; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { font-size: 20px; margin: 0 0 20px 0; border-bottom: 2px solid var(--border); padding-bottom: 10px; }
        .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 15px; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .row { display: flex; flex-wrap: wrap; gap: 15px; align-items: flex-end; }
        .col { flex: 1; min-width: 140px; display: flex; flex-direction: column; }
        label { font-size: 12px; font-weight: 700; color: var(--sub); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
        select { padding: 8px; border: 1px solid var(--border); border-radius: 4px; font-family: inherit; font-size: 14px; outline: none; }
        input[type=range] { -webkit-appearance: none; width: 100%; background: transparent; margin-bottom: 8px; }
        input[type=range]::-webkit-slider-runnable-track { width: 100%; height: 6px; background: #e0e0e0; border-radius: 3px; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 18px; width: 18px; border-radius: 50%; background: var(--accent); cursor: pointer; margin-top: -6px; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }
        button { padding: 9px 16px; border: none; border-radius: 4px; background: var(--accent); color: #fff; font-family: inherit; font-weight: 700; cursor: pointer; transition: 0.2s; font-size: 14px; }
        button:hover { background: var(--accent-hover); } button.active { background: #d32f2f; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }
        .stat-card { background: var(--panel); border-left: 4px solid var(--accent); padding: 12px 15px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .stat-lbl { font-size: 11px; color: var(--sub); text-transform: uppercase; margin-bottom: 4px; font-weight: 700; }
        .stat-val { font-size: 18px; font-weight: 700; }
        .stat-card.hl { border-left-color: #d32f2f; } .stat-card.hl .stat-val { color: #d32f2f; }
        #view { width: 100%; height: 400px; border: 1px solid var(--border); border-radius: 8px; background: #87CEEB; display: block; overflow: hidden; }
        .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px; }
        .chart-box { background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .chart-title { font-size: 12px; font-weight: 700; color: var(--sub); margin-bottom: 10px; text-transform: uppercase; }
        canvas { width: 100%; height: 220px; display: block; background: #fafafa; border: 1px solid #eee; border-radius: 4px; }
    </style>
</head>
<body>
<div class="container">
    <h1>Botanical Shade Analysis</h1>
    
    <div class="panel row">
        <div class="col">
            <label>Tree Species</label>
            <select id="sp" onchange="changeTree()">
                <option value="banana">Banana (Mat: 1 yr)</option>
                <option value="papaya">Papaya (Mat: 2 yrs)</option>
                <option value="amla">Amla (Mat: 8 yrs)</option>
                <option value="ber">Ber (Mat: 10 yrs)</option>
                <option value="mango" selected>Mango (Mat: 12 yrs)</option>
                <option value="kathal">Kathal (Mat: 15 yrs)</option>
                <option value="jamun">Jamun (Mat: 20 yrs)</option>
                <option value="sheesham">Sheesham (Mat: 25 yrs)</option>
                <option value="sagvan">Sagvan (Mat: 30 yrs)</option>
            </select>
        </div>
        <div class="col" style="flex: 2;">
            <label>Age: <span id="lA">6.0</span> / <span id="lMA">12</span> Yrs</label>
            <input type="range" id="age" min="0" step="0.01" value="6" oninput="update()">
        </div>
        <div class="col">
            <label>Time: <span id="lT">10:00</span></label>
            <input type="range" id="time" min="6" max="18" step="0.05" value="10" oninput="update()">
        </div>
        <div class="col">
            <label>Day: <span id="lD">160</span></label>
            <input type="range" id="day" min="1" max="365" value="160" oninput="update()">
        </div>
        <div class="col">
            <label>&nbsp;</label>
            <button id="btn" onclick="togglePlay()">RUN ANIMATION</button>
        </div>
    </div>

    <div class="stats">
        <div class="stat-card"><div class="stat-lbl">Height</div><div class="stat-val" id="oH">0.0 m</div></div>
        <div class="stat-card"><div class="stat-lbl">Crown Radius</div><div class="stat-val" id="oR">0.0 m</div></div>
        <div class="stat-card"><div class="stat-lbl">Sun Elevation</div><div class="stat-val" id="oA">0.0&deg;</div></div>
        <div class="stat-card"><div class="stat-lbl">Shadow Length</div><div class="stat-val" id="oS">0.0 m</div></div>
        <div class="stat-card"><div class="stat-lbl">Leaf Density</div><div class="stat-val" id="oL">100%</div></div>
        <div class="stat-card hl"><div class="stat-lbl">Shaded Area</div><div class="stat-val" id="oArea">0.0 m&sup2;</div></div>
    </div>

    <div style="margin-top: 15px;"><div id="view"></div></div>

    <div class="charts">
        <div class="chart-box">
            <div class="chart-title">Side Elevation (Orthographic)</div>
            <canvas id="c1"></canvas>
        </div>
        <div class="chart-box">
            <div class="chart-title">Plan Footprint (Top-Down)</div>
            <canvas id="c2"></canvas>
        </div>
        <div class="chart-box">
            <div class="chart-title">Diurnal Shaded Area (m&sup2; vs Time)</div>
            <canvas id="c3"></canvas>
        </div>
        <div class="chart-box">
            <div class="chart-title">Seasonal Leaf Density (% vs Month)</div>
            <canvas id="c4"></canvas>
        </div>
    </div>
</div>

<script>
// --- DATA & MATHEMATICAL LOGIC ---
var T = {
    banana:{h:4.5,r:2.8,maxL:.75,minL:.6,shed:110,w:0x6b8e23,l:0x4ca626,age:1},
    papaya:{h:6,r:2.2,maxL:.65,minL:.5,shed:95,w:0x737d62,l:0x3b8132,age:2},
    amla:{h:9,r:4,maxL:.7,minL:.3,shed:80,w:0x6e5d4f,l:0x558b2f,age:8},
    ber:{h:8,r:4.2,maxL:.7,minL:.3,shed:135,w:0x4a3525,l:0x4d7c2b,age:10},
    mango:{h:13,r:6,maxL:.9,minL:.75,shed:75,w:0x5c4033,l:0x2d5a27,age:12},
    kathal:{h:12,r:5.5,maxL:.9,minL:.78,shed:65,w:0x3d2817,l:0x1f5223,age:15},
    jamun:{h:14,r:5,maxL:.85,minL:.7,shed:60,w:0x594d42,l:0x27622d,age:20},
    sheesham:{h:14,r:4.8,maxL:.75,minL:.2,shed:45,w:0x4e3629,l:0x38761d,age:25},
    sagvan:{h:15,r:5.2,maxL:.85,minL:.15,shed:85,w:0x5c4838,l:0x4a7c2c,age:30}
};

function calc(sp, a, t, d) {
    var m = T[sp];
    // 1. Growth Math: Power curves (fast early growth, slows down at maturity)
    var r = Math.min(1, a / m.age);
    var gh = Math.pow(r, 0.6);
    var gr = Math.pow(r, 1.1);
    if (gh < 0.08) gh = 0.08;
    if (gr < 0.08) gr = 0.08;
    
    var h = m.h * gh;
    var rad = m.r * gr;
    
    // 2. Leaf Shedding: Cosine wave centered on the shedding day
    var ds = Math.abs(d - m.shed);
    if (ds > 182.5) ds = 365 - ds;
    var drop = ds < 65 ? Math.cos((ds / 65) * Math.PI / 2) : 0;
    var den = m.maxL - (m.maxL - m.minL) * drop;
    
    // 3. Sun Elevation: Sine wave for time of day (6am to 6pm) + seasonal tilt
    var pk = 68 - 15 * Math.cos(2 * Math.PI * d / 365);
    var el = Math.max(5, 6 + (pk - 6) * Math.sin((t - 6) / 12 * Math.PI));
    
    // 4. Shadow & Area: Trigonometry (Shadow = Height / tan(angle)) & Ellipse Area
    var sh = h / Math.tan(el * Math.PI / 180);
    var ar = Math.PI * rad * (rad + sh / 2) * den;
    
    return {h:h, rad:rad, gh:gh, gr:gr, den:den, drop:drop, el:el, sh:sh, ar:ar};
}

// --- 3D VISUALIZATION ---
var dom = document.getElementById('view'), scn = new THREE.Scene();
scn.background = new THREE.Color(0x87CEEB);
var cam = new THREE.PerspectiveCamera(45, dom.clientWidth/dom.clientHeight, 0.1, 1000);
var ren = new THREE.WebGLRenderer({antialias:true});
ren.setSize(dom.clientWidth, dom.clientHeight); 
ren.shadowMap.enabled = true; 
ren.shadowMap.type = THREE.PCFSoftShadowMap; 
dom.appendChild(ren.domElement);

var cX = 0.6, cY = 0.38, cR = 26, tgt = new THREE.Vector3(0, 3, 0);
function uCam() { cam.position.set(cR*Math.cos(cY)*Math.sin(cX), tgt.y+cR*Math.sin(cY), cR*Math.cos(cY)*Math.cos(cX)); cam.lookAt(tgt); }
uCam();

// Mouse controls
var drag=false, pX=0, pY=0;
ren.domElement.onmousedown=function(e){drag=true;pX=e.clientX;pY=e.clientY;};
window.onmouseup=function(){drag=false;};
window.onmousemove=function(e){if(!drag)return;cX-=(e.clientX-pX)*.01;cY=Math.max(.05,Math.min(1.4,cY+(e.clientY-pY)*.01));pX=e.clientX;pY=e.clientY;uCam();};
ren.domElement.onwheel=function(e){e.preventDefault();cR=Math.max(8,Math.min(80,cR+e.deltaY*.04));uCam();};

// Lights
scn.add(new THREE.AmbientLight(0xffffff, 0.62));
var sunL = new THREE.DirectionalLight(0xffffff, 1.1);
sunL.castShadow = true; 
sunL.shadow.mapSize.width = 2048; sunL.shadow.mapSize.height = 2048;
sunL.shadow.camera.left = -40; sunL.shadow.camera.right = 40; sunL.shadow.camera.top = 40; sunL.shadow.camera.bottom = -40;
scn.add(sunL);
var sunM = new THREE.Mesh(new THREE.SphereGeometry(2,24,24), new THREE.MeshBasicMaterial({color:0xffcc00})); 
scn.add(sunM);

// Ground & Grid (enabled receiveShadow so the 3D tree casts a visible shadow)
var groundMesh = new THREE.Mesh(new THREE.PlaneGeometry(300,300), new THREE.MeshLambertMaterial({color:0xf5f5f5}));
groundMesh.rotation.x = -Math.PI/2;
groundMesh.receiveShadow = true;
scn.add(groundMesh);
scn.add(new THREE.GridHelper(200, 50, 0xaaaaaa, 0xdddddd));

var tGrp = new THREE.Group(); 
scn.add(tGrp); 
var leaves = [], crownParts = [];

function build(sp) {
    while(tGrp.children.length > 0) tGrp.remove(tGrp.children[0]); 
    leaves = []; crownParts = [];
    var m = T[sp], wm = new THREE.MeshLambertMaterial({color:m.w}), lm = new THREE.MeshLambertMaterial({color:m.l});
    
    if (sp === 'banana' || sp === 'papaya') {
        var th = sp==='banana' ? 3 : 4.2, tr = sp==='banana' ? 0.35 : 0.22;
        var trunk = new THREE.Mesh(new THREE.CylinderGeometry(tr*0.8, tr*1.3, th, 8), wm); 
        trunk.position.y = th/2; trunk.castShadow = true; tGrp.add(trunk);
        
        var lg = new THREE.SphereGeometry(0.5, 8, 8); 
        lg.scale(1.1, 0.08, 3.2); 
        lg.translate(0, 0, 1.6);
        
        for (var i=0; i<9; i++) {
            var pv = new THREE.Group(); pv.position.y = th; pv.rotation.y = i*Math.PI*2/9; pv.rotation.x = -0.35 + (i%2)*0.12;
            var lf = new THREE.Mesh(lg, lm); lf.castShadow = true; pv.add(lf); tGrp.add(pv);
            crownParts.push(lf);
        }
    } else {
        var isTall = (sp==='sagvan' || sp==='sheesham' || sp==='jamun');
        var isShrub = (sp==='ber' || sp==='amla');
        var th = isTall ? 6.0 : isShrub ? 2.8 : 4.2;
        var tr = isTall ? 0.45 : isShrub ? 0.3 : 0.55;
        
        var trunk = new THREE.Mesh(new THREE.CylinderGeometry(tr*0.7, tr, th, 10), wm); 
        trunk.position.y = th/2; trunk.castShadow = true; tGrp.add(trunk);
        
        var lg = new THREE.IcosahedronGeometry(isShrub ? 1.5 : 1.9, 1);
        var n = isTall ? 6 : isShrub ? 7 : 6;
        var spd = isTall ? 2.4 : isShrub ? 2.3 : 2.6; 
        
        for (var i=0; i<n; i++) {
            var ang = i*Math.PI*2/n;
            // Wooden branch connecting trunk to canopy cluster
            var br = new THREE.Mesh(new THREE.CylinderGeometry(tr*0.25, tr*0.45, spd*1.1, 6), wm);
            br.position.set(Math.cos(ang)*spd*0.45, th + 0.4, Math.sin(ang)*spd*0.45);
            br.rotation.z = -Math.cos(ang)*0.7;
            br.rotation.x = Math.sin(ang)*0.7;
            br.castShadow = true; tGrp.add(br);

            var c = new THREE.Mesh(lg, lm); 
            var yOffset = th + (isTall ? 1.5 : isShrub ? 0.8 : 1.2) + (i%2)*0.4;
            c.position.set(Math.cos(ang)*spd, yOffset, Math.sin(ang)*spd); 
            c.castShadow = true; tGrp.add(c);
            crownParts.push(c);
        }
        var top = new THREE.Mesh(lg, lm); 
        top.position.y = th + (isTall ? 2.8 : isShrub ? 1.6 : 2.4); 
        top.scale.set(1.2, 0.9, 1.2);
        top.castShadow = true; tGrp.add(top);
        crownParts.push(top);
    }
    
    // Falling Leaves
    var pG = new THREE.PlaneGeometry(0.45, 0.45);
    for (var i=0; i<28; i++) {
        var p = new THREE.Mesh(pG, new THREE.MeshLambertMaterial({color:0xc87a28, side:THREE.DoubleSide, transparent:true, opacity:0.85}));
        p.position.set((Math.random()-0.5)*6, 1+Math.random()*6, (Math.random()-0.5)*6);
        p.userData = {v: 0.02+Math.random()*0.02, rx: Math.random()*0.08, ry: Math.random()*0.08}; 
        tGrp.add(p); leaves.push(p);
    }
}

// --- 2D DIAGRAMS ---
function draw(id, fn) {
    var c = document.getElementById(id), x = c.getContext('2d'), dpr = window.devicePixelRatio || 1;
    c.width = c.clientWidth * dpr; c.height = c.clientHeight * dpr; 
    x.scale(dpr, dpr); x.clearRect(0, 0, c.clientWidth, c.clientHeight); 
    fn(x, c.clientWidth, c.clientHeight);
}

function chart(id, sp, curT, curD, color, isArea) {
    draw(id, function(x, w, h) {
        var pl = 56, pr = 24, pt = 24, pb = 30;
        var pw = w - pl - pr, ph = h - pt - pb, pts = [];
        var max = isArea ? 0 : 100;
        var curAge = parseFloat(document.getElementById('age').value);
        
        for (var i=0; i<=100; i++) {
            var val;
            if (isArea) {
                val = calc(sp, curAge, 7 + (i/100)*10, curD).ar;
                if (val > max) max = val;
            } else {
                val = calc(sp, curAge, 12, 1 + (i/100)*364).den * 100;
            }
            pts.push(val);
        }
        if (max < 1) max = 1;
        
        x.strokeStyle='#eee';
        for(var i=0;i<=4;i++){
            x.beginPath();x.moveTo(pl,pt+(i/4)*ph);x.lineTo(w-pr,pt+(i/4)*ph);x.stroke();
        }
        x.strokeStyle='#000';
        x.beginPath();x.moveTo(pl,pt);x.lineTo(pl,h-pb);x.lineTo(w-pr,h-pb);x.stroke();
        
        x.strokeStyle=color; x.lineWidth=2; x.beginPath();
        for(var i=0;i<=100;i++){
            var px=pl+(i/100)*pw, py=(h-pb)-(pts[i]/max)*ph;
            if(i===0)x.moveTo(px,py);else x.lineTo(px,py);
        }
        x.stroke();

        // Draw live marker dot for current Time or Day
        var prog = isArea ? Math.max(0, Math.min(1, (curT - 7) / 10)) : (curD - 1) / 364;
        var curVal = isArea ? calc(sp, curAge, curT, curD).ar : calc(sp, curAge, 12, curD).den * 100;
        var dotX = pl + prog * pw, dotY = (h - pb) - (curVal / max) * ph;
        x.fillStyle = color;
        x.beginPath(); x.arc(dotX, dotY, 4, 0, Math.PI*2); x.fill();

        x.fillStyle='#000'; x.font='11px monospace'; x.textAlign='right';
        x.fillText(isArea ? max.toFixed(1)+' m²' : '100%', pl-6, pt+8);
        x.fillText(isArea ? '0 m²' : '0%', pl-6, h-pb);
        x.textAlign='center';
        x.fillText(isArea?'7AM':'Jan', pl, h-10);
        x.fillText(isArea?'12PM':'Jun', pl+pw/2, h-10);
        x.fillText(isArea?'5PM':'Dec', w-pr, h-10);
    });
}

function update() {
    var sp = document.getElementById('sp').value, a = parseFloat(document.getElementById('age').value), t = parseFloat(document.getElementById('time').value), d = parseInt(document.getElementById('day').value);
    var hr = Math.floor(t), mn = Math.round((t-hr)*60); if(mn===60){hr++;mn=0;}
    
    document.getElementById('lA').innerText = a.toFixed(1); 
    document.getElementById('lT').innerText = hr + ':' + (mn<10?'0'+mn:mn); 
    document.getElementById('lD').innerText = d;
    
    var s = calc(sp, a, t, d);
    
    document.getElementById('oH').innerText = s.h.toFixed(1) + ' m'; 
    document.getElementById('oR').innerText = s.rad.toFixed(1) + ' m'; 
    document.getElementById('oA').innerText = s.el.toFixed(1) + '°';
    document.getElementById('oS').innerText = s.sh.toFixed(1) + ' m'; 
    document.getElementById('oL').innerText = Math.round(s.den*100) + '%'; 
    document.getElementById('oArea').innerText = s.ar.toFixed(1) + ' m²';
    
    tGrp.scale.set(s.gr, s.gh, s.gr);
    var leafScale = 0.35 + 0.65 * (s.den / T[sp].maxL);
    for (var i=0; i<crownParts.length; i++) crownParts[i].scale.setScalar(leafScale);
    for (var i=0; i<leaves.length; i++) leaves[i].visible = (s.den > 0.15);
    tgt.y = Math.max(2, s.h * 0.45); 
    uCam();
    
    // Update 3D Sun Position
    var az = ((t-6)/12) * Math.PI; 
    var el = s.el * (Math.PI/180);
    sunL.position.set(Math.cos(az)*Math.cos(el)*60, Math.sin(el)*60, Math.sin(az)*Math.cos(el)*60); 
    sunM.position.copy(sunL.position);
    
    // 1. SIDE ELEVATION CHART
    draw('c1', function(x, w, h) {
        var p = 32, gy = h - 28;
        var maxScale = Math.max(T[sp].h + T[sp].r, s.h + s.sh * 0.6);
        var sc = (h - p - 32) / maxScale;
        var treeTopY = gy - s.h * sc;
        var crownR = s.rad * sc;
        var crownCY = treeTopY + crownR * 0.65;
        var shW = Math.min(s.sh * sc, w/2 - p);

        x.strokeStyle='#000'; x.beginPath(); x.moveTo(p,gy); x.lineTo(w-p,gy); x.stroke();
        x.fillStyle='rgba(0,0,0,0.25)'; x.beginPath(); x.ellipse(w/2 - shW/2, gy, shW/2, 4, 0, 0, Math.PI*2); x.fill();
        x.fillStyle='#5c4033'; x.fillRect(w/2 - 3, crownCY, 6, gy - crownCY);
        x.fillStyle='rgba(76,175,80,'+s.den+')'; x.beginPath(); x.arc(w/2, crownCY, crownR, 0, Math.PI*2); x.fill();

        // Dashed sun ray line grazing canopy top down to shadow tip
        x.strokeStyle='#f59e0b'; x.setLineDash([4, 3]); x.lineWidth=1.5;
        x.beginPath(); x.moveTo(w/2 + 25, treeTopY - 14); x.lineTo(w/2 - shW, gy); x.stroke();
        x.setLineDash([]);
        
        x.fillStyle='#000'; x.font='11px monospace'; x.textAlign='center';
        x.fillText('H: '+s.h.toFixed(1)+'m', w/2, Math.max(14, treeTopY - 6));
        x.fillText('L: '+s.sh.toFixed(1)+'m', w/2 - shW/2, gy + 15);
    });

    // 2. TOP-DOWN PLAN FOOTPRINT
    draw('c2', function(x, w, h) {
        var cx = w/2, cy = h/2;
        var maxVisual = Math.max(T[sp].r * 2.2, s.rad + s.sh);
        var sc = (Math.min(w, h)/2 - 22) / maxVisual;

        x.strokeStyle='#eee'; x.beginPath(); x.moveTo(cx, 12); x.lineTo(cx, h-12); x.stroke();
        x.beginPath(); x.moveTo(12, cy); x.lineTo(w-12, cy); x.stroke();

        x.save(); 
        x.translate(cx, cy); 
        var sunAngle = ((t - 6) / 12) * Math.PI; 
        x.rotate(sunAngle); 
        
        x.fillStyle='rgba(0,0,0,0.22)';
        x.beginPath(); 
        x.ellipse(-s.sh*sc/2, 0, (s.rad + s.sh/2)*sc, s.rad*sc, 0, 0, Math.PI*2); 
        x.fill();
        x.restore();

        x.fillStyle='rgba(76,175,80,'+s.den+')';
        x.beginPath(); x.arc(cx, cy, s.rad*sc, 0, Math.PI*2); x.fill();

        x.fillStyle='#000'; x.font='12px monospace'; x.textAlign='center';
        x.fillText('N', cx, 14); x.fillText('S', cx, h-4);
        x.textAlign='left'; x.fillText('W', 6, cy+4);
        x.textAlign='right'; x.fillText('E', w-6, cy+4);
    });

    // 3 & 4. AREA & DENSITY CHARTS
    chart('c3', sp, t, d, '#1a73e8', true); 
    chart('c4', sp, t, d, '#ff7f0e', false);
}

// --- ANIMATION CONTROLS ---
var play = false, tm;
function togglePlay() {
    play = !play; 
    document.getElementById('btn').innerText = play ? 'STOP ANIMATION' : 'RUN ANIMATION'; 
    document.getElementById('btn').className = play ? 'active' : '';
    
    if (play) {
        var a = document.getElementById('age'), m = parseFloat(a.max);
        if (parseFloat(a.value) >= m - 0.05) a.value = 0.05;
        
        tm = setInterval(function() {
            if (parseFloat(a.value) < m) a.value = Math.min(m, parseFloat(a.value) + m/240);
            var t = document.getElementById('time'), d = document.getElementById('day');
            var nt = parseFloat(t.value) + 0.15;
            if (nt >= 18) {
                t.value = 6; 
                d.value = (parseInt(d.value) % 365) + 1;
            } else {
                t.value = nt;
            }
            update();
        }, 35);
    } else {
        clearInterval(tm);
    }
}

function changeTree() {
    if (play) togglePlay(); 
    var sp = document.getElementById('sp').value, m = T[sp].age, a = document.getElementById('age');
    a.max = m; a.value = (m * 0.6).toFixed(2); 
    document.getElementById('lMA').innerText = m; 
    build(sp); 
    update();
}

// --- 3D ANIMATION LOOP ---
var clk = new THREE.Clock();
function loop() {
    requestAnimationFrame(loop); 
    var time = clk.getElapsedTime();
    
    for (var i=0; i<leaves.length; i++) {
        var l = leaves[i]; 
        if (!l.visible) continue;
        
        l.position.y -= l.userData.v; 
        l.position.x += Math.sin(time * 2 + l.position.y) * 0.01; 
        l.rotation.x += l.userData.rx; 
        l.rotation.y += l.userData.ry;
        
        if (l.position.y < 0.1) { 
            l.position.y = 2.5 + Math.random() * 5; 
            l.position.x = (Math.random() - 0.5) * 5; 
        }
    }
    ren.render(scn, cam);
}

changeTree(); 
loop();

window.onresize = function() { 
    cam.aspect = dom.clientWidth/dom.clientHeight; 
    cam.updateProjectionMatrix(); 
    ren.setSize(dom.clientWidth, dom.clientHeight); 
    update(); 
};
</script>
</body>
</html>"""

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode("utf-8"))

if __name__ == "__main__":
    print("Running on http://localhost:8080")
    webbrowser.open("http://localhost:8080")
    HTTPServer(("localhost", 8080), Handler).serve_forever()
