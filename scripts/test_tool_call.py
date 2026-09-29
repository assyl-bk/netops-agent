from app.agent.llm import chat, user_msg, tool_result_msg

TOOLS = [
    {"name": "search_docs",
     "description": "Search technical documentation (RFCs, 3GPP, vendor guides) "
                    "for how a protocol or network feature works.",
     "parameters": {"type": "object",
                    "properties": {"query": {"type": "string", "description": "search query"}},
                    "required": ["query"]}},
    {"name": "query_kpis",
     "description": "Query the network KPI database: latency, packet loss, "
                    "throughput per site and date. Use for measured numbers.",
     "parameters": {"type": "object",
                    "properties": {"question": {"type": "string", "description": "natural-language question"}},
                    "required": ["question"]}},
]
SYSTEM = (
    "You are a network operations assistant. "
    "Use tools to find information. "
    "Answer ONLY from the tool results. Do not add facts that are not in them. "
    "If the tool results do not contain the answer, say you don't have enough information. "
    "Cite the source of each claim. "
    "For greetings or small talk, answer directly without tools."
)

questions = [
    "How does BGP route withdrawal work?",
    "What was the packet loss at site Tunis-01 last Monday?",
    "Hello, who are you?",
]

for q in questions:
    r = chat([user_msg(q)], TOOLS, SYSTEM)
    print(q, "->", [(c.name, c.args) for c in r.tool_calls] or r.text[:80])

# full round trip on the first question, with a fake tool result
q = questions[0]
r = chat([user_msg(q)], TOOLS, SYSTEM)
if r.tool_calls:
    call = r.tool_calls[0]
    fake = {"chunks": ["A BGP speaker withdraws a route by listing it in the "
                       "withdrawn-routes field of an UPDATE message."]}
    history = [user_msg(q), r.raw_content, tool_result_msg(call.name, fake)]
    print("\nFINAL:", chat(history, TOOLS, SYSTEM).text)