import { HandLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";

export class GestureEngine {
    private handLandmarker: HandLandmarker | null = null;
    private video: HTMLVideoElement | null = null;
    private lastVideoTime: number = -1;
    private onGesture: (gesture: string, data?: any) => void;

    constructor(onGesture: (gesture: string, data?: any) => void) {
        this.onGesture = onGesture;
        this.initMediaPipe();
        this.initWebcam();
    }

    private async initMediaPipe() {
        const vision = await FilesetResolver.forVisionTasks(
            "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
        );
        this.handLandmarker = await HandLandmarker.createFromOptions(vision, {
            baseOptions: {
                modelAssetPath: `https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task`,
                delegate: "GPU"
            },
            runningMode: "VIDEO",
            numHands: 2
        });
        console.log("MediaPipe Hand Landmarker initialized");
    }

    private async initWebcam() {
        this.video = document.createElement("video");
        this.video.style.display = "none";
        document.body.appendChild(this.video);

        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        this.video.srcObject = stream;
        this.video.play();
    }

    public update() {
        if (!this.handLandmarker || !this.video || this.video.readyState !== 4) return;

        const startTimeMs = performance.now();
        if (this.lastVideoTime !== this.video.currentTime) {
            this.lastVideoTime = this.video.currentTime;
            const results = this.handLandmarker.detectForVideo(this.video, startTimeMs);
            
            if (results.landmarks) {
                this.processLandmarks(results.landmarks);
            }
        }
    }

    private processLandmarks(landmarks: any[][]) {
        if (landmarks.length === 0) return;

        const hand = landmarks[0];
        const thumbTip = hand[4];
        const indexTip = hand[8];
        const pinkyTip = hand[20];

        // Pinch detection (Thumb + Index)
        const pinchDist = Math.sqrt(
            Math.pow(thumbTip.x - indexTip.x, 2) +
            Math.pow(thumbTip.y - indexTip.y, 2) +
            Math.pow(thumbTip.z - indexTip.z, 2)
        );

        if (pinchDist < 0.05) {
            this.onGesture("grab", { x: indexTip.x, y: indexTip.y });
        }

        // Spread detection (Distance between thumb and pinky)
        const spreadDist = Math.sqrt(
            Math.pow(thumbTip.x - pinkyTip.x, 2) +
            Math.pow(thumbTip.y - pinkyTip.y, 2)
        );

        if (spreadDist > 0.2) {
            this.onGesture("zoom", { distance: spreadDist });
        }
    }
}
