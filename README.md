# 🤖 Shashank ChatBot – AI-Powered Web Assistant with Local LLMs

**Shashank ChatBot** is a secure, intelligent chatbot web application built using Flask that can **answer user prompts**, **generate images**, and **describe uploaded photos** — all powered by **local LLaMA 3 via Ollama**, **Stable Diffusion**, and **BLIP image captioning**. With user authentication and admin dashboard, it provides a complete AI-augmented web experience.
 
**LLM Model**: [LLaMA 3 via Ollama](https://ollama.com/library/llama3)  
**Image Model**: Stable Diffusion v1.5  
**Captioning Model**: BLIP (Salesforce)

---

## 🚀 Features

###  AI Chat Interface
- Prompts sent to **local LLaMA 3 model** (via `ollama run llama3`)
- Responses shown in real time

###  Image Generation
- Enter `image: <your prompt>` to generate a custom image
- Powered by Stable Diffusion v1.5

###  Image Upload & Description
- Upload an image → get a detailed caption using BLIP
- Automatically generates a similar image

###  Authentication System
- User **Registration/Login**
- Chats saved per user
- Sessions managed securely

###  Admin Dashboard
- View all users & chats
- Search chats by user
- Delete users and their chat histories

---

##  Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Python, Flask, Flask-SQLAlchemy, Flask-Login |
| **LLMs & AI** | LLaMA 3 (Ollama), Stable Diffusion, BLIP (Salesforce) |
| **Frontend** | HTML5, CSS3, Bootstrap, Jinja2 |
| **Database** | SQLite |
| **Deployment** | Localhost (can be deployed via Render/Heroku) |

---

##  Project Structure

```bash
chatbot-code/
├── app.py                  # Main Flask app
├── models.py               # SQLAlchemy models
├── forms.py                # User login & registration forms
├── utils/
│   └── local_llm.py        # LLaMA, BLIP, and Stable Diffusion logic
├── templates/              # HTML templates
├── static/                 # CSS, JS, and generated images
├── uploads/                # Uploaded images (user input)
├── requirements.txt
└── README.md               # You're here!

**How to Run Locally
Prerequisites
Python 3.9+
Ollama installed with LLaMA 3 model (ollama run llama3)
pip + virtualenv (recommended)
CUDA-enabled GPU (for Stable Diffusion performance)**
