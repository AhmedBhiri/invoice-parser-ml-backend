cat << 'EOF' > API.md
# Backend API Documentation

Base URL (local): `http://localhost:8000`

This backend provides invoice/receipt extraction using a YOLO detector + OCR pipeline.
It is consumed by the frontend.

---

## Endpoints

### `GET /`
Basic health/index endpoint.

```bash
curl http://localhost:8000/

