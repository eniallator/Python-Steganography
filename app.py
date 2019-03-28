from sys import argv
from PIL import Image
import numpy as np


def add_bin(num, lst):
    curr_bin = []
    while num > 0:
        curr_bin.append(num % 2)
        num = num // 2
    for i in range(7, -1, -1):
        if len(curr_bin) > i:
            lst.append(curr_bin[i])
        else:
            lst.append(0)


def file_to_binary(path):
    binary = []
    with open(path, 'rb') as file_handle:
        file_handle
        file_bytes = file_handle.read()
        for b in file_bytes:
            add_bin(b, binary)
    return binary


def encode_bitmap(path, bitmap):
    file_binary = file_to_binary(path)


def main():
    if len(argv) < 4:
        raise Exception('Needs 3 params')

    img_input = argv[1]
    file_to_encode = argv[2]
    img_output = argv[3]

    img = Image.open(img_input)
    bitmap = np.asarray(img)

    encode_bitmap(file_to_encode, bitmap)


if __name__ == '__main__':
    main()
