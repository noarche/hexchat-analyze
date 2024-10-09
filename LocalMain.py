import spacy
from collections import defaultdict
import textstat
import enchant

nlp = spacy.load("en_core_web_sm")
english_dict = enchant.Dict("en_US")  # Using PyEnchant to check for valid English words

def analyze_sentence(sentence):
    """
    Analyze the structure of a sentence and categorize words into parts of speech.
    
    :param sentence: The sentence to analyze
    :return: A dictionary categorizing words into nouns, verbs, pronouns, adjectives, and others
    """
    doc = nlp(sentence)
    
    pos_dict = defaultdict(list)
    
    for token in doc:
        if token.pos_ == "NOUN":
            pos_dict["Nouns"].append(token.text)
        elif token.pos_ == "VERB":
            pos_dict["Verbs"].append(token.text)
        elif token.pos_ == "PRON":
            pos_dict["Pronouns"].append(token.text)
        elif token.pos_ == "ADJ":
            pos_dict["Adjectives"].append(token.text)
        else:
            pos_dict[token.pos_].append(token.text) 
    
    return pos_dict

def display_results(pos_dict):
    """
    Display the categorized words in a structured manner.
    
    :param pos_dict: A dictionary with categorized words by parts of speech
    """
    print("\n--- Sentence Structure Analysis ---\n")
    
    for pos, words in pos_dict.items():
        print(f"{pos}: {', '.join(words) if words else 'None'}")
    
    print("\n-------------------------------\n")

def calculate_readability(sentence):
    """
    Calculate the readability score using the Dale-Chall readability formula, 
    but ignore made-up or non-dictionary words.
    
    :param sentence: The sentence to calculate readability for
    :return: Adjusted Dale-Chall readability score and the corresponding grade level
    """
    # Tokenize sentence and check if words are valid English words
    words = sentence.split()
    valid_words = [word for word in words if english_dict.check(word)]
    
    if not valid_words:  # If all words are invalid, return lowest possible readability score
        return 0, "4th Grade or below"
    
    # Recreate sentence with only valid words
    valid_sentence = ' '.join(valid_words)
    
    # Calculate readability score on valid sentence
    readability_score = textstat.dale_chall_readability_score(valid_sentence)
    
    if readability_score <= 4.9:
        grade_level = "4th Grade or below"
    elif readability_score <= 5.9:
        grade_level = "5th - 6th Grade"
    elif readability_score <= 6.9:
        grade_level = "7th - 8th Grade"
    elif readability_score <= 7.9:
        grade_level = "9th - 10th Grade"
    elif readability_score <= 8.9:
        grade_level = "11th - 12th Grade"
    else:
        grade_level = "College Level"
    
    return readability_score, grade_level

if __name__ == "__main__":
    while True:
        print("Enter a sentence to analyze (or press Enter for a default sentence):")
        sentence = input().strip() or "The quick brown fox jumps over the lazy dog."
        
        pos_results = analyze_sentence(sentence)
        
        display_results(pos_results)
        
        readability_score, grade_level = calculate_readability(sentence)
        
        print(f"Dale-Chall Readability Score: {readability_score:.2f}")
        print(f"Grade Level: {grade_level}")

        # Add a prompt to allow the user to continue without clearing the console
        print("\nType 'exit' to quit or press Enter to analyze another sentence.")
        if input().strip().lower() == 'exit':
            break
