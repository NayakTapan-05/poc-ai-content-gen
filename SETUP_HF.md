# Hugging Face Setup Guide

This guide will help you set up Hugging Face authentication for the AI Content Generator POC.

## Prerequisites

- A Hugging Face account (free)
- Python 3.10+ installed
- Poetry installed

## Step 1: Create a Hugging Face Account

If you don't already have one:

1. Go to https://huggingface.co/join
2. Sign up with your email or GitHub account
3. Verify your email address

## Step 2: Create an Access Token

1. **Log in to Hugging Face**: Go to https://huggingface.co and log in

2. **Navigate to Settings**: Click on your profile picture (top right) → **Settings**

3. **Access Tokens**: In the left sidebar, click on **Access Tokens**

4. **Create New Token**:
   - Click the **"New token"** button
   - **Name**: Give it a descriptive name (e.g., "AI Content Generator POC")
   - **Role**: Select **"Read"** (sufficient for inference)
   - Click **"Generate token"**

5. **Copy the Token**: 
   - **IMPORTANT**: Copy the token immediately and save it securely
   - You won't be able to see it again after closing the page
   - The token looks like: `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

## Step 3: Configure the Application

### Option A: Using .env File (Recommended)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Open `.env` in your text editor:
   ```bash
   nano .env
   # or
   vim .env
   # or use any text editor
   ```

4. Paste your token:
   ```env
   HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

5. Save and close the file

### Option B: Using Environment Variable

You can also set the token as an environment variable:

```bash
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent.

## Step 4: (Optional) Set Up Inference Endpoints for Video

For faster video generation, you can deploy Inference Endpoints on Hugging Face:

1. **Go to Inference Endpoints**: https://huggingface.co/inference-endpoints

2. **Create New Endpoint**:
   - Click **"Create new endpoint"**
   - **Model**: Select `stabilityai/stable-video-diffusion-img2vid`
   - **Region**: Choose closest to you
   - **Instance Type**: GPU (minimum: 1x NVIDIA T4)
   - **Name**: `svd-img2vid-endpoint`

3. **Deploy**: Click **"Create Endpoint"** and wait for deployment (~5 minutes)

4. **Copy Endpoint URL**: Once deployed, copy the endpoint URL

5. **Add to .env**:
   ```env
   HF_SVD_IMG2VID_ENDPOINT=https://xxxxx.endpoints.huggingface.cloud
   ```

6. **Repeat for SVD-XT** (optional):
   - Model: `stabilityai/stable-video-diffusion-img2vid-xt`
   - Add to .env as `HF_SVD_XT_ENDPOINT`

**Note**: Inference Endpoints are paid services. The free Inference API works for images but video generation requires endpoints or local fallback.

## Step 5: Verify Setup

1. **Start the backend**:
   ```bash
   cd backend
   poetry install
   poetry run python -m fastapi dev app/main.py
   ```

2. **Test the API**:
   ```bash
   curl http://localhost:8000/api/models
   ```

   You should see a JSON response with available models:
   ```json
   {
     "image": [
       {"id": "sd-turbo", "label": "Stable Diffusion Turbo"},
       {"id": "sd15", "label": "Stable Diffusion 1.5"}
     ],
     "video": [...],
     "defaults": {...}
   }
   ```

3. **Start Streamlit**:
   ```bash
   streamlit run apps/streamlit_app.py
   ```

   Open http://localhost:8501 in your browser

## Troubleshooting

### "HF_TOKEN environment variable not set"

- Make sure you created the `.env` file in the `backend/` directory
- Check that the token is correctly pasted (no extra spaces)
- Restart the backend server after adding the token

### "Authentication failed"

- Verify your token is valid: https://huggingface.co/settings/tokens
- Make sure the token has "Read" permissions
- Try regenerating the token if it's expired

### "Model not found" or "403 Forbidden"

- Some models require accepting their license agreement
- Go to the model page on Hugging Face and accept the terms:
  - https://huggingface.co/stabilityai/sd-turbo
  - https://huggingface.co/runwayml/stable-diffusion-v1-5
  - https://huggingface.co/stabilityai/stable-video-diffusion-img2vid

### Video generation is very slow

- Video generation on CPU can take 5-10 minutes
- Consider using Inference Endpoints (see Step 4) for faster generation
- Or use a machine with GPU support

## Security Best Practices

1. **Never commit your .env file**: It's already in `.gitignore`
2. **Don't share your token**: Treat it like a password
3. **Rotate tokens regularly**: Create new tokens every few months
4. **Use Read-only tokens**: Unless you need to upload models
5. **Revoke unused tokens**: Delete old tokens from your HF settings

## Additional Resources

- **Hugging Face Documentation**: https://huggingface.co/docs
- **Inference API Docs**: https://huggingface.co/docs/api-inference/index
- **Inference Endpoints**: https://huggingface.co/docs/inference-endpoints/index
- **Model Cards**:
  - SD-Turbo: https://huggingface.co/stabilityai/sd-turbo
  - SD 1.5: https://huggingface.co/runwayml/stable-diffusion-v1-5
  - SVD img2vid: https://huggingface.co/stabilityai/stable-video-diffusion-img2vid

## Need Help?

If you encounter issues:

1. Check the backend logs for detailed error messages
2. Verify your token at https://huggingface.co/settings/tokens
3. Ensure you have accepted model licenses
4. Try the local diffusers fallback by setting `ENGINE_IMAGE=local` in `.env`

---

**Next Steps**: Once your token is configured, proceed to the main [README.md](README.md) for usage instructions.
