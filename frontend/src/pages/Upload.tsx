import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { UploadCloud, X, Loader2, CheckCircle2, ImageUp } from 'lucide-react'
import { cn } from '@/lib/utils'
import { api } from '@/lib/api'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/ui/button'

const inputClass = 'rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring md:h-10 h-12'

export function Upload() {
  const { token } = useAuth()
  const navigate = useNavigate()
  const [dragging, setDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [done, setDone] = useState(false)

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
      setError(null)
    }
  }

  const clearFile = () => {
    setFile(null)
    setError(null)
    setDone(false)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file || !token) return
    setError(null)
    setUploading(true)
    try {
      await api.uploadImage(file, token)
      setDone(true)
      setTimeout(() => navigate('/manage'), 1500)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <main className="mx-auto flex max-w-2xl flex-col gap-6 px-3 py-8 md:gap-8 md:px-4 md:py-16">
      <div className="flex items-center gap-3">
        <ImageUp size={28} className="text-primary" />
        <h1 className="text-2xl font-bold text-foreground md:text-3xl">Upload Image</h1>
      </div>
      {!file && (
        <label
          htmlFor="file-input"
          onDragOver={e => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          className={cn(
            'flex cursor-pointer flex-col items-center gap-4 rounded-lg border-2 border-dashed px-6 py-12 text-center transition-colors md:px-8 md:py-16',
            dragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50 hover:bg-muted/30'
          )}
        >
          <UploadCloud size={40} className="text-muted-foreground" />
          <p className="text-sm font-medium text-foreground md:text-base">Drag &amp; drop a photo here, or click to browse</p>
          <p className="text-xs text-muted-foreground">PNG, JPG, WEBP up to 50 MB</p>
          <input
            id="file-input"
            type="file"
            accept="image/png,image/jpeg,image/webp"
            capture="environment"
            className="sr-only"
            onChange={e => {
              setFile(e.target.files?.[0] ?? null)
              setError(null)
            }}
          />
        </label>
      )}

      {file && preview && (
        <>
          <div className="relative overflow-hidden rounded-lg border bg-muted/30">
            <img src={preview} alt="Selected preview" className="max-h-96 w-full object-contain" />
            {!uploading && !done && (
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

          {done && (
            <div className="flex items-center gap-3 rounded-md bg-green-50 px-4 py-3 text-sm text-green-800 dark:bg-green-900/20 dark:text-green-400">
              <CheckCircle2 size={18} />
              Uploaded successfully — redirecting to your photos…
            </div>
          )}

          {error && <p className="rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive">{error}</p>}

          {!done && (
            <form onSubmit={handleSubmit} className="flex flex-col gap-4 md:gap-4">
              <div className="flex flex-col gap-1.5">
                <label htmlFor="photo-title" className="text-sm font-medium text-foreground md:text-base">
                  Title <span className="text-muted-foreground">(optional)</span>
                </label>
                <input id="photo-title" type="text" placeholder={file.name} className={inputClass} />
              </div>
              <div className="flex flex-col gap-1.5">
                <label htmlFor="photo-description" className="text-sm font-medium text-foreground md:text-base">
                  Description <span className="text-muted-foreground">(optional)</span>
                </label>
                <textarea
                  id="photo-description"
                  rows={3}
                  placeholder="Optional description..."
                  className={cn(inputClass, 'resize-none')}
                />
              </div>
              <div className="flex flex-col-reverse items-stretch gap-3 md:flex-row md:items-center md:justify-between">
                <button
                  type="button"
                  onClick={clearFile}
                  disabled={uploading}
                  className="text-sm text-muted-foreground underline underline-offset-4 hover:text-foreground disabled:opacity-50"
                >
                  Choose a different photo
                </button>
                <Button type="submit" disabled={uploading} className="h-12 md:h-10">
                  {uploading && <Loader2 size={16} className="animate-spin" />}
                  {uploading ? 'Uploading…' : 'Upload & Watermark'}
                </Button>
              </div>
            </form>
          )}
        </>
      )}
    </main>
  )
}
