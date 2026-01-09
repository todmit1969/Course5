from rest_framework.exceptions import ValidationError


def habit_validation(attrs):
    errors = {}

    related_habit = attrs.get("related_habit")
    reward_text = attrs.get("reward_text")
    is_rewarding = attrs.get("is_rewarding")

    # 1. Нельзя одновременно указывать связанную привычку и награду
    if related_habit and reward_text:
        errors["related_habit"] = "Нельзя указать одновременно связанную привычку и награду."
        errors["reward_text"] = "Нельзя указать одновременно награду и связанную привычку."

    # 2. Необходимо указать либо связанную привычку, либо награду (если привычка не является приятной)
    if not is_rewarding and not related_habit and not reward_text:
        errors["reward_text"] = "Необходимо указать либо связанную привычку, либо награду."

    # 3. Связанная привычка должна быть приятной
    if related_habit and not getattr(related_habit, "is_rewarding", False):
        errors["related_habit"] = "Связанная привычка должна быть приятной (is_rewarding=True)."

    # 4. Для приятной привычки нельзя указывать награду и связанную привычку
    if is_rewarding and (reward_text or related_habit):
        errors["is_rewarding"] = "Для приятной привычки нельзя указывать награду или связанную привычку."

    if errors:
        raise ValidationError(errors)

    return attrs
