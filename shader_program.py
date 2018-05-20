import os
from OpenGL.GL import (glCreateProgram, glLinkProgram, glDeleteProgram, 
                       glCreateShader, glShaderSource, glCompileShader, glAttachShader, glDeleteShader, 
                       glGetAttribLocation, glGetProgramiv, glGetShaderiv,
                       glGetUniformLocation, glGetShaderInfoLog, glGetProgramInfoLog, glUseProgram,
                       GL_FLOAT, GL_TRUE, GL_FALSE, GL_COMPILE_STATUS, GL_LINK_STATUS, GL_VERTEX_SHADER,
                       GL_FRAGMENT_SHADER, GL_GEOMETRY_SHADER, GL_TESS_CONTROL_SHADER, GL_TESS_EVALUATION_SHADER,
                       GL_COMPUTE_SHADER)

class ShaderProgram(object):
  
  def __init__(self, shaderPaths = []):
      
    self.shader_program = glCreateProgram()
    self.shader_objects = {}
    for (shader_type, path) in shaderPaths:
      self.shader_objects[shader_type] = self.loadAndCompileShaderObject(shader_type, path)
      glAttachShader(self.shader_program, self.shader_objects[shader_type])
      
    glLinkProgram(self.shader_program)
    if glGetProgramiv(self.shader_program, GL_LINK_STATUS) != GL_TRUE:
      info = glGetProgramInfoLog(self.shader_program)
      glDeleteProgram(self.shader_program)
      for shader in self.shader_objects :
        glDeleteShader(shader)
      raise RuntimeError("Error in program linking: %s"%info)


  def loadAndCompileShaderObject(self, shader_type, path):
    
    if not os.path.exists(path):
      raise RuntimeError('Shader source not found at: %s'%path)
        
    source_file = open(path)
    shader_source = source_file.read()
    source_file.close()
    shader_object = glCreateShader(shader_type)
    glShaderSource(shader_object, shader_source)
    glCompileShader(shader_object)
    if glGetShaderiv(shader_object, GL_COMPILE_STATUS) != GL_TRUE:
      info = glGetShaderInfoLog(shader_object)
      raise RuntimeError('Shader compilation failed:\n %s'%info)
    return shader_object


  def attribLocation(self, name):
    return glGetAttribLocation(self.shader_program, name)

  def uniformLocation(self, name):
    return glGetUniformLocation(self.shader_program, name)
  
  def bindProgram(self):
    glUseProgram(self.shader_program)
      
  def unbindProgram(self):
    glUseProgram(0)