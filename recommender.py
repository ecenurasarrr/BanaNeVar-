import os
import random
from google import genai

class AIRecommender:
    def __init__(self):
        # API anahtarını çevre değişkenlerinden al
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
            
    def get_daily_tip(self, events):
        """ Statik açılış önerisi yerine AI ile günün önerisini oluşturur """
        if not self.api_key or not self.client or not events:
            return self._get_fallback_tip(events)
            
        try:
            event_names = [f"'{e['name']}' ({e['category']})" for e in events]
            events_str = ", ".join(event_names)
            
            prompt = f"""
            Mersin'deki etkinlikler: {events_str}
            Bu etkinlikler arasından rastgele birini seç ve kullanıcıya bugün için harika bir öneri olarak sun. 
            Çok kısa olsun (tek cümle). HTML <b> etiketini etkinlik ismi için kullan.
            """
            
            response = self.client.models.generate_content(
                 model='gemini-flash-latest',
                 contents=prompt
             )
            return response.text if response and response.text else self._get_fallback_tip(events)
        except:
            return self._get_fallback_tip(events)

    def get_interactive_tip(self, events, user_input):
        """
        Kullanıcının ne istediğini anlayarak, veritabanındaki etkinlikleri buna göre süzer 
        ve ona çok spesifik bir program/tavsiye çizer.
        """
        if not self.api_key or not self.client:
            return "Sistemde Gemini API anahtarı ayarlı olmadığı için şu an sana özel öneri oluşturamıyorum. Lütfen .env dosyanı kontrol et."
            
        try:
            event_names = [f"'{e['name']}' ({e['category']} - {e['venue']}, Tarih: {e['date']})" for e in events]
            events_str = "\n".join(event_names)
            
            prompt = f"""
            Sen çok samimi, enerjik ve uzman bir Mersin Etkinlik Rehberisin.
            Mersin'deki mevcut biletli etkinlikler şunlar:
            {events_str}
            
            Kullanıcıdan gelen talep: "{user_input}"
            
            Görev: Kullanıcının talebine en uygun olan 1 veya 2 etkinliği seç. Neden bunu seçtiğini, 
            kullanıcının talebiyle nasıl bağdaştığını samimi bir dille, kısa bir paragrafta (maks 3 cümle) anlat.
            Önemli yerleri HTML <b> etiketleriyle vurgula. Asla etkinlik listesinde olmayan bir etkinliği uydurma. 
            Direkt cevaba gir, "merhaba", "elbette" vs deme.
            """
            
            response = self.client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt
            )

            if response and response.text:
                return response.text.replace('\n', '<br>')
            else:
                return "Şu an Mersin bulutlu galiba, öneri sistemim bağlatılamadı."
                
        except Exception as e:
            print("Gemini API Error:", e)
            # API hatası durumunda akıllı fallback
            if events:
                user_input_lower = user_input.lower()
                
                # Mood mapping
                mood_map = {
                    'enerjik': ['Müzik', 'Gezi'],
                    'yorgun': ['Sinema', 'Gastronomi'],
                    'aç': ['Gastronomi'],
                    'kültür': ['Tiyatro', 'Gezi'],
                    'eğlence': ['Müzik', 'Sinema'],
                    'müzik': ['Müzik'],
                    'yemek': ['Gastronomi'],
                    'gezi': ['Gezi'],
                    'film': ['Sinema']
                }

                # Try exact matches first
                matched = [e for e in events if user_input_lower in e['name'].lower() or user_input_lower in e['category'].lower()]
                
                # If no exact match, try mood mapping
                if not matched:
                    for mood, categories in mood_map.items():
                        if mood in user_input_lower:
                            matched = [e for e in events if e['category'] in categories]
                            break
                
                if matched:
                    selected = random.choice(matched)
                    return f"Şu an asistanım yoğun ama moduna göre senin için <b>{selected['name']}</b> etkinliğini buldum! Mersin'de bugün buna ne dersin?"
            
            return "Şu an Mersin bulutlu galiba, öneri sistemim bağlatılamadı. Ama etkinlik listesine göz atabilirsin!"

    def _get_fallback_tip(self, events):
        if len(events) >= 2:
            event1 = events[0]['name']
            return f"<b>{event1}</b> ile harika bir başlangıç yapabilirsin. Gelişmiş bir arama için bana ne yapmak istediğini söyle!"
        return "Mersin'i keşfetmek için harika bir gün!"