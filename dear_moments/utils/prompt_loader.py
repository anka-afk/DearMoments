class PromptLoader:
    """
    根据语言读取本地的提示词文件
    """

    def __init__(self, language: str):
        self.language = language
