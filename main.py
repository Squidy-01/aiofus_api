from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr, Field, field_validator
from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
print("DATABASE_URL utilisée :", DATABASE_URL)
if not DATABASE_URL:
    raise ValueError("DATABASE_URL non défini")
engine = create_engine(DATABASE_URL)
try:
    with engine.connect() as conn:
        conn.execute("SELECT 1")
        print("Connexion à la base PostgreSQL OK")
except Exception as e:
    print("Erreur de connexion à la base :", e)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(String(50), primary_key=True)
    username = Column(String(12), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    is_premium = Column(Boolean, default=False)

Base.metadata.create_all(engine)
print("Tables créées (ou déjà existantes)")

app = FastAPI(title="AIofus API")

class RegisterRequest(BaseModel):
    username: str = Field(..., strip_whitespace=True, min_length=1, max_length=12)
    password: str = Field(..., min_length=8, max_length=30)

    @field_validator('password')
    def password_strength(cls, v):
        if not any(c.isdigit() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre.')
        if not any(c.isupper() for c in v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule.')
        return v

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/register")
def register(data: RegisterRequest):
    with Session() as session:
        if session.query(User).filter_by(username=data.username).first():
            raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé.")
        hashed_pw = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(id=os.urandom(8).hex(), username=data.username, password_hash=hashed_pw)
        session.add(new_user)
        session.commit()
        return {"message": "Compte créé avec succès !"}

@app.post("/login")
def login(data: LoginRequest):
    with Session() as session:
        user = session.query(User).filter_by(username=data.username).first()
        if user and bcrypt.checkpw(data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return {"message": "Connexion réussie !", "user_id": user.id, "is_premium": user.is_premium}
        raise HTTPException(status_code=401, detail="Identifiants incorrects.")
