# TODO - PRJ.3 Fractais (Backend Python)

## Passo 1 — Estrutura do projeto
- [x] Criar diretórios: app/, tests/, docs/
- [x] Criar requirements.txt
- [x] Criar arquivo de entrada do pacote (app/__init__.py) e configuraçao mínima

## Passo 2 — Implementação do core (fractal/cores)
- [ ] Implementar fractal.py (Julia e Mandelbrot, iteração, suavização)
- [ ] Implementar color.py (paletas 6+, mapeamento por iteração/magnitude, interpolação contínua)
- [ ] Implementar utils.py (validações numéricas, parsing de paleta hex)

## Passo 3 — API REST + CLI
- [ ] Implementar api.py (FastAPI endpoints: /health, /palettes, /fractal)
- [ ] Implementar cli.py (python -m app generate ...)
- [ ] Implementar export PNG (Pillow) e SVG (opcional, desenhando retângulos otimizado)

## Passo 4 — Testes
- [ ] Testes unitários: fractal iteration/escape, color mapping, validações
- [ ] Testes de integração: API /fractal (status, content-type, dimensões)

## Passo 5 — Documentação e exemplos
- [ ] README.md com instalação, uso API e CLI, exemplos de parâmetros
- [x] Incluir 3 imagens de exemplo (quando gerar for possível; caso não, deixar instrução)

## Passo 6 — CI (GitHub Actions)
- [ ] Workflow com lint (ruff/flake8 opcional), pytest e teste simples de performance

## Passo 7 — Execução local
- [ ] Validar: `py -m pip install -r requirements.txt`
- [ ] Validar: `pytest`
- [ ] Validar: rodar API via `uvicorn app.api:app`
- [ ] Validar: CLI `py -m app generate ...`

## Ajustes em andamento
- [x] Corrigir /palettes e simplificar parsing de paletas em POST /fractal (app/api.py)

