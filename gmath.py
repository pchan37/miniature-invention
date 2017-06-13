from operator import add

import math

e = 120
V = [0, 0, 1]

def get_normal(polygons, i):

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

def get_magnitude(vector):
    return math.sqrt(sum([vector[index] ** 2 for index in xrange(len(vector))]))

def scalar_mult(vector, scalar):
    return [vector_component * scalar for vector_component in vector]

def vector_subtraction(vector_1, vector_2):
    return [vector_1[index] - vector_2[index] for index in xrange(len(vector_1))]

def normalize(vector):
    magnitude = get_magnitude(vector)
    return [vector[index] / magnitude for index in xrange(3)]

def get_dot_product(vector_1, vector_2):
    normalized_vector_1 = normalize(vector_1)
    normalized_vector_2 = normalize(vector_2)
    dot_product = sum([normalized_vector_1[index] * normalized_vector_2[index] for index in xrange(3)])
    return max(dot_product, 0)

def get_ambient_intensity(L_c, K_a):
    return L_c * K_a

def get_diffuse_intensity(L_c, K_d, normal, location):
    dot_product = get_dot_product(normal, location)
    return L_c * K_d * dot_product

def get_specular_intensity(L_c, K_s, normal, location):
    N_L = get_dot_product(normal, location)
    scalar_product = scalar_mult(normal, 2 * N_L)
    vector_difference = vector_subtraction(scalar_product, location)
    dot_product = get_dot_product(vector_difference, V)
    return L_c * K_s * (dot_product ** e)

def get_intensity(ambient_intensity, diffuse_intensity, specular_intensity):
    total_intensity = ambient_intensity + diffuse_intensity + specular_intensity
    return min(int(round(total_intensity)), 255)

def get_light(normal, constants, light_source):
    location = light_source['location']

    ambient_light = [constants[color][0] for color in ('red', 'green', 'blue')]
    diffuse_light = [constants[color][1] for color in ('red', 'green', 'blue')]
    specular_light = [constants[color][2] for color in ('red', 'green', 'blue')]

    ambient_light_intensity = map(get_ambient_intensity, light_source['color'], ambient_light)
    diffuse_light_intensity = map(get_diffuse_intensity, light_source['color'], diffuse_light,
                                                         [normal] * 3, [location] * 3)
    specular_light_intensity = map(get_specular_intensity, light_source['color'], specular_light,
                                                           [normal] * 3, [location] * 3)

    red_light = get_intensity(ambient_light_intensity[0], diffuse_light_intensity[0], specular_light_intensity[0])
    green_light = get_intensity(ambient_light_intensity[1], diffuse_light_intensity[1], specular_light_intensity[1])
    blue_light = get_intensity(ambient_light_intensity[2], diffuse_light_intensity[2], specular_light_intensity[2])

    return [red_light, green_light, blue_light]

def get_total_light(normal, constants, list_of_light_sources):
    color = [0, 0, 0]

    for light_source in list_of_light_sources:
        light = get_light(normal, constants, light_source)
        color = map(add, color, light)
    return map(min, color, [255, 255, 255])

def get_avg_normal(list_of_normals):
    normals_sum = [0.0, 0.0, 0.0]

    for normal in list_of_normals:
        normals_sum = map(add, normals_sum, normal)

    length = len(list_of_normals)
    return [normals_sum[index] / length for index in xrange(len(normals_sum))]

def normalize_vectors(matrix):
    normalized_vectors_dict = {}

    point = 0
    while point < len(matrix) - 2:
        normal = get_normal(matrix, point)[:]

        list_of_matrix_points = [matrix[point], matrix[point + 1], matrix[point + 2]]
        for matrix_points in list_of_matrix_points:
            matrix_points_as_ints = (int(matrix_points[0]), int(matrix_points[1]), matrix_points[2])
            if matrix_points_as_ints in normalized_vectors_dict:
                normalized_vectors_dict[matrix_points_as_ints].append(normal)
            else:
                normalized_vectors_dict[matrix_points_as_ints] = [normal]
        point += 3

    for key, value in normalized_vectors_dict.items():
        normalized_vectors_dict[key] = get_avg_normal(value)
    return normalized_vectors_dict
