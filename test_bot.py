#!/usr/bin/env python3
# اختبار حالة البوت

import requests
import json

TOKEN = "8406518150:AAHqmxStz6pdrKrZ7EAsu29U8XbzNab9A8s"

def test_bot():
    """اختبار حالة البوت"""
    print("🤖 اختبار حالة البوت...")
    print("=" * 50)
    
    # اختبار getMe
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getMe"
        response = requests.get(url)
        data = response.json()
        
        if data['ok']:
            bot_info = data['result']
            print("✅ البوت يعمل بشكل صحيح!")
            print(f"📛 الاسم: {bot_info['first_name']}")
            print(f"🆔 Username: @{bot_info['username']}")
            print(f"🔢 ID: {bot_info['id']}")
        else:
            print("❌ خطأ في البوت:", data)
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False
    
    print("-" * 50)
    
    # اختبار getUpdates
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        response = requests.get(url)
        data = response.json()
        
        if data['ok']:
            updates = data['result']
            print(f"📨 عدد الرسائل المستلمة: {len(updates)}")
            
            if updates:
                print("📋 آخر الرسائل:")
                for i, update in enumerate(updates[-3:], 1):  # آخر 3 رسائل
                    message = update.get('message', {})
                    chat = message.get('chat', {})
                    user = message.get('from', {})
                    text = message.get('text', 'لا يوجد نص')
                    
                    print(f"  {i}. من: {user.get('first_name', 'غير معروف')}")
                    print(f"     Chat ID: {chat.get('id', 'غير متوفر')}")
                    print(f"     النص: {text}")
                    print()
                
                # أخذ آخر chat ID
                last_chat_id = updates[-1]['message']['chat']['id']
                print(f"🎯 Chat ID المطلوب: {last_chat_id}")
                print(f"📋 انسخ هذا الرقم: CHAT_ID = \"{last_chat_id}\"")
                
            else:
                print("📭 لا توجد رسائل مستلمة بعد")
                print("💡 تأكد من إرسال رسالة للبوت")
        else:
            print("❌ خطأ في استلام الرسائل:", data)
            
    except Exception as e:
        print(f"❌ خطأ في قراءة الرسائل: {e}")
    
    return True

if __name__ == "__main__":
    test_bot()
