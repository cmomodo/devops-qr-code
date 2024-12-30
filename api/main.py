from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import qrcode
import boto3
import os
from io import BytesIO
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Allowing CORS for local testing
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Add this
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]    # Add this
)

# Add error handling middleware
@app.middleware("http")
async def errors_handling(request: Request, call_next):
    try:
        logger.info(f"Processing request to {request.url}")
        return await call_next(request)
    except Exception as exc:
        logger.error(f"Error processing request: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error occurred. Please check logs for details."}
        )

# Configure S3 client
try:
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
        region_name='us-east-1'  # specify your region
    )
    logger.info("Successfully configured S3 client")
except Exception as e:
    logger.error(f"Failed to configure S3 client: {str(e)}")
    raise

class URLRequest(BaseModel):
    url: str

@app.post("/generate-qr/")
async def generate_qr(request: URLRequest):
    try:
        url = request.url
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        # Upload to S3
        file_name = f"qr-{url.replace('/', '-')}.png"
        bucket_name = 'capstone-27-bucket'
        
        try:
            s3.upload_fileobj(
                img_byte_arr,
                bucket_name,
                file_name,
                ExtraArgs={'ContentType': 'image/png'}
            )
            logger.info(f"Successfully uploaded QR code for {url} to S3")
            
            # Generate S3 URL
            s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
            return {"qr_code_url": s3_url}
            
        except Exception as s3_error:
            logger.error(f"S3 upload error: {str(s3_error)}")
            raise HTTPException(status_code=500, detail="Failed to upload to S3")
            
    except Exception as e:
        logger.error(f"QR generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate QR code")
