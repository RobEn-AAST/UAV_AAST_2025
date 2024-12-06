def split_into_words(lines):
    word_list = []  # Initialize an empty list to store words from each line
    for line in lines:
        words = line.split()  # Split the line into words
        word_list.append(words)  # Add the list of words to the main list
    return word_list



lines = [
    "Hello, World! ",
    " Welcome to Python programming. ",
    "Have a great day!"
]




word_list = split_into_words(lines)


print(word_list[0][0])