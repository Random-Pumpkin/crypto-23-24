#!/bin/python3

from collections import Counter
import sys

ALPHABET = "абвгдежзийклмнопрстуфхцчшщыьэюя"
M = len(ALPHABET)
FREQ_L = "оеа"
RARE_L = "щэф"
BIGRAMS = ["ст", "но", "то", "на", "ен"]

# Calculate gcd(a, b).
def euclid(a: int, b: int) -> list:
    # Initialize base values.
    u = [1, 0]
    v = [0, 1]
    a0, b0 = a, b
    if a > b:
        a, b = b, a
        u, v = v, u
        a0, b0 = b, a
    r = a % b
    q = [a // b]
    # Find gcd(a, b) and inverses.
    while a % b:
        a = b
        b = r
        r = a % b
        u.append(u[-2] - q[-1] * u[-1])
        v.append(v[-2] - q[-1] * v[-1])
        q.append(a // b)
    if u[-1] < 0:
        u[-1] += b0
    if v[-1] < 0:
        v[-1] += a0
    # Return [gcd(a, b), a^(-1), b^(-1)].
    return [b, u[-1], v[-1]]

# Solve a * x = b mod n.
def lin_cmp(a: int, b: int, n: int):
    lst = euclid(n, a)
    # Case gcd(a, n) == 1.
    if lst[0] == 1:
        return (lst[2] * b) % n
    # Case gcd(a, n) = d > 1 and b % d != 0.
    if b % lst[0] != 0:
        return 0
    # Case gcd(a, n) = d > 1 and b % d == 0. 
    else:
        a //= lst[0]
        b //= lst[0]
        n //= lst[0]
        x = (euclid(n, a)[2] * b) % n
        return [x + i * n for i in range(lst[0])]

# Count bigrams of a text.
def count_bigrams(text: str, overlap=False) -> dict:
    text_len = len(text)
    # Set step for text traversing.
    step = overlap + 1
    bigrams = [text[s:s + 2] for s in range(0, text_len - 1, step)]
    # Return bigrams sorted by their count.
    return dict(sorted(Counter(bigrams).items(), reverse=True, key=lambda item: item[1]))

# Encode letter or bigram.
def encode(ngram: str) -> int:
    if len(ngram) == 1:
        return ALPHABET.index(ngram)
    else:
        return ALPHABET.index(ngram[0]) * M + ALPHABET.index(ngram[1])

# Decode letter or bigram.
def decode(code) -> str:
    # Actual decoding function.
    def get_str(c: int) -> str: 
        if c < M:
            return ALPHABET[c]
        else:
            second = c % M
            first = c // M
            return f"{ALPHABET[first]}{ALPHABET[second]}"
            
    if isinstance(code, list):
        return ''.join([get_str(x) for x in code])
    else:
        return get_str(code)
    
# Decrypt ciphered text.
def decrypt(ct: str, key: tuple) -> str:
    pt = ''
    for i in range(0, len(ct), 2):
        pt = pt + decode(lin_cmp(key[0], encode(ct[i:i+2]) - key[1], M ** 2))
    return pt

# Find candidates for keys.
def find_keys(ct: str) -> list:
    keys = []
    ct_bigrams = list(count_bigrams(ct))
    # Loop through every possible combination of X*, X**, Y*, Y**.
    for i in ct_bigrams[:5]:
        ct_temp = [x for x in ct_bigrams[:5] if x != i]
        for j in ct_temp:
            for k in BIGRAMS:
                temp = [x for x in BIGRAMS if x != k]
                for l in temp:
                    a = lin_cmp(encode(k) - encode(l), encode(i) - encode(j), M ** 2)
                    if isinstance(a, list):
                        for n in a:
                            b = (encode(i) - n * encode(k)) % M ** 2
                            keys.append((n, b))
                    else:
                        b = (encode(i) - a * encode(k)) % M ** 2
                        keys.append((a, b))
    return keys

# Check if deciphered PT is sensible.
def sensible(pt: str) -> int:
    score = 0
    letters = list(dict(sorted(Counter(pt).items(), reverse=True, key=lambda item: item[1])))
    # Check the most frequent letters.
    for l in letters[:3]:
    	if l in FREQ_L:
            score += 1
    # Check the least frequent letters.
    for l in letters[:3]:
    	if l in RARE_L:
            score += 1
    # Check the most frequent bigrams.
    bigrams = list(count_bigrams(pt, overlap=True))[:5]
    for b in range(5):
        if bigrams[b] in BIGRAMS:
            score += 1
    return score 

# TESTS
# Find inverse.
print(euclid(155, 29))
# Solve linear comparison (case 1).
print(lin_cmp(7, 19, 41))
# Solve linear comparison (case 3).
print(lin_cmp(39, 30, 111))
# Count bigrams of "hello world!" without and with overlap.
print(count_bigrams("hello world! hello mum"))
print(count_bigrams("hello world! hello mum", overlap=True))
# Encode and decode bigram.
print(f"{decode(63)} ({encode('вб')})")
# Check sensibility of text.
data = open('custom.txt', 'r').read().strip()
print(f"sensible: score = {sensible(data)}")
data = open('var3.txt', 'r').read().strip()
print(f"nonsensible: score = {sensible(data)}")
# Find canditates for keys.
candidates = find_keys(data)
keys = []
for k in candidates:
    if sensible(decrypt(data, k)) > 4:
        keys.append(k)
# Remove duplicates.
keys = list(dict.fromkeys(keys))
print(keys)
for k in keys:
    print(f"key = {k}\n{decrypt(data, k)}\n\n")
