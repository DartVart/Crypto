from typing import Tuple
from collections import Counter

from src.des.utils.feistel_cipher import feistel_encrypt, feistel_decrypt
from src.des.config import (
    APPENDED_LETTER,
    IP_PERMUTATION,
    EXTENSION_TABLE,
    BASIC_CONVERSION_TABLES,
    FINAL_DES_FUNCTION_PERMUTATION,
    REVERSE_IP_PERMUTATION,
    INITIAL_KEY_PERMUTATION,
    ROUND_KEYS_SHIFTS,
    FINAL_KEY_PERMUTATION,
)

# Permutation length can be different from the length of the string.
from src.utils.encodings_processing import (
    add_parity_bits,
    xor_string,
    number_to_binary_str,
    to_binary,
    binary_to_hex,
    hex_to_binary,
    from_binary,
)
from src.utils.std_stream import (
    input_hex,
    check_encryption_algorithm_with_user,
    InputStringHandlerTypes,
    get_hex_to_display,
)
from src.utils.strinig_processing import shift_string, chunk_str, pad_string_to_multiple_of_length


def permute(string, permutation: Tuple, bias=-1):
    len(string)
    return "".join([string[i + bias] for i in permutation])


def get_parity_bit(chunk):
    counter = Counter()
    counter.update(list(chunk))
    new_symbol = str(1 - counter["1"] % 2)
    return new_symbol


def get_round_keys(binary_key, initial_key_permutation, round_keys_shifts, final_key_permutation):
    round_keys = []
    key_with_parity_bits = add_parity_bits(binary_key, get_parity_bit)
    permuted_key = permute(key_with_parity_bits, initial_key_permutation, -1)

    center_index = len(permuted_key) // 2
    c = permuted_key[:center_index]
    d = permuted_key[center_index:]
    for shift_value in round_keys_shifts:
        c = shift_string(c, shift_value)
        d = shift_string(d, shift_value)
        round_keys.append(permute(c + d, final_key_permutation))
    return round_keys


def get_des_feistel_func(extension_table, basic_conversion_table, final_permutation_table):
    def des_feistel_func(binary_string, key):
        cipher_string = permute(binary_string, extension_table)
        chunks = chunk_str(xor_string(cipher_string, key), len(cipher_string) // 8)
        after_basic_conversion = ""
        for i, chunk in enumerate(chunks):
            row = int(chunk[0] + chunk[-1], 2)
            column = int(chunk[1:-1], 2)
            after_basic_conversion += number_to_binary_str(basic_conversion_table[i][row][column], 4)
        return permute(after_basic_conversion, final_permutation_table)

    return des_feistel_func


def apply_des_cipher(
    binary_text,
    binary_key,
    ip_permutation,
    extension_table,
    basic_conversion_table,
    final_permutation_table,
    initial_key_permutation,
    round_keys_shifts,
    final_key_permutation,
    reverse_ip_permutation,
    encrypt=True,
):
    keys = get_round_keys(binary_key, initial_key_permutation, round_keys_shifts, final_key_permutation)
    binary_codes = chunk_str(binary_text, 64)
    for code in binary_codes:
        cipher_text = permute(code, ip_permutation)
        func = feistel_encrypt if encrypt else feistel_decrypt
        cipher_text = func(
            cipher_text, keys, get_des_feistel_func(extension_table, basic_conversion_table, final_permutation_table)
        )
        yield permute(cipher_text, reverse_ip_permutation)


def des_encrypt(ascii_text, hex_key):
    binary_text = to_binary(pad_string_to_multiple_of_length(ascii_text, 8, APPENDED_LETTER))
    return get_hex_to_display(
        binary_to_hex(
            "".join(
                apply_des_cipher(
                    binary_text,
                    hex_to_binary(hex_key.replace(" ", "")),
                    IP_PERMUTATION,
                    EXTENSION_TABLE,
                    BASIC_CONVERSION_TABLES,
                    FINAL_DES_FUNCTION_PERMUTATION,
                    INITIAL_KEY_PERMUTATION,
                    ROUND_KEYS_SHIFTS,
                    FINAL_KEY_PERMUTATION,
                    REVERSE_IP_PERMUTATION,
                )
            )
        )
    )


def des_decrypt(hex_text, hex_key):
    binary_result = "".join(
        apply_des_cipher(
            hex_to_binary(hex_text),
            hex_to_binary(hex_key.replace(" ", "")),
            IP_PERMUTATION,
            EXTENSION_TABLE,
            BASIC_CONVERSION_TABLES,
            FINAL_DES_FUNCTION_PERMUTATION,
            INITIAL_KEY_PERMUTATION,
            ROUND_KEYS_SHIFTS,
            FINAL_KEY_PERMUTATION,
            REVERSE_IP_PERMUTATION,
            encrypt=False,
        )
    )
    return from_binary(binary_result, APPENDED_LETTER)


if __name__ == "__main__":
    # Examples:
    # key: 'ac 43 d5 e3 ba f1 8e'
    # text: 'What's up guys?'
    check_encryption_algorithm_with_user("DES", 14, des_encrypt, des_decrypt, InputStringHandlerTypes.ASCII)
