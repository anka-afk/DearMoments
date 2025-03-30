# 标签生成器
class LabelGenerator:
    def __init__(self, llm_service, max_examples=5):
        self.llm_service = llm_service
        self.max_examples = max_examples
        self.labels = {}  # 聚类ID -> 标签映射

    def generate_label(self, cluster_id, cluster_data, summaries):
        """为聚类生成标签

        Args:
            cluster_id (int): 聚类ID
            cluster_data (list): 聚类数据
            summaries (list): 摘要列表
        """
        # 选择聚类中的代表性样本
        sample_indices = cluster_data[: self.max_examples]
        examples = [summaries[i].text for i in sample_indices]

        # 提示词
        prompt = f"""
        以下是一组相关的对话摘要:

        {examples}

        请为这组摘要生成:
        1. 一个简短的标签（5个字以内）
        2. 一个更详细的主题描述（20字以内）
        3. 提取3-5个关键词

        回复格式:
        {{
            "label": "简短标签",
            "description": "更详细描述",
            "keywords": ["关键词1", "关键词2", "关键词3"]
        }}
        """

        # 调用LLM生成标签
        result = self.llm_service.generate(prompt)

        # 解析JSON结果
        import json

        try:
            label_data = json.loads(result)
            self.labels[cluster_id] = label_data
            return label_data
        except:
            # 解析失败, 选择备用方案
            return {
                "label": f"聚类 #{cluster_id}",
                "description": f"包含{len(cluster_data)}条记忆",
                "keywords": [],
            }
