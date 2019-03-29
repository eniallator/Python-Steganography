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


def bin_to_dec(bin_num):
    dec = 0
    for i in range(len(bin_num)):
        if bin_num[i] == 1:
            dec += 2 ** i
    return dec


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
    working_bin = lengthen_bin(bin_num, ceil(len(bin_num) / HEADER_BIN_INTERVAL) * HEADER_BIN_INTERVAL)
    header_bin = []
    for i in range(ceil(len(working_bin) / HEADER_BIN_INTERVAL)):
        if header_bin != []:
            header_bin.append(1)
        header_bin += working_bin[i * HEADER_BIN_INTERVAL: (i + 1) * HEADER_BIN_INTERVAL]
    header_bin.append(0)
    return header_bin


def replace_bitmap_data(bitmap, data, bits_to_take):
    data_index = 0
    for row in bitmap:
        for pixel in row:
            for i in range(len(pixel)):
                channel = pixel[i]
                if data_index >= len(data):
                    return
                curr_bits = data[data_index: data_index + bits_to_take]
                channel_bits = lengthen_bin(dec_to_bin(channel), 8)
                for i in range(len(curr_bits)):
                    channel_bits[i] = curr_bits[i]
                pixel[i] = bin_to_dec(channel_bits)
                data_index += bits_to_take


def file_to_bitmap(path, bitmap):
    file_binary = file_to_binary(path)
    num_bytes = len(file_binary) // 8
    header_bin = create_header_bin(num_bytes)
    data = header_bin + file_binary

    bits_to_take = ceil(len(data) / bitmap.size)
    if bits_to_take > 8:
        raise Exception('Data too big for image bitmap')

    print(bitmap.flags)
    replace_bitmap_data(bitmap, data, bits_to_take)
    print(bitmap)


def main():
    if len(argv) < 4:
        raise Exception('Needs 3 params')

    img_input = argv[1]
    file_to_encode = argv[2]
    img_output = argv[3]

    img = Image.open(img_input)
    bitmap = np.asarray(img)

    file_to_bitmap(file_to_encode, bitmap)


if __name__ == '__main__':
    main()
