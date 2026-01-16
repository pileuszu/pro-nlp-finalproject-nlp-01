import { Sidebar } from "@/components/layout/Sidebar";

export default function WorkspaceLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex min-h-screen">
            <Sidebar />
            <div className="flex-1 flex flex-col">
                {/* Top Header if needed for mobile or user menu */}
                <header className="flex h-14 items-center gap-4 border-b bg-muted/40 px-6 lg:h-[60px]">
                    <div className="flex-1">
                        <h1 className="text-lg font-semibold">Workspace</h1>
                    </div>
                </header>
                <main className="flex-1 p-4 lg:p-6">{children}</main>
            </div>
        </div>
    );
}
