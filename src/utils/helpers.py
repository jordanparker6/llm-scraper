def file_safe_string(string: str):
    safe_title = string.replace(" ", "_").replace('"', "").replace(r'\\"', "-").replace("/", "-")
    if len(safe_title) > 150:
        safe_title = safe_title[:150]
    return