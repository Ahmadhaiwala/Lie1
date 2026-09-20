import { Search, X } from "lucide-react";
import { motion } from "framer-motion";

/**
 * SearchBar Component
 * 
 * Black text on light background for maximum readability.
 * Props:
 *   - value: current search value
 *   - onChange: handler for input change
 *   - placeholder: placeholder text (default "Search...")
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
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />

      {/* Input field - BLACK TEXT, LIGHT BACKGROUND */}
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-white border-2 border-gray-200 text-black placeholder-gray-500 font-medium text-sm transition-all duration-200 focus:outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/30 hover:border-gray-300"
      />

      {/* Clear button right */}
      {value && (
        <button
          onClick={onClear}
          type="button"
          className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
          aria-label="Clear search"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}

