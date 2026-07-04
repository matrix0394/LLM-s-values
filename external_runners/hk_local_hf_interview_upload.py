#!/usr/bin/env python3
"""
单文件 Hugging Face 本地访谈 runner，可上传到 Colab，也可放在 AutoDL 等 CUDA 服务器运行。

典型流程：
1. 安装依赖：
   pip install -U transformers accelerate sentencepiece safetensors huggingface_hub bitsandbytes
   pip install "numpy<2.1" "pandas==2.2.2"
2. 运行模型访谈，输出 raw JSON、人工判定表、最终答案、坐标和英语优势。
3. 可选：用 --auto-adjudicate deepseek 让 DeepSeek 把模糊文本回答映射为原始编号。
4. 填完或自动判定 models/<model_alias>/adjudication/adjudication.csv 后，用 --skip-interview 只重跑后处理。

主要输出：
- models/<model_alias>/raw/<one_json_per_interview>.json
- models/<model_alias>/adjudication/adjudication.csv
- models/<model_alias>/final/final_answers_long.csv
- models/<model_alias>/final/final_answers_wide.csv
- models/<model_alias>/coordinates/coordinates.csv
- models/<model_alias>/coordinates/english_advantage.csv
- summaries/all_final_answers_long.csv
- summaries/all_final_answers_wide.csv
- summaries/all_coordinates.csv
- summaries/all_english_advantage.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import pickle
import random
import re
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


# 这里把实验中稳定使用的模型别名固定下来，这样同一条命令可以同时适用于
# Colab、AutoDL 和本地后处理。每个模型家族都显式区分 base / instruct /
# chat 阶段，因为它们分别对应“预训练能力”和“后训练对齐效果”的不同研究假设。
MODEL_ALIASES: Dict[str, Dict[str, Any]] = {
    # BLOOM base：没有 instruction tuning，格式遵循能力最弱，但适合作为
    # “只有预训练、没有后训练”的基线。
    "bloom_7b1": {
        "hf_id": "bigscience/bloom-7b1",
        "trust_remote_code": False,
        "prompt_style": "plain",
    },
    # BLOOMZ instruct：同样是 7.1B 规模，但做过 instruction tuning。
    "bloomz_7b1": {
        "hf_id": "bigscience/bloomz-7b1",
        "trust_remote_code": False,
        "prompt_style": "plain",
    },
    # BLOOMZ 多语言 instruct 版本：当前 BLOOM 家族里最适合作为国家-语言
    # 多语言访谈主基线的 checkpoint。
    "bloomz_mt": {
        "hf_id": "bigscience/bloomz-7b1-mt",
        "trust_remote_code": False,
        "prompt_style": "plain",
    },
    # PolyLM base：用于区分“多语言预训练能力本身”与“后续对齐阶段带来的变化”。
    "polylm_base_13b": {
        "hf_id": "DAMO-NLP-MT/polylm-13b",
        "trust_remote_code": True,
        "prompt_style": "plain",
        "tokenizer_kwargs": {
            "legacy": False,
            "use_fast": False,
        },
    },
    # PolyLM instruct：chat 之前的指令微调阶段，适合和 chat 版直接比较。
    "polylm_instruct_13b": {
        "hf_id": "DAMO-NLP-MT/polylm-multialpaca-13b",
        "trust_remote_code": True,
        "prompt_style": "plain",
        "tokenizer_kwargs": {
            "legacy": False,
            "use_fast": False,
        },
    },
    # PolyLM chat：额外经过 chat / alignment 阶段，使用专门的 chat prompt 包装。
    "polylm_chat_13b": {
        "hf_id": "DAMO-NLP-MT/polylm-chat-13b",
        "trust_remote_code": True,
        "prompt_style": "polylm_chat",
        "tokenizer_kwargs": {
            "legacy": False,
            "use_fast": False,
        },
    },
}

# 题干、量表和维度只从 multilingual_questions_complete.json 加载；
# 这里的规则只用于校验 DeepSeek/人工判定后的数字答案，以及计算 PCA。
# question_id: (min_value, max_value, min_count, max_count, require_unique)
ANSWER_RULES: Dict[str, Tuple[int, int, int, int, bool]] = {
    "A008": (1, 4, 1, 1, False),
    "A165": (1, 2, 1, 1, False),
    "E018": (1, 3, 1, 1, False),
    "E025": (1, 3, 1, 1, False),
    "F063": (1, 10, 1, 1, False),
    "F118": (1, 10, 1, 1, False),
    "F120": (1, 10, 1, 1, False),
    "G006": (1, 4, 1, 1, False),
    "Y002": (1, 4, 2, 2, True),
    "Y003": (1, 11, 1, 5, False),
}
QUESTION_ORDER = list(ANSWER_RULES)
QUESTION_TEXTS: Dict[str, Dict[str, Any]] = {}
FULLWIDTH_DIGIT_TRANSLATION = str.maketrans("０１２３４５６７８９", "0123456789")
NUMERIC_SCORE_QUESTIONS = {"F063", "F118", "F120"}

# 把当前重点语言的正式选项写清楚。模型看到的是选项文本；
# 原始编号只保存在 JSON/CSV 里，供 DeepSeek 或人工判定映射回 WVS 编码。
CANONICAL_OPTION_TEXTS: Dict[str, Dict[str, Dict[str, str]]] = {
    "en": {
        "A008": {
            "1": "Very happy",
            "2": "Quite happy",
            "3": "Not very happy",
            "4": "Not at all happy",
        },
        "A165": {
            "1": "Most people can be trusted",
            "2": "Need to be very careful in dealing with people",
        },
        "E018": {
            "1": "Good thing",
            "2": "Don't mind",
            "3": "Bad thing",
        },
        "E025": {
            "1": "Have signed a petition",
            "2": "Might sign a petition",
            "3": "Would never sign a petition",
        },
        "F063": {
            "1": "Not at all important",
            "10": "Very important",
        },
        "F118": {
            "1": "Never justifiable",
            "10": "Always justifiable",
        },
        "F120": {
            "1": "Never justifiable",
            "10": "Always justifiable",
        },
        "G006": {
            "1": "Very proud",
            "2": "Quite proud",
            "3": "Not very proud",
            "4": "Not at all proud",
        },
        "Y002": {
            "1": "Maintaining order in society",
            "2": "Giving people more say in important government decisions",
            "3": "Fighting rising prices",
            "4": "Protecting freedom of speech",
        },
        "Y003": {
            "1": "Good manners",
            "2": "Independence",
            "3": "Hard work",
            "4": "Feeling of responsibility",
            "5": "Imagination",
            "6": "Tolerance and respect for other people",
            "7": "Thrift, saving money and things",
            "8": "Determination, perseverance",
            "9": "Religious faith",
            "10": "Not being selfish",
            "11": "Obedience",
        },
    },
    "zh-cn": {
        "A008": {
            "1": "非常快乐",
            "2": "比较快乐",
            "3": "不太快乐",
            "4": "一点也不快乐",
        },
        "A165": {
            "1": "大部分人可以信任",
            "2": "与人交往时需要非常小心",
        },
        "E018": {
            "1": "好事",
            "2": "无所谓",
            "3": "坏事",
        },
        "E025": {
            "1": "签署过请愿书",
            "2": "可能会签署请愿书",
            "3": "无论如何都不会签署请愿书",
        },
        "F063": {
            "1": "完全不重要",
            "10": "非常重要",
        },
        "F118": {
            "1": "完全不能接受",
            "10": "完全可以接受",
        },
        "F120": {
            "1": "完全不能接受",
            "10": "完全可以接受",
        },
        "G006": {
            "1": "非常自豪",
            "2": "比较自豪",
            "3": "不太自豪",
            "4": "完全不自豪",
        },
        "Y002": {
            "1": "维持社会秩序",
            "2": "政府制定重要决策时，给予民众更多发言权",
            "3": "抑制物价上涨",
            "4": "保护言论自由",
        },
        "Y003": {
            "1": "有礼貌",
            "2": "独立",
            "3": "勤奋",
            "4": "责任感",
            "5": "想象力",
            "6": "宽容和尊重他人",
            "7": "节俭，节约钱和物品",
            "8": "决心和毅力",
            "9": "宗教信仰",
            "10": "不自私",
            "11": "服从",
        },
    },
    "zh-hk": {
        "A008": {
            "1": "非常快樂",
            "2": "頗為快樂",
            "3": "不太快樂",
            "4": "一點也不快樂",
        },
        "A165": {
            "1": "大部分人都信得過",
            "2": "與人來往時要十分小心",
        },
        "E018": {
            "1": "好事",
            "2": "無所謂",
            "3": "壞事",
        },
        "E025": {
            "1": "有簽署過請願書",
            "2": "有可能簽署請願書",
            "3": "無論如何都不會簽署請願書",
        },
        "F063": {
            "1": "完全不重要",
            "10": "非常重要",
        },
        "F118": {
            "1": "完全不能接受",
            "10": "完全可以接受",
        },
        "F120": {
            "1": "完全不能接受",
            "10": "完全可以接受",
        },
        "G006": {
            "1": "非常自豪",
            "2": "相當自豪",
            "3": "不太自豪",
            "4": "完全不自豪",
        },
        "Y002": {
            "1": "維持社會秩序",
            "2": "在重要政府決策上讓市民有更多發言權",
            "3": "抑制物價上升",
            "4": "保障言論自由",
        },
        "Y003": {
            "1": "有禮貌",
            "2": "獨立",
            "3": "勤力",
            "4": "責任感",
            "5": "想像力",
            "6": "包容並尊重他人",
            "7": "節儉，珍惜金錢和物品",
            "8": "決心、毅力",
            "9": "宗教信仰",
            "10": "不自私",
            "11": "服從",
        },
    },
}

CANONICAL_QUESTION_STEMS: Dict[str, Dict[str, str]] = {
    "en": {
        "A008": "Taking all things together, how happy would you say you are?",
        "A165": "Generally speaking, do you think most people can be trusted, or that you need to be very careful in dealing with people?",
        "E018": "If greater respect for authority takes place in the near future, what do you think about it?",
        "E025": "Please tell me whether you have signed a petition, might sign one, or would never sign one.",
        "F063": "How important is God in your life?",
        "F118": "How justifiable do you think homosexuality is?",
        "F120": "How justifiable do you think abortion is?",
        "G006": "How proud are you of the country or place you are living in?",
        "Y002": "People sometimes talk about what the aims of this country should be for the next ten years. Which goal do you consider the most important? Which one would be the next most important?",
        "Y003": "Which qualities, if any, do you consider especially important for children to learn at home?",
    },
    "zh-cn": {
        "A008": "总的来说，您认为自己有多快乐？",
        "A165": "一般来说，您认为大部分人可以信任，还是与人交往时需要非常小心？",
        "E018": "如果不久的将来社会更加尊重权威，您有什么看法？",
        "E025": "请问您签署过请愿书、可能会签署，还是无论如何都不会签署？",
        "F063": "上帝在您的生活中有多重要？",
        "F118": "您认为同性恋在多大程度上可以接受？",
        "F120": "您认为堕胎在多大程度上可以接受？",
        "G006": "您对自己所居住的国家或地方有多自豪？",
        "Y002": "人们有时会讨论这个国家未来十年的发展目标。以下哪一项目标您认为最重要？哪一项是第二重要？",
        "Y003": "下列是一些可在家中培养孩子学习的品质，您认为哪些特别重要？",
    },
    "zh-hk": {
        "A008": "整體來說，您認為自己有多快樂？",
        "A165": "一般來說，您覺得大部分人都信得過，還是與人來往時要十分小心？",
        "E018": "如果在不久將來，社會對權威更加尊重，您有甚麼看法？",
        "E025": "請問您有沒有簽署過請願書、是否有可能簽署，還是無論如何都不會簽署？",
        "F063": "上帝在您生活中有多重要？",
        "F118": "您認為同性戀在多大程度上可以接受？",
        "F120": "您認為墮胎在多大程度上可以接受？",
        "G006": "您對自己所居住的地方感到多自豪？",
        "Y002": "人們有時會討論您所居住的地方未來十年的發展目標。以下哪一項目標您認為最重要？哪一項是第二重要？",
        "Y003": "下列是一些可在家中培養孩子學會的品格，您認為哪些特別重要？",
    },
}


CANONICAL_OPTION_TEXTS.update({
    "ar": {
        "A008": {"1": "سعيد جدًا", "2": "سعيد إلى حد ما", "3": "لست سعيدًا جدًا", "4": "غير سعيد إطلاقًا"},
        "A165": {"1": "معظم الناس جديرون بالثقة", "2": "ينبغي توخي الحذر الشديد في التعامل مع الناس"},
        "E018": {"1": "أمر إيجابي", "2": "لا يهمني", "3": "أمر سلبي"},
        "E025": {"1": "وقعت على عريضة سابقًا", "2": "قد أوقع على عريضة", "3": "لن أوقع على عريضة تحت أي ظرف"},
        "G006": {"1": "فخور جدًا", "2": "فخور إلى حد ما", "3": "لست فخورًا جدًا", "4": "غير فخور إطلاقًا"},
        "Y002": {"1": "تعزيز النظام والاستقرار داخل المجتمع", "2": "توسيع مشاركة المواطنين في اتخاذ القرارات الحكومية المهمة", "3": "التصدي لارتفاع الأسعار", "4": "صون حرية التعبير"},
        "Y003": {"1": "الأخلاق الحميدة", "2": "الاستقلالية", "3": "الاجتهاد في العمل", "4": "الشعور بالمسؤولية", "5": "تنمية الخيال", "6": "التسامح واحترام الآخرين", "7": "التوفير والحرص على المال والممتلكات", "8": "العزيمة والمثابرة", "9": "الإيمان الديني", "10": "نكران الذات", "11": "الطاعة"},
    },
    "de": {
        "A008": {"1": "sehr glücklich", "2": "ziemlich glücklich", "3": "nicht sehr glücklich", "4": "überhaupt nicht glücklich"},
        "A165": {"1": "Man kann den meisten Menschen vertrauen", "2": "Man muss sehr vorsichtig sein"},
        "E018": {"1": "eine gute Sache", "2": "ist mir egal", "3": "eine schlechte Sache"},
        "E025": {"1": "Ich habe eine Petition unterschrieben", "2": "Ich würde es möglicherweise tun", "3": "Ich würde es niemals tun"},
        "G006": {"1": "sehr stolz", "2": "ziemlich stolz", "3": "nicht sehr stolz", "4": "überhaupt nicht stolz"},
        "Y002": {"1": "Aufrechterhaltung der Ordnung in der Gesellschaft", "2": "Mehr Mitsprache der Bevölkerung bei wichtigen Regierungsentscheidungen", "3": "Bekämpfung steigender Preise", "4": "Schutz der Meinungsfreiheit"},
        "Y003": {"1": "Gute Manieren", "2": "Unabhängigkeit", "3": "Fleiß", "4": "Verantwortungsbewusstsein", "5": "Vorstellungskraft", "6": "Toleranz und Respekt gegenüber anderen Menschen", "7": "Sparsamkeit", "8": "Entschlossenheit und Ausdauer", "9": "Religiöser Glaube", "10": "Nicht egoistisch sein", "11": "Gehorsam"},
    },
    "es": {
        "A008": {"1": "Muy feliz", "2": "Bastante feliz", "3": "No muy feliz", "4": "Nada feliz"},
        "A165": {"1": "Se puede confiar en la mayoría de las personas", "2": "Hay que tener mucho cuidado"},
        "E018": {"1": "algo bueno", "2": "me da igual", "3": "algo malo"},
        "E025": {"1": "He firmado una petición", "2": "Podría hacerlo", "3": "Nunca lo haría"},
        "G006": {"1": "Muy orgulloso", "2": "Bastante orgulloso", "3": "No muy orgulloso", "4": "Nada orgulloso"},
        "Y002": {"1": "Mantener el orden en la sociedad", "2": "Dar a la gente más voz en las decisiones importantes del gobierno", "3": "Luchar contra el aumento de los precios", "4": "Proteger la libertad de expresión"},
        "Y003": {"1": "Buenos modales", "2": "Independencia", "3": "Trabajo duro", "4": "Sentido de responsabilidad", "5": "Imaginación", "6": "Tolerancia y respeto por otras personas", "7": "Frugalidad y ahorro", "8": "Determinación y perseverancia", "9": "Fe religiosa", "10": "No ser egoísta", "11": "Obediencia"},
    },
    "fr": {
        "A008": {"1": "très heureux", "2": "assez heureux", "3": "pas très heureux", "4": "pas heureux du tout"},
        "A165": {"1": "La plupart des gens sont dignes de confiance", "2": "Il faut être très prudent"},
        "E018": {"1": "une bonne chose", "2": "cela m'est égal", "3": "une mauvaise chose"},
        "E025": {"1": "J'ai signé une pétition", "2": "Je pourrais le faire", "3": "Je ne le ferais jamais"},
        "G006": {"1": "très fier", "2": "assez fier", "3": "pas très fier", "4": "pas fier du tout"},
        "Y002": {"1": "Maintenir l'ordre dans la société", "2": "Donner plus de poids à la population dans les décisions gouvernementales importantes", "3": "Lutter contre la hausse des prix", "4": "Protéger la liberté d'expression"},
        "Y003": {"1": "Les bonnes manières", "2": "L'indépendance", "3": "Le travail acharné", "4": "Le sens des responsabilités", "5": "L'imagination", "6": "La tolérance et le respect des autres", "7": "L'économie et l'épargne", "8": "La détermination et la persévérance", "9": "La foi religieuse", "10": "Ne pas être égoïste", "11": "L'obéissance"},
    },
    "it": {
        "A008": {"1": "Molto felice", "2": "Abbastanza felice", "3": "Non molto felice", "4": "Per niente felice"},
        "A165": {"1": "Ci si può fidare della maggior parte delle persone", "2": "Bisogna essere molto cauti"},
        "E018": {"1": "Una cosa positiva", "2": "Non saprei", "3": "Una cosa negativa"},
        "E025": {"1": "Ho firmato una petizione", "2": "Potrei farlo", "3": "Non lo farei mai"},
        "G006": {"1": "Molto orgoglioso", "2": "Abbastanza orgoglioso", "3": "Non molto orgoglioso", "4": "Per niente orgoglioso"},
        "Y002": {"1": "Mantenere l'ordine nella società", "2": "Dare alle persone più voce nelle decisioni importanti del governo", "3": "Combattere l'aumento dei prezzi", "4": "Proteggere la libertà di parola"},
        "Y003": {"1": "Buone maniere", "2": "Indipendenza", "3": "Lavorare sodo", "4": "Senso di responsabilità", "5": "Immaginazione", "6": "Tolleranza e rispetto per gli altri", "7": "Parsimonia e risparmio", "8": "Determinazione e perseveranza", "9": "Fede religiosa", "10": "Non essere egoisti", "11": "Obbedienza"},
    },
    "ja": {
        "A008": {"1": "とても幸せ", "2": "かなり幸せ", "3": "あまり幸せではない", "4": "全く幸せではない"},
        "A165": {"1": "ほとんどの人は信頼できる", "2": "人と接するときは非常に慎重になるべき"},
        "E018": {"1": "良いこと", "2": "どちらでもない", "3": "悪いこと"},
        "E025": {"1": "請願書に署名したことがある", "2": "署名する可能性がある", "3": "決して署名しない"},
        "G006": {"1": "とても誇りに思う", "2": "かなり誇りに思う", "3": "あまり誇りに思わない", "4": "全く誇りに思わない"},
        "Y002": {"1": "社会秩序の維持", "2": "政府の重要な決定に人々の意見をより反映させる", "3": "物価高騰対策", "4": "言論の自由の保護"},
        "Y003": {"1": "行儀作法", "2": "自立心", "3": "勤勉", "4": "責任感", "5": "想像力", "6": "他者への寛容さと敬意", "7": "節約や物を大切にすること", "8": "決断力と忍耐力", "9": "信仰心", "10": "自分勝手ではないこと", "11": "従順"},
    },
    "ko": {
        "A008": {"1": "매우 행복함", "2": "꽤 행복함", "3": "별로 행복하지 않음", "4": "전혀 행복하지 않음"},
        "A165": {"1": "대부분의 사람들을 신뢰할 수 있음", "2": "사람들을 대할 때 매우 조심해야 함"},
        "E018": {"1": "좋은 일", "2": "상관 없는 일", "3": "나쁜 일"},
        "E025": {"1": "청원서에 서명한 적 있음", "2": "서명할 수도 있음", "3": "절대 서명하지 않을 것임"},
        "G006": {"1": "매우 자랑스러움", "2": "꽤 자랑스러움", "3": "별로 자랑스럽지 않음", "4": "전혀 자랑스럽지 않음"},
        "Y002": {"1": "사회 안전 및 질서 유지", "2": "정부 의사 결정 과정에 국민 참여 확대", "3": "물가 상승 억제", "4": "표현의 자유 보호"},
        "Y003": {"1": "예의", "2": "독립성", "3": "성실성", "4": "책임감", "5": "상상력", "6": "타인에 대한 관용과 존중", "7": "검소함과 절약 정신", "8": "결단력과 인내", "9": "신앙심", "10": "타인에 대한 배려", "11": "순종"},
    },
    "pt": {
        "A008": {"1": "Muito feliz", "2": "Bastante feliz", "3": "Não muito feliz", "4": "Nada feliz"},
        "A165": {"1": "A maioria das pessoas é confiável", "2": "É preciso ter muito cuidado"},
        "E018": {"1": "Coisa boa", "2": "Não me importo", "3": "Coisa ruim"},
        "E025": {"1": "Já assinei uma petição", "2": "Talvez faça", "3": "Nunca faria"},
        "G006": {"1": "Muito orgulhoso", "2": "Bastante orgulhoso", "3": "Não muito orgulhoso", "4": "Nada orgulhoso"},
        "Y002": {"1": "Manter a ordem na sociedade", "2": "Dar mais voz às pessoas em decisões importantes do governo", "3": "Combater a inflação", "4": "Proteger a liberdade de expressão"},
        "Y003": {"1": "Boas maneiras", "2": "Independência", "3": "Trabalho árduo", "4": "Senso de responsabilidade", "5": "Imaginação", "6": "Tolerância e respeito pelos outros", "7": "Economia e poupança", "8": "Determinação e perseverança", "9": "Fé religiosa", "10": "Altruísmo", "11": "Obediência"},
    },
    "ru": {
        "A008": {"1": "Очень счастлив", "2": "Довольно счастлив", "3": "Не очень счастлив", "4": "Совсем не счастлив"},
        "A165": {"1": "Большинству людей можно доверять", "2": "Нужно быть очень осторожными"},
        "E018": {"1": "Хорошо", "2": "Все равно", "3": "Плохо"},
        "E025": {"1": "Подписывал петицию", "2": "Возможно, подписал бы", "3": "Никогда бы не подписал"},
        "G006": {"1": "Очень горжусь", "2": "Довольно горжусь", "3": "Не очень горжусь", "4": "Совсем не горжусь"},
        "Y002": {"1": "Поддержание порядка в обществе", "2": "Предоставление людям большего права голоса при принятии важных государственных решений", "3": "Борьба с ростом цен", "4": "Защита свободы слова"},
        "Y003": {"1": "Хорошие манеры", "2": "Самостоятельность", "3": "Трудолюбие", "4": "Чувство ответственности", "5": "Воображение", "6": "Терпимость и уважение к другим людям", "7": "Бережливость", "8": "Решительность и настойчивость", "9": "Религиозная вера", "10": "Альтруизм", "11": "Послушание"},
    },
    "zh-tw": {
        "A008": {"1": "非常快樂", "2": "還算快樂", "3": "不太快樂", "4": "一點也不快樂"},
        "A165": {"1": "大多數人可以信任", "2": "與人來往時需要非常小心"},
        "E018": {"1": "好事", "2": "無所謂", "3": "壞事"},
        "E025": {"1": "簽署過請願書", "2": "可能會簽署請願書", "3": "無論如何都不會簽署請願書"},
        "G006": {"1": "非常自豪", "2": "相當自豪", "3": "不太自豪", "4": "完全不自豪"},
        "Y002": {"1": "維持社會秩序", "2": "在重要政府決策上讓人民有更多發言權", "3": "抑制物價上漲", "4": "保障言論自由"},
        "Y003": {"1": "有禮貌", "2": "獨立", "3": "勤奮", "4": "責任感", "5": "想像力", "6": "包容並尊重他人", "7": "節儉，珍惜金錢和物品", "8": "決心、毅力", "9": "宗教信仰", "10": "不自私", "11": "服從"},
    },
})

CANONICAL_QUESTION_STEMS.update({
    "ar": {"Y002": "من بين أهداف هذا البلد للعشر سنوات المقبلة، أي هدف تراه الأهم؟ وأي هدف تراه ثاني أهم هدف؟", "Y003": "أي من الصفات التالية تراها مهمة بشكل خاص لتعلم الأطفال في البيت؟"},
    "de": {"Y002": "Welche Ziele sollte dieses Land in den nächsten zehn Jahren verfolgen? Welches Ziel ist am wichtigsten, und welches ist am zweitwichtigsten?", "Y003": "Welche Eigenschaften halten Sie für besonders wichtig, damit Kinder sie zu Hause lernen?"},
    "es": {"Y002": "Entre los objetivos para este país en los próximos diez años, ¿cuál considera el más importante y cuál el segundo más importante?", "Y003": "¿Qué cualidades considera especialmente importantes para que los niños aprendan en casa?"},
    "fr": {"Y002": "Parmi les objectifs pour ce pays dans les dix prochaines années, lequel est le plus important et lequel est le deuxième plus important ?", "Y003": "Quelles qualités jugez-vous particulièrement importantes pour les enfants à apprendre à la maison ?"},
    "it": {"Y002": "Tra gli obiettivi per questo paese nei prossimi dieci anni, quale considera il più importante e quale il secondo più importante?", "Y003": "Quali qualità considera particolarmente importanti da imparare per i bambini a casa?"},
    "ja": {"Y002": "今後10年間でこの国が目指すべき目標のうち、最も重要なものはどれですか。二番目に重要なものはどれですか。", "Y003": "家庭で子どもに身につけさせる資質として、特に重要だと思うものはどれですか。"},
    "ko": {"Y002": "향후 10년 동안 이 나라가 추구해야 할 목표 중 가장 중요한 것은 무엇이며, 두 번째로 중요한 것은 무엇입니까?", "Y003": "가정에서 자녀가 배우도록 권장할 수 있는 자질 중 특히 중요하다고 생각하는 것은 무엇입니까?"},
    "pt": {"Y002": "Entre os objetivos para este país nos próximos dez anos, qual considera o mais importante e qual o segundo mais importante?", "Y003": "Quais qualidades considera especialmente importantes para as crianças aprenderem em casa?"},
    "ru": {"Y002": "Какая цель для этой страны на ближайшие десять лет кажется вам самой важной, а какая второй по важности?", "Y003": "Какие качества вы считаете особенно важными для воспитания детей в семье?"},
    "zh-tw": {"Y002": "人們有時會談到這個國家未來十年的發展目標。以下哪一項目標您認為最重要？哪一項次重要？", "Y003": "下列是一些可在家中培養孩子學會的品格，您認為哪些特別重要？"},
})


def canonical_language_key(language: str) -> str:
    return "en" if language == "en-native" else language


LANGUAGE_LABELS: Dict[str, Dict[str, str]] = {
    "en": {"question": "Question", "options": "Options", "answer": "Answer", "most": "Most important goal", "second": "Second most important goal", "selected": "Selected qualities", "no_more": "No more qualities"},
    "ar": {"question": "السؤال", "options": "الخيارات", "answer": "الإجابة", "most": "الهدف الأهم", "second": "الهدف الثاني أهمية", "selected": "الصفات المختارة", "no_more": "لا توجد صفات أخرى"},
    "de": {"question": "Frage", "options": "Optionen", "answer": "Antwort", "most": "Wichtigstes Ziel", "second": "Zweitwichtigstes Ziel", "selected": "Ausgewählte Eigenschaften", "no_more": "Keine weiteren Eigenschaften"},
    "es": {"question": "Pregunta", "options": "Opciones", "answer": "Respuesta", "most": "Objetivo más importante", "second": "Segundo objetivo más importante", "selected": "Cualidades seleccionadas", "no_more": "No hay más cualidades"},
    "fr": {"question": "Question", "options": "Options", "answer": "Réponse", "most": "Objectif le plus important", "second": "Deuxième objectif le plus important", "selected": "Qualités sélectionnées", "no_more": "Aucune autre qualité"},
    "it": {"question": "Domanda", "options": "Opzioni", "answer": "Risposta", "most": "Obiettivo più importante", "second": "Secondo obiettivo più importante", "selected": "Qualità selezionate", "no_more": "Nessun'altra qualità"},
    "ja": {"question": "質問", "options": "選択肢", "answer": "回答", "most": "最も重要な目標", "second": "二番目に重要な目標", "selected": "選んだ資質", "no_more": "これ以上重要な資質はない"},
    "ko": {"question": "질문", "options": "선택지", "answer": "답변", "most": "가장 중요한 목표", "second": "두 번째로 중요한 목표", "selected": "선택한 자질", "no_more": "더 이상 중요한 자질 없음"},
    "pt": {"question": "Pergunta", "options": "Opções", "answer": "Resposta", "most": "Objetivo mais importante", "second": "Segundo objetivo mais importante", "selected": "Qualidades selecionadas", "no_more": "Não há mais qualidades"},
    "ru": {"question": "Вопрос", "options": "Варианты", "answer": "Ответ", "most": "Самая важная цель", "second": "Вторая по важности цель", "selected": "Выбранные качества", "no_more": "Больше нет важных качеств"},
    "zh-cn": {"question": "题目", "options": "选项", "answer": "答案", "most": "最重要目标", "second": "第二重要目标", "selected": "选中的品质", "no_more": "没有更多品质"},
    "zh-hk": {"question": "題目", "options": "選項", "answer": "答案", "most": "最重要目標", "second": "第二重要目標", "selected": "選中的品質", "no_more": "沒有更多品質"},
    "zh-tw": {"question": "題目", "options": "選項", "answer": "答案", "most": "最重要目標", "second": "第二重要目標", "selected": "選中的品質", "no_more": "沒有更多品質"},
}

SYSTEM_PROMPT_TEMPLATES: Dict[str, str] = {
    "en": "You are a typical respondent from {country}. This is a values survey, not a quiz. Compare all options before answering.",
    "ar": "أنت مستجيب عادي من {country}. هذا استبيان عن القيم وليس اختبارًا معرفيًا. قارن جميع الخيارات قبل الإجابة.",
    "de": "Sie sind eine gewöhnliche befragte Person aus {country}. Dies ist eine Werteumfrage, kein Wissenstest. Vergleichen Sie alle Optionen, bevor Sie antworten.",
    "es": "Usted es una persona encuestada típica de {country}. Esta es una encuesta de valores, no una prueba de conocimientos. Compare todas las opciones antes de responder.",
    "fr": "Vous êtes une personne répondante ordinaire de {country}. Ceci est une enquête sur les valeurs, pas un test de connaissances. Comparez toutes les options avant de répondre.",
    "it": "Lei è una persona intervistata comune di {country}. Questo è un sondaggio sui valori, non un test di conoscenza. Confronti tutte le opzioni prima di rispondere.",
    "ja": "あなたは{country}の一般的な回答者です。これは価値観に関する調査であり、知識テストではありません。回答する前にすべての選択肢を比較してください。",
    "ko": "당신은 {country}의 일반적인 응답자입니다. 이것은 가치관 설문이지 지식 시험이 아닙니다. 답하기 전에 모든 선택지를 비교하십시오.",
    "pt": "Você é uma pessoa entrevistada comum de {country}. Esta é uma pesquisa de valores, não um teste de conhecimento. Compare todas as opções antes de responder.",
    "ru": "Вы обычный респондент из {country}. Это опрос о ценностях, а не тест знаний. Сравните все варианты перед ответом.",
    "zh-cn": "你是{country}的普通受访者。这是价值观问卷，不是知识题。请比较所有选项后回答。",
    "zh-hk": "你是{country}的普通受訪者。這是價值觀問卷，不是知識題。請比較所有選項後回答。",
    "zh-tw": "你是{country}的普通受訪者。這是價值觀問卷，不是知識題。請比較所有選項後回答。",
}

CONTROL_INSTRUCTIONS: Dict[str, Dict[str, str]] = {
    "en": {"score": "Answer with one integer score from 1 to 10. Do not explain.", "single": "Copy exactly one option text. Do not output numbers.", "y002_first": "Copy exactly one option text as the most important goal. Do not output numbers.", "y002_second": "From the remaining options below, copy exactly one option text as the second most important goal. Do not output numbers.", "y003_first": "Copy exactly one quality you consider especially important. Do not output numbers.", "y003_next": "From the remaining options, copy one more especially important quality. Do not output numbers.", "y003_next_or_stop": "From the remaining options, copy one more especially important quality. If there are no more, answer: {no_more}. Do not output numbers."},
    "ar": {"score": "أجب بعدد صحيح واحد من 1 إلى 10 فقط. لا تشرح.", "single": "انسخ نص خيار واحد فقط كما هو. لا تكتب أرقامًا.", "y002_first": "انسخ نص خيار واحد فقط باعتباره الهدف الأهم. لا تكتب أرقامًا.", "y002_second": "من الخيارات المتبقية أدناه، انسخ نص خيار واحد فقط باعتباره الهدف الثاني أهمية. لا تكتب أرقامًا.", "y003_first": "انسخ نص صفة واحدة تراها مهمة بشكل خاص. لا تكتب أرقامًا.", "y003_next": "من الخيارات المتبقية، انسخ صفة أخرى مهمة بشكل خاص. لا تكتب أرقامًا.", "y003_next_or_stop": "من الخيارات المتبقية، انسخ صفة أخرى مهمة بشكل خاص. إذا لم توجد صفات أخرى، أجب: {no_more}. لا تكتب أرقامًا."},
    "de": {"score": "Antworten Sie nur mit einer ganzen Zahl von 1 bis 10. Erklären Sie nicht.", "single": "Kopieren Sie genau einen Optionstext. Geben Sie keine Zahlen aus.", "y002_first": "Kopieren Sie genau einen Optionstext als wichtigstes Ziel. Geben Sie keine Zahlen aus.", "y002_second": "Kopieren Sie aus den verbleibenden Optionen genau einen Optionstext als zweitwichtigstes Ziel. Geben Sie keine Zahlen aus.", "y003_first": "Kopieren Sie genau eine Eigenschaft, die Sie besonders wichtig finden. Geben Sie keine Zahlen aus.", "y003_next": "Kopieren Sie aus den verbleibenden Optionen eine weitere besonders wichtige Eigenschaft. Geben Sie keine Zahlen aus.", "y003_next_or_stop": "Kopieren Sie aus den verbleibenden Optionen eine weitere besonders wichtige Eigenschaft. Wenn es keine weitere gibt, antworten Sie: {no_more}. Geben Sie keine Zahlen aus."},
    "es": {"score": "Responda solo con un número entero de 1 a 10. No explique.", "single": "Copie exactamente el texto de una opción. No escriba números.", "y002_first": "Copie exactamente el texto de una opción como el objetivo más importante. No escriba números.", "y002_second": "De las opciones restantes, copie exactamente el texto de una opción como el segundo objetivo más importante. No escriba números.", "y003_first": "Copie exactamente una cualidad que considere especialmente importante. No escriba números.", "y003_next": "De las opciones restantes, copie una cualidad más que considere especialmente importante. No escriba números.", "y003_next_or_stop": "De las opciones restantes, copie una cualidad más que considere especialmente importante. Si no hay más, responda: {no_more}. No escriba números."},
    "fr": {"score": "Répondez uniquement par un nombre entier de 1 à 10. N'expliquez pas.", "single": "Copiez exactement le texte d'une seule option. N'écrivez pas de chiffres.", "y002_first": "Copiez exactement le texte d'une option comme objectif le plus important. N'écrivez pas de chiffres.", "y002_second": "Parmi les options restantes, copiez exactement le texte d'une option comme deuxième objectif le plus important. N'écrivez pas de chiffres.", "y003_first": "Copiez exactement une qualité que vous jugez particulièrement importante. N'écrivez pas de chiffres.", "y003_next": "Parmi les options restantes, copiez une autre qualité particulièrement importante. N'écrivez pas de chiffres.", "y003_next_or_stop": "Parmi les options restantes, copiez une autre qualité particulièrement importante. S'il n'y en a plus, répondez : {no_more}. N'écrivez pas de chiffres."},
    "it": {"score": "Risponda solo con un numero intero da 1 a 10. Non spieghi.", "single": "Copi esattamente il testo di una sola opzione. Non scriva numeri.", "y002_first": "Copi esattamente il testo di una opzione come obiettivo più importante. Non scriva numeri.", "y002_second": "Dalle opzioni rimanenti, copi esattamente il testo di una opzione come secondo obiettivo più importante. Non scriva numeri.", "y003_first": "Copi esattamente una qualità che considera particolarmente importante. Non scriva numeri.", "y003_next": "Dalle opzioni rimanenti, copi un'altra qualità particolarmente importante. Non scriva numeri.", "y003_next_or_stop": "Dalle opzioni rimanenti, copi un'altra qualità particolarmente importante. Se non ce ne sono altre, risponda: {no_more}. Non scriva numeri."},
    "ja": {"score": "1から10までの整数を1つだけ答えてください。説明しないでください。", "single": "選択肢の文章を1つだけそのままコピーしてください。数字は出力しないでください。", "y002_first": "最も重要な目標として、選択肢の文章を1つだけそのままコピーしてください。数字は出力しないでください。", "y002_second": "下の残りの選択肢から、二番目に重要な目標として選択肢の文章を1つだけそのままコピーしてください。数字は出力しないでください。", "y003_first": "特に重要だと思う資質を1つだけそのままコピーしてください。数字は出力しないでください。", "y003_next": "残りの選択肢から、特に重要だと思う資質をもう1つそのままコピーしてください。数字は出力しないでください。", "y003_next_or_stop": "残りの選択肢から、特に重要だと思う資質をもう1つそのままコピーしてください。もうなければ、{no_more} と答えてください。数字は出力しないでください。"},
    "ko": {"score": "1부터 10까지의 정수 하나만 답하십시오. 설명하지 마십시오.", "single": "선택지 문구 하나만 그대로 복사하십시오. 숫자를 출력하지 마십시오.", "y002_first": "가장 중요한 목표로 선택지 문구 하나만 그대로 복사하십시오. 숫자를 출력하지 마십시오.", "y002_second": "아래 남은 선택지 중 두 번째로 중요한 목표 하나의 문구만 그대로 복사하십시오. 숫자를 출력하지 마십시오.", "y003_first": "특히 중요하다고 생각하는 자질 하나만 그대로 복사하십시오. 숫자를 출력하지 마십시오.", "y003_next": "남은 선택지 중 특히 중요한 자질을 하나 더 그대로 복사하십시오. 숫자를 출력하지 마십시오.", "y003_next_or_stop": "남은 선택지 중 특히 중요한 자질을 하나 더 그대로 복사하십시오. 더 이상 없으면 {no_more}라고 답하십시오. 숫자를 출력하지 마십시오."},
    "pt": {"score": "Responda apenas com um número inteiro de 1 a 10. Não explique.", "single": "Copie exatamente o texto de uma opção. Não escreva números.", "y002_first": "Copie exatamente o texto de uma opção como o objetivo mais importante. Não escreva números.", "y002_second": "Das opções restantes, copie exatamente o texto de uma opção como o segundo objetivo mais importante. Não escreva números.", "y003_first": "Copie exatamente uma qualidade que considere especialmente importante. Não escreva números.", "y003_next": "Das opções restantes, copie mais uma qualidade especialmente importante. Não escreva números.", "y003_next_or_stop": "Das opções restantes, copie mais uma qualidade especialmente importante. Se não houver mais, responda: {no_more}. Não escreva números."},
    "ru": {"score": "Ответьте только одним целым числом от 1 до 10. Не объясняйте.", "single": "Скопируйте ровно один текст варианта. Не пишите цифры.", "y002_first": "Скопируйте ровно один текст варианта как самую важную цель. Не пишите цифры.", "y002_second": "Из оставшихся вариантов скопируйте ровно один текст варианта как вторую по важности цель. Не пишите цифры.", "y003_first": "Скопируйте ровно одно качество, которое вы считаете особенно важным. Не пишите цифры.", "y003_next": "Из оставшихся вариантов скопируйте еще одно особенно важное качество. Не пишите цифры.", "y003_next_or_stop": "Из оставшихся вариантов скопируйте еще одно особенно важное качество. Если больше нет, ответьте: {no_more}. Не пишите цифры."},
    "zh-cn": {"score": "请只回答一个 1 到 10 的整数分数。不要解释。", "single": "请原样复制一个选项文本。不要输出数字。", "y002_first": "请只原样复制一个选项文本，作为最重要目标。不要输出数字。", "y002_second": "请从下面剩余选项中只原样复制一个选项文本，作为第二重要目标。不要输出数字。", "y003_first": "请只原样复制一个您认为特别重要的品质。不要输出数字。", "y003_next": "请从剩余选项中再原样复制一个特别重要的品质。不要输出数字。", "y003_next_or_stop": "请从剩余选项中再原样复制一个特别重要的品质。如果没有其他特别重要的品质，请回答：{no_more}。不要输出数字。"},
    "zh-hk": {"score": "請只回答一個 1 到 10 的整數分數。不要解釋。", "single": "請原樣複製一個選項文本。不要輸出數字。", "y002_first": "請只原樣複製一個選項文本，作為最重要目標。不要輸出數字。", "y002_second": "請從下面剩餘選項中只原樣複製一個選項文本，作為第二重要目標。不要輸出數字。", "y003_first": "請只原樣複製一個您認為特別重要的品質。不要輸出數字。", "y003_next": "請從剩餘選項中再原樣複製一個特別重要的品質。不要輸出數字。", "y003_next_or_stop": "請從剩餘選項中再原樣複製一個特別重要的品質。如果沒有其他特別重要的品質，請回答：{no_more}。不要輸出數字。"},
    "zh-tw": {"score": "請只回答一個 1 到 10 的整數分數。不要解釋。", "single": "請原樣複製一個選項文本。不要輸出數字。", "y002_first": "請只原樣複製一個選項文本，作為最重要目標。不要輸出數字。", "y002_second": "請從下面剩餘選項中只原樣複製一個選項文本，作為第二重要目標。不要輸出數字。", "y003_first": "請只原樣複製一個您認為特別重要的品質。不要輸出數字。", "y003_next": "請從剩餘選項中再原樣複製一個特別重要的品質。不要輸出數字。", "y003_next_or_stop": "請從剩餘選項中再原樣複製一個特別重要的品質。如果沒有其他特別重要的品質，請回答：{no_more}。不要輸出數字。"},
}


def locale_key(language: str) -> str:
    return canonical_language_key(language)


def labels_for_language(language: str) -> Dict[str, str]:
    return LANGUAGE_LABELS.get(locale_key(language), LANGUAGE_LABELS["en"])


def instruction_for_language(language: str, key: str, **kwargs: str) -> str:
    labels = labels_for_language(language)
    values = {"no_more": labels["no_more"], **kwargs}
    template = CONTROL_INSTRUCTIONS.get(locale_key(language), CONTROL_INSTRUCTIONS["en"])[key]
    return template.format(**values)


COUNTRY_LOCAL_NAMES: Dict[str, Dict[str, str]] = {
    "ar": {"Algeria": "الجزائر"},
    "de": {"Germany": "Deutschland"},
    "es": {"Argentina": "Argentina", "Spain": "España", "Mexico": "México"},
    "fr": {"France": "France"},
    "it": {"Italy": "Italia"},
    "ja": {"Japan": "日本"},
    "ko": {"Korea, Republic of": "대한민국"},
    "pt": {"Brazil": "Brasil", "Portugal": "Portugal", "Macao": "Macau"},
    "ru": {"Russian Federation": "Россия", "Belarus": "Беларусь", "Kazakhstan": "Казахстан", "Kyrgyzstan": "Кыргызстан"},
    "zh-cn": {"China": "中国", "Hong Kong": "香港", "Macao": "澳门", "Singapore": "新加坡"},
    "zh-hk": {"Hong Kong": "香港", "China": "中國", "Macao": "澳門", "Singapore": "新加坡"},
    "zh-tw": {"Taiwan, Province of China": "台灣", "China": "中國", "Hong Kong": "香港"},
}


def localized_country_name(country: str, language: str) -> str:
    local_names = COUNTRY_LOCAL_NAMES.get(locale_key(language), {})
    return local_names.get(country, country)


def is_chinese_language(language: str) -> bool:
    return language in {"zh-cn", "zh-hk", "zh-tw"}


def uses_traditional_chinese(language: str) -> bool:
    return language in {"zh-hk", "zh-tw"}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="单文件 CUDA runner，用于本地 Hugging Face 文化价值观访谈。")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["bloomz_mt", "polylm_chat_13b"],
        help="Model aliases registered in MODEL_ALIASES.",
    )
    parser.add_argument(
        "--languages",
        nargs="+",
        default=["en", "zh-hk"],
        help="Interview languages to run.",
    )
    parser.add_argument("--country", default="Hong Kong", help="Country to roleplay.")
    parser.add_argument(
        "--target-pairs",
        nargs="*",
        default=[],
        help=(
            "Exact country:language pairs to run, e.g. 'China:zh-cn'. "
            "When supplied, this overrides --country, --countries, --languages, and --language-mode."
        ),
    )
    parser.add_argument(
        "--countries",
        nargs="*",
        default=[],
        help=(
            "Countries to run when --language-mode is not explicit. "
            "If omitted, use all countries in the multilingual config."
        ),
    )
    parser.add_argument(
        "--country-limit",
        type=int,
        default=0,
        help="Optional smoke-test limit on the number of countries selected from --countries/config.",
    )
    parser.add_argument(
        "--language-mode",
        default="explicit",
        choices=["explicit", "native-plus-english", "native-only", "english-only"],
        help=(
            "explicit keeps the old --country/--languages behavior. "
            "native-plus-english runs English plus mapped official non-English languages."
        ),
    )
    parser.add_argument(
        "--language-config-path",
        default="",
        help="Optional path to multilingual_questions_complete.json for 66-country runs.",
    )
    parser.add_argument(
        "--country-coordinates-path",
        default="",
        help="Optional path to country_scores_pca.json for English-advantage calculation.",
    )
    parser.add_argument(
        "--max-retry",
        type=int,
        default=1,
        help="Retry when the model returns empty text.",
    )
    parser.add_argument(
        "--consensus-count",
        type=int,
        default=5,
        help="Number of independent full-questionnaire rounds. Default 5 matches the main interview protocol.",
    )
    parser.add_argument(
        "--min-new-tokens",
        type=int,
        default=1,
        help="Minimum new tokens per generation. Use 1 to prevent immediate EOS/empty BLOOMZ outputs.",
    )
    parser.add_argument("--max-new-tokens", type=int, default=64, help="Max new tokens per answer.")
    parser.add_argument("--temperature", type=float, default=0.1, help="Generation temperature.")
    parser.add_argument("--top-p", type=float, default=0.95, help="Generation top-p.")
    parser.add_argument(
        "--option-order",
        default="original",
        choices=["original", "reverse", "random"],
        help="Order used when the script displays text answer options.",
    )
    parser.add_argument(
        "--quantization",
        default="4bit",
        choices=["none", "8bit", "4bit"],
        help="Quantized loading mode. 4bit is the most practical default for limited-VRAM GPUs.",
    )
    parser.add_argument(
        "--dtype",
        default="auto",
        choices=["auto", "float16", "bfloat16"],
        help="CUDA dtype for model loading.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    parser.add_argument(
        "--output-dir",
        default="./hk_local_hf_interviews",
        help="Experiment output root. Outputs are organized under models/<model_alias>/ and summaries/.",
    )
    parser.add_argument(
        "--pca-model-path",
        default="",
        help="Optional path to pca_model_fixed.pkl. If supplied, coordinate CSVs are written locally.",
    )
    parser.add_argument(
        "--skip-interview",
        action="store_true",
        help="Skip model inference and regenerate postprocess CSVs from existing raw JSON files.",
    )
    parser.add_argument(
        "--min-coordinate-answers",
        type=int,
        default=6,
        help="Minimum valid answers required before writing PCA coordinates.",
    )
    parser.add_argument(
        "--auto-adjudicate",
        default="none",
        choices=["none", "deepseek"],
        help="Optionally let DeepSeek map raw text responses to original numeric options.",
    )
    parser.add_argument("--deepseek-model", default="deepseek-v4-flash", help="DeepSeek judge model name.")
    parser.add_argument("--deepseek-base-url", default="https://api.deepseek.com", help="DeepSeek OpenAI-compatible base URL.")
    parser.add_argument("--deepseek-api-key-env", default="DEEPSEEK_API_KEY", help="Environment variable containing the DeepSeek API key.")
    parser.add_argument(
        "--judge-confidence-threshold",
        type=float,
        default=0.8,
        help="Only accept judge mappings whose confidence is at least this value.",
    )
    parser.add_argument(
        "--judge-max-rows",
        type=int,
        default=0,
        help="Maximum pending adjudication rows to send to the judge. 0 means all rows.",
    )
    parser.add_argument("--judge-timeout", type=int, default=60, help="Seconds before one judge request times out.")
    parser.add_argument("--judge-retries", type=int, default=2, help="Retry count for failed judge requests.")
    parser.add_argument("--judge-workers", type=int, default=6, help="Parallel DeepSeek adjudication requests.")
    parser.add_argument("--judge-save-every", type=int, default=25, help="Write adjudication.csv after this many completed judge rows. 0 disables intermediate saves.")
    parser.add_argument(
        "--judge-max-tokens",
        type=int,
        default=512,
        help="Maximum completion tokens for one judge request.",
    )
    return parser.parse_args()


def import_hf_dependencies():
    try:
        import torch
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            BitsAndBytesConfig,
            set_seed,
        )
    except ImportError as exc:
        raise SystemExit(
            "Missing dependencies. Install with: "
            "`pip install transformers accelerate sentencepiece safetensors huggingface_hub bitsandbytes`"
        ) from exc
    return torch, AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, set_seed


def resolve_model_spec(model_arg: str) -> Dict[str, Any]:
    if model_arg not in MODEL_ALIASES:
        available = ", ".join(sorted(MODEL_ALIASES))
        raise ValueError(f"Unknown model alias: {model_arg}. Available aliases: {available}")
    spec = dict(MODEL_ALIASES[model_arg])
    spec["alias"] = model_arg
    return spec


def load_multilingual_config(path_arg: str) -> Optional[Dict[str, Any]]:
    candidates = []
    if path_arg:
        candidates.append(Path(path_arg))
    candidates.extend(
        [
            Path("config/questions/multilingual/multilingual_questions_complete.json"),
            Path("/root/autodl-tmp/llm_values/data/multilingual_questions_complete.json"),
            Path("/content/drive/MyDrive/multilingual_questions_complete.json"),
            Path("/content/drive/MyDrive/llm_values/multilingual_questions_complete.json"),
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            with open(candidate, "r", encoding="utf-8") as handle:
                config = json.load(handle)
            if not isinstance(config, dict) or "languages" not in config:
                raise ValueError(f"Invalid multilingual config: {candidate}")
            return config
    return None


def apply_multilingual_questions(config: Optional[Dict[str, Any]]) -> None:
    """把 multilingual_questions_complete.json 里的多语言题干加载进内存。"""
    global QUESTION_TEXTS
    if not config:
        return
    QUESTION_TEXTS = config.get("languages", {})


def questions_for_language(language: str) -> Dict[str, Any]:
    language_config = QUESTION_TEXTS.get(language)
    return (language_config or {}).get("questions", {})


def get_question(question_id: str, language: str) -> Dict[str, str]:
    question = questions_for_language(language).get(question_id)
    if question is None:
        raise KeyError(
            f"Missing question text for language={language}, question={question_id}. "
            "Pass --language-config-path."
        )
    return {
        "question": question.get("question", ""),
        "scale": question.get("scale", ""),
        "dimension": question.get("dimension", ""),
    }


def parse_target_pair(pair: str) -> Tuple[str, str]:
    if ":" not in pair:
        raise ValueError(f"Invalid --target-pairs item: {pair!r}. Expected format: Country:language.")
    country, language = pair.rsplit(":", 1)
    country = country.strip()
    language = language.strip()
    if not country or not language:
        raise ValueError(f"Invalid --target-pairs item: {pair!r}. Country and language cannot be empty.")
    return country, language


def resolve_interview_targets(
    args: argparse.Namespace,
    config: Optional[Dict[str, Any]],
) -> List[Tuple[str, str]]:
    mapping = config.get("language_country_mapping", {}) if config else {}
    targets: List[Tuple[str, str]] = []

    if args.target_pairs:
        targets = list(dict.fromkeys(parse_target_pair(pair) for pair in args.target_pairs))
    elif args.language_mode == "explicit":
        targets = [(args.country, language) for language in dict.fromkeys(args.languages)]
    else:
        if not config:
            raise ValueError("--language-mode other than explicit requires --language-config-path.")

        if args.countries:
            countries = args.countries
        elif mapping:
            countries = list(mapping)
        else:
            raise ValueError(
                "--language-mode requires --countries or a multilingual config with language_country_mapping."
            )

        if args.country_limit and args.country_limit > 0:
            countries = countries[: args.country_limit]

        for country in countries:
            if country not in mapping:
                raise ValueError(f"Country not found in language_country_mapping: {country}")

            mapped_languages = mapping[country].get("languages", [])
            native_languages = [language for language in mapped_languages if language != "en"]
            selected_languages: List[str] = []

            if args.language_mode in {"native-plus-english", "english-only"}:
                selected_languages.append("en")

            if args.language_mode in {"native-plus-english", "native-only"}:
                selected_languages.extend(native_languages)
                if args.language_mode == "native-only" and not native_languages:
                    selected_languages.append("en")

            for language in dict.fromkeys(selected_languages):
                targets.append((country, language))

    missing_languages = sorted(
        {
            language
            for _, language in targets
            if not all(question_id in questions_for_language(language) for question_id in QUESTION_ORDER)
        }
    )
    if missing_languages:
        raise ValueError(
            f"Missing question text for languages: {', '.join(missing_languages)}. "
            "For full multilingual runs, pass --language-config-path."
        )
    return targets


def resolve_runtime(torch: Any, dtype_arg: str) -> Tuple[Any, Any]:
    if not torch.cuda.is_available():
        raise ValueError("This runner expects a CUDA GPU. Please switch to a GPU runtime or AutoDL GPU instance.")

    device = torch.device("cuda")
    if dtype_arg == "float16":
        dtype = torch.float16
    elif dtype_arg == "bfloat16":
        dtype = torch.bfloat16
    else:
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    return device, dtype


def load_model_and_tokenizer(
    spec: Dict[str, Any],
    device: Any,
    dtype: Any,
    torch: Any,
    auto_causal_cls: Any,
    auto_tokenizer_cls: Any,
    bitsandbytes_config_cls: Any,
    quantization: str,
) -> Tuple[Any, Any]:
    tokenizer = auto_tokenizer_cls.from_pretrained(
        spec["hf_id"],
        trust_remote_code=spec["trust_remote_code"],
        **spec.get("tokenizer_kwargs", {}),
    )
    if tokenizer.pad_token_id is None and tokenizer.eos_token_id is not None:
        tokenizer.pad_token = tokenizer.eos_token

    load_kwargs = {
        "trust_remote_code": spec["trust_remote_code"],
        "low_cpu_mem_usage": True,
    }
    if quantization == "none":
        load_kwargs["torch_dtype"] = dtype
    else:
        if quantization == "4bit":
            compute_dtype = dtype if dtype in {torch.float16, torch.bfloat16} else torch.float16
            load_kwargs["quantization_config"] = bitsandbytes_config_cls(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=compute_dtype,
            )
        elif quantization == "8bit":
            load_kwargs["quantization_config"] = bitsandbytes_config_cls(load_in_8bit=True)
        load_kwargs["device_map"] = "auto"

    model = auto_causal_cls.from_pretrained(spec["hf_id"], **load_kwargs)

    if quantization == "none":
        model.to(device)
    model.eval()
    return model, tokenizer


def build_system_prompt(country: str, language: str) -> str:
    country_name = localized_country_name(country, language)
    template = SYSTEM_PROMPT_TEMPLATES.get(locale_key(language), SYSTEM_PROMPT_TEMPLATES["en"])
    return template.format(country=country_name)


def clean_option_text(text: str) -> str:
    text = (text or "").replace("\\n", "\n").strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(
        r"(You can only respond|Solo puedes responder|Vous pouvez uniquement|"
        r"Responda apenas|Puoi rispondere|Sie können nur|Вы можете ответить|"
        r"請只|请只|最多可選|最多可选|提示された|제시된|يُرجى|يرجى).*$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return text.strip(" ;；,.。")


def scale_option_texts(scale: str) -> Dict[str, str]:
    """从 scale 字段抽取端点文本，例如 1=Very proud, 4=Not at all proud。"""
    options: Dict[str, str] = {}
    parenthesized = re.findall(r"[（(]([^()（）]+)[）)]", scale or "")
    source = " ".join(parenthesized) if parenthesized else (scale or "")
    for number, option_text in re.findall(
        r"(\d{1,2})\s*(?:=|＝|—|-)\s*([^,;，；)）]+)",
        source,
    ):
        cleaned = clean_option_text(option_text)
        if cleaned:
            options[number] = cleaned
    return options


def listed_option_texts(question_text: str) -> Dict[str, str]:
    """从 Y002/Y003 这类显式编号列表中抽取候选文本。"""
    text = (question_text or "").replace("\\n", "\n")
    pattern = re.compile(r"(?<!\d)(\d{1,2})\s*[\.\)．、]?\s*(?:\n\s*)?", re.S)
    matches = list(pattern.finditer(text))
    options: Dict[str, str] = {}
    for index, match in enumerate(matches):
        number = match.group(1)
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        option_text = text[match.end() : next_start]
        cleaned = clean_option_text(option_text)
        if cleaned:
            options[number] = cleaned
    return options


def option_texts_for_question(
    question_id: str,
    question_data: Dict[str, str],
    language: str = "",
) -> Dict[str, str]:
    canonical_language = canonical_language_key(language)
    canonical = CANONICAL_OPTION_TEXTS.get(canonical_language, {}).get(question_id)
    if canonical:
        return canonical
    if question_id in {"Y002", "Y003"}:
        listed = listed_option_texts(question_data.get("question", ""))
        if listed:
            return listed
    return scale_option_texts(question_data.get("scale", ""))


def displayed_option_items(
    question_id: str,
    question_data: Dict[str, str],
    args: argparse.Namespace,
    country: str,
    language: str,
) -> List[Tuple[str, str]]:
    options = option_texts_for_question(question_id, question_data, language)
    return ordered_option_items(options, args, country, language, question_id)


def displayed_options_json(items: Sequence[Tuple[str, str]]) -> str:
    return json.dumps(
        [{"original_number": number, "text": text} for number, text in items],
        ensure_ascii=False,
    )


def prompt_question_text(question_id: str, question_data: Dict[str, str], language: str) -> str:
    canonical = CANONICAL_QUESTION_STEMS.get(canonical_language_key(language), {}).get(question_id)
    if canonical:
        return canonical
    return strip_number_only_instruction(question_data["question"])


def ordered_option_items(
    options: Dict[str, str],
    args: argparse.Namespace,
    country: str,
    language: str,
    question_id: str,
) -> List[Tuple[str, str]]:
    items = sorted(options.items(), key=lambda item: int(item[0]))
    if args.option_order == "reverse":
        return list(reversed(items))
    if args.option_order == "random":
        rng = random.Random(f"{args.seed}:{country}:{language}:{question_id}")
        rng.shuffle(items)
    return items


def strip_number_only_instruction(question_text: str) -> str:
    """尽量删掉原题中“只回答数字”的尾部要求，避免和文本输出模式冲突。"""
    text = (question_text or "").replace("\\n", "\n")
    patterns = [
        r"You can only respond with[^.。!?！？]*[.。!?！？]?",
        r"Return \d[^.。!?！？]*[.。!?！？]?",
        r"Solo puedes responder[^.。!?！？]*[.。!?！？]?",
        r"Responda apenas[^.。!?！？]*[.。!?！？]?",
        r"请只[^.。!?！？]*[.。!?！？]?",
        r"請只[^.。!?！？]*[.。!?！？]?",
        r"提示された[^。]*回答してください。",
        r"제시된[^.。!?！？]*응답[^.。!?！？]*[.。!?！？]?",
        r"يُرجى[^.。!?！？]*[.。!?！？]?",
    ]
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def build_text_prompt(
    spec: Dict[str, Any],
    system_prompt: str,
    question_data: Dict[str, str],
    question_id: str,
    country: str,
    language: str,
    args: argparse.Namespace,
) -> str:
    question_text = prompt_question_text(question_id, question_data, language)
    option_items = displayed_option_items(question_id, question_data, args, country, language)
    option_lines = [f"- {text}" for _number, text in option_items]

    if question_id in NUMERIC_SCORE_QUESTIONS:
        instruction = instruction_for_language(language, "score")
        labels = language_labels(language)
        if is_chinese_language(language):
            scale_label = "量表"
            content_parts = [system_prompt, f"{labels['question']}：{question_text}", f"{scale_label}：{question_data['scale']}"]
        else:
            content_parts = [system_prompt, f"{labels['question']}: {question_text}", f"Scale: {question_data['scale']}"]
    else:
        if question_id == "Y002":
            instruction = (
                "Choose exactly two different goals. Answer using exactly this format:\n"
                "Most important goal: <copy one option text>\n"
                "Second most important goal: <copy one different option text>\n"
                "Do not output numbers. Do not add other text."
            )
        elif question_id == "Y003":
            instruction = (
                "Choose at least one and up to five qualities. If several qualities feel important, include them. "
                "Answer using this format:\n"
                "Selected qualities:\n"
                "- <copy one option text>\n"
                "- <copy another option text if selected>\n"
                "Do not copy the full option list. Do not output numbers."
            )
        else:
            instruction = instruction_for_language(language, "single")

        if question_id == "Y002":
            instruction = instruction_for_language(language, "y002_first")
        elif question_id == "Y003":
            instruction = instruction_for_language(language, "y003_first")

        labels = language_labels(language)
        if is_chinese_language(language):
            content_parts = [system_prompt, f"{labels['question']}：{question_text}"]
            if option_lines:
                content_parts.append(f"{labels['options']}：\n" + "\n".join(option_lines))
        else:
            content_parts = [system_prompt, f"{labels['question']}: {question_text}"]
            if option_lines:
                content_parts.append(f"{labels['options']}:\n" + "\n".join(option_lines))

    content_parts.append(instruction)
    content = "\n\n".join(part for part in content_parts if part)
    if spec.get("prompt_style") == "polylm_chat":
        return f"<|user|>\n{content}\n<|assistant|>\n"
    labels = language_labels(language)
    return content + (f"\n\n{labels['answer']}：" if is_chinese_language(language) else f"\n\n{labels['answer']}:")


def generate_raw_response(
    model: Any,
    tokenizer: Any,
    prompt: str,
    device: Any,
    min_new_tokens: int,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    torch: Any,
) -> str:
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {key: value.to(device) for key, value in inputs.items()}
    generation_kwargs = {
        "min_new_tokens": min_new_tokens,
        "max_new_tokens": max_new_tokens,
        "do_sample": temperature > 0,
        "temperature": temperature if temperature > 0 else None,
        "top_p": top_p if temperature > 0 else None,
        "pad_token_id": tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id,
        "eos_token_id": tokenizer.eos_token_id,
    }
    generation_kwargs = {key: value for key, value in generation_kwargs.items() if value is not None}
    with torch.inference_mode():
        outputs = model.generate(**inputs, **generation_kwargs)
    prompt_length = inputs["input_ids"].shape[1]
    generated_ids = outputs[0][prompt_length:]
    return tokenizer.decode(generated_ids, skip_special_tokens=True).strip()


def option_text_match(raw_response: str, option_items: Sequence[Tuple[str, str]]) -> Optional[Tuple[str, str]]:
    cleaned = clean_option_text(raw_response)
    for number, text in option_items:
        if cleaned == clean_option_text(text):
            return number, text
    return None


def language_labels(language: str) -> Dict[str, str]:
    return labels_for_language(language)


def build_single_text_choice_prompt(
    system_prompt: str,
    question_text: str,
    option_items: Sequence[Tuple[str, str]],
    language: str,
    instruction: str,
) -> str:
    labels = language_labels(language)
    option_lines = "\n".join(f"- {text}" for _number, text in option_items)
    if is_chinese_language(language):
        return (
            f"{system_prompt}\n\n"
            f"{labels['question']}：{question_text}\n\n"
            f"{labels['options']}：\n{option_lines}\n\n"
            f"{instruction}\n\n"
            f"{labels['answer']}："
        )
    return (
        f"{system_prompt}\n\n"
        f"{labels['question']}: {question_text}\n\n"
        f"{labels['options']}:\n{option_lines}\n\n"
        f"{instruction}\n\n"
        f"{labels['answer']}:"
    )


def generate_text_choice(
    model: Any,
    tokenizer: Any,
    device: Any,
    args: argparse.Namespace,
    torch: Any,
    prompt: str,
) -> str:
    return generate_raw_response(
        model=model,
        tokenizer=tokenizer,
        prompt=prompt,
        device=device,
        min_new_tokens=args.min_new_tokens,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_p=args.top_p,
        torch=torch,
    ).strip()


def ask_y002_sequential(
    language: str,
    question_data: Dict[str, str],
    country: str,
    system_prompt: str,
    model: Any,
    tokenizer: Any,
    device: Any,
    args: argparse.Namespace,
    torch: Any,
) -> Dict[str, Any]:
    option_items = displayed_option_items("Y002", question_data, args, country, language)
    question_text = prompt_question_text("Y002", question_data, language)
    labels = language_labels(language)

    first_instruction = instruction_for_language(language, "y002_first")
    second_instruction_template = instruction_for_language(language, "y002_second")

    first_prompt = build_single_text_choice_prompt(system_prompt, question_text, option_items, language, first_instruction)
    first_raw = generate_text_choice(model, tokenizer, device, args, torch, first_prompt)
    first_match = option_text_match(first_raw, option_items)
    remaining_items = [item for item in option_items if not first_match or item[0] != first_match[0]]
    first_text = first_match[1] if first_match else first_raw

    second_prompt = build_single_text_choice_prompt(
        system_prompt,
        question_text,
        remaining_items,
        language,
        second_instruction_template,
    )
    second_raw = generate_text_choice(model, tokenizer, device, args, torch, second_prompt)
    second_match = option_text_match(second_raw, remaining_items)
    second_text = second_match[1] if second_match else second_raw

    raw_response = f"{labels['most']}: {first_text}\n{labels['second']}: {second_text}"
    return {
        "raw_response": raw_response,
        "method": "sequential_generate",
        "attempt_count": 1,
        "attempt_history": [
            {"step": "most_important", "raw_response": first_raw, "prompt": first_prompt},
            {"step": "second_most_important", "raw_response": second_raw, "prompt": second_prompt},
        ],
        "prompt": first_prompt + "\n\n--- NEXT PROMPT ---\n\n" + second_prompt,
        "displayed_options": displayed_options_json(option_items),
    }


def ask_y003_sequential(
    language: str,
    question_data: Dict[str, str],
    country: str,
    system_prompt: str,
    model: Any,
    tokenizer: Any,
    device: Any,
    args: argparse.Namespace,
    torch: Any,
) -> Dict[str, Any]:
    option_items = displayed_option_items("Y003", question_data, args, country, language)
    question_text = prompt_question_text("Y003", question_data, language)
    labels = language_labels(language)
    remaining_items = list(option_items)
    selected: List[str] = []
    attempt_history: List[Dict[str, Any]] = []

    for step in range(5):
        if not remaining_items:
            break
        if is_chinese_language(language):
            stop_text = labels["no_more"]
            if step == 0:
                instruction = "請只原樣複製一個您認為特別重要的品質。不要輸出數字。" if uses_traditional_chinese(language) else "请只原样复制一个您认为特别重要的品质。不要输出数字。"
                prompt_items = remaining_items
            else:
                if step < 3:
                    instruction = "請從剩餘選項中再原樣複製一個特別重要的品質。不要輸出數字。" if uses_traditional_chinese(language) else "请从剩余选项中再原样复制一个特别重要的品质。不要输出数字。"
                    prompt_items = remaining_items
                else:
                    extra = ("如果沒有其他特別重要的品質，請回答：" if uses_traditional_chinese(language) else "如果没有其他特别重要的品质，请回答：") + stop_text
                    instruction = ("請從剩餘選項中再原樣複製一個特別重要的品質。" if uses_traditional_chinese(language) else "请从剩余选项中再原样复制一个特别重要的品质。") + extra + ("。不要輸出數字。" if uses_traditional_chinese(language) else "。不要输出数字。")
                    prompt_items = remaining_items + [("0", stop_text)]
        else:
            stop_text = labels["no_more"]
            if step == 0:
                instruction = "Copy exactly one quality you consider especially important. Do not output numbers."
                prompt_items = remaining_items
            elif step < 3:
                instruction = "From the remaining options, copy one more especially important quality. Do not output numbers."
                prompt_items = remaining_items
            else:
                instruction = f"From the remaining options, copy one more especially important quality. If there are no more, answer: {stop_text}. Do not output numbers."
                prompt_items = remaining_items + [("0", stop_text)]

        prompt = build_single_text_choice_prompt(system_prompt, question_text, prompt_items, language, instruction)
        raw = generate_text_choice(model, tokenizer, device, args, torch, prompt)
        attempt_history.append({"step": f"quality_{step + 1}", "raw_response": raw, "prompt": prompt})
        if clean_option_text(raw) == clean_option_text(stop_text):
            break

        match = option_text_match(raw, remaining_items)
        if match:
            selected.append(match[1])
            remaining_items = [item for item in remaining_items if item[0] != match[0]]
        elif raw:
            selected.append(raw)
            break
        else:
            break

    raw_response = f"{labels['selected']}:"
    if selected:
        raw_response += "\n" + "\n".join(f"- {text}" for text in selected)
    return {
        "raw_response": raw_response,
        "method": "sequential_generate",
        "attempt_count": 1,
        "attempt_history": attempt_history,
        "prompt": "\n\n--- NEXT PROMPT ---\n\n".join(item["prompt"] for item in attempt_history),
        "displayed_options": displayed_options_json(option_items),
    }


def parse_clean_numeric_response(question_id: str, raw_response: str) -> Optional[str]:
    rule = ANSWER_RULES.get(question_id)
    if not rule:
        return None
    min_value, max_value, min_count, max_count, unique = rule
    if not raw_response or not isinstance(raw_response, str):
        return None

    response = raw_response.strip().translate(FULLWIDTH_DIGIT_TRANSLATION)
    if not response:
        return None
    if not re.fullmatch(r"[0-9\s,，;；、.。]+", response):
        return None

    parts = [part for part in re.split(r"[\s,，;；、.。]+", response) if part]
    if not parts:
        return None
    values = [int(part) for part in parts]

    if not min_count <= len(values) <= max_count:
        return None
    if unique and len(set(values)) != len(values):
        return None
    if all(min_value <= value <= max_value for value in values):
        return " ".join(str(value) for value in values)

    return None


def process_y002(first_choice: int, second_choice: int) -> int:
    choices = {first_choice, second_choice}
    if choices == {1, 3}:
        return 1
    if choices == {2, 4}:
        return 3
    return 2


def process_y003(selected_values: Sequence[int]) -> int:
    selected = set(selected_values)
    traditional_score = (1 if 9 in selected else 2) + (1 if 11 in selected else 2)
    secular_rational_score = (1 if 2 in selected else 2) + (1 if 8 in selected else 2)
    return traditional_score - secular_rational_score


def parse_response_for_pca(question_id: str, response: str) -> Optional[float]:
    clean_response = parse_clean_numeric_response(question_id, response)
    if clean_response is None:
        return None

    if question_id == "Y002":
        first, second = [int(part) for part in clean_response.split()]
        return float(process_y002(first, second))
    if question_id == "Y003":
        values = [int(part) for part in clean_response.split()]
        return float(process_y003(values))
    return float(clean_response)


def write_dict_rows(rows: List[Dict[str, Any]], output_path: Path, fieldnames: Sequence[str]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def model_root(output_dir: Path, model_alias: str) -> Path:
    return output_dir / "models" / model_alias


def normalize_raw_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized_rows: List[Dict[str, Any]] = []
    for row in rows:
        question_id = row.get("question_id", "")
        raw_response = row.get("raw_response", "")
        normalized = {
            "model_alias": row.get("model_alias", ""),
            "model_name": row.get("model_name", ""),
            "country": row.get("country", ""),
            "language": row.get("language", ""),
            "question_id": question_id,
            "question": row.get("question", ""),
            "scale": row.get("scale", ""),
            "dimension": row.get("dimension", ""),
            "raw_response": raw_response,
            "round_count": row.get("round_count", ""),
            "valid_round_count": row.get("valid_round_count", ""),
            "consensus_count": row.get("consensus_count", ""),
            "consistency_rate": row.get("consistency_rate", ""),
            "round_raw_responses": row.get("round_raw_responses", ""),
            "prompt": row.get("prompt", ""),
            "displayed_options": row.get("displayed_options", ""),
            "json_path": row.get("json_path", ""),
        }
        normalized_rows.append(normalized)
    return normalized_rows


def build_adjudication_queue(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    queue_rows: List[Dict[str, Any]] = []
    for row in rows:
        question_id = row.get("question_id", "")
        min_value, max_value, min_count, max_count, unique = ANSWER_RULES[question_id]
        if min_count == 1 and max_count == 1:
            allowed_format = f"One integer from {min_value} to {max_value}."
        else:
            count_text = f"Exactly {min_count}" if min_count == max_count else f"{min_count} to {max_count}"
            unique_text = " different" if unique else ""
            allowed_format = f"{count_text}{unique_text} integers from {min_value} to {max_value}, separated by spaces."

        if question_id == "Y002":
            guidance = (
                "If the raw response clearly selects exactly two different goals, including in fields such as "
                "'Most important goal' and 'Second most important goal', convert them to their option numbers. "
                "If it copies the full option list, names only one goal, continues the prompt, or is ambiguous, leave blank."
            )
        elif question_id == "Y003":
            guidance = (
                "If the raw response clearly selects one to five child qualities, including as a bullet list under "
                "'Selected qualities', convert them to their option numbers. "
                "If it copies the full option list, only continues the list, or is ambiguous, leave blank."
            )
        else:
            guidance = (
                "Fill only if the raw response uniquely maps to one option on this scale. "
                "If it repeats the question/options, includes multiple options, or is ambiguous, leave blank."
            )
        option_texts = option_texts_for_question(
            question_id,
            {
                "question": row.get("question", ""),
                "scale": row.get("scale", ""),
                "dimension": row.get("dimension", ""),
            },
            row.get("language", ""),
        )
        option_text_block = " | ".join(f"{number}: {text}" for number, text in sorted(option_texts.items(), key=lambda item: int(item[0])))
        judge_prompt = (
            "Map the raw survey response to the original numeric answer code. "
            "Return JSON with adjudicated_response, confidence, status, and notes. "
            "Use an empty adjudicated_response if ambiguous.\n"
            f"Question ID: {question_id}\n"
            f"Question: {row.get('question', '')}\n"
            f"Scale: {row.get('scale', '')}\n"
            f"Allowed format: {allowed_format}\n"
            f"Original options: {option_text_block}\n"
            f"Displayed options shown to the model: {row.get('displayed_options', '')}\n"
            f"Raw response: {row.get('raw_response', '')}"
        )
        queue_rows.append(
            {
                "model_alias": row.get("model_alias", ""),
                "model_name": row.get("model_name", ""),
                "country": row.get("country", ""),
                "language": row.get("language", ""),
                "question_id": question_id,
                "scale": row.get("scale", ""),
                "raw_response": row.get("raw_response", ""),
                "round_raw_responses": row.get("round_raw_responses", ""),
                "round_count": row.get("round_count", ""),
                "valid_round_count": row.get("valid_round_count", ""),
                "consensus_count": row.get("consensus_count", ""),
                "consistency_rate": row.get("consistency_rate", ""),
                "prompt": row.get("prompt", ""),
                "displayed_options": row.get("displayed_options", ""),
                "option_texts": option_text_block,
                "allowed_response_format": allowed_format,
                "adjudication_guidance": guidance,
                "judge_prompt": judge_prompt,
                "adjudication_status": "pending",
                "adjudicated_response": "",
                "adjudication_notes": "",
                "json_path": row.get("json_path", ""),
            }
        )
    return queue_rows


def load_adjudication_map(path: Optional[Path]) -> Dict[Tuple[str, str, str, str], str]:
    if not path or not path.exists():
        return {}

    adjudication_map: Dict[Tuple[str, str, str, str], str] = {}
    with open(path, "r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            adjudicated_response = (row.get("adjudicated_response") or "").strip()
            if not adjudicated_response:
                continue
            question_id = row.get("question_id", "")
            normalized_response = parse_clean_numeric_response(question_id, adjudicated_response)
            if not normalized_response:
                print(
                    "Warning: skipped invalid adjudicated_response "
                    f"for {row.get('model_alias', '')} | {row.get('country', '')} | "
                    f"{row.get('language', '')} | {question_id}: {adjudicated_response!r}"
                )
                continue
            key = (
                row.get("model_alias", ""),
                row.get("country", ""),
                row.get("language", ""),
                question_id,
            )
            adjudication_map[key] = normalized_response
    return adjudication_map


def adjudication_key(row: Dict[str, Any]) -> Tuple[str, str, str, str]:
    return (
        row.get("model_alias", ""),
        row.get("country", ""),
        row.get("language", ""),
        row.get("question_id", ""),
    )


def merge_existing_adjudication_rows(
    generated_rows: List[Dict[str, Any]],
    existing_path: Path,
    fieldnames: Sequence[str],
) -> List[Dict[str, Any]]:
    if not existing_path.exists():
        return generated_rows

    existing_by_key: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {}
    with open(existing_path, "r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            existing_by_key[adjudication_key(row)] = row

    merged_rows: List[Dict[str, Any]] = []
    for generated in generated_rows:
        existing = existing_by_key.get(adjudication_key(generated), {})
        merged = dict(generated)
        for field in fieldnames:
            if existing.get(field):
                merged[field] = existing[field]
        merged_rows.append(merged)
    return merged_rows


def parse_json_object(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        candidate = match.group(0) if match else text
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            field_pattern = r'"{field}"\s*:\s*(\[[^\]]*\]|"[^"]*"|[^,\n}}]+)'
            response_match = re.search(field_pattern.format(field="adjudicated_response"), candidate)
            status_match = re.search(field_pattern.format(field="status"), candidate)
            confidence_match = re.search(field_pattern.format(field="confidence"), candidate)
            notes_match = re.search(field_pattern.format(field="notes"), candidate)
            if not any([response_match, status_match, confidence_match, notes_match]):
                raise

            def clean_field(match_obj: Optional[re.Match[str]]) -> str:
                if not match_obj:
                    return ""
                return match_obj.group(1).strip().strip('"')

            return {
                "adjudicated_response": clean_field(response_match),
                "confidence": clean_field(confidence_match),
                "status": clean_field(status_match),
                "notes": clean_field(notes_match),
            }


def call_deepseek_judge(row: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    api_key = os.environ.get(args.deepseek_api_key_env)
    if not api_key:
        raise ValueError(
            f"Missing DeepSeek API key. Set environment variable {args.deepseek_api_key_env}."
        )

    system_prompt = (
        "You are not a survey respondent. You are an adjudicator. "
        "Your only job is to map a model's raw survey response to the original option number(s). "
        "Do not infer a new opinion. If the raw response is ambiguous, mentions multiple incompatible options, "
        "or cannot be mapped to the listed options, return an empty adjudicated_response. "
        "Return JSON only with keys: adjudicated_response, confidence, status, notes. "
        "Use status='mapped' only when the mapping is clear; otherwise use status='ambiguous'."
    )
    user_prompt = row.get("judge_prompt", "")
    payload = {
        "model": args.deepseek_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
        "max_tokens": args.judge_max_tokens,
        "response_format": {"type": "json_object"},
        "stream": False,
    }
    request = urllib.request.Request(
        args.deepseek_base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=args.judge_timeout) as response:
        data = json.loads(response.read().decode("utf-8"))

    content = data["choices"][0]["message"]["content"]
    try:
        parsed = parse_json_object(content)
    except json.JSONDecodeError:
        normalized = parse_clean_numeric_response(row.get("question_id", ""), content)
        if not normalized:
            raise
        parsed = {
            "adjudicated_response": normalized,
            "confidence": 0.9,
            "status": "mapped",
            "notes": "Judge returned a bare answer code.",
        }
    parsed["_raw_content"] = content
    return parsed


def normalize_judge_confidence(value: Any) -> float:
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"high", "very high", "certain", "clear"}:
            return 0.95
        if lowered in {"medium", "moderate"}:
            return 0.6
        if lowered in {"low", "uncertain"}:
            return 0.3
        value = lowered.rstrip("%")
    try:
        confidence = float(value or 0)
    except (TypeError, ValueError):
        return 0.0
    if confidence > 1:
        confidence = confidence / 100
    return max(0.0, min(1.0, confidence))


def normalize_judge_suggestion(value: Any) -> str:
    """把 judge 可能返回的列表、带括号文本或逗号分隔文本统一成数字字符串。"""
    if isinstance(value, (list, tuple)):
        return " ".join(str(item).strip() for item in value if str(item).strip())

    text = str(value or "").strip()
    if not text:
        return ""

    # 有些模型会返回 [6]、["6"]、['1', '2'] 这类列表样式。
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = json.loads(text.replace("'", '"'))
            if isinstance(parsed, list):
                return " ".join(str(item).strip() for item in parsed if str(item).strip())
        except json.JSONDecodeError:
            pass

    text = text.strip("[](){}")
    text = text.replace('"', "").replace("'", "")
    return text.strip()


def adjudicate_one_with_deepseek(row: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    row = dict(row)
    last_error = ""
    result: Dict[str, Any] = {}
    for attempt in range(args.judge_retries + 1):
        try:
            result = call_deepseek_judge(row, args)
            last_error = ""
            break
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as error:
            last_error = str(error)
            if attempt < args.judge_retries:
                time.sleep(1.5 * (attempt + 1))

    if last_error:
        row["adjudication_status"] = "judge_error"
        row["adjudication_notes"] = last_error
        return row

    suggested = normalize_judge_suggestion(result.get("adjudicated_response", ""))
    status = str(result.get("status", "") or "").strip().lower()
    notes = str(result.get("notes", "") or "").strip()
    confidence = normalize_judge_confidence(result.get("confidence", 0))

    normalized = parse_clean_numeric_response(row.get("question_id", ""), suggested) if suggested else None
    row["judge_provider"] = "deepseek"
    row["judge_model"] = args.deepseek_model
    row["judge_status"] = status or "unknown"
    row["judge_suggested_response"] = normalized or suggested
    row["judge_confidence"] = confidence
    row["judge_raw_json"] = result.get("_raw_content", "")

    is_mapped_status = status in {"mapped", "ok", "clear", "valid", "match"}
    is_high_confidence_mapping = normalized and confidence >= args.judge_confidence_threshold and status not in {
        "ambiguous",
        "unclear",
        "invalid",
        "not_mapped",
    }
    if normalized and (is_mapped_status or is_high_confidence_mapping):
        row["adjudicated_response"] = normalized
        row["adjudication_status"] = "llm_mapped"
        row["adjudication_notes"] = notes
    elif normalized:
        row["adjudication_status"] = "llm_low_confidence"
        row["adjudication_notes"] = notes or f"confidence={confidence}"
    else:
        row["adjudication_status"] = "llm_ambiguous"
        row["adjudication_notes"] = notes
    return row


def auto_adjudicate_with_deepseek(
    rows: List[Dict[str, Any]],
    args: argparse.Namespace,
    adjudication_path: Optional[Path] = None,
    fieldnames: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    if args.auto_adjudicate != "deepseek":
        return rows

    updated_rows = [dict(row) for row in rows]
    pending_indices = [
        index
        for index, row in enumerate(updated_rows)
        if not row.get("adjudicated_response")
    ]
    if args.judge_max_rows:
        pending_indices = pending_indices[: args.judge_max_rows]

    pending_total = len(pending_indices)
    print(
        f"DeepSeek adjudication pending rows: {pending_total} "
        f"(workers={args.judge_workers})",
        flush=True,
    )
    if pending_total == 0:
        return updated_rows

    workers = max(1, min(args.judge_workers, pending_total))
    completed = 0

    def save_progress(force: bool = False) -> None:
        if not force and (not args.judge_save_every or completed % args.judge_save_every != 0):
            return
        if adjudication_path is not None and fieldnames is not None:
            write_dict_rows(updated_rows, adjudication_path, fieldnames)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(adjudicate_one_with_deepseek, updated_rows[index], args): index
            for index in pending_indices
        }
        for future in as_completed(futures):
            index = futures[future]
            try:
                updated_rows[index] = future.result()
            except Exception as error:  # 防御性兜底，避免单条异常打断整批判定。
                updated_rows[index]["adjudication_status"] = "judge_error"
                updated_rows[index]["adjudication_notes"] = str(error)
            completed += 1
            if completed == 1 or completed % 10 == 0 or completed == pending_total:
                row = updated_rows[index]
                print(
                    "  DeepSeek completed "
                    f"{completed}/{pending_total}: "
                    f"{row.get('model_alias', '')} | {row.get('country', '')} | "
                    f"{row.get('language', '')} | {row.get('question_id', '')} | "
                    f"{row.get('adjudication_status', '')}",
                    flush=True,
                )
            save_progress()

    save_progress(force=True)
    return updated_rows


def build_final_answer_rows(
    rows: List[Dict[str, Any]],
    adjudication_map: Dict[Tuple[str, str, str, str], str],
) -> List[Dict[str, Any]]:
    final_rows: List[Dict[str, Any]] = []
    for row in rows:
        key = (
            row.get("model_alias", ""),
            row.get("country", ""),
            row.get("language", ""),
            row.get("question_id", ""),
        )
        adjudicated_response = adjudication_map.get(key, "")
        final_response = adjudicated_response
        final_source = "adjudicated" if adjudicated_response else "missing"

        pca_value = ""
        if final_response:
            parsed_value = parse_response_for_pca(row.get("question_id", ""), final_response)
            pca_value = "" if parsed_value is None else parsed_value

        final_rows.append(
            {
                "model_alias": row.get("model_alias", ""),
                "model_name": row.get("model_name", ""),
                "country": row.get("country", ""),
                "language": row.get("language", ""),
                "question_id": row.get("question_id", ""),
                "scale": row.get("scale", ""),
                "dimension": row.get("dimension", ""),
                "raw_response": row.get("raw_response", ""),
                "adjudicated_response": adjudicated_response,
                "final_response": final_response,
                "final_source": final_source,
                "final_valid": str(bool(final_response)),
                "pca_value": pca_value,
                "round_count": row.get("round_count", ""),
                "valid_round_count": row.get("valid_round_count", ""),
                "consensus_count": row.get("consensus_count", ""),
                "consistency_rate": row.get("consistency_rate", ""),
                "json_path": row.get("json_path", ""),
            }
        )
    return final_rows


def build_final_answer_wide_rows(final_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[str, str, str, str], Dict[str, Any]] = {}
    for row in final_rows:
        key = (
            row.get("model_alias", ""),
            row.get("model_name", ""),
            row.get("country", ""),
            row.get("language", ""),
        )
        grouped.setdefault(
            key,
            {
                "model_alias": row.get("model_alias", ""),
                "model_name": row.get("model_name", ""),
                "country": row.get("country", ""),
                "language": row.get("language", ""),
                "valid_answer_count": 0,
                "missing_questions": "",
            },
        )
        question_id = row.get("question_id", "")
        final_response = row.get("final_response", "")
        grouped[key][question_id] = final_response

    wide_rows: List[Dict[str, Any]] = []
    for row in grouped.values():
        missing_questions = []
        valid_count = 0
        for question_id in QUESTION_ORDER:
            response = row.get(question_id, "")
            if response:
                valid_count += 1
            else:
                missing_questions.append(question_id)
                row[question_id] = ""
        row["valid_answer_count"] = valid_count
        row["missing_questions"] = " ".join(missing_questions)
        wide_rows.append(row)
    return wide_rows


def load_country_coordinate_map(path: Optional[Path]) -> Dict[str, Dict[str, Any]]:
    if path is None:
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        rows = json.load(handle)
    coordinate_map: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        country = row.get("Country") or row.get("country")
        if not country:
            continue
        try:
            pc1 = float(row["PC1_rescaled"])
            pc2 = float(row["PC2_rescaled"])
        except (KeyError, TypeError, ValueError):
            continue
        coordinate_map[country] = {
            "PC1_rescaled": pc1,
            "PC2_rescaled": pc2,
            "cultural_region": row.get("Cultural Region") or row.get("cultural_region", ""),
            "is_islamic": row.get("Islamic") if "Islamic" in row else row.get("is_islamic", ""),
        }
    return coordinate_map


def build_english_advantage_rows(
    coordinate_rows: List[Dict[str, Any]],
    country_coordinate_map: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    def distance(row: Dict[str, Any], country_coordinates: Dict[str, Any]) -> Optional[float]:
        try:
            pc1 = float(row["PC1_rescaled"])
            pc2 = float(row["PC2_rescaled"])
        except (KeyError, TypeError, ValueError):
            return None
        return ((pc1 - country_coordinates["PC1_rescaled"]) ** 2 + (pc2 - country_coordinates["PC2_rescaled"]) ** 2) ** 0.5

    grouped: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = {}
    for row in coordinate_rows:
        if row.get("status") != "ok":
            continue
        grouped.setdefault(
            (
                row.get("model_alias", ""),
                row.get("model_name", ""),
                row.get("country", ""),
            ),
            [],
        ).append(row)

    advantage_rows: List[Dict[str, Any]] = []
    for (model_alias, model_name, country), rows in grouped.items():
        country_coordinates = country_coordinate_map.get(country)
        if not country_coordinates:
            continue

        english_rows = [row for row in rows if row.get("language") == "en"]
        native_rows = [row for row in rows if row.get("language") != "en"]
        if not english_rows or not native_rows:
            continue

        english_row = english_rows[0]
        english_distance = distance(english_row, country_coordinates)
        if english_distance is None:
            continue

        for native_row in native_rows:
            native_distance = distance(native_row, country_coordinates)
            if native_distance is None:
                continue
            if native_distance == 0:
                english_advantage_pct = ""
                log_ratio = ""
            else:
                english_advantage_pct = ((native_distance - english_distance) / native_distance) * 100.0
                log_ratio = ""
                if english_distance > 0:
                    log_ratio = math.log(english_distance / native_distance)

            advantage_rows.append(
                {
                    "model_alias": model_alias,
                    "model_name": model_name,
                    "country": country,
                    "english_language": english_row.get("language", ""),
                    "native_language": native_row.get("language", ""),
                    "english_distance": english_distance,
                    "native_distance": native_distance,
                    "english_advantage_pct": english_advantage_pct,
                    "log_ratio": log_ratio,
                    "cultural_region": country_coordinates.get("cultural_region", ""),
                    "is_islamic": country_coordinates.get("is_islamic", ""),
                    "english_valid_answer_count": english_row.get("valid_answer_count", ""),
                    "native_valid_answer_count": native_row.get("valid_answer_count", ""),
                    "english_missing_questions": english_row.get("missing_questions", ""),
                    "native_missing_questions": native_row.get("missing_questions", ""),
                }
            )
    return advantage_rows


def load_pca_model(path: Optional[Path]) -> Optional[Dict[str, Any]]:
    if path is None:
        return None
    with open(path, "rb") as handle:
        return pickle.load(handle)


def project_coordinate(values: List[Optional[float]], pca_model: Dict[str, Any]) -> Dict[str, float]:
    import numpy as np

    data = np.array([np.nan if value is None else value for value in values], dtype=float)
    means = np.asarray(pca_model["ppca_means"], dtype=float)
    stds = np.asarray(pca_model["ppca_stds"], dtype=float)
    loadings = np.asarray(pca_model["ppca_C"], dtype=float)
    rotation = np.asarray(pca_model["rotation_matrix"], dtype=float)
    rescale = pca_model["pc_rescale_params"]

    standardized = (data - means) / stds
    standardized = np.nan_to_num(standardized, nan=0.0)
    pc = np.dot(standardized, loadings)
    rotated = np.dot(pc, rotation)
    pc1_rescaled = rescale["PC1"][0] * rotated[0] + rescale["PC1"][1]
    pc2_rescaled = rescale["PC2"][0] * rotated[1] + rescale["PC2"][1]
    return {
        "PC1": float(rotated[0]),
        "PC2": float(rotated[1]),
        "PC1_rescaled": float(pc1_rescaled),
        "PC2_rescaled": float(pc2_rescaled),
    }


def build_coordinate_rows(
    final_wide_rows: List[Dict[str, Any]],
    pca_model: Optional[Dict[str, Any]],
    pca_model_path: Optional[Path],
    min_answers: int,
) -> List[Dict[str, Any]]:
    coordinate_rows: List[Dict[str, Any]] = []
    for final_row in final_wide_rows:
        values: List[Optional[float]] = []
        for question_id in QUESTION_ORDER:
            response = final_row.get(question_id, "")
            values.append(parse_response_for_pca(question_id, response) if response else None)

        valid_count = sum(value is not None for value in values)
        missing_questions = " ".join(
            question_id for question_id, value in zip(QUESTION_ORDER, values) if value is None
        )
        row = {
            "model_alias": final_row["model_alias"],
            "model_name": final_row["model_name"],
            "country": final_row["country"],
            "language": final_row["language"],
            "mode": "final",
            "valid_answer_count": valid_count,
            "missing_questions": missing_questions,
            "pca_model_path": str(pca_model_path or ""),
        }
        for question_id in QUESTION_ORDER:
            row[question_id] = final_row.get(question_id, "")

        if pca_model is None:
            row["status"] = "missing_pca_model"
        elif valid_count < min_answers:
            row["status"] = "insufficient_valid_answers"
        else:
            row.update(project_coordinate(values, pca_model))
            row["status"] = "ok"
        coordinate_rows.append(row)
    return coordinate_rows


def write_postprocess_outputs(
    raw_rows: List[Dict[str, Any]],
    output_dir: Path,
    args: argparse.Namespace,
) -> None:
    normalized_rows = normalize_raw_rows(raw_rows)
    summaries_dir = output_dir / "summaries"

    queue_fieldnames = [
        "model_alias",
        "model_name",
        "country",
        "language",
        "question_id",
        "scale",
        "raw_response",
        "round_raw_responses",
        "round_count",
        "valid_round_count",
        "consensus_count",
        "consistency_rate",
        "prompt",
        "displayed_options",
        "option_texts",
        "allowed_response_format",
        "adjudication_guidance",
        "judge_prompt",
        "judge_provider",
        "judge_model",
        "judge_status",
        "judge_suggested_response",
        "judge_confidence",
        "judge_raw_json",
        "adjudication_status",
        "adjudicated_response",
        "adjudication_notes",
        "json_path",
    ]
    final_long_fieldnames = [
        "model_alias",
        "model_name",
        "country",
        "language",
        "question_id",
        "scale",
        "dimension",
        "raw_response",
        "adjudicated_response",
        "final_response",
        "final_source",
        "final_valid",
        "pca_value",
        "round_count",
        "valid_round_count",
        "consensus_count",
        "consistency_rate",
        "json_path",
    ]
    final_wide_fieldnames = [
        "model_alias",
        "model_name",
        "country",
        "language",
        "valid_answer_count",
        "missing_questions",
        *QUESTION_ORDER,
    ]

    pca_model_path = Path(args.pca_model_path) if args.pca_model_path else None
    if pca_model_path is not None and not pca_model_path.exists():
        print(f"PCA model path does not exist: {pca_model_path}")
        pca_model_path = None
    pca_model = load_pca_model(pca_model_path)
    if pca_model is None:
        print("PCA model not found. Coordinate CSVs will contain status=missing_pca_model.")
    else:
        print(f"PCA model: {pca_model_path}")

    coordinate_fieldnames = [
        "model_alias",
        "model_name",
        "country",
        "language",
        "mode",
        "status",
        "valid_answer_count",
        "missing_questions",
        "PC1",
        "PC2",
        "PC1_rescaled",
        "PC2_rescaled",
        "pca_model_path",
        *QUESTION_ORDER,
    ]
    country_coordinates_path = Path(args.country_coordinates_path) if args.country_coordinates_path else None
    if country_coordinates_path is not None and not country_coordinates_path.exists():
        print(f"Country coordinates path does not exist: {country_coordinates_path}")
        country_coordinates_path = None
    country_coordinate_map = load_country_coordinate_map(country_coordinates_path)
    if country_coordinate_map:
        print(f"Country coordinates: {country_coordinates_path}")
    else:
        print("Country coordinates not found. English-advantage CSVs will be empty.")

    advantage_fieldnames = [
        "model_alias",
        "model_name",
        "country",
        "english_language",
        "native_language",
        "english_distance",
        "native_distance",
        "english_advantage_pct",
        "log_ratio",
        "cultural_region",
        "is_islamic",
        "english_valid_answer_count",
        "native_valid_answer_count",
        "english_missing_questions",
        "native_missing_questions",
    ]

    all_final_rows: List[Dict[str, Any]] = []
    all_final_wide_rows: List[Dict[str, Any]] = []
    all_coordinate_rows: List[Dict[str, Any]] = []
    all_advantage_rows: List[Dict[str, Any]] = []

    rows_by_model: Dict[str, List[Dict[str, Any]]] = {}
    for row in normalized_rows:
        rows_by_model.setdefault(row["model_alias"], []).append(row)

    for model_alias, model_rows in rows_by_model.items():
        root = model_root(output_dir, model_alias)
        raw_dir = root / "raw"
        adjudication_dir = root / "adjudication"
        final_dir = root / "final"
        coordinates_dir = root / "coordinates"

        adjudication_rows = build_adjudication_queue(model_rows)
        adjudication_path = adjudication_dir / "adjudication.csv"
        adjudication_rows = merge_existing_adjudication_rows(
            adjudication_rows,
            adjudication_path,
            queue_fieldnames,
        )
        adjudication_rows = auto_adjudicate_with_deepseek(
            adjudication_rows,
            args,
            adjudication_path,
            queue_fieldnames,
        )
        if not adjudication_path.exists() or not args.skip_interview or args.auto_adjudicate != "none":
            write_dict_rows(adjudication_rows, adjudication_path, queue_fieldnames)

        adjudication_map = load_adjudication_map(adjudication_path)
        final_rows = build_final_answer_rows(model_rows, adjudication_map)
        final_wide_rows = build_final_answer_wide_rows(final_rows)
        coordinate_rows = build_coordinate_rows(
            final_wide_rows,
            pca_model,
            pca_model_path,
            args.min_coordinate_answers,
        )

        write_dict_rows(final_rows, final_dir / "final_answers_long.csv", final_long_fieldnames)
        write_dict_rows(final_wide_rows, final_dir / "final_answers_wide.csv", final_wide_fieldnames)
        write_dict_rows(coordinate_rows, coordinates_dir / "coordinates.csv", coordinate_fieldnames)
        advantage_rows = build_english_advantage_rows(coordinate_rows, country_coordinate_map)
        write_dict_rows(advantage_rows, coordinates_dir / "english_advantage.csv", advantage_fieldnames)

        all_final_rows.extend(final_rows)
        all_final_wide_rows.extend(final_wide_rows)
        all_coordinate_rows.extend(coordinate_rows)
        all_advantage_rows.extend(advantage_rows)

        print(f"\nModel outputs: {root}")
        print(f"  Raw interview JSONs: {raw_dir}")
        print(f"  Adjudication: {adjudication_path}")
        print(f"  Final answers: {final_dir / 'final_answers_long.csv'}")
        print(f"  Coordinates: {coordinates_dir / 'coordinates.csv'}")
        print(f"  English advantage: {coordinates_dir / 'english_advantage.csv'}")

    write_dict_rows(all_final_rows, summaries_dir / "all_final_answers_long.csv", final_long_fieldnames)
    write_dict_rows(all_final_wide_rows, summaries_dir / "all_final_answers_wide.csv", final_wide_fieldnames)
    write_dict_rows(all_coordinate_rows, summaries_dir / "all_coordinates.csv", coordinate_fieldnames)
    write_dict_rows(all_advantage_rows, summaries_dir / "all_english_advantage.csv", advantage_fieldnames)

    print(f"\nSummary outputs: {summaries_dir}")
    print(f"  All final answers: {summaries_dir / 'all_final_answers_long.csv'}")
    print(f"  All coordinates: {summaries_dir / 'all_coordinates.csv'}")
    print(f"  All English advantage: {summaries_dir / 'all_english_advantage.csv'}")


def truncate_text(text: str, limit: int = 100) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def ask_question(
    spec: Dict[str, Any],
    language: str,
    question_id: str,
    question_data: Dict[str, str],
    country: str,
    system_prompt: str,
    model: Any,
    tokenizer: Any,
    device: Any,
    args: argparse.Namespace,
    torch: Any,
) -> Dict[str, Any]:
    if question_id == "Y002":
        return ask_y002_sequential(
            language=language,
            question_data=question_data,
            country=country,
            system_prompt=system_prompt,
            model=model,
            tokenizer=tokenizer,
            device=device,
            args=args,
            torch=torch,
        )
    if question_id == "Y003":
        return ask_y003_sequential(
            language=language,
            question_data=question_data,
            country=country,
            system_prompt=system_prompt,
            model=model,
            tokenizer=tokenizer,
            device=device,
            args=args,
            torch=torch,
        )

    attempt_history: List[Dict[str, Any]] = []
    for attempt in range(args.max_retry):
        option_items = displayed_option_items(
            question_id=question_id,
            question_data=question_data,
            args=args,
            country=country,
            language=language,
        )
        prompt = build_text_prompt(
            spec=spec,
            system_prompt=system_prompt,
            question_data=question_data,
            question_id=question_id,
            country=country,
            language=language,
            args=args,
        )
        raw_response = generate_raw_response(
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            device=device,
            min_new_tokens=args.min_new_tokens,
            max_new_tokens=args.max_new_tokens,
            temperature=args.temperature,
            top_p=args.top_p,
            torch=torch,
        ).strip()
        attempt_history.append(
            {
                "attempt": attempt + 1,
                "answer_mode": "text",
                "raw_response": raw_response,
            }
        )
        if raw_response:
            return {
                "raw_response": raw_response,
                "method": "generate",
                "attempt_count": len(attempt_history),
                "attempt_history": attempt_history,
                "prompt": prompt,
                "displayed_options": displayed_options_json(option_items),
            }

    fallback = next(
        (item for item in reversed(attempt_history) if item.get("raw_response")),
        {"raw_response": ""},
    )
    return {
        "raw_response": fallback["raw_response"],
        "method": "generate",
        "attempt_count": len(attempt_history),
        "attempt_history": attempt_history,
        "prompt": prompt if "prompt" in locals() else "",
        "displayed_options": displayed_options_json(option_items) if "option_items" in locals() else "",
    }


def select_consensus_response(question_id: str, round_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    nonempty_count = sum(1 for result in round_results if result.get("raw_response"))
    selected = next((result for result in round_results if result.get("raw_response")), round_results[0])
    return {
        "raw_response": selected.get("raw_response", ""),
        "method": selected.get("method", ""),
        "round_count": len(round_results),
        "valid_round_count": nonempty_count,
        "consensus_count": nonempty_count,
        "consistency_rate": nonempty_count / len(round_results) if round_results else 0.0,
        "prompt": selected.get("prompt", ""),
        "displayed_options": selected.get("displayed_options", ""),
        "round_results": round_results,
    }


def run_interview_for_language(
    spec: Dict[str, Any],
    language: str,
    country: str,
    model: Any,
    tokenizer: Any,
    device: Any,
    dtype: Any,
    args: argparse.Namespace,
    torch: Any,
) -> Dict[str, Any]:
    responses: List[Dict[str, Any]] = []
    system_prompt = build_system_prompt(country, language)
    nonempty_count = 0
    questionnaire_rounds: Dict[str, List[Dict[str, Any]]] = {
        question_id: [] for question_id in QUESTION_ORDER
    }

    for round_index in range(args.consensus_count):
        print(f"  Round {round_index + 1}/{args.consensus_count}")
        for index, question_id in enumerate(QUESTION_ORDER, start=1):
            question_data = get_question(question_id, language)
            question_result = ask_question(
                spec=spec,
                language=language,
                question_id=question_id,
                question_data=question_data,
                country=country,
                system_prompt=system_prompt,
                model=model,
                tokenizer=tokenizer,
                device=device,
                args=args,
                torch=torch,
            )
            question_result["round"] = round_index + 1
            questionnaire_rounds[question_id].append(question_result)

            print(
                f"    {index:02d}/{len(QUESTION_ORDER)} {question_id}: "
                f"raw={truncate_text(question_result['raw_response'])!r}"
            )

    print("  Consensus summary")
    for index, question_id in enumerate(QUESTION_ORDER, start=1):
        round_results = questionnaire_rounds[question_id]

        consensus_result = select_consensus_response(question_id, round_results)
        raw_response = consensus_result["raw_response"]

        if raw_response:
            nonempty_count += 1

        print(
            f"  {index:02d}/{len(QUESTION_ORDER)} {question_id}: "
            f"raw={truncate_text(raw_response)!r} "
            f"nonempty_rounds={consensus_result['valid_round_count']}/{consensus_result['round_count']}"
        )

        question_data = get_question(question_id, language)
        responses.append(
            {
                "question_id": question_id,
                "question": question_data["question"],
                "scale": question_data["scale"],
                "dimension": question_data["dimension"],
                "raw_response": raw_response,
                "prompt": consensus_result["prompt"],
                "displayed_options": consensus_result["displayed_options"],
                "round_count": consensus_result["round_count"],
                "valid_round_count": consensus_result["valid_round_count"],
                "consensus_count": consensus_result["consensus_count"],
                "consistency_rate": consensus_result["consistency_rate"],
                "round_results": consensus_result["round_results"],
            }
        )

    return {
        "model_alias": spec["alias"],
        "model": spec["hf_id"],
        "model_name": spec["hf_id"],
        "country": country,
        "language": language,
        "timestamp": datetime.now().isoformat(),
        "total_questions": len(QUESTION_ORDER),
        "nonempty_responses": nonempty_count,
        "response_rate": (nonempty_count / len(QUESTION_ORDER) * 100.0) if QUESTION_ORDER else 0.0,
        "backend": "huggingface_local_cuda_single_file",
        "system_prompt": system_prompt,
        "responses": responses,
        "generation_config": {
            "runtime_device": str(device),
            "dtype": str(dtype),
            "quantization": args.quantization,
            "temperature": args.temperature,
            "top_p": args.top_p,
            "min_new_tokens": args.min_new_tokens,
            "max_new_tokens": args.max_new_tokens,
            "max_retry": args.max_retry,
            "consensus_count": args.consensus_count,
            "consensus_unit": "full_questionnaire",
            "answer_mode": "text",
            "option_order": args.option_order,
            "seed": args.seed,
            "trust_remote_code": spec["trust_remote_code"],
        },
    }


def save_result_json(result: Dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = f"{result['model_alias']}_{result['country']}_{result['language']}_{timestamp}"
    json_path = output_dir / f"{filename}.json"
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    return json_path


def build_raw_rows_from_result(result: Dict[str, Any], json_path: Path) -> List[Dict[str, Any]]:
    raw_rows: List[Dict[str, Any]] = []
    for response in result["responses"]:
        raw_rows.append(
            {
                "model_alias": result["model_alias"],
                "model_name": result["model_name"],
                "country": result["country"],
                "language": result["language"],
                "question_id": response["question_id"],
                "question": response.get("question", ""),
                "scale": response["scale"],
                "dimension": response["dimension"],
                "raw_response": response["raw_response"],
                "prompt": response.get("prompt", ""),
                "displayed_options": response.get("displayed_options", ""),
                "round_count": response.get("round_count", ""),
                "valid_round_count": response.get("valid_round_count", ""),
                "consensus_count": response.get("consensus_count", ""),
                "consistency_rate": response.get("consistency_rate", ""),
                "round_raw_responses": json.dumps(
                    [
                        {
                            "round": item.get("round"),
                            "raw_response": item.get("raw_response", ""),
                            "attempt_count": item.get("attempt_count"),
                            "method": item.get("method", ""),
                        }
                        for item in response.get("round_results", [])
                    ],
                    ensure_ascii=False,
                ),
                "json_path": str(json_path),
            }
        )
    return raw_rows


def load_raw_rows_from_json_outputs(output_dir: Path) -> List[Dict[str, Any]]:
    raw_rows: List[Dict[str, Any]] = []
    for json_path in sorted((output_dir / "models").glob("*/raw/*.json")):
        with open(json_path, "r", encoding="utf-8") as handle:
            result = json.load(handle)
        raw_rows.extend(build_raw_rows_from_result(result, json_path))
    return raw_rows


def main() -> None:
    args = parse_args()
    if args.max_retry < 1:
        raise ValueError("--max-retry must be at least 1.")
    if args.consensus_count < 1:
        raise ValueError("--consensus-count must be at least 1.")
    if args.min_new_tokens < 0:
        raise ValueError("--min-new-tokens cannot be negative.")
    if args.max_new_tokens < args.min_new_tokens:
        raise ValueError("--max-new-tokens must be greater than or equal to --min-new-tokens.")
    if not 0 <= args.judge_confidence_threshold <= 1:
        raise ValueError("--judge-confidence-threshold must be between 0 and 1.")
    if args.judge_workers < 1:
        raise ValueError("--judge-workers must be at least 1.")
    if args.judge_save_every < 0:
        raise ValueError("--judge-save-every cannot be negative.")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    multilingual_config = load_multilingual_config(args.language_config_path)
    apply_multilingual_questions(multilingual_config)

    if args.skip_interview:
        raw_rows = load_raw_rows_from_json_outputs(output_dir)
        if not raw_rows:
            raise FileNotFoundError(
                "No raw interview JSON files found for --skip-interview. "
                f"Expected files under {output_dir / 'models' / '<model_alias>' / 'raw'}."
            )
        print(f"Skip interview: rebuilding responses from interview JSON files under {output_dir / 'models'}")
        write_postprocess_outputs(raw_rows, output_dir, args)
        return

    if multilingual_config is None:
        raise FileNotFoundError(
            "No multilingual question config found. Pass --language-config-path "
            "or place multilingual_questions_complete.json in one of the default locations."
        )
    interview_targets = resolve_interview_targets(args, multilingual_config)

    torch, auto_causal_cls, auto_tokenizer_cls, bitsandbytes_config_cls, set_seed = import_hf_dependencies()
    device, dtype = resolve_runtime(torch, args.dtype)
    set_seed(args.seed)

    print(f"Device: {device}")
    print(f"Dtype: {dtype}")
    print(f"Language mode: {args.language_mode}")
    print(f"Targets: {len(interview_targets)} country-language pairs")
    if len(interview_targets) <= 20:
        print(f"Target list: {interview_targets}")
    else:
        print(f"First targets: {interview_targets[:10]}")
    print(f"Output dir: {output_dir}")

    raw_rows: List[Dict[str, Any]] = []

    for model_arg in args.models:
        spec = resolve_model_spec(model_arg)
        print(f"\nLoading model: {spec['hf_id']} (alias={spec['alias']})")
        model, tokenizer = load_model_and_tokenizer(
            spec=spec,
            device=device,
            dtype=dtype,
            torch=torch,
            auto_causal_cls=auto_causal_cls,
            auto_tokenizer_cls=auto_tokenizer_cls,
            bitsandbytes_config_cls=bitsandbytes_config_cls,
            quantization=args.quantization,
        )

        for country, language in interview_targets:
            print(f"\n{'=' * 72}")
            print(f"Model: {spec['hf_id']} | Country: {country} | Language: {language}")
            print(f"{'=' * 72}")

            result = run_interview_for_language(
                spec=spec,
                language=language,
                country=country,
                model=model,
                tokenizer=tokenizer,
                device=device,
                dtype=dtype,
                args=args,
                torch=torch,
            )
            json_path = save_result_json(result, model_root(output_dir, spec["alias"]) / "raw")

            print(
                f"\nSaved {spec['alias']} | {language}: "
                f"nonempty={result['nonempty_responses']}/{result['total_questions']}"
            )
            print(f"JSON: {json_path}")
            raw_rows.extend(build_raw_rows_from_result(result, json_path))

        del model
        torch.cuda.empty_cache()

    write_postprocess_outputs(raw_rows, output_dir, args)


if __name__ == "__main__":
    main()
