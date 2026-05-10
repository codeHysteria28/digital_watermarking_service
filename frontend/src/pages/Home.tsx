import { Link } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { Button } from '@/components/ui/button'

export function Home() {
  const { isAuthenticated } = useAuth()

  return (
    <main className="mx-auto flex max-w-5xl flex-col items-center justify-center gap-6 px-3 py-16 text-center md:px-4 md:py-24">
      <h1 className="text-3xl font-bold tracking-tight text-foreground md:text-5xl">
        Digital Watermarking Service
      </h1>
      <p className="max-w-xl text-base text-muted-foreground md:text-lg">
        Protect and verify your images with invisible digital watermarks.
      </p>
      {isAuthenticated ? (
        <Button size="lg" asChild className="h-12 md:h-11">
          <Link to="/upload">Get Started</Link>
        </Button>
      ) : (
        <div className="flex w-full max-w-xs flex-col gap-3 md:w-auto md:max-w-none md:flex-row md:gap-4">
          <Button size="lg" asChild className="h-12 md:h-11">
            <Link to="/register">Get Started</Link>
          </Button>
          <Button variant="secondary" size="lg" asChild className="h-12 md:h-11">
            <Link to="/login">Login</Link>
          </Button>
        </div>
      )}
    </main>
  )
}
