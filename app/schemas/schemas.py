def event_serial(event) -> dict:
    return {
        "id":               str(event["_id"]),
        "title":            event["title"],
        "description":      event["description"],
        "location":         event["location"],
        "date":             event["date"],
        "max_participants": event["max_participants"],
    }


def registration_serial(reg) -> dict:
    return {
        "id":            str(reg["_id"]),
        "event_id":      reg["event_id"],
        "user_name":     reg["user_name"],
        "email":         reg["email"],
        "registered_at": reg["registered_at"],
    }


def user_serial(user) -> dict:
    return {
        "id":    str(user["_id"]),
        "name":  user["name"],
        "email": user["email"],
        "role":  user.get("role", "user"),
    }
