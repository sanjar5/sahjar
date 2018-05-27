#version 330 core
in vec3 vFragPosition;
in vec3 vNormal;

out vec4 color;


void main()
{
  vec3 pos = vFragPosition;
  vec3 lightDir = vec3(1.0f, 1.0f, 0.0f);
  float f = pos.y/20.0;
  float s = 12*f;
  float r = max(0, (3 - f*abs(s-9)- f*abs(s-9))/2);
  float g = max(0, (8 - f*abs(s-5)- f*abs(s-5))/2);
  float b = max(0, (3 - f*abs(s-1)- f*abs(s-1))/2);
  vec3 col = vec3(1-r,1-g,1-b); //vec3(0.0f, 0.9f, 0.75f);

  float kd = max(dot(vNormal, lightDir), 0.0);

  color = vec4(kd * col, 1.0f);
}