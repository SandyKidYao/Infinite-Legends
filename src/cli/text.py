class Text:
    # Main Menu
    GAME_TITLE = "=== Infinite Legends: An AI-driven Text-Based Role-Playing Game ==="
    NEW_GAME = "New Game"
    LOAD_GAME = "Load Game"
    QUIT = "Quit"
    ENTER_CHOICE = "Enter your choice: "
    INVALID_CHOICE = "Invalid choice. Please try again."

    # Game Setup
    ENTER_KEYWORDS = "Enter keywords for game theme (Press Enter to continue...):"
    KEYWORD_PROMPT = "> "

    # Dialogue
    DIALOGUE_TITLE = "=== Dialogue ==="

    # Inventory
    INVENTORY_TITLE = "=== Inventory ==="
    INVENTORY_EMPTY = "Your inventory is empty."
    PRESS_ENTER = "Press Enter to continue..."

    # Use Item
    USE_ITEM_TITLE = "=== Use Item ==="
    CHOOSE_ITEM = "Choose an item to use (or press Enter to cancel): "
    USING_ITEM = "Using {}..."
    ITEM_USED = "{} has been used and removed from your inventory."
    CANCELLED_ITEM_USE = "Cancelled item use."

    # Options
    OPTIONS_TITLE = "=== Options ==="
    VIEW_INVENTORY = "View Inventory"
    USE_ITEM = "Use Item"
    VIEW_HISTORY = "View Dialogue History"
    RETURN_TO_MAIN_MENU = "Return to Main Menu"

    # Dialogue History
    HISTORY_TITLE = "=== Dialogue History ==="

    # Exit Confirmation
    EXIT_CONFIRM = "Are you sure you want to return to the main menu? Your progress will be saved. (y/n): "
    INVALID_YES_NO = "Invalid input. Please enter 'y' or 'n'."

    # Game End
    THANK_YOU = "Thank you for playing. Goodbye!"

    # Error Messages
    NO_SAVE_FOUND = "No saved game found. Starting a new game."
    INVALID_NUMBER = "Invalid input. Please enter a number."

    # Game Start
    GAME_START = "Starting a new game with theme: {}"

    # New texts for save file selection
    LOAD_GAME_TITLE = "=== Load Game ==="
    NO_SAVE_FILES = "No save files found."
    CHOOSE_SAVE_FILE = "Choose a save file to load (or enter the number to return to main menu): "
    GAME_LOADED_SUCCESSFULLY = "Game loaded successfully."
    FAILED_TO_LOAD_GAME = "Failed to load the game. Starting a new game."

    @classmethod
    def get(cls, key, *args):
        return getattr(cls, key).format(*args) if args else getattr(cls, key)
