class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # Ensure this points to your active database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security Settings
    SECRET_KEY = 'myprojectsecretkey'  # Keep this static and secure
    SESSION_COOKIE_NAME = 'my_app_session'  # Name of the session cookie
    SESSION_COOKIE_SECURE = False  # Set to True if running on HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Protect against JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # Prevent CSRF on cross-site requests

    # Session Lifetime (1 hour)
    PERMANENT_SESSION_LIFETIME = 3600  # Lifetime in seconds
