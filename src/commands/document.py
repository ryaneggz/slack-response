from src.utils.logger import logger
from src.config import *
import requests

#####################################################################
## Document command handler
#####################################################################
def handle_documents(event, say):
    from src.commands import event_data
    channel_id, _, text = event_data(event)
    
    handled = False
    
    # Add document command
    if "$add_doc" in text.lower():
        # Split on first occurrence of $add_doc to get the rest of the message
        doc_text = text.split("$add_doc", 1)[1].strip()
        if doc_text:
            # Create document payload
            payload = {
                "documents": [{
                    "page_content": doc_text,
                    "metadata": {
                        "source": f"slack_channel_{channel_id}",
                        "title": f"Document from Slack {channel_id}"
                    }
                }]
            }
            
            response = requests.post(
                f"{BASE_API_URL}/documents", 
                json=payload, 
                headers=HEADERS, 
                auth=(APP_USERNAME, APP_PASSWORD)
            )
            
            if response.status_code == 200:
                doc_ids = response.json().get("documents", [])
                if doc_ids:
                    say(f"Document added successfully! ID: {doc_ids[0]}")
                else:
                    say("Document was added but no ID was returned")
            else:
                say(f"Error adding document: {response.status_code}")
        else:
            say("Please provide text for the document. Example: $add_doc This is the document content")
        handled = True
    
    # List documents command
    if "$list_docs" in text.lower():
        response = requests.get(f"{BASE_API_URL}/documents", headers=HEADERS, auth=(APP_USERNAME, APP_PASSWORD))
        if response.status_code == 200:
            docs = response.json().get("documents", [])
            if docs:
                # Format document information
                doc_list = []
                for doc in docs:
                    title = doc.get("metadata", {}).get("title", "Untitled")
                    doc_id = doc.get("id", "No ID")
                    doc_list.append(f"• {title} (ID: {doc_id})")
                
                formatted_docs = "\n".join(doc_list)
                say(f"Available documents:\n{formatted_docs}")
            else:
                say("No documents found in the system.")
        else:
            say(f"Error fetching documents: {response.status_code}")
        handled = True
    
    # Get specific document command
    if "$get_doc" in text.lower():
        doc_id = text.split("$get_doc", 1)[1].strip()
        if doc_id:
            response = requests.get(f"{BASE_API_URL}/documents/{doc_id}", headers=HEADERS, auth=(APP_USERNAME, APP_PASSWORD))
            if response.status_code == 200:
                doc = response.json().get("document", {})
                metadata = doc.get("metadata", {})
                metadata_str = "\n".join([f"*{key}:* {value}" for key, value in metadata.items()])
                text = doc.get("page_content", "No content")
                say(f"{metadata_str}\n\n{text}")
            else:
                say(f"Error fetching document: {response.status_code}")
        else:
            say("Please provide a document ID. Example: $get_doc abc123")
        handled = True
    
    # Delete document command
    if "$delete_doc" in text.lower():
        doc_ids = [id.strip() for id in text.split("$delete_doc", 1)[1].strip().split(',')]
        if doc_ids:
            payload = {"documents": doc_ids}
            response = requests.delete(f"{BASE_API_URL}/documents", json=payload, headers=HEADERS, auth=(APP_USERNAME, APP_PASSWORD))
            if response.status_code in [200, 204]:
                say(f"Successfully deleted {len(doc_ids)} document(s)")
            else:
                say(f"Error deleting documents: {response.status_code}")
        else:
            say("Please provide document ID(s). Example: $delete_doc abc123,def456")
        handled = True
    
    return handled 