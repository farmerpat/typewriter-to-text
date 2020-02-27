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
