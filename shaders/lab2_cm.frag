#version 330 core
in vec3 vFragPosition;
in vec2 vTexCoords;
in vec3 vNormal;

out vec4 color;

uniform sampler2D tex;
uniform bool cm_switch;


vec4 cm1(float f)
{
    f = clamp( f, 0.0, 1.0 );
    return vec4(1.0, f, 1.0 - f, 1.0);
}



float cm2_red(float x) {
	const float pi = 3.141592653589793238462643383279502884197169399;
	const float a = 12.16378802377247;
	const float b = 0.05245257017955226;
	const float c = 0.2532139106569052;
	const float d = 0.02076964056039702;
	const float e = 270.124167081014;
	const float f = 1.724941960305955;
	float v = (a * x + b) * sin(2.0 * pi / c * (x - d)) + e * x + f;
	if (v > 255.0) {
		return 255.0 - (v - 255.0);
	} else {
		return v;
	}
}

float cm2_green(float x) {
	const float pi = 3.141592653589793238462643383279502884197169399;
	const float a = 88.08537391182792;
	const float b = 0.25280516046667;
	const float c = 0.05956080245692388;
	const float d = 106.5684078925541;
	return a * sin(2.0 * pi / b * (x - c)) + d;
}

float cm2_blue(float x) {
	const float pi = 3.141592653589793238462643383279502884197169399;
	const float a = 63.89922420106684;
	const float b = 0.4259605778503662;
	const float c = 0.2529247343450655;
	const float d = 0.5150868195804643;
	const float e = 938.1798072557968;
	const float f = 503.0883490697431;
	float v = (a * x + b) * sin(2.0 * pi / c * x + d * 2.0 * pi) - e * x + f;
	if (v > 255.0) {
		return 255.0 - (v - 255.0);
	} else {
		return mod(v, 255.0);
	}
}

vec4 cm2(float x) {
	float r = clamp(cm2_red(x) / 255.0, 0.0, 1.0);
	float g = clamp(cm2_green(x) / 255.0, 0.0, 1.0);
	float b = clamp(cm2_blue(x) / 255.0, 0.0, 1.0);
	return vec4(r, g, b, 1.0);
}



void main()
{
  vec3 lightDir = vec3(1.0f, 1.0f, 0.0f);

  vec3 sampled = texture(tex, vTexCoords).rgb;
  float grayscale = 0.299f*sampled.r + 0.587f*sampled.g + 0.114*sampled.b;

  vec4 col;

  if ( cm_switch )
    col = cm1( grayscale );
  else
    col = cm2( grayscale );

  float kd = max(dot(vNormal, lightDir), 0.0);

  color = kd * col;
}