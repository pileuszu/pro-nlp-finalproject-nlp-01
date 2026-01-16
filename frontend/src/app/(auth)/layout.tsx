export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="flex h-screen w-full items-center justify-center bg-gray-50">
            <div className="w-full max-w-md p-8 space-y-4 bg-white rounded-xl shadow-md">
                <div className="flex justify-center mb-6">
                    <span className="text-2xl font-bold">Pro-NLP</span>
                </div>
                {children}
            </div>
        </div>
    );
}
