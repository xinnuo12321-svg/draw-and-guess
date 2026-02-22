from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from openai import AsyncOpenAI
import random

app = FastAPI()

# 1. 初始化 AI 客户端
api_key = os.getenv("SILICONFLOW_API_KEY")
client = AsyncOpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")

# ==========================================
# 🎨 模块一：你画我猜出题器
# ==========================================
@app.get("/api/draw_card")
async def draw_card():
    topics = ["动物", "日常用品", "食物", "交通工具", "常见职业", "水果"]
    selected_topic = random.choice(topics)
    
    try:
        response = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {"role": "system", "content": "你是一个你画我猜出题助手。"},
                {"role": "user", "content": f"请给出一个属于【{selected_topic}】类别的词语。只需输出词语本身，不要废话。"}
            ],
            temperature=0.8
        )
        word = response.choices[0].message.content.strip()
        return {"status": "success", "word": word, "category": selected_topic}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ==========================================
# 🌤️ 模块二：毒舌天气预报
# ==========================================
@app.get("/api/weather")
async def get_weather(city: str = "北京"):
    try:
        response = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {"role": "system", "content": "你是一个幽默、犀利、有点毒舌的天气播报员。"},
                {"role": "user", "content": f"请吐槽一下【{city}】今天的天气，给出穿衣或出门建议。字数50字以内，要好玩！"}
            ],
            temperature=0.8
        )
        report = response.choices[0].message.content.strip()
        return {"status": "success", "city": city, "report": report}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ==========================================
# ⚠️ 必须放在最底部：挂载前端网页
# ==========================================
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")