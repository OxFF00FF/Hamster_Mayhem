from dotenv import load_dotenv

from Src.Login import hamster_client
load_dotenv()

# cooldowns = hamster_client().get_cooldowns()

hamster_client().login()
hamster_client().send_balance_to_group(chat_id=-1002155132619)
