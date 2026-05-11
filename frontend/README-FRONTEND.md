# Frontend - Fractal Generator

## Requisitos
- Node.js 20+ (foi usado Node 22)

## Instalar
```bash
cd "frontend"
npm install
```

## Rodar
1) Inicie o backend (exemplo):
```bash
py -m uvicorn app.api:app --reload --host 127.0.0.1 --port 8000
```

2) Rode o frontend:
```bash
cd "frontend"
npm run dev
```

Abra:
- http://localhost:5173

## Configuração do backend
Por padrão, o frontend usa:
- `http://127.0.0.1:8000`

Para mudar via env:
- crie um arquivo `.env` em `frontend/` com:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

