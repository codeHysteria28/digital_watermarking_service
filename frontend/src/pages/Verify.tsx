import { useState, useEffect } from 'react'
import { UploadCloud, X, CheckCircle2, XCircle, Loader2, ShieldCheck } from 'lucide-react'
import { cn } from '@/lib/utils'
import { api, type VerificationLog } from '@/lib/api'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/ui/button'

export function Verify() {
  const { token } = useAuth()
  const [dragging, setDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [verifying, setVerifying] = useState(false)
  const [result, setResult] = useState<VerificationLog | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!file) {
      setPreview(null)
      return
    }
    const url = URL.createObjectURL(file)
    setPreview(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) {
      setFile(dropped)
      setResult(null)
      setError(null)
    }
  }

  const clearFile = () => {
    setFile(null)
    setResult(null)
    setError(null)
  }

  const handleVerify = async () => {
    if (!file || !token) return
    setError(null)
    setVerifying(true)
    try {
      const log = await api.verifyFile(file, token)
      setResult(log)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Verification failed')
    } finally {
      setVerifying(false)
    }
  }

  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-8 px-4 py-16">
      <div className="flex items-center gap-3">
        <ShieldCheck size={28} className="text-primary" />
        <h1 className="text-3xl font-bold text-foreground">Verify Image</h1>
      </div>
      <p className="text-sm text-muted-foreground">
        Upload any image to check whether it contains a valid watermark and has not been tampered with.
      </p>

      {!file && (
        <label
          htmlFor="verify-input"
          onDragOver={e => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={cn(
            'flex cursor-pointer flex-col items-center gap-4 rounded-lg border-2 border-dashed px-8 py-16 text-center transition-colors',
            dragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50 hover:bg-muted/30'
          )}
        >
          <UploadCloud size={40} className="text-muted-foreground" />
          <p className="text-sm font-medium text-foreground">Drag &amp; drop an image here, or click to browse</p>
          <p className="text-xs text-muted-foreground">PNG, JPG, WEBP, BMP, TIFF</p>
          <input
            id="verify-input"
            type="file"
            accept="image/png,image/jpeg,image/webp,image/bmp,image/tiff"
            className="sr-only"
            onChange={e => {
              setFile(e.target.files?.[0] ?? null)
              setResult(null)
              setError(null)
            }}
          />
        </label>
      )}

      {file && preview && (
        <div className="relative overflow-hidden rounded-lg border bg-muted/30">
          <img src={preview} alt="Image to verify" className="max-h-72 w-full object-contain" />
          {!verifying && (
            <button
              type="button"
              onClick={clearFile}
              className="absolute right-2 top-2 h-9 w-9 rounded-full bg-background/80 p-2 text-foreground backdrop-blur-sm transition-colors hover:bg-destructive hover:text-destructive-foreground"
            >
              <X size={20} />
            </button>
          )}
          <div className="border-t px-4 py-2 text-xs text-muted-foreground">
            {file.name} &mdash; {(file.size / 1024 / 1024).toFixed(2)} MB
          </div>
        </div>
      )}

      {file && !result && (
        <Button onClick={handleVerify} disabled={verifying}>
          {verifying && <Loader2 size={16} className="animate-spin" />}
          {verifying ? 'Verifying…' : 'Verify Watermark'}
        </Button>
      )}

      {error && <p className="rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive">{error}</p>}

      {result && (
        <div className="flex flex-col gap-4 rounded-lg border p-6">
          <h2 className="text-base font-semibold text-foreground">Verification Result</h2>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex flex-col gap-1">
              <span className="text-xs text-muted-foreground">Authentic</span>
              {result.is_authentic ? (
                <span className="flex items-center gap-1 text-green-700 dark:text-green-400">
                  <CheckCircle2 size={15} /> Authentic
                </span>
              ) : (
                <span className="flex items-center gap-1 text-red-600 dark:text-red-400">
                  <XCircle size={15} /> Not authentic
                </span>
              )}
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-xs text-muted-foreground">Tampered</span>
              {!result.is_tampered ? (
                <span className="flex items-center gap-1 text-green-700 dark:text-green-400">
                  <CheckCircle2 size={15} /> No tampering
                </span>
              ) : (
                <span className="flex items-center gap-1 text-red-600 dark:text-red-400">
                  <XCircle size={15} /> Tampering detected
                </span>
              )}
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-xs text-muted-foreground">Confidence</span>
              <span className="font-medium text-foreground">{(result.confidence_score * 100).toFixed(1)}%</span>
            </div>
            {result.tampering_severity && (
              <div className="flex flex-col gap-1">
                <span className="text-xs text-muted-foreground">Severity</span>
                <span className="font-medium capitalize text-foreground">{result.tampering_severity}</span>
              </div>
            )}
            {result.processing_time_ms != null && (
              <div className="flex flex-col gap-1">
                <span className="text-xs text-muted-foreground">Processing time</span>
                <span className="text-foreground">{result.processing_time_ms} ms</span>
              </div>
            )}
            {result.algorithm_version && (
              <div className="flex flex-col gap-1">
                <span className="text-xs text-muted-foreground">Algorithm</span>
                <span className="text-foreground">{result.algorithm_version}</span>
              </div>
            )}
          </div>

          {result.error_message && (
            <p className="rounded bg-destructive/10 px-3 py-2 text-xs text-destructive">{result.error_message}</p>
          )}

          <button
            onClick={clearFile}
            className="mt-2 self-start text-sm text-muted-foreground underline underline-offset-4 hover:text-foreground"
          >
            Verify another image
          </button>
        </div>
      )}
    </main>
  )
}
