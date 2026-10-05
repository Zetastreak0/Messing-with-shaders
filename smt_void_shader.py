import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import math
import sys

# Vertex Shader
VERTEX_SHADER = """
#version 120
attribute vec2 position;
varying vec2 vTexCoord;
void main() {
    gl_Position = vec4(position, 0.0, 1.0);
    // Map [-1, 1] position to [0, 1] texture coordinates
    vTexCoord = position * 0.5 + 0.5;
}
"""

# Fragment Shader implementing the SMT IV-inspired procedural boss void
FRAGMENT_SHADER = """
#version 120
uniform float u_time;
uniform vec2 u_resolution;
varying vec2 vTexCoord;

void main() {
    // Normalize coordinates centered at (0.5, 0.5) adjusted for aspect ratio
    vec2 uv = vTexCoord - 0.5;
    uv.x *= u_resolution.x / u_resolution.y;

    // Layer 1: Swirling vortex using polar coordinates
    float r1 = length(uv);
    float theta1 = atan(uv.y, uv.x);
    
    // Distort the radius over time and angle to create a pulsing wave effect
    float distort1 = sin(r1 * 12.0 - u_time * 2.0) * 0.15;
    float swirl1 = theta1 + r1 * 4.0 + sin(u_time * 0.5) * 2.0;
    
    // Create rhythmic energy bands
    float pattern1 = sin(swirl1 * 4.0 + distort1 * 8.0);
    pattern1 = smoothstep(0.1, 0.8, abs(pattern1));

    // Layer 2: Counter-rotating, melting chaotic noise layer
    vec2 uv2 = uv;
    uv2.x += sin(uv2.y * 8.0 + u_time) * 0.1;
    uv2.y += cos(uv2.x * 6.0 - u_time * 1.5) * 0.1;
    
    float r2 = length(uv2);
    float theta2 = atan(uv2.y, uv2.x);
    float pattern2 = cos(theta2 * 5.0 - r2 * 10.0 + u_time * 2.5);
    pattern2 = smoothstep(0.2, 0.7, abs(pattern2));

    // Combine layers using multiplicative and additive logic
    float finalNoise = mix(pattern1, pattern2, 0.4);

    // Color Palette Shift (SMT IV style: dark blues, deep purples, neon cyan sparks)
    vec3 baseBg = vec3(0.02, 0.02, 0.08); // Dark atmospheric void
    vec3 neonCyan = vec3(0.0, 0.8, 0.9);
    vec3 deepPurple = vec3(0.5, 0.0, 0.6);
    
    // Dynamically cycle palette colors over time
    vec3 pulseColor = mix(deepPurple, neonCyan, sin(u_time * 0.8) * 0.5 + 0.5);
    vec3 finalColor = mix(baseBg, pulseColor, finalNoise * (1.0 - r1 * 0.8));

    // Add a dark vignette around the screen edges
    float vignette = smoothstep(0.7, 0.3, r1);
    finalColor *= vignette;

    gl_FragColor = vec4(finalColor, 1.0);
}
"""

def main():
    pygame.init()
    width, height = 800, 600
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("SMT IV Minotaur Background Simulator")
    clock = pygame.time.Clock()

    # Compile Shaders
    shader = compileProgram(
        compileShader(VERTEX_SHADER, GL_VERTEX_SHADER),
        compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)
    )

    # Simple full-screen quad (2 triangles)
    # Each vertex has X, Y coordinates
    vertices = [
        -1.0, -1.0,
         1.0, -1.0,
         1.0,  1.0,
        -1.0, -1.0,
         1.0,  1.0,
        -1.0,  1.0
    ]
    
    import numpy as np
    vbo_data = np.array(vertices, dtype=np.float32)

    # Generate VBO
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vbo_data.nbytes, vbo_data, GL_STATIC_DRAW)

    # Get Attribute and Uniform locations
    glUseProgram(shader)
    position_loc = glGetAttribLocation(shader, "position")
    glEnableVertexAttribArray(position_loc)
    glVertexAttribPointer(position_loc, 2, GL_FLOAT, GL_FALSE, 0, None)

    time_loc = glGetUniformLocation(shader, "u_time")
    res_loc = glGetUniformLocation(shader, "u_resolution")

    glUniform2f(res_loc, float(width), float(height))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

        # Clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Update time uniform
        current_time = pygame.time.get_ticks() / 1000.0
        glUniform1f(time_loc, current_time)

        # Draw full screen quad
        glDrawArrays(GL_TRIANGLES, 0, 6)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
