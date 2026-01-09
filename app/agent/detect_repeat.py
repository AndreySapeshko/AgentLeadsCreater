from app.agent.client import llm_client
from app.db.models import Memory


async def detect_repeat(
    user_input: str,
    memories: list[Memory],
) -> bool:
    if not memories:
        return False

    topics = "\n".join(f"- {m.title}" for m in memories)

    prompt = f"""
        User request:
        "{user_input}"

        Previously researched topics:
        {topics}

        Question:
        Does the user request repeat or strongly overlap with any of the previous topics?

        Answer ONLY one word:
        YES or NO
        """
    print("REQUEST LLM from detect_repeat")
    response = await llm_client.chat(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a strict classifier."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        max_tokens=3,
    )

    answer = response.choices[0].message.content.strip().upper()
    return answer == "YES"
