from typing import List, Dict

from .model import GameStory, Item, GameRound, GameRecord, KeyGameInformation


class GameState:
    def __init__(self, game_story: GameStory, current_round: GameRound):
        self.game_story = game_story
        self.current_round: GameRound = current_round
        self.inventory: Dict[str, Item] = dict()
        self.records: List[GameRecord] = []
        self.key_information: KeyGameInformation | None = None

    def add_record(self, record: GameRecord):
        self.records.append(record)

    def add_item(self, item: Item):
        self.inventory[item.name] = item

    def remove_item(self, item: Item):
        self.inventory.pop(item.name, None)

    def to_dict(self):
        return {
            "game_story": self.game_story.json(),
            "current_round": self.current_round.json(),
            "inventory": [item.json() for item in self.inventory.values()],
            "records": [record.json() for record in self.records],
            "key_information": self.key_information.json() if self.key_information else None
        }

    @classmethod
    def from_dict(cls, data):
        cls.game_story = GameStory.parse_raw(data["game_story"])
        cls.current_round = GameRound.parse_raw(data["current_round"])
        cls.inventory = {item["name"]: Item.parse_raw(item) for item in data["inventory"]}
        cls.records = [GameRecord.parse_raw(record_data) for record_data in data["records"]]
        cls.key_information = KeyGameInformation.parse_raw(data["key_information"]) if data[
            "key_information"] else None
        return cls
