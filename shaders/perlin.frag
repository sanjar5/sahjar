#version 330 core
in vec3 vFragPosition;
in vec3 vNormal;
in float Noise;

out vec4 color;


void main()
{
  vec3 lightDir = vec3(1.0f, 1.0f, 0.0f);

  vec3 col_native = vec3(0.0,0.5,1.0); //vec3(0.0f, 0.9f, 0.75f);
  vec3 noise_gs = vec3(Noise);
  vec3 col = mix(col_native, noise_gs, 0.2);

  float kd = max(dot(vNormal, lightDir), 0.0);

  color = vec4(kd * col, 1.0f);
}