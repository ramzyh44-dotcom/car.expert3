from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from google import genai
from google.genai import types
import uvicorn
import base64
import io
from PIL import Image
import os
import re

app = FastAPI()

# تشغيل الملفات الثابتة (الصور)
app.mount("/static", StaticFiles(directory="."), name="static")

# ضع الـ API Key بتاعك هنا
API_KEY = "AIzaSyCzJtPDPv8fpR_gSyHIXZ5hv4rEfZMW3as"

SERVICES = {
    "فحص متنقل": "فحص السيارة في موقع العميل",
    "فحص سيارات مستعملة": "فحص شامل قبل شراء سيارة مستعملة",
    "غسيل احترافي": "غسيل السيارات بأحدث التقنيات",
    "إكسسوارات": "تركيب اكسسوارات السيارات",
    "تأجير": "تأجير السيارات لشركات السياحة",
    "حجز صيانة": "حجز موعد صيانة السيارة",
    "صيانة دورية": "تغيير الزيت أو الإطارات دورياً",
    "خدمات متنقلة": "تبديل البطاريات أو تصليح الإطارات"
}

def diagnose_and_suggest(problem, image_base64=None):
    client = genai.Client(api_key=API_KEY)
    model = "gemini-2.5-flash"
    
    parts = [types.Part.from_text(text=problem)]
    
    if image_base64:
        parts.append(
            types.Part.from_bytes(
                data=base64.b64decode(image_base64),
                mime_type="image/jpeg"
            )
        )
    
    services_list = "\n".join([f"- {k}: {v}" for k, v in SERVICES.items()])
    
    config = types.GenerateContentConfig(
        system_instruction=[
            types.Part.from_text(text=f"""أنت خبير سيارات محترف متخصص في أعطال السيارات.

مهمتك:
1. فهم مشكلة السيارة من وصف المستخدم
2. تقديم تقرير تشخيصي بالعربية (الأسباب، درجة الخطورة، الإجراءات)
3. **في نهاية ردك، اذكر بوضوح الخدمة المناسبة من قائمة خدماتنا**
4. استخدم هذا التنسيق بالضبط: [SERVICE_SUGGESTION] اسم الخدمة

خدماتنا:
{services_list}

مثال للرد:
[التقرير التشخيصي...]

[SERVICE_SUGGESTION] فحص متنقل"""),
        ],
    )
    
    contents = [types.Content(role="user", parts=parts)]
    response = client.models.generate_content(model=model, contents=contents, config=config)
    return response.text

def extract_suggestion(text):
    match = re.search(r'\[SERVICE_SUGGESTION\]\s*(.+)', text)
    if match:
        for key in SERVICES.keys():
            if key in match.group(1):
                return key
    return None

# الصفحة الرئيسية - تخدم dashboard.html
@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head><title>خطأ</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>⚠️ ملف dashboard.html غير موجود</h1>
            <p>تأكد من وجود الملف في نفس المجلد مع app.py</p>
            <p>المسار الحالي: C:\\Users\\hp\\Desktop\\CarExpert3</p>
        </body>
        </html>
        """)

# مسار الصورة
@app.get("/logo.png")
async def get_logo():
    try:
        with open("logo.png", "rb") as f:
            return Response(content=f.read(), media_type="image/png")
    except:
        return Response(content=b"", media_type="image/png")

# مسار التحليل (للاتصال بالشات)
@app.post("/analyze")
async def analyze(problem: str = Form(...), image: str = Form(None)):
    try:
        full = diagnose_and_suggest(problem, image)
        diag = re.sub(r'\n?\[SERVICE_SUGGESTION\].*', '', full)
        sug = extract_suggestion(full)
        return {"diagnosis": diag.strip().replace(chr(10), '<br>'), "suggestion": sug}
    except Exception as e:
        return {"diagnosis": f"❌ خطأ: {str(e)}", "suggestion": None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)