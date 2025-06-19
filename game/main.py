import random
import os
from datetime import datetime

# Define file paths
SECRET_NUMBER_FILE = 'game/secret_number.txt'
GUESS_LOG_FILE = 'guesses.log'
README_FILE = 'README.md'

def get_secret_number():
    """Reads or generates the secret number."""
    if os.path.exists(SECRET_NUMBER_FILE):
        with open(SECRET_NUMBER_FILE, 'r') as f:
            try:
                return int(f.read().strip())
            except ValueError:
                # If file content is not a valid int, regenerate
                pass
    
    # Generate new number if file doesn't exist or content is invalid
    new_secret = random.randint(1, 100)
    with open(SECRET_NUMBER_FILE, 'w') as f:
        f.write(str(new_secret))
    print(f"Generated new secret number: {new_secret}")
    return new_secret

def get_last_guess_from_commit():
    """Tries to extract the last guess from the latest commit message."""
    # This assumes the commit message for a guess is like "Guess: 50"
    commit_message = os.environ.get('GITHUB_COMMIT_MESSAGE', '').strip()
    if commit_message.lower().startswith('guess:'):
        try:
            return int(commit_message.split(':')[1].strip())
        except (ValueError, IndexError):
            pass
    return None

def update_readme(log_entry):
    """Updates the README.md with the latest game status and log."""
    with open(README_FILE, 'r') as f:
        readme_content = f.readlines()

    # Find the game section (you'll define this in your README)
    start_tag = ''
    end_tag = ''

    game_section_start = -1
    game_section_end = -1

    for i, line in enumerate(readme_content):
        if start_tag in line:
            game_section_start = i
        if end_tag in line:
            game_section_end = i
            break

    if game_section_start != -1 and game_section_end != -1:
        # Build new game section
        new_game_section = [
            start_tag + '\n',
            '## 🔢 Guess My Number!\n',
            'I\'ve picked a secret number between 1 and 100. Can you guess it?\n',
            'To play, make a **commit** to this repository with a message like: `Guess: 50`\n',
            '\n### Last Game Update:\n',
            f'```\n{log_entry}\n```\n',
            '\n### Game History:\n',
            '```\n'
        ]
        
        # Read the last few lines from the log file
        log_lines = []
        if os.path.exists(GUESS_LOG_FILE):
            with open(GUESS_LOG_FILE, 'r') as f_log:
                log_lines = f_log.readlines()
        
        # Add last 10 entries from log (or fewer if not 10)
        new_game_section.extend(log_lines[-10:]) 
        new_game_section.append('```\n')
        new_game_section.append(end_tag + '\n')

        # Replace the old section with the new one
        updated_readme = readme_content[:game_section_start] + new_game_section + readme_content[game_section_end+1:]
    else:
        # If tags are not found, append to the end
        print("Warning: Guess game tags not found in README. Appending game section.")
        updated_readme = readme_content + [
            '\n---\n',
            start_tag + '\n',
            '## 🔢 Guess My Number!\n',
            'I\'ve picked a secret number between 1 and 100. Can you guess it?\n',
            'To play, make a **commit** to this repository with a message like: `Guess: 50`\n',
            '\n### Last Game Update:\n',
            f'```\n{log_entry}\n```\n',
            '\n### Game History:\n',
            '```\n',
            f'{log_entry}\n', # Initial entry
            '```\n',
            end_tag + '\n'
        ]

    with open(README_FILE, 'w') as f:
        f.writelines(updated_readme)
    print("README.md updated successfully.")

def main():
    secret_number = get_secret_number()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = ""

    last_guess = get_last_guess_from_commit()

    if last_guess is None:
        log_message = f"[{current_time}] No new guess detected in commit message. Current secret number is still active."
    elif last_guess == secret_number:
        log_message = f"[{current_time}] 🎉 You guessed it! The number was {secret_number}! Starting a new game..."
        # Reset game by deleting secret_number.txt
        if os.path.exists(SECRET_NUMBER_FILE):
            os.remove(SECRET_NUMBER_FILE)
            print("Secret number reset for new game.")
    elif last_guess < secret_number:
        log_message = f"[{current_time}] Your guess ({last_guess}) is too LOW. Try again!"
    else: # last_guess > secret_number
        log_message = f"[{current_time}] Your guess ({last_guess}) is too HIGH. Try again!"

    # Append to log file
    with open(GUESS_LOG_FILE, 'a') as f_log:
        f_log.write(log_message + '\n')
    print(f"Logged: {log_message}")

    # Update README
    update_readme(log_message)

if __name__ == "__main__":
    main()