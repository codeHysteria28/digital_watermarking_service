import { useEffect, useState } from 'react'
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/context/AuthContext'
import { api, type VerificationLog } from '@/lib/api'

type Tab = 'history'

export function Profile() {
  const { user, token } = useAuth()
  const [tab] = useState<Tab>('history')
  const [history, setHistory] = useState<VerificationLog[]>([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) return
    setHistoryLoading(true)
    api.getVerificationHistory(token)
      .then(setHistory)
      .catch(e => setHistoryError(e.message))
      .finally(() => setHistoryLoading(false))
  }, [token])

  return (
    <main className="mx-auto flex max-w-4xl flex-col gap-6 px-3 py-8 md:gap-8 md:px-4 md:py-16">
      <h1 className="text-2xl font-bold text-foreground md:text-3xl">Profile &amp; Statistics</h1>

      {/* Stats */}
      {user && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:gap-4">
          {[
            { label: 'Photos Uploaded', value: user.total_images_uploaded },
            { label: 'Verifications Run', value: user.total_verifications },
            { label: 'Member Since', value: new Date(user.created_at).toLocaleDateString() },
          ].map(stat => (
            <div key={stat.label} className="rounded-lg border border-border p-3 text-center md:p-4">
              <p className="text-xl font-bold text-foreground md:text-2xl">{stat.value}</p>
              <p className="mt-1 text-xs text-muted-foreground">{stat.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Verification History */}
      <div className="flex flex-col gap-4">
        <h2 className="text-lg font-semibold text-foreground md:text-xl">Verification History</h2>

        {historyLoading && (
          <div className="flex justify-center py-12 text-muted-foreground md:py-16">
            <Loader2 size={24} className="animate-spin" />
          </div>
        )}

        {historyError && (
          <p className="rounded-md bg-destructive/10 px-4 py-3 text-sm text-destructive">{historyError}</p>
        )}

        {!historyLoading && !historyError && history.length === 0 && (
          <p className="py-12 text-center text-sm text-muted-foreground md:py-16">No verifications run yet.</p>
        )}

        {!historyLoading && history.length > 0 && (
          <>
            {/* Mobile Card Layout */}
            <div className="flex flex-col gap-3 md:hidden">
              {history.map(log => (
                <div key={log.id} className="rounded-lg border bg-card p-4 text-card-foreground">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex min-w-0 flex-1 flex-col gap-2">
                      <p className="text-xs text-muted-foreground">
                        {new Date(log.created_at).toLocaleString()}
                      </p>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div className="flex flex-col gap-1">
                          <span className="text-xs text-muted-foreground">Authentic</span>
                          {log.is_authentic ? (
                            <span className="flex items-center gap-1 text-green-700 dark:text-green-400">
                              <CheckCircle2 size={14} /> Yes
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-red-600 dark:text-red-400">
                              <XCircle size={14} /> No
                            </span>
                          )}
                        </div>
                        <div className="flex flex-col gap-1">
                          <span className="text-xs text-muted-foreground">Tampered</span>
                          {log.is_tampered ? (
                            <span className="flex items-center gap-1 text-red-600 dark:text-red-400">
                              <XCircle size={14} /> Yes
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-green-700 dark:text-green-400">
                              <CheckCircle2 size={14} /> No
                            </span>
                          )}
                        </div>
                        <div className="flex flex-col gap-1">
                          <span className="text-xs text-muted-foreground">Confidence</span>
                          <span className="font-medium text-foreground">
                            {(log.confidence_score * 100).toFixed(1)}%
                          </span>
                        </div>
                        {log.image_id && (
                          <div className="flex flex-col gap-1">
                            <span className="text-xs text-muted-foreground">Image ID</span>
                            <span className="text-foreground">{log.image_id}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Desktop Table Layout */}
            <div className="hidden overflow-hidden rounded-lg border border-border md:block">
              <table className="w-full text-sm">
                <thead className="bg-muted text-muted-foreground">
                  <tr>
                    <th className="px-4 py-3 text-left font-medium">Date</th>
                    <th className="px-4 py-3 text-left font-medium">Authentic</th>
                    <th className="px-4 py-3 text-left font-medium">Tampered</th>
                    <th className="px-4 py-3 text-left font-medium">Confidence</th>
                    <th className="px-4 py-3 text-left font-medium">Image ID</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {history.map(log => (
                    <tr key={log.id} className="bg-background transition-colors hover:bg-muted/50">
                      <td className="px-4 py-3 text-muted-foreground">
                        {new Date(log.created_at).toLocaleString()}
                      </td>
                      <td className="px-4 py-3">
                        {log.is_authentic ? (
                          <span className="flex items-center gap-1 text-green-700 dark:text-green-400">
                            <CheckCircle2 size={14} /> Yes
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-red-600 dark:text-red-400">
                            <XCircle size={14} /> No
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        {log.is_tampered ? (
                          <span className="flex items-center gap-1 text-red-600 dark:text-red-400">
                            <XCircle size={14} /> Yes
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-green-700 dark:text-green-400">
                            <CheckCircle2 size={14} /> No
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-foreground">
                        {(log.confidence_score * 100).toFixed(1)}%
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {log.image_id ?? '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </main>
  )
}
