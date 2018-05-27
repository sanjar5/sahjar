#version 330 core
in vec3 vFragPosition;
in vec3 vNormal;

out vec4 color;

uniform vec3 col;

void main()
{
  vec3 lightDir = vec3(1.0f, 1.0f, 0.0f);

  float kd = max(dot(vNormal, lightDir), 0.0);

  color = vec4(kd * col, 1.0f);
}