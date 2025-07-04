import Image from "next/image";

export default function Home() {
  return (
    <main className="min-h-screen p-24">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          SGE Dashboard
        </h1>
        <p className="text-gray-600">
          Welcome to the SGE Dashboard. This is a test page to verify Tailwind CSS and TypeScript setup.
        </p>
      </div>
    </main>
  )
}
