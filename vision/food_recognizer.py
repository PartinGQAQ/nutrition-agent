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
    
    image = Image.open(image_bytes)
    
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
        
    # 等比例缩放，保证最长边不超过 max_size
    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.LANCZOS)
 
    # 输出为 JPEG bytes
    output = BytesIO()
    image.save(output, format="JPEG", quality=85)
    return output.getvalue()

