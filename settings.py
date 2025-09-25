INSTALLED_APPS = [
    # ...otros apps...
    'corsheaders',
    # ...otros apps...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ...otros middlewares...
]

CORS_ALLOW_ALL_ORIGINS = True  # Para desarrollo, permite todos los orígenes
# Para producción, usa:
# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "https://tu-frontend.com",
# ]