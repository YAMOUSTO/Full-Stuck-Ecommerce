# test_cloudinary.py
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

print("--- Starting Cloudinary Upload Test ---")
load_dotenv()

try:
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )
    print("Cloudinary configured successfully.")
    
    # Upload the test image
    print("Attempting to upload 'test_image.jpg'...")
    result = cloudinary.uploader.upload("test_image.jpg", folder="test_uploads")
    
    print("\n✅ ✅ ✅ SUCCESS! ✅ ✅ ✅")
    print("Image uploaded successfully.")
    print("You can find it in the 'test_uploads' folder in your Cloudinary Media Library.")
    print("URL:", result.get('secure_url'))

except Exception as e:
    print("\n❌ ❌ ❌ ERROR ❌ ❌ ❌")
    print("The upload failed. Here is the exact error from Cloudinary:")
    print(e)

print("\n--- Test Finished ---")