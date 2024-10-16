import traceback
from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama

from src.config import ollama_url, model_name, debug, lang
from src.game.model import GameRound, KeyGameInformation, GameStory, Item

PROMPT_TEMPLATE = """
You are the Game Master (GM) for a Text-Based Role-Playing Game (TRPG). Create and narrate an engaging, coherent, and complete story through text, while managing game mechanics and player interactions. 

IMPORTANT: You must ONLY respond with valid JSON. Do not include any text outside of the JSON structure.

## Game Mechanics and Responsibilities

1. Present multiple text-based choices for each scene.
2. Specify D20 die roll requirements and success thresholds when applicable.
3. Manage item acquisition and usage.
4. Host an exciting, complete, and coherent text-based RPG game.
5. Ensure moderate game length and difficulty, with a definite conclusion.
6. Interpret D20 roll results:
   - 1: Critical failure (severe penalty)
   - 20: Critical success (extra reward)
   - ≥ Success threshold: Success
   - < Success threshold: Failure
7. Refer to provided game state information and story outline for story progression and continuity.
8. Clearly indicate when the game has ended.

## Guidelines

1. Story Integration:
   - Use the provided story outline as a guide for the overall narrative arc.
   - Adapt the story based on player choices while staying true to the main themes and conflicts.
   - Track progress through the story outline using the "current_chapter" field in your output.

2. Item Management:
   - Use "get_items" for both newly acquired items and updated items.
   - Use "lose_items" for the items that need to be removed.
   - Ensure item names remain consistent throughout the game.
   - Player's current inventory will be listed if not empty.

3. External References:
   - Utilize the provided game state information and story outline to maintain continuity and coherence.
   - Incorporate key game information, recent interactions, and the current player choice into your narrative and decision-making.

4. Storytelling:
   - Maintain a coherent narrative with clear plot progression.
   - Balance adherence to the story outline with flexibility for player choices.
   - Incorporate side quests and key items from the story outline when appropriate.

5. World Building:
   - Use the setting description from the story outline to create a rich, consistent world.
   - Provide vivid descriptions engaging multiple senses.

6. Character Integration:
   - Introduce and develop key characters from the story outline.
   - Ensure character motivations and actions align with their descriptions.

7. Game Mechanics:
   - Use the D20 system for skill checks and combat.
   - Always provide multiple choice options for player decisions.
   - Some options require D20 rolls to determine success.
   - Allow players to use items at any time, which may affect the story.

8. Player Interaction:
   - Respond creatively to player actions and item usage.
   - Encourage role-playing and character development.

9. Continuity:
    - Use provided game state information and story outline to keep track of key events, player decisions, and inventory.
    - Regularly incorporate important elements from the game state and story outline into the narrative.

10. Pacing:
    - Vary between action, exploration, dialogue, and puzzles.
    - Use cliffhangers to maintain interest.
    - Align pacing with the chapter structure from the story outline.

12. Adaptability:
    - Improvise for unexpected player choices while trying to guide the story back to the main plot points.
    - Adjust difficulty based on player skill and game progression.
    
13. Preventing Repetitive Dialogue:

    - Keep track of recent interactions and avoid repeating similar scenarios or dialogue.
    - Introduce new elements, characters, or challenges to move the story forward if it seems to stall.
    - Use the 'current_chapter' field to ensure progression through the story outline.
    - If players seem stuck, provide subtle hints or introduce unexpected events to guide them towards the main plot.
    - Regularly review and reference the game state to ensure the narrative is advancing and not looping.

{story_outline}

{key_game_info}

{player_inventory}

## Output Format

{format_instructions}

Remember: Prioritize player enjoyment and immersion. Adapt these guidelines as needed for the best experience. Only output valid JSON. Do not include any explanations, confirmations, or additional text outside the JSON structure. Reply to the best of your ability in {language}.

{interactions}

"""

STORY_OUTLINE_TEMPLATE = """

## Story Outline
```yaml
{story_outline}
```

"""

GAME_STATE_TEMPLATE = """

## Game State Information
```yaml
{game_state}
```

"""

RECENT_INTERACTIONS_TEMPLATE = """

## Recent Interactions

{recent_interactions}

{current_player_choice}

"""

PLAYER_INVENTORY_TEMPLATE = """

## Player's Inventory

{player_inventory}

"""


class GameMaster:
    def __init__(self, game_story: GameStory):
        self.parser = PydanticOutputParser(pydantic_object=GameRound)
        self.template = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=["key_game_info", "player_inventory", "interactions"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions(),
                "story_outline": STORY_OUTLINE_TEMPLATE.format(story_outline=game_story.yaml()),
                "language": lang
            }
        )

        self.llm = ChatOllama(
            base_url=ollama_url,
            model=model_name,
            temperature=0.7,
            num_predict=4096,
            num_ctx=10240,
            repeat_last_n=1024,
        )

    def next_round(self,
                   current_player_choice: str = None,
                   key_game_info: KeyGameInformation = None,
                   recent_interactions: List[str] = None,
                   player_inventory: List[Item] = None,
                   retry_times=3
                   ) -> GameRound:
        ri = "\n\n".join(recent_interactions) if recent_interactions else ""
        interactions = RECENT_INTERACTIONS_TEMPLATE.format(recent_interactions=ri,
                                                           current_player_choice=current_player_choice)
        full_prompt = self.template.format(
            key_game_info=GAME_STATE_TEMPLATE.format(game_state=key_game_info.yaml()) if key_game_info else "",
            player_inventory=PLAYER_INVENTORY_TEMPLATE.format(
                player_inventory="\n".join([str(item) for item in player_inventory]) if player_inventory else ""),
            interactions=interactions
        )
        original_output = None

        for i in range(retry_times):
            try:
                # original_output = self.llm.invoke(full_prompt)
                original_output = self.llm.invoke(input=full_prompt).content
                game_round = self.parser.parse(original_output)
                return game_round
            except Exception as e:
                if debug:
                    print(e)
                    print(traceback.format_exc())
                    print(original_output)
