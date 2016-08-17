from collections import deque

class NoData(Exception):
    pass

class Drain(Exception):
    pass

class Pipe(object):
    '''Generic pipe object. Add functions to put items in the pipe or something.'''
    def __init__(self, debug=False):
        self.processors = deque()
        self.first = None
        self.last = None
        self.debug = debug
    def __rshift__(self, something):
        '''We assume that something is a processor.
        If not, we can fail. Usage:
        pipe >> something'''
        something.drain = False
        self.processors.append(something)
        return self
    def __matmul__(self, something):
        '''Same as rshift, except: Set something to buffer.'''
        something.drain = True
        self.processors.append(something)
        return self
    def __rrshift__(self, data):
        '''Not sure if we want this. This would mean:
        [1,2,3] >> mypipe >> foo("bar")
        or similar. Could only be done once, I guess?'''
        if self.debug: print("Adding input data: {}".format(repr(data)))
        # If we give it a deque already, we use it and modify, otherwise copy
        if isinstance(data, deque):
            self.first = data
        else:
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
            try:
                for i, proc in enumerate(self.processors):
                    if proc.drain and i != 0:
                        # start the while loop again. so break but nobreak?
                        raise Drain
                    try:
                        proc.process()
                    except NoData:
                        if i == 0: #first generator?
                            print("Was first generator")
                            break
                        else:
                            print("Wasn't first generator")
                            continue # go to next processor
                else: #nobreak
                    continue #start from the beginning again
            except Drain:
                continue
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
        '''You're not supposed to redefine this'''
        self.in_ = in_
        self.out_ = deque()
        return self.out_
    def process(self):
        '''Do something with input, into output. If empty, raise NoData.
        Subclasses of Processor should define this method, because otherwise,
        they do nothing. Make sure to popleft from in_, and to append to out_'''
        pass
    def pull(self):
        '''Abstraction of popping left from input'''
        try:
            return self.in_.popleft()
        except IndexError:
            raise NoData
    def push(self, data):
        '''Abstraction of appending to output'''
        self.out_.append(data)
    def pushfrom(self, data):
        '''Appending from iterable'''
        for thing in data:
            self.push(thing)
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
    def __init__(self, debug=False):
        self.buf = None
        self.debug = debug
    def process(self):
        while True:
            if self.buf==None:
                self.buf = self.pull()
            self.push(self.buf + self.pull())
            if self.debug: print("Appending {}".format(self.out_[-1]))
            self.buf = None

class Map(Processor):
    '''Transform a true function into a processor'''
    def __init__(self, fn, debug=False):
        self.fn = fn
        self.debug = debug
    def process(self):
        while True:
            e = self.pull()
            if self.debug: print("Appending {}".format(e))
            self.push(self.fn(e))
    def __repr__(self):
        return '<Map: {}>'.format(repr(self.fn))

class Filter(Processor):
    '''Transform a true function into a processor'''
    def __init__(self, fn, debug=False):
        self.fn = fn
        self.debug = debug
    def process(self):
        while True:
            e = self.pull()
            if self.fn(e):
                if self.debug: print("Appending {}".format(e))
                self.push(e)
    def __repr__(self):
        return '<Filter: {}>'.format(repr(self.fn))

class Reduce(Processor):
    '''Transform a true function into a processor'''
    def __init__(self, fn, start=None, debug=False):
        self.fn = fn
        self.cur = None
        self.start = start
        self.debug = debug
    def process(self):
        print(self.cur)
        if self.start == None:
            self.cur = self.pull()
        else:
            self.cur = self.start
        try:
            while True:
                e = self.pull()
                if self.debug: print("Pulled {}".format(e))
                self.cur = self.fn(self.cur, e)
        except NoData:
            if self.debug: print("Appending {}".format(self.cur))
            self.push(self.cur)
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
        self.pushfrom(map(int, i.split(" ")))

class Bufferer(Processor):
    def __init__(self, number):
        self.number = number
    def process(self):
        buffr = []
        try:
            for i in range(self.number):
                buffr.append(self.pull())
                #print(buffr)
            for e in buffr:
                self.push(e)
        except NoData:
            for e in buffr:
                self.push(e)
            raise NoData

class Printer(Processor):
    def process(self):
        print("Printing:")
        while True:
            e = self.pull()
            print(e)
            self.push(e)

if __name__ == '__main__':
    '''
    mypipe = UserInput() >> Filter(lambda x: x%2==0) >> Map(str) >> Reduce(lambda x, y: x+y) >> Map(int)
    for res in mypipe():
        print(res)
    '''

    #mypipe = range(100) >> AddTwo() >> Filter(lambda x: (x+1)%10==0) >> AddTwo() >> Map(str) >> Reduce(lambda x, y: x+y) >> Map(int)
    mypipe = (range(100) >> Bufferer(10)) >> Printer() >> Reduce(lambda x,y: x+y)
    print(mypipe)
    print(mypipe.processors)
    input()
    for res in mypipe(debug=True):
        print(res)

    '''
    #More practical example:

    mypipe = LineReader(filename="my_big_file.txt", yield_after=10) >> Transform(lowercase=True) >> Tokenizer() >> CountWords()

    words = dict(mypipe())
    '''
    #if we want some part to block, we could do:
    #mypipe = (Something() >> Somethong() >> Foo())() >> Bar() >> Bat()
    # but that would execute the first part here already... hmm
    # other option would be to declare processors blocking... could also use a different operator then?
    #mypipe = Something() >> Somethong() >> Foo() @ Bar() >> Bat()
