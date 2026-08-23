import urllib.parse
import webbrowser
import sys
from config import Config

def main():
    client_id = Config.TWITCH_CLIENT_ID
    if not client_id or client_id == "your_client_id_here":
        print("ERROR: Please set your TWITCH_CLIENT_ID in the .env file first!")
        sys.exit(1)
        
    redirect_uri = Config.TWITCH_REDIRECT_URI # Ensure this matches what you registered in Twitch Dev Console
    scopes = "chat:read chat:edit"
    
    # URL encode the scopes and redirect URI
    encoded_scopes = urllib.parse.quote(scopes)
    encoded_redirect = urllib.parse.quote(redirect_uri)
    
    # Twitch OAuth implicit grant URL
    auth_url = (
        f"https://id.twitch.tv/oauth2/authorize"
        f"?response_type=token"
        f"&client_id={client_id}"
        f"&redirect_uri={encoded_redirect}"
        f"&scope={encoded_scopes}"
    )
    
    print("=" * 60)
    print("TWITCH OAUTH IMPLICIT GRANT HELPER")
    print("=" * 60)
    print("Opening your browser to authorize your Twitch bot...")
    print(f"\nIf it doesn't open automatically, copy and paste this URL into your browser:\n{auth_url}\n")
    print("=" * 60)
    
    try:
        webbrowser.open(auth_url)
    except Exception as e:
        print(f"Could not open browser: {e}")
        
    print("\nINSTRUCTIONS AFTER AUTHORIZING:")
    print("1. Click 'Authorize' in your browser.")
    print("2. You will be redirected to a blank page or error page at http://localhost.")
    print("3. Look at your browser's address bar. It will look like:")
    print("   http://localhost/#access_token=abcdefg123456...&scope=chat%3Aread...")
    print("4. Copy the long string after 'access_token=' and before the next '&' symbol.")
    print("5. Paste this token as your TWITCH_OAUTH_TOKEN in the .env file.")
    print("=" * 60)

if __name__ == "__main__":
    main()
