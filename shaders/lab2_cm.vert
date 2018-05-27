#version 330 core
layout(location = 0) in vec3 vertex;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec2 texCoords;


out vec2 vTexCoords;
out vec3 vFragPosition;
out vec3 vNormal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform sampler2D tex;

void main()
{
//  vec3 sampled = texture(tex, texCoords).rgb;
//  float grayscale = 0.299f*sampled.r + 0.587f*sampled.g + 0.114*sampled.b;
//  pos.y += 5.0f* grayscale;
  gl_Position = projection * view * model * vec4(vertex, 1.0f);


  vTexCoords = texCoords;
  vFragPosition = vec3(model * vec4(vertex, 1.0f));
  vNormal = mat3(transpose(inverse(model))) * normal;
}