import json
import os
import random
from typing import List

from src.config import save_dir
from src.llm.game_master import GameMaster
from src.llm.record_keeper import RecordKeeper
from src.llm.story_generator import StoryGenerator
from .game_state import GameState
from .model import Choice, GameRecord, GameRound, Item, RecordType


class GameManager:
    def __init__(self):
        self.game_state: GameState | None = None
        self.game_master: GameMaster | None = None
        self.record_keeper: RecordKeeper | None = None

    def start_new_game(self, keywords) -> bool:
        story = StoryGenerator().generate_story(keywords)
        if not story:
            print("Failed to generate story")
            return False
        self.game_master = GameMaster(game_story=story)
        next_round = self.game_master.next_round()
        if not next_round:
            print("Failed to generate first round")
            return False
        self.game_state = GameState(game_story=story, current_round=next_round)
        self.record_keeper = RecordKeeper(game_story=story)
        self.process_round(next_round)
        return True

    def get_current_round(self) -> GameRound:
        return self.game_state.current_round

    def process_round(self, next_round: GameRound):
        # 更新、记录Item
        for item in next_round.lose_items:
            self.game_state.remove_item(item)
            self.game_state.add_record(GameRecord(
                record_type=RecordType.ITEM_REMOVED,
                text=f"{item.name}:{item.description}"
            ))

        for item in next_round.get_items:
            self.game_state.add_item(item)
            self.game_state.add_record(GameRecord(
                record_type=RecordType.ITEM_ACQUIRED,
                text=f"{item.name}:{item.description}"
            ))

        # 记录Round Record
        self.game_state.records.append(GameRecord(
            record_type=RecordType.TURN_DESCRIPTION,
            text=next_round.narrative))
        self.game_state.current_round = next_round

    def process_option(self, option: Choice = None, item: Item = None):
        # 记录玩家Record
        player_record = None
        if option is not None:
            player_record = GameRecord(
                record_type=RecordType.PLAYER_CHOICE,
                text=option.text if not option.requires_roll else f"{option.text} (roll: {random.randint(1, 20)} / success threshold: {option.success_threshold})"
            )
        elif item is not None:
            player_record = GameRecord(
                record_type=RecordType.ITEM_USED,
                text=f"{item.name}:{item.description}"
            )
            self.game_state.remove_item(item)
        # 整理 recent_interactions
        next_key_info = self.record_keeper.summary(
            key_game_info=self.game_state.key_information,
            recent_interactions=self.get_recent_interactions(round_num=50)
        )
        if not next_key_info:
            print("RK Failed")
            return
        next_round = self.game_master.next_round(
            current_player_choice=str(player_record),
            key_game_info=next_key_info,
            recent_interactions=self.get_recent_interactions(round_num=10)
        )
        if not next_round:
            print("GM Failed")
            return
        self.game_state.key_information = next_key_info
        self.game_state.records.append(player_record)
        self.process_round(next_round)
        # AutoSave
        self.save_game()

    def get_dialogue_history(self) -> List[GameRecord]:
        return self.game_state.records

    def get_inventory(self) -> List[Item]:
        return list(self.game_state.inventory.values())

    def get_recent_interactions(self, round_num=10) -> List[str]:
        return [str(r) for r in self.game_state.records[-round_num * 2:]]

    def get_save_files(self):
        if not os.path.exists(save_dir):
            return []
        return [f for f in os.listdir(save_dir) if f.endswith('.json')]

    def load_game(self, save_file):
        file_path = os.path.join(save_dir, save_file)
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.game_state = GameState.from_dict(data)
                self.game_master = GameMaster(self.game_state.game_story)
                self.record_keeper = RecordKeeper(self.game_state.game_story)
            return True
        return False

    def save_game(self, save_name=None):
        if not save_name:
            save_name = f"AUTO_SAVE_{self.game_state.game_story.title}"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        file_path = os.path.join(save_dir, f"{save_name}.json")
        with open(file_path, 'w') as f:
            json.dump(self.game_state.to_dict(), f)
