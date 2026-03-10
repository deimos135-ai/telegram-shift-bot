def _format_list(items: list[str]) -> str:
    if not items:
        return "• —"

    return "\n".join(f"• {name}" for name in items)


def build_schedule_message(data: dict | None, title: str):
    if not data:
        return "⚠️ Не вдалося знайти дані в таблиці."

    first = _format_list(data["first_shift"])
    second = _format_list(data["second_shift"])
    admins = _format_list(data["admins_working"])

    duty = data["duty_admin"]
    duty_text = f"• {duty}" if duty else "• —"

    return (
        f"📅 {title} ({data['date']})\n\n"
        f"1️⃣ Перша зміна:\n{first}\n\n"
        f"2️⃣ Друга зміна:\n{second}\n\n"
        f"🧑‍💼 Адміністратори на роботі:\n{admins}\n\n"
        f"🚨 Черговий адміністратор:\n{duty_text}"
    )
