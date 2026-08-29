"""
One-time helper to get a TikTok user access token via OAuth.

You only run this manually, once (well, once every time your refresh token
expires — TikTok refresh tokens last 365 days). It is NOT part of the
scheduled GitHub Actions pipeline.

STEP A — Get an authorization code (do this in your browser, not this script):

  1. Build this URL, filling in your own CLIENT_KEY and REDIRECT_URI:

     https://www.tiktok.com/v2/auth/authorize/
       ?client_key=YOUR_CLIENT_KEY
       &scope=user.info.basic,video.upload
       &response_type=code
       &redirect_uri=YOUR_REDIRECT_URI
       &state=xyz123

     (Remove the line breaks — it must be a single-line URL.)

  2. Open that URL in a browser where you're logged into the TARGET
     TikTok account (@driftloopmusic), approve access.

  3. TikTok redirects you to your callback.html page with a `code=...`
     parameter in the URL — that page displays it for you to copy.

STEP B — Exchange that code for a token (this script does that part):

  Fill in CLIENT_KEY, CLIENT_SECRET, REDIRECT_URI, and AUTH_CODE below,
  then run: python scripts/get_tiktok_token.py
"""

import requests

CLIENT_KEY = "PASTE_YOUR_CLIENT_KEY_HERE"
CLIENT_SECRET = "PASTE_YOUR_CLIENT_SECRET_HERE"
REDIRECT_URI = "https://saidfy-commits.github.io/gg/callback.html"
AUTH_CODE = "PASTE_THE_CODE_FROM_callback.html_HERE"

TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"


def main():
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache",
    }
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": AUTH_CODE,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
    }
    resp = requests.post(TOKEN_URL, headers=headers, data=data, timeout=30)
    print("Status:", resp.status_code)
    print(resp.json())
    print()
    print("If this worked, copy the 'access_token' value above into your")
    print("GitHub repo secret named TIKTOK_ACCESS_TOKEN.")
    print("Also save 'refresh_token' somewhere safe — you'll need it once")
    print("access_token expires (every 24h) to get a new one without")
    print("repeating the browser login step.")


if __name__ == "__main__":
    main()
