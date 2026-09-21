# Ovoza service and location catalog.
# Services intentionally restored from the original Ovoza catalog,
# except the three services removed for the current product scope:
# Konsert, Korporativ tadbir, To'y tashkil qilish.
SERVICES = [
    ("host", "🎤 Boshlovchilik", "🎤 Ведение мероприятий"),
    ("ceremony", "🎉 Marosimlar", "🎉 Церемонии"),
    ("event", "🎪 Tadbir tashkil qilish", "🎪 Организация мероприятий"),
]

# Ovoza currently operates only within Tashkent city.
CITY = ("toshkent", "Toshkent", "Ташкент")
DISTRICTS = [
    ("yunusobod", "Yunusobod", "Юнусабад"),
    ("mirzo_ulugbek", "Mirzo Ulugbek", "Мирзо-Улугбек"),
    ("olmazor", "Olmazor", "Алмазар"),
    ("shayxontoxur", "Shayxontoxur", "Шайхантахур"),
    ("uchtepa", "Uchtepa", "Учтепа"),
    ("chilonzor", "Chilonzor", "Чиланзар"),
    ("mirobod", "Mirobod", "Мирабад"),
    ("yashnobod", "Yashnobod", "Яшнабад"),
    ("sergeli", "Sergeli", "Сергелий"),
    ("yangihayot", "Yangihayot", "Янгиҳаёт"),
]
DISTRICT_MAP = {k: (uz, ru) for k, uz, ru in DISTRICTS}
