from langchain_core.tools import tool
from datetime import datetime
import math

@tool
def calculator(expression: str) -> str:
    """
    计算器工具：用于执行数学表达式计算。
    
    Args:
        expression: 数学表达式字符串，例如 "2 + 3 * 4"
    
    Returns:
        计算结果字符串
    """
    try:
        result = eval(expression, {"__builtins__": None}, {"math": math})
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

@tool
def get_current_time() -> str:
    """
    获取当前时间工具：返回当前日期和时间。
    
    Returns:
        当前日期和时间字符串
    """
    now = datetime.now()
    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')}"

@tool
def weather_query(city: str) -> str:
    """
    天气查询工具：获取指定城市的天气信息（模拟数据）。
    
    Args:
        city: 城市名称
    
    Returns:
        天气信息字符串
    """
    weather_data = {
        "北京": {"temperature": "25°C", "condition": "晴", "wind": "北风3级"},
        "上海": {"temperature": "28°C", "condition": "多云", "wind": "东风2级"},
        "广州": {"temperature": "32°C", "condition": "雷阵雨", "wind": "南风4级"},
        "深圳": {"temperature": "30°C", "condition": "多云转晴", "wind": "东南风3级"},
        "杭州": {"temperature": "27°C", "condition": "阴", "wind": "东北风2级"},
    }
    
    if city in weather_data:
        w = weather_data[city]
        return f"{city}天气: {w['condition']}, 温度: {w['temperature']}, 风力: {w['wind']}"
    else:
        return f"暂未收录{city}的天气信息"

tools = [calculator, get_current_time, weather_query]