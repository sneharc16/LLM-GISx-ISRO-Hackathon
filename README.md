# LLM-GISX: AI-Powered Geospatial Intelligence for Sustainable Site Planning

**LLM-GISX** is an end-to-end AI + GIS platform designed to democratize geospatial intelligence for ministries, planners, and grassroots users like farmers. It enables intuitive natural language interaction with complex spatial datasets — eliminating the need for GIS expertise.

Built on top of advanced Large Language Models (LLMs) and modern geospatial processing libraries, the system interprets user queries, reasons through multi-step geoprocessing logic (Chain-of-Thought), and generates actionable insights and downloadable reports.

This monorepo contains:

- `backend/` – LLM-driven reasoning engine, geospatial pipeline executor, and CoT logger
- `frontend/` – Responsive React-based interface with map interaction, chat assistant, voice input, and multilingual capabilities

---

## Developed for Bharatiya Antariksh Hackathon 2025

This project was developed as part of the **Bharatiya Antariksh Hackathon 2025**, a nationwide innovation challenge hosted by the **Indian Space Research Organisation (ISRO)** and facilitated by **Hack2skill**.

---

### Problem Statement

> **Title**: Designing a Chain-of-Thought-Based LLM System for Solving Complex Spatial Analysis Tasks Through Intelligent Geoprocessing Orchestration

The challenge asked participants to create a system that could perform reasoning-driven geospatial analysis from natural language queries. Tasks like flood risk mapping or site suitability assessment typically require manual orchestration of complex GIS workflows — a process that demands expertise and time.

The objective was to **build an LLM-powered system capable of:**

- Interpreting spatial queries in natural language
- Generating multi-step geospatial workflows
- Selecting appropriate tools, parameters, and data sources
- Producing output maps, structured plans, and reasoning trails

---

## Our Approach: LLM-GISX

**LLM-GISX** addresses this problem by leveraging the reasoning power of modern LLMs in combination with robust geospatial processing libraries and user-friendly interfaces.

### System Outputs

- Structured multi-step workflows (JSON/YAML)
- Transparent Chain-of-Thought logs for traceability
- Visual map outputs from raster/vector inputs
- Region-specific recommendations and analysis summaries
- Downloadable PDF reports for planners and ministries
- Multilingual voice/text chat for rural accessibility

---

## Key Use Cases

- **Policy Makers / Ministries**: Request large-scale renewable siting reports with legal and environmental overlays
- **Planners & GIS Analysts**: Upload shapefiles or TIFFs, draw bounding boxes, and get LLM-generated workflows
- **Farmers**: Speak in their native language and receive personalized agri-advisory insights and energy recommendations

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

### Key Features

- **Role-Based Login**: Email-password for ministries; OTP for farmers
- **Multilingual LLM Chat**: Text and voice input in 15+ Indian languages
- **Map Tools**: Draw bounding boxes, upload `.tif` geospatial files
- **Report Generator**: PDF exports with coordinates, cost, and impact
- **Accessibility-First Design**: Support for rural and low-literacy users

> Developed by [@sneharc16](https://github.com/sneharc16), [@shivya0410](https://github.com/shivya0410), and [@dhruv-developer](https://github.com/dhruv-developer)

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

# Open the app in browser
http://localhost:5173
