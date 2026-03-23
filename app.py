from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from google import genai
from google.genai import types
import uvicorn
import base64
import io
from PIL import Image
import os
import re

app = FastAPI()

API_KEY = "AIzaSyATgVSLWNGiFKqFWqBC29f-LFeDReN8LYE"

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

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Car Expert | خبير أعطال السيارات</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #1a1a2e;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #0f0f1a;
            border-bottom: 1px solid #2d2d44;
            padding: 12px 20px;
        }
        .header-content {
            max-width: 800px;
            margin: 0 auto;
        }
        .logo h1 {
            font-size: 1.5rem;
            color: #4c9aff;
        }
        .logo span {
            background: #4c9aff;
            color: #0f0f1a;
            font-size: 0.7rem;
            padding: 2px 8px;
            border-radius: 20px;
        }
        .services-bar {
            background: #0f0f1a;
            border-bottom: 1px solid #2d2d44;
            padding: 12px 20px;
        }
        .services-container {
            max-width: 800px;
            margin: 0 auto;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .service-badge {
            background: #2d2d44;
            padding: 8px 16px;
            border-radius: 30px;
            font-size: 0.85rem;
            color: #4c9aff;
            cursor: pointer;
        }
        .service-badge:hover {
            background: #3d3d5c;
        }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
        }
        .message {
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
        }
        .user-message {
            align-items: flex-end;
        }
        .bot-message {
            align-items: flex-start;
        }
        .message-content {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 24px;
            line-height: 1.5;
        }
        .user-message .message-content {
            background: #4c9aff;
            color: white;
            border-bottom-right-radius: 4px;
        }
        .bot-message .message-content {
            background: #2d2d44;
            border: 1px solid #3d3d5c;
            color: #e4e4e7;
            border-bottom-left-radius: 4px;
        }
        .suggestion-card {
            background: #1a5c8c;
            border-radius: 12px;
            padding: 12px;
            margin-top: 12px;
            cursor: pointer;
            text-align: center;
        }
        .booking-card {
            background: #2d2d44;
            border-radius: 16px;
            padding: 16px;
            margin: 10px 0;
            border: 1px solid #4c9aff;
        }
        .booking-card h4 {
            color: #4c9aff;
            margin-bottom: 12px;
        }
        .booking-input {
            width: 100%;
            padding: 10px;
            margin: 8px 0;
            background: #1a1a2e;
            border: 1px solid #3d3d5c;
            border-radius: 8px;
            color: white;
        }
        .booking-btn {
            background: #4c9aff;
            color: #0f0f1a;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 8px;
        }
        .input-container {
            border-top: 1px solid #2d2d44;
            background: #0f0f1a;
            padding: 16px 20px;
        }
        .input-wrapper {
            max-width: 800px;
            margin: 0 auto;
            display: flex;
            gap: 12px;
            background: #1a1a2e;
            border: 1px solid #2d2d44;
            border-radius: 32px;
            padding: 8px 16px;
        }
        textarea {
            flex: 1;
            border: none;
            outline: none;
            background: transparent;
            color: white;
            font-family: inherit;
            resize: none;
            padding: 8px 0;
        }
        .send-btn {
            background: #4c9aff;
            border: none;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            cursor: pointer;
            font-weight: bold;
        }
        .image-upload {
            cursor: pointer;
            padding: 8px;
            color: #8e8e93;
        }
        .image-upload input {
            display: none;
        }
        .image-preview {
            background: #2d2d44;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            color: #4c9aff;
            display: inline-block;
            margin-top: 8px;
        }
        .loading {
            display: flex;
            gap: 4px;
            padding: 12px 16px;
        }
        .loading span {
            width: 8px;
            height: 8px;
            background: #8e8e93;
            border-radius: 50%;
            animation: bounce 1.4s infinite;
        }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">
                <h1>🚗 Car Expert <span>AI</span></h1>
            </div>
        </div>
    </div>
    
    <div class="services-bar">
        <div class="services-container">
            <div class="service-badge" onclick="bookService('فحص متنقل')">🔧 فحص متنقل</div>
            <div class="service-badge" onclick="bookService('فحص سيارات مستعملة')">🔍 فحص سيارات مستعملة</div>
            <div class="service-badge" onclick="bookService('غسيل احترافي')">🧼 غسيل احترافي</div>
            <div class="service-badge" onclick="bookService('إكسسوارات')">✨ إكسسوارات</div>
            <div class="service-badge" onclick="bookService('تأجير')">🚙 تأجير</div>
            <div class="service-badge" onclick="bookService('حجز صيانة')">📅 حجز صيانة</div>
            <div class="service-badge" onclick="bookService('صيانة دورية')">🛞 صيانة دورية</div>
            <div class="service-badge" onclick="bookService('خدمات متنقلة')">🔋 خدمات متنقلة</div>
        </div>
    </div>
    
    <div class="chat-container" id="chatContainer">
        <div class="message bot-message">
            <div class="message-content">
                👋 مرحباً بك في Car Expert!<br><br>
                اسألني عن أي مشكلة في سيارتك، وسأقترح لك الخدمة المناسبة.
            </div>
        </div>
    </div>
    
    <div class="input-container">
        <div class="input-wrapper">
            <div class="image-upload">
                <label for="imageInput">📷</label>
                <input type="file" id="imageInput" accept="image/*">
            </div>
            <textarea id="problemInput" rows="1" placeholder="اكتب مشكلة سيارتك... (Enter للإرسال)"></textarea>
            <button class="send-btn" id="sendBtn">➤</button>
        </div>
        <div id="imagePreview" style="max-width:800px; margin:8px auto 0;"></div>
    </div>

    <script>
        let currentImage = null;
        
        function addMessage(text, isUser, showSuggestion=false, suggestionService=null) {
            const container = document.getElementById('chatContainer');
            const div = document.createElement('div');
            div.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            let html = `<div class="message-content">${text.replace(/\\n/g, '<br>')}</div>`;
            if (showSuggestion && suggestionService) {
                html += `<div class="suggestion-card" onclick="bookService('${suggestionService}')">🔧 احجز خدمة ${suggestionService}</div>`;
            }
            div.innerHTML = html;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }
        
        function addBookingForm(service) {
            const container = document.getElementById('chatContainer');
            const existing = document.getElementById('bookingForm');
            if (existing) existing.remove();
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.id = 'bookingForm';
            div.innerHTML = `<div class="message-content"><div class="booking-card"><h4>📝 حجز: ${service}</h4>
                <input type="text" id="bookingName" class="booking-input" placeholder="الاسم الكامل">
                <input type="tel" id="bookingPhone" class="booking-input" placeholder="رقم الهاتف">
                <input type="text" id="bookingCar" class="booking-input" placeholder="موديل السيارة">
                <input type="datetime-local" id="bookingDate" class="booking-input">
                <input type="text" id="bookingLocation" class="booking-input" placeholder="الموقع">
                <button class="booking-btn" onclick="submitBooking('${service}')">✅ تأكيد الحجز</button></div></div>`;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }
        
        function submitBooking(service) {
            const name = document.getElementById('bookingName')?.value;
            const phone = document.getElementById('bookingPhone')?.value;
            const car = document.getElementById('bookingCar')?.value;
            const date = document.getElementById('bookingDate')?.value;
            const loc = document.getElementById('bookingLocation')?.value;
            if (!name || !phone || !car || !date || !loc) {
                alert('❌ الرجاء ملء جميع الحقول');
                return;
            }
            document.getElementById('bookingForm')?.remove();
            addMessage(`✅ تم تأكيد حجز ${service}\nالاسم: ${name}\nالهاتف: ${phone}\nالسيارة: ${car}\nالتاريخ: ${new Date(date).toLocaleString('ar-EG')}\nالموقع: ${loc}\n📞 سيتم التواصل خلال 24 ساعة`, false);
        }
        
        function bookService(service) {
            addMessage(`أود حجز خدمة: ${service}`, true);
            addBookingForm(service);
        }
        
        async function sendMessage() {
            const input = document.getElementById('problemInput');
            const msg = input.value.trim();
            if (!msg && !currentImage) return;
            addMessage(msg || '📷 صورة', true);
            input.value = '';
            const fd = new FormData();
            fd.append('problem', msg || 'حلل الصورة');
            if (currentImage) fd.append('image', currentImage);
            const loading = document.createElement('div');
            loading.className = 'message bot-message';
            loading.innerHTML = '<div class="message-content"><div class="loading"><span></span><span></span><span></span></div></div>';
            document.getElementById('chatContainer').appendChild(loading);
            try {
                const res = await fetch('/analyze', { method: 'POST', body: fd });
                const data = await res.json();
                loading.remove();
                addMessage(data.diagnosis, false);
                if (data.suggestion) {
                    addMessage(`🔧 أنصحك بحجز خدمة "${data.suggestion}"`, false, true, data.suggestion);
                }
            } catch(e) {
                loading.remove();
                addMessage('❌ خطأ في الاتصال', false);
            }
            currentImage = null;
            document.getElementById('imagePreview').innerHTML = '';
        }
        
        document.getElementById('imageInput').addEventListener('change', e => {
            const file = e.target.files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = ev => {
                currentImage = ev.target.result.split(',')[1];
                document.getElementById('imagePreview').innerHTML = '<div class="image-preview">📷 صورة مرفوعة ✓</div>';
            };
            reader.readAsDataURL(file);
        });
        
        document.getElementById('problemInput').addEventListener('keydown', e => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
        });
        document.getElementById('sendBtn').addEventListener('click', sendMessage);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE

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