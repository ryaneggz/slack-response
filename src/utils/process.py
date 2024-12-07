import requests
import base64
import os

def process_images(event, BASE64_ENCODE=True):
    try:
        # Extract images from the event
        images = []
        if "files" in event:
            for file in event["files"]:
                if file["mimetype"].startswith("image/"):
                    # Get the file URL - prefer private URL if available
                    image_url = file.get("url_private_download")
                    if image_url:
                        if BASE64_ENCODE:
                            # Add authorization header for private files
                            headers = {"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"}
                            # Download the image with proper headers
                            response = requests.get(image_url, headers=headers)
                            if response.status_code == 200:
                                image_base64 = base64.b64encode(response.content).decode('utf-8')
                                images.append(f"data:{file['mimetype']};base64,{image_base64}")
                        else:
                            images.append(image_url)
        return images
    except Exception as e:
        print(f"Error processing images: {e}")
        return []
