import json


def load_setting(key=None):
    """Load settings from the JSON file and return the value for the specified key."""
    settings = load_settings()
    if key:
        if key not in settings:
            if key == 'spinner':
                settings[key] = 'default'
                save_settings(settings)

            elif key == 'lang':
                settings[key] = 'ru'
                save_settings(settings)

        return settings.get(key)
    return settings


def load_settings():
    """Load settings from the JSON file."""
    try:
        with open('Src/data/settings.json', 'r') as file:
            settings = json.load(file)
            return settings
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {
            'send_to_group': False,
            'save_to_file': False,
            'apply_promo': False,
            'hamster_token': None,
            'account': 'HAMSTER_TOKEN_1',
            'spinner': 'default',
            'lang': 'ru'
         }
        save_settings(settings)
        return settings


def save_settings(settings):
    """Save settings to the JSON file."""
    with open('Src/data/settings.json', 'w') as file:
        json.dump(settings, file, indent=4)
