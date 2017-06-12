import math

def light(matrix, index, ka, kd, ks, normal, setting, color):
    surface_normal = normal
    vector_normal = normalize(normal)

    for counter in xrange(3):

        AMBIENT = setting['ambient'][counter] * ka[index]
        color[i] += AMBIENT

        for light in setting['lights']:
            source = setting['lights'][light]['location']
            light = vector_subtraction(source, matrix[index])
            normalize_light = normalize(light)

            diffuse = source[counter] * kd[counter] * max(dot_product(vector_normal, normalize_light), 0)

            normalize_r = normalize(vector_subtraction(vector_normal,
                                                       dot_product(vector_normal, normalize_light) * 2),
                                    normalize_light)
            view = (0, 0, 10)
            normalize_view = vector_addition(matrix[index], view)

            specular = source[counter] * ks[counter] * max(dot_product(normalize_r, normalize_view), 0)

            color[counter] += diffuse + specular

        color = [int(min(max(color_component, 0), 255)) for color_component in color]
        return color

def vector_subtraction(vector1, vector2):
    return [vector1[index] - vector2[index] for index in xrange(3)]

def vector_addition(vector1, vector2):
    return [vector1[index] + vector2[index] for index in xrange(3)]

def scale(vector, scalar_factor):
    return [vector_component * scalar_factor for vector_component in vector]

def dot_product(vector1, vector2):
    return sum([vector1[index] * vector2[index] for index in xrange(3)])

def cross_product(vector1, vector2):
    return [vector1[1] * vector2[2] - vector1[2] * vector2[1],
            vector1[2] * vector2[0] - vector1[0] * vector2[2],
            vector1[0] * vector2[1] - vector1[1] * vector2[0]]

def magnitude(vector):
    return math.sqrt(sum(vector_component ** 2 for vector_component in vector))

def normalize(vector):
    vector_magnitude = magnitude(vector)
    return [vector_component/vector_magnitude for vector_component in vector]

def calculate_normal(polygons, i):

    A = [0, 0, 0]
    B = [0, 0, 0]
    N = [0, 0, 0]

    A[0] = polygons[i+1][0] - polygons[i][0]
    A[1] = polygons[i+1][1] - polygons[i][1]
    A[2] = polygons[i+1][2] - polygons[i][2]

    B[0] = polygons[i+2][0] - polygons[i][0]
    B[1] = polygons[i+2][1] - polygons[i][1]
    B[2] = polygons[i+2][2] - polygons[i][2]

    N[0] = A[1] * B[2] - A[2] * B[1]
    N[1] = A[2] * B[0] - A[0] * B[2]
    N[2] = A[0] * B[1] - A[1] * B[0]

    return N
