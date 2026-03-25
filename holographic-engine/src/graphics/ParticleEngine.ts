import * as THREE from 'three';
import vertexShader from './shaders/particle.vert?raw';
import fragmentShader from './shaders/particle.frag?raw';
import * as dat from 'dat.gui';

export class ParticleEngine {
    private scene: THREE.Scene;
    private count: number = 100000;
    private points: THREE.Points | null = null;
    private geometry: THREE.BufferGeometry | null = null;
    private material: THREE.ShaderMaterial | null = null;
    private gui: dat.GUI;

    private morphFactor: number = 0;
    private isDrawMode: boolean = false;
    private drawPoints: THREE.Vector3[] = [];

    constructor(scene: THREE.Scene) {
        this.scene = scene;
        this.gui = new dat.GUI();
        this.initParticles();
        this.initGUI();
    }

    private initParticles() {
        this.geometry = new THREE.BufferGeometry();
        
        const positions = new Float32Array(this.count * 3);
        const offsets = new Float32Array(this.count * 3);
        const targets = new Float32Array(this.count * 3);
        const colors = new Float32Array(this.count * 3);

        const color = new THREE.Color(0x00ffff);

        for (let i = 0; i < this.count; i++) {
            positions[i * 3] = 0;
            positions[i * 3 + 1] = 0;
            positions[i * 3 + 2] = 0;

            // Start with random distribution
            const pos = this.getRandomPosition();
            offsets[i * 3] = pos.x;
            offsets[i * 3 + 1] = pos.y;
            offsets[i * 3 + 2] = pos.z;

            // Target (same as start initially)
            targets[i * 3] = pos.x;
            targets[i * 3 + 1] = pos.y;
            targets[i * 3 + 2] = pos.z;

            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;
        }

        this.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        this.geometry.setAttribute('aOffset', new THREE.BufferAttribute(offsets, 3));
        this.geometry.setAttribute('aTargetPosition', new THREE.BufferAttribute(targets, 3));
        this.geometry.setAttribute('aColor', new THREE.BufferAttribute(colors, 3));

        this.material = new THREE.ShaderMaterial({
            vertexShader,
            fragmentShader,
            uniforms: {
                uTime: { value: 0 },
                uSize: { value: 2.0 },
                uMorphFactor: { value: 0.0 }
            },
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false
        });

        this.points = new THREE.Points(this.geometry, this.material);
        this.scene.add(this.points);
    }

    private getRandomPosition() {
        return new THREE.Vector3(
            (Math.random() - 0.5) * 10,
            (Math.random() - 0.5) * 10,
            (Math.random() - 0.5) * 10
        );
    }

    private getSpherePosition() {
        const phi = Math.acos(-1 + (2 * Math.random()));
        const theta = Math.sqrt(this.count * Math.PI) * phi;
        const radius = 3;
        return new THREE.Vector3(
            radius * Math.cos(theta) * Math.sin(phi),
            radius * Math.sin(theta) * Math.sin(phi),
            radius * Math.cos(phi)
        );
    }

    private getCubePosition() {
        return new THREE.Vector3(
            (Math.random() - 0.5) * 5,
            (Math.random() - 0.5) * 5,
            (Math.random() - 0.5) * 5
        );
    }

    private initGUI() {
        const params = {
            shape: 'random',
            particleCount: this.count,
            size: 2.0,
            color: '#00ffff'
        };

        this.gui.add(params, 'shape', ['random', 'sphere', 'cube', 'tetrahedron', 'triangle', 'image']).onChange((value: string) => {
            if (value === 'image') {
                this.loadAndMorphImage('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/sprites/snowflake1.png');
            } else {
                this.morphTo(value);
            }
        });

        this.gui.add(params, 'particleCount', 1000, 200000).step(1000).onFinishChange((value: number) => {
            this.setCount(value);
        });

        this.gui.add(params, 'size', 0.1, 10).onChange((value: number) => {
            if (this.material) this.material.uniforms.uSize.value = value;
        });

        this.gui.addColor(params, 'color').onChange((value: string) => {
            if (this.geometry) {
                const color = new THREE.Color(value);
                const colors = this.geometry.attributes.aColor.array as Float32Array;
                for (let i = 0; i < this.count; i++) {
                    colors[i * 3] = color.r;
                    colors[i * 3 + 1] = color.g;
                    colors[i * 3 + 2] = color.b;
                }
                this.geometry.attributes.aColor.needsUpdate = true;
            }
        });

        const commands = {
            input: "Jarvis VR mode",
            ask: () => {
                const core = (window as any).jarvisCore;
                if (core) core.executeCommand(commands.input);
            }
        };
        const guiFolder = this.gui.addFolder('AI Command Lab');
        guiFolder.add(commands, 'input').name('Command');
        guiFolder.add(commands, 'ask').name('Ask JARVIS');
        guiFolder.open();
    }

    private loadAndMorphImage(url: string) {
        const loader = new THREE.ImageLoader();
        loader.load(url, (image) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d')!;
            canvas.width = 128;
            canvas.height = 128;
            ctx.drawImage(image, 0, 0, 128, 128);
            const imageData = ctx.getImageData(0, 0, 128, 128).data;
            
            this.morphToImage(imageData, 128, 128);
        });
    }

    private morphToImage(data: Uint8ClampedArray, width: number, height: number) {
        if (!this.geometry || !this.material) return;

        const offsets = this.geometry.attributes.aOffset.array as Float32Array;
        const targets = this.geometry.attributes.aTargetPosition.array as Float32Array;
        const currentMorph = this.material.uniforms.uMorphFactor.value;

        // Calculate valid pixel positions (non-transparent/bright enough)
        const validPixels: THREE.Vector3[] = [];
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const idx = (y * width + x) * 4;
                const brightness = (data[idx] + data[idx + 1] + data[idx + 2]) / 3;
                if (brightness > 20) {
                    const depth = (brightness / 255) * 2; // Simulate depth based on brightness
                    validPixels.push(new THREE.Vector3(
                        (x / width - 0.5) * 10,
                        (0.5 - y / height) * 10,
                        depth - 1
                    ));
                }
            }
        }

        for (let i = 0; i < this.count; i++) {
            offsets[i * 3] = THREE.MathUtils.lerp(offsets[i * 3], targets[i * 3], currentMorph);
            offsets[i * 3 + 1] = THREE.MathUtils.lerp(offsets[i * 3 + 1], targets[i * 3 + 1], currentMorph);
            offsets[i * 3 + 2] = THREE.MathUtils.lerp(offsets[i * 3 + 2], targets[i * 3 + 2], currentMorph);

            const pixelPos = validPixels[i % validPixels.length];
            targets[i * 3] = pixelPos.x;
            targets[i * 3 + 1] = pixelPos.y;
            targets[i * 3 + 2] = pixelPos.z;
        }

        this.geometry.attributes.aOffset.needsUpdate = true;
        this.geometry.attributes.aTargetPosition.needsUpdate = true;
        
        this.material.uniforms.uMorphFactor.value = 0;
        this.morphFactor = 0;
    }

    private getTetrahedronPosition() {
        const r = 4;
        const vertices = [
            new THREE.Vector3(r, r, r),
            new THREE.Vector3(-r, -r, r),
            new THREE.Vector3(-r, r, -r),
            new THREE.Vector3(r, -r, -r)
        ];
        
        const v1 = vertices[Math.floor(Math.random() * 4)];
        const v2 = vertices[Math.floor(Math.random() * 4)];
        const v3 = vertices[Math.floor(Math.random() * 4)];
        
        const a = Math.random();
        const b = Math.random();
        if (a + b > 1) {
            return new THREE.Vector3().addScaledVector(v1, 1 - a).addScaledVector(v2, a - b).addScaledVector(v3, b);
        }
        return new THREE.Vector3().addScaledVector(v1, 1 - a - b).addScaledVector(v2, a).addScaledVector(v3, b);
    }

    private getTrianglePosition() {
        const r = 5;
        const v1 = new THREE.Vector3(0, r, 0);
        const v2 = new THREE.Vector3(-r, -r, 0);
        const v3 = new THREE.Vector3(r, -r, 0);
        
        const a = Math.random();
        const b = Math.random();
        if (a + b > 1) {
            return new THREE.Vector3().lerpVectors(v1, v2, 1 - a).lerp(v3, b);
        }
        return new THREE.Vector3().lerpVectors(v1, v2, a).lerp(v3, b);
    }

    public morphTo(shape: string) {
        if (!this.geometry || !this.material) return;

        const offsets = this.geometry.attributes.aOffset.array as Float32Array;
        const targets = this.geometry.attributes.aTargetPosition.array as Float32Array;
        const currentMorph = this.material.uniforms.uMorphFactor.value;

        for (let i = 0; i < this.count; i++) {
            offsets[i * 3] = THREE.MathUtils.lerp(offsets[i * 3], targets[i * 3], currentMorph);
            offsets[i * 3 + 1] = THREE.MathUtils.lerp(offsets[i * 3 + 1], targets[i * 3 + 1], currentMorph);
            offsets[i * 3 + 2] = THREE.MathUtils.lerp(offsets[i * 3 + 2], targets[i * 3 + 2], currentMorph);

            let newPos: THREE.Vector3;
            switch (shape) {
                case 'sphere': newPos = this.getSpherePosition(); break;
                case 'cube': newPos = this.getCubePosition(); break;
                case 'tetrahedron': newPos = this.getTetrahedronPosition(); break;
                case 'triangle': newPos = this.getTrianglePosition(); break;
                default: newPos = this.getRandomPosition();
            }
            targets[i * 3] = newPos.x;
            targets[i * 3 + 1] = newPos.y;
            targets[i * 3 + 2] = newPos.z;
        }

        this.geometry.attributes.aOffset.needsUpdate = true;
        this.geometry.attributes.aTargetPosition.needsUpdate = true;
        
        this.material.uniforms.uMorphFactor.value = 0;
        this.morphFactor = 0;
    }

    public update() {
        if (this.material) {
            this.material.uniforms.uTime.value = performance.now() * 0.001;
            
            if (this.morphFactor < 1.0) {
                this.morphFactor += 0.02; // Speed of morphing
                if (this.morphFactor > 1.0) this.morphFactor = 1.0;
                this.material.uniforms.uMorphFactor.value = this.morphFactor;
            }
        }
    }

    public setCount(newCount: number) {
        if (this.points) {
            this.scene.remove(this.points);
            this.geometry?.dispose();
            this.material?.dispose();
        }
        this.count = newCount;
        this.initParticles();
    }

    public enableDrawMode(enable: boolean) {
        this.isDrawMode = enable;
        if (!enable) this.drawPoints = [];
    }

    public addDrawPoint(point: THREE.Vector3) {
        if (!this.isDrawMode) return;
        this.drawPoints.push(point);
        if (this.drawPoints.length > 1000) this.drawPoints.shift();
        
        // Update particles to follow draw points
        const targets = this.geometry!.attributes.aTargetPosition.array as Float32Array;
        for (let i = 0; i < this.count; i++) {
            const p = this.drawPoints[i % this.drawPoints.length];
            targets[i * 3] = p.x;
            targets[i * 3 + 1] = p.y;
            targets[i * 3 + 2] = p.z;
        }
        this.geometry!.attributes.aTargetPosition.needsUpdate = true;
        this.material!.uniforms.uMorphFactor.value = 1.0;
        this.morphFactor = 1.0;
    }
}
