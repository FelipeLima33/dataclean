import io
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from app.core.config import settings

def _get_r2_client():
    if not settings.CLOUDFLARE_R2_ACCESS_KEY_ID or not settings.CLOUDFLARE_R2_ENDPOINT_URL:
        raise ValueError("Credenciais do R2 não configuradas no ambiente.")
    
    return boto3.client(
        's3',
        endpoint_url=settings.CLOUDFLARE_R2_ENDPOINT_URL,
        aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4'),
        region_name='auto'  # R2 is 'auto' or 'wnam' etc, auto works
    )

def upload_file(file_bytes: bytes, object_name: str, content_type: str = "application/octet-stream") -> str:
    """Faz upload de um arquivo em bytes para o R2 e retorna o caminho/chave"""
    s3 = _get_r2_client()
    try:
        s3.put_object(
            Bucket=settings.CLOUDFLARE_R2_BUCKET_NAME,
            Key=object_name,
            Body=file_bytes,
            ContentType=content_type
        )
        return object_name
    except ClientError as e:
        raise Exception(f"Erro ao fazer upload para o R2: {e}")

def download_file(object_name: str) -> bytes:
    """Baixa um arquivo do R2 retornando seus bytes"""
    s3 = _get_r2_client()
    try:
        response = s3.get_object(
            Bucket=settings.CLOUDFLARE_R2_BUCKET_NAME,
            Key=object_name
        )
        return response['Body'].read()
    except ClientError as e:
        raise Exception(f"Erro ao baixar arquivo do R2: {e}")

def delete_file(object_name: str) -> bool:
    """Deleta um arquivo do R2"""
    s3 = _get_r2_client()
    try:
        s3.delete_object(
            Bucket=settings.CLOUDFLARE_R2_BUCKET_NAME,
            Key=object_name
        )
        return True
    except ClientError as e:
        raise Exception(f"Erro ao deletar arquivo do R2: {e}")
