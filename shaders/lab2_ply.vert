#version 330 core
layout(location = 0) in vec3 vertex;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec3 color;


out vec3 vFragPosition;
out vec3 vNormal;
out vec3 col;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;


void main()
{
  vec3 pos = vertex;

  pos.y *= -1;
  gl_Position = projection * view * model * vec4(pos, 1.0f);
  vFragPosition = vec3(model * vec4(pos, 1.0f));
  vNormal = mat3(transpose(inverse(model))) * normal;
  col = color;
}