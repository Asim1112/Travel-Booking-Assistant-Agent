# 🧳 Travel Booking Assistant Agent

An AI-powered **Travel Booking Assistant** built with the **OpenAI Agents SDK** that helps users plan and book flights & hotels while ensuring safe and relevant responses through **input and output guardrails**.

---

## 📌 Features

- **Flight Search** – Get real-time flight options (will be shown in tables in future updates).
- **Hotel Search** – Explore accommodation options tailored to your preferences.
- **Context Awareness** – Stores user profile details such as:
  - Name
  - Age
  - Preferred city
  - Budget
  - Travel history
- **Guardrails Integration**:
  - **Input Guardrails** – Block requests for illegal destinations, offensive, or irrelevant messages.
  - **Output Guardrails** – Block medical/legal advice and booking confirmations without showing total cost first.
- **Multi-Agent Setup**:
  - Main Agent → `gemini-2.5-flash`
  - Guardrail Agents → `gemini-2.0-flash`

---

## 🛠️ Tech Stack

- **Language:** Python
- **Framework:** OpenAI Agents SDK
- **Model Providers:** Gemini
- **Tools & Libraries:**  
  - `dotenv` – Environment variable management  
  - `tabulate` *(future)* – For displaying results in tables

---

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Asim1112/Travel-Booking-Assistant-Agent.git
   cd travel-booking-agent

## Developed by Asim Hussain
### An AI Entrprenuer | Agentic AI SDK Expert | Web developer | Mastered in Python, TypeScript, Next.JS
***Linkedin Profile:** www.linkedin.com/in/asim-hussain-5429252b8 


