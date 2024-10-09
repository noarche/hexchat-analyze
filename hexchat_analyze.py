import hexchat
import spacy
import textstat
import enchant

nlp = spacy.load("en_core_web_sm")
english_dict = enchant.Dict("en_US")

user_scores = {}
message_count = 0

def filter_valid_words(sentence):
    """
    Filters out non-English words from the sentence using PyEnchant.

    :param sentence: The sentence to filter
    :return: A sentence containing only valid English words
    """
    words = sentence.split()
    valid_words = [word for word in words if english_dict.check(word)]
    
    return ' '.join(valid_words)

def calculate_readability(sentence):
    """
    Calculate the readability score using the Dale-Chall readability formula.
    Filters out non-English words before the calculation.
    
    :param sentence: The sentence to calculate readability for
    :return: Dale-Chall readability score
    """
    valid_sentence = filter_valid_words(sentence)
    
    
    if not valid_sentence:
        return 0
    
    readability_score = textstat.dale_chall_readability_score(valid_sentence)
    return readability_score

def score_to_grade_level(score):
    """
    Convert the Dale-Chall readability score to a grade level.
    
    :param score: Dale-Chall readability score
    :return: Corresponding grade level as a string
    """
    if score <= 4.9:
        return "4th Grade or below"
    elif score <= 5.9:
        return "5th - 6th Grade"
    elif score <= 6.9:
        return "7th - 8th Grade"
    elif score <= 7.9:
        return "9th - 10th Grade"
    elif score <= 8.9:
        return "11th - 12th Grade"
    else:
        return "College Level"

def on_message(word, word_eol, userdata):
    """
    Event handler for when a message is received in the IRC chat.
    Analyzes the readability of the message and maintains a running average per user.
    """
    global message_count

    username = word[0]
    message = word[1]
    
    readability_score = calculate_readability(message)
    
    if username not in user_scores:
        user_scores[username] = [readability_score]
    else:
        user_scores[username].append(readability_score)
    
    message_count += 1
    
    if message_count >= 50:
        average_scores = {user: sum(scores) / len(scores) for user, scores in user_scores.items()}
        
        hexchat.command(f"MSG {hexchat.get_info('nick')} --- Average Readability Scores after {message_count} messages ---")
        
        for user, avg_score in average_scores.items():
            grade_level = score_to_grade_level(avg_score)
            hexchat.command(f"MSG {hexchat.get_info('nick')} {user}'s average Dale-Chall readability score: {avg_score:.2f} ({grade_level})")
        
        hexchat.command(f"MSG {hexchat.get_info('nick')} --- End of Average Readability Scores ---\n")
        
        message_count = 0
        user_scores.clear()

    return hexchat.EAT_NONE

hexchat.hook_print("Channel Message", on_message)

hexchat.prnt("Readability Analyzer Plugin Loaded - Analyzing each user's message for you!")

__module_name__ = "Readability Analyzer"
__module_version__ = "1.0"
__module_description__ = "Analyzes sentence readability for each user and tracks their average score for you."

