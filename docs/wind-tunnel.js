import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const CAR_PATH = '../references/mercedec-f1-2020/mercedec-f1-2020.glb';
const FLOW_PATH = '../outputs/W11_2020_GLBDERIVED_CFD_V2_300KPH/CFD_RESULTS/SOLVER_DERIVED_STREAMLINES.json';
const CFD_MIN = new THREE.Vector3(-2.690099, -0.990111, 0.029905);
const CFD_LENGTH = 5.640224;
const PRINT_LENGTH = 203.2;
const MODEL_SCALE = PRINT_LENGTH / CFD_LENGTH;

function assetUrl(path) {
  if (location.hostname.endsWith('.github.io')) {
    const owner = location.hostname.slice(0, -'.github.io'.length);
    const repo = location.pathname.split('/').filter(Boolean)[0];
    return `https://raw.githubusercontent.com/${owner}/${repo}/main/${path.replace(/^\.\.\//, '')}`;
  }
  return path;
}

const host = document.querySelector('#viewport');
const loading = document.querySelector('#loading');
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x030609);
scene.fog = new THREE.FogExp2(0x030609, 0.0032);

const camera = new THREE.PerspectiveCamera(39, 1, 0.1, 1800);
camera.position.set(150, 88, 168);
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.18;
host.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.065;
controls.target.set(0, 16, 0);
controls.minDistance = 55;
controls.maxDistance = 540;

scene.add(new THREE.HemisphereLight(0xe5f7ff, 0x101a20, 4.4));
scene.add(new THREE.AmbientLight(0xd7ebf2, 1.35));
const key = new THREE.DirectionalLight(0xffffff, 7.5); key.position.set(-80, 140, 130); scene.add(key);
const edge = new THREE.DirectionalLight(0x35c9ff, 5.2); edge.position.set(120, 50, -150); scene.add(edge);
const warm = new THREE.DirectionalLight(0xff7548, 2.2); warm.position.set(-160, 75, 70); scene.add(warm);
const fill = new THREE.PointLight(0xffffff, 1100, 380, 1.2); fill.position.set(15, 82, 95); scene.add(fill);

const tunnelGroup = new THREE.Group();
scene.add(tunnelGroup);
const floorMaterial = new THREE.MeshPhysicalMaterial({ color: 0x071018, metalness: .65, roughness: .32, clearcoat: .55, transparent: true, opacity: .96 });
const floor = new THREE.Mesh(new THREE.PlaneGeometry(520, 190), floorMaterial);
floor.rotation.x = -Math.PI / 2; floor.position.y = -0.5; tunnelGroup.add(floor);
const grid = new THREE.GridHelper(520, 52, 0x1b7795, 0x18303b); grid.position.y = -0.15;
grid.material.opacity = .32; grid.material.transparent = true; tunnelGroup.add(grid);
const cageGeometry = new THREE.EdgesGeometry(new THREE.BoxGeometry(500, 120, 180));
const cage = new THREE.LineSegments(cageGeometry, new THREE.LineBasicMaterial({ color: 0x287891, transparent: true, opacity: .22 }));
cage.position.y = 59.5; tunnelGroup.add(cage);

// A simple inlet fan gives the scene a readable wind-tunnel reference without
// borrowing visual assets from the reference website.
const fan = new THREE.Group(); fan.position.set(-232, 57, 0); fan.rotation.y = Math.PI / 2;
for (const radius of [27, 38, 49]) {
  fan.add(new THREE.Mesh(new THREE.TorusGeometry(radius, .65, 6, 64), new THREE.MeshBasicMaterial({ color: 0x2b7085, transparent: true, opacity: .34 })));
}
for (let i = 0; i < 8; i++) {
  const blade = new THREE.Mesh(new THREE.BoxGeometry(3.3, 43, .45), new THREE.MeshBasicMaterial({ color: 0x2b7085, transparent: true, opacity: .18 }));
  blade.rotation.z = i * Math.PI / 4; fan.add(blade);
}
tunnelGroup.add(fan);

const beltMarkers = [];
const beltGeometry = new THREE.BoxGeometry(10, .12, .65);
const beltMaterial = new THREE.MeshBasicMaterial({ color: 0x4bb9da, transparent: true, opacity: .25 });
for (let row = -3; row <= 3; row++) {
  for (let x = -220; x <= 220; x += 24) {
    const marker = new THREE.Mesh(beltGeometry, beltMaterial);
    marker.position.set(x + (row % 2) * 11, .05, row * 20); tunnelGroup.add(marker); beltMarkers.push(marker);
  }
}

let car;
const flowGroup = new THREE.Group(); scene.add(flowGroup);
const lineRecords = [];
const particles = [];
let particleCloud;
let ambientCloud;
let currentMode = 'all';
let running = true;
let windSpeed = 300;
let densityFraction = .75;
let clock = new THREE.Clock();
let cameraGoal = null;

const regionColor = {
  whole_car: new THREE.Color(0x31bff3),
  underfloor: new THREE.Color(0x43d991),
  front_floor_diffuser: new THREE.Color(0xff5b2e),
};

function isFocusRegion(region) {
  return region === 'underfloor' || region === 'front_floor_diffuser';
}

function flowPoint(point) {
  return new THREE.Vector3(
    (point[0] - CFD_MIN.x) * MODEL_SCALE - PRINT_LENGTH / 2,
    (point[2] - CFD_MIN.z) * MODEL_SCALE,
    point[1] * MODEL_SCALE,
  );
}

function addCar(gltf) {
  car = gltf.scene;
  // The supplied GLB stores a 90-degree presentation rotation on its mesh
  // node. Reset it, then apply the documented source-to-CFD coordinate map:
  // CFD X=-source Y, CFD lateral=source X, CFD Z=-source Z.
  car.traverse(node => { if (node.name === 'f1_2020_mercedes') node.quaternion.identity(); });
  const tx = -CFD_MIN.x * MODEL_SCALE - PRINT_LENGTH / 2;
  const ty = -CFD_MIN.z * MODEL_SCALE + 1.1;
  car.matrix.set(
    0, -MODEL_SCALE, 0, tx,
    0, 0, -MODEL_SCALE, ty,
    MODEL_SCALE, 0, 0, 0,
    0, 0, 0, 1,
  );
  car.matrixAutoUpdate = false;
  car.traverse(node => {
    if (!node.isMesh) return;
    node.castShadow = false;
    node.receiveShadow = true;
    const materials = Array.isArray(node.material) ? node.material : [node.material];
    materials.forEach(material => {
      material.side = THREE.DoubleSide;
      if ('roughness' in material) material.roughness = Math.max(material.roughness ?? .35, .28);
      if ('metalness' in material) material.metalness = Math.min(material.metalness ?? .3, .48);
      material.needsUpdate = true;
    });
  });
  scene.add(car);
}

function addFlow(data) {
  const positions = [];
  const colors = [];
  data.streamlines.forEach((entry, lineIndex) => {
    const points = entry.points_m.map(flowPoint);
    if (points.length < 2) return;
    // The original "front_wing_to_diffuser" seed set travels around the
    // upper/side body in this coarse field, so it is shown as general solved
    // flow rather than being mislabeled as an underfloor connection.
    const displayRegion = entry.region === 'front_wing_to_diffuser' ? 'whole_car' : entry.region;
    const curve = new THREE.CatmullRomCurve3(points, false, 'centripetal', .25);
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    const base = regionColor[displayRegion];
    const lineColor = [];
    points.forEach((_, i) => {
      const ratio = entry.speed_ratio[Math.min(i, entry.speed_ratio.length - 1)] || 1;
      const c = base.clone();
      c.offsetHSL(0, 0, THREE.MathUtils.clamp((ratio - .75) * .20, -.12, .15));
      lineColor.push(c.r, c.g, c.b);
    });
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(lineColor, 3));
    const material = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: displayRegion === 'underfloor' ? .64 : .42, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: displayRegion === 'whole_car' });
    const line = new THREE.Line(geometry, material);
    line.renderOrder = displayRegion === 'whole_car' ? 1 : 3;
    line.userData.region = displayRegion; flowGroup.add(line);
    lineRecords.push({ line, region: displayRegion });

    const count = displayRegion === 'underfloor' ? 9 : 5;
    for (let i = 0; i < count; i++) {
      particles.push({ curve, phase: (i / count + lineIndex * .037) % 1, speed: .035 + (lineIndex % 7) * .0025, region: displayRegion });
      const p = curve.getPoint(i / count); positions.push(p.x, p.y, p.z); colors.push(base.r, base.g, base.b);
    }

    if (displayRegion === 'underfloor') {
      // The solved floor paths begin downstream because upstream integration
      // terminated in the unconverged screening field. Add a clearly labeled
      // tracing guide from the inlet/front-wing region to the first solved
      // sample, then retain every solver-derived floor/diffuser point.
      const first = points[0];
      const lateral = first.z;
      const joinHeight = THREE.MathUtils.clamp(first.y, 2.1, 5.8);
      const guide = [
        new THREE.Vector3(-148, 8.2, lateral * .93),
        new THREE.Vector3(-122, 6.8, lateral * .95),
        new THREE.Vector3(-103, 4.5, lateral * .97),
        new THREE.Vector3(-82, 3.1, lateral * .98),
        new THREE.Vector3(-53, 2.45, lateral),
        new THREE.Vector3(-19, 2.35, lateral),
        new THREE.Vector3(Math.min(first.x - 7, -3), joinHeight, lateral),
      ];
      const compositePoints = [...guide, ...points];
      const compositeCurve = new THREE.CatmullRomCurve3(compositePoints, false, 'centripetal', .22);
      const traceGeometry = new THREE.BufferGeometry().setFromPoints(compositeCurve.getPoints(Math.max(220, compositePoints.length)));
      const traceMaterial = new THREE.LineBasicMaterial({ color: regionColor.front_floor_diffuser, transparent: true, opacity: .96, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false });
      const trace = new THREE.Line(traceGeometry, traceMaterial);
      trace.renderOrder = 4;
      trace.userData.region = 'front_floor_diffuser';
      flowGroup.add(trace);
      lineRecords.push({ line: trace, region: 'front_floor_diffuser' });

      const traceCount = 14;
      for (let i = 0; i < traceCount; i++) {
        particles.push({ curve: compositeCurve, phase: (i / traceCount + lineIndex * .051) % 1, speed: .041 + (lineIndex % 5) * .0028, region: 'front_floor_diffuser' });
        const p = compositeCurve.getPoint(i / traceCount);
        positions.push(p.x, p.y, p.z);
        colors.push(regionColor.front_floor_diffuser.r, regionColor.front_floor_diffuser.g, regionColor.front_floor_diffuser.b);
      }
    }
  });
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  const material = new THREE.PointsMaterial({ size: 1.75, sizeAttenuation: true, vertexColors: true, transparent: true, opacity: .98, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false });
  particleCloud = new THREE.Points(geometry, material); flowGroup.add(particleCloud);
  document.querySelector('#path-readout').textContent = data.streamline_count;
}

function addAmbient() {
  const count = 620;
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    positions[i * 3] = THREE.MathUtils.randFloat(-245, 245);
    positions[i * 3 + 1] = THREE.MathUtils.randFloat(3, 112);
    positions[i * 3 + 2] = THREE.MathUtils.randFloat(-87, 87);
  }
  const geometry = new THREE.BufferGeometry(); geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  ambientCloud = new THREE.Points(geometry, new THREE.PointsMaterial({ color: 0x8bdff7, size: .46, transparent: true, opacity: .34, depthWrite: false, blending: THREE.AdditiveBlending }));
  tunnelGroup.add(ambientCloud);
}

function updateTelemetry() {
  const velocity = windSpeed / 3.6;
  const pressure = .5 * 1.225 * velocity * velocity / 1000;
  document.querySelector('#speed-readout').textContent = windSpeed.toFixed(0);
  document.querySelector('#velocity-readout').textContent = velocity.toFixed(1);
  document.querySelector('#pressure-readout').textContent = pressure.toFixed(2);
  document.querySelector('#speed-output').textContent = `${windSpeed} km/h`;
}

function setMode(mode) {
  currentMode = mode;
  document.querySelectorAll('[data-mode]').forEach(button => button.classList.toggle('active', button.dataset.mode === mode));
  lineRecords.forEach(record => {
    const trailsEnabled = document.querySelector('#trails').checked;
    record.line.visible = trailsEnabled && (mode === 'all' || (mode === 'focus' && isFocusRegion(record.region)));
    record.line.material.opacity = record.region === 'front_floor_diffuser' ? .98 : (record.region === 'underfloor' ? (mode === 'focus' ? .78 : .64) : .42);
  });
  if (particleCloud) particleCloud.visible = mode !== 'inspect';
  if (ambientCloud) ambientCloud.visible = mode === 'all' && document.querySelector('#ambient').checked;
  if (mode === 'focus') setCamera('floor');
  if (mode === 'inspect') setCamera('iso');
}

const cameraViews = {
  iso: { position: new THREE.Vector3(150, 88, 168), target: new THREE.Vector3(0, 17, 0) },
  side: { position: new THREE.Vector3(0, 39, 224), target: new THREE.Vector3(0, 17, 0) },
  top: { position: new THREE.Vector3(0, 255, .1), target: new THREE.Vector3(0, 0, 0) },
  floor: { position: new THREE.Vector3(48, 15, 205), target: new THREE.Vector3(22, 7, 0) },
};
function setCamera(name) {
  const view = cameraViews[name]; if (!view) return;
  cameraGoal = { position: view.position.clone(), target: view.target.clone() };
  document.querySelectorAll('[data-camera]').forEach(button => button.classList.toggle('active', button.dataset.camera === name));
}

function updateParticles(dt) {
  if (!particleCloud) return;
  const positions = particleCloud.geometry.attributes.position;
  const flowMultiplier = windSpeed / 300;
  particleCloud.geometry.setDrawRange(0, particles.length);
  for (let i = 0; i < particles.length; i++) {
    const item = particles[i];
    if (running) item.phase = (item.phase + dt * item.speed * flowMultiplier) % 1;
    const modeVisible = currentMode === 'all' || (currentMode === 'focus' && isFocusRegion(item.region));
    const densityVisible = ((i * 37) % 101) / 100 < densityFraction;
    if (!modeVisible || !densityVisible || currentMode === 'inspect') {
      positions.setXYZ(i, 9999, 9999, 9999);
      continue;
    }
    const point = item.curve.getPoint(item.phase);
    positions.setXYZ(i, point.x, point.y, point.z);
  }
  positions.needsUpdate = true;
}

function updateAmbient(dt) {
  if (!ambientCloud || !running) return;
  const position = ambientCloud.geometry.attributes.position;
  const step = dt * windSpeed * .15;
  for (let i = 0; i < position.count; i++) {
    let x = position.getX(i) + step;
    if (x > 245) x = -245;
    position.setX(i, x);
  }
  position.needsUpdate = true;
  beltMarkers.forEach(marker => {
    marker.position.x += step * .62;
    if (marker.position.x > 245) marker.position.x -= 490;
  });
  fan.rotation.z -= dt * windSpeed * .0035;
}

function resize() {
  const rect = host.getBoundingClientRect();
  camera.aspect = rect.width / Math.max(rect.height, 1); camera.updateProjectionMatrix();
  renderer.setSize(rect.width, rect.height, false);
}
new ResizeObserver(resize).observe(host);

document.querySelector('#speed').addEventListener('input', event => { windSpeed = Number(event.target.value); updateTelemetry(); });
document.querySelector('#density').addEventListener('input', event => { densityFraction = Number(event.target.value) / 100; document.querySelector('#density-output').textContent = `${event.target.value}%`; });
document.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => setMode(button.dataset.mode)));
document.querySelectorAll('[data-camera]').forEach(button => button.addEventListener('click', () => setCamera(button.dataset.camera)));
document.querySelector('#trails').addEventListener('change', event => lineRecords.forEach(record => record.line.visible = event.target.checked && (currentMode === 'all' || (currentMode === 'focus' && isFocusRegion(record.region)))));
document.querySelector('#ambient').addEventListener('change', event => { if (ambientCloud) ambientCloud.visible = event.target.checked && currentMode === 'all'; });
document.querySelector('#tunnel').addEventListener('change', event => { tunnelGroup.visible = event.target.checked; });
document.querySelector('#collapse').addEventListener('click', () => {
  const panel = document.querySelector('.control-panel'); panel.classList.toggle('collapsed');
  document.querySelector('#collapse').textContent = panel.classList.contains('collapsed') ? '+' : '−';
});
document.querySelector('#pause').addEventListener('click', event => {
  running = !running; event.currentTarget.classList.toggle('active', !running);
  event.currentTarget.innerHTML = running ? '<b>Ⅱ</b> PAUSE' : '<b>▶</b> PLAY';
});

addAmbient(); updateTelemetry();
Promise.all([
  new GLTFLoader().loadAsync(assetUrl(CAR_PATH)),
  fetch(assetUrl(FLOW_PATH), { cache: 'no-store' }).then(response => {
    if (!response.ok) throw new Error(`Flow data ${response.status}`); return response.json();
  }),
]).then(([gltf, flow]) => {
  addCar(gltf); addFlow(flow); loading.hidden = true; setMode('all');
}).catch(error => {
  console.error(error); loading.innerHTML = '<span></span>Unable to load the W11 visualization.';
});

renderer.setAnimationLoop(() => {
  const dt = Math.min(clock.getDelta(), .05);
  updateParticles(dt); updateAmbient(dt);
  if (cameraGoal) {
    camera.position.lerp(cameraGoal.position, .075); controls.target.lerp(cameraGoal.target, .075);
    if (camera.position.distanceTo(cameraGoal.position) < .12) cameraGoal = null;
  }
  controls.update(); renderer.render(scene, camera);
});
