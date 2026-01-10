"""Quick script to trigger Gmail OAuth flow."""

from src.services.gmail import GmailService

def main():
    print("Starting Gmail OAuth flow...")
    print("A browser window should open for authentication.")
    print()
    
    gmail = GmailService(
        credentials_path="credentials.json",
        token_path="token.json",
    )
    
    # This will trigger the OAuth flow
    try:
        gmail._authenticate()
        print("✅ Authentication successful!")
        print("token.json has been created.")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")

if __name__ == "__main__":
    main()
