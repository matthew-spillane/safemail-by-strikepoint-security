function StatusBadge({ status }) {
  const config = {
    pass: { label: 'Pass', bg: 'bg-green-500/10', text: 'text-green-400', border: 'border-green-500/20' },
    warn: { label: 'Warning', bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/20' },
    fail: { label: 'Fail', bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/20' },
    skip: { label: 'Skipped', bg: 'bg-gray-500/10', text: 'text-gray-400', border: 'border-gray-500/20' },
  }

  const c = config[status] || config.skip

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${c.bg} ${c.text} ${c.border}`}>
      {c.label}
    </span>
  )
}

export default StatusBadge
