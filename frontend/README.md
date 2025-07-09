# LLM-GISX Frontend

Welcome to the **LLM-GISX Frontend**, a user-first AI + GIS platform that empowers ministries, farmers, and planners to intelligently identify renewable energy sites across India.

This frontend interfaces with an LLM-powered geospatial engine, allowing users to chat, draw bounding boxes, analyze maps, view reports, and even speak in their native languages — all without needing GIS expertise.

---

## 🌏 What Is This?

**LLM-GISX** helps India transition toward **Net Zero** by making renewable energy planning accessible and automated. It supports:

- **Ministry Users:** Access detailed geospatial site reports with cost, environmental checks, and legal compliance.
- **Farmers:** Ask agricultural queries via voice or text, in regional languages, and get AI-powered insights.
- **Map Analysis:** Draw bounding boxes, upload TIFF files, and view optimized energy zones.
- **Reports:** Download submission-ready PDFs or email outputs directly.

This is the frontend client built with **React + TypeScript + TailwindCSS**, and designed to integrate with a powerful backend AI+GIS agent.

---

## 🧠 Tech Stack

| Area         | Technology                                     |
|--------------|------------------------------------------------|
| Framework    | React + Vite                                   |
| UI Library   | TailwindCSS, shadcn/ui                         |
| State & Hooks| React Hooks                                    |
| GIS Engine   | OpenLayers                                     |
| AI & Voice   | Chat-based LLM interaction, Web Speech API     |
| Routing      | React Router                                   |
| Icons        | Lucide                                         |
| Styling      | Custom theme: Green & White (Earth-safe palette) |

---

## 🚀 Features

### ✅ Authentication
- **Ministry:** Email + password login (no signup)
- **Farmer:** Mobile-based signup/login with multilingual voice/text support

### 🗣️ Chat Assistant
- Ask about renewable energy sites, crops, weather, etc.
- Works in both English and native Indian languages
- Voice-enabled for farmers

### 🗺️ Interactive Map
- Draw bounding box to select area
- Upload `.tif` files for analysis
- View optimized site points and recommendations

### 📊 Reports & Summary
- Auto-generated reports with lat/lon, cost, and growth projections
- Ministry users can download or email outputs
- Farmer users can visually explore results

### 🌐 Language Selector
- Supports over 15+ Indian languages
- Text-to-speech feedback
- Designed for low-literacy and rural users

---

## ⚙️ Getting Started

```bash
# 1. Clone the repository
git clone [https://github.com/your-org/llm-gisx-frontend.git](https://github.com/dhruv-developer/LLM-GISX-Frontend
cd llm-gisx-frontend

# 2. Install dependencies
npm install

# 3. Run the dev server
npm run dev

# 4. Open in browser
http://localhost:5173


Folder Structure
bash
Copy
Edit
/src
├── components         # UI and logic (ChatBot, MapView, Dashboard)
├── context            # Auth context for protected routes
├── api                # API calls to backend
├── hooks              # Reusable hooks (e.g. toast)
├── pages              # Route-level pages (Dashboard, Landing)
├── assets             # Static files, icons, etc.
├── App.tsx            # Main app entry
├── main.tsx           # Bootstrap file


Made by @sneharc16, @shivya0410 and @dhruv-developer
