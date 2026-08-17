import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

const host = document.querySelector('#viewer');
const loading = document.querySelector('#loading');
const modelSelect = document.querySelector('#model');
const familySelect = document.querySelector('#family');
const search = document.querySelector('#search');
const title = document.querySelector('#title');
const version = document.querySelector('#version');
const pathLabel = document.querySelector('#path');
const download = document.querySelector('#download');
const animationButton = document.querySelector('#animation');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0a0e14);
scene.fog = new THREE.FogExp2(0x0a0e14, 0.00018);
const camera = new THREE.PerspectiveCamera(38, 1, 0.01, 100000);
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
host.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.screenSpacePanning = true;

scene.add(new THREE.HemisphereLight(0xdbeafe, 0x18202b, 2.6));
const key = new THREE.DirectionalLight(0xffffff, 4.0); key.position.set(4, 7, 6); scene.add(key);
const rim = new THREE.DirectionalLight(0x67e8f9, 3.0); rim.position.set(-6, 2, -5); scene.add(rim);
const floor = new THREE.GridHelper(20000, 80, 0x2d4858, 0x17232d); floor.material.opacity = .35; floor.material.transparent = true; scene.add(floor);

let root = null;
let mixer = null;
let animationsPlaying = true;
let models = [];
let visibleModels = [];
const clock = new THREE.Clock();

function assetUrl(item) {
  // GitHub Pages publishes only /docs, so model binaries remain in the main
  // repository and are loaded through raw.githubusercontent.com. Local testing
  // from the repository root continues to use the relative path.
  if (location.hostname.endsWith('.github.io')) {
    const owner = location.hostname.slice(0, -'.github.io'.length);
    const repo = location.pathname.split('/').filter(Boolean)[0];
    if (owner && repo) return `https://raw.githubusercontent.com/${owner}/${repo}/main/${item.path.replace(/^\.\.\//, '')}`;
  }
  return item.path;
}

function resize() {
  const box = host.getBoundingClientRect();
  camera.aspect = box.width / Math.max(box.height, 1);
  camera.updateProjectionMatrix();
  renderer.setSize(box.width, box.height, false);
}
new ResizeObserver(resize).observe(host);

function clearModel() {
  if (!root) return;
  scene.remove(root);
  root.traverse?.(node => {
    node.geometry?.dispose?.();
    if (Array.isArray(node.material)) node.material.forEach(m => m.dispose());
    else node.material?.dispose?.();
  });
  root = null; mixer = null;
}

function frameObject(object) {
  const box = new THREE.Box3().setFromObject(object);
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  const radius = Math.max(size.x, size.y, size.z) * .58 || 1;
  controls.target.copy(center);
  camera.near = Math.max(radius / 10000, .001);
  camera.far = radius * 100;
  camera.position.copy(center).add(new THREE.Vector3(radius * 1.5, radius * .85, radius * 1.75));
  camera.updateProjectionMatrix();
  floor.position.y = box.min.y;
  floor.scale.setScalar(Math.max(radius / 10000, .001));
  controls.update();
}

async function loadModel(item) {
  clearModel();
  loading.hidden = false;
  loading.textContent = 'Loading model…';
  title.textContent = item.label;
  version.textContent = item.family;
  pathLabel.textContent = item.path.replace('../', '');
  const url = assetUrl(item);
  download.href = url;
  try {
    if (item.ext === 'glb') {
      const gltf = await new GLTFLoader().loadAsync(url);
      root = gltf.scene;
      scene.add(root);
      if (gltf.animations.length) {
        mixer = new THREE.AnimationMixer(root);
        gltf.animations.forEach(clip => mixer.clipAction(clip).play());
        animationButton.disabled = false;
      } else animationButton.disabled = true;
    } else {
      const geometry = await new STLLoader().loadAsync(url);
      geometry.computeVertexNormals();
      root = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ color: 0xd8dde4, metalness: .55, roughness: .32 }));
      scene.add(root);
      animationButton.disabled = true;
    }
    frameObject(root);
    loading.hidden = true;
  } catch (error) {
    console.error(error);
    loading.textContent = 'Could not load this model. Download it to inspect locally.';
  }
}

function rebuildList(keepSelection = false) {
  const current = keepSelection ? modelSelect.value : '';
  const q = search.value.trim().toLowerCase();
  const family = familySelect.value;
  visibleModels = models.filter(m => (family === 'all' || m.family === family) && (!q || `${m.label} ${m.path}`.toLowerCase().includes(q)));
  modelSelect.replaceChildren(...visibleModels.map((m, index) => {
    const option = document.createElement('option');
    option.value = m.path; option.textContent = m.label; option.selected = current ? m.path === current : index === 0;
    return option;
  }));
  const selected = visibleModels.find(m => m.path === modelSelect.value) || visibleModels[0];
  if (selected) loadModel(selected);
}

modelSelect.addEventListener('change', () => {
  const item = visibleModels.find(m => m.path === modelSelect.value);
  if (item) loadModel(item);
});
familySelect.addEventListener('change', () => rebuildList());
search.addEventListener('input', () => rebuildList(true));
document.querySelector('#reset').addEventListener('click', () => root && frameObject(root));
animationButton.addEventListener('click', () => {
  animationsPlaying = !animationsPlaying;
  if (mixer) mixer.timeScale = animationsPlaying ? 1 : 0;
  animationButton.textContent = animationsPlaying ? 'Pause animation' : 'Play animation';
});

fetch('models.json').then(r => r.json()).then(data => {
  models = data.models;
  const families = [...new Set(models.map(m => m.family))];
  familySelect.append(...families.map(f => { const o = document.createElement('option'); o.value = f; o.textContent = f; return o; }));
  rebuildList();
}).catch(error => { console.error(error); loading.textContent = 'Model catalog could not be loaded.'; });

renderer.setAnimationLoop(() => {
  const dt = clock.getDelta();
  if (mixer && animationsPlaying) mixer.update(dt);
  controls.update();
  renderer.render(scene, camera);
});
