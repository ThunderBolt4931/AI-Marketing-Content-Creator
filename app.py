import gradio as gr
import base64
import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from typing import List
import nest_asyncio
import threading
import queue
import time
from PIL import Image
from io import BytesIO
os.makedirs("AI-Marketing-Content-Creator/created_image", exist_ok=True)

nest_asyncio.apply()



class MCP_Modal_Marketing_Tool:
    def __init__(self):
        self.session: ClientSession = None
        self.available_tools: List[dict] = []
        self.is_connected = False
        self.request_queue = queue.Queue()
        self.result_queue = queue.Queue()

    async def call_mcp_tool(self, tool_name: str, arguments: dict):
        """Generic method to call any MCP tool"""
        try:
            result = await self.session.call_tool(tool_name, arguments=arguments)
            if hasattr(result, 'content') and result.content:
                return result.content[0].text
            return None
        except Exception as e:
            print(f"Error calling tool {tool_name}: {str(e)}")
            raise e

    async def process_queue(self):
        """Process requests from the queue"""
        while True:
            try:
                if not self.request_queue.empty():
                    item = self.request_queue.get()
                    if item == "STOP":
                        break

                    tool_name, arguments, request_id = item
                    try:
                        result = await self.call_mcp_tool(tool_name, arguments)
                        self.result_queue.put(("success", result, request_id))
                    except Exception as e:
                        self.result_queue.put(("error", str(e), request_id))
                else:
                    await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error in process_queue: {str(e)}")

    async def connect_to_server_and_run(self):
        """Connect to MCP server and start processing"""
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"],
            env={"MODAL_API_URL": os.environ.get("MODAL_API_URL"),
                 "MISTRAL_API_KEY": os.environ.get("MISTRAL_API_KEY"),
            },
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                await session.initialize()

                response = await session.list_tools()
                tools = response.tools
                print("Connected to MCP server with tools:",
                      [tool.name for tool in tools])

                self.available_tools = [{
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema
                } for tool in tools]

                self.is_connected = True
                print("Marketing Tool MCP Server connected!")

                # Check Modal health
                health_result = await self.call_mcp_tool("health_check", {})
                print(f"Modal API Status: {health_result}")

                await self.process_queue()



marketing_tool = MCP_Modal_Marketing_Tool()


def wait_for_result(request_id, timeout=300):
    """Wait for a result with a specific request ID"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not marketing_tool.result_queue.empty():
            status, result, result_id = marketing_tool.result_queue.get()
            if result_id == request_id:
                return status, result
            else:
                # Put it back if it's not our result
                marketing_tool.result_queue.put((status, result, result_id))
        time.sleep(0.1)
    return "error", "Timeout"


def decode_and_save_image(image_b64, filename):
    """Decode base64 and save image"""
    import base64
    from PIL import Image
    from io import BytesIO

    # Ensure the path is inside created_image/
    full_path = os.path.join("AI-Marketing-Content-Creator/created_image", filename)
    image_b64 = image_b64.strip()
    missing_padding = len(image_b64) % 4
    if missing_padding:
        image_b64 += '=' * (4 - missing_padding)

    image_data = base64.b64decode(image_b64)
    image = Image.open(BytesIO(image_data))
    image.save(full_path)
    return full_path


def single_image_generation(prompt, num_steps, style):
    """Generate a single image with optional style"""
    if not marketing_tool.is_connected:
        return None, "⚠️ MCP Server not connected. Please wait a few seconds and try again."

    try:
        request_id = f"single_{time.time()}"

        # Apply style if selected
        if style != "none":
            style_request_id = f"style_{time.time()}"
            marketing_tool.request_queue.put((
                "add_style_modifier",
                {"prompt": prompt, "style": style},
                style_request_id
            ))

            status, result = wait_for_result(style_request_id, timeout=50)
            if status == "success":
                style_data = json.loads(result)
                prompt = style_data["enhanced_prompt"]

        # Generate image
        marketing_tool.request_queue.put((
            "generate_and_save_image",
            {"prompt": prompt, "num_inference_steps": num_steps},
            request_id
        ))

        status, result = wait_for_result(request_id)

        if status == "success":
            filename = decode_and_save_image(
                result, f"generated_{int(time.time())}.png")
            return filename, f"✅ Image generated successfully!\n📝 Final prompt: {prompt}"
        else:
            return None, f"❌ Error: {result}"

    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# Update the batch generation function in app.py
def enhanced_batch_generation(prompt, variation_type, count, num_steps):
    """Generate strategic variations for A/B testing"""
    if not marketing_tool.is_connected:
        return None, "⚠️ MCP Server not connected. Please wait a few seconds and try again."
        
    try:
        request_id = f"smart_batch_{time.time()}"
        marketing_tool.request_queue.put((
            "batch_generate_smart_variations",
            {
                "prompt": prompt, 
                "count": count, 
                "variation_type": variation_type,
                "num_inference_steps": num_steps
            },
            request_id
        ))
        
        status, result = wait_for_result(request_id, timeout=300) 
        
        if status == "success":
            batch_data = json.loads(result)
            images = []
            variation_details = []
            
            for i, img_data in enumerate(batch_data["images"]):
                filename = decode_and_save_image(
                    img_data["image_base64"], 
                    f"variation_{i+1}_{int(time.time())}.png"
                )
                images.append(filename)
                
                variation_details.append(
                    f"**Variation {i+1}:** {img_data['variation_description']}\n"
                    f"*Testing Purpose:* {img_data['testing_purpose']}\n"
                )
            
            strategy_explanation = batch_data.get("testing_strategy", "")
            
            status_message = (
                f"✅ Generated {len(images)} strategic variations!\n\n"
                f"**Testing Strategy:** {strategy_explanation}\n\n"
                f"**Variations Created:**\n" + 
                "\n".join(variation_details) +
                f"\n💡 **Next Steps:** Post each variation and track engagement metrics to see which performs best!"
            )
            
            return images, status_message
        else:
            return None, f"❌ Error: {result}"
            
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


def update_strategy_info(variation_type):
    strategy_descriptions = {
        "mixed": {
            "title": "Mixed Strategy Testing",
            "description": "Tests multiple variables (colors, layout, mood) to find overall best approach",
            "use_case": "Best for comprehensive optimization when you're not sure what to test first"
        },
        "color_schemes": {
            "title": "Color Psychology Testing", 
            "description": "Tests how different color schemes affect emotional response and engagement",
            "use_case": "Great for brand content, product launches, and emotional marketing"
        },
        "composition_styles": {
            "title": "Layout & Composition Testing",
            "description": "Tests different visual arrangements and focal points",
            "use_case": "Perfect for optimizing visual hierarchy and user attention flow"
        },
        "emotional_tones": {
            "title": "Emotional Tone Testing",
            "description": "Tests different moods and feelings to see what resonates with your audience", 
            "use_case": "Ideal for brand personality and audience connection optimization"
        },
        "social_media": {
            "title": "Platform Optimization Testing",
            "description": "Tests platform-specific elements and styles",
            "use_case": "Essential for multi-platform content strategies"
        },
        "engagement_hooks": {
            "title": "Attention-Grabbing Testing",
            "description": "Tests different ways to capture and hold viewer attention",
            "use_case": "Critical for improving reach and stopping scroll behavior"
        },
        "brand_positioning": {
            "title": "Brand Positioning Testing", 
            "description": "Tests how different brand personalities affect audience perception",
            "use_case": "Important for brand development and target audience alignment"
        }
    }
    
    info = strategy_descriptions.get(variation_type, strategy_descriptions["mixed"])
    return f"""
    **💡 Current Strategy:** {info['title']}
    
    **What this tests:** {info['description']}
    
    **Best for:** {info['use_case']}
    """

def social_media_generation(prompt, platforms, num_steps):
    """Generate images for multiple social media platforms with correct resolutions"""
    if not marketing_tool.is_connected:
        return None, "MCP Server not connected"
        
    try:
        request_id = f"social_{time.time()}"
        marketing_tool.request_queue.put((
            "generate_social_media_set",
            {"prompt": prompt, "platforms": platforms, "num_inference_steps": num_steps},
            request_id
        ))
        
        status, result = wait_for_result(request_id)
        
        if status == "success":
            social_data = json.loads(result)
            results = []
            
            for platform_data in social_data["results"]:
                filename = decode_and_save_image(
                    platform_data["image_base64"],
                    f"{platform_data['platform']}_{platform_data['resolution']}_{int(time.time())}.png"
                )
                results.append((platform_data["platform"], filename, platform_data["resolution"]))
                
            # Create a status message with resolutions
            if results:
                status_msg = "Generated images:\n" + "\n".join([
                    f"• {r[0]}: {r[2]}" for r in results
                ])
                return [r[1] for r in results], status_msg
            else:
                return None, "No images generated"
        else:
            return None, f"Error: {result}"
            
    except Exception as e:
        return None, f"Error: {str(e)}"


def start_mcp_server():
    """Start MCP server in background"""
    def run_server():
        asyncio.run(marketing_tool.connect_to_server_and_run())

    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    return thread



SIZE_PRESETS = {
    "instagram_post": (1080, 1080),
    "instagram_story": (1080, 1920),
    "twitter_post": (1200, 675),
    "linkedin_post": (1200, 1200),
    "facebook_cover": (1200, 630),
    "youtube_thumbnail": (1280, 720)
}


with gr.Blocks(title="AI Marketing Content Generator") as demo:
    gr.Markdown("""
    # 🎨 AI Marketing Content Generator
    ### Powered by Flux AI on Modal GPU via MCP
    
    Generate professional marketing images with AI - optimized for content creators and marketers!
    
    ⏰ **Please wait 5-10 seconds after launching for the MCP server to connect**
    """)

    # Connection status
    connection_status = gr.Markdown("🔄 Connecting to MCP server...")

    with gr.Tabs():

        with gr.TabItem("📖 Quick Start"):
            gr.Markdown("""
            # 🚀 Welcome to AI Marketing Content Generator!
            ### Create professional marketing images in minutes - no design skills needed!
            
            ---
            
            ## ⚡ Get Started in 3 Simple Steps
            
            ### Step 1: ✅ Check Connection
            Look at the status above - wait for "✅ Connected" before starting
            
            ### Step 2: 🎯 Choose What You Need
            - **🖼️ Single Image** → One perfect marketing image
            - **🔄 A/B Testing** → Multiple versions to see what works best
            - **📱 Social Media** → Images sized for different platforms
            - **🤖 AI Assistant** → Let AI write the perfect prompt for you
            
            ### Step 3: 🎨 Create & Download
            Enter your details, click generate, and download your professional images!
            
            ---
            """)

            with gr.Row():
                with gr.Column():
                    gr.Markdown("""
                    ## 🖼️ Single Image
                    **Perfect for beginners!**
                    
                    ✨ **What it does:** Creates one professional marketing image
                    
                    🎯 **Best for:**
                    - Blog post headers
                    - Social media posts
                    - Product announcements
                    - Website banners
                    
                    💡 **How to use:**
                    1. Describe what you want
                    2. Pick a style (optional)
                    3. Click "Generate Image"
                    
                    **Example:** "Professional photo of a coffee cup on wooden table"
                    """)
                
                with gr.Column():
                    gr.Markdown("""
                    ## 🔄 A/B Testing Batch
                    **For optimizing performance**
                    
                    ✨ **What it does:** Creates 2-5 different versions to test
                    
                    🎯 **Best for:**
                    - Finding what your audience likes
                    - Improving engagement rates
                    - Testing different approaches
                    
                    💡 **How to use:**
                    1. Describe your content idea
                    2. Choose testing strategy
                    3. Post each version and see which performs best
                    
                    **Example:** Test different colors for your sale announcement
                    """)
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("""
                    ## 📱 Social Media Pack
                    **Multi-platform made easy**
                    
                    ✨ **What it does:** Creates perfectly sized images for each platform
                    
                    🎯 **Best for:**
                    - Cross-platform campaigns
                    - Consistent branding
                    - Saving time
                    
                    💡 **How to use:**
                    1. Describe your content
                    2. Check platforms you need
                    3. Get all sizes at once
                    
                    **Platforms:** Instagram, Twitter, LinkedIn, Facebook, YouTube
                    """)
                
                with gr.Column():
                    gr.Markdown("""
                    ## 🤖 AI Assistant
                    **Let AI do the thinking**
                    
                    ✨ **What it does:** Writes professional prompts for you
                    
                    🎯 **Best for:**
                    - When you're not sure how to describe what you want
                    - Getting professional results
                    - Learning better prompting
                    
                    💡 **How to use:**
                    1. Tell AI what you're creating in plain English
                    2. AI writes the perfect prompt
                    3. Generate your image
                    
                    **Example Input:** "I need a hero image for my water bottle business"
                    """)
            
            gr.Markdown("---")
            
            with gr.Accordion("🎯 Real-World Examples", open=False):
                gr.Markdown("""
                ## See What You Can Create
                
                ### 🛍️ E-commerce Business Owner
                **Need:** Product photos for online store
                **Use:** Single Image tab
                **Prompt:** "Professional product photography of [your product], white background, studio lighting"
                **Result:** Clean, professional product images
                
                ### 📱 Social Media Manager
                **Need:** Content that gets engagement
                **Use:** A/B Testing tab
                **Prompt:** "Eye-catching announcement for Black Friday sale"
                **Result:** 3-5 different versions to test which gets more likes/shares
                
                ### 🏢 Small Business Owner
                **Need:** Content for multiple platforms
                **Use:** Social Media Pack tab
                **Prompt:** "Grand opening celebration announcement"
                **Result:** Perfect sizes for Instagram, Facebook, Twitter, LinkedIn
                
                ### 🤔 First-Time User
                **Need:** Not sure how to describe what you want
                **Use:** AI Assistant tab
                **Input:** "I need marketing images for my yoga studio"
                **Result:** AI creates perfect prompts for you
                """)
            

            with gr.Accordion("💡 Tips for Amazing Results", open=False):
                gr.Markdown("""
                ## Make Your Images Stand Out
                
                ### ✅ Do This:
                - **Be specific:** "Red sports car in garage" vs "car"
                - **Mention the mood:** "professional," "fun," "elegant"
                - **Include details:** "wooden background," "bright lighting"
                - **Use style presets:** They make everything look more professional
                
                ### ❌ Avoid This:
                - Vague descriptions like "nice image"
                - Too many conflicting ideas in one prompt
                - Forgetting to mention important details
                
                ### 🎨 Style Guide:
                - **Professional:** For business, corporate, formal content
                - **Playful:** For fun brands, kids products, casual content
                - **Minimalist:** For clean, modern, simple designs
                - **Luxury:** For high-end products, premium brands
                - **Tech:** For software, apps, modern technology
                
                ### ⚡ Speed vs Quality:
                - **Quick test:** 30-40 steps (faster, good for trying ideas)
                - **Final image:** 70-100 steps (slower, best quality)
                """)
            

            with gr.Accordion("🔧 Common Issues & Solutions", open=False):
                gr.Markdown("""
                ## Troubleshooting Guide
                
                ### ❗ "MCP Server not connected"
                **Solution:** Wait 10-15 seconds after opening the app, then refresh the page
                
                ### ❗ "Timeout" errors
                **Solution:** The AI might be starting up - wait 30 seconds and try again
                
                ### ❗ Image quality is poor
                **Solution:** Increase the "Quality" slider to 70+ steps
                
                ### ❗ Image doesn't match what I wanted
                **Solution:** 
                - Be more specific in your description
                - Try the AI Assistant tab for better prompts
                - Use style presets
                
                ### ❗ Generation is too slow
                **Solution:** Lower the quality steps to 30-40 for faster results
                
                ### 💬 Still need help?
                - Check if your internet connection is stable
                - Try refreshing the page
                - Make sure you're being specific in your prompts
                """)
            
            gr.Markdown("""
            ---
            
            ## 🚀 Ready to Start?
            
            1. **Check the connection status** at the top of the page
            2. **Choose a tab** based on what you need to create
            3. **Start with simple prompts** and experiment
            4. **Have fun creating!** 🎨
            
            ---
            
            ### 🎯 Pro Tip for Beginners
            Start with the **🤖 AI Assistant** tab if you're unsure - it will guide you through creating the perfect prompt!
            """)
 
        with gr.TabItem("🖼️ Single Image"):
            with gr.Row():
                with gr.Column():
                    single_prompt = gr.Textbox(
                        label="Prompt",
                        placeholder="Describe your image in detail...\nExample: Professional headshot of business person in modern office",
                        lines=3
                    )
                    with gr.Row():
                        single_style = gr.Dropdown(
                            choices=["none", "professional", "playful",
                                     "minimalist", "luxury", "tech"],
                            value="none",
                            label="Style Preset",
                            info="Apply a consistent style to your image"
                        )
                        single_steps = gr.Slider(
                            10, 100, 50,
                            step=10,
                            label="Quality (Inference Steps)",
                            info="Higher = better quality but slower"
                        )
                    single_btn = gr.Button(
                        "🎨 Generate Image", variant="primary", size="lg")

                  
                    with gr.Accordion("💭 Example Ideas",open=False):
                        gr.Examples(
                            examples=[
                                ["""This poster is dominated by blue-purple neon lights, with the background of a hyper city at night, with towering skyscrapers surrounded by colorful LED light strips. In the center of the picture is a young steampunk modern robot with virtual information interfaces and digital codes floating around him. The future fonted title "CYNAPTICS" is in neon blue, glowing, as if outlined by laser, exuding a sense of technology and a cold and mysterious atmosphere. The small words "FUTURE IS NOW" seem to be calling the audience to the future, full of science fiction and trendy charm""", "professional", 50],
                                ["poster of,a white girl,A young korean woman pose with a white Vespa scooter on a sunny day,dressed in a stylish red and white jacket .inside a jacket is strapless,with a casual denim skirt. She wears a helmet with vintage-style goggles,and converse sneakers,adding a retro touch to her outfit. The bright sunlight highlights her relaxed and cheerful expression,and the Vespaâs white color pops against the clear blue sky. The background features a vibrant,sunlit scene with a few trees or distant buildings,creating a fresh and joyful atmosphere. Art style: realistic,high detail,vibrant colors,warm and cheerful.,f1.4 50mm,commercial photo style,with text around is 'Chasing the sun on my Vespa nothing but the open road ahead'", "playful", 40],
                                ["""Badminton is not just about winning, it’s about daring to challenge the limits of speed and precision. It’s a game where every strike is a test of reflexes, every point a moment of courage. To play badminton is to engage in a battle of endurance, strategy, and passion.""", "minimalist", 50],
                                ],
                            inputs=[single_prompt, single_style, single_steps],
                            label="Quick Examples"
                            )

                with gr.Column():
                    single_output = gr.Image(
                        label="Generated Image", type="filepath")
                    single_status = gr.Textbox(
                        label="Status", lines=3, interactive=False)

        with gr.TabItem("🔄 A/B Testing Batch"):
            gr.Markdown("""
                        ### Generate Strategic Variations for Testing
                        Create different versions that test specific elements to optimize your content performance.
                        Each variation tests a different hypothesis about what works best for your audience.
                        """)
            with gr.Row():
                with gr.Column():
                    batch_prompt = gr.Textbox(
                        label="Base Content Prompt",
                        placeholder="Describe your core content idea...\nExample: Professional announcement for new product launch",
                        lines=3
                    )
                    batch_variation_type = gr.Dropdown(
                        choices=[
                            ("🎨 Mixed Strategy (Recommended)", "mixed"),
                            ("🌈 Color Psychology Test", "color_schemes"),
                            ("📐 Layout & Composition Test", "composition_styles"),
                            ("😊 Emotional Tone Test", "emotional_tones"),
                            ("📱 Platform Optimization Test", "social_media"),
                            ("👁️ Attention-Grabbing Test", "engagement_hooks"),
                            ("🏷️ Brand Positioning Test", "brand_positioning")
                            ],
                        value="mixed",
                        label="Testing Strategy",
                        info="Choose what aspect you want to test"
                        )
                    with gr.Row():
                        batch_count = gr.Slider(
                            2, 5, 3,
                            step=1,
                            label="Number of Variations",
                            info="How many different versions to generate"
                            )
                        batch_steps = gr.Slider(
                            10, 100, 40,
                            label="Quality (Inference Steps)",info="Lower steps for quick testing")

                    batch_btn = gr.Button(
                        "🔄 Generate Variations", variant="primary", size="lg")
                    
                    strategy_info = gr.Markdown("""
                                                **💡 Current Strategy:** Mixed approach testing multiple variables
                                                **What this tests:** Different colors, layouts, and styles to find what works best
                                                **How to use results:** Post each variation and compare engagement metrics
                                                """)


                with gr.Column():
                    batch_output = gr.Gallery(
                        label="Generated Test Variations",
                        columns=2,
                        height="auto"
                    )
                    batch_status = gr.Textbox(
                        label="Variation Details", lines=6, interactive=False)
                    with gr.Accordion("📊 A/B Testing Guide",open=False):
                        gr.Markdown("""
                                **Step 1:** Generate variations above
                                **Step 2:** Post each variation to your platform
                                **Step 3:** Track these metrics for each:
                                - Engagement rate (likes, comments, shares)
                                - Click-through rate (if applicable)
                                - Reach and impressions
                                - Save/bookmark rate
                                
                                **Step 4:** Use the best performer for future content
                                
                                **💡 Pro Tips:**
                                - Test one element at a time for clear results
                                - Run tests for at least 7 days
                                - Use the same posting time and hashtags
                                - Need 1000+ views per variation for statistical significance
                                """)
      
        with gr.TabItem("📱 Social Media Pack"):
            gr.Markdown("""
            ### Generate Platform-Optimized Images
            Create perfectly sized images for multiple social media platforms at once.
            """)
            with gr.Row():
                with gr.Column():
                    social_prompt = gr.Textbox(
                        label="Content Prompt",
                        placeholder="Describe your social media content...\nExample: Exciting announcement for new product launch",
                        lines=3
                    )
                    social_platforms = gr.CheckboxGroup(
                        choices=[
                            ("Instagram Post (1080x1080)", "instagram_post"),
                            ("Instagram Story (1080x1920)", "instagram_story"),
                            ("Twitter Post (1200x675)", "twitter_post"),
                            ("LinkedIn Post (1200x1200)", "linkedin_post"),
                            ("Facebook Cover (1200x630)", "facebook_cover"),
                            ("YouTube Thumbnail (1280x720)", "youtube_thumbnail")
                        ],
                        value=["instagram_post", "twitter_post"],
                        label="Select Platforms",
                        info="Each platform will get an optimized image"
                    )
                    social_steps = gr.Slider(
                        10, 100, 50,
                        label="Quality (Inference Steps)"
                    )
                    social_btn = gr.Button(
                        "📱 Generate Social Pack", variant="primary", size="lg")

                with gr.Column():
                    social_output = gr.Gallery(
                        label="Platform-Optimized Images",
                        columns=2,
                        height="auto"
                    )
                    social_status = gr.Textbox(
                        label="Status", lines=4, interactive=False)

        with gr.TabItem("🤖 AI Prompt Assistant"):
            
            with gr.Column():
                gr.Markdown("### 🤖 AI-Powered Prompt Creation")
                with gr.Accordion("💡 How This Works", open=False):
                    gr.Markdown("""
                    **Simple 3-step process:**
                    1. Describe what you want in plain English
                    2. AI creates an optimized prompt  
                    3. Generate your professional image
                    """)
            
           
            with gr.Row():
                
                with gr.Column(scale=1, min_width=300):
                    ai_user_input = gr.Textbox(
                        label="What do you want to create?",
                        placeholder="Example: A hero image for my new eco-friendly water bottle product launch",
                        lines=4,
                        info="Describe your vision in plain language"
                    )
                    
                    with gr.Group():
                        gr.Markdown("#### Settings")
                        
                        ai_context = gr.Dropdown(
                            choices=[
                                ("General Marketing", "marketing"),
                                ("Product Photography", "product"),
                                ("Social Media Post", "social"),
                                ("Blog/Article Header", "blog"),
                                ("Event Promotion", "event"),
                                ("Brand Identity", "brand")
                            ],
                            value="marketing",
                            label="Content Type",
                            info="What are you creating?"
                        )
                        ai_style = gr.Dropdown(
                            choices=[
                                ("Professional", "professional"),
                                ("Playful & Fun", "playful"),
                                ("Minimalist", "minimalist"),
                                ("Luxury", "luxury"),
                                ("Tech/Modern", "tech"),
                                ("Natural/Organic", "natural")
                            ],
                            value="professional",
                            label="Style",
                            info="What mood to convey?"
                        )
                        ai_platform = gr.Dropdown(
                            choices=[
                                ("General Use", "general"),
                                ("Instagram", "instagram"),
                                ("Twitter/X", "twitter"),
                                ("LinkedIn", "linkedin"),
                                ("Facebook", "facebook"),
                                ("Website Hero", "website")
                            ],
                            value="general",
                            label="Platform",
                            info="Where will this be used?"
                        )
                    

                    ai_generate_btn = gr.Button(
                        "🤖 Generate AI Prompt", 
                        variant="primary", 
                        size="lg",
                        scale=1
                    )
                    
                    
                    with gr.Accordion("💭 Example Ideas", open=False):
                        gr.Examples(
                            examples=[
                                ["A hero image for my new eco-friendly water bottle", "product", "natural", "website"],
                                ["Announcement for our Black Friday sale", "social", "playful", "instagram"],
                                ["Professional headshots for company about page", "marketing", "professional", "linkedin"],
                                ["Blog header about AI in marketing", "blog", "tech", "general"],
                                ["Product showcase for luxury watch collection", "product", "luxury", "instagram"]
                            ],
                            inputs=[ai_user_input, ai_context, ai_style, ai_platform],
                            label=None
                        )

 
                with gr.Column(scale=1, min_width=300):
                    ai_generated_prompt = gr.Textbox(
                        label="AI-Generated Prompt",
                        lines=6,
                        interactive=True,
                        info="Edit this prompt if needed"
                    )
                    
                    ai_status = gr.Textbox(
                        label="Status",
                        lines=2,
                        interactive=False
                    )
                    

                    with gr.Row():
                        ai_use_prompt_btn = gr.Button(
                            "🎨 Generate Image", 
                            variant="primary",
                            scale=2
                        )
                        ai_save_prompt_btn = gr.Button(
                            "💾 Save to Single Tab", 
                            variant="secondary",
                            scale=1
                        )
                    

                    with gr.Accordion("🔧 Advanced Prompt Refinement", open=False):
                        ai_improvement_request = gr.Textbox(
                            label="How to improve this prompt?",
                            placeholder="Example: Add more dramatic lighting, make it more colorful, include people",
                            lines=2
                        )
                        ai_improve_btn = gr.Button(
                            "✨ Improve Prompt", 
                            variant="secondary",
                            size="sm"
                        )
                    

                    ai_preview_image = gr.Image(
                        label="Generated Image Preview",
                        type="filepath",
                        visible=False,
                        height=300
                    )
            
  
            with gr.Accordion("🎯 Pro Tips for Better Results", open=False):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("""
                        **Be Specific About:**
                        - **Subject**: What's the main focus?
                        - **Setting**: Where is it happening?
                        - **Mood**: What feeling to convey?
                        - **Colors**: Any specific palette?
                        """)
                    with gr.Column():
                        gr.Markdown("""
                        **Good Examples:**
                        - ✅ "Minimalist product photo of smartphone on marble"
                        - ✅ "Vibrant Instagram post for summer sale"
                        - ❌ "Product photo" (too vague)
                        - ❌ "Social media post" (not specific)
                        """)

    # Footer
    gr.Markdown("""
    ---
    ### 🛠️ Powered by:
    - **Flux AI Model** - State-of-the-art image generation
    - **Modal Labs** - GPU infrastructure
    - **AI Prompt Assistant** - Mistral
    - **MCP Protocol** - Tool integration
    - **Gradio** - User interface
    
    Made by RajputVansh
    
    Member of Cynaptics Cub, IIT Indore, India
    
    **Made with ❤️ for content creators and marketers**
    """)

    # Event handlers
    single_btn.click(
        single_image_generation,
        inputs=[single_prompt, single_steps, single_style],
        outputs=[single_output, single_status]
    )

    batch_btn.click(
        enhanced_batch_generation,
        inputs=[batch_prompt,batch_variation_type, batch_count, batch_steps],
        outputs=[batch_output, batch_status]
    )
    batch_variation_type.change(
        update_strategy_info,
        inputs=[batch_variation_type],
        outputs=[strategy_info]
        )

    social_btn.click(
        social_media_generation,
        inputs=[social_prompt, social_platforms, social_steps],
        outputs=[social_output, social_status]
    )


    def generate_ai_prompt(user_input, context, style, platform):
        """Generate an optimized prompt using AI"""
        if not marketing_tool.is_connected:
            return "", "⚠️ MCP Server not connected. Please wait a few seconds and try again."

        if not user_input.strip():
            return "", "⚠️ Please describe what you want to create."

        try:
            request_id = f"ai_prompt_{time.time()}"
            marketing_tool.request_queue.put((
                "generate_prompt_with_ai",
                {
                    "user_input": user_input,
                    "context": context,
                    "style": style,
                    "platform": platform
                    },
                request_id
                ))
            status, result = wait_for_result(request_id, timeout=60)
            if status == "success":
                result_data = json.loads(result)
                if result_data.get("success"):
                    return result_data["prompt"], "✅ AI prompt generated successfully!"
                else:
                    return result_data.get("fallback_prompt", ""), f"⚠️ Using fallback prompt: {result_data.get('error', 'Unknown error')}"
            else:
                return "", f"❌ Error: {result}"
        except Exception as e:
            return "", f"❌ Error: {str(e)}"
    ai_generate_btn.click(
        generate_ai_prompt,
        inputs=[ai_user_input, ai_context, ai_style, ai_platform],
        outputs=[ai_generated_prompt, ai_status]
    )
    
    def improve_ai_prompt(current_prompt, improvement_request):
        if not marketing_tool.is_connected:
            return current_prompt, "⚠️ MCP Server not connected."
        if not current_prompt.strip():
            return "", "⚠️ No prompt to improve. Generate one first."
        if not improvement_request.strip():
            return current_prompt, "⚠️ Please describe how you'd like to improve the prompt."
        try:
            enhanced_base = f"{current_prompt}. {improvement_request}"
            request_id = f"improve_prompt_{time.time()}"
            marketing_tool.request_queue.put((
                "enhance_prompt_with_details",  # Use the same tool
                {
                    "base_prompt": enhanced_base,
                    "enhancement_type": "detailed"
                    },
                request_id
                ))
            status, result = wait_for_result(request_id, timeout=60)
            if status == "success":
                if not result:
                    return current_prompt, "⚠️ Received empty response from server."
                try:
                    result_data = json.loads(result)
                    if result_data.get("success"):
                        return result_data["enhanced_prompt"], "✅ Prompt improved successfully!"
                    else:
                        return current_prompt, f"⚠️ Could not improve prompt: {result_data.get('error', 'Unknown error')}"
                except json.JSONDecodeError as json_error:
                    print(f"JSON decode error: {json_error}")
                    print(f"Raw result: {repr(result)}")
                    return result if result else current_prompt, "✅ Prompt improved (received as text)!"
                
            else:
                return current_prompt, f"❌ Error: {result}"
            
        except Exception as e:
            print(f"Exception in improve_ai_prompt: {str(e)}")
            return current_prompt, f"❌ Error: {str(e)}"
        
    ai_improve_btn.click(
        improve_ai_prompt,
        inputs=[ai_generated_prompt, ai_improvement_request],
        outputs=[ai_generated_prompt, ai_status]
    )
    
    def generate_image_from_ai_prompt(prompt, show_preview=True):
        if not prompt.strip():
            return None, "⚠️ Please generate a prompt first."
        image_path, status = single_image_generation(prompt, 50, "none")
        if show_preview and image_path:
            return gr.update(value=image_path, visible=True), status
        else:
            return gr.update(visible=False), status
        
    ai_use_prompt_btn.click(
        lambda prompt: generate_image_from_ai_prompt(prompt, True),
        inputs=[ai_generated_prompt],
        outputs=[ai_preview_image, ai_status]
    )
    ai_save_prompt_btn.click(
        lambda prompt: (prompt, "✅ Prompt copied to Single Image tab!"),
        inputs=[ai_generated_prompt],
        outputs=[single_prompt, ai_status]
    ).then(
        lambda: gr.update(selected="🖼️ Single Image"),
        outputs=[]
    )

    # Update connection status
    def update_connection_status():
        if marketing_tool.is_connected:
            return "✅ **Connected to MCP Server** - Ready to generate!"
        else:
            return "🔄 Connecting to MCP server... (please wait)"

    # Periodic status update
    demo.load(update_connection_status, outputs=[connection_status])

if __name__ == "__main__":
    print("Starting Marketing Content Generator...")
    print("Please wait for MCP server to initialize...")
    start_mcp_server()
    time.sleep(5)
    print("Launching Gradio interface...")
    demo.launch(share=False, mcp_server=True)
