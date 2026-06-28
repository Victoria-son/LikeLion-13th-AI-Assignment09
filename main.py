import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["API_KEY"]
client = genai.Client(api_key=API_KEY)

HISTORY_FILE = "chat_history.json"
KNOWLEDGE_FILE = "여행추천챗봇.txt"

def load_knowledge():
    if os.path.exists(KNOWLEDGE_FILE):
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

knowledge_context = load_knowledge()
chat_history = load_history()

sys_instruct = f"""
너는 제공된 [참고 문서]의 내용을 기반으로 질문에 답변하는 여행지 추천 AI 도우미야.
[답변 규칙]
1. 반드시 아래 제공된 [참고 문서]에 있는 사실에만 기반해서 답변해줘.
2. 문서에 없는 내용은 "제공된 문서에서 관련 정보를 찾을 수 없습니다."라고 정중하게 답변해.
3. 항상 친절하고 상냥한 존댓말을 사용해줘.
[참고 문서]
{knowledge_context}
"""

print("-- 챗봇 시작 (종료하려면 'q' 입력) --")
if chat_history:
    print(f"이전 대화 내역({len(chat_history) // 2}가지 대화)를 불러왔습니다.")

while True:
    user_input = input("\n질문: ")

    if user_input.lower() in ['q', 'quit', 'exit']:
        print("-- 챗봇 종료 --")
        break

    if not user_input.strip():
        continue

    chat_history.append({
        "role": "user",
        "parts": [{"text": user_input}]
    })

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=chat_history,
            config=types.GenerateContentConfig(
                system_instruction=sys_instruct
            )
        )

        print(f"답변: {response.text}")

        chat_history.append({
            "role": "model",
            "parts": [{"text": response.text}]
        })

        save_history(chat_history)

    except Exception as e:
        print(f"에러: {e}")
        chat_history.pop()