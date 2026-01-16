import Link from 'next/link';

export function Header() {
    return (
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-14 items-center justify-between px-4 md:px-8">
                <div className="mr-4 flex">
                    <Link href="/" className="mr-6 flex items-center space-x-2">
                        <span className="font-bold text-xl">Pro-NLP</span>
                    </Link>
                    <nav className="flex items-center space-x-6 text-sm font-medium">
                        <Link href="/recruit" className="transition-colors hover:text-foreground/80 text-foreground/60">
                            채용 공고
                        </Link>
                    </nav>
                </div>
                <div className="flex items-center space-x-4">
                    <nav className="flex items-center space-x-2">
                        <Link href="/login" className="text-sm font-medium transition-colors hover:text-primary">
                            로그인
                        </Link>
                        <Link href="/signup" className="text-sm font-medium transition-colors hover:text-primary border px-3 py-1.5 rounded-md">
                            회원가입
                        </Link>
                    </nav>
                </div>
            </div>
        </header>
    );
}
