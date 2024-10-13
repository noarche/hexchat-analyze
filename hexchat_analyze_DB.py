import hexchat
import spacy
import textstat
import enchant
import mysql.connector
from mysql.connector import Error

# Load language processing tools
nlp = spacy.load("en_core_web_sm")
english_dict = enchant.Dict("en_US")

# Global variables
user_scores = {}
message_count = 0

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'UserNameHere',     # Replace with your MariaDB username
    'password': 'PassWordHere', # Replace with your MariaDB password
    'database': 'readability_analyzer' # Replace with your database name
}

def initialize_database():
    """Initializes the MariaDB database connection and creates necessary tables if they do not exist."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS readability_analyzer")
        cursor.execute("USE readability_analyzer")

        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                readability_score FLOAT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        hexchat.prnt(f"Error initializing database: {e}")

def log_message_to_db(username, message, readability_score):
    """Logs the message to the MariaDB database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO messages (username, message, readability_score) 
            VALUES (%s, %s, %s)
        ''', (username, message, readability_score))
        
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        hexchat.prnt(f"Error logging message to database: {e}")

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

def get_average_readability_from_db(username):
    """Calculates the average readability score for a given user based on all messages in the database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Query to calculate the average readability score for the user
        cursor.execute('''
            SELECT AVG(readability_score) 
            FROM messages 
            WHERE username = %s
        ''', (username,))

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        # Return the average score if found, otherwise 0
        return result[0] if result[0] is not None else 0
    except Error as e:
        hexchat.prnt(f"Error calculating average readability from database: {e}")
        return 0

def on_message(word, word_eol, userdata):
    global message_count

    username = word[0]
    message = word[1]
    
    readability_score = calculate_readability(message)
    
    # Log the message to the database
    log_message_to_db(username, message, readability_score)
    
    # Update user scores
    if username not in user_scores:
        user_scores[username] = []
    user_scores[username].append(readability_score)
    
    message_count += 1
    
    # After 20 messages, calculate average readability from the database and send private message
    if message_count >= 20:
        hexchat.command(f"MSG {hexchat.get_info('nick')} --- Average Readability Scores for All Users ---")
        
        users = set(user_scores.keys())
        
        for user in users:
            avg_score = get_average_readability_from_db(user)
            grade_level = score_to_grade_level(avg_score)
            hexchat.command(f"MSG {hexchat.get_info('nick')} {user}'s average Dale-Chall readability score: {avg_score:.2f} ({grade_level})")
        
        hexchat.command(f"MSG {hexchat.get_info('nick')} --- End of Average Readability Scores ---\n")
        
        # Reset message count and user scores for the next batch
        message_count = 0
        user_scores.clear()

    return hexchat.EAT_NONE



# Initialize the database
initialize_database()

# Hook the message event
hexchat.hook_print("Channel Message", on_message)

hexchat.prnt("Readability Analyzer Plugin Loaded - Analyzing each user's message for you!")

__module_name__ = "Readability Analyzer"
__module_version__ = "1.0"
__module_description__ = "Analyzes sentence readability for each user and tracks their average score for you."
