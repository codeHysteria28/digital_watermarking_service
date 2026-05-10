import { Link } from 'react-router-dom'
import { cn } from '@/lib/utils'

export function About() {
  return (
    <main className="mx-auto flex max-w-3xl flex-col gap-8 px-3 py-16 md:gap-10 md:px-4 md:py-24">
      <div className="flex flex-col gap-3">
        <h1 className="text-3xl font-bold tracking-tight text-foreground md:text-4xl">About FotoMark</h1>
        <p className="text-base text-muted-foreground md:text-lg">
          Protecting your visual work with invisible digital watermarks.
        </p>
      </div>

      <div className="flex flex-col gap-6 text-sm leading-relaxed text-foreground">
        <section className="flex flex-col gap-2">
          <h2 className="text-lg font-semibold md:text-xl">What we do</h2>
          <p className="text-muted-foreground">
            FotoMark helps users hide private messages inside images in a simple and secure way.
            It provides an easy-to-use platform for creating, storing, and retrieving protected stego images.
          </p>
        </section>

        <section className="flex flex-col gap-2">
          <h2 className="text-lg font-semibold md:text-xl">Our mission</h2>
          <p className="text-muted-foreground">
            Our mission is to make secure image-based communication more accessible. 
            FotoMark is designed to combine privacy, simplicity, and modern cloud-based access in one user-friendly tool.
          </p>
        </section>

        <section className="flex flex-col gap-2">
          <h2 className="text-lg font-semibold md:text-xl">How it works</h2>
          <p className="text-muted-foreground">
            Users upload an image, add a private message, and FotoMark embeds the message into the image.
            The protected image can then be saved and later decoded only by authorised users.
          </p>
        </section>
      </div>

      <div className="flex w-full flex-col gap-3 md:w-auto md:flex-row md:gap-4">
        <Link
          to="/register"
          className={cn(
            'rounded-md bg-primary px-6 py-3 text-center text-sm font-medium text-primary-foreground md:text-base',
            'transition-opacity hover:opacity-90 h-12 md:h-auto'
          )}
        >
          Get Started
        </Link>
        <Link
          to="/login"
          className={cn(
            'rounded-md border border-input px-6 py-3 text-center text-sm font-medium text-foreground md:text-base',
            'transition-colors hover:bg-accent h-12 md:h-auto'
          )}
        >
          Login
        </Link>
      </div>
    </main>
  )
}
