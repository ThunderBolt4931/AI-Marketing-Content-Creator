import time
from io import BytesIO
import modal
from huggingface_hub import login
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import sys
import requests
import os
from safetensors.torch import load_file

# Modal setup (same as your original)
cuda_version = "12.4.0"
flavor = "devel"
operating_sys = "ubuntu22.04"
tag = f"{cuda_version}-{flavor}-{operating_sys}"
cuda_dev_image = modal.Image.from_registry(
    f"nvidia/cuda:{tag}", add_python="3.11"
).entrypoint([])

diffusers_commit_sha = "81cf3b2f155f1de322079af28f625349ee21ec6b"

flux_image = (
    cuda_dev_image.apt_install(
        "git",
        "libglib2.0-0",
        "libsm6",
        "libxrender1",
        "libxext6",
        "ffmpeg",
        "libgl1",
    )
    .pip_install(
        "invisible_watermark==0.2.0",
        "peft==0.10.0",
        "transformers==4.44.0",
        "huggingface_hub[hf_transfer]==0.26.2",
        "accelerate==0.33.0",
        "safetensors==0.4.4",
        "sentencepiece==0.2.0",
        "torch==2.5.0",
        f"git+https://github.com/huggingface/diffusers.git@{diffusers_commit_sha}",
        "numpy<2",
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HUB_CACHE": "/cache"})
)

flux_image = flux_image.env(
    {
        "TORCHINDUCTOR_CACHE_DIR": "/root/.inductor-cache",
        "TORCHINDUCTOR_FX_GRAPH_CACHE": "1",
    }
)

app = modal.App("flux-api-server", image=flux_image, secrets=[modal.Secret.from_name("huggingface-token")])

with flux_image.imports():
    import torch
    from diffusers import FluxPipeline

MINUTES = 60  # seconds
VARIANT = "dev"
NUM_INFERENCE_STEPS = 50

class ImageRequest(BaseModel):
    prompt: str
    num_inference_steps: int = 50
    width: int = 1024  # Add width parameter
    height: int = 1024  # Add height parameter

class ImageResponse(BaseModel):
    image_base64: str
    generation_time: float

@app.cls(
    gpu="H200",
    scaledown_window=20 * MINUTES,
    timeout=60 * MINUTES,
    volumes={
        "/cache": modal.Volume.from_name("hf-hub-cache", create_if_missing=True),
        "/root/.nv": modal.Volume.from_name("nv-cache", create_if_missing=True),
        "/root/.triton": modal.Volume.from_name("triton-cache", create_if_missing=True),
        "/root/.inductor-cache": modal.Volume.from_name(
            "inductor-cache", create_if_missing=True
        ),
    },
)
class Model:
    compile: bool = modal.parameter(default=False)

    lora_loaded = False
    lora_path = "/cache/flux.1_lora_flyway_doodle-poster.safetensors"
    lora_url = "https://huggingface.co/RajputVansh/SG161222-DISTILLED-IITI-VANSH-RUHELA/resolve/main/flux.1_lora_flyway_doodle-poster.safetensors?download=true"

    def download_lora_from_url(self, url, save_path):
        """Download LoRA with proper error handling"""
        try:
            print(f"📥 Downloading LoRA from {url}")
            response = requests.get(url, timeout=300)  # 5 minute timeout
            response.raise_for_status()  # Raise exception for bad status codes
            
            with open(save_path, "wb") as f:
                f.write(response.content)
            
            print(f"✅ LoRA downloaded successfully to {save_path}")
            print(f"📊 File size: {len(response.content)} bytes")
            return True
        except Exception as e:
            print(f"❌ LoRA download failed: {str(e)}")
            return False

    def verify_lora_file(self, lora_path):
        """Verify that the LoRA file is valid"""
        try:
            if not os.path.exists(lora_path):
                return False, "File does not exist"
            
            file_size = os.path.getsize(lora_path)
            if file_size == 0:
                return False, "File is empty"
            
            # Try to load the file to verify it's valid
            try:
                load_file(lora_path)
                return True, f"Valid LoRA file ({file_size} bytes)"
            except Exception as e:
                return False, f"Invalid LoRA file: {str(e)}"
                
        except Exception as e:
            return False, f"Error verifying file: {str(e)}"

    @modal.enter()
    def enter(self):
        from huggingface_hub import login
        import os

        # Login to HuggingFace
        token = os.environ["huggingface_token"]
        login(token)

        # Download and verify LoRA
        if not os.path.exists(self.lora_path):
            print("📥 LoRA not found, downloading...")
            download_success = self.download_lora_from_url(self.lora_url, self.lora_path)
            if not download_success:
                print("❌ Failed to download LoRA, continuing without it")
                self.lora_loaded = False
        else:
            print("📁 LoRA file found in cache")

        # Verify LoRA file
        is_valid, message = self.verify_lora_file(self.lora_path)
        print(f"🔍 LoRA verification: {message}")

        # Load the base model
        from diffusers import FluxPipeline
        import torch

        print("🚀 Loading Flux model...")
        pipe = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-dev",
            torch_dtype=torch.bfloat16
        ).to("cuda")

        # Load LoRA if available and valid
        if is_valid:
            try:
                print(f"🔄 Loading LoRA from {self.lora_path}")
                pipe.load_lora_weights(self.lora_path)
                print("✅ LoRA successfully loaded!")
                self.lora_loaded = True
                
                # Test LoRA by checking if it affects the model
                print("🧪 Testing LoRA integration...")
                # You could add a simple test generation here if needed
                
            except Exception as e:
                print(f"❌ LoRA loading failed: {str(e)}")
                self.lora_loaded = False
        else:
            print("⚠️ LoRA not loaded due to verification failure")
            self.lora_loaded = False

        # Optimize the pipeline
        self.pipe = optimize(pipe, compile=self.compile)
        
        print(f"🎯 Model ready! LoRA status: {'✅ Loaded' if self.lora_loaded else '❌ Not loaded'}")


    @modal.method()
    def get_model_status(self) -> dict:
        """Get detailed model and LoRA status"""
        lora_file_info = {}
        if os.path.exists(self.lora_path):
            try:
                file_size = os.path.getsize(self.lora_path)
                lora_file_info = {
                    "exists": True,
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2)
                }
            except:
                lora_file_info = {"exists": False}
        else:
            lora_file_info = {"exists": False}

        return {
            "status": "ready",
            "lora_loaded": self.lora_loaded,
            "lora_path": self.lora_path,
            "model_info": {
                "base_model": "black-forest-labs/FLUX.1-dev",
                "lora_file": lora_file_info,
                "lora_url": self.lora_url
            }
        }

    @modal.method()
    def inference(self, prompt: str, num_inference_steps: int = 50, width: int = 1024, height: int = 1024) -> dict:
        # Clean and prepare the prompt
        final_prompt = prompt
        
        print(f"🎨 Generating image:")
        print(f"   Original prompt: {prompt}")
        print(f"   Final prompt: {final_prompt}")
        print(f"   Dimensions: {width}x{height}")
        print(f"   LoRA status: {'✅ Active' if self.lora_loaded else '❌ Inactive'}")
        
        start_time = time.time()
        
        out = self.pipe(
            final_prompt,
            output_type="pil",
            num_inference_steps=num_inference_steps,
            width=width,
            height=height,
            max_sequence_length=512
        ).images[0]

        # Convert to base64
        byte_stream = BytesIO()
        out.save(byte_stream, format="PNG")
        image_bytes = byte_stream.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        generation_time = time.time() - start_time
        print(f"✅ Generated image in {generation_time:.2f} seconds")
        
        return {
            "image_base64": image_base64,
            "generation_time": generation_time,
            "final_prompt": final_prompt,
            "lora_used": self.lora_loaded
        }
# FastAPI server
fastapi_app = FastAPI(title="Flux Image Generation API")

# Initialize model instance
model_instance = Model(compile=False)

@fastapi_app.post("/generate", response_model=ImageResponse)
async def generate_image(request: ImageRequest):
    try:
        print(f"Received request: {request.prompt} at {request.width}x{request.height}")
        result = model_instance.inference.remote(
            request.prompt, 
            request.num_inference_steps,
            request.width,
            request.height
        )
        return ImageResponse(**result)
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@fastapi_app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Flux API server is running"}

@app.function(
    image=flux_image.pip_install("fastapi", "uvicorn"),
    keep_warm=1,
    timeout=60 * MINUTES,
)
@modal.asgi_app()
def fastapi_server():
    return fastapi_app

def optimize(pipe, compile=True):
    # fuse QKV projections in Transformer and VAE
    pipe.transformer.fuse_qkv_projections()
    pipe.vae.fuse_qkv_projections()

    # switch memory layout to Torch's preferred, channels_last
    pipe.transformer.to(memory_format=torch.channels_last)
    pipe.vae.to(memory_format=torch.channels_last)

    if not compile:
        return pipe

    # set torch compile flags
    config = torch._inductor.config
    config.disable_progress = False
    config.conv_1x1_as_mm = True
    config.coordinate_descent_tuning = True
    config.coordinate_descent_check_all_directions = True
    config.epilogue_fusion = False

    # compile the compute-intensive modules
    pipe.transformer = torch.compile(
        pipe.transformer, mode="max-autotune", fullgraph=True
    )
    pipe.vae.decode = torch.compile(
        pipe.vae.decode, mode="max-autotune", fullgraph=True
    )

    # trigger torch compilation
    print("🔦 Running torch compilation (may take up to 20 minutes)...")
    pipe(
        "dummy prompt to trigger torch compilation",
        output_type="pil",
        num_inference_steps=NUM_INFERENCE_STEPS,
    ).images[0]
    print("🔦 Finished torch compilation")

    return pipe

if __name__ == "__main__":
    print("Starting Modal Flux API server...")
    # This will be handled by Modal's deployment