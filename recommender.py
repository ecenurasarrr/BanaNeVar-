import random

class LocalRecommender:
    def get_daily_tip(self, event1, event2):
        # Kendi yazdığın profesyonel tavsiye şablonları
        tips = [
            f"Mersin'de bugün harika bir enerji var! {event1} ile başlayıp günü {event2} ile bitirmek sana çok iyi gelecek.",
            f"Kendi şehrini keşfet! {event1} etkinliği tam senin tarzın, ardından {event2} ile keyifli bir mola verebilirsin.",
            f"Haftanın yorgunluğunu atmak için {event1} ve {event2} ikilisi mükemmel bir tercih.",
            f"Dışarıda hayat var! {event1} ve {event2} planı ile Mersin'in tadını çıkarmaya hazır mısın?"
        ]
        return random.choice(tips)