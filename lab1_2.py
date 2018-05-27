import glfw
import math
from polygon import get_ply_elements
import numpy as np
from PIL import Image
import OpenEXR, Imath
from OpenGL.GL import *
from OpenGL.arrays import ArrayDatatype
from OpenGL.GLUT import *
from shader_program import ShaderProgram
from _camera import Camera
from light_math import *
from create_field import create_field

Width = 1024
Height = 1024
lastX = float(Width) / 2.0
lastY = float(Height) / 2.0
filling = False
keys = np.zeros(1024)
firstMouse = True
captureMouse = True
capturedMouseJustNow = False
camera = Camera(a_pos=np.array([0.0, 50.0, 50.0], dtype=np.float32))

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


def get_texture(filename):
    image_data = 0
    is_hdr = False
    size = ()

    if OpenEXR.isOpenExrFile(filename):
        is_hdr = True
        img = OpenEXR.InputFile(filename)
        FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)
        (r, g, b) = (img.channel(chan, FLOAT) for chan in ('R', 'G', 'B'))
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

    texture_id = glGenTextures(1)
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


# definition of control function

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


###############################################################


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


def normals_for_triangles(indices_vec, vertices_vec, size):
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


def uv_sphere(mers, pars):
    vertices_list = []
    vertices_list.append([0.0, 1.0, 0.0])
    tri_ind = []

    for i in range(pars):
        polar = math.pi * (i + 1) / pars
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
        a = i + 1
        b = (i + 1) % mers + 1
        tri_ind.append(0)
        tri_ind.append(b)
        tri_ind.append(a)

    for j in range(pars - 2):
        aStart = j * mers + 1
        bStart = (j + 1) * mers + 1
        for i in range(mers):
            a = aStart + i
            a1 = aStart + (i + 1) % mers
            b = bStart + i
            b1 = bStart + (i + 1) % mers

            tri_ind.append(a)
            tri_ind.append(a1)
            tri_ind.append(b1)
            tri_ind.append(a)
            tri_ind.append(b1)
            tri_ind.append(b)

    for i in range(mers):
        a = i + mers * (pars - 2) + 1
        b = (i + 1) % mers + mers * (pars - 2) + 1
        tri_ind.append(len(vertices_list) - 1)
        tri_ind.append(a)
        tri_ind.append(b)

    vertices_vec = np.array(vertices_list, dtype=np.float32)
    indices_vec = np.array(tri_ind, dtype=np.uint32)

    normals_vec = normals_for_triangles(indices_vec, vertices_vec, indices_vec.size // 3)

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
        cos2ps = float(math.cos(2.0 * math.pi * s))
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
    prefix = 'imageData/00'

    cm_texture_num = 0

    cm_textures = []

    while cm_texture_num < hdr_textures_amount:

        cur_texture_name = prefix

        if cm_texture_num < 10:
            cur_texture_name += '0'

        cur_texture_name += str(cm_texture_num) + '.exr'

        cur_cm_texture = get_texture(cur_texture_name)

        cm_textures.append(cur_cm_texture)
        cm_texture_num += 1

    return cm_textures


def main():
    global Width
    global Height
    global camera

    Width = 1000
    Height = 1000

    last_frame = 0.0

    glfw.init()  # initialize glfw

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)  # initialize window
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.RESIZABLE, GL_FALSE)

    window = glfw.create_window(1000, 1000, "ACG2018", None, None)  # window params

    glfw.set_key_callback(window, key_callback)  # bind  key callback function
    glfw.set_cursor_pos_callback(window, mousemove_callback)  # bind  cursor callback function
    glfw.set_mouse_button_callback(window, mouseclick_callback)  # bind  mouse callback function

    glfw.make_context_current(window)  # bind  context

    size_of_field = 25
    projection = projectionMatrixTransposed(60.0, float(Width) / float(Height), 1, 1000.0)

    (fun_vao1, ind_fun1) = create_field(100, 100, size_of_field, lambda x, z: x * z, False)
    (fun_vao2, ind_fun2) = create_field(100, 100, size_of_field, lambda x, z: math.exp(-x * x - z * z), False)
    (fun_vao3, ind_fun3) = create_field(100, 100, size_of_field, lambda x, z: (x + z) / (x * z), False)

    (plot_vao, ind_con, vec_lines, isoline_v) = create_field(100, 100, size_of_field, 0, False, True)
    (hm_vao, ind_hm) = create_field(100, 100, size_of_field, lambda x, z: 0.0, True)
    (rotation_vao, rotation_ind) = uv_sphere(22, 11)
    (cm_vao, ind_cm) = create_field(100, 100, size_of_field, lambda x, z: 0.0, True)
    (ply_vao, ply_count) = get_ply_elements()
    (perlin_vao, ind_perlin) = create_field(100, 100, size_of_field, lambda x, z: 0.0, False)


    fun_shader_sources = [(GL_VERTEX_SHADER, "shaders/lab1_fun.vert"), (GL_FRAGMENT_SHADER, "shaders/lab1_fun.frag")]
    fun_program = ShaderProgram(fun_shader_sources)

    hm_shader_sources = [(GL_VERTEX_SHADER, "shaders/lab1_hm.vert"), (GL_FRAGMENT_SHADER, "shaders/lab1_hm.frag")]
    hm_program = ShaderProgram(hm_shader_sources)
    hm_texture = get_texture("royal_garden.jpg")

    plot_shader_sources = [(GL_VERTEX_SHADER, "shaders/plot.vert"), (GL_FRAGMENT_SHADER, "shaders/plot.frag")]
    plot_program = ShaderProgram(plot_shader_sources)

    rotation_sources = [(GL_VERTEX_SHADER, "shaders/lab1_rotate.vert"), (GL_FRAGMENT_SHADER, "shaders/lab1_rotate.frag")]
    rotation_program = ShaderProgram(rotation_sources)

    cm_shader_sources = [(GL_VERTEX_SHADER, "shaders/lab2_cm.vert"), (GL_FRAGMENT_SHADER, "shaders/lab2_cm.frag")]
    colormap = ShaderProgram(cm_shader_sources)

    perlin_shader_sources = [(GL_VERTEX_SHADER, "shaders/lab2_perlin.vert"), (GL_FRAGMENT_SHADER, "shaders/lab2_perlin.frag")]
    perlin_program = ShaderProgram(perlin_shader_sources)

    ply_shader_sources = [(GL_VERTEX_SHADER, "shaders/lab2_ply.vert"), (GL_FRAGMENT_SHADER, "shaders/lab2_ply.frag")]
    ply_program = ShaderProgram(ply_shader_sources)


    HDR_TEXTURES_AMOUNT = 33

    cm_textures = read_cm_textures(HDR_TEXTURES_AMOUNT)

    cm_texture_num = 0

    colormap_change_counter = 0

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
        view = camera.get_view_matrix()

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glViewport(0, 0, Width, Height)
        glEnable(GL_DEPTH_TEST)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

###########################################################################################

        fun_program.bindProgram()
        glUniformMatrix4fv(fun_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())  # projection

        model = translateM4x4(np.array([0.0, 0.0, 0.0]))  # surface 1
        glUniform3fv(fun_program.uniformLocation("col"), 1, [0.0, 1.0, 1.0])
        glUniformMatrix4fv(fun_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniformMatrix4fv(fun_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glBindVertexArray(fun_vao1)
        glDrawElements(GL_TRIANGLE_STRIP, ind_fun1, GL_UNSIGNED_INT, None)

        model = translateM4x4(np.array([0.0, -1.0 * size_of_field, 0.0]))  # surface 2
        glUniform3fv(fun_program.uniformLocation("col"), 1, [1.0, 1.0, 0.0])
        glUniformMatrix4fv(fun_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glBindVertexArray(fun_vao2)
        glDrawElements(GL_TRIANGLE_STRIP, ind_fun2, GL_UNSIGNED_INT, None)

        model = translateM4x4(np.array([0.0, +1.6 * size_of_field, 0.0]))  # surface 3
        glUniform3fv(fun_program.uniformLocation("col"), 1, [1.0, 0.0, 1.0])
        glUniformMatrix4fv(fun_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glBindVertexArray(fun_vao3)
        glDrawElements(GL_TRIANGLE_STRIP, ind_fun3, GL_UNSIGNED_INT, None)

###########################################################################################

        ply_program.bindProgram() #PLY
        model = translateM4x4(np.array([-1.5 * size_of_field, 0.0, 0.0]))
        glUniformMatrix4fv(ply_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniformMatrix4fv(ply_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glUniformMatrix4fv(ply_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())
        glBindVertexArray(ply_vao)
        glDrawArrays(GL_POINTS, 0, ply_count)

###########################################################################################

        rotation_program.bindProgram()   #result of rotation
        glUniformMatrix4fv(rotation_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())

        sph_scale = scaleM4x4(np.array([10, 10, 10])) #sphere radius
        sph_translate = translateM4x4(np.array([0.0, 0.0, 2.0 * size_of_field]))
        glUniformMatrix4fv(rotation_program.uniformLocation("model"), 1, GL_FALSE,
                           np.transpose(sph_translate + sph_scale).flatten())
        glUniform3fv(rotation_program.uniformLocation("col"), 1, [1.0, 0.0, 1.0])
        glUniformMatrix4fv(rotation_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glBindVertexArray(rotation_vao)
        glDrawElements(GL_TRIANGLES, rotation_ind, GL_UNSIGNED_INT, None)

###########################################################################################

        plot_program.bindProgram()  #plot_program

        model = translateM4x4(np.array([0.0, 0.0, -3.0 * size_of_field]))

        glUniformMatrix4fv(plot_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniformMatrix4fv(plot_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glUniformMatrix4fv(plot_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())
        glBindVertexArray(plot_vao)
        glDrawElements(GL_TRIANGLE_STRIP, ind_con, GL_UNSIGNED_INT, None)

        fun_program.bindProgram()   #isolines
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
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, ArrayDatatype.arrayByteCount(isoline_v),
                  isoline_v.flatten(),
                  GL_STATIC_DRAW)

        glUniformMatrix4fv(fun_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniformMatrix4fv(fun_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glUniformMatrix4fv(fun_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())
        glBindVertexArray(lines_vao)
        glDrawElements(GL_LINES, isoline_v.size, GL_UNSIGNED_INT, None)

###########################################################################################

        hm_program.bindProgram() #altitude map
        model = translateM4x4(np.array([0.0, 0.0, -1.5 * size_of_field]))
        bindTexture(0, hm_texture)
        glUniform1i(hm_program.uniformLocation("tex"), 0)
        glUniformMatrix4fv(hm_program.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniformMatrix4fv(hm_program.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glUniformMatrix4fv(hm_program.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())
        glBindVertexArray(hm_vao)
        glDrawElements(GL_TRIANGLE_STRIP, ind_hm, GL_UNSIGNED_INT, None)

###########################################################################################

        colormap.bindProgram()

        model = translateM4x4(np.array([1.5 * size_of_field, 0.0, -1.5 * size_of_field]))
        cur_colormap_texture = cm_textures[cm_texture_num % HDR_TEXTURES_AMOUNT]
        bindTexture(1, cur_colormap_texture)

        if colormap_change_counter % hdr_textures_speed == 0:
         cm_texture_num += 1

        colormap_change_counter += 1

        glUniform1i(colormap.uniformLocation("cm_switch"), False)

        glUniform1i(colormap.uniformLocation("tex"), 1)
        glUniformMatrix4fv(colormap.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniformMatrix4fv(colormap.uniformLocation("view"), 1, GL_FALSE, np.transpose(view).flatten())
        glUniformMatrix4fv(colormap.uniformLocation("projection"), 1, GL_FALSE, projection.flatten())
        glBindVertexArray(cm_vao)
        glDrawElements(GL_TRIANGLE_STRIP, ind_cm, GL_UNSIGNED_INT, None)

        # HDR
        model = translateM4x4(np.array([2.5 * size_of_field, 0.0, -2.5 * size_of_field]))
        glUniformMatrix4fv(colormap.uniformLocation("model"), 1, GL_FALSE, np.transpose(model).flatten())
        glUniform1i(colormap.uniformLocation("cm_switch"), True)
        glDrawElements(GL_TRIANGLE_STRIP, ind_cm, GL_UNSIGNED_INT, None)

###########################################################################################

        perlin_program.bindProgram()
        model = translateM4x4(np.array([0.0, 0.0, 4.5 * size_of_field]))
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
