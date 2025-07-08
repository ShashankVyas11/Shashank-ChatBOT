import subprocess
import json
import torch
import os
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from diffusers import StableDiffusionPipeline

# ==========  BLIP: Image Captioning Setup ==========
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def analyze_image(image_path):
    """
    Analyze an uploaded image and generate a text caption using BLIP.
    """
    try:
        image = Image.open(image_path).convert("RGB")

        # Resize large images for memory efficiency
        max_dim = 1024
        if max(image.size) > max_dim:
            image.thumbnail((max_dim, max_dim))

        inputs = blip_processor(image, return_tensors="pt")
        output = blip_model.generate(**inputs)
        caption = blip_processor.decode(output[0], skip_special_tokens=True)
        return caption

    except Exception as e:
        return f" Error analyzing image: {str(e)}"


# ==========  LLaMA (via Ollama) Setup ==========
def ask_llama(prompt):
    """
    Send a prompt to local LLaMA 3 model via Ollama CLI.
    """
    try:
        result = subprocess.run(
            [
                "C:\\Users\\Shashank\\AppData\\Local\\Programs\\Ollama\\ollama.exe",
                "run", "llama3", prompt
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        return f" LLaMA error: {e.stderr.strip()}"
    except Exception as e:
        return f" Unexpected error: {str(e)}"


# ==========  Stable Diffusion: Image Generation ==========
try:
    model_id = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float32)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = pipe.to(device)
except Exception as e:
    pipe = None
    print(f" Failed to load Stable Diffusion model: {e}")

def generate_image(prompt):
    """
    Generate image from prompt using Stable Diffusion. Returns web path for Flask.
    """
    try:
        if pipe is None:
            return " Stable Diffusion model is not loaded."

        # Get absolute static folder path
        base_dir = os.path.dirname(os.path.abspath(__file__))  # .../chatbot-code/utils
        static_dir = os.path.join(base_dir, "..", "static")
        os.makedirs(static_dir, exist_ok=True)

        # Full image save path
        output_path = os.path.join(static_dir, "generated.png")

        # Generate and save image
        image = pipe(prompt).images[0]
        image.save(output_path)

        # Return relative web path
        return "/static/generated.png"

    except Exception as e:
        return f" Image generation error: {str(e)}"


# ==========  (Optional) Dummy Weather API ==========
def get_weather(location, unit="celsius"):
    """
    Dummy weather function for future extension.
    """
    return json.dumps({
        "location": location,
        "temperature": "31",
        "unit": unit,
        "forecast": ["sunny", "clear"]
    })
