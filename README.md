# AI Marketing Content Creator 🎨

Generate professional marketing images with AI using FLUX.1-schnell. Perfect for content creators, marketers, and social media managers!

![AI Marketing Content Creator](https://img.shields.io/badge/AI-Marketing-blue)
![FLUX.1](https://img.shields.io/badge/FLUX.1-schnell-green)
![Modal Labs](https://img.shields.io/badge/Modal-Labs-purple)
![GPU](https://img.shields.io/badge/GPU-H200-red)

## ✨ Features

### 🎯 Individual Marketing Assets
- Create professional marketing images with AI
- Apply professional style presets
- Optimized prompts for marketing content
- Generate multiple variations of the same concept

### 🔄 A/B Testing Support
- Compare different approaches
- Perfect for testing engagement
- Generate variations for optimization

### 📱 Platform Optimization
- Generate platform-optimized images
- Support for Instagram, Twitter, LinkedIn, Facebook, YouTube
- Correct aspect ratios for each platform

### 🎨 Pre-built Templates
- Product photography templates
- Social media announcements
- Blog headers and banners
- Easy variable substitution

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Modal Labs account
- Hugging Face account and token

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
   export HF_TOKEN="your_hugging_face_token"
   export MODAL_TOKEN_ID="your_modal_token_id"
   export MODAL_TOKEN_SECRET="your_modal_token_secret"
   ```

### Usage

1. **Choose Your Task**: Select the appropriate generation mode
2. **Enter Your Prompt**: Be specific about what you want
3. **Adjust Settings**: Configure style and quality options
4. **Generate**: Click the button and wait for results

## 🏗️ Architecture

### Backend (Modal Labs + H200 GPU)
The project uses Modal Labs infrastructure with H200 GPUs for high-performance image generation:

```
src/
├── modal_server.py          # Main Modal Labs backend server
└── ...
```

**Key Features:**
- **GPU**: NVIDIA H200 for ultra-fast inference
- **Model**: FLUX.1-schnell optimized for speed
- **Scalability**: Auto-scaling infrastructure
- **Performance**: 10-30 seconds per image generation

### MCP Server Integration
The project includes a Model Context Protocol (MCP) server for enhanced AI integration:

```
mcp_server.py                # MCP server implementation
```

### Frontend
- **Framework**: Gradio for user-friendly interface
- **Real-time**: Live preview and generation
- **Responsive**: Works on desktop and mobile

## 📊 Platform Specifications

| Platform | Resolution | Aspect Ratio |
|----------|------------|--------------|
| Instagram Post | 1024×1024 | 1:1 |
| Instagram Story | 1024×1820 | 9:16 |
| Twitter Post | 1200×675 | 16:9 |
| LinkedIn Post | 1200×1200 | 1:1 |
| Facebook Cover | 1200×630 | 1.91:1 |
| YouTube Thumbnail | 1280×720 | 16:9 |

## 💡 Pro Tips

### Prompt Engineering
- **Be Specific**: "Red sports car on mountain road at sunset" > "car"
- **Use Style Presets**: Apply consistent branding with style options
- **Leverage Templates**: Use pre-built templates for faster results

### Optimization
- **FLUX.1-schnell**: Works best with 1-4 inference steps
- **Batch Processing**: Generate multiple variations simultaneously
- **A/B Testing**: Test different approaches to find what works best

## 🔧 Technical Details

### AI Model
- **Model**: FLUX.1-schnell (Schwarzer Labs)
- **Backend**: Modal Labs with H200 GPU
- **API**: Hugging Face Diffusers + Inference API
- **Inference Steps**: 1-4 (optimized for speed)

### Performance
- **Generation Time**: 10-30 seconds per image
- **Hardware**: NVIDIA H200 GPU via Modal Labs
- **Scalability**: Auto-scaling based on demand
- **Availability**: 99.9% uptime

### Integration
- **MCP Server**: Enhanced AI model integration
- **API**: RESTful API for external integrations
- **Webhooks**: Real-time notifications

## 🛠️ Development Setup

### Local Development

1. **Install Modal CLI**
   ```bash
   pip install modal
   modal token new
   ```

2. **Deploy to Modal**
   ```bash
   modal deploy src/modal_server.py
   ```

3. **Run MCP Server**
   ```bash
   python mcp_server.py
   ```

4. **Start Frontend**
   ```bash
   python app.py
   ```

### Environment Variables

```bash
# Hugging Face
HF_TOKEN=your_hugging_face_token

# Modal Labs
MODAL_TOKEN_ID=your_modal_token_id
MODAL_TOKEN_SECRET=your_modal_token_secret

# Optional
REDIS_URL=your_redis_url
DEBUG=true
```

## 📝 Example Prompts

### Product Photography
```
Professional product photography of wireless headphones, white background, studio lighting, commercial style
```

### Social Media
```
Vibrant Instagram post announcing summer sale, bold colors, modern design, eye-catching
```

### Blog Content
```
Minimalist blog header about productivity tips, clean design, professional, engaging
```

## 🚀 Deployment

### Modal Labs Deployment

1. **Configure Modal**
   ```bash
   modal config set-up
   ```

2. **Deploy Backend**
   ```bash
   modal deploy src/modal_server.py
   ```

3. **Set Secrets**
   ```bash
   modal secret create huggingface-secret HF_TOKEN=your_token
   ```

### Hugging Face Spaces

1. **Fork this Space** or create a new one
2. **Set Environment Variables**: `HF_TOKEN`
3. **Choose Hardware**: CPU (free) or GPU (faster)
4. **Deploy**: Push your changes

## 🤝 Contributing

Issues and pull requests welcome! Help make this tool even better for the marketing community.

### Development Guidelines
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FLUX.1-schnell**: Schwarzer Labs for the amazing AI model
- **Modal Labs**: For providing H200 GPU infrastructure
- **Hugging Face**: For model hosting and inference APIs
- **Gradio**: For the intuitive frontend framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ThunderBolt4931/AI-Marketing-Content-Creator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ThunderBolt4931/AI-Marketing-Content-Creator/discussions)
- **Email**: [Contact Support](mailto:support@example.com)

---

Made with ❤️ for content creators and marketers

**Powered by**: FLUX.1-schnell, Modal Labs H200 GPU, Hugging Face, and Gradio
