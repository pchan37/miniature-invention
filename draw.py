from display import *
from matrix import *
from math import *
from gmath import *

import random

def scanline_convert(polygons, index, screen, zbuffer, color, shading_type, intensities, constants, light_sources):

    unsorted_vertices = [polygons[index], polygons[index + 1], polygons[index + 2]]
    sorted_vertices = sorted(unsorted_vertices, key=lambda x: (x[1], x[0]),
                             reverse=True)

    TOP_INDEX = 0
    MID_INDEX = 1
    BOT_INDEX = 2
    TOP_X, TOP_Y, TOP_Z = [int(sorted_vertices[TOP_INDEX][index]) for index in xrange(3)]
    MID_X, MID_Y, MID_Z = [int(sorted_vertices[MID_INDEX][index]) for index in xrange(3)]
    BOT_X, BOT_Y, BOT_Z = [int(sorted_vertices[BOT_INDEX][index]) for index in xrange(3)]

    Y0 = BOT_Y
    Y1 = TOP_Y
    X0 = X1 = BOT_X
    Z0 = Z1 = BOT_Z

    X0_coordinates = scanline_helper(X0, Y0, Z0, TOP_X, TOP_Y, TOP_Z)
    if X0 > TOP_X:
        X0_coordinates.reverse()
    X1_coordinates = scanline_helper(X0, Y0, Z0, MID_X, MID_Y, MID_Z)
    if X0 > MID_X:
        X1_coordinates.reverse()

    intensity_0 = intensity_1 = 0
    if shading_type == 'goroud':
        TOP_INDEX = unsorted_vertices.index(sorted_vertices[0])
        MID_INDEX = unsorted_vertices.index(sorted_vertices[1])
        BOT_INDEX = unsorted_vertices.index(sorted_vertices[2])
        TOP_INTENSITY = intensities[TOP_INDEX]
        MID_INTENSITY = intensities[MID_INDEX]
        BOT_INTENSITY = intensities[BOT_INDEX] # i_2

        I_A = BOT_INTENSITY[:]
        I_B = BOT_INTENSITY[:]
        Y3, Y2 = MID_Y, BOT_Y

        swap = bool(MID_X <= TOP_X and MID_X <= BOT_X)
        if MID_X != X0 and TOP_X != X0:
            swap = bool(MID_X <= TOP_X and MID_X >= BOT_X and float(Y1 - Y0) / (TOP_X - X0)) or swap
            swap = bool(BOT_X >= TOP_X and MID_X <= BOT_X and float(Y1 - Y0) / (X0 - TOP_X)) or swap

    elif shading_type == 'phong':
        N_Bpt = intensities[b]
        N_Mpt = intensities[m]
        N_Tpt = intensities[t]

        if Y1 - Y0 != 0:
            d_N_0 = [float(N_Tpt[0] - N_Bpt[0]) / (Y1 - Y0), float(N_Tpt[1] - N_Bpt[1]) / (Y1 - Y0), float(N_Tpt[2] - N_Bpt[2]) / (Y1 - Y0)]
            if int(Mpt[1])- Y0 != 0:
                d_N_1 = [float(N_Mpt[0] - N_Bpt[0])/(MID_Y - Y0), float(N_Mpt[1] - N_Bpt[1])/(MID_Y - Y0), float(N_Mpt[2] - N_Bpt[2]) / (MID_Y - Y0)]

        N_a = N_Bpt[:]
        N_b = N_Bpt[:]

        swap = bool(MID_X <= TOP_X and MID_X <= BOT_X)
        if MID_X != X0 and TOP_X != X0:
            swap = bool(MID_X <= TOP_X and MID_X >= BOT_X and float(Y1 - Y0) / (TOP_X - X0) <= float(MID_Y - Y0) / (MID_X - X0)) or swap
            swap = bool(BOT_X >= TOP_X and MID_X <= BOT_X and float(Y1 - Y0) / (X0 - TOP_X) >= float(MID_Y - Y0) / (X0 - MID_X)) or swap

    while Y0 < Y1:
        if Y0 == MID_Y:
            X1 = MID_X
            Z1 = MID_Z
            X1_coordinates = scanline_helper(X1, Y0, Z1, TOP_X, Y1, TOP_Z)
            if X1 > TOP_X:
                X1_coordinates.reverse()
            intensity_1 = 0
            if shading_type == 'goroud' and MID_Y != Y1:
                I_B = intensities[MID_INDEX][:]
                BOT_INTENSITY = intensities[MID_INDEX]
                MID_INTENSITY = intensities[TOP_INDEX]
                Y3, Y2 = Y1, MID_Y
            elif shading_type == 'phong' and MID_Y != Y1:
                d_N_1 = [float(N_Tpt[0] - N_Mpt[0]) / (Y1 - MID_Y), float(N_Tpt[1] - N_Mpt[1]) / (Y1 - MID_Y), float(N_Tpt[2] - N_Mpt[2]) / (Y1 - MID_Y)]
                N_b = N_Mpt[:]

        if shading_type == 'goroud':
            if swap:
                draw_line(X0, Y0, Z0, X1, Y0, Z1, screen, zbuffer, color, I_B, I_A, shading_type)
            else:
                draw_line(X0, Y0, Z0, X1, Y0, Z1, screen, zbuffer, color, I_A, I_B, shading_type)
        elif shading_type == "phong":
            if swap:
                draw_line(X0, Y0, Z0, X1, Y0, Z1, screen, zbuffer, color, N_b, N_a, shading_type, constants, light_sources)
            else:
                draw_line(X0, Y0, Z0, X1, Y0, Z1, screen, zbuffer, color, N_a, N_b, shading_type, constants, light_sources)
        else:
            draw_line(X0, Y0, Z0, X1, Y0, Z1, screen, zbuffer, color)

        Y0 += 1
        intensity_0 += 1
        intensity_1 += 1
        X0 = X0_coordinates[intensity_0][0]
        Z0 = X0_coordinates[intensity_0][1]
        X1 = X1_coordinates[intensity_1][0]
        Z1 = X1_coordinates[intensity_1][1]

        if shading_type == "goroud":
            for j in range(len(color)):
                I_A[j] = int(round(float(Y0 - BOT_Y) / (Y1 - BOT_Y) * TOP_INTENSITY[j] + float(Y1 - Y0) / (Y1 - BOT_Y) * BOT_INTENSITY[j]))
                I_B[j] = int(round(float(Y0 - Y2) / (Y3 - Y2) * MID_INTENSITY[j] + float(Y3 - Y0) / (Y3 - Y2) * BOT_INTENSITY[j]))

        elif shading_type == "phong":
            for j in range(len(color)):
                N_a[j] += d_N_0[j]
                N_b[j] += d_N_1[j]

    if shading_type == 'goroud':
        if swap:
            draw_line(X0, Y0, Z0, X1, Y0, Z1, screen, zbuffer, color, I_B, TOP_INTENSITY, shading_type)
        else:
            draw_line(X0, Y0, Z0, X1, Y0, Z1, screen, zbuffer, color, TOP_INTENSITY, I_B, shading_type)
    elif shading_type == 'phong':
        if swap:
            draw_line(X0, Y0, Z0, X1, Y0, Z1, screen, zbuffer, color, N_b, N_Tpt, shading_type, constants, light_sources)
        else:
            draw_line(X0, Y0, Z0, X1, Y0, Z1, screen, zbuffer, color, N_Tpt, N_b, shading_type, constants, light_sources)
    else:
        draw_line(X0, Y0, Z0, X1, Y0, Z1, screen, zbuffer, color)

def add_polygon( polygons, x0, y0, z0, x1, y1, z1, x2, y2, z2 ):
    add_point(polygons, x0, y0, z0);
    add_point(polygons, x1, y1, z1);
    add_point(polygons, x2, y2, z2);

def draw_polygons( matrix, screen, zbuffer, color, constants = [], light_sources = [], shading_type = "" ):
    if len(matrix) < 2:
        print 'Need at least 3 points to draw'
        return

    if shading_type == "goroud" or shading_type == "phong":
        normalized_vectors_dict = normalize_vectors(matrix)

    intensities = []
    point = 0
    while point < len(matrix) - 2:

        normal = get_normal(matrix, point)[:]
        if normal[2] > 0:
            if shading_type == "flat":
                color = get_total_light(normal, constants, light_sources)

            elif shading_type == "goroud":
                list_of_matrix_points = [matrix[point], matrix[point + 1], matrix[point + 2]]
                intensities = [get_total_light(normalized_vectors_dict[(int(matrix_points[0]), int(matrix_points[1]), matrix_points[2])],
                                               constants, light_sources) for matrix_points in list_of_matrix_points]

            elif shading_type == "phong":
                list_of_matrix_points = [matrix[point], matrix[point + 1], matrix[point + 2]]
                intensities = [ normalized_vectors_dict[int(matrix_points[0]), int(matrix_points[1]), matrix_points[2]] for matrix_points in list_of_matrix_points]
            scanline_convert(matrix, point, screen, zbuffer, color, shading_type, intensities, constants, light_sources)
        point += 3

def add_box( polygons, x, y, z, width, height, depth ):
    x1 = x + width
    y1 = y - height
    z1 = z - depth

    #front
    add_polygon(polygons, x, y, z, x1, y1, z, x1, y, z);
    add_polygon(polygons, x, y, z, x, y1, z, x1, y1, z);

    #back
    add_polygon(polygons, x1, y, z1, x, y1, z1, x, y, z1);
    add_polygon(polygons, x1, y, z1, x1, y1, z1, x, y1, z1);

    #right side
    add_polygon(polygons, x1, y, z, x1, y1, z1, x1, y, z1);
    add_polygon(polygons, x1, y, z, x1, y1, z, x1, y1, z1);
    #left side
    add_polygon(polygons, x, y, z1, x, y1, z, x, y, z);
    add_polygon(polygons, x, y, z1, x, y1, z1, x, y1, z);

    #top
    add_polygon(polygons, x, y, z1, x1, y, z, x1, y, z1);
    add_polygon(polygons, x, y, z1, x, y, z, x1, y, z);
    #bottom
    add_polygon(polygons, x, y1, z, x1, y1, z1, x1, y1, z);
    add_polygon(polygons, x, y1, z, x, y1, z1, x1, y1, z1);

def add_sphere( edges, cx, cy, cz, r, step ):
    points = generate_sphere(cx, cy, cz, r, step)
    num_steps = int(1/step+0.1)

    lat_start = 0
    lat_stop = num_steps
    longt_start = 0
    longt_stop = num_steps

    num_steps+= 1
    for lat in range(lat_start, lat_stop):
        for longt in range(longt_start, longt_stop):

            p0 = lat * (num_steps) + longt
            p1 = p0+1
            p2 = (p1+num_steps) % (num_steps * (num_steps-1))
            p3 = (p0+num_steps) % (num_steps * (num_steps-1))

            if longt != num_steps - 2:
                add_polygon( edges, points[p0][0],
                             points[p0][1],
                             points[p0][2],
                             points[p1][0],
                             points[p1][1],
                             points[p1][2],
                             points[p2][0],
                             points[p2][1],
                             points[p2][2])
            if longt != 0:
                add_polygon( edges, points[p0][0],
                             points[p0][1],
                             points[p0][2],
                             points[p2][0],
                             points[p2][1],
                             points[p2][2],
                             points[p3][0],
                             points[p3][1],
                             points[p3][2])

def generate_sphere( cx, cy, cz, r, step ):
    points = []
    num_steps = int(1/step+0.1)

    rot_start = 0
    rot_stop = num_steps
    circ_start = 0
    circ_stop = num_steps

    for rotation in range(rot_start, rot_stop):
        rot = step * rotation
        for circle in range(circ_start, circ_stop+1):
            circ = step * circle

            x = r * math.cos(math.pi * circ) + cx
            y = r * math.sin(math.pi * circ) * math.cos(2*math.pi * rot) + cy
            z = r * math.sin(math.pi * circ) * math.sin(2*math.pi * rot) + cz

            points.append([x, y, z])
            #print 'rotation: %d\tcircle%d'%(rotation, circle)
    return points

def add_torus( edges, cx, cy, cz, r0, r1, step ):
    points = generate_torus(cx, cy, cz, r0, r1, step)
    num_steps = int(1/step+0.1)

    lat_start = 0
    lat_stop = num_steps
    longt_start = 0
    longt_stop = num_steps

    for lat in range(lat_start, lat_stop):
        for longt in range(longt_start, longt_stop):

            p0 = lat * (num_steps) + longt;
            if (longt == num_steps - 1):
                p1 = p0 - longt;
            else:
                p1 = p0 + 1;
            p2 = (p1 + num_steps) % (num_steps * num_steps);
            p3 = (p0 + num_steps) % (num_steps * num_steps);

            add_polygon(edges,
                        points[p0][0],
                        points[p0][1],
                        points[p0][2],
                        points[p3][0],
                        points[p3][1],
                        points[p3][2],
                        points[p2][0],
                        points[p2][1],
                        points[p2][2] )
            add_polygon(edges,
                        points[p0][0],
                        points[p0][1],
                        points[p0][2],
                        points[p2][0],
                        points[p2][1],
                        points[p2][2],
                        points[p1][0],
                        points[p1][1],
                        points[p1][2] )

def generate_torus( cx, cy, cz, r0, r1, step ):
    points = []
    num_steps = int(1/step+0.1)

    rot_start = 0
    rot_stop = num_steps
    circ_start = 0
    circ_stop = num_steps

    for rotation in range(rot_start, rot_stop):
        rot = step * rotation
        for circle in range(circ_start, circ_stop):
            circ = step * circle

            x = math.cos(2*math.pi * rot) * (r0 * math.cos(2*math.pi * circ) + r1) + cx;
            y = r0 * math.sin(2*math.pi * circ) + cy;
            z = -1*math.sin(2*math.pi * rot) * (r0 * math.cos(2*math.pi * circ) + r1) + cz;

            points.append([x, y, z])
    return points

def add_circle( points, cx, cy, cz, r, step ):
    x0 = r + cx
    y0 = cy
    t = step

    while t <= 1.00001:
        x1 = r * math.cos(2*math.pi * t) + cx;
        y1 = r * math.sin(2*math.pi * t) + cy;

        add_edge(points, x0, y0, cz, x1, y1, cz)
        x0 = x1
        y0 = y1
        t+= step

def add_curve( points, x0, y0, x1, y1, x2, y2, x3, y3, step, curve_type ):

    xcoefs = generate_curve_coefs(x0, x1, x2, x3, curve_type)[0]
    ycoefs = generate_curve_coefs(y0, y1, y2, y3, curve_type)[0]

    t = step
    while t <= 1.00001:
        x = xcoefs[0] * t*t*t + xcoefs[1] * t*t + xcoefs[2] * t + xcoefs[3]
        y = ycoefs[0] * t*t*t + ycoefs[1] * t*t + ycoefs[2] * t + ycoefs[3]

        add_edge(points, x0, y0, 0, x, y, 0)
        x0 = x
        y0 = y
        t+= step

def draw_lines( matrix, screen, zbuffer, color ):
    if len(matrix) < 2:
        print 'Need at least 2 points to draw'
        return

    point = 0
    while point < len(matrix) - 1:
        draw_line( int(matrix[point][0]),
                   int(matrix[point][1]),
                   matrix[point][2],
                   int(matrix[point+1][0]),
                   int(matrix[point+1][1]),
                   matrix[point+1][2],
                   screen, zbuffer, color)
        point+= 2

def add_edge( matrix, x0, y0, z0, x1, y1, z1 ):
    add_point(matrix, x0, y0, z0)
    add_point(matrix, x1, y1, z1)

def add_point( matrix, x, y, z=0 ):
    matrix.append( [x, y, z, 1] )

def scanline_helper(x0, y0, z0, x1, y1, z1):
    #swap points if going right -> left
    if x0 > x1:
        xt = x0
        yt = y0
        zt = z0
        x0 = x1
        y0 = y1
        z0 = z1
        x1 = xt
        y1 = yt
        z1 = zt

    x = x0
    y = y0
    z = z0
    A = 2 * (y1 - y0)
    B = -2 * (x1 - x0)
    wide = False
    tall = False

    if ( abs(x1-x0) >= abs(y1 - y0) ): #octants 1/8
        wide = True
        loop_start = x
        loop_end = x1
        dx_east = dx_northeast = 1
        dy_east = 0
        d_east = A
        distance = x1 - x
        if ( A > 0 ): #octant 1
            d = A + B/2
            dy_northeast = 1
            d_northeast = A + B
        else: #octant 8
            d = A - B/2
            dy_northeast = -1
            d_northeast = A - B

    else: #octants 2/7
        tall = True
        dx_east = 0
        dx_northeast = 1
        distance = abs(y1 - y)
        if ( A > 0 ): #octant 2
            d = A/2 + B
            dy_east = dy_northeast = 1
            d_northeast = A + B
            d_east = B
            loop_start = y
            loop_end = y1
        else: #octant 7
            d = A/2 - B
            dy_east = dy_northeast = -1
            d_northeast = A - B
            d_east = -1 * B
            loop_start = y1
            loop_end = y

    delta_z = float(z1 - z)/distance if distance != 0 else 0
    old_y = y
    l = [ [x, z] ]
    while ( loop_start < loop_end ):
        if y != old_y:
            l.append([x, z])
            old_y = y
        if ( (wide and ((A > 0 and d > 0) or (A < 0 and d < 0))) or
             (tall and ((A > 0 and d < 0) or (A < 0 and d > 0 )))):
            x+= dx_northeast
            y+= dy_northeast
            d+= d_northeast
        else:
            x+= dx_east
            y+= dy_east
            d+= d_east
        z += delta_z
        loop_start+= 1

    if y != old_y:
        l.append([x, z])
    return l

def draw_line( x0, y0, z0, x1, y1, z1, screen, zbuffer, color, left=[], right=[], shading_type="", constants=[], light_sources=[] ):

    #swap points if going right -> left
    if x0 > x1:
        xt = x0
        yt = y0
        zt = z0
        x0 = x1
        y0 = y1
        z0 = z1
        x1 = xt
        y1 = yt
        z1 = zt

    x = x0
    y = y0
    z = z0
    A = 2 * (y1 - y0)
    B = -2 * (x1 - x0)
    wide = False
    tall = False

    if ( abs(x1-x0) >= abs(y1 - y0) ): #octants 1/8
        wide = True
        loop_start = x
        loop_end = x1
        dx_east = dx_northeast = 1
        dy_east = 0
        d_east = A
        distance = x1 - x
        if ( A > 0 ): #octant 1
            d = A + B/2
            dy_northeast = 1
            d_northeast = A + B
        else: #octant 8
            d = A - B/2
            dy_northeast = -1
            d_northeast = A - B

    else: #octants 2/7
        tall = True
        dx_east = 0
        dx_northeast = 1
        distance = abs(y1 - y)
        if ( A > 0 ): #octant 2
            d = A/2 + B
            dy_east = dy_northeast = 1
            d_northeast = A + B
            d_east = B
            loop_start = y
            loop_end = y1
        else: #octant 7
            d = A/2 - B
            dy_east = dy_northeast = -1
            d_northeast = A - B
            d_east = -1 * B
            loop_start = y1
            loop_end = y

    delta_z = float(z1 - z)/distance if distance != 0 else 0

    if shading_type == "goroud":
        color = left[:]

    elif shading_type == "phong":
        color = get_total_light(left, constants, light_sources)
        if distance != 0:
            d_N = [ float(right[0] - left[0])/(distance), float(right[1] - left[1])/(distance), float(right[2] - left[2])/(distance) ]
            N = left[:]

    while ( loop_start < loop_end ):
        plot( screen, zbuffer, color, x, y, z )

        if ( (wide and ((A > 0 and d > 0) or (A < 0 and d < 0))) or
             (tall and ((A > 0 and d < 0) or (A < 0 and d > 0 )))):
            x+= dx_northeast
            y+= dy_northeast
            d+= d_northeast
        else:
            x+= dx_east
            y+= dy_east
            d+= d_east

        if shading_type == "goroud":
            for i in range(len(color)):
                I = int(round((float(x - x0)/(x1 - x0)) * right[i] + (float(x1 - x)/(x1 - x0)) * left[i]))
                color[i] = I if I <= 255 else 255
        elif shading_type == "phong":
            for i in range(len(color)):
                N[i] += d_N[i]
            color = get_total_light(N, constants, light_sources)


        z += delta_z
        loop_start+= 1

    plot( screen, zbuffer, color, x1, y1, z1 )
