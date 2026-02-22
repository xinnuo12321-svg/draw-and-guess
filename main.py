@app.get("/api/draw_card")
async def draw_card():
    # 强制大模型输出 JSON 格式，这是获取“绘画提示”的关键
    system_prompt = """你是一个“你画我猜”游戏的发牌器。
    请随机生成一个适合用来画画猜谜的词语。
    必须严格以 JSON 格式返回，不要有任何 Markdown 包裹，不要有任何多余文字。
    包含字段：
    - "word": 要猜的词语
    - "category": 词语分类（如：成语、动物、生活用品等）
    - "hint": 15字以内带emoji的简短绘画提示，严禁出现原词。
    示例：{"word": "九牛一毛", "category": "成语", "hint": "画很多牛和一根毛 🐂"}
    """
    
    try:
        response = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "请发一张牌"}
            ],
            temperature=0.9, # 调高一点随机性
            response_format={ 'type': 'json_object' } # 强制 JSON 输出
        )
        
        # 将字符串解析为字典
        import json
        result = json.loads(response.choices[0].message.content)
        
        return {
            "status": "success",
            "word": result["word"],
            "category": result["category"],
            "hint": result["hint"]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}