import contextlib
import io

from test_generations import TESTS

def main():
    for test in TESTS:
        print("Rebuilding %s" % test.gold_file)
        args = ['--output_name', test.gold_file] + test.args
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            test.model.main(args)

if __name__ == '__main__':
    main()
