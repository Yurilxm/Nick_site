import secrets


def login_code():
    # secrets.randbelow é criptograficamente seguro (usa o CSPRNG do SO),
    # ao contrário de random.randint, que não é adequado para fins de segurança.
    return f"{secrets.randbelow(900000) + 100000}"