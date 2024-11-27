# SMS Service API  

Bu loyiha **Django Rest Framework (DRF)** va **Eskiz API** yordamida SMS xizmati uchun oddiy va funksional API yaratish maqsadida ishlab chiqilgan.  

## 🚀 Loyihaning imkoniyatlari  
- SMS yuborish uchun API interfeysi.  
- Telefon raqamlarini maxsus validator yordamida tekshirish.  
- Django DRF orqali mustahkam va kengaytiriladigan backend.  

## 🛠 O‘rnatish va ishga tushirish  

### Talablar  
Loyihani ishga tushirishdan oldin quyidagi dasturlar o‘rnatilgan bo‘lishi kerak:  
- Python (>= 3.8)  
- Django (>= 4.x)  
- Django Rest Framework  

### O‘rnatish bo‘yicha qadamlar  

1. Loyihani klonlash:  
   ```bash
   git clone https://github.com/foydalanuvchi/sms-service-api.git
   cd sms-service-api
2. Virtual muhit yaratish va ishga tushirish:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows uchun: venv\Scripts\activate
   ```
3. Talab qilinadigan kutubxonalarni o‘rnatish:
   ```bash
   pip install -r requirements.txt
   ```
4. Django sozlamalarini yangilash:
   settings.py faylida Eskiz API uchun TOKEN va boshqa kerakli sozlamalarni kiriting:
   ```python
   ESKIZ_API_TOKEN = 'sizning_tokeningiz'
   ```
5. Ma'lumotlar bazasini migratsiya qilish:
   ```bash
   python manage.py migrate
   ```
6. Djangoni ishga tushirish:
   ```bash
   python manage.py runserver
   ```

### 🧑‍💻 Hissa qo‘shish
Pull requestlar va takliflar har doim ochiq! Quyidagi qadamlar orqali hissa qo‘shishingiz mumkin:
1. Fork qiling.
2. O‘z o‘zgarishlaringizni amalga oshiring.
3. Pull request yuboring.

### 📄 Litsenziya
Ushbu loyiha MIT litsenziyasi asosida taqdim etiladi.

### 💬 Aloqa
Savol yoki takliflaringiz bo‘lsa, menga Telegram orqali murojaat qiling: @rozievich
