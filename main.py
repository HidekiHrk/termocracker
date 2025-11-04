import random
import itertools
import unicodedata
import re
from typing import List

WORD_RE = r'(_|\w){5}'
AVAILABLE_LETTERS_RE = r'\w+'

class TermoCrackerError(Exception):
    pass

def normalize(text: str) -> str:
    normalized_text = unicodedata.normalize('NFKD', text)
    
    return "".join([
        c for c in normalized_text if not unicodedata.combining(c)
    ])
    

sentence_list_dict = [None] * 5

def get_sentence_list(word: str):
    for first_letter_index in range(len(word)):
        if word[first_letter_index] != '_':
            break
    
    if sentence_list_dict[first_letter_index] is None:
        sentence_list_dict[first_letter_index] = []
        with open('./palavrasnormalizadas{}.txt'.format(f"_{first_letter_index}" if first_letter_index > 0 else ''), 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            item = line.strip()
            sentence_list_dict[first_letter_index].append(item)
            yield item
    else:
        for line in sentence_list_dict[first_letter_index]:
            yield line
    

def iterate_through_string(text: str):
    for i in text:
        yield i

def get_missing_letter_count(word: str):
    result = 0
    for i in word:
        if i == '_':
            result += 1
    return result

def get_word_combinations(word: str, available_letters: List[str]):
    missing_count = get_missing_letter_count(word)
    current_word = word.replace('_', '{}')
    
    for permutation in itertools.product(available_letters, repeat=missing_count):
        yield current_word.format(*permutation)

def have_index(arr: list, index: int):
    try:
        arr[index]
        return True
    except IndexError:
        return False

def binary_search(text: str, text_list: List[str], current_index=0):
    if current_index >= len(text) or text[current_index] is None:
        return text_list
    elif text[current_index] == '_':
        return binary_search(text, text_list, current_index=current_index+1)
    elif not have_index(text_list, 1):
        if len(text_list) == 1 and text[current_index] == text_list[0][current_index]:
           return text_list 
        return []
    letter = text[current_index]
    size = len(text_list)
    middle = size // 2
    left = text_list[:middle]
    left = binary_search(text, left, current_index=current_index) if have_index(left, -1) and ord(letter) <= ord(left[-1][current_index]) else []
    right = text_list[middle:]
    right = binary_search(text, right, current_index=current_index) if have_index(right, 0) and ord(letter) >= ord(right[0][current_index]) else []
    return binary_search(text, [*left, *right], current_index=current_index+1)
    
def filter_for_mislocated_letters(word_list: List[str], mislocated_letters: List[str]):
    new_list = []
    for word in word_list:
        is_invalid = False
        for mislocation in mislocated_letters:
            if is_invalid:
                break
            for i in range(len(mislocation)):
                mislocated = mislocation[i]
                if mislocated == '_':
                    continue
                if mislocated not in word or word[i] == mislocated:
                    is_invalid = True
                    break
        if not is_invalid:
            new_list.append(word)
    return new_list

def print_data(data: dict):
    print("""Data:
\tWord: {word}
\tMislocated Letters: {mislocated_letters}
\tAvailable Letters: {available_letters}
""".format(**data))

def add_mislocated(data: dict, *args):
    if not re.match(WORD_RE, args[0]):
        raise TermoCrackerError(f"Pattern not attended by {args[0]}")

    data['mislocated_letters'].append(args[0].upper())

def set_mislocated(data: dict, *args):
    data['mislocated_letters'] = []
    for arg in args:
        add_mislocated(data, arg)

def set_available(data: dict, *args):
    if not re.match(AVAILABLE_LETTERS_RE, args[0].strip()):
        raise TermoCrackerError(f"Pattern not attended by {args[0]}")

    data['available_letters'] = args[0].strip().upper()

def set_word(data: dict, *args):        
    if not re.match(WORD_RE, args[0].strip()):
        raise TermoCrackerError(f"Pattern not attended by {args[0]}")
    
    data['word'] = args[0].strip().upper()

def clear(data: dict):
    new_data = {
        "word": "",
        "mislocated_letters": [],
        "available_letters": ""
    }
    
    for k, v in new_data.items():
        data[k] = v

def get_help(*args):
    print("""Help:
\thelp - Shows this message.
\texit - Exits the system.
\tword - Sets the incomplete word. Missing spaces are represented by '_'. Example: > word C_R_O
\taddmis - Adds a mislocated letter config. Missing spaces are represented by '_'. Example: > addmis _R_A_
\tsetmis - Set all mislocated letter configs. Missing spaces are represented by '_'. Example: > setmis _R___ ___A_
\tsetavailable - Set all available letters. Example: > setavailable ABCDEFGHIJKLMNOPQRSTUVWXYZ
\tsearch - Searches all possible matches and prints out on the shell.
\tdata - Prints out all info the system have about the guess.
\tclear - Clear the system for another guess.
""")
        
def search(data: dict):
    word = data['word']
    discovered_mislocated_letters = data['mislocated_letters']
    available_letters = [*iterate_through_string(data['available_letters'])]
    if not re.match(WORD_RE, word) or not all(map(lambda x: re.match(WORD_RE, x), discovered_mislocated_letters)) or not re.match(AVAILABLE_LETTERS_RE, data['available_letters']):
        raise TermoCrackerError("System not fullfilled.")
    sentence_list = [*get_sentence_list(word)]
    possible = binary_search(word, sentence_list)
    possible_combinations = []
    for combination in get_word_combinations(word, available_letters):
        if combination in possible:
            possible_combinations.append(combination)
    filtered_combinations = filter_for_mislocated_letters(possible_combinations, discovered_mislocated_letters)
    print(filtered_combinations)

def cli():
    data = {
        "word": "",
        "mislocated_letters": [],
        "available_letters": ""
    }
    command_list = {
        'help': get_help,
        'word': lambda *args: set_word(data, *args),
        'addmis': lambda *args: add_mislocated(data, *args),
        'setmis': lambda *args: set_mislocated(data, *args),
        'setavailable': lambda *args: set_available(data, *args),
        'search': lambda: search(data),
        'data': lambda: print_data(data),
        'clear': lambda: clear(data)
    }
    while True:
        command_text = input('> ').strip()
        arguments = command_text.split(' ')
        
        if arguments[0] == 'exit':
            break
                
        try:
            command_function = command_list[arguments[0]]
            command_function(*arguments[1:])
        except KeyError:
            print(f"Comando '{arguments[0]}' inexistente")
        except TermoCrackerError as e:
            print(f"Erro do sistema: {e}")
        
        

def main():
    cli()
    
if __name__ == '__main__':
    main()