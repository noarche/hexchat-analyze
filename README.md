# hexchat-analyze
Introducing the Readability Analyzer Plugin for HexChat!


 Unlock the power of clear communication with the Readability Analyzer Plugin. This innovative tool harnesses advanced Natural Language Processing (NLP) and the Dale-Chall readability formula to assess the clarity of messages in real-time within your IRC chat.


## Why Choose the Readability Analyzer?


Enhanced Understanding: In an age where information overload is common, our plugin helps you gauge the readability of chat messages. It converts complex language into actionable insights, ensuring your discussions are accessible to all participants.

OSINT-Ready: For those in the OSINT (Open Source Intelligence) community, this tool is invaluable. It enables analysts to quickly evaluate the communication styles of users, allowing for better interpretation of messages and the development of effective communication strategies.

User-Friendly Interface: The plugin seamlessly integrates with HexChat, providing immediate feedback on message clarity. Simply chat away, and let the Readability Analyzer do the heavy lifting!

Engaging Metrics: After every 50 messages, receive a detailed report on each user’s average readability score, including their corresponding grade level. Whether you’re collaborating with peers or engaging in public forums, you'll always know how accessible your conversation is.

## Key Features:


Utilizes the reliable Dale-Chall readability score to provide clear assessments.

Tracks and averages scores for individual users, promoting improved communication practices.

Designed for both casual users and serious analysts, making it a versatile tool in any chat environment.

Elevate your communication strategy with the Readability Analyzer Plugin for HexChat today! Clear conversations lead to better understanding, collaboration, and actionable intelligence. Don't let complexity hinder your dialogue—analyze, adapt, and succeed!


## Steps to install

    pip install spacy
    pip install textstat
    pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.5.0/en_core_web_sm-3.5.0.tar.gz
    python3 -m spacy validate
    python3 -m spacy download en_core_web_sm
    sudo mv ./hexchat_analyze.py ./.config/hexchat/addons/


    /py load hexchat_analyze.py
    /py unload hexchat_analyze.py

# Result

**Every 50 messages it prints the users average score and associated reading grade level.**

**Example Output (default is every 50 messages) sent via private message**

    --- Average Readability Scores after 50 messages ---
    JohnDoe's average Dale-Chall readability score: 6.20 (7th - 8th Grade)
    JaneSmith's average Dale-Chall readability score: 5.80 (5th - 6th Grade)
    Alice's average Dale-Chall readability score: 7.30 (9th - 10th Grade)
    --- End of Average Readability Scores ---


