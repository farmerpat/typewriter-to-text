#!/usr/bin/env python
"""
typewriter output -> text files via CanoScan
"""

# https://pypi.org/project/pytesseract/

# https://python-sane.readthedocs.io/en/latest/

from PIL import Image
import pytesseract
import sane
import sys

# print(pytesseract.image_to_string(Image.open('ocr0.png')))
# print('attempting to parse text from input0')
# print()
# print(pytesseract.image_to_string(Image.open('input0.png')))
# print('done')

# BOXES = pytesseract.image_to_boxes(Image.open("ocr1.png"))
# print(BOXES)
# print(type(BOXES))

# parsed_string = pytesseract.image_to_string(Image.open("ocr1.png"))
# print(parsed_string)

# it seems like by leveraging this function
# i can easily determine "furthest left margin"
# which characters belong to the same line
# and (hopefully) how large a glyph itself is
# (e.g. how large is a space supposed to be
# so that we can indent properly)
# ...
# I am pretty sure that I can wire up a script that will
# scan a document, pipe the generated image to a py script
# that does work
# and outputs a bloody text file.
# ...this will become my freedom from computational machines.
# I determine my level of involvement outside of my current career.
# this seems an appropriate use of technology to allow
# for creativity w/o all the gross side-effects of constant
# screen-gazing

class Word:
    def __init__(
            self,
            text='',
            line_num=0,
            word_num=0,
            par_num=0,
            left=0,
            top=0,
            width=0,
            height=0
    ):
        self.text = text
        self.line_num = line_num
        self.word_num = word_num
        self.par_num = par_num
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    def __str__(self):
        s = ''
        s += 'text: ' + self.text + '\n'
        s += 'line_num: ' + str(self.line_num) + '\n'
        s += 'word_num: ' + str(self.word_num) + '\n'
        s += 'par_num: ' + str(self.par_num) + '\n'
        s += 'left: ' + str(self.left) + '\n'
        s += 'top: ' + str(self.top) + '\n'
        s += 'width: ' + str(self.width) + '\n'
        s += 'height: ' + str(self.height) + '\n'
        return s

def dump_boxes(BOXES, index=-1):
    if index == -1:
        # all the boxes
        for idx in range(len(BOXES.keys())):
            print("")
            print('level:', BOXES['level'][index])
            print('page_num', BOXES['page_num'][index])
            print('block_num', BOXES['block_num'][index])
            print('par_num', BOXES['par_num'][index])
            print('line_num', BOXES['line_num'][index])
            print('word_num', BOXES['word_num'][index])
            print('left', BOXES['left'][index])
            print('top', BOXES['top'][index])
            print('width', BOXES['width'][index])
            print('height', BOXES['height'][index])
            print('conf', BOXES['conf'][index])
            print('text', BOXES['text'][index])

    else:
        print("")
        print('level:', BOXES['level'][index])
        print('page_num', BOXES['page_num'][index])
        print('block_num', BOXES['block_num'][index])
        print('par_num', BOXES['par_num'][index])
        print('line_num', BOXES['line_num'][index])
        print('word_num', BOXES['word_num'][index])
        print('left', BOXES['left'][index])
        print('top', BOXES['top'][index])
        print('width', BOXES['width'][index])
        print('height', BOXES['height'][index])
        print('conf', BOXES['conf'][index])
        print('text', BOXES['text'][index])
        # a specific box

def generate_line_of_words(boxes, line_number):
    low = []
    # pluck all the things with that line_number...
    # so if we find a matching line num,
    # then we can create a new Word
    # initialize it w/ matching index things
    # and push it onto low
    for idx in range(len(boxes['line_num'])):
        ln = boxes['line_num'][idx]
        if ln == line_number:
            this_word = Word(boxes['text'][idx],
                             boxes['line_num'][idx],
                             boxes['word_num'][idx],
                             boxes['par_num'][idx],
                             boxes['left'][idx],
                             boxes['top'][idx],
                             boxes['width'][idx],
                             boxes['height'][idx])
            low.append(this_word)

    return low

def boxes_to_lines_of_words(boxes):
    lines = []
    num_lines = max(boxes['line_num'])

    if num_lines == 0:
        return lines

    for ln in range(num_lines):
        # well the zeroth line maybe we don't care about...
        words_in_line = generate_line_of_words(boxes, ln)
        lines.append(words_in_line)

    return lines

def scan_page():
    """do work"""
    depth = 14
    mode = 'Lineart'
    resolution = 200
    br_x = 404

    # TODO: fixme
    # br_y = 19464192.0 / resolution
    br_y = 523



    # TODO: OBVIOUSLY DO ALL THIS ONCE DURING INIT.
    sane_init_result = sane.init()
    print(sane_init_result)

    devices = sane.get_devices(True)
    print('available devices: ', devices)

    cano_tuple_list = [d for d in devices if d[2].startswith('CanoScan')]

    if len(cano_tuple_list) > 0:
        print('cano_tuple_list:', cano_tuple_list)
        cano_tuple = cano_tuple_list[0]
        scanner_name = cano_tuple[0]
        print('scanner_name:', scanner_name)

        scanner = sane.open(scanner_name)
        print('scanner:', scanner)
        print('fyf again')

        params = scanner.get_parameters()

        print('Initial Device parameters:', params, "\n Resolutions %d, "%(scanner.resolution))

        # try:
            # print('setting depth')
            # scanner.depth = depth
            # print('set depth')
        # except:
            # print('cant set depth, defaulting to %d' % params[3])

        """
        try:
            print('setting mode')
            scanner.mode = mode
            print('set mode')
        except:
            print('cant set mode, defaulting to %s' % params[0])

        try:
            print('setting preview')
            scanner.preview = 0
            print('set preview')
        except:
            print('cant set preview')

        try:
            print('setting tl_x')
            scanner.tl_x = 0
            print('set tl_x')
        except:
            print('cant set tl_x')

        try:
            print('setting tl_y')
            scanner.tl_y = 0
            print('set tl_y')
        except:
            print('cant set tl_y')
        """

        # it occurs to me that the order in which we set these matters...
        # in Canon:CanoScanN1220U.drc
        # the order is mode, resolution, tl, br, brightness, etc
        # so mode defaults to color.
        # set res to 200 and see how it does.
        try:
            print('setting resolution')
            scanner.resolution = 200
            print('set resolution')
        except:
            print('cant set resolution, using default')

        try:
            print('setting br_x')
            scanner.br_x = br_x
            print('set br_x')
        except:
            print('cant set br_x')

        try:
            print('setting br_y')
            scanner.br_y = br_y
            print('set br_y')
        except:
            print('cant set br_y')

        params = scanner.get_parameters()
        # print('updated scanner params:', params)
        print('Updated Device parameters:', params, "\n Resolutions %d, "%(scanner.resolution))

        # breakpoint()

        # scanner.opt is a dict... how convenient:
        # print(scanner.opt['resolution'])

        # start scanning and grab a PIL.Image obj
        try:
            scanner.start()
        except:
            print('failed starting scanner')
            eat_me = sys.exc_info()[0]
            print(eat_me)
            breakpoint()
            scanner.close()
            exit()

        scanned_image = scanner.snap()
        # TODO: if this works, inspect the image data
        scanned_image.save('input0.png')
        image_text = pytesseract.image_to_string(scanned_image)
        print('text extracted from the image:', image_text)

        # BOXES = pytesseract.image_to_boxes(scanned_image)
        BOXES = pytesseract.image_to_data(scanned_image, None, '', 0, pytesseract.Output.DICT)
        print(BOXES)
        print(type(BOXES))

        # inspect the BOXES...see what we might do with them...

        # dump_boxes(BOXES, 9)
        dump_boxes(BOXES)

        # there may be a more pythony way, but
        # it seems like collapsing BOXES
        # into a data structure grouped by line
        # or perhaps words
        # or perhaps Line is a collection of Words
        # among other things.
        # so we could explode into words first...
        # would be a fine approach

        # ...word_num of 0 is scattered throughout...
        # perhaps it means "a space, so not part of a word...
        lines = boxes_to_lines_of_words(BOXES)
        breakpoint()
        scanner.close()
    else:
        print("cano_tuple_list empty")

    sane.exit()

scan_page()
