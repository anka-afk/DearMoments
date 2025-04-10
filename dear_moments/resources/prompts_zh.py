class StoragePrompts:
    """
    存储方向的prompts集合
    """

    @classmethod
    def get_information_extract_prompt(
        cls,
        system_prompt: str,
        examples: str,
        conversations: str,
        topic_examples: str,
        tab: str = " ",
    ) -> str:
        """
        获取信息提取的提示词

        Args:
            system_prompt (str): 系统提示词
            examples (str): 示例提示词
            conversations (str): 对话内容
            topic_examples (str): 主题示例
            tab (str): 分隔符，默认为空格
        """

        information_extract_prompt: str = f"""
        你是一位专业的心理学家。
        你的责任是仔细阅读用户与其他方的对话。然后提取相关且重要的事实、用户偏好，这些信息将有助于评估用户的状态。
        你不仅要提取明确陈述的信息，还要推断对话中隐含的信息。
        请注意，你要准确地提取和推断用户相关(user)的信息，而非其他方(assistant)的。


        FACT_RETRIEVAL_PROMPT = {system_prompt}

        ## 格式
        ### 输入
        #### 主题建议
        这个章节里会放一些主题和子主题的建议，你需要参考这些主题和子主题来提取信息。
        如果你认为有必要，可以创建自己的主题/子主题，除非用户明确要求不要创建新的主题/子主题。
        #### 已有的主题
        这个章节中会放用户已经与助手分享的主题和子主题
        如果对话中再次提到相同的主题/子主题，请考虑使用相同的主题/子主题。
        #### 对话
        输入的格式是用户和另一方的对话:
        - [TIME] NAME: MESSAGE
        其中NAME有时候是user，有时候是assistant。
        MESSAGE则是对话内容. 理解对话内容并且记住事情发生的时间

        ### 输出
        你需要从对话中提取事实和偏好，并按顺序列出：
        - TOPIC{tab}SUB_TOPIC{tab}MEMO
        例如：
        - 基本信息{tab}姓名{tab}melinda
        - 工作{tab}职称{tab}软件工程师

        每行代表一个事实或偏好，包含：
        1. TOPIC: 主题，表示该偏好的类别
        2. SUB_TOPIC: 详细主题，表示该偏好的具体类别
        3. MEMO: 提取的信息、事实或偏好
        这些元素应以 `{tab}` 分隔，每行应以 `\n` 分隔，并以 "- " 开头。

        ## 示例
        以下是一些示例：
        {examples}

        请按上述格式返回事实和偏好。

        请记住以下几点：
        - 如果用户有提到时间敏感的信息，试图推理出具体的日期.
        - 当可能时，请使用具体日期，而不是使用“今天”或“昨天”等相对时间。
        - 如果在以下对话中没有找到任何相关信息，可以返回空列表。
        - 确保按照格式和示例部分中提到的格式返回响应。
        - 你应该推断对话中隐含的内容，而不仅仅是明确陈述的内容。
        - 相同的内容不需要在不同的 topic 和 sub_topic 下重复，选择最相关的主题和子主题即可。
        - 相同的 topic 和 sub_topic 只能出现一次。
        忽视用户(user)对其他方(assistant)的称呼：比如用户称呼其他方(assistant)为小姨，因为对其他方的称呼不一定代表真实的关系，不需要推断用户有一个小姨， 只需要记录用户称呼其他方为小姨即可

        以下是用户和助手之间的对话。你需要从对话中提取/推断相关的事实和偏好，并按上述格式返回。
        请注意，你要准确地提取和推断用户相关(user)的信息，而非其他方(assistant)的。
        你应该检测用户输入的语言，并用相同的语言记录事实。如果在以下对话中没有找到任何相关事实、用户记忆和偏好，你可以返回"NONE"或"NO FACTS"。

        {conversations}

        #### 主题建议
        以下是一些主题和子主题的建议，你需要参考这些主题和子主题来提取信息。
        {topic_examples}
        """
        return information_extract_prompt
