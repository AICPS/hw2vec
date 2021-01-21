from optparse import OptionParser
import os

def main(filename):
    f = open(filename, 'r')
    s = f.read().replace('_', '')
    f.close()
    f = open(filename, 'w')
    f.write(s)
    f.close()

if __name__ == '__main__':
    optparser = OptionParser()
    (options, args) = optparser.parse_args()

    if len(args) == 0:
        print('\nUSAGE: python removeUnderscores.py FILENAMES\n')
    else:
        for fil in args:
            if not os.path.exists(fil):
                raise IOError("file not found: " + args[0])
        for fil in args:
            main(fil)