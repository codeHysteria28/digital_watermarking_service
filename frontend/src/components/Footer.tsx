export function Footer() {
  return (
    <footer className="border-t bg-background">
      <div className="mx-auto max-w-5xl px-3 py-6 text-center text-xs text-muted-foreground md:px-4">
        <div>
          &copy; {new Date().getFullYear()} FotoMark. 
        </div>
        <div>
          Damian Przysiwek and Branislav Buna. 
        </div>
      </div>
    </footer>
  )
}
