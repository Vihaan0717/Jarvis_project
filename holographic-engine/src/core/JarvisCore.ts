import { ParticleEngine } from "../graphics/ParticleEngine";
import { GestureEngine } from "../interaction/GestureEngine";
import { SimulationEngine } from "../physics/SimulationEngine";
import { HolographicUIEngine } from "../graphics/HolographicUIEngine";
import { IntentInterpreter } from "./IntentInterpreter";
import * as THREE from 'three';

export class JarvisCore {
    private particleEngine: ParticleEngine;
    private gestureEngine: GestureEngine;
    private simulationEngine: SimulationEngine;
    private uiEngine: HolographicUIEngine;
    private interpreter: IntentInterpreter;
    constructor(scene: THREE.Scene) {
        this.particleEngine = new ParticleEngine(scene);
        this.gestureEngine = new GestureEngine((gesture, data) => this.handleGesture(gesture, data));
        this.simulationEngine = new SimulationEngine(this.particleEngine);
        this.uiEngine = new HolographicUIEngine(scene, (cmd) => this.executeCommand(cmd));
        this.interpreter = new IntentInterpreter();
    }

    private handleGesture(gesture: string, data: any) {
        if (gesture === "grab") {
            // Manipulate particles near the hand position
            console.log("JARVIS: Grabbing holographic space at", data);
        } else if (gesture === "zoom") {
            // Scale the particle structure
            console.log("JARVIS: Zooming holographic projection");
        }
    }

    public update() {
        this.particleEngine.update();
        this.gestureEngine.update();
        this.simulationEngine.update();
        this.uiEngine.update();
    }

    public executeCommand(command: string) {
        const intent = this.interpreter.interpret(command);
        if (!intent) return;

        console.log("JARVIS Intent:", intent);

        switch (intent.action) {
            case "morph":
                this.particleEngine.morphTo(intent.params.shape);
                break;
            case "setCount":
                this.particleEngine.setCount(intent.params.count);
                break;
            case "simulate":
                if (intent.params.type === "molecular") this.simulationEngine.applyLennardJones();
        }
    }
}
