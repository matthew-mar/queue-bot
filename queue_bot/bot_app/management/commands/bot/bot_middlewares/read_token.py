def read_token() -> str:
    """ функция считывает токен из файла """
    bot_dir: str = "/".join(__file__.split("/")[:-1])
    with open(f"{bot_dir}/token.txt") as token_file:
        token: str = token_file.read()
    return token
