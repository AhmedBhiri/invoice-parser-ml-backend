# ML & OCR Model Overview

This document describes the machine learning and OCR components used in the
invoice and receipt parsing backend.

---

## Problem Overview

Invoices and receipts come in many layouts and formats.
Template-based approaches fail when layouts change.

This project uses **object detection + OCR** to extract structured information
without relying on fixed templates.

---

## Object Detection

### Model
- YOLO (You Only Look Once)
- Versions used: YOLOv5 and YOLOv8

### Purpose
The object detection model is used to locate semantically relevant regions
on a document, such as:
- invoice number
- date
- total amount
- vendor / merchant
- header and footer regions

Detecting regions before OCR improves accuracy by:
- reducing noise
- limiting OCR to relevant areas
- making the system layout-agnostic

---

## OCR (Optical Character Recognition)

### Engine
- Tesseract OCR (via pytesseract)

### Role
After region detection, OCR is applied to each detected region individually.
This allows:
- better text recognition
- easier post-processing
- separation of concerns between vision and text extraction

---

## Post-processing & Parsing

OCR outputs are post-processed to:
- normalize text (dates, currency, numbers)
- filter low-confidence results
- map detected regions to structured fields

The final output is returned as structured JSON.

---

## Pipeline Summary

1. Document upload (PDF / image)
2. Optional conversion to image
3. Object detection (YOLO)
4. OCR on detected regions (Tesseract)
5. Post-processing & parsing
6. Structured JSON output

---

## Notes

- Models are pretrained and fine-tuned for document layouts
- No trained weights or proprietary datasets are included in this repository
- The public repository contains a sanitized version of the system
