import hexchat
import mysql.connector
from mysql.connector import pooling
import textstat
import spacy
import json
import os

__module_name__ = "Readability Score Script"
__module_version__ = "1.8"
__module_description__ = "Calculates readability score with grade levels for each user using the Dale-Chall formula. Type slash showscores to see all user scores. Build Date OCT 12 2024. 1337s.i2p"

# Load English tokenizer, tagger, parser, NER, and POS tagger
nlp = spacy.load("en_core_web_sm")

# Caching file path
CACHE_FILE = "scores_cache.json"

# Hardcoded database credentials
DB_CONFIG = {
    'host': 'localhost',         # Replace with your database host
    'user': 'uername_Here',     # Replace with your database user
    'password': 'pass_Here', # Replace with your database password
    'database': 'db_name_here'  # Replace with your database name
}

# Create tables if they do not exist
def create_tables_if_not_exists(connection):
    cursor = connection.cursor()
    hexchat.prnt("Creating tables if not exist...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user VARCHAR(255) NOT NULL,
        message TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    hexchat.prnt("Table creation checked.")
    cursor.close()

# Database connection setup with pooling
def get_db_connection():
    # Connection pool setup
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="mypool",
        pool_size=5,
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database']
    )
    connection = pool.get_connection()
    if connection is None:
        hexchat.prnt("Database connection failed.")
        return None
    else:
        hexchat.prnt("Database connection established.")
    
    # Create tables if they do not exist
    create_tables_if_not_exists(connection)
    
    return connection

# Load cached results if available
def load_cached_scores():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as file:
            return json.load(file)
    return {}

# Save results to cache
def save_scores_to_cache(scores):
    with open(CACHE_FILE, "w") as file:
        json.dump(scores, file)

# Fetch messages and calculate readability scores with grade levels for each user
def calculate_user_scores():
    cached_scores = load_cached_scores()
    connection = get_db_connection()
    if connection is None:
        return {}, "Database connection failed. Please check config.txt."  # Changed to return an empty dict

    cursor = connection.cursor()
    
    # Use prepared statement to fetch messages
    cursor.execute("SELECT user, message FROM chat_messages")
    messages = cursor.fetchall()
    
    cursor.close()
    connection.close()

    if not messages:
        return {}, "No messages available to calculate scores."  # Changed to return an empty dict

    # Group messages by user and count total messages
    user_messages = {}
    total_messages = len(messages)
    for user, message in messages:
        if user not in user_messages:
            user_messages[user] = []
        user_messages[user].append(message)

    # Calculate scores per user
    user_scores = {}
    for user, msgs in user_messages.items():
        if user in cached_scores:
            user_scores[user] = cached_scores[user]  # Use cached result
            continue

        total_words = sum(len(msg.split()) for msg in msgs)
        total_sentences = sum(len(nlp(msg).sents) for msg in msgs)
        total_syllables = sum(textstat.syllable_count(msg) for msg in msgs)
        
        if total_sentences > 0:
            dale_chall_score = textstat.dale_chall_readability_score(" ".join(msgs))
            grade_level = map_score_to_grade_level(dale_chall_score)
            user_scores[user] = (dale_chall_score, grade_level)
        
            # Update cache with new score
            cached_scores[user] = (dale_chall_score, grade_level)

    # Save updated cache
    save_scores_to_cache(cached_scores)
    return user_scores, total_messages

# Map the score to a corresponding grade level
def map_score_to_grade_level(score):
    if score < 4:
        return "Kindergarten"
    elif 4 <= score < 6:
        return "1st to 3rd grade"
    elif 6 <= score < 8:
        return "4th to 5th grade"
    elif 8 <= score < 10:
        return "6th to 8th grade"
    elif 10 <= score < 12:
        return "9th to 10th grade"
    elif 12 <= score < 14:
        return "11th to 12th grade"
    else:
        return "College level"

# Handle '/showscores' command (private message)
def handle_showscores_command(word, word_eol, userdata):
    user_scores, total_messages = calculate_user_scores()
    
    if total_messages is None:
        hexchat.emit_print("Notice", "Private", user_scores)  # This is the error message
    else:
        # Create a formatted message with total messages and scores for all users
        scores_message = f"Total Messages Analyzed: {total_messages}\n" + \
                         "Readability scores:\n" + \
                         "\n".join(f"{user}: {score:.2f} ({grade_level})" for user, (score, grade_level) in user_scores.items())
        hexchat.emit_print("Notice", "Private", scores_message)
    return hexchat.EAT_ALL

# Handle '/showscoreschat' command (chat response)
def handle_showscoreschat_command(word, word_eol, userdata):
    user_scores, total_messages = calculate_user_scores()
    
    if total_messages is None:
        hexchat.command(f"SAY {user_scores}")  # This is the error message
    else:
        # Create a formatted message with total messages and scores for all users
        scores_message = f"Total Messages Analyzed: {total_messages}\n" + \
                         "Readability scores:\n" + \
                         ", ".join(f"{user}: {score:.2f} ({grade_level})" for user, (score, grade_level) in user_scores.items())
        hexchat.command(f"SAY {scores_message}")
    return hexchat.EAT_ALL

# Handle '/showus' command (private message with total messages and percentage)
def handle_showus_command(word, word_eol, userdata):
    connection = get_db_connection()
    if connection is None:
        hexchat.emit_print("Notice", "Private", "Database connection failed.")
        return hexchat.EAT_ALL
    
    cursor = connection.cursor()
    cursor.execute("SELECT user FROM chat_messages")
    messages = cursor.fetchall()
    cursor.close()
    connection.close()
    
    total_messages = len(messages)
    
    if total_messages == 0:
        hexchat.emit_print("Notice", "Private", "No messages found.")
        return hexchat.EAT_ALL

    # Count messages per user
    user_message_count = {}
    for user, in messages:
        if user in user_message_count:
            user_message_count[user] += 1
        else:
            user_message_count[user] = 1

    # Create the response message
    response_message = f"Total Messages: {total_messages}\n"
    response_message += "User Contributions (% of Total):\n"

    for user, count in user_message_count.items():
        percentage = (count / total_messages) * 100
        response_message += f"{user}: {count} ({percentage:.2f}%)\n"

    hexchat.emit_print("Notice", "Private", response_message)
    return hexchat.EAT_ALL

# Registering the commands
hexchat.hook_command("SHOWSCORES", handle_showscores_command, help="/SHOWSCORES - Displays readability scores and grade levels for each user privately")
hexchat.hook_command("SHOWSCORESCHAT", handle_showscoreschat_command, help="/SHOWSCORESCHAT - Displays readability scores and grade levels for each user in chat")
hexchat.hook_command("SHOWUS", handle_showus_command, help="/SHOWUS - Displays total number of messages and user contributions as a percentage")

hexchat.prnt(f"{__module_name__} {__module_version__} loaded")