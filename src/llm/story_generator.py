import random
import traceback

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

from src.config import ollama_url, model_name, debug, lang
from src.game.model import GameStory

PROMPT_TEMPLATE = """
You are a creative writer specializing in crafting engaging and coherent story outlines for Text-Based Role-Playing Games (TRPGs). Your task is to create a compelling story outline based on the keywords for game theme provided by the user. This outline will serve as the foundation for a TRPG adventure.

IMPORTANT: You must ONLY respond with valid JSON. Do not include any text outside of the JSON structure.

## Guidelines

1. Story Structure:
   - Create a compelling narrative arc with a clear beginning, middle, and end.
   - Ensure the story has a strong central conflict that drives the plot.
   - Incorporate multiple decision points that allow for player agency.

2. World Building:
   - Develop a rich and interesting setting that complements the story themes.
   - Create a consistent internal logic for the world.

3. Character Development:
   - Design memorable and diverse characters with clear motivations.
   - Include both allies and antagonists to create a dynamic story.

4. Player Engagement:
   - Incorporate elements that encourage role-playing and character development.
   - Balance linear storytelling with opportunities for player choice.

5. Themes and Depth:
   - Weave the provided themes throughout the story in meaningful ways.
   - Explore complex ideas while maintaining accessibility for the target audience.

6. Adaptability:
   - Design the outline to be flexible enough to accommodate various player choices.
   - Include potential branching paths or alternative scenarios.

7. Pacing:
   - Vary the pacing to include moments of action, exploration, dialogue, and reflection.
   - Ensure the story length aligns with the desired length provided.

8. Integration of Keywords:
   - Creatively incorporate the provided keywords into the story elements.
   - Use keywords to inspire unique story elements, characters, or plot points.

## Input Information

Keywords: {keywords}

## Output Format

{format_instructions}

Remember:Only output valid JSON. Do not include any explanations, confirmations, or additional text outside the JSON structure. Craft a story that is engaging, logical, and coherent, providing a solid foundation for an immersive TRPG experience. Adapt your writing style and complexity to suit the specified target audience. Reply to the best of your ability in {language}.
"""

DEFAULT_KEYWORDS = ["magic", "adventure", "dungeon", "dragon", "sword and sorcery", "role-playing", "fantasy world",
                    "quest", "monster", "treasure", "rise of a hero", "saving the world", "journey of revenge",
                    "treasure hunt", "stopping evil", "solving mysteries", "kingdom conflicts", "time travel",
                    "artifact pursuit", "racial conflict",
                    "cosmic horror", "sanity", "investigation", "mythos", "eldritch", "cultists", "forbidden knowledge",
                    "ancient artifacts", "paranormal", "occult", "madness", "lovecraftian", "supernatural", "mystery",
                    "secret societies", "otherworldly entities", "arcane rituals", "cosmic indifference",
                    "unspeakable horrors"]


class StoryGenerator:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=GameStory)
        self.template = PromptTemplate(
            template=PROMPT_TEMPLATE,
            input_variables=["keywords"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions(),
                "language": lang
            }
        )

        self.llm = OllamaLLM(
            base_url=ollama_url,
            model=model_name,
            temperature=0.5,
            num_predict=4096,
            num_ctx=10240,
        )

    def generate_story(self, keywords: list[str] = None, retry_times=3) -> GameStory:
        if not keywords:
            keywords = random.choices(DEFAULT_KEYWORDS, k=7)

        full_prompt = self.template.format(
            keywords=",".join(keywords)
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


if __name__ == '__main__':
    sg = StoryGenerator()
    print(sg.generate_story(["romantic", "adventure"]))
    print(sg.generate_story())
