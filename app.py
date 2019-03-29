from sys import argv
from math import ceil
from PIL import Image
import numpy as np


HEADER_BIN_INTERVAL = 15


def dec_to_bin(num):
    bin_num = []
    while num > 0:
        bin_num.append(num % 2)
        num = num // 2

    return bin_num


def lengthen_bin(bin_num, length):
    return [bin_num[i] if i < len(bin_num) else 0 for i in range(length)]


def file_to_binary(path):
    binary = []
    with open(path, 'rb') as file_handle:
        file_handle
        file_bytes = file_handle.read()
        for b in file_bytes:
            binary += lengthen_bin(dec_to_bin(b), 8)
    return binary


def create_header_bin(num):
    bin_num = dec_to_bin(num)
    print(bin_num)
    working_bin = lengthen_bin(bin_num, ceil(len(bin_num) / HEADER_BIN_INTERVAL) * HEADER_BIN_INTERVAL)
    print(ceil(len(bin_num) / HEADER_BIN_INTERVAL) * HEADER_BIN_INTERVAL, len(working_bin), working_bin)
    header_bin = []
    for i in range(ceil(len(working_bin) / HEADER_BIN_INTERVAL)):
        if header_bin != []:
            header_bin.append(1)
        header_bin += working_bin[i * HEADER_BIN_INTERVAL: (i + 1) * HEADER_BIN_INTERVAL]
    header_bin.append(0)
    return header_bin


def encode_bitmap(path, bitmap):
    file_binary = file_to_binary(path)
    num_bytes = len(file_binary) // 8
    header_bin = create_header_bin(num_bytes)
    print(header_bin, num_bytes)


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
