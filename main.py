from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from openai import AsyncOpenAI
import random

app = FastAPI()

# 1. 初始化 AI 客户端（自动从 Render 环境变量读取密钥）
api_key = os.getenv("SILICONFLOW_API_KEY")
client = AsyncOpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")

# 2. 你画我猜的 API 接口
@app.get("/api/draw_card")
async def draw_card():
    topics = ["动物", "日常用品", "食物", "交通工具", "常见职业", "水果"]
    selected_topic = random.choice(topics)
    
    try:
        response = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {"role": "system", "content": "你是一个你画我猜出题助手。"},
                {"role": "user", "content": f"请给出一个属于【{selected_topic}】类别的词语（例如：老虎、手机、苹果）。只需输出词语本身，不要任何标点和废话。"}
            ],
            temperature=0.8
        )
        word = response.choices[0].message.content.strip()
        return {"status": "success", "word": word, "category": selected_topic}
    except Exception as e:
        # 如果出错，把真实的错误信息返回给前端，方便排查
        return {"status": "error", "message": str(e)}

# 3. 静态页面挂载（这一句必须放在代码的最下面！）
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")