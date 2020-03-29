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
from Word import Word
import tty
import termios
from datetime import datetime
import os

SCANNER = None


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


# and Word is in Word.py
class Line:
    def __init__(self, words=[]):
        self.words = words


class Paragraph:
    def __init__(self, lines=[]):
        self.lines = lines


class Block:
    def __init__(self, paragraphs=[]):
        self.paragraphs = paragraphs


def boxes_to_blocks(boxes):
    # print(boxes)

    blocks = []

    levels = boxes['level']
    page_nums = boxes['page_num']
    block_nums = boxes['block_num']
    paragraph_nums = boxes['par_num']
    line_nums = boxes['line_num']
    word_nums = boxes['word_num']
    lefts = boxes['left']
    tops = boxes['top']
    widths = boxes['width']
    heights = boxes['height']
    confs = boxes['conf']
    texts = boxes['text']

    # what i have been referring to as a paragraph is actually a "block"
    # in their terminology.
    current_block_number = -1

    this_paragraph = {
        'levels': [],
        'page_nums': [],
        'paragraph_nums': [],
        'line_nums': [],
        'word_nums': [],
        'lefts': [],
        'tops': [],
        'widths': [],
        'heights': [],
        'confs': [],
        'texts': []
    }

    for i in range(len(texts)):
        level = levels[i]
        page_num = page_nums[i]
        block_num = block_nums[i]
        paragraph_num = paragraph_nums[i]
        line_num = line_nums[i]
        word_num = word_nums[i]
        left = lefts[i]
        top = tops[i]
        width = widths[i]
        height = heights[i]
        conf = confs[i]
        text = texts[i]

        if block_num != current_block_number:
            if current_block_number > -1:
                blocks.append(this_paragraph)

            current_block_number = block_num
            # TODO
            # these should probably be Words (or something) instead...
            this_paragraph = {
                'levels': [level],
                'page_nums': [page_num],
                'paragraph_nums': [paragraph_num],
                'line_nums': [line_num],
                'block_nums': [block_num],
                'word_nums': [word_num],
                'lefts': [left],
                'tops': [top],
                'widths': [width],
                'heights': [height],
                'confs': [conf],
                'texts': [text]
            }
        else:
            this_paragraph['levels'].append(level)
            this_paragraph['page_nums'].append(page_num)
            this_paragraph['paragraph_nums'].append(paragraph_num)
            this_paragraph['line_nums'].append(line_num)
            this_paragraph['word_nums'].append(word_num)
            this_paragraph['lefts'].append(left)
            this_paragraph['tops'].append(top)
            this_paragraph['widths'].append(width)
            this_paragraph['heights'].append(height)
            this_paragraph['confs'].append(conf)
            this_paragraph['texts'].append(text)

    blocks.append(this_paragraph)

    return blocks


def boxes_to_lines_of_words(boxes):
    lines = []

    # this is actually the nubmer of characters.
    # number of lines is probably number of \n
    num_lines = max(boxes['line_num'])
    print('num lines according to boxes_to_lines_of_words:', num_lines)

    if num_lines == 0:
        return lines

    # THIS IS LOOKING @ THE DATA INCORRECTLY.
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

        print(
            'Initial Device parameters:',
            params,
            "\n Resolutions %d," % (SCANNER.resolution))

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
        except Exception as e:
            print('cant set resolution, using default', e)

        try:
            print('setting br_x')
            SCANNER.br_x = br_x
            print('set br_x')
        except Exception as e:
            print('cant set br_x', e)

        try:
            print('setting br_y')
            SCANNER.br_y = br_y
            print('set br_y')
        except Exception as e:
            print('cant set br_y', e)

        params = SCANNER.get_parameters()
        # print('updated scanner params:', params)
        print(
            'Updated Device parameters:',
            params,
            "\n Resolutions %d, " % (SCANNER.resolution))

        try:
            # TODO:
            # this tends to fail on first runs...i suspect that
            # it has something to do w/ scanner warm up time or something..
            # perhaps a delay before or after, or polling something on
            # SCANNER is in order...
            SCANNER.start()
        except Exception as e:
            print('failed starting scanner', e)
            eat_me = sys.exc_info()[0]
            print(eat_me)
            SCANNER.close()
            exit()

        return SCANNER.snap()

    else:
        print("cano_tuple_list empty")
        return None


def process_image(im):
    image_text = pytesseract.image_to_string(im)
    print('text extracted from the image:', image_text)
    print('num lines according to image_to_string:', len(image_text))

    # this is the line count i expect
    alt_num_lines = image_text.count('\n')
    print('alt_num_lines:', alt_num_lines)

    # BOXES = pytesseract.image_to_boxes(im)
    # BOXES = pytesseract.image_to_data(im, lang=None, config='', nice=0,
    #                                   output_type=pytesseract.Output.STRING)
    BOXES = pytesseract.image_to_data(im, lang=None, config='', nice=0,
                                      output_type='dict')

    # pytesseract.image_to_data()

    # print(BOXES)
    # breakpoint()
    # print(type(BOXES))

    # dump_boxes(BOXES)

    # lines = boxes_to_lines_of_words(BOXES)
    blocks = None
    blocks = boxes_to_blocks(BOXES)

    # foreach block, make a new Block
    # maybe the simplest thing i can do is
    # have each line know by how many tabs it is indented.
    return blocks


def pluck_left_most_words(lines):
    # iterate over each of the lines, grab the one
    # w/ the
    # 0 seems empty...
    line = lines[1]
    for w in line:
        print(w.left, w.text)

    return []


class GetCh:
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class Book:
    def __init__(self):
        self.page_count = 0
        self.current_page = 0
        self.pages = []
        self.title = None
        self.library_location = '/home/patrick/library/'

    def add_page(self):
        im = image_from_scanner()
        page = pytesseract.image_to_string(im)
        self.pages.append(page)

    def get_pages(self):
        return self.pages

    def write_to_library(self):
        if len(self.pages) == 0:
            print("there are no pages, and so nothing to export...bailing")
            return

        if self.title is None:
            self.title = str(datetime.timestamp(datetime.now())).split('.')[0]

        # this added slash may be extraneous...
        book_dir = self.library_location + '/' + self.title

        print("book_dir: " + book_dir)

        if os.path.exists(book_dir):
            raise Exception('{} already exists. will not overwrite'.format(book_dir))

        print("looks like " + book_dir + " DNE yet. will create it")

        os.mkdir(book_dir)

        page_number = 0
        # foreach one of pages, dump every line to file page_number
        # inc page_number, continue.
        for page in self.pages:
            lines = page.split("\n")
            # this_file_name = book_dir + str(page_number) + '.txt'
            this_file_name = book_dir + '/' + str(page_number) + '.txt'
            this_file = open(this_file_name, "w+")
            print("writing lines to " + this_file_name)

            # since i exploded all newlines, this does not serve.
            # this_file.writelines(lines)

            for line in lines:
                this_file.write(line + "\n")

            this_file.close()
            print("wrote lines to " + this_file_name)
            page_number += 1


def main():
    """do work"""
    global SCANNER

    getch = GetCh()

    print("starting book.")

    book = Book()
    book.title = "typewriter_output"

    book.write_to_library()

    print("stick a page in the scanner.")
    print("press y when ready. any other key will bail.")
    keep_going = getch()

    while keep_going == 'y':
        book.add_page()
        print("stick a page in the scanner.")
        print("press y when ready. any other key will bail.")
        keep_going = getch()

    book.write_to_library()
    # im = image_from_file('input0_small.png')
    # paragraphs = process_image(im)
    # s = pytesseract.image_to_string(im)
    # print(s)

    # print(paragraphs)
    # for p in paragraphs:
        # print(p)
        # print("\n")

    breakpoint()

    # left_most_words = pluck_left_most_words(lines)
    # print('left_most_words:', left_most_words)

    # at this point, i should have enough info to calculate indentation...
    # breakpoint()
    # print(type(lines))

    if SCANNER is not None:
        SCANNER.close()
        sane.exit()


if __name__ == '__main__':
    main()
