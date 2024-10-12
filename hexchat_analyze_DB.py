import hexchat
import mysql.connector
from mysql.connector import pooling
import textstat
import spacy
import json
import os

__module_name__ = "Readability Score Script"
__module_version__ = "1.8"
__module_description__ = "Calculates readability score with grade levels for each user using the Dale-Chall formula. Type slash /SHOWSCORES to see all user scores. Build Date OCT 12 2024."

# Load English tokenizer, tagger, parser, NER, and POS tagger
nlp = spacy.load("en_core_web_sm")

# Caching file path
CACHE_FILE = "scores_cache.json"

# Hardcoded database credentials
DB_CONFIG = {
    'host': 'localhost',
    'user': 'USERNAME',
    'password': 'PASSWORD',
    'database': 'DBNAME'
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

# Log incoming chat messages
def log_message(word, word_eol, userdata):
    user = word[0]
    message = word[1]
    
    connection = get_db_connection()
    if connection is None:
        return hexchat.EAT_NONE  # Do not consume the event if logging fails

    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO chat_messages (user, message) VALUES (%s, %s)", (user, message))
        connection.commit()
    except Exception as e:
        hexchat.prnt(f"Failed to log message: {e}")
    finally:
        cursor.close()
        connection.close()
    
    return hexchat.EAT_NONE  # Allow the message to pass through

# Hook to capture all channel messages
hexchat.hook_print("Channel Message", log_message)

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
        return {}, 0  # Return an empty dictionary and 0 total messages

    cursor = connection.cursor()
    cursor.execute("SELECT user, message FROM chat_messages")
    messages = cursor.fetchall()
    cursor.close()
    connection.close()

    if not messages:
        return {}, 0  # Return an empty dictionary and 0 total messages

    user_messages = {}
    total_messages = len(messages)
    for user, message in messages:
        if user not in user_messages:
            user_messages[user] = []
        user_messages[user].append(message)

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
            cached_scores[user] = (dale_chall_score, grade_level)

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

# Handle '/SHOWSCORES' command
def handle_showscores_command(word, word_eol, userdata):
    user_scores, total_messages = calculate_user_scores()
    
    if not user_scores and total_messages == 0:
        hexchat.emit_print("Notice", "Private", "No messages available to calculate scores.")
        return hexchat.EAT_ALL

    scores_message = f"Total Messages Analyzed: {total_messages}\n" + \
                     "Readability scores:\n" + \
                     "\n".join(f"{user}: {score:.2f} ({grade_level})" for user, (score, grade_level) in user_scores.items())
    hexchat.emit_print("Notice", "Private", scores_message)
    return hexchat.EAT_ALL

# Handle '/SHOWSCORESCHAT' command
def handle_showscoreschat_command(word, word_eol, userdata):
    user_scores, total_messages = calculate_user_scores()
    
    if not user_scores and total_messages == 0:
        hexchat.command(f"SAY No messages available to calculate scores.")
        return hexchat.EAT_ALL

    scores_message = f"Total Messages Analyzed: {total_messages}\n" + \
                     "Readability scores:\n" + \
                     ", ".join(f"{user}: {score:.2f} ({grade_level})" for user, (score, grade_level) in user_scores.items())
    hexchat.command(f"SAY {scores_message}")
    return hexchat.EAT_ALL

# Handle '/SHOWUS' command
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

    user_message_count = {}
    for user, in messages:
        if user in user_message_count:
            user_message_count[user] += 1
        else:
            user_message_count[user] = 1

    response_message = f"Total Messages: {total_messages}\nUser Contributions (% of Total):\n"

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
