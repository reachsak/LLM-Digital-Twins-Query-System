# TwinGPT: LLM-Digital-Twins-Query-System

## Video Demo

[![Watch the demo video](https://img.youtube.com/vi/llvWQsCaRTs/0.jpg)](https://youtu.be/llvWQsCaRTs)  
*Click on the image to view the video.*

---

## Project Overview

**TwinGPT** is an AI-powered digital twin query system designed for facility managers to interact with and extract insights from building data using a large language model (LLM). This system integrates static data, such as BIM (Building Information Modeling) details, with dynamic data from sensors, environmental inputs, and occupancy information. It provides an intuitive interface for querying both historical and real-time building data.

### Key Features

- **Interactive AI Chatbot**: Facility managers can ask questions or talk to the AI assistant to retrieve building information.
- **Static and Dynamic Data Query**: Access both BIM-related static data and dynamic data like sensor readings, environmental conditions, and occupancy metrics.
- **LLM Integration**: Built using the open-source AI system Llama 3.2, powered by the efficient `llama.cpp` framework for inference.
- **Digital Twin Platform**: Leverages Autodesk Tandem to manage and visualize building information.
- **API-Based Data Retrieval**: The AI queries Autodesk Tandem through REST APIs to fetch and analyze building data.

---

## Implementation Details

- **AI Framework**: 
  - Utilizes the open-source Llama 3.2 large language model for natural language understanding and responses.
  - Inference is performed using the efficient `llama.cpp` toolkit.

- **Digital Twin Platform**: 
  - Autodesk Tandem is used as the digital twin platform to host and manage building data.

- **Data Query Mechanism**: 
  - The system communicates with Autodesk Tandem via REST APIs to request and retrieve building data dynamically.

---

## Getting Started

### Prerequisites

To replicate or extend this project, you will need:

- **AI System**: Open-source Llama 3.2 model and `llama.cpp` tools for inference.
- **Digital Twin**: Autodesk Tandem account and access to its API.
- **Programming Tools**:
  - Python 3.x
  - REST API integration tools and libraries

### Installation




