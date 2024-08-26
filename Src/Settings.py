import json


def load_settings():
    """Load settings from the JSON file."""
    try:
        with open('Src/data/settings.json', 'r') as file:
            settings = json.load(file)
            return settings
    except (FileNotFoundError, json.JSONDecodeError):
        print("Настройки не найдены. Создан файл с настройками по умолчанию")
        settings = {'send_to_group': False, 'save_to_file': False, 'apply_promo': False, 'hamster_token': None, 'account': 'HAMSTER_TOKEN_1'}
        save_settings(settings)
        return settings


def save_settings(settings):
    """Save settings to the JSON file."""
    with open('Src/data/settings.json', 'w') as file:
        json.dump(settings, file, indent=4)
