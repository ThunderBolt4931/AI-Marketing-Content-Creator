# 🎨 AI Marketing Content Creator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Gradio](https://img.shields.io/badge/Gradio-UI-orange.svg)](https://gradio.app)
[![Modal](https://img.shields.io/badge/Modal-GPU-green.svg)](https://modal.com)
[![MCP](https://img.shields.io/badge/MCP-Protocol-purple.svg)](https://modelcontextprotocol.io)

> **Professional AI-powered marketing image generation tool** - Create stunning marketing visuals in minutes, not hours!

Generate high-quality marketing images using state-of-the-art Flux AI model running on Modal Labs H200 GPUs. Perfect for content creators, marketers, and businesses who need professional visuals without design expertise.

## ✨ Features

### 🖼️ **Single Image Generation**
- Create professional marketing images with detailed prompts
- Multiple style presets (Professional, Playful, Minimalist, Luxury, Tech)
- Adjustable quality settings for speed vs quality trade-offs

### 🔄 **A/B Testing Batch Generation**
- Generate 2-5 strategic variations for performance testing
- Multiple testing strategies:
  - 🎨 Mixed Strategy (colors, layout, mood)
  - 🌈 Color Psychology Testing
  - 📐 Layout & Composition Testing
  - 😊 Emotional Tone Testing
  - 📱 Platform Optimization
  - 👁️ Attention-Grabbing Testing
  - 🏷️ Brand Positioning Testing

### 📱 **Social Media Pack**
- Generate platform-optimized images in one click
- Perfect sizing for:
  - Instagram Post (1080x1080)
  - Instagram Story (1080x1920)
  - Twitter Post (1200x675)
  - LinkedIn Post (1200x1200)
  - Facebook Cover (1200x630)
  - YouTube Thumbnail (1280x720)

### 🤖 **AI Prompt Assistant**
- Let AI write professional prompts for you
- Context-aware prompt generation
- Support for different content types and platforms
- Prompt improvement and refinement

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Modal Labs account with GPU access
- Mistral API key (for AI assistant)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ThunderBolt4931/AI-Marketing-Content-Creator.git
cd AI-Marketing-Content-Creator
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
export MISTRAL_API_KEY="your_mistral_api_key"
export MODAL_API_URL="your_modal_api_url"
```

4. **Deploy Modal backend**
```bash
cd src
modal deploy modal_server.py
```

5. **Run the application**
```bash
python app.py
```

6. **Open your browser**
   - Navigate to `http://localhost:7860`
   - Wait 5-10 seconds for MCP server connection

## 🏗️ Architecture

```
AI-Marketing-Content-Creator/
├── app.py                  # Main Gradio application
├── mcp_server.py          # MCP protocol server
├── src/
│   └── modal_server.py    # Modal Labs GPU backend
├── created_image/         # Generated images output
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### System Architecture

```
graph TD
    A[Gradio UI] --> B[MCP Server]
    B --> C[Modal Labs H200 GPU]
    C --> D[Flux AI Model]
    D --> E[Generated Images]
    E --> F[Local Storage]
    
    G[AI Assistant] --> H[Mistral API]
    H --> I[Optimized Prompts]
    I --> B
```

## 🛠️ Technology Stack

- **Frontend**: Gradio - Interactive web interface
- **Backend**: Modal Labs - GPU infrastructure with H200 GPUs
- **AI Model**: Flux AI - State-of-the-art image generation
- **Protocol**: MCP (Model Context Protocol) - Tool integration
- **AI Assistant**: Mistral API - Intelligent prompt generation
- **Image Processing**: PIL/Pillow - Image manipulation

## 📋 Usage Examples

### Basic Image Generation
```python
# Simple product photo
prompt = "Professional product photography of eco-friendly water bottle, white background, studio lighting"

# Marketing announcement
prompt = "Eye-catching Black Friday sale announcement, bold colors, modern design"

# Social media content
prompt = "Instagram-style flat lay of coffee and laptop, cozy aesthetic, warm lighting"
```

### A/B Testing Strategy
```python
# Test different approaches for the same content
base_prompt = "New product launch announcement"
strategy = "color_schemes"  # Test different color psychology
variations = 3  # Generate 3 different versions
```

### AI-Assisted Prompting
```python
# Let AI create the perfect prompt
user_input = "I need a hero image for my yoga studio website"
context = "brand"
style = "natural"
platform = "website"
# AI generates optimized prompt automatically
```

## 🎯 Best Practices

### For Better Results
- **Be specific**: "Red sports car in modern garage" vs "car"
- **Include mood**: "professional," "friendly," "elegant"
- **Mention setting**: "studio lighting," "outdoor setting"
- **Use style presets**: They ensure consistent professional look

### For A/B Testing
- Test one element at a time for clear results
- Run tests for at least 7 days
- Use same posting time and hashtags
- Need 1000+ views per variation for statistical significance

### Quality vs Speed
- **Quick testing**: 30-40 steps (faster, good for iteration)
- **Final production**: 70-100 steps (slower, best quality)

## 📁 File Structure Details

### `app.py`
Main application file containing:
- Gradio interface setup
- MCP client integration
- Image processing functions
- UI event handlers

### `mcp_server.py`
MCP protocol server providing:
- Tool definitions and implementations
- Modal API integration
- Image generation orchestration

### `src/modal_server.py`
Modal Labs backend featuring:
- Flux AI model deployment
- GPU-accelerated inference
- Image generation and processing
- API endpoint management

## 🔧 Configuration

### Environment Variables
```bash
# Required
MISTRAL_API_KEY=your_mistral_api_key_here
MODAL_API_URL=your_modal_deployment_url

# Optional
MODAL_TOKEN_ID=your_modal_token_id
MODAL_TOKEN_SECRET=your_modal_token_secret
```

### Modal Configuration
Update `src/modal_server.py` with your specific requirements:
- GPU type (H100, H200, A100)
- Model versions
- Timeout settings
- Resource limits

## 🚨 Troubleshooting

### Common Issues

**"MCP Server not connected"**
- Wait 10-15 seconds after launching
- Check if Modal deployment is running
- Verify environment variables

**"Timeout" errors**
- Modal GPU might be cold starting
- Wait 30 seconds and retry
- Check Modal logs for issues

**Poor image quality**
- Increase inference steps to 70+
- Use more specific prompts
- Try different style presets

**Slow generation**
- Reduce inference steps to 30-40
- Check Modal GPU availability
- Verify internet connection

### Debug Mode
Enable debug logging:
```bash
export DEBUG=1
python app.py
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Code formatting
black app.py mcp_server.py
```

## 📊 Performance Metrics

- **Average generation time**: 15-30 seconds
- **Supported image sizes**: Up to 1920x1920
- **Concurrent users**: 10+ (depending on Modal scaling)
- **Success rate**: 95%+ for valid prompts

## 🔒 Security & Privacy

- Images are generated on-demand and stored locally
- No persistent storage of user prompts
- Modal Labs provides enterprise-grade security
- API keys are handled securely

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Modal Labs** - GPU infrastructure and deployment platform
- **Flux AI** - State-of-the-art image generation model
- **Gradio** - Excellent UI framework for ML applications
- **MCP Protocol** - Tool integration standard
- **Mistral** - AI assistant capabilities

## 👨‍💻 Author

**RajputVansh**
- Member of Cynaptics Club, IIT Indore, India
- GitHub: [@ThunderBolt4931](https://github.com/ThunderBolt4931)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ThunderBolt4931/AI-Marketing-Content-Creator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ThunderBolt4931/AI-Marketing-Content-Creator/discussions)
- **Email**: [Contact via GitHub](https://github.com/ThunderBolt4931)

---

**Made with ❤️ for content creators and marketers worldwide**

*Transform your marketing visuals with the power of AI - because great content shouldn't require great design skills!*
