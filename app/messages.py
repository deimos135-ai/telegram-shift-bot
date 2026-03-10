from __future__ import annotations


def _format_list(items: list[str]) -> str:
    if not items:
        return "• —"
    return "\n".join(f"• {item}" for item in items)


def build_schedule_message(data: dict | None, title: str = "Графік на сьогодні") -> str:
    if not data:
        return "⚠️ Не вдалося знайти дані в таблиці."

    first_shift = _format_list(data.get("first_shift", []))
    second_shift = _format_list(data.get("second_shift", []))
    admins_working = _format_list(data.get("admins_working", []))

    duty_admin = data.get("duty_admin")
    duty_admin_text = f"• {duty_admin}" if duty_admin else "• —"

    return (
        f"📅 {title} ({data['date']})\n\n"
        f"1️⃣ Перша зміна:\n{first_shift}\n\n"
        f"2️⃣ Друга зміна:\n{second_shift}\n\n"
        f"🧑‍💼 Адміністратори на роботі:\n{admins_working}\n\n"
        f"🚨 Черговий адміністратор:\n{duty_admin_text}"
    )
