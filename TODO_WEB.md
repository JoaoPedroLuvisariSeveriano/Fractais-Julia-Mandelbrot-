# TODO - Frontend Web (Fractais)

- [ ] Definir stack (Vite + React + TypeScript) e criar pasta `frontend/`.
- [ ] Criar integração com a API: `GET /palettes` e `POST /fractal` (png e svg) com `fetch`.
- [ ] Construir UI:
  - [ ] Seletor de tipo (Julia/Mandelbrot)
  - [ ] Campos: width/height, max_iter, step, escape_radius
  - [ ] Para Julia: real/imag (c)
  - [ ] Para Mandelbrot: real/imag (centro)
  - [ ] Seletor de palette (nomes retornados pela API + opção de custom via hex opcional)
  - [ ] Seletor de modo de coloração (iteration/magnitude/smoothed)
- [ ] Área de preview:
  - [ ] Renderizar PNG (img blob URL)
  - [ ] Exibir também prévia SVG (caso gerado)
- [ ] Exportar:
  - [ ] Botão Download PNG
  - [ ] Botão Download SVG (garantir cores fiéis usando o mesmo payload do backend)
- [ ] Implementar estados de carregamento/erro e validações básicas.
- [ ] Testar manualmente contra o backend rodando localmente.
- [ ] (Opcional) Adicionar script README de como iniciar backend + frontend.

