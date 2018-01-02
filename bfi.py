#!/usr/bin/env python
from __future__ import print_function
import sys
import argparse

class Runner:

    arr = []
    ptr = 0

    def __init__(self, arrsize=100):
        global ptr
        global arr
        arr = [0 for i in range(arrsize)]
        ptr = 0

    def run(self, cmd, debug=False, use_byte_range=False):
        if not _validate(cmd):
            raise BracketsMismatch('check \'[\' and \']\' must not overlap and match')
        global ptr
        c = 0
        while c < len(cmd):
            if cmd[c] == '>':
                ptr += 1
            elif cmd[c] == '<':
                ptr -= 1
            elif cmd[c] == '+':
                arr[ptr] += 1
            elif cmd[c] == '-':
                arr[ptr] -= 1
            elif cmd[c] == '.':
                print(chr(arr[ptr]), end='')
            elif cmd[c] == ',':
                arr[ptr] = ord(sys.stdin.read(1))
            elif cmd[c] == '[':
                if arr[ptr] == 0:
                    # goto next matching ']'
                    check = 1
                    while cmd[c] != ']' or check != 0:
                        c += 1
                        if cmd[c] == '[':
                            check += 1
                        elif cmd[c] == ']':
                            check -= 1
            elif cmd[c] == ']':
                if arr[ptr] != 0:
                    # goto previous matching '['
                    check = 1
                    while cmd[c] != '[' or check != 0:
                        c -= 1
                        if cmd[c] == '[':
                            check -=1
                        elif cmd[c] == ']':
                            check += 1

            if debug:
                if cmd[c] == '.':
                    print()
                if cmd[c] in '><+-.,[]':
                    print(cmd[c], c, ptr, arr[ptr])
            c += 1  # move to next character

            # checking
            if ptr < 0:
                raise NegativePointer('pointer must be non negative integer')
            if ptr >= len(arr):
                raise PointerOutOfRange('pointer exceeds length of array')
            if use_byte_range:
                if arr[ptr] < 0 or arr[ptr] > 255:
                    raise ValueOutOfBound('value for each cell must between 0 and 255')

    def run_multiline(self, cmd, debug=False, use_byte_range=False):
        strcmd = ''
        for c in cmd:
            strcmd = strcmd + c
        self.run(strcmd, debug=debug, use_byte_range=use_byte_range)

    def get_arr(self):
        return arr

    def get_ptr(self):
        return ptr

    def run_file(self, filepath, debug=False, use_byte_range=False):
        cmd = []
        with open(filepath, 'r') as fl:
            for line in fl:
                cmd.append(line)
        self.run_multiline(cmd, debug=debug, use_byte_range=use_byte_range)


def _validate(strcmd):
    check = 0
    valid = True
    for i in strcmd:
        if i == '[':
            check += 1
        elif i == ']':
            check -= 1
        if check < 0:
            valid = False
            break
    if check != 0:
        valid = False
    return valid


class BracketsMismatch(Exception):
    pass


class NegativePointer(Exception):
    pass


class ValueOutOfBound(Exception):
    pass


class PointerOutOfRange(Exception):
    pass


if __name__ == '__main__':
    # b = Runner(arrsize=3)
    # b.run('++++[a>+++[b>+<-]<-]', debug=True)
    DEFAULT_ARRSIZE = 100
    parser = argparse.ArgumentParser(description='brainfuck intepreter')
    parser.add_argument('-a', metavar='arraysize', help='array size (default 100)', default=DEFAULT_ARRSIZE, type=int)
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', help='enable debug mode')
    parser.add_argument('-f', metavar='filename', type=str, default='', help='run from file then exit')
    parser.set_defaults(debug=False)
    args = parser.parse_args()
    size = args.a
    debug = args.debug

    fl = args.f

    b = Runner(arrsize=size)
    # print('brainfuck intepreter')
    # print('type help for list of available commands')

    repeat = True

    if fl != '':
        lines = []
        with open(fl, 'r') as f:
            for l in f:
                lines.append(l)
        b.run_multiline(lines, debug=debug)
        repeat = False

    while(repeat):
        try:
            cmd = input(':: ')
        except KeyboardInterrupt:
            cmd = 'exit'
            print()
        if cmd == 'help':
            print(
                '[brainfuck interpreter]\n' +
                'help\t\tshow this help\n' +
                'reset\t\treset session\n' +
                'load <file>\trun command from file\n' +
                'debug\t\ttoggle debug mode (cmd cmd_position pointer value_at_pointer)\n' +
                'array\t\tprint array to screen\n' +
                'exit\t\tterminate session')
        elif cmd == 'exit':
            print('\nbye!')
            repeat = False
        elif cmd == 'reset':
            b = Runner(arrsize=size)
            print('session reset')
        elif cmd.startswith('load'):
            filename = ' '.join(cmd.split(' ')[1:])
            tmp = []
            try:
                with open(filename, 'r') as f:
                    for l in f:
                        tmp.append(l)
                b.run_multiline(tmp, debug=debug)
            except FileNotFoundError as ex:
                print(ex)
        elif cmd == 'debug':
            debug = not debug
            print('debug mode', debug)
        elif cmd == 'array':
            print(arr)
        else:
            try:
                b.run(cmd, debug=debug)
            except BracketsMismatch as ex:
                print(ex)
            except NegativePointer as ex:
                print(ex)
            except PointerOutOfRange as ex:
                print(ex)
            except Exception as ex:
                print(ex)
