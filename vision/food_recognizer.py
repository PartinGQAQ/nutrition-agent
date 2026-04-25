from PIL import Image
import base64
import json
from io import BytesIO
 
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel


def preprocess_image(image_bytes: bytes, max_size: int = 1024) -> bytes:
    """预处理图片"""
    
    image = Image.open(BytesIO(image_bytes))
    
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
        
    # 等比例缩放，保证最长边不超过 max_size
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.LANCZOS)
 
    # 输出为 JPEG bytes
    output = BytesIO()
    image.save(output, format="JPEG", quality=85)
    return output.getvalue()

def image_bytes_to_base64(image_bytes: bytes) -> str:
    """
    把图片二进制转成 base64 字符串。
    
    多模态模型 API 需要这个格式：
    "data:image/jpeg;base64,{base64字符串}"
    
    Args:
        image_bytes: 图片二进制（已经过预处理）
    
    Returns:
        纯 base64 字符串（不含 data URI 前缀）
    """
    return base64.b64encode(image_bytes).decode("utf-8")