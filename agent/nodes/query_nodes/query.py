from agent.state import AgentState
from agent.context import DataAgentContext
from langgraph.runtime import Runtime
from jieba.analyse import extract_tags


def run(state: AgentState, runtime: Runtime[DataAgentContext]) -> AgentState:
    """查询语义并组织回复"""
    # 判断语义精准度，如果如果信息明确-> SQL， 不明确-> 语义查询， 都有信息 -> 结合查询
    question = state.question
    allow_pos = ('n',
                 'v',
                 'ns',
                 'nt',
                 'nz',
                 'nw',
                 'vn', 
                 'a',
                 'an',
                 'eng',
                 'i',
                 'l',
                 )
    
    keywords = extract_tags(question, 
                            topK=10, 
                            withWeight=False,
                            allowPOS=allow_pos
                            )
    
    prompt = """
你是饮食数据查询路由助手。请基于“用户问题 + 提取关键词”判断最合适的查询方式。

判定规则：
1) 选择 SQL：当问题包含明确的结构化约束（如具体时间、餐次、数值区间、排序、统计口径、精确筛选字段）。
2) 选择 语义查询：当问题偏开放表达、意图模糊、需要近义理解或主题检索，缺少可直接映射为 SQL 条件的约束。
3) 选择 结合查询：当问题同时包含明确结构化条件与语义意图，需要先结构化筛选再语义补充。

用户问题：{question}
关键词：{keywords}

请只输出以下三个字符串之一（不要输出其他解释）：
SQL
Semantic
Hybrid
"""
    
    
    if state.keyword == "SQL":
        return {"reply": "（占位）查询SQL功能开发中"}
    elif state.keyword == "Semantic":
        return {"reply": "（占位）查询语义功能开发中"}
    elif state.keyword == "Hybrid":
        return {"reply": "（占位）结合查询功能开发中"}
    else:
        return {"reply": "（占位）查询语义功能开发中"}
    
    return {"reply": "（占位）查询语义功能开发中"}