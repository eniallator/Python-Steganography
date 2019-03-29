from sys import argv
from math import ceil
from PIL import Image


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


def modify_pixel(in_pixel, data):
    out_pixel = []
    for i, channel in enumerate(in_pixel):
        channel_bits = lengthen_bin(dec_to_bin(channel), 8)
        for j in range(len(data[i])):
            channel_bits[j] = data[i][j]
        out_pixel.append(bin_to_dec(channel_bits))
    return tuple(out_pixel)


def replace_bitmap_data(bitmap, data, bits_to_take):
    btt_bin = lengthen_bin(dec_to_bin(bits_to_take), 3)
    bitmap[0] = modify_pixel(bitmap[0], [[bit] for bit in btt_bin])

    data_index = 0
    for i in range(1, len(bitmap)):
        if data_index >= len(data):
            return
        data_bits = []
        for i in range(bitmap[i]):
            data_bits.append(data[data_index: data_index + bits_to_take])
            data_index += bits_to_take
        bitmap[i] = modify_pixel(bitmap[i], data_bits)


def encode_bitmap(path, bitmap):
    file_binary = file_to_binary(path)
    num_bytes = len(file_binary) // 8
    header_bin = create_header_bin(num_bytes)
    data = header_bin + file_binary

    bits_to_take = ceil(len(data) / (len(bitmap) - 1))
    if bits_to_take > 8:
        raise Exception('Data too big for image bitmap')

    replace_bitmap_data(bitmap, data, bits_to_take)


def save_bitmap(old_img, bitmap, img_output):
    new_img = Image.new(old_img.mode, old_img.size)
    new_img.putdata(bitmap)
    new_img.save(img_output)


def encode(img_input, file_to_encode, img_output):
    img = Image.open(img_input)
    bitmap = list(img.getdata())

    encode_bitmap(file_to_encode, bitmap)
    save_bitmap(img, bitmap, img_output)

    img = Image.open(img_input)
    bitmap = list(img.getdata())

    file_to_bitmap(file_to_encode, bitmap)
    save_bitmap(img, bitmap, img_output)


if __name__ == '__main__':
    args = argv[1:]
    if len(args) == 3:
        encode(*args)
    else:
        raise Exception("Wrong usage.")
