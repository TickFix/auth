import boto3
import json
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Inicializa cliente de AWS Secrets Manager
secrets_client = boto3.client("secretsmanager", region_name="us-east-1")

def get_db_secret(secret_name: str):
    secret_value = secrets_client.get_secret_value(SecretId=secret_name)
    return json.loads(secret_value["SecretString"])

# Obtener secreto de auth
auth_secret = get_db_secret("tiqfix/auth_db_secret")

# Construir URL de conexión
DATABASE_URL = f"mysql+aiomysql://{auth_secret['username']}:{auth_secret['password']}@{auth_secret['host']}:{auth_secret['port']}/{auth_secret['dbname']}"

# Engine y sesión
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSession = async_sessionmaker(engine, expire_on_commit=False)

# Base para modelos
Base = declarative_base()

async def init_db():
    from app import models  # importa modelos de auth
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
