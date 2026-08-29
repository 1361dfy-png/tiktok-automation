# TikTok Auto-Publisher (Free, GitHub Actions)

Generates one image + one instrumental track, turns the image into a slowly
zooming loop video, muxes it with the music, and posts it to TikTok — twice a
day, on a schedule, for free on GitHub-hosted runners.

## How it fits together

1. `scripts/generate_image.py` — Hugging Face free Inference API → `output/image.png`
2. `scripts/generate_music.py` — Hugging Face free Inference API → `output/music.mp3`
3. `scripts/make_loop.py` — ffmpeg zoompan (CPU only, no AI) → `output/loop.mp4`
4. `scripts/combine.py` — ffmpeg loops the video to match the music length → `output/final.mp4`
5. `scripts/upload_tiktok.py` — TikTok Content Posting API → publishes `final.mp4`

`.github/workflows/generate.yml` runs all five steps twice a day via `cron`,
and can also be triggered manually from the **Actions** tab
(`workflow_dispatch`).

## One-time setup

1. **Make the repo public** — GitHub Actions minutes are effectively
   unlimited on public repos. Private repos get 2,000 free minutes/month,
   which is still enough for 2 short videos/day, but public is simpler.

2. **Hugging Face token**
   - Create one at https://huggingface.co/settings/tokens
   - Repo → Settings → Secrets and variables → Actions → New repository secret
   - Name: `HF_TOKEN`

3. **TikTok developer app**
   - Register an app at https://developers.tiktok.com/
   - Add the "Content Posting API" product and get it approved for the
     `video.publish` scope (this review step is TikTok's, not something
     code can skip)
   - Complete the OAuth flow once to get a user access token
   - Add it as the `TIKTOK_ACCESS_TOKEN` secret

4. **Test locally first**
   ```bash
   pip install -r requirements.txt
   export HF_TOKEN=your_token
   python scripts/generate_image.py
   python scripts/generate_music.py
   python scripts/make_loop.py
   python scripts/combine.py
   # inspect output/final.mp4 before wiring up the TikTok upload
   ```

5. **Test the workflow manually** — push this repo to GitHub, then run it
   once from the Actions tab (`workflow_dispatch`) before trusting the cron
   schedule. Check how long each step actually takes on GitHub's CPU-only
   runners; if generation is too slow, swap in a lighter model.

## Things worth knowing

- **Licensing**: `facebook/musicgen-small` (the default music model) is
  CC BY-NC 4.0 — non-commercial only. If you plan to monetize the channel,
  switch to a commercially-licensed model (Apache 2.0 options like ACE-Step
  or Stable Audio Open) once you've confirmed it's servable on the free
  Inference API.
- **Free tier limits**: Hugging Face's free Inference API is rate-limited
  and model availability shifts over time — check the model page for
  current serverless-inference status before depending on it.
- **AI-content disclosure**: TikTok requires labeling AI-generated content.
  `upload_tiktok.py` sets an `is_aigc` flag as a starting point — verify the
  exact current field name against TikTok's docs before relying on it.
- **Privacy level**: the script defaults to `SELF_ONLY` so you can check
  output quality before making posts public. Switch to
  `PUBLIC_TO_EVERYONE` once you trust the pipeline.
