
import numpy as np
from OpenGL.arrays import ArrayDatatype
from OpenGL.GL import (GL_ARRAY_BUFFER,
                       GL_FALSE, GL_FLOAT,
                       GL_STATIC_DRAW,GL_ELEMENT_ARRAY_BUFFER,
                       GL_PRIMITIVE_RESTART,glBindBuffer,
                       glBindVertexArray,glEnableVertexAttribArray,
                       glGenBuffers, glGenVertexArrays,
                       glVertexAttribPointer,glBufferData,
                       glEnable, glPrimitiveRestartIndex)
from light_math import normalize
from random import randint

def create_field(rows, cols, size, fun, gen_textures, gen_relief = False):

    normals_vec = np.zeros((rows * cols, 3), dtype=np.float32)

    vertices_list = []
    texcoords_list = []
    faces_list = []
    indices_list = []

    if not gen_relief:
        for z in range(0, rows):
            for x in range(0, cols):

               # if (x**2 + z**2)**(1/2) <= cols:
                    xx = -size / 2 + x * size / cols
                    zz = -size / 2 + z * size / rows

                    try:
                        yy = fun(xx, zz)
                        if yy < -size/2:
                            yy = -size / 2
                        if yy > size/2:
                            yy = size / 2
                    except (ArithmeticError, ValueError):
                        yy = 0.0

                    vertices_list.append([xx, yy, zz])
                    if gen_textures:
                        texcoords_list.append([x / float(cols - 1), z / float(rows - 1)])
    else:
        buff1 = []
        vertices_list_mountain = []
        for z in range(0, rows):
            del buff1[:]
            for x in range(0, cols):
                xx = -size / 2 + x * size / cols
                zz = -size / 2 + z * size / rows
                yy = 0.0

                buff1.append([xx, yy, zz])

            vertices_list_mountain.append(buff1[:])
        for i in range(0, 250):
            radius = 12
            z = randint(0,rows-1)
            x = randint(0,cols-1)
            for iz in range(z - radius,z + radius):
                if iz < 0 or iz > rows-1 :
                    continue
                else:
                    for ix in range(x - radius, x + radius):
                        if ix < 0 or ix > cols-1:
                            continue
                        else:
                            if radius ** 2 - ((z - iz+10) ** 2 + (x - ix) ) > vertices_list_mountain[iz][ix][1]**(2):
                                vertices_list_mountain[iz][ix][1] = (radius ** 2 - ((z - iz+ 10) ** 2 + (x - ix) ))**(1/2)
                            else: continue

        v = vertices_list_mountain[:]
        vec_lines = []
        for ii in range(0,10):
            i = 2 * ii
            for z in range(0, rows-1):
                for x in range(0, cols-1):
                    xx = -size / 2 + x * size / cols
                    zz = -size / 2 + z * size / rows

                    if v[z][x][1] < i and v[z][x + 1][1] < i and v[z + 1][x][1] < i and v[z + 1][x + 1][1] < i or \
                            v[z][x][1] >= i and v[z][x + 1][1] >= i and v[z + 1][x][1] >= i and v[z + 1][x + 1][1] >= i:
                        continue
                    elif v[z][x][1] >= i and v[z][x + 1][1] < i and v[z + 1][x][1] < i and v[z + 1][x + 1][1] < i:
                        vec_lines.append([xx + 0.25, i, zz])
                        vec_lines.append([xx, i, zz + 0.25])
                    elif v[z][x][1] < i and v[z][x + 1][1] >= i and v[z + 1][x][1] < i and v[z + 1][x + 1][1] < i:
                        vec_lines.append([xx + 0.25, i, zz])
                        vec_lines.append([xx + 0.5, i, zz + 0.25])
                    elif v[z][x][1] < i and v[z][x + 1][1] < i and v[z + 1][x][1] >= i and v[z + 1][x + 1][1] < i:
                        vec_lines.append([xx + 0.25, i, zz + 0.5])
                        vec_lines.append([xx, i, zz + 0.25])
                    elif v[z][x][1] < i and v[z][x + 1][1] < i and v[z + 1][x][1] < i and v[z + 1][x + 1][1] >= i:
                        vec_lines.append([xx + 0.25, i, zz + 0.5])
                        vec_lines.append([xx + 0.5, i, zz + 0.25])

                    elif v[z][x][1] < i and v[z][x + 1][1] >= i and v[z + 1][x][1] >= i and v[z + 1][x + 1][1] >= i:
                        vec_lines.append([xx + 0.25, i, zz])
                        vec_lines.append([xx, i, zz + 0.25])
                    elif v[z][x][1] >= i and v[z][x + 1][1] < i and v[z + 1][x][1] >= i and v[z + 1][x + 1][1] >= i:
                        vec_lines.append([xx + 0.25, i, zz])
                        vec_lines.append([xx + 0.5, i, zz + 0.25])
                    elif v[z][x][1] >= i and v[z][x + 1][1] >= i and v[z + 1][x][1] < i and v[z + 1][x + 1][1] >= i:
                        vec_lines.append([xx + 0.25, i, zz + 0.5])
                        vec_lines.append([xx, i, zz + 0.25])
                    elif v[z][x][1] >= i and v[z][x + 1][1] >= i and v[z + 1][x][1] >= i and v[z + 1][x + 1][1] < i:
                        vec_lines.append([xx + 0.25, i, zz + 0.5])
                        vec_lines.append([xx + 0.5, i, zz + 0.25])

                    elif v[z][x][1] < i and v[z][x + 1][1] < i and v[z + 1][x][1] >= i and v[z + 1][x + 1][1] >= i or \
                         v[z][x][1] >= i and v[z][x + 1][1] >= i and v[z + 1][x][1] < i and v[z + 1][x + 1][1] < i:
                        vec_lines.append([xx, i, zz + 0.25])
                        vec_lines.append([xx + 0.5, i, zz + 0.25])
                    elif v[z][x][1] >= i and v[z][x + 1][1] < i and v[z + 1][x][1] >= i and v[z + 1][x + 1][1] < i or \
                            v[z][x][1] < i and v[z][x + 1][1] >= i and v[z + 1][x][1] < i and v[z + 1][x + 1][1] >= i:
                        vec_lines.append([xx + 0.25, i, zz])
                        vec_lines.append([xx + 0.25, i, zz + 0.5])

                    elif v[z][x][1] >= i and v[z][x + 1][1] < i and v[z + 1][x][1] < i and v[z + 1][x + 1][1] >= i or \
                            v[z][x][1] < i and v[z][x + 1][1] >= i and v[z + 1][x][1] >= i and v[z + 1][x + 1][1] < i:
                        vec_lines.append([xx, i, zz + 0.25])
                        vec_lines.append([xx + 0.25, i, zz])
                        vec_lines.append([xx + 0.5, i, zz + 0.25])
                        vec_lines.append([xx + 0.25, i, zz + 0.5])


        index_lines = [it for it in range(0,len(vec_lines))]
        vector_lines = np.array(vec_lines, dtype=np.float32)
        vector_line_indexes = np.array(index_lines, dtype=np.uint32)


        for z in range(0, rows):
            for x in range(0, cols):
                vertices_list.append(vertices_list_mountain[z][x])

    primRestart = rows * cols

    vertices_vec = np.array(vertices_list, dtype=np.float32)
    print(len(vertices_list))
    print(vertices_vec.size)
    print(len(indices_list))
    print(size)
    if gen_textures:
        texcoords_vec = np.array(texcoords_list, dtype=np.float32)


    for x in range(0, cols - 1):
        for z in range(0, rows - 1):
            if ((50 - x) ** 2 + (50 - z) ** 2) ** (1 / 2) <= (rows - 1)/2 or gen_relief == True :
                offset = x * cols + z
                if z == 0:
                    indices_list.append(offset)
                    indices_list.append(offset + rows)
                    indices_list.append(offset + 1)
                    indices_list.append(offset + rows + 1)
                else:
                    indices_list.append(offset + 1)
                    indices_list.append(offset + rows + 1)
                    if z == rows - 2:
                        indices_list.append(primRestart)

    print(len(indices_list))
    indices_vec = np.array(indices_list, dtype=np.uint32)

    print (indices_vec.size)
    currFace = 1
    for i in range(0, indices_vec.size - 2):
        index0 = indices_vec[i]
        index1 = indices_vec[i + 1]
        index2 = indices_vec[i + 2]

        face = np.array([0, 0, 0], dtype=np.int32)
        if (index0 != primRestart) and (index1 != primRestart) and (index2 != primRestart):
            if currFace % 2 != 0:
                face[0] = indices_vec[i]
                face[1] = indices_vec[i + 1]
                face[2] = indices_vec[i + 2]
                currFace += 1
            else:
                face[0] = indices_vec[i]
                face[1] = indices_vec[i + 2]
                face[2] = indices_vec[i + 1]
                currFace += 1

            faces_list.append(face)

    faces = np.reshape(faces_list, newshape=(len(faces_list), 3))

    for i in range(0, faces.shape[0]):
        A = np.array([vertices_vec[faces[i, 0], 0], vertices_vec[faces[i, 0], 1], vertices_vec[faces[i, 0], 2]],
                     dtype=np.float32)
        B = np.array([vertices_vec[faces[i, 1], 0], vertices_vec[faces[i, 1], 1], vertices_vec[faces[i, 1], 2]],
                     dtype=np.float32)
        C = np.array([vertices_vec[faces[i, 2], 0], vertices_vec[faces[i, 2], 1], vertices_vec[faces[i, 2], 2]],
                     dtype=np.float32)

        edge1A = normalize(B - A)
        edge2A = normalize(C - A)

        face_normal = np.cross(edge1A, edge2A)

        normals_vec[faces[i, 0]] += face_normal
        normals_vec[faces[i, 1]] += face_normal
        normals_vec[faces[i, 2]] += face_normal

    for i in range(0, normals_vec.shape[0]):
        normals_vec[i] = normalize(normals_vec[i])

    vao = glGenVertexArrays(1)
    vbo_vertices = glGenBuffers(1)
    vbo_normals = glGenBuffers(1)
    if gen_textures:
        vbo_texcoords = glGenBuffers(1)
    vbo_indices = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo_vertices)
    glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(vertices_vec), vertices_vec.flatten(), GL_STATIC_DRAW)  #
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, vbo_normals)
    glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(normals_vec), normals_vec.flatten(), GL_STATIC_DRAW)  #
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, vbo_indices)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(indices_vec), indices_vec.flatten(),
                 GL_STATIC_DRAW)

    if gen_textures:
        glBindBuffer(GL_ARRAY_BUFFER, vbo_texcoords)
        glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(texcoords_vec), texcoords_vec.flatten(),
                     GL_STATIC_DRAW)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(2)



    glEnable(GL_PRIMITIVE_RESTART)
    glPrimitiveRestartIndex(primRestart)

    glBindVertexArray(0)
    if gen_relief:
        return (vao, indices_vec.size, vector_lines,vector_line_indexes)
    else:
        return (vao, indices_vec.size)