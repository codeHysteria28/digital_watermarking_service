import { useState } from 'react'
import { Link } from 'react-router-dom'
import { FingerprintPatternIcon, Moon, Sun, Menu } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useTheme } from '@/context/ThemeContext'
import { useAuth } from '@/context/AuthContext'
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from '@/components/ui/navigation-menu'
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'

function LogoPlaceholder() {
  return (
    <div className="flex items-center gap-2 text-foreground">
      <FingerprintPatternIcon />
      <span className="text-lg font-semibold text-foreground">FotoMark</span>
    </div>
  )
}

export function Header() {
  const { theme, toggle } = useTheme()
  const { isAuthenticated, logout } = useAuth()
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 border-b bg-muted/30 backdrop-blur-sm">
      <div className="mx-auto flex h-14 items-center justify-between px-3 md:h-16 md:max-w-5xl md:px-4">
        <Link to="/" aria-label="Home">
          <LogoPlaceholder />
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden items-center gap-4 md:flex">
          <NavigationMenu>
            <NavigationMenuList>
              {isAuthenticated ? (
                <>
                  <NavigationMenuItem>
                    <NavigationMenuLink asChild className={navigationMenuTriggerStyle()}>
                      <Link to="/manage">My Photos</Link>
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                  <NavigationMenuItem>
                    <NavigationMenuLink asChild className={navigationMenuTriggerStyle()}>
                      <Link to="/upload">Upload</Link>
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                  <NavigationMenuItem>
                    <NavigationMenuLink asChild className={navigationMenuTriggerStyle()}>
                      <Link to="/verify">Verify</Link>
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                  <NavigationMenuItem>
                    <NavigationMenuLink asChild className={navigationMenuTriggerStyle()}>
                      <Link to="/profile">Profile</Link>
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                  <NavigationMenuItem>
                    <NavigationMenuLink asChild className={navigationMenuTriggerStyle()}>
                      <button onClick={logout}>Sign Out</button>
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                </>
              ) : (
                <>
                  <NavigationMenuItem>
                    <NavigationMenuLink asChild className={navigationMenuTriggerStyle()}>
                      <Link to="/">Home</Link>
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                  <NavigationMenuItem>
                    <NavigationMenuLink asChild className={navigationMenuTriggerStyle()}>
                      <Link to="/about">About</Link>
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                  <NavigationMenuItem>
                    <NavigationMenuLink asChild className={navigationMenuTriggerStyle()}>
                      <Link to="/login">Login</Link>
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                  <NavigationMenuItem>
                    <Link
                      to="/register"
                      className={cn(
                        'rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground',
                        'transition-opacity hover:opacity-90'
                      )}
                    >
                      Register
                    </Link>
                  </NavigationMenuItem>
                </>
              )}
            </NavigationMenuList>
          </NavigationMenu>

          <button
            onClick={toggle}
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            className="rounded-md p-2 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          >
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        <div className="flex items-center gap-2 md:hidden">
          <button
            onClick={toggle}
            aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            className="rounded-md p-2 text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
          >
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="h-10 w-10">
                <Menu size={20} className="text-foreground" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-64">
              <SheetHeader>
                <SheetTitle className="text-base">Menu</SheetTitle>
              </SheetHeader>
              <nav className="mt-6 flex flex-col gap-1">
                {isAuthenticated ? (
                  <>
                    <Link
                      to="/manage"
                      onClick={() => setOpen(false)}
                      className="rounded-md px-4 py-2.5 text-sm font-medium transition-colors hover:bg-muted"
                    >
                      My Photos
                    </Link>
                    <Link
                      to="/upload"
                      onClick={() => setOpen(false)}
                      className="rounded-md px-4 py-2.5 text-sm font-medium transition-colors hover:bg-muted"
                    >
                      Upload
                    </Link>
                    <Link
                      to="/verify"
                      onClick={() => setOpen(false)}
                      className="rounded-md px-4 py-2.5 text-sm font-medium transition-colors hover:bg-muted"
                    >
                      Verify
                    </Link>
                    <Link
                      to="/profile"
                      onClick={() => setOpen(false)}
                      className="rounded-md px-4 py-2.5 text-sm font-medium transition-colors hover:bg-muted"
                    >
                      Profile
                    </Link>
                    <button
                      onClick={() => {
                        logout()
                        setOpen(false)
                      }}
                      className="rounded-md px-4 py-2.5 text-left text-sm font-medium transition-colors hover:bg-muted"
                    >
                      Sign Out
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      to="/"
                      onClick={() => setOpen(false)}
                      className="rounded-md px-4 py-2.5 text-sm font-medium transition-colors hover:bg-muted"
                    >
                      Home
                    </Link>
                    <Link
                      to="/about"
                      onClick={() => setOpen(false)}
                      className="rounded-md px-4 py-2.5 text-sm font-medium transition-colors hover:bg-muted"
                    >
                      About
                    </Link>
                    <Link
                      to="/login"
                      onClick={() => setOpen(false)}
                      className="rounded-md px-4 py-2.5 text-sm font-medium transition-colors hover:bg-muted"
                    >
                      Login
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setOpen(false)}
                      className="mt-2 inline-block rounded-md bg-primary px-4 py-2.5 text-left text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
                    >
                      Register
                    </Link>
                  </>
                )}
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}
