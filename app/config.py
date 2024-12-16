import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "7bb385b68e3376292c30fc63dcf74db4edebb14058a2412fead873b0fa363236")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "77f1a4bea606e3aff2afa7fb34654849d5018cb5178cd33b77d6e99fd509cdf8")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://tusharyadav:admin1234@unified-identity-nexus.g0eka.mongodb.net/?retryWrites=true&w=majority&appName=unified-identity-nexus")