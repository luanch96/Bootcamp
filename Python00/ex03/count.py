"""
Takes a single string argument and displays the sums of its upper-case characters,
lower-case characters, punctuation characters and spaces.
"""
def text_analyzer(string=None):
    if string is None:
        string = input('Please enter a string: ')
    elif not isinstance(string, str):
        print('Error: argument must be a string')
        return
    
    upper_count = 0
    lower_count = 0
    punct_count = 0
    space_count = 0
    
    for char in string:
        if char.isupper():
            upper_count += 1
        elif char.islower():
            lower_count += 1
        elif char in string.punctuation:
            punct_count += 1
        elif char.isspace():
            space_count += 1
    
    print('Upper case characters:', upper_count)
    print('Lower case characters:', lower_count)
    print('Punctuation characters:', punct_count)
    print('Spaces:', space_count)
