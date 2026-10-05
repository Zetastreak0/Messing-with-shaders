import pygame
from pygame.locals import *
from OpenGL.GL import *
import sys
import time
import os
import glob

shaderDict = {"V":None,
             "F":{}}
activeSh = None
directory = "Assets/shaders/"

def compile_shader(shader_type, source):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(shader).decode('utf-8'))
    return shader

def linkFSVS(FS, VS):
    program = glCreateProgram()
    glAttachShader(program, VS)
    glAttachShader(program, FS)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        raise RuntimeError(f"Failed linking file '{FS}' to '{VS}':\n{glGetProgramInfoLog(program).decode('utf-8')}")
    time_loc = glGetUniformLocation(program, "time")
    return (program, time_loc)

def init_shaders():
    with open(os.path.join(directory, "vertexS.txt"), "r", encoding="utf-8-sig") as file:
        sh = file.read().strip()
        shaderDict["V"] = compile_shader(GL_VERTEX_SHADER, sh)
        
    direct = os.fsencode(directory)
    listing = os.listdir(direct)
    listing.sort()
    for file in listing:
        shader = os.fsdecode(file)

        print(f"Loading fragment shader: {shader}")
        
        with open(os.path.join(directory, shader), "r", encoding="utf-8-sig") as script:
            sh = script.read().strip()
            if shader.startswith("vertex") or not shader.endswith(".txt"):
                continue
            else:
                fs = compile_shader(GL_FRAGMENT_SHADER, sh)
                shaderDict["F"][shader[0:-4]] = [linkFSVS(fs, shaderDict["V"]), time.time()]
                

def change_active(target):
    if target in shaderDict["F"]:
        global activeSh
        activeSh = target
        shaderDict["F"][target][1] = time.time()
    else:
        print("invalid shader")
        pass

def check():
    global activeSh
    prog, l = shaderDict["F"][activeSh][0]
    time_loc = glGetUniformLocation(prog, "time")
    res_loc = glGetUniformLocation(prog, "u_resolution")
    print(f"Time loc: {time_loc}, Res loc: {res_loc}") # Both should be 0 or greater



def set_viewport(width, height, matrix = False):
    glViewport(0,0,width, height)
    if matrix:
        set_matrix()

def set_matrix():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def unset_matrix(width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def update_shaders(width, height, active = False):
    if active:
        if shaderDict["F"] is not None and shaderDict["F"][activeSh] is not None:
            #setup and shader update=========================
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            set_matrix()
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)
            program, loc = shaderDict["F"][activeSh][0]
            glUseProgram(program)
            glUniform1f(loc, time.time() - shaderDict["F"][activeSh][1])
            
            res_loc = glGetUniformLocation(program, "u_resolution")
            glUniform2f(res_loc, float(width), float(height))

            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(-1.0, -1.0)
            glTexCoord2f(1.0, 0.0); glVertex2f(1.0, -1.0)
            glTexCoord2f(1.0, 1.0); glVertex2f(1.0, 1.0)
            glTexCoord2f(0.0, 1.0); glVertex2f(-1.0, 1.0)
            glEnd()
            #===============================================

            #cleanup========================
            glUseProgram(0)
            unset_matrix(width, height)
            glDisable(GL_TEXTURE_2D)
        else:
            #print("no active shaders")
            pass
        

def merge_layers(sprite_surface):
    data = pygame.image.tostring(sprite_surface, "RGBA", True)
    width, height = sprite_surface.get_size()
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                 width, height, 0, GL_RGBA,
                 GL_UNSIGNED_BYTE, data)

    drawGL(tex_id, width, height)

    return tex_id

def update_layers(sprite_surface, tex_id):
    if tex_id == None:
        tex_id = merge_layers(sprite_surface)
    else:
        data = pygame.image.tostring(sprite_surface, "RGBA", True)
        width, height = sprite_surface.get_size()
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0,
                     width, height, GL_RGBA,
                     GL_UNSIGNED_BYTE, data)
        drawGL(tex_id, width, height)
    
    return tex_id


def drawGL(tex_id, width, height):
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex2f(0, 0)
    glTexCoord2f(1.0, 0.0); glVertex2f(width, 0)
    glTexCoord2f(1.0, 1.0); glVertex2f(width, height)
    glTexCoord2f(0.0, 1.0); glVertex2f(0, height)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    

















        

    
