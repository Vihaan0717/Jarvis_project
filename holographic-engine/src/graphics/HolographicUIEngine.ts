import * as THREE from 'three';

export class HolographicUIEngine {
    private scene: THREE.Scene;
    private panels: THREE.Group;

    private onCommand: (cmd: string) => void;

    constructor(scene: THREE.Scene, onCommand: (cmd: string) => void) {
        this.scene = scene;
        this.onCommand = onCommand;
        this.panels = new THREE.Group();
        this.scene.add(this.panels);
        this.createControlPanel();
    }

    private createControlPanel() {
        // ... (existing panel)
        
        // Add a "Voice Input" sphere (simulating a microphone)
        const micGeometry = new THREE.SphereGeometry(0.2, 32, 32);
        const micMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x00ffff, 
            emissive: 0x00ffff, 
            emissiveIntensity: 0.5,
            transparent: true,
            opacity: 0.8
        });
        const mic = new THREE.Mesh(micGeometry, micMaterial);
        mic.position.set(-3, 1, -2);
        this.panels.add(mic);

        // Add a simple label/indicator
        console.log("Holographic UI: 'Ask JARVIS' mic added.");
    }

    public simulateVoiceCommand(text: string) {
        console.log("JARVIS Voice Input:", text);
        this.onCommand(text);
    }

    public update() {
        // Floating animation
        this.panels.position.y = Math.sin(Date.now() * 0.001) * 0.1;
    }
}
