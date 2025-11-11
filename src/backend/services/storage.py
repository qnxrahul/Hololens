from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import boto3
from botocore.client import Config as BotoConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ObjectStorageSettings:
    endpoint_url: Optional[str]
    access_key: str
    secret_key: str
    bucket_name: str
    region_name: Optional[str] = None
    signature_version: str = "s3v4"
    use_ssl: bool = True


class ObjectStorageClient:
    """Wrapper around S3-compatible storage such as MinIO or Ceph."""

    def __init__(self, settings: ObjectStorageSettings) -> None:
        session = boto3.session.Session()
        self._bucket = settings.bucket_name
        self._client = session.client(
            "s3",
            aws_access_key_id=settings.access_key,
            aws_secret_access_key=settings.secret_key,
            endpoint_url=settings.endpoint_url,
            region_name=settings.region_name,
            use_ssl=settings.use_ssl,
            config=BotoConfig(signature_version=settings.signature_version),
        )

    def ensure_bucket(self) -> None:
        """Create the bucket if it does not exist."""
        existing = self._client.list_buckets()
        if any(bucket["Name"] == self._bucket for bucket in existing.get("Buckets", [])):
            return
        self._client.create_bucket(Bucket=self._bucket)
        logger.info("Created object storage bucket %s", self._bucket)

    def upload_file(self, key: str, data: bytes, *, content_type: str = "application/octet-stream") -> None:
        self._client.put_object(Bucket=self._bucket, Key=key, Body=data, ContentType=content_type)
        logger.debug("Uploaded object %s to bucket %s", key, self._bucket)

    def generate_presigned_url(self, key: str, *, expires_in: int = 3600) -> str:
        url = self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        logger.debug("Generated presigned URL for %s", key)
        return url

