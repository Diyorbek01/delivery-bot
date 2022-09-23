from environs import Env

# environs kutubxonasidan foydalanish
env = Env()
env.read_env()

# .env fayl ichidan quyidagilarni o'qiymiz
BOT_TOKEN = env.str("BOT_TOKEN")  # Bot toekn
ADMINS = env.list("ADMINS")  # adminlar ro'yxati
BASE_URL = env.str("BASE_URL")  # site domeni
MY_TOKEN = env.str("MY_TOKEN")  # site domeni
IP = env.str("ip")  # Xosting ip manzili
