from collections import deque

class NoData(Exception):
    pass

class Pipe(object):
    '''Generic pipe object. Add functions to put items in the pipe or something.'''
    def __init__(self, debug=False):
        self.processors = deque()
        self.first = None
        self.last = None
        self.debug = debug
    def __rshift__(self, something):
        '''Let's for now assume it's a normal function. If not, we can also detect
        that in __call__, but maybe we would want to do something here..'''
        '''Yeah. Actually, we will want to transform that function here.'''
        self.processors.append(something)
        return self
    def __rrshift__(self, data):
        '''Not sure if we want this. This would mean:
        [1,2,3] @ mypipe + foo("bar")
        or similar. Could only be done once, I guess?'''
        if self.debug: print("Adding input data: {}".format(repr(data)))
        self.first = deque(data)
        return self
    def __call__(self, debug = False):
        '''Process everything.
        Assumptions: self.processors is fixed now. self.data is not.'''
        #Initialize in- and outputs:
        previous = self.first
        for proc in self.processors:
            if self.debug: print("Adding processor: {}".format(repr(proc)))
            #print(repr(previous))
            previous = proc.set_in_out(previous)
        self.last = previous
        #while we still have processors:
        while self.processors:
            #loop through them,
            for i, proc in enumerate(self.processors):
                try:
                    proc.process()
                except NoData:
                    if i == 0: #first generator?
                        break
                    else:
                        continue # go to next processor
            else: #nobreak
                continue #start from the beginning again
            #break
            if self.debug: print("Processor {} stopped".format(repr(self.processors[0])))
            self.processors.popleft()#remove leftmost processor
        if self.debug: print("No more processors active, returning result")
        yield from self.last


class Processor(object):
    def __init__(self):
        '''Initialize settings from args.'''
        pass
    def set_in_out(self, in_):
        self.in_ = in_
        #some mutable object
        self.out_ = deque()
        return self.out_
    def process(self):
        '''Do with input, into output. If empty, raise NoData.'''
        pass
    def __rshift__(self, other):
        '''This means: No pipe class was there.
        We have to make a pipe and return it.'''
        return Pipe() >> self >> other
    def __rrshift__(self, data):
        '''This means we got input on the left.
        Possibly rename to rrshift.
        [1,2,3] @ mypipe + foo("bar")
        or similar. Could only be done once, I guess?'''
        p = Pipe()
        p.first = deque(data)
        return p >> self

class AddTwo(Processor):
    def __init__(self):
        self.buf = None
    def process(self):
        while True:
            try:
                if self.buf==None:
                    self.buf = self.in_.popleft()
                self.out_.append(self.buf + self.in_.popleft())
                #print("Appending {}".format(self.out_[-1]))
                self.buf = None
            except IndexError:
                raise NoData

class Map(Processor):
    '''Transform a true function into a processor'''
    def __init__(self, fn):
        self.fn = fn
    def process(self):
        try:
            while True:
                e = self.in_.popleft()
                #print("Appending {}".format(self.fn(e)))
                self.out_.append(self.fn(e))
        except IndexError:
            raise NoData
    def __repr__(self):
        return '<Map: {}>'.format(repr(self.fn))

class Filter(Processor):
    '''Transform a true function into a processor'''
    def __init__(self, fn):
        self.fn = fn
    def process(self):
        try:
            while True:
                e = self.in_.popleft()
                if self.fn(e):
                    #print("Appending {}".format(e))
                    self.out_.append(e)
        except IndexError:
            raise NoData
    def __repr__(self):
        return '<Filter: {}>'.format(repr(self.fn))

class Reduce(Processor):
    '''Transform a true function into a processor'''
    def __init__(self, fn):
        self.fn = fn
        self.cur = None
    def process(self):
        try:
            self.cur = self.in_.popleft()
            try:
                while True:
                    e = self.in_.popleft()
                    self.cur = self.fn(self.cur, e)
            except IndexError:
                #print("Appending {}".format(self.cur))
                self.out_.append(self.cur)
                raise NoData
        except IndexError:
            raise NoData
    def __repr__(self):
        return '<Reduce: {}>'.format(repr(self.fn))

class UserInput(Processor):
    '''Get numbers from user'''
    def process(self):
        #ignore input
        i = input("Enter some numbers seperated by spaces: ")
        if len(i) < 2:
            raise NoData
        self.out_.extend(map(int,i.split(" ")))

if __name__ == '__main__':
    mypipe = UserInput() >> Filter(lambda x: x%2==0) >> Map(str) >> Reduce(lambda x, y: x+y) >> Map(int)
    for res in mypipe():
        print(res)

    mypipe = range(100) >> AddTwo() >> Filter(lambda x: (x+1)%10==0) >> AddTwo() >> Map(str) >> Reduce(lambda x, y: x+y) >> Map(int)
    for res in mypipe():
        print(res)

    '''
    #More practical example:

    mypipe = LineReader(filename="my_big_file.txt", yield_after=10) >> Transform(lowercase=True) >> Tokenizer() >> CountWords()

    words = dict(mypipe())
    '''
