import os

class Config:
    # ✅ Use DATABASE_URL from environment variables, ensure SSL is handled correctly
    # SQLALCHEMY_DATABASE_URI = os.getenv(
    #    "DATABASE_URL",
    #    "postgresql://astrology_user_data_user:uYfa51BtqNNH7GqCPHjcNvz7p4ddj1VR@dpg-cujjbhjv2p9s73821o40-a/astrology_user_data"
    #   ).replace("postgres://", "postgresql://")  # Fix for Render using outdated "postgres://" format
    SQLALCHEMY_DATABASE_URI = "postgresql://astrology_user_data_user:uYfa51BtqNNH7GqCPHjcNvz7p4ddj1VR@dpg-cujjbhjv2p9s73821o40-a.frankfurt-postgres.render.com/astrology_user_data"
    # ✅ Prevent unnecessary modifications tracking
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ Secret keys (Ensure they are set securely!)
    SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    # ✅ Extra Security - Require SSL (if running on production)
    if os.getenv("FLASK_ENV") == "production":
        SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "sslmode": "require"}