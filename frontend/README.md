# Note Maker Frontend

React + TypeScript UI for the Note Maker app.

## Setup

Requires Node.js 18+.

```bash
npm install
npm run dev
```

The dev server runs on http://127.0.0.1:5173 and proxies API calls to the backend at http://127.0.0.1:8000.

Start the backend first from `../backend`:

```bash
uvicorn app.main:app --reload
```
