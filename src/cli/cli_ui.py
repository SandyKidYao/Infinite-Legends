import os
import sys
import time

from colorama import init, Fore, Style

from src.game.game_manager import GameManager
from src.game.model import RecordType, GameRound
from .text import Text
from .text_zh import TextZH


class CLIUI:
    def __init__(self, game_manager: GameManager, language='Chinese'):
        self.game_manager: GameManager = game_manager
        if language == 'Chinese':
            self.text = TextZH
        else:
            self.text = Text
        init(autoreset=True)  # Initialize colorama
        self.DYNAMIC_OPTION_COLOR = Fore.CYAN
        self.FIXED_OPTION_COLOR = Fore.GREEN
        self.PROMPT_COLOR = Fore.MAGENTA
        self.ERROR_COLOR = Fore.RED
        self.TITLE_COLOR = Fore.YELLOW

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_slowly(self, text, delay=0.03, color=Fore.WHITE):
        for char in text:
            sys.stdout.write(color + char)
            sys.stdout.flush()
            time.sleep(delay)
        print(Style.RESET_ALL)

    def main_menu(self):
        while True:
            self.clear_screen()
            self.print_slowly(self.text.get('GAME_TITLE'), color=self.TITLE_COLOR)
            print(self.DYNAMIC_OPTION_COLOR + f"1. {self.text.get('NEW_GAME')}")
            print(self.DYNAMIC_OPTION_COLOR + f"2. {self.text.get('LOAD_GAME')}")
            print(self.DYNAMIC_OPTION_COLOR + f"3. {self.text.get('QUIT')}")
            choice = input(self.PROMPT_COLOR + self.text.get('ENTER_CHOICE') + Fore.WHITE)
            if choice == "1":
                return "new_game"
            elif choice == "2":
                return "load_game"
            elif choice == "3":
                return "quit"
            else:
                print(self.ERROR_COLOR + self.text.get('INVALID_CHOICE'))
                time.sleep(1)

    def new_game_setup(self):
        keywords = []
        self.clear_screen()
        self.print_slowly(self.text.get('ENTER_KEYWORDS'), color=self.TITLE_COLOR)
        while True:
            keyword = input(self.PROMPT_COLOR + self.text.get('KEYWORD_PROMPT') + Fore.WHITE)
            if not keyword:
                break
            keywords.append(keyword)
        return keywords

    def display_round(self, current_round: GameRound):
        self.clear_screen()
        for item in current_round.get_items:
            print(Fore.MAGENTA + f"[Get Item] {item}")
        for item in current_round.lose_items:
            print(Fore.MAGENTA + f"[Lose Item] {item}")
        self.print_slowly(self.text.get('DIALOGUE_TITLE'), color=self.TITLE_COLOR)
        self.print_slowly(current_round.narrative, color=Fore.WHITE)
        print()
        print(self.TITLE_COLOR + self.text.get('OPTIONS_TITLE'))
        options = current_round.choices

        for i, option in enumerate(options, 1):
            print(self.DYNAMIC_OPTION_COLOR + f"{i}. {option}")

        fixed_options = [
            self.text.get('USE_ITEM'),
            self.text.get('VIEW_HISTORY'),
            self.text.get('RETURN_TO_MAIN_MENU')
        ]
        for i, option in enumerate(fixed_options, len(options) + 1):
            print(self.FIXED_OPTION_COLOR + f"{i}. {option}")
        print()

    def display_inventory(self):
        self.clear_screen()
        self.print_slowly(self.text.get('INVENTORY_TITLE'), color=self.TITLE_COLOR)
        inventory = self.game_manager.get_inventory()
        if not inventory:
            print(self.ERROR_COLOR + self.text.get('INVENTORY_EMPTY'))
        else:
            for item in inventory:
                print(Fore.MAGENTA + f"- {item}")
        input(self.PROMPT_COLOR + self.text.get('PRESS_ENTER') + Fore.WHITE)

    def use_item(self):
        self.clear_screen()
        self.print_slowly(self.text.get('USE_ITEM_TITLE'), color=self.TITLE_COLOR)
        inventory = self.game_manager.get_inventory()
        if not inventory:
            print(self.ERROR_COLOR + self.text.get('INVENTORY_EMPTY'))
        else:
            for i, item in enumerate(inventory, 1):
                print(self.DYNAMIC_OPTION_COLOR + f"{i}. {item}")
            choice = input(self.PROMPT_COLOR + self.text.get('CHOOSE_ITEM') + Fore.WHITE)
            if choice.isdigit() and 1 <= int(choice) <= len(inventory):
                item = inventory[int(choice) - 1]
                print(self.TITLE_COLOR + self.text.get('USING_ITEM', item))
                self.game_manager.process_option(item=item)
                print(self.DYNAMIC_OPTION_COLOR + self.text.get('ITEM_USED', item))
            elif choice == "":
                print(self.TITLE_COLOR + self.text.get('CANCELLED_ITEM_USE'))
            else:
                print(self.ERROR_COLOR + self.text.get('INVALID_CHOICE'))
        input(self.PROMPT_COLOR + self.text.get('PRESS_ENTER') + Fore.WHITE)

    def view_dialogue_history(self):
        self.clear_screen()
        self.print_slowly(self.text.get('HISTORY_TITLE'), color=self.TITLE_COLOR)
        for record in self.game_manager.get_dialogue_history():
            if record.record_type == RecordType.TURN_DESCRIPTION:
                print(Fore.WHITE + str(record))
            elif record.record_type == RecordType.PLAYER_CHOICE:
                print(self.DYNAMIC_OPTION_COLOR + str(record))
            elif record.record_type == RecordType.ITEM_ACQUIRED:
                print(Fore.MAGENTA + str(record))
            elif record.record_type == RecordType.ITEM_USED:
                print(self.DYNAMIC_OPTION_COLOR + str(record))
        input(self.PROMPT_COLOR + self.text.get('PRESS_ENTER') + Fore.WHITE)

    def confirm_exit(self):
        while True:
            choice = input(self.PROMPT_COLOR + self.text.get('EXIT_CONFIRM') + Fore.WHITE).lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print(self.ERROR_COLOR + self.text.get('INVALID_YES_NO'))

    def game_loop(self):
        while True:
            current_round = self.game_manager.get_current_round()
            options = current_round.choices
            self.display_round(current_round)
            if current_round.game_over:
                print(self.TITLE_COLOR + self.text.get('THANK_YOU'))
                self.confirm_exit()
                return "main_menu"
            choice = input(self.PROMPT_COLOR + self.text.get('ENTER_CHOICE') + Fore.WHITE)
            try:
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(options):
                    self.game_manager.process_option(option=options[choice_index])
                elif choice_index == len(options):
                    self.use_item()
                elif choice_index == len(options) + 1:
                    self.view_dialogue_history()
                elif choice_index == len(options) + 2:
                    if self.confirm_exit():
                        self.game_manager.save_game()
                        return "main_menu"
                else:
                    print(self.ERROR_COLOR + self.text.get('INVALID_CHOICE'))
                    time.sleep(1)
            except ValueError:
                print(self.ERROR_COLOR + self.text.get('INVALID_NUMBER'))
                time.sleep(1)

    def load_game_menu(self):
        while True:
            self.clear_screen()
            self.print_slowly(self.text.get('LOAD_GAME_TITLE'), color=self.TITLE_COLOR)
            save_files = self.game_manager.get_save_files()

            if not save_files:
                print(self.ERROR_COLOR + self.text.get('NO_SAVE_FILES'))
                input(self.PROMPT_COLOR + self.text.get('PRESS_ENTER') + Fore.WHITE)
                return None

            for i, save_file in enumerate(save_files, 1):
                print(self.DYNAMIC_OPTION_COLOR + f"{i}. {save_file}")
            print(self.FIXED_OPTION_COLOR + f"{len(save_files) + 1}. {self.text.get('RETURN_TO_MAIN_MENU')}")

            choice = input(self.PROMPT_COLOR + self.text.get('CHOOSE_SAVE_FILE') + Fore.WHITE)
            if choice.isdigit():
                choice = int(choice)
                if 1 <= choice <= len(save_files):
                    return save_files[choice - 1]
                elif choice == len(save_files) + 1:
                    return None

            print(self.ERROR_COLOR + self.text.get('INVALID_CHOICE'))
            time.sleep(1)

    def run(self):
        while True:
            action = self.main_menu()

            if action == "new_game":
                keywords = self.new_game_setup()
                self.game_manager.start_new_game(keywords)
            elif action == "load_game":
                save_file = self.load_game_menu()
                if save_file:
                    if self.game_manager.load_game(save_file):
                        print(self.TITLE_COLOR + self.text.get('GAME_LOADED_SUCCESSFULLY'))
                    else:
                        print(self.ERROR_COLOR + self.text.get('FAILED_TO_LOAD_GAME'))
                else:
                    continue  # Return to main menu
            elif action == "quit":
                print(self.TITLE_COLOR + self.text.get('THANK_YOU'))
                sys.exit()

            result = self.game_loop()
            if result != "main_menu":
                break
