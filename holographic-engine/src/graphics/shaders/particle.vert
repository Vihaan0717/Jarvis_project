uniform float uTime;
uniform float uSize;
uniform float uMorphFactor;

attribute vec3 aOffset;
attribute vec3 aTargetPosition;
attribute vec3 aColor;

varying vec3 vColor;

void main() {
    vColor = aColor;
    
    // Morph between current offset and target position
    vec3 animatedPos = mix(aOffset, aTargetPosition, uMorphFactor);
    
    // Add some GPU noise/animation
    animatedPos.y += sin(uTime + animatedPos.x * 10.0) * 0.05;
    
    vec3 pos = position + animatedPos;
    
    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
    gl_PointSize = uSize * (300.0 / -mvPosition.z);
    gl_Position = projectionMatrix * mvPosition;
}
