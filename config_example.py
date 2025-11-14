# مثال على الإعدادات المطلوبة لـ boot.py

# إعدادات البوت - غير هذه القيم
TOKEN = "1234567890:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw"  # توكن البوت من BotFather
CHAT_ID = "123456789"  # معرف المحادثة
SAVE_DIR = "captured_data"
WEB_PORT = 8080  # أو أي port متاح
PUBLIC_URL = "https://abo-hamza.online:8080"  # دومينك

# إذا كنت تستخدم reverse proxy (nginx):
# PUBLIC_URL = "https://abo-hamza.online"

# إعدادات إضافية للأمان
ALLOWED_IPS = ["0.0.0.0"]  # اتركها كما هي للسماح لجميع الـ IPs
DEBUG_MODE = False  # غير إلى True للاختبار فقط
