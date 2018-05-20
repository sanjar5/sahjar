import glfw
import math
from CloudPly import read_ply
import numpy as np
from PIL import Image
import OpenEXR, Imath
from OpenGL.GL import (GL_ARRAY_BUFFER, GL_COLOR_BUFFER_BIT,GL_POINTS,
                       GL_FALSE, GL_FLOAT, GL_FRAGMENT_SHADER, GL_RENDERER, GL_SHADING_LANGUAGE_VERSION,
                       GL_UNSIGNED_INT, GL_RGBA, GL_RGBA32F, GL_RGB32F,
                       GL_STATIC_DRAW, GL_TRIANGLES, GL_TRUE, GL_VENDOR, GL_VERSION, GL_ELEMENT_ARRAY_BUFFER,
                       GL_TEXTURE_BASE_LEVEL, GL_VERTEX_SHADER,
                       GL_DEPTH_TEST, GL_DEPTH_BUFFER_BIT, GL_FRONT_AND_BACK, GL_FILL, GL_LINES, GL_UNPACK_ALIGNMENT,
                       GL_TEXTURE_MAX_LEVEL, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR_MIPMAP_LINEAR,
                       GL_LINEAR, GL_REPEAT, GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T,
                       GL_NO_ERROR, GL_INVALID_ENUM, GL_INVALID_VALUE, GL_INVALID_OPERATION, GL_STACK_OVERFLOW,
                       GL_TEXTURE_2D, GL_TEXTURE0, GL_TEXTURE1,GL_LINE,
                       GL_STACK_UNDERFLOW, GL_OUT_OF_MEMORY, GL_TABLE_TOO_LARGE, GL_PRIMITIVE_RESTART,
                       GL_TRIANGLE_STRIP, GL_TRIANGLE_FAN, GL_RGB, GL_UNSIGNED_BYTE,
                       glAttachShader, glBindBuffer, glBindVertexArray, glDrawElements,
                       glBufferData, glClear, glClearColor, glDrawArrays, glEnableVertexAttribArray,
                       glGenBuffers, glGenVertexArrays, glGetAttribLocation, glDeleteVertexArrays,
                       glGetString, glGetUniformLocation, glUseProgram, glDeleteBuffers,
                       glVertexAttribPointer, glViewport, glPolygonMode, glUniformMatrix4fv,glUniform3fv, glBindTexture,
                       glTexImage2D,
                       glEnable, glGetError, glPrimitiveRestartIndex, glDisable, glGenTextures, glPixelStorei,
                       glTexParameteri, glActiveTexture, glUniform1i, glUniform1f,
                       glTexParameteri, glActiveTexture, glUniform1i, glBegin, glEnd, glVertex3f,glColor3f,glLineWidth,
                       glFlush)
from OpenGL.arrays import ArrayDatatype
from math import sin, sqrt, cos

from shader_program import ShaderProgram
from camera import Camera
from light_math import (projectionMatrixTransposed, identityM4x4, translateM4x4, scaleM4x4,
                        rotateXM4x4, rotateYM4x4, rotateZM4x4, projectionMatrix, normalize)
from create_surface_module import create_surface

width = 1024
height = 1024
lastX = float(width) / 2.0
lastY = float(height) / 2.0
filling = False
keys = np.zeros(1024)
firstMouse = True
captureMouse = True;
capturedMouseJustNow = False
camera = Camera(a_pos=np.array([0.0, 50.0, 50.0], dtype=np.float32))
# dsadsad
from inspect import getframeinfo, stack

def bind_buffer(vbo_vertices, vertices_vec, vbo_normals, normals_vec, vbo_indices, indices_vec):
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
    pass



def check_gl_errors():
    caller = getframeinfo(stack()[1][0])
    gl_error = glGetError()

    if (gl_error == GL_NO_ERROR):
        return

    if (gl_error == GL_INVALID_ENUM):
        print("%s:%d - GL_INVALID_ENUM" % (caller.filename, caller.lineno))

    if (gl_error == GL_INVALID_VALUE):
        print("%s:%d - GL_INVALID_VALUE" % (caller.filename, caller.lineno))

    if (gl_error == GL_INVALID_OPERATION):
        print("%s:%d - GL_INVALID_OPERATION" % (caller.filename, caller.lineno))

    if (gl_error == GL_STACK_OVERFLOW):
        print("%s:%d - GL_STACK_OVERFLOW" % (caller.filename, caller.lineno))

    if (gl_error == GL_STACK_UNDERFLOW):
        print("%s:%d - GL_STACK_UNDERFLOW" % (caller.filename, caller.lineno))

    if (gl_error == GL_OUT_OF_MEMORY):
        print("%s:%d - GL_OUT_OF_MEMORY" % (caller.filename, caller.lineno))

    if (gl_error == GL_TABLE_TOO_LARGE):
        print("%s:%d - GL_TABLE_TOO_LARGE" % (caller.filename, caller.lineno))


def read_texture(filename):
    image_data = 0
    is_hdr = False
    size = ()

    if OpenEXR.isOpenExrFile(filename):
        is_hdr = True
        img = OpenEXR.InputFile(filename)
        FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
        (r, g, b) = ( img.channel(chan, FLOAT) for chan in ('R', 'G', 'B'))
        dw = img.header()['dataWindow']
        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

        r_data = np.fromstring(r, dtype=np.float32)
        g_data = np.fromstring(g, dtype=np.float32)
        b_data = np.fromstring(b, dtype=np.float32)

        image_data = np.dstack((r_data, g_data, b_data))
        img.close()

    else:
        try:
            image = Image.open(filename)
        except IOError as ex:
            print('IOError: failed to open texture file %s' % filename)
            return -1
        print('opened file: size=', image.size, 'format=', image.format)
        image_data = np.array(list(image.getdata()), np.uint8)
        size = image.size
        image.close()


    texture_id= glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    if is_hdr:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB32F, size[0], size[1], 0, GL_RGB, GL_FLOAT, image_data)
    else:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, size[0], size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

    return texture_id


def bindTexture(unit, textureID):
    glActiveTexture(GL_TEXTURE0 + unit)
    glBindTexture(GL_TEXTURE_2D, textureID)


def key_callback(window, key, scancode, action, mods):
    global keys
    global filling

    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, 1)
    if key == glfw.KEY_SPACE and action == glfw.PRESS:

        if (filling):
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            filling = False
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            filling = True
    else:
        if action == glfw.PRESS:
            keys[key] = 1
        elif action == glfw.RELEASE:
            keys[key] = 0


def mouseclick_callback(window, button, action, mods):
    global captureMouse
    global capturedMouseJustNow

    if button == glfw.MOUSE_BUTTON_RIGHT and action == glfw.RELEASE:
        captureMouse = not captureMouse

    if captureMouse:
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        capturedMouseJustNow = True
    else:
        glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_NORMAL)


def mousemove_callback(window, xpos, ypos):
    global firstMouse
    global lastX
    global lastY
    global camera

    if firstMouse:
        lastX = float(xpos)
        lastY = float(ypos)
        firstMouse = False

    xoffset = float(xpos) - lastX
    yoffset = lastY - float(ypos)

    lastX = float(xpos)
    lastY = float(ypos)

    if captureMouse:
        camera.process_mouse(xoffset, yoffset, True)


sphere_radius = 10.0

def doCameraMovement(camera=Camera(), delta_time=0.0):

    global sphere_radius

    if (keys[glfw.KEY_W] == 1):
        camera.process_keyboard("forward", delta_time)
    if (keys[glfw.KEY_A] == 1):
        camera.process_keyboard("left", delta_time)
    if (keys[glfw.KEY_S] == 1):
        camera.process_keyboard("backward", delta_time)
    if (keys[glfw.KEY_D] == 1):
        camera.process_keyboard("right", delta_time)
    if (keys[glfw.KEY_Q] == 1):
        sphere_radius += 0.5
    if (keys[glfw.KEY_E] == 1):
        sphere_radius -= 0.5


def normals_for_triangles(indices_vec, vertices_vec, size ):
    currFace = 1
    faces_list = []
    normals_vec = np.zeros((size, 3), dtype=np.float32)

    for i in range(0, indices_vec.size - 2, 3):
        index0 = indices_vec[i]
        index1 = indices_vec[i + 1]
        index2 = indices_vec[i + 2]

        face = np.array([0, 0, 0], dtype=np.int32)
        # if (index0 != primRestart) and (index1 != primRestart) and (index2 != primRestart):

        face[0] = index0
        face[1] = index1
        face[2] = index2

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

    return normals_vec




def uv_sphere( mers, pars ):
    vertices_list = []
    vertices_list.append([0.0, 1.0, 0.0])
    tri_ind = []

    for i in range(pars):
        polar = math.pi * (i+1) / pars
        sp = math.sin(polar)
        cp = math.cos(polar)
        for j in range(mers):
            azimuth = 2.0 * math.pi * j / mers
            sa = math.sin(azimuth)
            ca = math.cos(azimuth)
            x = sp * ca
            y = cp
            z = sp * sa
            vertices_list.append([x, y, z])

    vertices_list.append([0.0, -1.0, 0.0])

    for i in range(mers):
        a = i+1
        b = (i+1) % mers + 1
        tri_ind.append( 0 )
        tri_ind.append( b )
        tri_ind.append( a )


    for j in range(pars-2):
        aStart = j * mers + 1
        bStart = (j + 1) * mers + 1
        for i in range(mers):
            a = aStart + i
            a1 = aStart + (i+1) % mers
            b = bStart + i
            b1 = bStart + (i+1) % mers

            tri_ind.append(a)
            tri_ind.append(a1)
            tri_ind.append(b1)
            tri_ind.append(a)
            tri_ind.append(b1)
            tri_ind.append(b)


    for i in range(mers):
        a = i + mers * (pars-2) + 1
        b = (i+1) % mers + mers * (pars-2) + 1
        tri_ind.append( len(vertices_list) - 1 )
        tri_ind.append(a)
        tri_ind.append(b)



    vertices_vec = np.array(vertices_list, dtype=np.float32)
    indices_vec = np.array(tri_ind, dtype=np.uint32)

    normals_vec = normals_for_triangles(indices_vec, vertices_vec, indices_vec.size//3)


    vao = glGenVertexArrays(1)
    vbo_vertices = glGenBuffers(1)
    vbo_indices = glGenBuffers(1)
    vbo_normals = glGenBuffers(1)


    glBindVertexArray(vao)

    bind_buffer(vbo_vertices, vertices_vec, vbo_normals, normals_vec, vbo_indices, indices_vec)

    glBindVertexArray(0)

    return (vao, indices_vec.size)

def uv_torus(inner_radius, outer_radius, num_sides, num_faces):
    vertices_list = []
    tri_ind = []
    normal_list = []

    t = 0.0
    s = 0


    t_incr = 1.0 / float(num_faces)
    s_incr = 1.0 / float(num_sides)

    for side_count in range(0, num_sides + 1):
        s += s_incr
        cos2ps = float(math.cos(2.0 * math.pi * s ))
        sin2ps = float(math.sin(2.0 * math.pi * s))

        for face_count in range(0, num_faces + 1):
            t += t_incr
            cos2pt = float(math.cos(2.0 * math.pi * t))
            sin2pt = float(math.sin(2.0 * math.pi * t))

            x = (outer_radius + inner_radius * cos2pt) * cos2ps
            y = (outer_radius + inner_radius * cos2pt) * sin2ps
            z = inner_radius * sin2pt
            vertices_list.append([x, y, z])

            x_norm = cos2ps * cos2pt;
            y_norm = sin2ps * cos2pt;
            z_norm = sin2pt;
            normal_list.append([x_norm, y_norm, z_norm])


    for side_count in range(0, num_sides):
        for face_count in range(0, num_faces):
            v0 = ((side_count * (num_faces + 1)) + face_count);
            v1 = (((side_count + 1) * (num_faces + 1)) + face_count);
            v2 = (((side_count + 1) * (num_faces + 1)) + (face_count + 1));
            v3 = ((side_count * (num_faces + 1)) + (face_count + 1));


            tri_ind.append(v0)
            tri_ind.append(v1)
            tri_ind.append(v2)

            tri_ind.append(v0)
            tri_ind.append(v2)
            tri_ind.append(v3)






    vertices_vec = np.array(vertices_list, dtype=np.float32)
    indices_vec = np.array(tri_ind, dtype=np.uint32)
    normals_vec = np.array(normal_list, dtype=np.float32)

    vao = glGenVertexArrays(1)
    vbo_vertices = glGenBuffers(1)
    vbo_indices = glGenBuffers(1)
    vbo_normals = glGenBuffers(1)

    glBindVertexArray(vao)

    bind_buffer(vbo_vertices, vertices_vec, vbo_normals, normals_vec, vbo_indices, indices_vec)

    glBindVertexArray(0)

    return (vao, indices_vec.size)


def read_cm_textures(hdr_textures_amount):

    prefix = 'hdr_image_data/00'

    cm_texture_num = 0

    cm_textures = []

    while cm_texture_num < hdr_textures_amount:

        cur_texture_name = prefix

        if cm_texture_num < 10:
            cur_texture_name += '0'

        cur_texture_name += str(cm_texture_num) + '.exr'

        cur_cm_texture = read_texture(cur_texture_name)

        cm_textures.append(cur_cm_texture)
        cm_texture_num += 1

    return cm_textures


def main():
    global width
    global height
    global camera

    width = 1024
    height = 1024

    delta_time = 0.0
    last_frame = 0.0

    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.RESIZABLE, GL_FALSE)
    window = glfw.create_window(width, height, "opengl_lab1", None, None)

    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, mousemove_callback)
    glfw.set_mouse_button_callback(window, mouseclick_callback)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    fun1 = lambda x, z: math.sin(x+z)
    fun2 = lambda x, z: math.exp(-x*x - z*z)
    fun3 = lambda x, z: (x**2 + z**2) / (x*z)
    contour_plot = lambda x, z: 0.0
    heightmap_dummy_fun = lambda x, z: 0.0

    surface_size = 50

    (fun_vao1, ind_fun1) = create_surface(100, 100, surface_size, fun1, False)
    (fun_vao2, ind_fun2) = create_surface(100, 100, surface_size, fun2, False)
    (fun_vao3, ind_fun3) = create_surface(100, 100, surface_size, fun3, False)
    (contour_plot_vao, ind_con, vec_lines, vector_line_indexes) = create_surface(100, 100, surface_size, 0, False, True)
    (heightmap_vao, ind_hm) = create_surface(100,100, surface_size, heightmap_dummy_fun, True)
    (sphere_vao, sphere_ind) = uv_sphere(22, 11)
    (torus_vao, torus_ind) = uv_torus(5, 10, 100, 100)
    (cm_vao, ind_cm) = create_surface(100, 100, surface_size, heightmap_dummy_fun, True)
    (cloud_vao, points_count) = read_ply()
    (perlin_vao, ind_perlin) = create_surface(100, 100, surface_size, heightmap_dummy_fun, False)

    fun_shader_sources = [(GL_VERTEX_SHADER, "shaders/functions.vert"), (GL_FRAGMENT_SHADER, "shaders/functions.frag")]

    fun_program = ShaderProgram(fun_shader_sources)

    hm_shader_sources = [(GL_VERTEX_SHADER, "shaders/heightmap.vert"), (GL_FRAGMENT_SHADER, "shaders/heightmap.frag")]

    hm_program = ShaderProgram(hm_shader_sources)

    hm_texture = read_texture("1.jpg")

    contour_plot_shader_sources = [(GL_VERTEX_SHADER, "shaders/contourplot.vert"), (GL_FRAGMENT_SHADER, "shaders/contourplot.frag")]

    contour_plot_program = ShaderProgram(contour_plot_shader_sources)

    sphere_shader_sources = [(GL_VERTEX_SHADER, "shaders/sphere.vert"), (GL_FRAGMENT_SHADER, "shaders/sphere.frag")]
    sphere_program = ShaderProgram(sphere_shader_sources)

    cm_shader_sources = [(GL_VERTEX_SHADER, "shaders/colormap.vert"), (GL_FRAGMENT_SHADER, "shaders/colormap.frag")]
    cm_program = ShaderProgram( cm_shader_sources )

    perlin_shader_sources = [(GL_VERTEX_SHADER, "shaders/perlin.vert"), (GL_FRAGMENT_SHADER, "shaders/perlin.frag")]
    perlin_program = ShaderProgram(perlin_shader_sources)

    cloud_shader_sources = [(GL_VERTEX_SHADER, "shaders/ply.vert"), (GL_FRAGMENT_SHADER, "shaders/ply.frag")]
    cloud_program = ShaderProgram(cloud_shader_sources)

    check_gl_errors()

    projection = projectionMatrixTransposed(60.0, float(width) / float(height), 1, 1000.0)

    HDR_TEXTURES_AMOUNT = 33

    cm_textures = read_cm_textures(HDR_TEXTURES_AMOUNT)

    cm_texture_num = 0

    cm_change_counter = 0

    hdr_textures_speed = 6

    perlin_time = 0.0
    perlin_time_step = 0.03

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)



    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame
        glfw.poll_events()

        doCameraMovement(camera, delta_time)

        model = translateM4x4(np.array([0.0, 0.0, 0.0]))
        view = camera.get_view_matrix()

        glClearColor(0.5, 0.5, 0.5, 1.0)
        glViewport(0, 0, width, height)
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        fun_program.bindProgram()

        glUniform3fv(fun_program.uniformLocation("col"), 1 , [1.0, 0, 0] )

        glUniformMatrix4fv(fun_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniformMatrix4fv(fun_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glUniformMatrix4fv(fun_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())

        glBindVertexArray(fun_vao1)
        glDrawElements(GL_TRIANGLE_STRIP, ind_fun1, GL_UNSIGNED_INT, None)

        model = translateM4x4(np.array([-1.5*surface_size,0.0 ,0.0 ]))
        glUniform3fv(fun_program.uniformLocation("col"), 1, [0.0, 1.0, 0])
        glUniformMatrix4fv(fun_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glBindVertexArray(fun_vao2)
        glDrawElements(GL_TRIANGLE_STRIP, ind_fun2, GL_UNSIGNED_INT, None)

        model = translateM4x4(np.array([1.5 * surface_size, 0.0, 0.0]))
        glUniform3fv(fun_program.uniformLocation("col"), 1, [0.0, 0.0, 1.0])
        glUniformMatrix4fv(fun_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glBindVertexArray(fun_vao3)
        glDrawElements(GL_TRIANGLE_STRIP, ind_fun3, GL_UNSIGNED_INT, None)

        cloud_program.bindProgram()

        translate_cloud = translateM4x4(np.array([-2.5*surface_size,0.0 ,0.0 ]))
        # rotate_cloud = rotateYM4x4(math.radians(180))
        model = translate_cloud
        # glUniform3fv(fun_program.uniformLocation("col"), 1, [0.0, 1.0, 0])
        glUniformMatrix4fv(cloud_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniformMatrix4fv(cloud_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glUniformMatrix4fv(cloud_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())
        glBindVertexArray(cloud_vao)
        glDrawArrays(GL_POINTS, 0, points_count)

        sphere_program.bindProgram()

        sph_scale = scaleM4x4(np.array([sphere_radius, sphere_radius, sphere_radius]))
        sph_translate = translateM4x4(np.array([0.0, 0.0, 2.0 * surface_size]))

        glUniformMatrix4fv(sphere_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(sph_translate + sph_scale).flatten())
        glUniformMatrix4fv(sphere_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glUniformMatrix4fv(sphere_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())
        glBindVertexArray(sphere_vao)
        glDrawElements(GL_TRIANGLES, sphere_ind, GL_UNSIGNED_INT, None)

        torus_translate = translateM4x4(np.array([0.0, 0.0, 3.0 * surface_size]))
        glUniformMatrix4fv(sphere_program.uniformLocation("model"), 1, GL_FALSE,
                           np.transpose(torus_translate + sph_scale).flatten())
        glBindVertexArray(torus_vao)
        glDrawElements(GL_TRIANGLES, torus_ind, GL_UNSIGNED_INT, None)

        contour_plot_program.bindProgram()

        model = translateM4x4(np.array([-1.5 * surface_size, 0.0, -1.5 * surface_size]))

        glUniformMatrix4fv(contour_plot_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniformMatrix4fv(contour_plot_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glUniformMatrix4fv(contour_plot_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())
        glBindVertexArray(contour_plot_vao)
        glDrawElements(GL_TRIANGLE_STRIP, ind_con, GL_UNSIGNED_INT, None)

        fun_program.bindProgram()
        lines_vao = glGenVertexArrays(1)
        glBindVertexArray(lines_vao)
        vbo_lines = glGenBuffers(1)
        vbo_indices = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo_lines)
        glBufferData(GL_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(vec_lines), vec_lines.flatten(),
                     GL_STATIC_DRAW)  #
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, vbo_indices)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(vector_line_indexes), vector_line_indexes.flatten(),
                     GL_STATIC_DRAW)

        glUniformMatrix4fv(fun_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniformMatrix4fv(fun_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glUniformMatrix4fv(fun_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())
        glBindVertexArray(lines_vao)
        glDrawElements(GL_LINES, vector_line_indexes.size, GL_UNSIGNED_INT, None)

        hm_program.bindProgram()

        model = translateM4x4(np.array([0.0, 0.0, -1.5 * surface_size]))

        bindTexture(0, hm_texture)

        glUniform1i(hm_program.uniformLocation("tex"), 0)
        glUniformMatrix4fv(hm_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniformMatrix4fv(hm_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glUniformMatrix4fv(hm_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())
        glBindVertexArray(heightmap_vao)
        glDrawElements(GL_TRIANGLE_STRIP, ind_hm, GL_UNSIGNED_INT, None)

        cm_program.bindProgram()

        model = translateM4x4(np.array([1.5 * surface_size, 0.0, -1.5 * surface_size]))

        cur_cm_texture = cm_textures[cm_texture_num % HDR_TEXTURES_AMOUNT]

        bindTexture(1, cur_cm_texture)

        if cm_change_counter % hdr_textures_speed == 0:
            cm_texture_num += 1

        cm_change_counter += 1

        glUniform1i(cm_program.uniformLocation("cm_switch"), False)

        glUniform1i(cm_program.uniformLocation("tex"), 1)
        glUniformMatrix4fv(cm_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniformMatrix4fv(cm_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glUniformMatrix4fv(cm_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())
        glBindVertexArray(cm_vao)
        glDrawElements(GL_TRIANGLE_STRIP, ind_cm, GL_UNSIGNED_INT, None)

        # draw second animated hdr on the same shader
        model = translateM4x4(np.array([2.5 * surface_size, 0.0, -2.5 * surface_size]))
        glUniformMatrix4fv(cm_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniform1i(cm_program.uniformLocation("cm_switch"), True)
        glDrawElements(GL_TRIANGLE_STRIP, ind_cm, GL_UNSIGNED_INT, None)

        perlin_program.bindProgram()
        model = translateM4x4(np.array([0.0, 0.0, -3.5 * surface_size]))
        glUniformMatrix4fv(perlin_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniformMatrix4fv(perlin_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glUniformMatrix4fv(perlin_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())
        glUniform1f(perlin_program.uniformLocation("time"), perlin_time)
        perlin_time += perlin_time_step

        glBindVertexArray(perlin_vao)
        glDrawElements(GL_TRIANGLE_STRIP, ind_perlin, GL_UNSIGNED_INT, None)

        perlin_program.unbindProgram()

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
