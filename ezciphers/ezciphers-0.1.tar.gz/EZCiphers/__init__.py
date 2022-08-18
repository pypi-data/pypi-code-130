# EZCiphers V0.1
# First python library, and first python project on github. 
# AUG 17 2022
# Basic ciphers added:
# Viginere - use using vigDecrypt and vigEncrypt
# Caesar Shift, or Rot[X] - Use using caeEncrypt, caeDecrypt, rotEncrypt, and rotDecrypt.
# Atbash - Use using atbash. I left atbEncrypt and atbDecrypt in there, but... why would you use that???
# Baconian - use using bacEncrypt (haha) and bacDecrypt.


# Basic vigenere cipher decryptor. Powered by magic and basic subtraction.


def vigDecrypt(message, keyword):
    # initialize variables. translatedMessage is the final output, cleared for now.
    fixedMessage = message.lower()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    translatedMessage = ""
    counter = 0
    # per letter, subtract the keyword's letter value 0-25 from the letter's letter value 0-25. limiter at 26
    for letter in fixedMessage:
        if letter in alphabet:
            letterValue = alphabet.find(letter)
            keywordValue = alphabet.find(keyword[counter % len(keyword)])
            translatedMessage += alphabet[((letterValue - keywordValue)) % 26]
            # move letter forward each rotation
            counter += 1
        # if it's not in the alphabet, skip it and leave it in the translated message
        else:
            translatedMessage += letter
    return translatedMessage

# Basic vigenere cipher encryptor. Powered by magic and, like an NFT, only has one thing changed about it.
def vigEncrypt(message, keyword):
    # initialize variables. translatedMessage is the final output, cleared for now.
    fixedMessage = message.lower()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    translatedMessage = ""
    counter = 0
    # per letter, add the keyword's letter value 0-25 from the letter's letter value 0-25. limiter at 26
    for letter in fixedMessage:
        if letter in alphabet:
            letterValue = alphabet.find(letter)
            keywordValue = alphabet.find(keyword[counter % len(keyword)])
            translatedMessage += alphabet[((letterValue + keywordValue)) % 26]
            # move letter forward each rotation
            counter += 1
        # if it's not in the alphabet, skip it and leave it in the translated message
        else:
            translatedMessage += letter
    return translatedMessage

# Basic rotN decryptor, give it the message and the number to shift it by and it'll work magic.
def rotDecrypt(message, number):
    # define the alphabet, make the end result a variable that can be added to.
    fixedMessage = message.lower()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    translatedMessage = ""
    # for each letter, find the value of said letter out of 25, then add it to the number used to shift.
    for letter in fixedMessage:
        if letter in alphabet:
            letterValue = alphabet.find(letter)
            translatedMessage += alphabet[(letterValue + int(number)) % 26]
        # if you added punctuation, whatever. it doesn't add it into the equation. just adds it into final.
        else: 
            translatedMessage += letter
    return translatedMessage

def rotEncrypt(message, number):
    # define the alphabet, make the end result a variable that can be added to.
    fixedMessage = message.lower()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    translatedMessage = ""
    # for each letter, find the value of said letter out of 25, then subtract it to the number used to shift.
    for letter in fixedMessage:
        if letter in alphabet:
            letterValue = alphabet.find(letter)
            translatedMessage += alphabet[(letterValue - int(number)) % 26]
        # if you added punctuation, whatever. it doesn't add it into the equation. just adds it into final.
        else: 
            translatedMessage += letter
    return translatedMessage

# Alias for rotN, just in case someone calls it the other way.
def caeDecrypt(message, number):
    # If you can't understand this code, how are you programming?
    return rotDecrypt(message, number)

# Alias for rotN, just in case someone calls it the other way.
def caeEncrypt(message, number):
    return rotEncrypt(message, number)

def rot13Encrypt(message):
    return rotEncrypt(message, 13)

def rot13Decrypt(message):
    return rotDecrypt(message, 13)

# THE MOST SIMPLE PART OF THIS LIBRARY (excluding aliases.)
def atbash(message):
    # Initialize variables, create a reverse alphabet.
    fixedMessage = message.lower()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    reverseAlphabet = "zyxwvutsrqponmlkjihgfedcba"
    translatedMessage = ""
    # For each letter, if it's in the alphabet, switch the value of the alphabet to the reverse. 0 = A in normal,
    # but 0 = Z in reverse.
    for letter in fixedMessage:
        if letter in alphabet:
            letterValue = alphabet.find(letter)
            translatedMessage += reverseAlphabet[letterValue]
    return translatedMessage

def atbEncrypt(message):
    return atbash(message)

def atbDecrypt(message):
    return atbash(message)

# I asked someone online for help on how to do this. I have no clue how this even works.
# Is this inefficient? Totally. Do I know how to make it more efficient yet? No.
bacEnlookup = {'a': 'aaaaa', 'b': 'aaaab', 'c': 'aaaba', 'd': 'aaabb', 'e': 'aabaa',
               'f': 'aabab', 'g': 'aabba', 'h': 'aabbb', 'i': 'abaaa', 'j': 'abaab',
               'k': 'ababa', 'l': 'ababb', 'm': 'abbaa', 'n': 'abbab', 'o': 'abbba',
               'p': 'abbbb', 'q': 'baaaa', 'r': 'baaab', 's': 'baaba', 't': 'baabb',
               'u': 'babaa', 'v': 'babab', 'w': 'babba', 'x': 'babbb', 'y': 'bbaaa', 
               'z': 'bbaab'}
bacDelookup = {'aaaaa': 'a', 'aaaab': 'b', 'aaaba': 'c', 'aaabb': 'd', 'aabaa': 'e',
               'aabab': 'f', 'aabba': 'g', 'aabbb': 'h', 'abaaa': 'i', 'abaab': 'j',
               'ababa': 'k', 'ababb': 'l', 'abbaa': 'm', 'abbab': 'n', 'abbba': 'o',
               'abbbb': 'p', 'baaaa': 'q', 'baaab': 'r', 'baaba': 's', 'baabb': 't',
               'babaa': 'u', 'babab': 'v', 'babba': 'w', 'babbb': 'x', 'bbaaa': 'y', 
               'bbaab': 'z'}

def bacEncrypt(message):
    # lowercase all the things!!! (◕ᗝ◕)🧹୨
    fixedMessage = message.lower()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    translatedMessage = ""
    #for each letter, if it's in the alphabet, look it up in the dictionary. then use that instead
    for letter in fixedMessage:
        if letter in alphabet:
            translatedMessage += bacEnlookup[letter]
        else:
            translatedMessage += letter
    return translatedMessage


# TODO: Fix decrypt of Baconian cipher. Doesn't work correctly.
# currently doesn't support punctuation. soz.
# it also completely combines into one script and doesn't actually re-put in all of the spaces.
# guess i'll put a todo.
def bacDecrypt(message):
    # good lord, this is finnicky.
    # for each letter in the stripped message, if it's a, A, b, or B, let it through.
    pass1 = ""
    for letter in message.strip():
        if letter in "abAB":
            pass1 += letter
    # i was interrupted after making this. all it does is create a space every 5 or so characters.
    pass2 = ' '.join(pass1[i:i+5] for i in range(0,len(pass1),5))
    fixedMessage = pass2.lower()
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    translatedMessageUnfinished = ""
    # now split! every list item is now checked against the dictionary, turned into that letter,
    # and then joined back together.
    passList = pass2.split(" ")
    for string in passList:
        if string in bacDelookup:
            translatedMessageUnfinished += bacDelookup[string]
        else:
            translatedMessageUnfinished += letter
    translatedMessage = "".join(translatedMessageUnfinished)
    return translatedMessage