varying vec3 vColor;

void main() {
    float r = distance(gl_PointCoord, vec2(0.5));
    if (r > 0.5) discard;
    
    // Neon glow effect: brighter center, soft edge
    float glow = 1.0 - smoothstep(0.0, 0.5, r);
    gl_FragColor = vec4(vColor, glow);
}
