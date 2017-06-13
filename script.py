import os
import sys

import mdl
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
def first_pass(source):
    FRAMES_SET = False
    NUM_FRAMES = -1
    BASENAME = 'default'
    list_of_commands_and_args = [[line[0], line[1:]] for line in source]

    for command, args in list_of_commands_and_args:
        assert command != 'vary' or FRAMES_SET, 'Frames was not set before calling vary!'

        if command == 'frames':
            NUM_FRAMES = args[0]
            FRAMES_SET = True
        elif command == 'basename':
            BASENAME = args[0]

    if FRAMES_SET and BASENAME == 'default':
        print 'Basename was not set, setting it to {0}'.format(BASENAME)

    return BASENAME, NUM_FRAMES

"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value.
  ===================="""
def second_pass(source, NUM_FRAMES):
    if NUM_FRAMES == -1:
        return

    knobs = [{} for _ in xrange(NUM_FRAMES)]
    list_of_commands_and_args = [[line[0], line[1:]] for line in source]

    for command, args in list_of_commands_and_args:
        if command == 'vary':
            name = args[0]
            start_frame, end_frame = map(int, args[1:3])
            start_value, end_value = map(float, args[3:])

            FRAME_DIFFERENCE = end_frame - start_frame
            MINIMUM_FRAME_NUM = -1
            MAXIMUM_FRAME_NUM = NUM_FRAMES

            assert (FRAME_DIFFERENCE > 0 and
                    start_frame > MINIMUM_FRAME_NUM and
                    end_frame < MAXIMUM_FRAME_NUM), ('Illegal Argument Exception: Invalid frame range')

            VALUE_DIFFERENCE = end_value - start_value
            DELTA_VALUE_DIFFERENCE = VALUE_DIFFERENCE / FRAME_DIFFERENCE

            current_value = start_value
            interval = 1

            if DELTA_VALUE_DIFFERENCE < 0:
                start_frame, end_frame = end_frame, start_frame
                DELTA_VALUE_DIFFERENCE = -DELTA_VALUE_DIFFERENCE
                interval = -interval
                current_value, end_value = end_value, start_value

            for frame_num in xrange(start_frame, end_frame + interval, interval):
                knobs[frame_num][name] = current_value
                current_value += (int(current_value < end_value) * DELTA_VALUE_DIFFERENCE)

    return knobs

def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    tmp = new_matrix()
    ident( tmp )
    screen = new_screen()
    step = 0.01

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    setting = {}
    BASENAME, NUM_FRAMES = first_pass(commands)
    knobs = second_pass(commands, NUM_FRAMES)

    if NUM_FRAMES == -1:
        NUM_FRAMES = 1

    light_sources = [symbols[i][1] for i in symbols if symbols[i][0] == 'light']
    if 'shading' in symbols:
        shading_type = symbols['shading'][1]

    for frame_num in xrange(NUM_FRAMES):
        print 'Pass {0}...    '.format(frame_num),
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]

        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step = 0.1

        for command in commands:
            c = command[0]
            args = command[1:]

            if c == 'set':
                symbols[args[0]][1] = float(args[1])

            elif c == 'setknobs':
                for s in symbols:
                    if symbols[s][0] == 'knob':
                        symbols[s][1] = float(args[0])

            elif c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                if args[-1]:
                    draw_polygons(tmp, screen, zbuffer, color, symbols[args[-1]][1], light_sources, shading_type)
                else:
                    draw_polygons(tmp, screen, zbuffer, color)
                tmp = []


            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                if args[-1]:
                    draw_polygons(tmp, screen, zbuffer, color, symbols[args[-1]][1], light_sources, shading_type)
                else:
                    draw_polygons(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                if args[-1]:
                    draw_polygons(tmp, screen, zbuffer, color, symbols[args[-1]][1], light_sources, shading_type)
                else:
                    draw_polygons(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':

                if args[3] != None:
                    a = knobs[frame_num][args[3]] * args[0]
                    b = knobs[frame_num][args[3]] * args[1]
                    c = knobs[frame_num][args[3]] * args[2]
                    args = (a,b,c,args[3])

                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':

                if args[3] != None:
                    a = knobs[frame_num][args[3]] * args[0]
                    b = knobs[frame_num][args[3]] * args[1]
                    c = knobs[frame_num][args[3]] * args[2]
                    args = (a,b,c,args[3])

                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':

                if args[2] != None:
                    a = knobs[frame_num][args[2]] * args[1]
                    args = (args[0],a,args[2])

                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []

            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        print 'Done!'

        name = 'anim/' + BASENAME + (3-len(str(frame_num)))*'0' + str(frame_num) + '.ppm'

        if not os.path.exists('anim'):
            os.makedirs('anim')

        save_ppm(screen,name)
        clear_screen(screen)

    make_animation(BASENAME)
