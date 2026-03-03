function SummaryBar({ summary }) {
  const items = [
    { label: 'Passed', count: summary.passed, color: 'text-green-400', bg: 'bg-green-500/10' },
    { label: 'Warnings', count: summary.warned, color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
    { label: 'Failed', count: summary.failed, color: 'text-red-400', bg: 'bg-red-500/10' },
    { label: 'Skipped', count: summary.skipped, color: 'text-gray-400', bg: 'bg-gray-500/10' },
  ]

  return (
    <div className="grid grid-cols-4 gap-3">
      {items.map((item) => (
        <div
          key={item.label}
          className="bg-sp-card border border-sp-border rounded-xl px-4 py-3 text-center"
        >
          <div className={`text-2xl font-bold ${item.color}`}>{item.count}</div>
          <div className="text-xs text-sp-text mt-1">{item.label}</div>
        </div>
      ))}
    </div>
  )
}

export default SummaryBar
