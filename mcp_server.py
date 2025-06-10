import os
import base64
import requests
import asyncio
import aiohttp
import json
from datetime import datetime
from typing import List, Dict
import zipfile
from io import BytesIO
from PIL import Image
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("modal_flux_testing", timeout=500)


MODAL_API_URL = os.environ.get("MODAL_API_URL")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


SIZE_PRESETS = {
    "instagram_post": (1080, 1080),
    "instagram_story": (1080, 1920),
    "twitter_post": (1200, 672),
    "linkedin_post": (1200, 1200),
    "facebook_cover": (1200, 632),
    "youtube_thumbnail": (1280, 720),
}


PROMPT_TEMPLATES = {
    "product_hero": """A professional, cinematic product photography composition featuring {product} as the center subject against a {background} backdrop. The scene is illuminated with dramatic studio lighting creating golden highlights and deep shadows. The {product} appears to float with ethereal light emanating from beneath, surrounded by subtle glowing particles and atmospheric mist. The composition uses cinematic depth of field with the product razor-sharp in focus while the background fades into artistic bokeh. Luxurious materials and textures are emphasized with photorealistic detail, showcasing premium quality and craftsmanship.""",
    
    "social_announcement": """A high-energy, cinematic social media poster announcing {announcement}. The composition features bold, dramatic lighting with vibrant neon glows and electric energy crackling through the frame. Dynamic typography with the announcement text appears in luxurious, impactful metallic font that seems to emerge from the composition. The backdrop features a futuristic cityscape at night with towering skyscrapers surrounded by colorful LED light strips. Atmospheric elements include flowing energy streams, glowing particles, and lens flares that create a sense of excitement and urgency. The entire poster pulses with kinetic energy and modern sophistication.""",
    
    "blog_header": """An elegant, cinematic header image for a blog post about {topic}. The composition features ethereal lighting with soft golden hour illumination casting dramatic shadows across the scene. In the foreground, symbolic elements related to {topic} are artistically arranged with professional depth of field. The background dissolves into atmospheric mist with subtle bokeh and floating light particles. The color palette consists of warm golds, deep purples, and rich earth tones. The entire composition exudes intellectual sophistication and visual storytelling, with magazine-quality photography aesthetics.""",
    
    "team_photo": """A cinematic corporate team photograph showing {description} in a modern, luxurious office environment. The scene is lit with dramatic architectural lighting, featuring large floor-to-ceiling windows with natural light streaming in, creating beautiful rim lighting around the subjects. The team is positioned dynamically across multiple levels of the space, with some standing and others seated in premium furniture. The background showcases sleek modern architecture with glass, steel, and wood elements. Professional color grading gives the image a premium, magazine-worthy aesthetic with rich contrasts and warm undertones.""",
    
    "event_banner": """A spectacular, cinematic event banner for {event} with movie poster-level production value. The composition features epic scale with dramatic perspective and atmospheric depth. Bold, metallic event typography dominates the upper portion with luxurious, impactful font treatment that appears to be forged from light itself. The scene is filled with dynamic elements: swirling energy, floating particles, dramatic spotlights cutting through atmospheric haze, and architectural elements that frame the composition. The color palette uses deep blues, electric purples, and gold accents to create excitement and grandeur.""",
    
    "testimonial_bg": """An abstract, cinematic background for testimonial content featuring {mood} aesthetic. The composition uses flowing, organic shapes with ethereal lighting effects creating depth and movement. Subtle geometric patterns emerge from atmospheric mist while soft, diffused lighting creates beautiful gradients across the frame. The scene includes floating elements like delicate particles, soft bokeh, and gentle light rays that add visual interest without overwhelming the testimonial text. The color palette is sophisticated and calming, using gradient transitions between complementary colors to create emotional resonance.""",
    
    "poster_style": """A cinematic movie poster composition featuring {subject} with dramatic, high-impact visual storytelling. The scene is dominated by theatrical lighting with bold contrasts between light and shadow. The main subject is positioned using classical composition rules with supporting elements arranged to guide the eye. Atmospheric elements include swirling mist, dramatic sky, glowing magical effects, and rich environmental details. The composition features layered depth with foreground, midground, and background elements all contributing to the narrative. Typography space is reserved for impactful text placement with the overall mood being {mood}.""",
    
    "luxury_product": """An ultra-premium product showcase featuring {product} in a luxurious, museum-quality presentation. The item sits on pristine surfaces with perfect reflections, surrounded by architectural elements like marble, gold accents, and crystal. Dramatic lighting creates spectacular highlights and deep shadows, emphasizing every detail and texture. The background features elegant negative space with subtle gradient lighting and floating particles that suggest exclusivity. The entire composition exudes opulence and sophistication, with photorealistic detail that showcases premium craftsmanship and materials."""
}


STYLE_MODIFIERS = {
    "professional": """professional studio lighting, cinematic composition, dramatic shadows and highlights, premium materials and textures, photorealistic detail, magazine-quality photography, sophisticated color grading, architectural precision, corporate elegance, high-end commercial aesthetics""",
    
    "playful": """vibrant neon colors, electric energy crackling through the frame, dynamic movement and flow, glowing particles and magical elements, whimsical floating objects, rainbow light effects, kinetic energy, joyful atmosphere, colorful light strips and LED effects, fun and energetic composition""",
    
    "minimalist": """clean geometric composition, pristine white negative space, single dramatic light source, subtle shadows and highlights, elegant simplicity, floating elements with perfect spacing, monochromatic or limited color palette, architectural precision, zen-like tranquility, museum-quality presentation""",
    
    "luxury": """opulent materials like gold, marble, and crystal, dramatic chiaroscuro lighting, rich textures and reflections, premium craftsmanship details, sophisticated color palette of deep jewel tones, elegant architectural elements, museum-quality presentation, exclusive atmosphere, metallic accents and flowing fabrics""",
    
    "tech": """futuristic neon lighting with electric blue and cyan glows, holographic interfaces and digital elements, sleek metallic surfaces with perfect reflections, floating geometric shapes, matrix-style digital rain effects, cyberpunk aesthetic, glowing circuit patterns, high-tech laboratory environment, innovative and cutting-edge atmosphere""",
    
    "cinematic": """movie poster lighting with dramatic spotlights, atmospheric haze and volumetric fog, epic scale and perspective, rich color grading with deep contrasts, cinematic depth of field, theatrical composition, dramatic sky and environmental elements, professional film-quality aesthetics, storytelling through visual elements""",
    
    "mystical": """ethereal lighting with soft, magical glows, floating particles and sparkles, misty atmospheric effects, enchanted forest or temple environment, glowing runes and magical symbols, otherworldly color palette of purples and golds, mysterious shadows and light rays, fantasy movie aesthetic, ancient and magical atmosphere""",
    
    "editorial": """magazine-quality photography lighting, sophisticated composition following rule of thirds, professional color grading, high fashion aesthetic, dramatic contrasts, premium materials and styling, architectural or natural backgrounds, artistic depth of field, editorial sophistication, contemporary visual storytelling"""
}

VARIATION_STRATEGIES = {
    "color_schemes": [
        "with warm colors (reds, oranges, yellows)",
        "with cool colors (blues, greens, purples)", 
        "with bold, high-contrast colors",
        "with muted, pastel colors",
        "monochromatic color scheme"
    ],
    "composition_styles": [
        "centered composition with symmetrical balance",
        "rule of thirds composition with dynamic flow",
        "minimalist composition with lots of white space",
        "busy, detailed composition with multiple elements",
        "close-up, focused composition"
    ],
    "emotional_tones": [
        "energetic and exciting mood",
        "calm and peaceful atmosphere",
        "professional and trustworthy feel",
        "fun and playful vibe",
        "luxurious and premium aesthetic"
    ],
    "visual_styles": [
        "photorealistic style",
        "illustrated/graphic design style",
        "vintage/retro aesthetic",
        "modern/contemporary look",
        "artistic/creative approach"
    ],
    "lighting_moods": [
        "bright, well-lit scene",
        "dramatic lighting with shadows",
        "soft, diffused lighting",
        "golden hour warm lighting",
        "studio lighting setup"
    ]
}


CONTENT_CREATOR_VARIATIONS = {
    "social_media": [
        "Instagram-optimized with bold text overlay space",
        "TikTok-style with vertical focus and trending elements",
        "LinkedIn professional with corporate aesthetic",
        "YouTube thumbnail with clickable visual hierarchy",
        "Twitter-friendly with clear, readable elements"
    ],
    "engagement_hooks": [
        "with eye-catching focal point in center",
        "with contrasting element to grab attention",
        "with human faces or eyes for connection",
        "with bright colors that pop in feeds",
        "with intriguing visual question or mystery"
    ],
    "brand_positioning": [
        "premium/luxury brand positioning",
        "affordable/accessible brand feel",
        "innovative/cutting-edge brand image",
        "trustworthy/established brand look",
        "fun/approachable brand personality"
    ]
}



generation_history = []


@mcp.tool()
async def generate_prompt_with_ai(user_input: str, context: str = "marketing", style: str = "professional", platform: str = "general") -> str:
    """
    Use Mistral AI to generate optimized prompts for Flux image generation.
    
    Args:
        user_input: What the user wants to create
        context: The context (marketing, product, social, etc.)
        style: The desired style
        platform: Target platform (instagram, twitter, etc.)
    
    Returns:
        An optimized prompt for Flux
    """
    try:
        system_prompt = """You are an expert prompt engineer specializing in creating detailed, cinematic prompts for Flux AI image generation. 

Your prompts should be like movie poster descriptions - highly detailed, vivid, and cinematic. Study these examples:

GOOD EXAMPLES:
- "minimal poster featuring multiple hands coming out of frame holding a globe as the center subject. there is a miniature world on top of the globe, with happy miniature people and lush green trees. the word 'EARTH' appears above the main subject, with a luxurious, impactful font. the backdrop features a minimalistic galaxy background with glowing stars. the main subject is well lit and the poster is vividly colorful."

- "A high-energy, cinematic movie poster capturing an intense, high-stakes race between Sonic the Hedgehog and a cheetah, set against the vast African savannah at sunset. The poster features bold, dramatic lighting, with the golden glow of the setting sun casting long shadows as both competitors blur across the landscape, dust swirling behind them."

KEY REQUIREMENTS:
1. Be extremely detailed and descriptive
2. Include specific lighting details (dramatic lighting, golden glow, well lit, etc.)
3. Describe the composition and framing
4. Add cinematic and poster-like qualities
5. Include color palette descriptions
6. Mention text placement if relevant
7. Add atmospheric details (mist, smoke, glowing elements)
8. Keep under 200 words but pack in maximum detail
9. Use vivid, cinematic language
10. Focus on visual storytelling

Generate prompts that sound like professional movie poster or advertisement descriptions."""
        
        user_message = f"""Create a detailed, cinematic prompt for Flux AI based on:

User Request: {user_input}
Context: {context} 
Style: {style}
Platform: {platform}

Make it sound like a professional movie poster description with rich visual details, specific lighting, composition, and atmospheric elements. Keep it under 200 words but extremely detailed and vivid."""
        
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistral-large-latest",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.8, 
            "max_tokens": 250 
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                MISTRAL_API_URL,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Mistral API error ({response.status}): {error_text}")
                
                result = await response.json()
                generated_prompt = result['choices'][0]['message']['content']
                
               
                word_count = len(generated_prompt.split())
                if word_count > 200:
                    
                    words = generated_prompt.split()
                    truncated = ' '.join(words[:190])
                    # Find the last complete sentence
                    last_period = truncated.rfind('.')
                    if last_period > 100:  
                        generated_prompt = truncated[:last_period + 1]
                
                return json.dumps({
                    "success": True,
                    "prompt": generated_prompt,
                    "user_input": user_input,
                    "context": context,
                    "style": style,
                    "word_count": len(generated_prompt.split())
                })
                
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "fallback_prompt": f"Cinematic {style} style image of {user_input}, dramatic lighting, high detail, professional composition, vivid colors"
        })

@mcp.tool()
async def enhance_prompt_with_details(base_prompt: str, enhancement_type: str = "cinematic") -> str:
    """
    Enhance a basic prompt with detailed visual elements like your examples.
    
    Args:
        base_prompt: The basic prompt to enhance
        enhancement_type: Type of enhancement (cinematic, poster, product, etc.)
    
    Returns:
        Enhanced detailed prompt
    """
    try:
        system_prompt = """You are an expert at enhancing image prompts with rich visual details. Take the basic prompt and transform it into a highly detailed, cinematic description like a movie poster or professional advertisement.

Add elements like:
- Specific lighting (dramatic, golden glow, well lit, ethereal light)
- Composition details (center subject, background elements, framing)
- Atmospheric elements (mist, smoke, glowing stars, dust swirling)
- Color palette descriptions
- Texture and material details
- Cinematic qualities and mood
- Professional photography/poster qualities

Keep the enhanced prompt under 200 words but extremely detailed."""
        
        user_message = f"""Enhance this basic prompt with rich visual details:

Basic Prompt: {base_prompt}
Enhancement Type: {enhancement_type}

Transform it into a detailed, cinematic description with specific lighting, composition, atmosphere, and visual storytelling elements."""
        
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mistral-large-latest",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.8,
            "max_tokens": 250
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                MISTRAL_API_URL,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Mistral API error ({response.status}): {error_text}")
                
                result = await response.json()
                enhanced_prompt = result['choices'][0]['message']['content']
                
                # Ensure under 200 words
                word_count = len(enhanced_prompt.split())
                if word_count > 200:
                    words = enhanced_prompt.split()
                    truncated = ' '.join(words[:190])
                    last_period = truncated.rfind('.')
                    if last_period > 100:
                        enhanced_prompt = truncated[:last_period + 1]
                
                return json.dumps({
                    "success": True,
                    "original_prompt": base_prompt,
                    "enhanced_prompt": enhanced_prompt,
                    "word_count": len(enhanced_prompt.split())
                })
                
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "original_prompt": base_prompt
        })

@mcp.tool()
async def generate_and_save_image(prompt: str, num_inference_steps: int = 50, width: int = 1024, height: int = 1024) -> str:
    """Generate a single image with specified dimensions"""
    try:
        print(f"Sending request to Modal API: {prompt} at {width}x{height}")
        payload = {
            "prompt": prompt,
            "num_inference_steps": num_inference_steps,
            "width": width,
            "height": height
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{MODAL_API_URL}/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Modal API error ({response.status}): {error_text}")
                
                result = await response.text()
                result_json = json.loads(result)
                
                if 'image_base64' in result_json:
                    image_b64 = result_json['image_base64']
                    
                    # Store in history
                    generation_history.append({
                        "prompt": prompt,
                        "timestamp": datetime.now().isoformat(),
                        "dimensions": f"{width}x{height}",
                        "image_base64": image_b64[:100] + "..." 
                    })
                    
                    return image_b64
                else:
                    raise Exception("No 'image_base64' key found in response")
                    
    except Exception as e:
        print(f"Error in generate_and_save_image: {str(e)}")
        raise Exception(f"Error generating image: {str(e)}")
    
@mcp.tool()
async def batch_generate_smart_variations(prompt: str, count: int = 3, variation_type: str = "mixed", num_inference_steps: int = 50, width: int = 1024, height: int = 1024) -> str:
    """
    Generate multiple meaningful variations for A/B testing content.
    
    variation_type options:
    - "mixed": Different strategies (recommended for general testing)
    - "color_schemes": Test different color approaches
    - "composition_styles": Test different layouts
    - "emotional_tones": Test different moods
    - "social_media": Platform-optimized variations
    - "engagement_hooks": Test attention-grabbing elements
    - "brand_positioning": Test different brand feels
    """
    if count > 5:
        count = 5
        
    variations = []
    
    if variation_type == "mixed":

        all_variations = []
        for strategy in VARIATION_STRATEGIES.values():
            all_variations.extend(strategy[:2]) 
        
       
        all_variations.extend(CONTENT_CREATOR_VARIATIONS["engagement_hooks"][:2])
        
        
        import random
        selected_variations = random.sample(all_variations, min(count, len(all_variations)))
        
    elif variation_type in VARIATION_STRATEGIES:
        selected_variations = VARIATION_STRATEGIES[variation_type][:count]
    elif variation_type in CONTENT_CREATOR_VARIATIONS:
        selected_variations = CONTENT_CREATOR_VARIATIONS[variation_type][:count]
    else:
       
        selected_variations = [
            "with vibrant, attention-grabbing colors",
            "with professional, clean aesthetic", 
            "with bold, dramatic composition"
        ][:count]
    
    results = []
    
    for i, variation in enumerate(selected_variations):
        enhanced_prompt = f"{prompt}, {variation}"
        
        try:
            print(f"Generating variation {i+1}/{count}: {variation}")
            image_b64 = await generate_and_save_image(enhanced_prompt, num_inference_steps, width, height)
            
            results.append({
                "index": i,
                "variation_description": variation,
                "full_prompt": enhanced_prompt,
                "dimensions": f"{width}x{height}",
                "image_base64": image_b64,
                "testing_purpose": get_testing_purpose(variation)
            })
            
        except Exception as e:
            print(f"Error generating variation {i+1}: {str(e)}")
            
    return json.dumps({
        "images": results, 
        "count": len(results),
        "variation_type": variation_type,
        "testing_strategy": get_testing_strategy(variation_type)
    })

def get_testing_purpose(variation: str) -> str:
    """Get the testing purpose for a variation"""
    if "warm colors" in variation or "cool colors" in variation:
        return "Test color psychology impact on engagement"
    elif "centered" in variation or "rule of thirds" in variation:
        return "Test composition impact on visual flow"
    elif "energetic" in variation or "calm" in variation:
        return "Test emotional response and brand perception"
    elif "Instagram" in variation or "TikTok" in variation:
        return "Test platform-specific optimization"
    elif "premium" in variation or "affordable" in variation:
        return "Test brand positioning and target audience appeal"
    elif "eye-catching" in variation or "contrasting" in variation:
        return "Test attention-grabbing effectiveness"
    else:
        return "Test visual style preference"

def get_testing_strategy(variation_type: str) -> str:
    """Get testing strategy explanation"""
    strategies = {
        "mixed": "Comprehensive A/B test across multiple variables to identify best overall approach",
        "color_schemes": "Test how different colors affect engagement and emotional response",
        "composition_styles": "Test how layout affects visual hierarchy and user attention",
        "emotional_tones": "Test which mood resonates best with your target audience",
        "social_media": "Test platform-specific optimizations for maximum reach",
        "engagement_hooks": "Test attention-grabbing elements for better click-through rates",
        "brand_positioning": "Test how different brand feels affect audience perception"
    }
    return strategies.get(variation_type, "Test different approaches to optimize content performance")

@mcp.tool()
async def generate_ab_test_report_template(variations_data: str) -> str:
    """Generate a template for tracking A/B test results"""
    import json
    data = json.loads(variations_data)
    
    report_template = {
        "test_name": "Content Variation A/B Test",
        "test_date": datetime.now().isoformat(),
        "variation_type": data.get("variation_type", "mixed"),
        "testing_strategy": data.get("testing_strategy", ""),
        "variations": [],
        "metrics_to_track": [
            "Impressions",
            "Engagement Rate (%)",
            "Click-through Rate (%)",
            "Saves/Shares",
            "Comments",
            "Conversion Rate (%)"
        ],
        "recommended_test_duration": "7-14 days for statistical significance",
        "sample_size_needed": "Minimum 1000 impressions per variation"
    }
    
    for img in data.get("images", []):
        report_template["variations"].append({
            "variation_id": f"V{img['index'] + 1}",
            "description": img["variation_description"],
            "testing_purpose": img["testing_purpose"],
            "results": {
                "impressions": 0,
                "engagement_rate": 0,
                "ctr": 0,
                "saves": 0,
                "comments": 0,
                "conversion_rate": 0
            },
            "notes": ""
        })
    
    return json.dumps(report_template, indent=2)


@mcp.tool()
async def batch_generate_images(prompt: str, count: int = 3, num_inference_steps: int = 50, width: int = 1024, height: int = 1024) -> str:
    """
    Generate multiple images with smart variations for A/B testing.
    Now uses meaningful variations instead of identical images.
    """
    return await batch_generate_smart_variations(
        prompt=prompt,
        count=count,
        variation_type="mixed",
        num_inference_steps=num_inference_steps,
        width=width,
        height=height
    )


@mcp.tool()
async def generate_social_media_set(prompt: str, platforms: List[str], num_inference_steps: int = 50) -> str:
    """
    Generate images optimized for different social media platforms with correct resolutions.
    Platforms: instagram_post, instagram_story, twitter_post, linkedin_post, etc.
    """
    results = []
    
    for platform in platforms:
        if platform in SIZE_PRESETS:
            width, height = SIZE_PRESETS[platform]
            platform_prompt = f"{prompt}, optimized for {platform.replace('_', ' ')}"
            
            try:
               
                image_b64 = await generate_and_save_image(
                    platform_prompt, 
                    num_inference_steps, 
                    width, 
                    height
                )
                results.append({
                    "platform": platform,
                    "size": [width, height],
                    "resolution": f"{width}x{height}",
                    "image_base64": image_b64
                })
                print(f"✅ Generated {platform} image at {width}x{height}")
            except Exception as e:
                print(f"Error generating for {platform}: {str(e)}")
                
    return json.dumps({"results": results})

@mcp.tool() 
async def add_style_modifier(prompt: str, style: str) -> str:
    """
    Add style modifiers to ensure brand consistency.
    Styles: professional, playful, minimalist, luxury, tech
    """
    if style not in STYLE_MODIFIERS:
        return json.dumps({
            "error": f"Style '{style}' not found",
            "available_styles": list(STYLE_MODIFIERS.keys())
        })
        
    enhanced_prompt = f"{prompt}, {STYLE_MODIFIERS[style]}"
    return json.dumps({
        "original_prompt": prompt,
        "enhanced_prompt": enhanced_prompt,
        "style_applied": style
    })

@mcp.tool()
async def get_generation_history(limit: int = 10) -> str:
    """Get recent generation history for reuse and reference"""
    recent_history = generation_history[-limit:]
    return json.dumps({
        "history": recent_history,
        "total_generations": len(generation_history)
    })

@mcp.tool()
async def create_image_package(image_data_list: List[Dict], package_name: str = "marketing_assets") -> str:
    """
    Create a downloadable package of generated images with metadata.
    Useful for bulk content creation and organization.
    """

    
    package_info = {
        "package_name": package_name,
        "created_at": datetime.now().isoformat(),
        "total_images": len(image_data_list),
        "images": []
    }
    
    for idx, data in enumerate(image_data_list):
        package_info["images"].append({
            "filename": f"{package_name}_{idx+1}.png",
            "prompt": data.get("prompt", ""),
            "metadata": data.get("metadata", {})
        })
        
    return json.dumps(package_info)

@mcp.tool()
async def health_check() -> str:
    """Check if the Modal API server is healthy"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{MODAL_API_URL}/health",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    result = await response.text()
                    return f"Modal API is healthy: {result}"
                else:
                    return f"Modal API returned status {response.status}"
    except Exception as e:
        return f"Modal API health check failed: {str(e)}"

if __name__ == "__main__":
    print("Starting Enhanced MCP server for Content Creators & Marketers...")
    print(f"Modal API URL: {MODAL_API_URL}")
    mcp.run(transport="stdio")