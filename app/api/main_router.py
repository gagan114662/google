from fastapi import APIRouter, Depends
from app.core import get_redis_client, get_db
from sqlalchemy.orm import Session
import redis

router = APIRouter()

@router.get("/health", tags=["System Health"])
async def health_check(
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """
    Checks the health of the database and Redis connections.
    """
    db_status = "ok"
    redis_status = "ok"
    try:
        # Test DB connection (simple query)
        db.execute("SELECT 1")
    except Exception as e:
        db_status = f"error: {e}"

    try:
        # Test Redis connection
        redis_client.ping()
    except Exception as e:
        redis_status = f"error: {e}"

    return {
        "status": "ok" if db_status == "ok" and redis_status == "ok" else "degraded",
        "database_status": db_status,
        "redis_status": redis_status,
    }
