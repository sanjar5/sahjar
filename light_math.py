import numpy as np
from math import cos, sin, tan


DEG_TO_RAD = 0.01745329251;

def identityM4x4():
    mat = np.array([[1.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)
                        
    return mat
    
def translateM4x4(t):
    assert(t.size == 3)
    
    mat = np.array([[1.0, 0.0, 0.0, t[0]],
                    [0.0, 1.0, 0.0, t[1]],
                    [0.0, 0.0, 1.0, t[2]],
                    [0.0, 0.0, 0.0,  1.0]], dtype=np.float32)
                        
    return mat

def scaleM4x4(t):
    assert(t.size == 3)
    
    mat = np.array([[t[0],  0.0,  0.0, 0.0],
                    [ 0.0, t[1],  0.0, 0.0],
                    [ 0.0,  0.0, t[2], 0.0],
                    [ 0.0,  0.0,  0.0, 1.0]], dtype=np.float32)
                        
    return mat
    
def rotateXM4x4(phi):
    
    mat = np.array([[1.0,       0.0,       0.0, 0.0],
                    [0.0, +cos(phi), +sin(phi), 0.0],
                    [0.0, -sin(phi), +cos(phi), 0.0],
                    [0.0,       0.0,       0.0, 1.0]], dtype=np.float32)
                        
    return mat
    
def rotateYM4x4(phi):
    
    mat = np.array([[+cos(phi), 0.0, -sin(phi), 0.0],
                    [      0.0, 1.0,       0.0, 0.0],
                    [+sin(phi), 0.0, +cos(phi), 0.0],
                    [      0.0, 0.0,       0.0, 1.0]], dtype=np.float32)
                        
    return mat
    
    
def rotateZM4x4(phi):
    
    mat = np.array([[+cos(phi), +sin(phi), 0.0, 0.0],
                    [-sin(phi), +cos(phi), 0.0, 0.0],
                    [      0.0,       0.0, 1.0, 0.0],
                    [      0.0,       0.0, 0.0, 1.0]], dtype=np.float32)
                        
    return mat
  
def normalize(v):
  norm = np.linalg.norm(v)
  if norm == 0: 
     return v
  return v / norm
  
def lookAtTransposed(eye, center, up):
  assert(eye.size == 3)
  assert(center.size == 3)
  assert(up.size == 3)

  z = normalize(eye - center)
  y = up

  x = normalize(np.cross(y, z))
  y = normalize(np.cross(z, x))
  
  mat = np.array([[+x[0], x[1], x[2], -x[0] * eye[0] - x[1] * eye[1] - x[2] * eye[2]],
                  [+y[0], y[1], y[2], -y[0] * eye[0] - y[1] * eye[1] - y[2] * eye[2]],
                  [+z[0], z[1], z[2], -z[0] * eye[0] - z[1] * eye[1] - z[2] * eye[2]],
                  [  0.0,  0.0,  0.0, 1.0]], dtype=np.float32)

  return mat


def my_frustumf3(left, right, bottom, top, znear, zfar):
  temp  = 2.0 * znear;
  temp2 = right - left;
  temp3 = top - bottom;
  temp4 = zfar - znear;
  matrix = np.array([[          temp / temp2,                    0.0,                      0.0,  0.0],
                     [                   0.0,           temp / temp3,                      0.0,  0.0],
                     [(right + left) / temp2, (top + bottom) / temp3,  (-zfar - znear) / temp4, -1.0],
                     [                   0.0,                    0.0,   (-temp * zfar) / temp4,  0.0]], dtype=np.float32)

  return matrix

def projectionMatrixTransposed(fovy, aspect, zNear, zFar):
  ymax = zNear * tan(fovy * 3.14159265358979323846 / 360.0);
  xmax = ymax * aspect;
  mat = my_frustumf3(-xmax, xmax, -ymax, ymax, zNear, zFar);
  return mat;

def projectionMatrix(fovy, aspect, zNear, zFar):
  zmul = (-2.0 * zNear * zFar) / (zFar - zNear)
  ymul = 1.0 / tan(fovy * 3.14159265 / 360)
  xmul = ymul / aspect
  matrix = np.array([[xmul, 0.0, 0.0, 0.0],
      [0.0, ymul, 0.0, 0.0],
      [0.0, 0.0, -1.0, -1.0],
      [0.0, 0.0, zmul, 0.0]], dtype=np.float32)
  
  return matrix



