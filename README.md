# Invoice Parser – ML & OCR Backend

Backend and machine learning pipeline for an AI-powered invoice and receipt parsing system.

This repository contains the **OCR, object detection, and parsing logic**, exposed via an API
and consumed by a separate frontend application.

➡ **Frontend / App layer**: https://github.com/AhmedBhiri/Invoice-parser

---

## Overview

This backend is responsible for:
- Preprocessing uploaded invoice / receipt documents
- Detecting relevant document regions using object detection
- Extracting text from detected regions using OCR
- Post-processing and structuring extracted data
- Exposing API endpoints for frontend consumption

The system is designed to support **multiple document layouts and formats**
without relying on fixed templates.

---

## ML & OCR Pipeline

1. Document upload (PDF / image)
2. Optional format conversion (PDF → images)
3. Object detection on document regions (YOLO)
4. OCR on detected regions (Tesseract)
5. Post-processing and field extraction
6. Structured JSON response

---

## Models

- **Object Detection**
  - YOLOv5
  - YOLOv8
- **OCR**
  - Tesseract OCR (via pytesseract)

Models were trained and benchmarked on invoice and receipt datasets
with varying layouts and languages.

---

## Tech Stack

- Python
- Django (API server)
- PyTorch
- YOLOv5 / YOLOv8
- Tesseract OCR
- Roboflow (dataset management & model hosting)
- Docker (local deployment & testing)

---

## API Role

This backend exposes REST endpoints used by the frontend to:
- Submit documents for processing
- Receive extracted structured data
- Handle temporary storage during processing

The frontend is responsible for user interaction, validation, and persistence.
- The Roboflow API key must be provided via the `ROBOFLOW_API_KEY` environment variable.

---

## Project Structure (simplified)

