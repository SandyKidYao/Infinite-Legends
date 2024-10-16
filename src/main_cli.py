from cli.cli_ui import CLIUI
from game.game_manager import GameManager
from src.config import lang

"""
TODO:
1. RK可以使用小模型，然后输入更长的Interactions
2. 解决GM无法推进游戏的问题，会产生重复输出
3. 控制RK的总结范围和频率，在超出对话长度后进行总结，防止GM看到KI与RI有Overlap
"""


def main():
    game_manager = GameManager()
    ui = CLIUI(game_manager, lang)
    ui.run()


if __name__ == "__main__":
    main()
