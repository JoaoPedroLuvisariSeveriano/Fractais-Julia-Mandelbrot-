import { useEffect, useState } from 'react'

import {
  type ColoringMode,
  type FractalPayload,
  type FractalType,
  type OutputFormat,
  fetchPalettes,
  generateFractal,
} from './api'

type FractalPayloadWithPalette = FractalPayload & { palette: string | string[] }

import './App.css'

type JuliaFields = {
  real: number
  imag: number
}

type MandelFields = {
  real: number
  imag: number
}

const DEFAULT_STEP = 0.002
const DEFAULT_MAX_ITER = 500
const DEFAULT_ESCAPE_RADIUS = 2.0


function clampNumber(value: number, min: number, max: number) {
  if (Number.isNaN(value)) return min
  return Math.max(min, Math.min(max, value))
}

function formatForDownload(filenameBase: string, ext: OutputFormat) {
  const suffix = ext.toLowerCase()
  return `${filenameBase}.${suffix}`
}

function objectToPayload(params: {
  type: FractalType
  step: number
  width: number
  height: number
  max_iter: number
  palette: string
  mode: ColoringMode
  format: OutputFormat
  escape_radius: number
  julia: JuliaFields
  mandelbrot: MandelFields
}): FractalPayload {
  const { type, step, width, height, max_iter, palette, mode, format, escape_radius, julia, mandelbrot } = params

  if (type === 'julia') {
    return {
      type,
      step,
      width,
      height,
      max_iter,
      palette,
      mode,
      format,
      escape_radius,
      real: julia.real,
      imag: julia.imag,
    }
  }

  // Backend: mandelbrot uses real/imag as center reference; it converts to x0/y0.
  return {
    type,
    step,
    width,
    height,
    max_iter,
    palette,
    mode,
    format,
    escape_radius,
    real: mandelbrot.real,
    imag: mandelbrot.imag,
  }
}

export default function App() {
  const [palettes, setPalettes] = useState<string[]>([])
  const [palette, setPalette] = useState<string>('viridis')
  const [paletteMode, setPaletteMode] = useState<'builtin' | 'custom'>('builtin')

  // Custom palette via hex list (at least 6 colors). We keep simple UI as optional.

  const [customPaletteText, setCustomPaletteText] = useState<string>('#440154,#482878,#3E4989,#31688E,#26828E,#FDE725')

  // Payload palette shape is handled below:
  // - builtin => palette is a string (e.g. "viridis")
  // - custom => palette is a list of hex strings
  const effectivePalette = palette


  const [type, setType] = useState<FractalType>('julia')
  const [mode, setMode] = useState<ColoringMode>('smoothed')
  const [step, setStep] = useState(DEFAULT_STEP)
  const [width, setWidth] = useState(640)
  const [height, setHeight] = useState(480)
  const [maxIter, setMaxIter] = useState(DEFAULT_MAX_ITER)
  const [escapeRadius, setEscapeRadius] = useState(DEFAULT_ESCAPE_RADIUS)

  const [julia, setJulia] = useState<JuliaFields>({ real: -0.7, imag: 0.27015 })
  const [mandelbrot, setMandelbrot] = useState<MandelFields>({ real: 0, imag: 0 })

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')

  const [previewUrl, setPreviewUrl] = useState<string>('')
  const [previewContentType, setPreviewContentType] = useState<string>('')

  const [lastPayload, setLastPayload] = useState<import('./api').FractalPayload | null>(null)


  useEffect(() => {
    const ac = new AbortController()
    fetchPalettes(ac.signal)
      .then((p) => {
        setPalettes(p)
        if (p.includes('viridis')) setPalette('viridis')
        else if (p.length > 0) setPalette(p[0])
      })
      .catch((e) => {
        // Non-blocking: UI still works if API is down.
        setError(String(e))
      })
    return () => ac.abort()
  }, [])

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function runGenerate(format: OutputFormat) {
    setLoading(true)
    setError('')

    try {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
      setPreviewUrl('')
      setPreviewContentType('')

      const payloadBase = objectToPayload({
        type,
        step,
        width,
        height,
        max_iter: maxIter,
        palette: effectivePalette,
        mode,
        format,
        escape_radius: escapeRadius,
        julia,
        mandelbrot,
      })

      let payload: FractalPayloadWithPalette = payloadBase




      if (paletteMode === 'custom') {
        const parts = customPaletteText
          .split(/[,\n]/g)
          .map((s) => s.trim())
          .filter(Boolean)

        payload = {
          ...payloadBase,
          palette: parts,
        }
      }

      setLastPayload(payload)

      const { blob, contentType } = await generateFractal(payload)
      const url = URL.createObjectURL(blob)
      setPreviewUrl(url)
      setPreviewContentType(contentType)
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e)
      setError(msg)

    } finally {
      setLoading(false)
    }
  }

  function downloadFromCurrentBlob(format: OutputFormat) {
    if (!previewUrl) return

    const filenameBase = `${type}-${width}x${height}-${mode}-${paletteMode === 'builtin' ? palette : 'custom'}`
    const filename = formatForDownload(filenameBase, format)

    const a = document.createElement('a')
    a.href = previewUrl
    a.download = filename

    // If preview is SVG but we request PNG, URL is wrong; so we only download for current preview.
    a.click()
  }

  const isSvg = previewContentType.includes('image/svg+xml')
  const isPng = previewContentType.includes('image/png')

  const showJulia = type === 'julia'
  const showMandel = type === 'mandelbrot'

  return (
    <div className="page">
      <header className="header">
        <h1>Fractais (Julia / Mandelbrot)</h1>
        <p className="subtitle">Frontend consumindo <code>/fractal</code> do backend.</p>
      </header>

      <main className="layout">
        <section className="controls" aria-label="Controles">
          <div className="row">
            <label className="field">
              <span>Tipo</span>
              <select value={type} onChange={(e) => setType(e.target.value as FractalType)}>
                <option value="julia">Julia</option>
                <option value="mandelbrot">Mandelbrot</option>
              </select>
            </label>

            <label className="field">
              <span>Modo de coloração</span>
              <select value={mode} onChange={(e) => setMode(e.target.value as ColoringMode)}>
                <option value="iteration">iteration</option>
                <option value="magnitude">magnitude</option>
                <option value="smoothed">smoothed</option>
              </select>
            </label>
          </div>

          <div className="sectionTitle">Parâmetros numéricos</div>
          <div className="grid2">
            <label className="field">
              <span>Largura (width)</span>
              <input
                type="number"
                min={16}
                max={4096}
                value={width}
                onChange={(e) => setWidth(clampNumber(Number(e.target.value), 16, 4096))}
              />
            </label>
            <label className="field">
              <span>Altura (height)</span>
              <input
                type="number"
                min={16}
                max={4096}
                value={height}
                onChange={(e) => setHeight(clampNumber(Number(e.target.value), 16, 4096))}
              />
            </label>

            <label className="field">
              <span>step (resolução/escala)</span>
              <input
                type="number"
                step={0.0001}
                value={step}
                onChange={(e) => setStep(Number(e.target.value))}
              />
            </label>
            <label className="field">
              <span>max_iter</span>
              <input
                type="number"
                min={1}
                max={20000}
                value={maxIter}
                onChange={(e) => setMaxIter(clampNumber(Number(e.target.value), 1, 20000))}
              />
            </label>

            <label className="field">
              <span>escape_radius</span>
              <input
                type="number"
                step={0.1}
                value={escapeRadius}
                onChange={(e) => setEscapeRadius(Number(e.target.value))}
              />
            </label>
          </div>

          {showJulia && (
            <>
              <div className="sectionTitle">Parâmetros da Julia (c = real + imag·i)</div>
              <div className="grid2">
                <label className="field">
                  <span>real</span>
                  <input type="number" step={0.0001} value={julia.real} onChange={(e) => setJulia((p) => ({ ...p, real: Number(e.target.value) }))} />
                </label>
                <label className="field">
                  <span>imag</span>
                  <input type="number" step={0.0001} value={julia.imag} onChange={(e) => setJulia((p) => ({ ...p, imag: Number(e.target.value) }))} />
                </label>
              </div>
            </>
          )}

          {showMandel && (
            <>
              <div className="sectionTitle">Parâmetros da Mandelbrot (centro)</div>
              <div className="grid2">
                <label className="field">
                  <span>real (centro)</span>
                  <input type="number" step={0.0001} value={mandelbrot.real} onChange={(e) => setMandelbrot((p) => ({ ...p, real: Number(e.target.value) }))} />
                </label>
                <label className="field">
                  <span>imag (centro)</span>
                  <input type="number" step={0.0001} value={mandelbrot.imag} onChange={(e) => setMandelbrot((p) => ({ ...p, imag: Number(e.target.value) }))} />
                </label>
              </div>
            </>
          )}

          <div className="sectionTitle">Paleta de cores</div>
          <div className="row">
            <label className="field">
              <span>Fonte</span>
              <select
                value={paletteMode}
                onChange={(e) => {
                  const v = e.target.value as 'builtin' | 'custom'
                  setPaletteMode(v)
                }}
              >
                <option value="builtin">Paletas do backend</option>
                <option value="custom">Custom (hex)</option>
              </select>
            </label>
          </div>

          {paletteMode === 'builtin' ? (
            <div className="row">
              <label className="field">
                <span>Paleta</span>
                <select value={palette} onChange={(e) => setPalette(e.target.value)}>
                  {palettes.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          ) : (
            <div className="row">
              <label className="field">
                <span>Lista de cores hex (#RRGGBB), separadas por vírgula</span>
                <textarea value={customPaletteText} onChange={(e) => setCustomPaletteText(e.target.value)} rows={3} />
              </label>
            </div>
          )}

          <div className="actions">
            <button disabled={loading} className="primary" onClick={() => runGenerate('png')}>
              {loading ? 'Gerando...' : 'Gerar PNG (preview)'}
            </button>
            <button disabled={loading} className="secondary" onClick={() => runGenerate('svg')}>
              {loading ? 'Gerando...' : 'Gerar SVG'}
            </button>
          </div>

          {error && <div className="error">{error}</div>}
        </section>

        <section className="preview" aria-label="Preview e download">
          <div className="previewHeader">
            <div>
              <div className="sectionTitle" style={{ marginTop: 0 }}>
                Prévia
              </div>
              <div className="meta">
                {previewContentType}
                {lastPayload ? <span className="pill">max_iter: {lastPayload.max_iter}</span> : null}
              </div>
            </div>
            <div className="downloadActions">
              <button
                disabled={!isPng}
                onClick={() => downloadFromCurrentBlob('png')}
                className="ghost"
                title="Baixar o PNG exatamente da prévia atual"
              >
                Download PNG
              </button>
              <button
                disabled={!isSvg}
                onClick={() => downloadFromCurrentBlob('svg')}
                className="ghost"
                title="Baixar o SVG exatamente da prévia atual"
              >
                Download SVG
              </button>
            </div>
          </div>

          <div className="previewBody">
            {!previewUrl ? (
              <div className="empty">
                Selecione parâmetros e clique em <b>Gerar PNG</b> ou <b>Gerar SVG</b>.
              </div>
            ) : isSvg ? (
              <img src={previewUrl} alt="Preview SVG" className="svgPreview" />
            ) : isPng ? (
              <img src={previewUrl} alt="Preview PNG" className="pngPreview" />
            ) : (
              <div className="empty">Formato desconhecido: {previewContentType || '—'}</div>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

