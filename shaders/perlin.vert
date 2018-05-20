#version 330 core
layout(location = 0) in vec3 vertex;
layout(location = 1) in vec3 normal;

out vec3 vFragPosition;
out vec3 vNormal;
out float Noise;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform float time;


//just 256x2 pseudorandom integers in [0;255] range
int[512] p = int[](
    151,160,137,91,90,15,
    131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,
    190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
    88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
    77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
    102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
    135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
    5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
    223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
    129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
    251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
    49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
    138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180,
    151,160,137,91,90,15,
    131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,
    190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
    88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
    77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
    102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
    135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
    5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
    223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
    129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
    251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
    49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
    138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180);



vec3 fade(vec3 t)
{
    return pow(t,vec3(5))*6 - pow(t,vec3(4))*15 + pow(t,vec3(3))*10;
}

float linterp( float a, float b, float x ) // simple 1d linear interpolation
{
    return a + x * (b - a);
}


float dot_pr( int hash, float x, float y, float t ) //get dot product of (x,y) dist vector and pseudorandom grad vector
{
    //pick one of 12 grad vectors based on hash
    switch( hash & 0xF ) //last 4 bits
    {
       case 0x0: return x+y; // 1 1 0
       case 0x1: return -x+y; // -1 1 0
       case 0x2: return x-y; // 1 -1 0
       case 0x3: return -x-y; // -1 -1 0
       case 0x4: return x+t; // 1 0 1
       case 0x5: return -x+t; // -1 0 1
       case 0x6: return  x-t; // 1 0 -1
       case 0x7: return -x-t; // -1 0 -1
       case 0x8: return  y+t; // 0 1 1
       case 0x9: return -y+t; // 0 -1 1
       case 0xA: return  y-t; // 0 1 -1
       case 0xB: return -y-t; // 0 -1 -1
       case 0xC: return  y+x; // 1 1 0
       case 0xD: return -y+t; // 0 -1 1
       case 0xE: return  y-x; // -1 1 0
       case 0xF: return -y-t; // 0 -1 -1
       default: return 0.0;
    }
}



float perlin_noise_improved_2d( vec3 xyt )
{
    ivec3 floored = ivec3(floor(xyt));
    xyt -= vec3(floored); //scale coords in [0;1] local coordinates


    // surrounding unit square
    // lu -- ru
    // -     -
    // -     -
    // ld -- rd

    // hash square angles coords
    floored &= 0xFF; // use last byte: [0;255] to hash floored coords
    int xi = floored.x;
    int yi = floored.y;
    int ti = floored.z;


    // hash andle coords to [0;255]
    // 8 corners hashes
    int c1_hash = p[p[p[xi]+yi]+ti];
    int c2_hash = p[p[p[xi]+yi+1]+ti];
    int c3_hash = p[p[p[xi]+yi]+ti+1];
    int c4_hash = p[p[p[xi]+yi+1]+ti+1];
    int c5_hash = p[p[p[xi+1]+yi]+ti];
    int c6_hash = p[p[p[xi+1]+yi+1]+ti];
    int c7_hash = p[p[p[xi+1]+yi]+ti+1];
    int c8_hash = p[p[p[xi+1]+yi+1]+ti+1];

    vec3 faded = fade(xyt);

    //get dot pr. of picked grad and dist vector
    float x1 = linterp(dot_pr(c1_hash, xyt.x, xyt.y, xyt.z),
                      dot_pr(c5_hash, xyt.x-1, xyt.y, xyt.z), faded.x);


    float x2 = linterp(dot_pr(c2_hash, xyt.x, xyt.y-1, xyt.z),
                       dot_pr(c6_hash, xyt.x-1, xyt.y-1, xyt.z), faded.x);

    float y1 = linterp(x1,x2,faded.y);

    x1 = linterp(dot_pr(c3_hash, xyt.x, xyt.y, xyt.z-1),
                  dot_pr(c7_hash, xyt.x-1, xyt.y, xyt.z-1), faded.x);

    x2 = linterp(dot_pr(c4_hash, xyt.x, xyt.y-1, xyt.z-1),
                dot_pr(c8_hash, xyt.x-1, xyt.y-1, xyt.z-1), faded.x);

    float y2 = linterp(x1,x2,faded.y);


    float linterped_val = linterp(y1,y2,faded.z);

    return (linterped_val + 1) / 2.0; // [0;1] scale?
}


float multioctave_perlin_noise(vec3 xyt, int octaves, float persistance)
{
  float res = 0;
  float frequency = 1.0;
  float amplitude = 100.0;
  float max = 0;


  for(int i=0; i<octaves; ++i )
  {
     res += perlin_noise_improved_2d(xyt*frequency) * amplitude;
     max += amplitude;
     amplitude *= persistance;
     frequency *= 2;
  }

  return clamp(res/max, 0.0, 1.0);
}

void main()
{
    vec3 pos = vertex;
    vFragPosition = vec3(model * vec4(pos, 1.0f));

    vec3 noise_dimensions = vec3(vFragPosition.xz, time);

    float noise = multioctave_perlin_noise(noise_dimensions, 7, 0.5);

    float multiplier = 3.0;

    pos.y = multiplier * noise;

    gl_Position = projection * view * model * vec4(pos, 1.0f);


    vNormal = mat3(transpose(inverse(model))) * normal;
    Noise = pos.y;
}