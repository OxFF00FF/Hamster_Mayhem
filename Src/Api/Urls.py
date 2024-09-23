from pydantic import AnyUrl


class HamsterUrls:
    # var: AnyUrl = f"{base_url}/{season}/endpint")
    main_url = "https://hamsterkombatgame.io"

    season = 'interlude'
    base_url: AnyUrl = "https://api.hamsterkombatgame.io"
    datavibe_base_url = "https://api21.datavibe.top/api"


    # Auth
    auth_by_telegram: AnyUrl = f"{base_url}/{season}/auth/auth-by-telegram-webapp"
    account_info: AnyUrl = f"{base_url}/auth/account-info"
    ip: AnyUrl = f"{base_url}/ip"

    # Config
    season_config: AnyUrl = f"{base_url}/{season}/config/s9HTT3LyuDriwRxy00L_BJqxgX8ajeCHzZ3Zlh3Cmc4"
    config: AnyUrl = f"{base_url}/{season}/config"
    nuxt: AnyUrl = f"{base_url}/{season}/_nuxt/builds/meta/fe021024-d4a8-4ad9-ab6f-3ce2a6e9db47.json"

    # Clicker
    sync: AnyUrl = f"{base_url}/{season}/sync"
    get_skin: AnyUrl = f"{base_url}/{season}/get-skin"
    select_exchange: AnyUrl = f"{base_url}/{season}/select-exchange"

    # Taps
    tap: AnyUrl = f"{base_url}/{season}/tap"

    # Boosts
    boosts_for_buy: AnyUrl = f"{base_url}/{season}/boosts-for-buy"
    buy_boost: AnyUrl = f"{base_url}/{season}/buy-boost"

    # Tasks
    list_tasks: AnyUrl = f"{base_url}/{season}/list-tasks"
    list_airdrop_tasks: AnyUrl = f"{base_url}/{season}/list-airdrop-tasks"
    check_task: AnyUrl = f"{base_url}/{season}/check-task"

    # Upgrades
    upgrades_for_buy: AnyUrl = f"{base_url}/{season}/upgrades-for-buy"
    buy_upgrade: AnyUrl = f"{base_url}/{season}/buy-upgrade"

    # Cipher
    claim_daily_cipher: AnyUrl = f"{base_url}/{season}/claim-daily-cipher"

    # Combo
    get_combo: AnyUrl = f"{datavibe_base_url}/GetCombo"
    claim_daily_combo: AnyUrl = f"{base_url}/{season}/claim-daily-combo"

    # Minigames
    start_keys_minigame: AnyUrl = f"{base_url}/{season}/start-keys-minigame"
    claim_daily_keys_minigame: AnyUrl = f"{base_url}/{season}/claim-daily-keys-minigame"

    # Promos
    get_games: AnyUrl = f"{datavibe_base_url}/Games"
    get_promos: AnyUrl = f"{base_url}/{season}/get-promos"
    apply_promo: AnyUrl = f"{base_url}/{season}/apply-promo"

    # Wallet
    withdraw_list: AnyUrl = f"{base_url}/{season}/withdraw/list"
    set_wallet_as_default: AnyUrl = f"{base_url}/{season}/set-wallet-as-default"
