from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import boto3
from botocore.client import BaseClient

from app.core.config import settings


@dataclass
class StoredObject:
    key: str
    size: int


class StorageBackend:
    def save_bytes(self, key: str, payload: bytes) -> StoredObject:
        raise NotImplementedError

    def read_bytes(self, key: str) -> bytes:
        raise NotImplementedError


class LocalStorageBackend(StorageBackend):
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save_bytes(self, key: str, payload: bytes) -> StoredObject:
        target = self.root / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        return StoredObject(key=key, size=len(payload))

    def read_bytes(self, key: str) -> bytes:
        return (self.root / key).read_bytes()


class S3StorageBackend(StorageBackend):
    def __init__(self) -> None:
        self.client: BaseClient = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            region_name=settings.s3_region,
        )
        self.bucket = settings.s3_bucket

    def save_bytes(self, key: str, payload: bytes) -> StoredObject:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=payload)
        return StoredObject(key=key, size=len(payload))

    def read_bytes(self, key: str) -> bytes:
        obj = self.client.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read()


_storage: StorageBackend | None = None


def get_storage() -> StorageBackend:
    global _storage
    if _storage is not None:
        return _storage

    if settings.storage_backend.lower() == "s3":
        _storage = S3StorageBackend()
    else:
        _storage = LocalStorageBackend(settings.resolved_storage_path)
    return _storage
