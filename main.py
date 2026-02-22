import os
import json
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import httpx
from dotenv import load_dotenv
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv("SILICONFLOW_API_KEY")

if not API_KEY:
    logger.error("SILICONFLOW_API_KEY not found in environment variables")

client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://api.siliconflow.cn/v1"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ==========================================
# 🚀 模块一：天气早报 API
# ==========================================
@app.get("/api/report")
async def generate_morning_report():
    # 获取国内天气（ITBoy 接口）
    url = "http://t.weather.itboy.net/api/weather/city/101010100"
    try:
        async with httpx.AsyncClient(proxy=None, timeout=10.0) as http_client:
            response = await http_client.get(url)
            data = response.json()
            if data.get("status") == 200:
                city = data["cityInfo"]["city"]
                forecast = data["data"]["forecast"][0] 
                weather_info = f"{city}今天{forecast['type']}，{forecast['low']}到{forecast['high']}。提示：{forecast['notice']}"
            else:
                weather_info = "气象局接口开了小差"
                logger.warning(f"Weather API returned status: {data.get('status')}")
    except Exception as e:
        weather_info = "天气获取失败"
        logger.error(f"Failed to fetch weather: {str(e)}")

    # 调用 DeepSeek V3 生成早报
    system_prompt = "你是一个幽默、毒舌但贴心的私人助理。请根据我提供的数据，写一段100字以内的早安播报。"
    user_prompt = f"今天的天气情报是：{weather_info}。请给我今天的早报！"
    
    try:
        completion = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.7
        )
        ai_report = completion.choices[0].message.content or "AI没有返回内容"
    except Exception as e:
        ai_report = f"AI 大脑连接失败，错误详情: {e}"
        logger.error(f"Failed to generate morning report: {str(e)}")

    return {"status": "success", "ai_report": ai_report}

# ==========================================
# 🎨 模块二：你画我猜发牌器 API
# ==========================================
@app.get("/api/draw_card")
async def draw_card():
    # 强制大模型输出 JSON 格式（这就是把 LLM 当做私有数据库的核心技术）
    system_prompt = """你是一个“你画我猜”游戏的发牌器。
    请随机生成一个适合用来画画猜谜的词语。
    必须严格以 JSON 格式返回，包含："word"(要猜的词语), "category"(分类), "hint"(带emoji的简短提示，不要出现原词)。
    示例：{"word": "九牛一毛", "category": "成语", "hint": "画很多牛和一根毛 🐂"}
    """
    try:
        completion = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": "发牌！给我一个新词。"}],
            temperature=0.9, 
            response_format={"type": "json_object"} # 强制返回 JSON
        )
        content = completion.choices[0].message.content
        if not content:
            raise ValueError("Empty response from AI")
        card_data = json.loads(content)
        return {"status": "success", "data": card_data}
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse card data JSON: {str(e)}")
        return {"status": "error", "data": {"word": "数据解析失败", "category": "错误", "hint": "请重试"}}
    except Exception as e:
        logger.error(f"Failed to draw card: {str(e)}")
        return {"status": "error", "data": {"word": "发牌失败", "category": "错误", "hint": "请检查网络或余额"}}

# ==========================================
# 🌐 静态网页挂载 (必须放在所有 API 路由的最后面)
# ==========================================
# 这行代码的意思是：把 frontend 文件夹里的文件，当做网页直接暴露给浏览器
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)