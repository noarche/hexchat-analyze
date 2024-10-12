# Updated 

hexchat_analyze_db.py uses mariadb and mysql connector

Much better results. 

# hexchat-analyze
 Unlock the power of clear communication with the Readability Analyzer Plugin. This innovative tool harnesses advanced Natural Language Processing (NLP) and the Dale-Chall readability formula to assess the clarity of messages in real-time within your IRC chat.


## Why Choose the Readability Analyzer?


### Enhanced Understanding:

In an age where information overload is common, our plugin helps you gauge the readability of chat messages. It converts complex language into actionable insights, ensuring your discussions are accessible to all participants.

### OSINT-Ready: 

For those in the OSINT (Open Source Intelligence) community, this tool is invaluable. It enables analysts to quickly evaluate the communication styles of users, allowing for better interpretation of messages and the development of effective communication strategies.

### User-Friendly Interface:

The plugin seamlessly integrates with HexChat, providing immediate feedback on message clarity. Simply chat away, and let the Readability Analyzer do the heavy lifting!

### Engaging Metrics: 

After every 50 messages, receive a detailed report on each user’s average readability score, including their corresponding grade level. Whether you’re collaborating with peers or engaging in public forums, you'll always know how accessible your conversation is.

## Key Features:


Utilizes the reliable Dale-Chall readability score to provide clear assessments.

Tracks and averages scores for individual users, promoting improved communication practices.

Designed for both casual users and serious analysts, making it a versatile tool in any chat environment.

Elevate your communication strategy with the Readability Analyzer Plugin for HexChat today! Clear conversations lead to better understanding, collaboration, and actionable intelligence. Don't let complexity hinder your dialogue—analyze, adapt, and succeed!


## Steps to install

    python3 -m pip install spacy
    python3 -m pip install textstat
    python3 -m pip install pyenchant
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


# Notes

    LocalMain.py is the local version of the script. 
    It allows the user to run the script and analyze text, 
    without connection to hexchat or irc. It does not monitor hexchat, 
    nor is it needed to run the hexchat script. 

# Additional Scripts

### User_Metrics.py

This script sends a private message every hour at :01 with user metrics in the format:

    -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- 
    User Metrics:
    user1: 25 messages, 3 connects, 1 disconnects, 5 away changes, 15.50 min away, 30.00% away, Known Aliases: user1, user2 
    user2: 40 messages, 2 connects, 0 disconnects, 3 away changes, 5.00 min away, 10.00% away, Known Aliases: user3 
    -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

# ꧁꧂  Buy me a coffee ☕

![qrCode](https://raw.githubusercontent.com/noarche/cd-ripper/main/unrelated-ignore/CryptoQRcodes.png)

**Bitcoin** address `bc1qnpjpacyl9sff6r4kfmn7c227ty9g50suhr0y9j`


**Ethereum** address `0x94FcBab18E4c0b2FAf5050c0c11E056893134266`


**Litecoin** address `ltc1qu7ze2hlnkh440k37nrm4nhpv2dre7fl8xu0egx`

![githubstamp](https://github.com/user-attachments/assets/d7b584e2-ba2a-442c-8783-9acb3a4781a5)


-------------------------------------------------------------------

![noarche's GitHub stats](https://github-readme-stats.vercel.app/api?username=noarche&show_icons=true&theme=transparent)

# Looking for a Combolist tool?

Check out my all in one [wordlist manipulator](https://github.com/noarche/ComboToolPro-GUI). Many useful combo tools. 



# Need website credential stuffing tool?

[Customizable Website Checker](https://github.com/noarche/brute)
