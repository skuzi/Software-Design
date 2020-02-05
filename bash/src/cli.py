from interpreter import execute_pipeline


def main():
    while True:
        print('$ ', end='')
        output = execute_pipeline(input())
        if output is None:
            break
        print(output)


if __name__ == '__main__':
    main()