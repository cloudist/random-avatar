import sys


def main():
    print 'colors = ['

    for line in sys.stdin:
        parts = line.split('itemer')
        for part in parts:
            if part[0] == '(':
                p = part.index(',') + 3
                print '\'%s\',' % part[p : p + 24]

    print ']'

if __name__ == '__main__':
    main()
