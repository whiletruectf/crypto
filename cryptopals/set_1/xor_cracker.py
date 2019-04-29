from itertools import combinations
from base64 import b64decode
import sys, string, base64

letter_frequency = {
    'a': 0.0651738, 'b': 0.0124248, 'c': 0.0217339, 'd': 0.0349835, 'e': 0.1041442, 'f': 0.0197881, 'g': 0.0158610,
    'h': 0.0492888, 'i': 0.0558094, 'j': 0.0009033, 'k': 0.0050529, 'l': 0.0331490, 'm': 0.0202124, 'n': 0.0564513,
    'o': 0.0596302, 'p': 0.0137645, 'q': 0.0008606, 'r': 0.0497563, 's': 0.0515760, 't': 0.0729357, 'u': 0.0225134,
    'v': 0.0082903, 'w': 0.0171272, 'x': 0.0013692, 'y': 0.0145984, 'z': 0.0007836, ' ': 0.1918182
}

def hamming_dist(str1, str2):
    assert (len(str1) == len(str2)), "Lengths of strings must be equal"
    dist = 0

    for bit1, bit2 in zip(str1, str2):
        diff = bin(ord(bit1) ^ ord(bit2))
        dist += diff.count('1')

    return dist

def find_keysize(cipher, answers):
    assert (answers <= len(cipher)), "Number of answers must be less than or equal to the length of the cipher"
    map = {}
    for i in range(2, 40):
        blocks = []
        blocks.append(cipher[:i])
        blocks.append(cipher[i:i*2])
        blocks.append(cipher[i*2:i*3])
        blocks.append(cipher[i*3:i*4])
        block_combinations = tuple(combinations(blocks, 2))
        dist = 0.0
        for str1, str2 in block_combinations:
            dist += hamming_dist(str1, str2)
        dist /= 6.0
        normalized_dist = dist / i
        map[i] = normalized_dist

    sorted_distances = sorted(map, key=map.get)[:answers]
    return sorted_distances

def compute_english_score(str):
    distance = 0.0
    for letter in str:
        distance += letter_frequency.get(letter.lower(), 0)
    return distance

def wrap_text(str, width):
    text = []
    for i in range(0, len(str), width):
        j = i
        block = ''
        while j < len(str) and j < i + width:
            block += str[j]
            j += 1
        text.append(block)
    return text

def transpose(str, key_size):
    wrapped_text = wrap_text(str, key_size)
    transposed_text = []
    for i in range(key_size):
        transposed_text.append(' ')
    for block in wrapped_text:
        for i in range(len(block)):
            transposed_text[i] += block[i]
    return transposed_text

def decrypt_block(block, key):
    result = ''
    key = ord(key)
    for c in block:
        result += chr(ord(c) ^ key)
    return result

def solve_block(block):
    key = ''
    closeness = 0.0
    for i in range(256):
        c = chr(i)
        guess = decrypt_block(block, c)
        value = compute_english_score(guess)
        if value > closeness:
            closeness = value
            key = c
    return key

def guess_keys(cipher, answers):
    key_sizes = find_keysize(cipher, answers)
    possible_keys = []
    for key_size in key_sizes:
        transposed_text = transpose(cipher, key_size)
        key = ''
        for block in transposed_text:
            key += solve_block(block)
        possible_keys.append(key)
    return possible_keys

def decrypt_cipher(cipher, key):
    result = ''
    for i in range(len(cipher)):
        result += chr(ord(cipher[i]) ^ ord(key[i % len(key)]))
    return result

def crack_cipher(cipher, answers = 1):
    keys = guess_keys(cipher, answers)
    dict_score = {}
    dict_text = {}
    for key in keys:
        text = decrypt_cipher(cipher, key)
        score = compute_english_score(text)
        dict_score[key] = score
        dict_text[key] = text
    sorted_dict_score = sorted(dict_score, key=dict_score.get)

    results = []
    for i in range(answers):
        results.append(sorted_dict_score[len(sorted_dict_score) - i - 1])
    chance = {}

    total = sum(value for value in dict_score.values())
    for key in results:
        chance[key] = dict_score[key] / total
    return {
        'keys' : results,
        'scores' : dict_score,
        'text' : dict_text,
        'chance' : chance
    }

def main():
    with open(sys.argv[1]) as f:
        for line in f:
            cipher = b64decode(f.read()).decode('ascii')
    results = crack_cipher(cipher, int(sys.argv[2]))
    print(results['text'][results['keys'][0]])

if __name__ == '__main__':
    main()