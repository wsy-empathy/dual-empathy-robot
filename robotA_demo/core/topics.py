"""
Topics and Subtopics Configuration
话题与子话题配置
"""

TOPICS = {
    "academic": {
        "ja": "学業のこと",
        "zh": "学业方面",
        "subtopics": {
            "follow_content": {
                "ja": "授業の内容についていくことが難しい",
                "zh": "跟上课程内容有困难"
            },
            "study_pace": {
                "ja": "勉強のペースや習慣をうまく整えられない",
                "zh": "难以建立稳定的学习节奏或学习习惯"
            },
            "exam_anxiety": {
                "ja": "試験や成績のことに不安がある",
                "zh": "对考试或成绩感到不安"
            }
        }
    },
    "future": {
        "ja": "進路・将来のこと",
        "zh": "发展与未来方面",
        "subtopics": {
            "unclear_goals": {
                "ja": "卒業後にやりたいことがまだはっきりしていない",
                "zh": "毕业后想做什么还不明确"
            },
            "career_choice": {
                "ja": "就職するか進学するかで迷っている",
                "zh": "在就业还是升学之间犹豫"
            },
            "preparation": {
                "ja": "将来に向けて何を準備すればよいかわからない",
                "zh": "不知道该为未来做哪些准备"
            }
        }
    },
    "financial": {
        "ja": "経済面のこと",
        "zh": "经济方面",
        "subtopics": {
            "cost_burden": {
                "ja": "学費や生活費の負担が大きい",
                "zh": "学费或生活费负担较大"
            },
            "work_study_balance": {
                "ja": "アルバイトと勉強を両立することが難しい",
                "zh": "兼职与学习难以兼顾"
            },
            "financial_anxiety": {
                "ja": "奨学金や今後のお金の見通しに不安がある",
                "zh": "对奖学金或今后的经济状况感到不安"
            }
        }
    },
    "relationship": {
        "ja": "学内の友人関係のこと",
        "zh": "校内同伴关系方面",
        "subtopics": {
            "making_friends": {
                "ja": "学内で友人をつくることが難しい",
                "zh": "在学校里难以交到朋友"
            },
            "interaction_issues": {
                "ja": "友人や同級生との付き合い方に悩みがある",
                "zh": "在与朋友或同学相处方式上有困扰"
            },
            "no_confidant": {
                "ja": "学内で気軽に相談できる相手がいない",
                "zh": "在学校里没有可以轻松倾诉或商量的人"
            }
        }
    }
}

# 交互流程阶段定义
DIALOGUE_STAGES = {
    "entry": {
        "name": "Entry",
        "steps": ["topic_selection", "subtopic_selection", "initial_description"]
    },
    "aer_1": {"name": "AER Round 1", "strategy": "M+N/U+E"},
    "aer_2": {"name": "AER Round 2", "strategy": "M+R+E"},
    "aer_3": {"name": "AER Round 3", "strategy": "M+S+E"},
    "aer_transition": {"name": "AER Transition to CER"},
    "cer_1": {"name": "CER Round 1", "strategy": "PT"},
    "cer_2": {"name": "CER Round 2", "strategy": "Mz"},
    "cer_3": {"name": "CER Round 3", "strategy": "Advice"},
    "aer_closing_1": {"name": "AER Closing 1", "strategy": "M+R"},
    "aer_closing_2": {"name": "AER Closing 2", "strategy": "M+S"}
}

# NURSE策略（AER使用）
NURSE_STRATEGIES = {
    "N": "Name - 命名情绪",
    "U": "Understand - 表达理解",
    "R": "Respect - 尊重感受",
    "S": "Support - 提供支持",
    "E": "Explore - 推动表达（感受导向）"
}

# CER策略
CER_STRATEGIES = {
    "PT": "Perspective-Taking - 视角采择",
    "Mz": "Mentalizing - 心智化建模",
    "Advice": "具体可执行建议"
}


def get_topic_list():
    """获取所有大topic列表"""
    return [(key, data["ja"], data["zh"]) for key, data in TOPICS.items()]


def get_subtopic_list(topic_key):
    """获取指定topic下的所有subtopic列表"""
    if topic_key not in TOPICS:
        return []
    return [
        (key, data["ja"], data["zh"]) 
        for key, data in TOPICS[topic_key]["subtopics"].items()
    ]


def get_topic_name(topic_key, lang="ja"):
    """获取topic名称"""
    if topic_key not in TOPICS:
        return ""
    return TOPICS[topic_key].get(lang, "")


def get_subtopic_name(topic_key, subtopic_key, lang="ja"):
    """获取subtopic名称"""
    if topic_key not in TOPICS:
        return ""
    if subtopic_key not in TOPICS[topic_key]["subtopics"]:
        return ""
    return TOPICS[topic_key]["subtopics"][subtopic_key].get(lang, "")
