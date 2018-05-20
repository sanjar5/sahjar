from plyfile import PlyData
from OpenGL.arrays import ArrayDatatype
from OpenGL.GL import (GL_ARRAY_BUFFER,
                       GL_FALSE, GL_FLOAT, GL_INT, GL_UNSIGNED_INT,
                       GL_STATIC_DRAW,GL_ELEMENT_ARRAY_BUFFER,
                       GL_PRIMITIVE_RESTART,glBindBuffer,
                       glBindVertexArray,glEnableVertexAttribArray,
                       glGenBuffers, glGenVertexArrays,
                       glVertexAttribPointer, glVertexAttribIPointer, glBufferData,
                       glEnable, glPrimitiveRestartIndex)
from light_math import normalize
import numpy as np


def read_ply():

    plydata = PlyData.read('cloud.ply')
    vertices_list = []
    normal_list = []
    color_list = []

    for data in plydata.elements[0].data:
        vertices_list.append([data[0],data[1],data[2]])
        normal_list.append([data[3],data[4],data[5]])
        color_list.append([data[6], data[7], data[8]])

    vector_vertices = np.array(vertices_list, dtype=np.float32)
    vector_normal = np.array(normal_list, dtype=np.float32)
    vector_color = np.array(color_list, dtype=np.float32)

    vector_color /= 255.0


    vao = glGenVertexArrays(1)
    vbo_vertices = glGenBuffers(1)
    vbo_normals = glGenBuffers(1)
    vbo_colors = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
    glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(vector_vertices), vector_vertices.flatten(), GL_STATIC_DRAW)  #
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, vbo_normals)
    glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(vector_normal), vector_normal.flatten(), GL_STATIC_DRAW)  #
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, vbo_colors)
    glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(vector_color), vector_color.flatten(),
                 GL_STATIC_DRAW)  #
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(2)


    glBindVertexArray(0)

    return vao, len(vertices_list)