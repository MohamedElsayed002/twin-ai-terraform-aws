import Twin  from "@/components/twin"

const TwinPage = () => {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold text-center text-gray-800 mb-2">
            AI in production
          </h1>
          <div className="h-[600px]">
            <Twin/>
          </div>
        </div>
      </div>
    </main>
  )
}

export default TwinPage