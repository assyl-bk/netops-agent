import json, random, re, time
from pathlib import Path
import httpx
from app.agent.llm import chat, user_msg

OUT = Path("data/tickets/tickets.jsonl")
OUT.parent.mkdir(parents=True, exist_ok=True)
TARGET, BATCH = 240, 10

SITES = ["Tunis-01", "Tunis-02", "Sfax-01", "Sousse-01",
         "Bizerte-01", "Gabes-01", "Nabeul-01", "Kairouan-01"]
TOPICS = {
    "FTTH": ["ONT not syncing", "low throughput", "frequent disconnections",
             "PON port errors", "wrong VLAN provisioning"],
    "4G/5G": ["high latency", "handover failures", "attach rejects",
              "poor coverage", "core network overload"],
    "DNS": ["resolution failures", "slow lookups", "wrong records"],
    "BGP/routing": ["session flapping", "route leak", "missing prefixes"],
    "Wi-Fi": ["interference", "authentication failures", "roaming drops"],
    "Transport": ["packet loss on a link", "MTU mismatch", "QoS misconfiguration"],
}

def count():
    return sum(1 for _ in OUT.open(encoding="utf-8")) if OUT.exists() else 0

def parse(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)

while (n := count()) < TARGET:
    tech = random.choice(list(TOPICS))
    topic = random.choice(TOPICS[tech])
    prompt = (
        f"Generate {BATCH} realistic, DIFFERENT network incident tickets for "
        f"technology {tech}, focusing on: {topic}. Return ONLY a JSON array. "
        "Each item has keys: symptom (1-2 sentences as reported by a customer or "
        "NOC), root_cause (technical, 1-2 sentences), resolution (1-3 concrete "
        "steps), severity (low|medium|high|critical), "
        f"site (one of {SITES})."
    )
    try:
        items = parse(chat([user_msg(prompt)]).text)
    except (json.JSONDecodeError, KeyError):
        print("bad JSON, retrying"); continue
    except httpx.HTTPStatusError as e:
        print("stopped:", e.response.status_code, "- rerun later, it resumes"); break
    with OUT.open("a", encoding="utf-8") as f:
        for i, it in enumerate(items):
            it.update(id=f"T-{n + i + 1:04d}", technology=tech)
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"{count()}/{TARGET}")
    time.sleep(6)