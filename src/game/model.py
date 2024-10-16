from enum import Enum
from typing import List, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class YamlModel(BaseModel):
    def yaml(self):
        return yaml.dump(self.model_dump(), sort_keys=False, allow_unicode=True)


class Character(BaseModel):
    name: str = Field(..., description="Character name")
    role: str = Field(..., description="Character's role in the story (e.g., protagonist, antagonist, ally)")
    description: str = Field(..., description="Brief character description")


class Item(BaseModel):
    name: str = Field(..., description="Name of the item")
    description: str = Field(..., description="Brief description of the item and its significance")

    def __str__(self):
        return f"{self.name}: {self.description}"


class GameStory(YamlModel):
    title: str = Field(..., description="Engaging title for the TRPG adventure")
    setting: str = Field(..., description="Brief description of the world or environment where the story takes place")
    main_conflict: str = Field(..., description="The central problem or challenge driving the story")
    key_characters: List[Character] = Field(..., description="List of key characters in the adventure")
    key_items: List[Item] = Field(..., description="List of important items in the adventure")


class Choice(BaseModel):
    text: str = Field(..., description="Text description of the option")
    requires_roll: Optional[bool] = Field(False, description="Whether this choice requires a dice roll")
    success_threshold: Optional[int] = Field(10,
                                             description="Threshold for success if requires_roll is true with max value 19")

    def __str__(self):
        return self.text if not self.requires_roll else f"{self.text} (R{self.success_threshold})"

    @field_validator('success_threshold', mode="before")
    def set_success_threshold_default(cls, v):
        return 10 if v is None else v

    @field_validator('requires_roll', mode="before")
    def set_requires_roll_default(cls, v):
        return False if v is None else v


class GameRound(BaseModel):
    narrative: str = Field(..., description="Detailed text description of the current scenario and its consequences")
    choices: List[Choice] = Field(..., description="List of available choices for the player")
    get_items: Optional[List[Item]] = Field([], description="List of items that the player has got in this round")
    lose_items: Optional[List[Item]] = Field([], description="List of items to be removed from the player's inventory")
    game_over: bool = Field(..., description="Whether the game has ended")

    @field_validator('get_items', mode="before")
    def set_get_items_default(cls, v):
        return [] if v is None else v

    @field_validator('lose_items', mode="before")
    def set_lose_items_default(cls, v):
        return [] if v is None else v


class KeyGameInformation(YamlModel):
    plot_developments: List[str] = Field(..., description="List of recent significant plot developments")
    summary_of_recent_events: str = Field(...,
                                          description="A concise paragraph summarizing the most recent and significant events in the game")


class RecordType(str, Enum):
    TURN_DESCRIPTION = "GAME MASTER"
    PLAYER_CHOICE = "PLAYER"
    ITEM_ACQUIRED = "PLAYER GET ITEM"
    ITEM_USED = "PLAYER USE ITEM"
    ITEM_REMOVED = "PLAYER LOSE ITEM"


class GameRecord(BaseModel):
    record_type: RecordType = Field(..., description="Type of the game record")
    text: str = Field(..., description="Detailed description of the record")

    def __str__(self):
        return f"{self.record_type.value}: {self.text}"
