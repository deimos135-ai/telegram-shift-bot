def build_shift_message(data):

    if not data:
        return "⚠️ Дані про зміну на сьогодні відсутні"

    operators = data["operators"]
    admin = data["admin"]
    comment = data.get("comment", "")

    text = f"""
📅 Зміна на {data["date"]}

👨‍💻 Оператори
{operators}

🛡 Черговий адмін
{admin}
"""

    if comment:
        text += f"\nℹ️ {comment}"

    return text
