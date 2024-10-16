import traceback
from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

from src.config import ollama_url, model_name, debug, lang
from src.game.model import KeyGameInformation, GameStory

PROMPT_TEMPLATE = """
You are an AI designed to act as a game recorder for a Text-Based Role-Playing Game (TRPG). Your primary function is to analyze the provided information, summarize recent events, and update the key story elements. This summary will serve as a reference for both the Game Master (GM) and future iterations of yourself.

## Guidelines

1. Information Analysis:
   - Carefully review the game outline, current key information, and recent interactions.
   - Identify new developments, changes, and significant events.
   - Look for connections between recent events and the overall plot.

2. Updating Key Information:
   - Plot Developments: Highlight major story progressions or revelations.
   - Character Updates: Note any significant changes in character status, relationships, or development.
   - World State Changes: Record any alterations to the game world or setting.
   - Important Items or Clues: List new items or information crucial to the plot.
   - Unresolved Plot Threads: Keep track of ongoing storylines or newly introduced mysteries.
   - Upcoming Challenges or Events: Anticipate potential future scenarios based on current developments.

3. Summarizing Recent Events:
   - Provide a concise yet comprehensive summary of the most recent and significant events.
   - Focus on events that have a direct impact on the main plot or character development.
   - Use clear and engaging language to capture the essence of what has transpired.

4. Consistency and Continuity:
   - Ensure that new information aligns with the established game outline and previous key information.
   - Highlight any apparent inconsistencies or potential plot holes for the GM's attention.

5. Relevance and Conciseness:
   - Prioritize information that is most relevant to the ongoing story and character arcs.
   - Be concise in your updates, focusing on quality over quantity.

6. Objectivity:
   - Maintain an objective tone, focusing on facts and observable developments.
   - Avoid speculative interpretation unless it's clearly marked as such.

7. Adaptability:
   - Be prepared to adjust the format or focus of your summary based on the specific needs of the game or GM.

## Input Information

{story_outline}

{key_game_info}

Recent Game Master and Player Interactions:

{recent_interactions}

## Output Format

{format_instructions}

Remember, your role is to assist in maintaining a coherent and engaging narrative. Your summaries and updates should help the GM and future iterations of yourself to quickly understand the current state of the game and its key elements. Reply to the best of your ability in {language}.
"""


class RecordKeeper:
    def __init__(self, game_story: GameStory):
        self.parser = PydanticOutputParser(pydantic_object=KeyGameInformation)
        self.template = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=["key_game_info", "recent_interactions"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions(),
                "story_outline": f"""
                Story Outline:
                ```yaml
                {game_story.yaml()}
                ```
                """,
                "language": lang
            }
        )

        self.llm = OllamaLLM(
            base_url=ollama_url,
            model=model_name,
            temperature=0.3,
            num_predict=4096,
            num_ctx=10240,
        )

    def summary(self, recent_interactions: List[str],
                key_game_info: KeyGameInformation = None,
                retry_times=3) -> KeyGameInformation:

        ri = "\n\n".join(recent_interactions) if recent_interactions else ""

        full_prompt = self.template.format(
            key_game_info=f"""
            Key Game Information:
            ```yaml
                {key_game_info.yaml()}
            ```
            """ if key_game_info else "",
            recent_interactions=f"""
            Recent Game Master and Player Interactions:
            {ri}
            """ if recent_interactions else "",
        )
        original_output = None
        for i in range(retry_times):
            try:
                original_output = self.llm.invoke(full_prompt)
                adventure = self.parser.parse(original_output)
                return adventure
            except Exception as e:
                if debug:
                    print(e)
                    print(traceback.format_exc())
                    print(original_output)
