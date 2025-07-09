# LLM-GISX: AI-Driven GIS Platform for Renewable Energy Planning

**LLM-GISX** is a unified AI + GIS platform designed to help ministries, farmers, and planners identify optimal renewable energy sites across India. The system integrates a large language model with geospatial intelligence, offering an intuitive interface for spatial analysis, interaction, and report generation — without requiring GIS expertise.

This monorepo contains:

- `backend/` – LLM-powered geospatial processing and report generation
- `frontend/` – React-based client with map interaction, voice/text queries, and multilingual support

---

## Developed for Bharatiya Antariksh Hackathon 2025

This project was built for the **Bharatiya Antariksh Hackathon 2025**, organized by the **Indian Space Research Organisation (ISRO)** in collaboration with **Hack2skill**. The problem statement invited participants to design a system that uses **Chain-of-Thought (CoT) reasoning in Large Language Models** to orchestrate complex geospatial workflows.

### Problem Statement

> **Title**: Designing a Chain-of-Thought-Based LLM System for Solving Complex Spatial Analysis Tasks Through Intelligent Geoprocessing Orchestration

The challenge was to create an AI system that can automatically plan and execute GIS workflows (like flood risk assessment, site suitability, or land cover analysis) based on natural language queries — much like a human GIS expert.

---

## Our Solution: LLM-GISX

**LLM-GISX** automates complex geospatial workflows using LLM reasoning, step-by-step geoprocessing, and multi-source data integration. The system generates Chain-of-Thought (CoT) logs, visual outputs, and structured workflows.

### Output Includes:

- Geospatial workflows (in JSON format)
- Transparent Chain-of-Thought logs
- Visual map outputs for bounding boxes or TIFF uploads
- Downloadable reports (PDF) for ministries or farmers
- Language-specific voice/text interaction with AI assistant

---

## Overview of Use Cases

- **Government Ministries**: Analyze large regions, get legally compliant reports
- **Farmers**: Interact with the system via voice in their local language to access insights
- **Researchers/Planners**: Upload GIS data, draw bounding boxes, and explore map overlays

---

## Frontend (Located in `/frontend`)

### Tech Stack

| Area            | Technology                                |
|-----------------|-------------------------------------------|
| Framework       | React + Vite                              |
| Styling         | Tailwind CSS, shadcn/ui                   |
| GIS Engine      | OpenLayers                                |
| Routing         | React Router                              |
| Voice Input     | Web Speech API                            |
| Icons           | Lucide                                    |

### Features

- **Authentication**: Email-password for ministries, mobile-OTP for farmers
- **Voice + Text AI Chat**: Multilingual interaction with the LLM
- **Interactive Mapping**: Draw bounding boxes or upload `.tif` files
- **Report Downloads**: Auto-generated PDF summaries based on region and use case
- **Language Selector**: Supports 15+ Indian languages for accessibility

Made by @sneharc16, @shivya0410 and @dhruv-developer

---

## Getting Started (Frontend)

```bash
# Clone the repository
git clone https://github.com/sneharc16/LLM-GISx-New.git
cd LLM-GISx-New/frontend

# Install dependencies
npm install

# Run the development server
npm run dev

# Open in browser
http://localhost:5173
