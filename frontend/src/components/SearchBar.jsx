import { Search, X } from "lucide-react";

/**
 * SearchBar Component — Modern Dark Design
 * 
 * Orange border, dark background, white text
 * Props:
 *   - value: current search value
 *   - onChange: handler for input change
 *   - placeholder: placeholder text
 *   - onClear: handler for clear button
 *   - className: extra classes
 */

export default function SearchBar({
  value,
  onChange,
  placeholder = "Search leads...",
  onClear,
  className = "",
}) {
  return (
    <div className={`relative w-full ${className}`}>
      {/* Search icon left */}
      <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-white pointer-events-none" />

      {/* Input field - DARK BG, ORANGE BORDER, WHITE TEXT */}
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="
          w-full
          pl-12 pr-12 py-3
          rounded-2xl
          bg-[#1a1a1a]
          border-2 border-orange-500
          text-white
          placeholder-zinc-500
          font-medium
          text-base
          transition-all duration-200
          focus:outline-none
          focus:border-orange-400
          focus:ring-2
          focus:ring-orange-500/30
          hover:border-orange-400
        "
      />

      {/* Clear button (X) right */}
      {value && (
        <button
          onClick={onClear}
          type="button"
          className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-zinc-400 hover:text-white transition-colors"
          aria-label="Clear search"
        >
          <X className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}

