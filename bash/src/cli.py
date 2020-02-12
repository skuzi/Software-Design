from src.interpreter import execute_pipeline


def main():
    """Main program cycle. Expects for input until output of the given command is None"""
    while True:
        print('$ ', end='')
        output = execute_pipeline(input() + ' ')
        if output is None:
            break
        print(output)


if __name__ == '__main__':
    main()
