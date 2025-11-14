#!/usr/bin/env python3
# سكريبت للحصول على Chat ID

import requests
import json

# ضع توكن البوت هنا
TOKEN = "8406518150:AAHqmxStz6pdrKrZ7EAsu29U8XbzNab9A8s"

def get_chat_id():
    """الحصول على Chat ID من آخر الرسائل"""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    
    print("🔍 جاري البحث عن Chat ID...")
    print("📱 يرجى إرسال رسالة للبوت في تيليجرام أولاً!")
    print(f"🤖 البوت: @burhan775bot")
    print("💬 أرسل أي رسالة مثل: 'مرحبا' أو '/start'")
    print("-" * 50)
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data['ok'] and data['result']:
            # أخذ آخر رسالة
            last_update = data['result'][-1]
            chat_id = last_update['message']['chat']['id']
            user_name = last_update['message']['from'].get('first_name', 'غير معروف')
            username = last_update['message']['from'].get('username', 'لا يوجد')
            
            print("✅ تم العثور على Chat ID!")
            print(f"👤 الاسم: {user_name}")
            print(f"📛 Username: @{username}" if username != 'لا يوجد' else "📛 Username: لا يوجد")
            print(f"🆔 Chat ID: {chat_id}")
            print("-" * 50)
            print("📋 انسخ هذا الرقم واستخدمه في boot.py:")
            print(f'CHAT_ID = "{chat_id}"')
            
            return chat_id
        else:
            print("❌ لم يتم العثور على رسائل!")
            print("💡 تأكد من إرسال رسالة للبوت أولاً")
            return None
            
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return None

if __name__ == "__main__":
    get_chat_id()
