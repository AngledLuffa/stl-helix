import contextlib
import io
import sys

from test_generations import TESTS

def rebuild(filename):
    for test in TESTS:
        if test.gold_file == filename or test.gold_file.split("/")[-1] == filename:
            print("Rebuilding %s" % test.gold_file)
            args = ['--output_name', test.gold_file] + test.args
            test.model.main(args)
            

def main():
    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            rebuild(filename)
    else:
        for test in TESTS:
            print("Rebuilding %s" % test.gold_file)
            args = ['--output_name', test.gold_file] + test.args
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                test.model.main(args)

if __name__ == '__main__':
    main()
