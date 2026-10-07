import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
from app.config import settings
from app.models.observation import Observation, ObservationCreate, IdentificationResult

SQLITE_DB_PATH = Path(__file__).parent.parent / "data" / "traillens_local.db"


class DatabaseService:
    def __init__(self):
        self._is_mongo: bool = False
        self._mongo_client = None
        self._mongo_db = None
        self._sqlite_path = SQLITE_DB_PATH
        self._init_sqlite()

    def _init_sqlite(self):
        """Ensure SQLite table exists for local offline operations."""
        self._sqlite_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self._sqlite_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                identification_json TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                user_notes TEXT,
                image_thumbnail TEXT,
                created_at TEXT NOT NULL,
                sync_status TEXT NOT NULL,
                client_id TEXT
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_obs_session ON observations(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_obs_created ON observations(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_obs_client_id ON observations(client_id)")
        conn.commit()
        conn.close()

    async def connect(self):
        """Attempt to connect to MongoDB Atlas if URI is provided."""
        if settings.MONGODB_URI:
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                self._mongo_client = AsyncIOMotorClient(
                    settings.MONGODB_URI,
                    serverSelectionTimeoutMS=2000
                )
                # Verify connection
                await self._mongo_client.admin.command('ping')
                self._mongo_db = self._mongo_client[settings.MONGODB_DB_NAME]
                self._is_mongo = True

                # Setup indexes
                await self._mongo_db.observations.create_index([("created_at", -1)])
                await self._mongo_db.observations.create_index([("session_id", 1)])
                await self._mongo_db.observations.create_index([("client_id", 1)], unique=False)
            except Exception:
                # Graceful fallback to SQLite
                self._is_mongo = False
                self._mongo_client = None
                self._mongo_db = None

    async def disconnect(self):
        if self._mongo_client:
            self._mongo_client.close()

    def get_status(self) -> Dict[str, Any]:
        return {
            "engine": "MongoDB Atlas" if self._is_mongo else "SQLite (Local Offline Storage)",
            "is_atlas": self._is_mongo,
            "database_name": settings.MONGODB_DB_NAME if self._is_mongo else "traillens_local.db",
            "sqlite_fallback_active": not self._is_mongo
        }

    async def insert_observation(self, obs_in: ObservationCreate) -> Observation:
        obs_id = str(uuid.uuid4())
        created_at = obs_in.offline_created_at or datetime.now(timezone.utc).isoformat()

        obs_dict = {
            "id": obs_id,
            "session_id": obs_in.session_id or "anon-explorer",
            "identification": obs_in.identification.model_dump(),
            "latitude": obs_in.latitude,
            "longitude": obs_in.longitude,
            "user_notes": obs_in.user_notes,
            "image_thumbnail": obs_in.image_thumbnail,
            "created_at": created_at,
            "sync_status": "synced",
            "client_id": obs_in.client_id
        }

        if self._is_mongo and self._mongo_db is not None:
            try:
                doc = obs_dict.copy()
                doc["_id"] = obs_id
                await self._mongo_db.observations.insert_one(doc)
            except Exception:
                # If Atlas write temporarily fails, write to SQLite
                self._sqlite_insert(obs_dict)
        else:
            self._sqlite_insert(obs_dict)

        return Observation(
            id=obs_id,
            session_id=obs_dict["session_id"],
            identification=obs_in.identification,
            latitude=obs_in.latitude,
            longitude=obs_in.longitude,
            user_notes=obs_in.user_notes,
            image_thumbnail=obs_in.image_thumbnail,
            created_at=created_at,
            sync_status="synced",
            client_id=obs_in.client_id
        )

    def _sqlite_insert(self, d: Dict[str, Any]):
        conn = sqlite3.connect(self._sqlite_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO observations
            (id, session_id, identification_json, latitude, longitude, user_notes, image_thumbnail, created_at, sync_status, client_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            d["id"],
            d["session_id"],
            json.dumps(d["identification"]),
            d.get("latitude"),
            d.get("longitude"),
            d.get("user_notes"),
            d.get("image_thumbnail"),
            d["created_at"],
            d["sync_status"],
            d.get("client_id")
        ))
        conn.commit()
        conn.close()

    async def get_observations(self, session_id: Optional[str] = None, limit: int = 50) -> List[Observation]:
        if self._is_mongo and self._mongo_db is not None:
            try:
                query = {"session_id": session_id} if session_id else {}
                cursor = self._mongo_db.observations.find(query).sort("created_at", -1).limit(limit)
                docs = await cursor.to_list(length=limit)
                return [
                    Observation(
                        id=d.get("id") or str(d.get("_id")),
                        session_id=d["session_id"],
                        identification=IdentificationResult(**d["identification"]),
                        latitude=d.get("latitude"),
                        longitude=d.get("longitude"),
                        user_notes=d.get("user_notes"),
                        image_thumbnail=d.get("image_thumbnail"),
                        created_at=d["created_at"],
                        sync_status=d.get("sync_status", "synced"),
                        client_id=d.get("client_id")
                    )
                    for d in docs
                ]
            except Exception:
                pass

        # SQLite query
        conn = sqlite3.connect(self._sqlite_path)
        cursor = conn.cursor()
        if session_id:
            cursor.execute("""
                SELECT id, session_id, identification_json, latitude, longitude, user_notes, image_thumbnail, created_at, sync_status, client_id
                FROM observations
                WHERE session_id = ?
                ORDER BY created_at DESC LIMIT ?
            """, (session_id, limit))
        else:
            cursor.execute("""
                SELECT id, session_id, identification_json, latitude, longitude, user_notes, image_thumbnail, created_at, sync_status, client_id
                FROM observations
                ORDER BY created_at DESC LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        items = []
        for r in rows:
            ident_data = json.loads(r[2])
            items.append(Observation(
                id=r[0],
                session_id=r[1],
                identification=IdentificationResult(**ident_data),
                latitude=r[3],
                longitude=r[4],
                user_notes=r[5],
                image_thumbnail=r[6],
                created_at=r[7],
                sync_status=r[8],
                client_id=r[9]
            ))
        return items

    async def delete_observation(self, obs_id: str) -> bool:
        if self._is_mongo and self._mongo_db is not None:
            try:
                res = await self._mongo_db.observations.delete_one({"id": obs_id})
                if res.deleted_count > 0:
                    return True
            except Exception:
                pass

        conn = sqlite3.connect(self._sqlite_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM observations WHERE id = ?", (obs_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    async def sync_batch(self, items: List[ObservationCreate]) -> List[Observation]:
        synced = []
        for item in items:
            obs = await self.insert_observation(item)
            synced.append(obs)
        return synced


db_service = DatabaseService()
