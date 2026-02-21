import os
import requests
import json
import re

# Path to the Bible Study JS file
JS_FILE_PATH = r"c:\Users\Georg\Projects\blackshepherddeveloper-project\public\js\biblestudy.js"

def find_placeholders_in_js(file_path):
    """
    Parses the JS file to find placeholder image markers or terms that need images.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all alt texts or names for images that are currently placeholders
    # Looking for: alt="...Illustration" or description: "..." in sections with [Placeholder]
    placeholders = []
    
    # Find alt text patterns like alt="Sabbath Rest Illustration"
    alt_matches = re.findall(r'alt="([^"]*Illustration)"', content)
    placeholders.extend(alt_matches)
    
    # Find descriptions in artifacts that mention placeholders
    artifact_matches = re.findall(r'description: "([^"]*)"', content)
    for match in artifact_matches:
        if "Tablet" in match or "Scroll" in match or "Manuscript" in match:
            placeholders.append(match)
            
    return list(set(placeholders))


def search_wikipedia_image(query):
    """
    Searches Wikipedia for an image related to the query.
    Returns a URL or None.
    """
    print(f"Searching for: {query}...")
    headers = {
        'User-Agent': 'BibleStudyPhotoBot/1.0 (contact: support@blacksheep.com)'
    }
    
    # 1. Search for the page title
    search_url = "https://en.wikipedia.org/w/api.php"
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json"
    }
    
    try:
        response = requests.get(search_url, params=search_params, headers=headers)
        if response.status_code != 200:
            print(f"  [ERROR] Search Request failed with status: {response.status_code}")
            return None
        
        search_data = response.json()
        
        if not search_data.get("query", {}).get("search"):
            return None
            
        page_title = search_data["query"]["search"][0]["title"]
        
        # 2. Get images for that page
        image_params = {
            "action": "query",
            "titles": page_title,
            "prop": "pageimages|images",
            "pithumbsize": 500,
            "format": "json"
        }
        
        img_response = requests.get(search_url, params=image_params, headers=headers)
        img_data = img_response.json()
        
        pages = img_data.get("query", {}).get("pages", {})
        for page_id in pages:
            page = pages[page_id]
            # Try to get thumbnail first
            if "thumbnail" in page:
                return page["thumbnail"]["source"]
            
            # If no thumbnail, look at the first image file
            if "images" in page:
                for img_info in page["images"]:
                    img_title = img_info["title"]
                    if img_title.lower().endswith(('.jpg', '.jpeg', '.png')):
                        # Get URL for the image file
                        file_params = {
                            "action": "query",
                            "titles": img_title,
                            "prop": "imageinfo",
                            "iiprop": "url",
                            "format": "json"
                        }
                        file_resp = requests.get(search_url, params=file_params, headers=headers)
                        file_data = file_resp.json()
                        file_pages = file_data.get("query", {}).get("pages", {})
                        for f_id in file_pages:
                            if "imageinfo" in file_pages[f_id]:
                                return file_pages[f_id]["imageinfo"][0]["url"]
                                
    except Exception as e:
        print(f"Error searching for {query}: {e}")
        
    return None

def main():
    if not os.path.exists(JS_FILE_PATH):
        print(f"Error: {JS_FILE_PATH} not found.")
        return

    print("Step 1: Finding placeholders in biblestudy.js...")
    placeholders = find_placeholders_in_js(JS_FILE_PATH)
    print(f"Found {len(placeholders)} unique photo terms needing real images.")

    results = {}
    for term in placeholders:
        img_url = search_wikipedia_image(term)
        if img_url:
            results[term] = img_url
            print(f"  [FOUND] {term} -> {img_url}")
        else:
            print(f"  [NOT FOUND] {term}")

    # Output a mapping that can be used to update the JS file
    if results:
        print("\nStep 2: Analysis complete. Found the following mappings:")
        print(json.dumps(results, indent=2))
        
        # Save mapping to a file for review
        with open("bible_photo_mapping.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\nMapping saved to bible_photo_mapping.json")
        print("You can now use this mapping to update the placeholders in biblestudy.js.")
    else:
        print("\nNo images were found automatically. Consider broadening the search terms.")

if __name__ == "__main__":
    main()
