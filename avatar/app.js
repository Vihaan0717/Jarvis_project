// ============================================================
// JARVIS Avatar Engine v3.0 - Full Human-Like Architecture
// ============================================================

// --- CORE THREE.JS GLOBALS ---
let scene, camera, renderer, vrm_model, clock;
let orbitControls = null;

// --- WEBSOCKET ---
let socket;
let socketConnected = false;

// --- AVATAR STATE ---
let isTalking = false;
let currentEmotion = "neutral";
let talkGestureVariant = 0;

// --- EMOTION MIRROR SYSTEM (smooth fade, avoids "stuck" expressions) ---
let mirroredEmotion = "neutral";
let mirroredValue = 0.0;      // current blended intensity
let mirroredTarget = 0.0;     // target we lerp toward
let mirroredTimer = 0;        // how long since last smile trigger

// --- GESTURE ENGINE STATE MACHINE ---
// States: idle, talking, thinking, pointing, open_hands, crossed_arms, sitting, walk, head_down
let gestureState = "idle";
let pendingGestureState = "idle"; // Queued by backend
let gestureTransitionProgress = 0.0;

// --- CAMERA SYSTEM ---
const CAM_IDLE = { x: 0.0, y: -0.1, z: 1.8, tx: 0.0, ty: 0.65, tz: 0.0 };
const CAM_TALK = { x: 0.0, y: 0.4, z: 1.2, tx: 0.0, ty: 0.90, tz: 0.0 };
const CAM_FULL = { x: 0.0, y: -0.5, z: 2.8, tx: 0.0, ty: 0.45, tz: 0.0 };
let camTarget = { ...CAM_IDLE };
let camCurrent = { x: 0.0, y: -0.1, z: 1.8, tx: 0.0, ty: 0.65, tz: 0.0 };

// --- MOUSE / GAZE TRACKING ---
let mouseX = 0.0, mouseY = 0.0;

// --- AUDIO CONTEXT (Lip-Sync + FFT) ---
let audioContext = new (window.AudioContext || window.webkitAudioContext)();
let analyser = audioContext.createAnalyser();
analyser.fftSize = 512;
let fftData = new Uint8Array(analyser.frequencyBinCount);
let source;

// --- AMBIENT AUDIO AMPLITUDE (for hand gestures) ---
let audioAmplitude = 0.0;

// --- BLINKING SYSTEM ---
let nextBlinkTime = Date.now() + (Math.random() * 3000 + 1500);
let blinkActive = false;
let blinkTimer = 0;

// --- AUDIO STANDBY OVERLAY ---
const standbyOverlay = document.getElementById('audio-standby');
window.addEventListener('click', () => {
    if (audioContext.state === 'suspended') {
        audioContext.resume().then(() => {
            if (standbyOverlay) standbyOverlay.style.display = 'none';
        });
    } else {
        if (standbyOverlay) standbyOverlay.style.display = 'none';
    }
}, { once: true });

function checkAudioAutoPlay() {
    if (audioContext.state === 'suspended') {
        if (standbyOverlay) standbyOverlay.style.display = 'flex';
    }
}
setTimeout(checkAudioAutoPlay, 1000);

// ============================================================
// VRM ACCESSOR HELPERS
// ============================================================
const VRMGlobalRef = (typeof THREE_VRM !== "undefined") ? THREE_VRM : null;
const VRMUtilsRef = VRMGlobalRef && VRMGlobalRef.VRMUtils ? VRMGlobalRef.VRMUtils : null;
const HumanoidBoneRef = (VRMGlobalRef && VRMGlobalRef.VRMSchema && VRMGlobalRef.VRMSchema.HumanoidBoneName) || {};

function getBone(name) {
    if (!vrm_model || !vrm_model.humanoid || !HumanoidBoneRef[name]) return null;
    return vrm_model.humanoid.getBoneNode(HumanoidBoneRef[name]);
}

function setVrmExpression(legacyPresetName, value) {
    if (!vrm_model) return;
    if (vrm_model.expressionManager) {
        const map = { BlinkL: "blinkLeft", BlinkR: "blinkRight", A: "aa", I: "ih", U: "ou", E: "ee", O: "oh", Joy: "joy", Angry: "angry", Sorrow: "sorrow", Fun: "fun" };
        vrm_model.expressionManager.setValue(map[legacyPresetName] || legacyPresetName, value);
        return;
    }
    const presetMap = (VRMGlobalRef && VRMGlobalRef.VRMSchema && VRMGlobalRef.VRMSchema.BlendShapePresetName) || null;
    if (vrm_model.blendShapeProxy && presetMap) {
        const preset = presetMap[legacyPresetName];
        if (preset !== undefined) vrm_model.blendShapeProxy.setValue(preset, value);
    }
}

function clearEmotions() {
    ["Joy", "Angry", "Sorrow", "Fun"].forEach(e => setVrmExpression(e, 0.0));
}

function lerp(a, b, t) { return a + (b - a) * t; }
function lerpBone(bone, axis, target, speed) {
    if (bone) bone.rotation[axis] = lerp(bone.rotation[axis], target, speed);
}

// ============================================================
// INITIALIZATION
// ============================================================
init();
connectWebSocket();
animate();

function init() {
    scene = new THREE.Scene();
    // Pillar 1: FOV 45 = natural human eye field of view, shows full body comfortably
    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 20.0);
    camera.position.set(CAM_IDLE.x, CAM_IDLE.y, CAM_IDLE.z);
    camera.lookAt(CAM_IDLE.tx, CAM_IDLE.ty, CAM_IDLE.tz);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.shadowMap.enabled = true;
    renderer.setClearColor(0x050505, 1);
    document.body.appendChild(renderer.domElement);

    // Rich Lighting
    const dirLight = new THREE.DirectionalLight(0xfff5e0, 1.0);
    dirLight.position.set(1.5, 2.0, 1.5);
    dirLight.castShadow = true;
    scene.add(dirLight);
    const fillLight = new THREE.DirectionalLight(0xb0c8ff, 0.4);
    fillLight.position.set(-1.5, 1.0, -1.0);
    scene.add(fillLight);
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.35);
    scene.add(ambientLight);

    // VRM Model Load
    const loader = new THREE.GLTFLoader();
    loader.load('../JARVIS_PROJECT1.vrm', (gltf) => {
        if (!VRMGlobalRef || !VRMGlobalRef.VRM) return;
        VRMGlobalRef.VRM.from(gltf).then((vrm) => {
            if (VRMUtilsRef && typeof VRMUtilsRef.removeUnnecessaryJoints === "function") {
                VRMUtilsRef.removeUnnecessaryJoints(vrm.scene);
            }
            scene.add(vrm.scene);
            vrm_model = vrm;
            vrm.scene.rotation.y = Math.PI;
            // Scale up the model to fill the screen (VRM files often load at a small scale)
            vrm.scene.scale.set(1.35, 1.35, 1.35);
            // Init T-pose correction
            const lArm = getBone("LeftUpperArm");
            const rArm = getBone("RightUpperArm");
            if (lArm) lArm.rotation.z = 1.2;
            if (rArm) rArm.rotation.z = -1.2;
            // DEBUG: log the model's actual Y range so camera can be tuned
            setTimeout(() => {
                const box = new THREE.Box3().setFromObject(vrm.scene);
                const cy = ((box.min.y + box.max.y) / 2).toFixed(3);
                console.log(`[JARVIS CAM DEBUG] Y min=${box.min.y.toFixed(3)} max=${box.max.y.toFixed(3)} center=${cy}`);
                console.log(`[JARVIS CAM DEBUG] Ideal camTarget ty = ${cy}, camera y = ${(parseFloat(cy) - 0.5).toFixed(3)}`);
            }, 500);
        });
    });

    // OrbitControls — if available
    if (typeof THREE.OrbitControls !== 'undefined') {
        orbitControls = new THREE.OrbitControls(camera, renderer.domElement);
        orbitControls.enableDamping = true;
        orbitControls.dampingFactor = 0.05;
        orbitControls.minDistance = 0.8;
        orbitControls.maxDistance = 5.0;
        orbitControls.target.set(0, 0.5, 0); // Aim orbit at avatar torso
    }

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
    window.addEventListener('mousemove', (e) => {
        mouseX = (e.clientX / window.innerWidth) * 2 - 1;
        mouseY = (e.clientY / window.innerHeight) * 2 - 1;
    });
    window.addEventListener('wheel', (e) => {
        // Scroll to zoom
        camTarget.z = Math.max(1.5, Math.min(5.0, camTarget.z + e.deltaY * 0.002));
        camCurrent.z = camTarget.z; // Instant for scroll
    });

    clock = new THREE.Clock();
}

// ============================================================
// WEBSOCKET CONNECTION
// ============================================================
function connectWebSocket() {
    socket = new WebSocket("ws://127.0.0.1:8765");
    socket.onopen = () => {
        socketConnected = true;
        const el = document.getElementById("status-text");
        if (el) el.innerText = "TRACKING: CONNECTED";
    };
    socket.onmessage = (event) => {
        try { handleBackendCommand(JSON.parse(event.data)); } catch (e) { }
    };
    socket.onclose = () => {
        socketConnected = false;
        const dot = document.getElementById("status-dot");
        const text = document.getElementById("status-text");
        if (dot) dot.className = "";
        if (text) text.innerText = "TRACKING: OFFLINE";
        setTimeout(connectWebSocket, 3000);
    };
}

// ============================================================
// BACKEND COMMAND HANDLER
// ============================================================
function handleBackendCommand(data) {
    if (!vrm_model) return;

    // --- HEAD TRACKING (from Vision Tracker) ---
    if (data.type === "TRACKING") {
        const dot = document.getElementById("status-dot");
        const text = document.getElementById("status-text");
        if (dot && text) {
            dot.className = data.detected ? "active" : "";
            text.innerText = data.detected ? "TRACKING: ACTIVE" : "TRACKING: SEARCHING...";
        }
        // Head rotations driven by actual face pose
        const head = getBone("Head");
        const neck = getBone("Neck");
        if (head) {
            head.rotation.y = lerp(head.rotation.y, (data.yaw || 0) * -1, 0.1);
            head.rotation.x = lerp(head.rotation.x, (data.pitch || 0) * -1, 0.1);
            head.rotation.z = lerp(head.rotation.z, (data.roll || 0), 0.08);
        }
        const lEye = getBone("LeftEye"), rEye = getBone("RightEye");
        if (lEye && rEye) {
            lEye.rotation.y = lerp(lEye.rotation.y, (data.eye_yaw || 0) * 0.4, 0.1);
            lEye.rotation.x = lerp(lEye.rotation.x, (data.eye_pitch || 0) * 0.3, 0.1);
            rEye.rotation.y = lerp(rEye.rotation.y, (data.eye_yaw || 0) * 0.4, 0.1);
            rEye.rotation.x = lerp(rEye.rotation.x, (data.eye_pitch || 0) * 0.3, 0.1);
        }
        // Blink from real face — suppress when mirroring Joy to avoid deep-eye-close
        if (mirroredEmotion !== "happy" || mirroredValue < 0.1) {
            setVrmExpression("BlinkL", data.blink_left > 0.6 ? 0.7 : 0.0);
            setVrmExpression("BlinkR", data.blink_right > 0.6 ? 0.7 : 0.0);
        }
    }

    // --- USER EMOTION MIRROR (smooth, fades out) ---
    if (data.type === "USER_EMOTION") {
        if (data.emotion !== "neutral") {
            mirroredEmotion = data.emotion;
            // Cap intensity at 0.45 max so expression is subtle, not extreme
            mirroredTarget = Math.min(data.intensity || 0.4, 0.45);
            mirroredTimer = Date.now(); // Reset the fade countdown
        }
        // Neutral events are not sent by tracker, fade is handled in animate loop
    }

    // --- AI RESPONSE (Subtitle + Emotion) ---
    if (data.type === "AI_RESPONSE") {
        const subtitleEl = document.getElementById("subtitle");
        if (subtitleEl) {
            subtitleEl.innerText = data.text;
            clearEmotions();
            if (data.emotion && data.emotion !== "neutral") {
                setVrmExpression(data.emotion, 1.0);
            } else {
                const t = data.text.toLowerCase();
                if (t.includes("happy") || t.includes("glad") || t.includes("welcome") || t.includes("!")) setVrmExpression("Joy", 0.8);
                else if (t.includes("sorry") || t.includes("sad") || t.includes("unfortunately")) setVrmExpression("Sorrow", 0.8);
                else if (t.includes("error") || t.includes("danger") || t.includes("locked")) setVrmExpression("Angry", 0.5);
            }
            clearTimeout(window.subtitleTimeout);
            window.subtitleTimeout = setTimeout(() => {
                subtitleEl.style.opacity = "0";
                clearEmotions();
            }, 7000);
        }
    }

    // --- AUDIO PLAYBACK ---
    if (data.type === "PLAY_AUDIO") {
        // Pillar 5: Pick a random talk gesture variant
        talkGestureVariant = Math.floor(Math.random() * 4);
        playAudioWithSync(data.url);
    }

    // --- ANIMATION COMMANDS ---
    if (data.type === "ANIMATION") {
        const action = data.action.toLowerCase();
        if (action === "talking") {
            // handled by audio start
        } else if (action === "stop_talking") {
            // handled by audio end
        } else if (action === "wave") {
            setGestureState("wave");
        } else if (action === "whisper") {
            setGestureState("whisper");
        } else if (["sitting", "walk", "thinking", "idle"].includes(action)) {
            setGestureState(action);
        } else if (action === "head_down") {
            setGestureState("head_down");
        }
    }

    // --- CAMERA STATE COMMANDS (from Python backend) ---
    if (data.type === "CAMERA_STATE") {
        if (data.state === "talk") camTarget = { ...CAM_TALK };
        else if (data.state === "full") camTarget = { ...CAM_FULL };
        else camTarget = { ...CAM_IDLE };
    }
}

// --- GESTURE STATE SETTER ---
function setGestureState(newState) {
    pendingGestureState = newState;
    gestureTransitionProgress = 0.0;
}

// ============================================================
// AUDIO PLAYBACK WITH LIP-SYNC
// ============================================================
async function playAudioWithSync(url) {
    if (!audioContext) return;
    try {
        const response = await fetch(url);
        const arrayBuffer = await response.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        if (source) { try { source.stop(); } catch (e) { } }
        source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(analyser);
        analyser.connect(audioContext.destination);

        source.onended = () => {
            isTalking = false;
            audioAmplitude = 0;
            ["A", "I", "U", "E", "O"].forEach(v => setVrmExpression(v, 0.0));
            // Return to idle camera
            camTarget = { ...CAM_IDLE };
            setGestureState("idle");
        };

        const subtitleEl = document.getElementById("subtitle");
        if (subtitleEl) subtitleEl.style.opacity = "1";

        // Pillar 3: Zoom camera in when JARVIS starts speaking
        camTarget = { ...CAM_TALK };

        isTalking = true;
        setGestureState("talking");
        source.start(0);
    } catch (e) {
        console.error("Audio playback error:", e);
    }
}

// ============================================================
// MAIN ANIMATION LOOP
// ============================================================
function animate() {
    requestAnimationFrame(animate);
    const deltaTime = clock.getDelta();
    const time = Date.now();

    if (vrm_model) {
        vrm_model.update(deltaTime);

        // --- PILLAR 1: SMOOTH CAMERA LERP ---
        camCurrent.x = lerp(camCurrent.x, camTarget.x, 0.03);
        camCurrent.y = lerp(camCurrent.y, camTarget.y, 0.03);
        camCurrent.z = lerp(camCurrent.z, camTarget.z, 0.03);
        camCurrent.tx = lerp(camCurrent.tx, camTarget.tx, 0.03);
        camCurrent.ty = lerp(camCurrent.ty, camTarget.ty, 0.03);
        if (!orbitControls) {
            camera.position.set(camCurrent.x, camCurrent.y, camCurrent.z);
            camera.lookAt(camCurrent.tx, camCurrent.ty, camCurrent.tz);
        }
        if (orbitControls) orbitControls.update();

        // --- GESTURE STATE TRANSITION ---
        if (pendingGestureState !== gestureState) {
            gestureTransitionProgress += 0.05;
            if (gestureTransitionProgress >= 1.0) {
                gestureState = pendingGestureState;
                gestureTransitionProgress = 0.0;
            }
        }

        // --- EMOTION MIRROR FADE-OUT (Pillar 4 fix: prevents stuck expressions) ---
        // If no new smile signal for 2 seconds, fade the emotion back to 0
        const timeSinceMirror = Date.now() - mirroredTimer;
        if (timeSinceMirror > 2000) {
            mirroredTarget = 0.0; // Start fading out
        }
        // Smooth lerp toward target (0.015 = slow natural fade)
        mirroredValue = lerp(mirroredValue, mirroredTarget, 0.015);
        if (mirroredValue > 0.01 && !isTalking) {
            // Only apply when JARVIS is not expressing her own emotion
            if (mirroredEmotion === "happy") setVrmExpression("Joy", mirroredValue);
            else if (mirroredEmotion === "worried") setVrmExpression("Sorrow", mirroredValue);
            else if (mirroredEmotion === "angry") setVrmExpression("Angry", mirroredValue);
        } else if (mirroredValue <= 0.01 && mirroredTarget === 0.0) {
            // Fully faded — clear the expression
            if (mirroredEmotion !== "neutral") {
                clearEmotions();
                mirroredEmotion = "neutral";
                mirroredValue = 0.0;
            }
        }

        // --- PILLAR 5: AUDIO FFT AMPLITUDE ---
        if (isTalking) {
            analyser.getByteFrequencyData(fftData);
            let sum = 0;
            for (let i = 0; i < fftData.length; i++) sum += fftData[i];
            audioAmplitude = (sum / fftData.length) / 128.0;
        } else {
            audioAmplitude = lerp(audioAmplitude, 0, 0.2);
        }

        // --- LIP SYNC ---
        if (isTalking) {
            const lipValue = Math.min(audioAmplitude * 1.5, 1.0);
            setVrmExpression("A", lipValue * 0.6);
            const variation = Math.sin(time / 120) * 0.3;
            setVrmExpression("I", Math.max(0, lipValue * 0.4 + variation));
            setVrmExpression("O", Math.max(0, lipValue * 0.3 - variation));
        }

        // --- AUTONOMOUS BLINKING ---
        if (!isTalking) {
            if (time > nextBlinkTime) {
                blinkActive = true;
                blinkTimer = 0;
                nextBlinkTime = time + (Math.random() * 4000 + 2000);
            }
            if (blinkActive) {
                blinkTimer += deltaTime;
                const blinkVal = blinkTimer < 0.06 ? 1.0 : lerp(1.0, 0.0, (blinkTimer - 0.06) / 0.1);
                setVrmExpression("BlinkL", blinkVal);
                setVrmExpression("BlinkR", blinkVal);
                if (blinkTimer > 0.16) {
                    blinkActive = false;
                    setVrmExpression("BlinkL", 0);
                    setVrmExpression("BlinkR", 0);
                }
            }
        }

        // --- GLOBAL BREATHING (gentle sine on entire model) ---
        const breathe = Math.sin(time / 1800) * 0.008;
        vrm_model.scene.position.y = breathe;

        // --- PILLAR 2: PROCEDURAL GESTURE ENGINE ---
        updateGestureEngine(time, deltaTime);
    }

    renderer.render(scene, camera);
}

// ============================================================
// PILLAR 2 + 3 + 5: GESTURE ENGINE
// ============================================================
function updateGestureEngine(time, dt) {
    const lArm = getBone("LeftUpperArm");
    const rArm = getBone("RightUpperArm");
    const lFore = getBone("LeftLowerArm");
    const rFore = getBone("RightLowerArm");
    const neck = getBone("Neck");
    const head = getBone("Head");
    const spine = getBone("Spine");
    const hips = getBone("Hips");
    const lThigh = getBone("LeftUpperLeg");
    const rThigh = getBone("RightUpperLeg");
    const lShin = getBone("LeftLowerLeg");
    const rShin = getBone("RightLowerLeg");

    // Micro-variation to avoid mechanical look
    const micro = Math.sin(time / 800) * 0.015;

    // --------------------------------------------------------
    // MOUSE GAZE (Pillar 3) — applied in all non-extreme states
    // --------------------------------------------------------
    const gazeStates = ["idle", "talking", "thinking", "pointing", "open_hands", "sitting", "walk"];
    if (neck && head && gazeStates.includes(gestureState)) {
        const targetNeckY = mouseX * 0.35;
        const targetHeadX = -mouseY * 0.18;
        neck.rotation.y = lerp(neck.rotation.y, targetNeckY, 0.04);
        head.rotation.x = lerp(head.rotation.x, targetHeadX, 0.04);
    }

    // --------------------------------------------------------
    // SPINE LEAN (Pillar 3) — avatar leans forward while talking
    // --------------------------------------------------------
    if (spine) {
        const spineTarget = isTalking ? -0.05 : 0.0;
        spine.rotation.x = lerp(spine.rotation.x, spineTarget + breatheSway(time), 0.03);
        spine.rotation.z = lerp(spine.rotation.z, Math.sin(time / 3000) * 0.02, 0.02);
    }

    // --------------------------------------------------------
    // GESTURE STATES
    // --------------------------------------------------------

    if (gestureState === "idle") {
        // Natural arm sway
        if (lArm) {
            lArm.rotation.z = lerp(lArm.rotation.z, 1.2 + micro, 0.04);
            lArm.rotation.x = lerp(lArm.rotation.x, Math.sin(time / 2500) * 0.04, 0.04);
        }
        if (rArm) {
            rArm.rotation.z = lerp(rArm.rotation.z, -1.2 - micro, 0.04);
            rArm.rotation.x = lerp(rArm.rotation.x, Math.sin(time / 2600) * 0.04, 0.04);
        }
        if (lFore) lFore.rotation.y = lerp(lFore.rotation.y, 0.0, 0.04);
        if (rFore) rFore.rotation.y = lerp(rFore.rotation.y, 0.0, 0.04);
        resetLegs(lThigh, rThigh, lShin, rShin, hips);
        resetHead(head, neck, time);
    }

    else if (gestureState === "talking") {
        // Pillar 5: Amplitude-driven gestures. Different variants randomized per utterance.
        const amp = audioAmplitude;
        if (talkGestureVariant === 0) {
            // Variant 0: Right hand emphasis
            if (rArm) {
                rArm.rotation.z = lerp(rArm.rotation.z, -0.7 - amp * 0.3, 0.06);
                rArm.rotation.x = lerp(rArm.rotation.x, 0.1 + amp * 0.2, 0.06);
            }
            if (rFore) rFore.rotation.y = lerp(rFore.rotation.y, -0.3 - amp * 0.4, 0.06);
            if (lArm) lArm.rotation.z = lerp(lArm.rotation.z, 1.1, 0.04);
        } else if (talkGestureVariant === 1) {
            // Variant 1: Both hands open, expressive
            if (lArm) {
                lArm.rotation.z = lerp(lArm.rotation.z, 0.8 + amp * 0.2, 0.06);
                lArm.rotation.x = lerp(lArm.rotation.x, -0.1 - amp * 0.15, 0.06);
            }
            if (rArm) {
                rArm.rotation.z = lerp(rArm.rotation.z, -0.8 - amp * 0.2, 0.06);
                rArm.rotation.x = lerp(rArm.rotation.x, -0.1 - amp * 0.15, 0.06);
            }
            if (lFore) lFore.rotation.y = lerp(lFore.rotation.y, 0.3, 0.05);
            if (rFore) rFore.rotation.y = lerp(rFore.rotation.y, -0.3, 0.05);
        } else if (talkGestureVariant === 2) {
            // Variant 2: Left hand wave while explaining
            if (lArm) {
                lArm.rotation.z = lerp(lArm.rotation.z, 0.6, 0.05);
                lArm.rotation.x = lerp(lArm.rotation.x, -0.3 + Math.sin(time / 400) * 0.1 * amp, 0.08);
            }
            if (rArm) rArm.rotation.z = lerp(rArm.rotation.z, -1.1, 0.04);
        } else {
            // Variant 3: Subtle engaged gesture
            if (rArm) {
                rArm.rotation.z = lerp(rArm.rotation.z, -0.9, 0.05);
                rArm.rotation.x = lerp(rArm.rotation.x, amp * 0.25, 0.06);
            }
            if (lArm) lArm.rotation.z = lerp(lArm.rotation.z, 1.0, 0.04);
        }
        resetLegs(lThigh, rThigh, lShin, rShin, hips);
    }

    else if (gestureState === "thinking") {
        // Right hand to chin area, head slight tilt
        if (rArm) {
            rArm.rotation.z = lerp(rArm.rotation.z, -0.5, 0.07);
            rArm.rotation.x = lerp(rArm.rotation.x, 0.55, 0.07);
        }
        if (rFore) rFore.rotation.y = lerp(rFore.rotation.y, 1.3, 0.07);
        if (lArm) lArm.rotation.z = lerp(lArm.rotation.z, 0.9, 0.05);
        if (head) {
            head.rotation.z = lerp(head.rotation.z, 0.12 + micro, 0.07);
            head.rotation.x = lerp(head.rotation.x, 0.08, 0.05);
        }
        resetLegs(lThigh, rThigh, lShin, rShin, hips);
    }

    else if (gestureState === "pointing") {
        // Right forearm extends forward
        if (rArm) {
            rArm.rotation.z = lerp(rArm.rotation.z, -0.4, 0.08);
            rArm.rotation.x = lerp(rArm.rotation.x, 0.3, 0.08);
        }
        if (rFore) {
            rFore.rotation.y = lerp(rFore.rotation.y, -0.8, 0.08);
            rFore.rotation.x = lerp(rFore.rotation.x, 0.2, 0.05);
        }
        if (lArm) lArm.rotation.z = lerp(lArm.rotation.z, 1.1, 0.04);
        resetLegs(lThigh, rThigh, lShin, rShin, hips);
    }

    else if (gestureState === "open_hands") {
        // Both forearms forward, palms facing up (greeting)
        if (lArm) {
            lArm.rotation.z = lerp(lArm.rotation.z, 0.7, 0.07);
            lArm.rotation.x = lerp(lArm.rotation.x, -0.35, 0.07);
        }
        if (rArm) {
            rArm.rotation.z = lerp(rArm.rotation.z, -0.7, 0.07);
            rArm.rotation.x = lerp(rArm.rotation.x, -0.35, 0.07);
        }
        if (lFore) lFore.rotation.y = lerp(lFore.rotation.y, 0.6, 0.07);
        if (rFore) rFore.rotation.y = lerp(rFore.rotation.y, -0.6, 0.07);
        resetLegs(lThigh, rThigh, lShin, rShin, hips);
    }

    else if (gestureState === "crossed_arms") {
        // Arms folded: arms cross in front of chest
        if (lArm) {
            lArm.rotation.z = lerp(lArm.rotation.z, 0.2, 0.05);
            lArm.rotation.x = lerp(lArm.rotation.x, 0.6, 0.05);
        }
        if (rArm) {
            rArm.rotation.z = lerp(rArm.rotation.z, -0.2, 0.05);
            rArm.rotation.x = lerp(rArm.rotation.x, 0.6, 0.05);
        }
        if (lFore) lFore.rotation.y = lerp(lFore.rotation.y, -1.4, 0.05);
        if (rFore) rFore.rotation.y = lerp(rFore.rotation.y, 1.4, 0.05);
        resetLegs(lThigh, rThigh, lShin, rShin, hips);
        if (head) head.rotation.z = lerp(head.rotation.z, -0.05, 0.05);
    }

    else if (gestureState === "wave") {
        if (rArm) rArm.rotation.z = -1.1 + Math.sin(time / 150) * 0.8;
        if (rFore) rFore.rotation.y = lerp(rFore.rotation.y, 0.9, 0.1);
        if (lArm) lArm.rotation.z = lerp(lArm.rotation.z, 1.1, 0.05);
        resetLegs(lThigh, rThigh, lShin, rShin, hips);
    }

    else if (gestureState === "whisper") {
        if (head) head.rotation.y = lerp(head.rotation.y, 0.25, 0.08);
        if (neck) neck.rotation.x = lerp(neck.rotation.x, 0.15, 0.08);
        if (rArm) rArm.rotation.z = lerp(rArm.rotation.z, -0.9, 0.05);
        resetLegs(lThigh, rThigh, lShin, rShin, hips);
    }

    else if (gestureState === "head_down") {
        // Extreme sadness — head hangs, arms drop
        if (head) head.rotation.x = lerp(head.rotation.x, 0.65, 0.06);
        if (neck) neck.rotation.x = lerp(neck.rotation.x, 0.35, 0.06);
        if (lArm) lArm.rotation.z = lerp(lArm.rotation.z, 1.4, 0.05);
        if (rArm) rArm.rotation.z = lerp(rArm.rotation.z, -1.4, 0.05);
        if (spine) spine.rotation.x = lerp(spine.rotation.x, 0.1, 0.04);
        resetLegs(lThigh, rThigh, lShin, rShin, hips);
    }

    else if (gestureState === "sitting") {
        if (hips) hips.position.y = lerp(hips.position.y, -0.38, 0.05);
        if (lThigh) lThigh.rotation.x = lerp(lThigh.rotation.x, -1.35, 0.06);
        if (rThigh) rThigh.rotation.x = lerp(rThigh.rotation.x, -1.35, 0.06);
        if (lShin) lShin.rotation.x = lerp(lShin.rotation.x, 1.5, 0.06);
        if (rShin) rShin.rotation.x = lerp(rShin.rotation.x, 1.5, 0.06);
        if (lArm) lArm.rotation.z = lerp(lArm.rotation.z, 0.65, 0.06);
        if (rArm) rArm.rotation.z = lerp(rArm.rotation.z, -0.65, 0.06);
        if (lFore) lFore.rotation.y = lerp(lFore.rotation.y, 0.8, 0.06);
        if (rFore) rFore.rotation.y = lerp(rFore.rotation.y, -0.8, 0.06);
    }

    else if (gestureState === "walk") {
        const spd = 6, amt = 0.5;
        const t = time / (1000 / spd);
        if (lThigh) lThigh.rotation.x = Math.sin(t) * amt;
        if (rThigh) rThigh.rotation.x = Math.sin(t + Math.PI) * amt;
        if (lArm) lArm.rotation.x = lerp(lArm.rotation.x, Math.sin(t + Math.PI) * 0.35, 0.1);
        if (rArm) rArm.rotation.x = lerp(rArm.rotation.x, Math.sin(t) * 0.35, 0.1);
        if (hips) {
            hips.position.y = Math.abs(Math.sin(t * 2)) * 0.04;
            hips.position.x = Math.sin(time / 2000) * 0.28; // Pacing left/right
        }
    }
}

// ============================================================
// HELPERS
// ============================================================
function breatheSway(time) {
    return Math.sin(time / 1800) * 0.012;
}

function resetHead(head, neck, time) {
    // Allow mouse gaze to control, just reset z-tilt
    if (head) head.rotation.z = lerp(head.rotation.z, 0, 0.04);
    if (neck) neck.rotation.z = lerp(neck.rotation.z, Math.cos(time / 4500) * 0.015, 0.03);
}

function resetLegs(lThigh, rThigh, lShin, rShin, hips) {
    if (lThigh) lThigh.rotation.x = lerp(lThigh.rotation.x, 0, 0.05);
    if (rThigh) rThigh.rotation.x = lerp(rThigh.rotation.x, 0, 0.05);
    if (lShin) lShin.rotation.x = lerp(lShin.rotation.x, 0, 0.05);
    if (rShin) rShin.rotation.x = lerp(rShin.rotation.x, 0, 0.05);
    if (hips) {
        hips.position.y = lerp(hips.position.y, 0, 0.05);
        hips.position.x = lerp(hips.position.x, 0, 0.05);
    }
}

// Camera controls (legacy buttons still work)
function zoomCamera(delta) { camTarget.z = Math.max(1.5, Math.min(5.0, camTarget.z + delta)); }
function resetCamera() { camTarget = { ...CAM_IDLE }; }
function fullBodyView() { camTarget = { ...CAM_FULL }; }
