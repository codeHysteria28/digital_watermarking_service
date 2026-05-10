import { Link } from 'react-router-dom'
import { ImageIcon, Trash2, Download, Loader2, RefreshCw, ShieldCheck } from 'lucide-react'
import { cn } from '@/lib/utils'
import { api, type EvidenceImage } from '@/lib/api'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/ui/button'
import { useEffect, useState } from 'react'

const STATUS_STYLES: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
  processing: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  completed: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
  verified: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
  tampered: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  failed: 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
}

function formatSize(bytes: number | null) {
  if (!bytes) return '—'
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

export function Manage() {
  const { token } = useAuth()
  const [images, setImages] = useState<EvidenceImage[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [retryingId, setRetryingId] = useState<number | null>(null)

  useEffect(() => {
    if (!token) return
    api.listImages(token)
      .then(setImages)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [token])

  const handleDelete = async (image: EvidenceImage) => {
    if (!token || !confirm(`Delete "${image.filename}"? This cannot be undone.`)) return
    setDeletingId(image.id)
    try {
      await api.deleteImage(image.id, token)
      setImages(prev => prev.filter(i => i.id !== image.id))
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Delete failed')
    } finally {
      setDeletingId(null)
    }
  }

  const handleDownload = async (image: EvidenceImage, watermarked = false) => {
    if (!token) return
    try {
      const res = watermarked
        ? await api.downloadWatermarkedImage(image.id, token)
        : await api.downloadImage(image.id, token)
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = watermarked ? `watermarked_${image.filename}` : image.filename
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Download failed')
    }
  }

  const handleRetryWatermark = async (image: EvidenceImage) => {
    if (!token) return
    setRetryingId(image.id)
    try {
      const updated = await api.retryWatermark(image.id, token)
      setImages(prev => prev.map(i => (i.id === updated.id ? updated : i)))
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Retry failed')
    } finally {
      setRetryingId(null)
    }
  }

  const canRetry = (status: EvidenceImage['status']) =>
    ['failed', 'completed', 'verified'].includes(status)

  if (loading) {
    return (
      <main className="mx-auto flex max-w-5xl items-center justify-center px-4 py-24">
        <Loader2 size={24} className="animate-spin text-muted-foreground" />
      </main>
    )
  }

  return (
    <main className="mx-auto flex max-w-5xl flex-col gap-6 px-3 py-8 md:gap-8 md:px-4 md:py-16">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <h1 className="text-2xl font-bold text-foreground md:text-3xl">My Photos</h1>
        <Button asChild className="h-12 md:h-10">
          <Link to="/upload">Upload New</Link>
        </Button>
      </div>

      {error && (
        <p className="rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive">{error}</p>
      )}

      {images.length === 0 ? (
        <div className="flex flex-col items-center gap-4 rounded-lg border border-dashed py-16 text-center md:py-24">
          <ImageIcon size={40} className="text-muted-foreground" />
          <p className="text-muted-foreground">No photos uploaded yet.</p>
          <Link to="/upload" className="text-sm text-primary underline underline-offset-4 hover:opacity-80">
            Upload your first photo
          </Link>
        </div>
      ) : (
        <>
          {/* Mobile Card Layout */}
          <div className="flex flex-col gap-3 md:hidden">
            {images.map(image => (
              <div key={image.id} className="rounded-lg border bg-card p-4 text-card-foreground">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex min-w-0 flex-1 items-start gap-3">
                    <ImageIcon size={20} className="mt-0.5 shrink-0 text-muted-foreground" />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-base font-medium text-foreground">{image.filename}</p>
                      <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                        <span>{formatSize(image.file_size)}</span>
                        <span>•</span>
                        <span>{new Date(image.created_at).toLocaleDateString()}</span>
                      </div>
                      <div className="mt-2">
                        <span className={cn('inline-block rounded-full px-2 py-0.5 text-xs font-medium capitalize', STATUS_STYLES[image.status])}>
                          {image.status}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="mt-4 flex flex-wrap items-center gap-2">
                  {canRetry(image.status) && (
                    <Button
                      onClick={() => handleRetryWatermark(image)}
                      disabled={retryingId === image.id}
                      variant="outline"
                      size="sm"
                      className="h-11 flex-1"
                    >
                      {retryingId === image.id ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                      <span className="ml-1">Re-watermark</span>
                    </Button>
                  )}
                  <Button
                    onClick={() => handleDownload(image)}
                    variant="outline"
                    size="sm"
                    className="h-11 flex-1"
                  >
                    <Download size={16} />
                    <span className="ml-1">Original</span>
                  </Button>
                  {image.watermarked_path && (
                    <Button
                      onClick={() => handleDownload(image, true)}
                      variant="outline"
                      size="sm"
                      className="h-11 flex-1"
                    >
                      <ShieldCheck size={16} />
                      <span className="ml-1">Watermarked</span>
                    </Button>
                  )}
                  <Button
                    onClick={() => handleDelete(image)}
                    disabled={deletingId === image.id}
                    variant="outline"
                    size="sm"
                    className="h-11"
                  >
                    {deletingId === image.id ? <Loader2 size={16} className="animate-spin" /> : <Trash2 size={16} />}
                  </Button>
                </div>
              </div>
            ))}
          </div>

          {/* Desktop Table Layout */}
          <div className="hidden overflow-hidden rounded-lg border md:block">
            <table className="w-full text-sm">
              <thead className="bg-muted text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 text-left font-medium">File Name</th>
                  <th className="px-4 py-3 text-left font-medium">Status</th>
                  <th className="px-4 py-3 text-left font-medium">Size</th>
                  <th className="px-4 py-3 text-left font-medium">Uploaded</th>
                  <th className="px-4 py-3 text-right font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {images.map(image => (
                  <tr key={image.id} className="transition-colors hover:bg-muted/50">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2 text-foreground">
                        <ImageIcon size={16} className="shrink-0 text-muted-foreground" />
                        <span className="max-w-xs truncate">{image.filename}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={cn('rounded-full px-2 py-0.5 text-xs font-medium capitalize', STATUS_STYLES[image.status])}>
                        {image.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{formatSize(image.file_size)}</td>
                    <td className="px-4 py-3 text-muted-foreground">
                      {new Date(image.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-1">
                        {canRetry(image.status) && (
                          <button
                            onClick={() => handleRetryWatermark(image)}
                            disabled={retryingId === image.id}
                            title="Re-watermark"
                            className="rounded p-1 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground disabled:opacity-50"
                          >
                            {retryingId === image.id ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                          </button>
                        )}
                        <button
                          onClick={() => handleDownload(image)}
                          title="Download original"
                          className="rounded p-1 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
                        >
                          <Download size={16} />
                        </button>
                        {image.watermarked_path && (
                          <button
                            onClick={() => handleDownload(image, true)}
                            title="Download watermarked"
                            className="rounded p-1 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
                          >
                            <ShieldCheck size={16} />
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(image)}
                          disabled={deletingId === image.id}
                          title="Delete"
                          className="rounded p-1 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive disabled:opacity-50"
                        >
                          {deletingId === image.id ? <Loader2 size={16} className="animate-spin" /> : <Trash2 size={16} />}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </main>
  )
}
