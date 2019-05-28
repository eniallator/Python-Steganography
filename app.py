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


def resize_bin(bin_num, length):
    return [bin_num[i] if i < len(bin_num) else 0 for i in range(length)]


def file_to_binary(path):
    binary = []
    with open(path, 'rb') as file_handle:
        file_handle
        file_bytes = file_handle.read()
        for b in file_bytes:
            binary += resize_bin(dec_to_bin(b), 8)
    return binary


def create_header_bin(num):
    bin_num = dec_to_bin(num)
    working_bin = resize_bin(bin_num, ceil(len(bin_num) / HEADER_BIN_INTERVAL) * HEADER_BIN_INTERVAL)
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
        channel_bits = resize_bin(dec_to_bin(channel), 8)
        for j in range(len(data[i])):
            channel_bits[j] = data[i][j]
        out_pixel.append(bin_to_dec(channel_bits))
    return tuple(out_pixel)


def replace_bitmap_data(bitmap, data, bits_to_take):
    btt_bin = resize_bin(dec_to_bin(bits_to_take - 1), 3)
    bitmap[0] = modify_pixel(bitmap[0], [[bit] for bit in btt_bin])

    data_index = 0
    for i in range(1, len(bitmap)):
        if data_index >= len(data):
            return
        data_bits = []
        for j in range(len(bitmap[i])):
            data_bits.append(data[data_index: data_index + bits_to_take])
            data_index += bits_to_take
        bitmap[i] = modify_pixel(bitmap[i], data_bits)


def encode_bitmap(path, bitmap):
    file_binary = file_to_binary(path)
    num_bytes = len(file_binary) // 8
    header_bin = create_header_bin(num_bytes)
    data = header_bin + file_binary
    print('Encoding ' + str(len(file_binary) // 8) + ' bytes')

    bits_to_take = ceil(len(data) / (len(bitmap) - 1))
    print('Allocating ' + str(bits_to_take) + ' bit' + ('s' if bits_to_take > 1 else '') + ' per byte in the image bitmap')
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


def get_bits_taken(pixel):
    bt_bin = []
    for channel in pixel:
        channel_bits = resize_bin(dec_to_bin(channel), 1)
        bt_bin.append(channel_bits[0])
    return bin_to_dec(bt_bin) + 1


def get_file_size(bitmap, bits_taken):
    size_bin = []
    abs_index = 0
    index = 1
    num_continues = True
    curr_bin = []
    while num_continues:
        for channel in bitmap[index]:
            next_bin = resize_bin(dec_to_bin(channel), bits_taken)
            to_take = len(next_bin) - len(curr_bin) + HEADER_BIN_INTERVAL + 1
            curr_bin += next_bin[:to_take]
            abs_index += min(to_take, bits_taken)
            if len(curr_bin) > HEADER_BIN_INTERVAL:
                size_bin += curr_bin[:-1]
                num_continues = curr_bin[-1] == 1
                curr_bin = []
                if not num_continues:
                    break
        index += 1
    file_size = bin_to_dec(size_bin)
    return (abs_index, file_size)


def get_file_data(bitmap, offset, file_size, bits_taken):
    pixel_data_bits = 3 * bits_taken
    index = offset // pixel_data_bits
    initial_offset = offset % pixel_data_bits
    curr_bin = []
    file_data = b''
    for i in range(ceil(offset / bits_taken / 3), len(bitmap)):
        pixel = bitmap[i]
        if initial_offset > pixel_data_bits:
            initial_offset -= pixel_data_bits
            continue
        for channel in pixel:
            if initial_offset > bits_taken:
                initial_offset -= bits_taken
                continue
            channel_bits = resize_bin(dec_to_bin(channel), bits_taken)
            if initial_offset > 0:
                curr_bin += channel_bits[initial_offset:]
                initial_offset = 0
            else:
                curr_bin += channel_bits
            if len(curr_bin) >= 8:
                file_data += chr(bin_to_dec(curr_bin[:8])).encode('utf-8')
                curr_bin = curr_bin[8:]

            if len(file_data) >= file_size:
                return file_data


def decode_bitmap(bitmap):
    bits_taken = get_bits_taken(bitmap[0])
    print('Found ' + str(bits_taken) + ' bits per byte in the image bitmap')
    offset, file_size = get_file_size(bitmap, bits_taken)
    print('Output file size will be ' + str(file_size) + ' bytes')
    return get_file_data(bitmap, offset, file_size, bits_taken)


def decode(img_input, file_output):
    img = Image.open(img_input)
    bitmap = list(img.getdata())
    file_data = decode_bitmap(bitmap)

    with open(file_output, 'wb') as file_handle:
        file_handle.write(file_data)


if __name__ == '__main__':
    args = argv[1:]
    if len(args) == 3:
        encode(*args)
    elif len(args) == 2:
        decode(*args)
    else:
        raise Exception("Wrong usage.")
