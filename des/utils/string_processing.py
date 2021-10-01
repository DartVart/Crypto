def chunk_str(text, chunk_length, appended_letter=None):
    if appended_letter is not None:
        number_of_last_letters = len(text) % chunk_length
        if number_of_last_letters != 0:
            text += appended_letter * (chunk_length - number_of_last_letters)
    return [text[i: i + chunk_length] for i in range(0, len(text), chunk_length)]


# left shift on 1 item: [1, 2, 3, 4] -> [2, 3, 4, 1]
def shift_string(string, shift_value, is_left_shift=True):
    shift_value = shift_value * (1 if is_left_shift else -1)
    return string[shift_value:] + string[:shift_value]