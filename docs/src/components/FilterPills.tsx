import React from "react";

interface FilterPillsProps {
  options: string[];
  selected: string[];
  onChange: (nextSelected: string[]) => void;
  className?: string;
}

function FilterPills({
  options,
  selected,
  onChange,
  className = "",
}: FilterPillsProps) {
  const toggleOption = (value: string) => {
    const isSelected = selected.includes(value);
    const next = isSelected
      ? selected.filter((v) => v !== value)
      : [...selected, value];
    onChange(next);
  };

  const basePillClasses =
    "mr-2 mb-2 inline-block !whitespace-nowrap cursor-pointer select-none border px-3 py-1 text-sm font-semibold transition-colors rounded-none";

  const renderPill = (
    label: string,
    isSelected: boolean,
    onClick: () => void,
    key?: string,
  ) => (
    <button
      key={key || label}
      type="button"
      aria-pressed={isSelected}
      onClick={onClick}
      className={
        basePillClasses +
        " " +
        (isSelected
          ? "border-lava-600 bg-lava-600 text-white dark:border-lava-500 dark:bg-lava-500"
          : "border-gray-700 bg-transparent text-[#1B3139] hover:bg-gray-100 dark:border-gray-500 dark:text-gray-300 dark:hover:bg-[#2e2f30]")
      }
    >
      {label}
    </button>
  );

  return (
    <div className={className}>
      {options.map((opt) =>
        renderPill(opt, selected.includes(opt), () => toggleOption(opt), opt),
      )}
    </div>
  );
}

export default FilterPills;
