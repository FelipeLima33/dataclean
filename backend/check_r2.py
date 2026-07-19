import os
from app.services.storage.r2_client import _get_r2_client
from app.core.config import settings

s3 = _get_r2_client()
response = s3.list_objects_v2(Bucket=settings.CLOUDFLARE_R2_BUCKET_NAME)

print("Arquivos no Bucket R2:")
if 'Contents' in response:
    for obj in response['Contents']:
        print(f"- {obj['Key']} ({obj['Size']} bytes)")
else:
    print("Bucket vazio.")
