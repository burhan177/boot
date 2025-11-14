#!/bin/bash
# سكريبت إعداد SSL للدومين

echo "🔒 إعداد SSL لـ abo-hamza.online"

# تثبيت Certbot
sudo apt update
sudo apt install -y certbot python3-certbot-apache

# الحصول على شهادة SSL
sudo certbot --apache -d abo-hamza.online -d www.abo-hamza.online

# إعداد التجديد التلقائي
sudo crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

echo "✅ تم إعداد SSL بنجاح!"
echo "🌐 الموقع متاح الآن على: https://abo-hamza.online"
