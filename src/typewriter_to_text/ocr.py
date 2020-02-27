#!/usr/bin/env python
"""
typewriter output -> text files via CanoScan
"""

# https://pypi.org/project/pytesseract/

# https://python-sane.readthedocs.io/en/latest/

import sys
from PIL import Image
import pytesseract
import sane

SCANNER = None


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


def dump_boxes(boxes, index=-1):
    """dumps boxes"""
    if index == -1:
        # all the boxes
        for idx in range(len(boxes.keys())):
            print("")
            print('level:', boxes['level'][index])
            print('page_num', boxes['page_num'][index])
            print('block_num', boxes['block_num'][index])
            print('par_num', boxes['par_num'][index])
            print('line_num', boxes['line_num'][index])
            print('word_num', boxes['word_num'][index])
            print('left', boxes['left'][index])
            print('top', boxes['top'][index])
            print('width', boxes['width'][index])
            print('height', boxes['height'][index])
            print('conf', boxes['conf'][index])
            print('text', boxes['text'][index])

    else:
        print("")
        print('level:', boxes['level'][index])
        print('page_num', boxes['page_num'][index])
        print('block_num', boxes['block_num'][index])
        print('par_num', boxes['par_num'][index])
        print('line_num', boxes['line_num'][index])
        print('word_num', boxes['word_num'][index])
        print('left', boxes['left'][index])
        print('top', boxes['top'][index])
        print('width', boxes['width'][index])
        print('height', boxes['height'][index])
        print('conf', boxes['conf'][index])
        print('text', boxes['text'][index])


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


def image_from_file(file):
    return Image.open(file)


def image_from_scanner():
    global SCANNER

    # depth = 14
    # mode = 'Lineart'
    # resolution = 200
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

        SCANNER = sane.open(scanner_name)
        print('SCANNER:', SCANNER)
        print('fyf again')

        params = SCANNER.get_parameters()

        print('Initial Device parameters:', params, "\n Resolutions %d, "%(SCANNER.resolution))

        # try:
            # print('setting depth')
            # SCANNER.depth = depth
            # print('set depth')
        # except:
            # print('cant set depth, defaulting to %d' % params[3])

        """
        try:
            print('setting mode')
            SCANNER.mode = mode
            print('set mode')
        except:
            print('cant set mode, defaulting to %s' % params[0])

        try:
            print('setting preview')
            SCANNER.preview = 0
            print('set preview')
        except:
            print('cant set preview')

        try:
            print('setting tl_x')
            SCANNER.tl_x = 0
            print('set tl_x')
        except:
            print('cant set tl_x')

        try:
            print('setting tl_y')
            SCANNER.tl_y = 0
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
            SCANNER.resolution = 200
            print('set resolution')
        except:
            print('cant set resolution, using default')

        try:
            print('setting br_x')
            SCANNER.br_x = br_x
            print('set br_x')
        except:
            print('cant set br_x')

        try:
            print('setting br_y')
            SCANNER.br_y = br_y
            print('set br_y')
        except:
            print('cant set br_y')

        params = SCANNER.get_parameters()
        # print('updated scanner params:', params)
        print('Updated Device parameters:', params, "\n Resolutions %d, "%(SCANNER.resolution))

        try:
            # TODO:
            # this tends to fail on first runs...i suspect that
            # it has something to do w/ scanner warm up time or something..
            # perhaps a delay before or after, or polling something on
            # SCANNER is in order...
            SCANNER.start()
        except:
            print('failed starting scanner')
            eat_me = sys.exc_info()[0]
            print(eat_me)
            breakpoint()
            SCANNER.close()
            exit()

        return SCANNER.snap()

    else:
        print("cano_tuple_list empty")
        return None


def process_image(im):
    image_text = pytesseract.image_to_string(im)
    print('text extracted from the image:', image_text)

    # BOXES = pytesseract.image_to_boxes(im)
    BOXES = pytesseract.image_to_data(im, None, '', 0, pytesseract.Output.DICT)
    print(BOXES)
    print(type(BOXES))

    dump_boxes(BOXES)

    lines = boxes_to_lines_of_words(BOXES)
    print("lines:", lines)
    return lines


def main():
    """do work"""
    global SCANNER

    im = image_from_file('input0.png')
    # im = image_from_scanner()
    lines = process_image(im)
    print(type(lines))

    breakpoint()

    if SCANNER is not None:
        SCANNER.close()
        sane.exit()


if __name__ == '__main__':
    main()
