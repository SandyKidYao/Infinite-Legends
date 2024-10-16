class TextZH:
    # 主菜单
    GAME_TITLE = "=== 无尽传说：一个AI驱动的TRPG游戏 ==="
    NEW_GAME = "新游戏"
    LOAD_GAME = "加载游戏"
    QUIT = "退出"
    ENTER_CHOICE = "请输入您的选择: "
    INVALID_CHOICE = "无效的选择。请重试。"

    # 游戏设置
    ENTER_KEYWORDS = "请输入游戏主题关键词（按回车键继续...）:"
    KEYWORD_PROMPT = "> "

    # 对话
    DIALOGUE_TITLE = "=== 对话 ==="

    # 库存
    INVENTORY_TITLE = "=== 库存 ==="
    INVENTORY_EMPTY = "您的库存是空的。"
    PRESS_ENTER = "按回车键继续..."

    # 使用物品
    USE_ITEM_TITLE = "=== 使用物品 ==="
    CHOOSE_ITEM = "选择要使用的物品（或按回车键取消）: "
    USING_ITEM = "正在使用{}..."
    ITEM_USED = "{}已被使用并从您的库存中移除。"
    CANCELLED_ITEM_USE = "已取消使用物品。"

    # 选项
    OPTIONS_TITLE = "=== 选项 ==="
    VIEW_INVENTORY = "查看库存"
    USE_ITEM = "使用物品"
    VIEW_HISTORY = "查看对话历史"
    RETURN_TO_MAIN_MENU = "返回主菜单"

    # 对话历史
    HISTORY_TITLE = "=== 对话历史 ==="

    # 退出确认
    EXIT_CONFIRM = "您确定要返回主菜单吗？您的进度将被保存。(y/n): "
    INVALID_YES_NO = "无效的输入。请输入'y'或'n'。"

    # 游戏结束
    THANK_YOU = "感谢您的游玩。再见！"

    # 错误信息
    NO_SAVE_FOUND = "未找到已保存的游戏。正在开始新游戏。"
    INVALID_NUMBER = "无效的输入。请输入一个数字。"

    # 游戏开始
    GAME_START = "正在开始一个新游戏，主题为: {}"

    # New texts for save file selection
    LOAD_GAME_TITLE = "=== 加载游戏 ==="
    NO_SAVE_FILES = "未找到存档文件。"
    CHOOSE_SAVE_FILE = "选择要加载的存档文件（或输入数字返回主菜单）: "
    GAME_LOADED_SUCCESSFULLY = "游戏加载成功。"
    FAILED_TO_LOAD_GAME = "加载游戏失败。正在开始新游戏。"

    @classmethod
    def get(cls, key, *args):
        return getattr(cls, key).format(*args) if args else getattr(cls, key)
