import React from 'react';
import { Tag } from '../types/task';

interface TagPillsProps {
  tags: Tag[];
  className?: string;
}

const TagPills: React.FC<TagPillsProps> = ({ tags, className = '' }) => {
  if (!tags || tags.length === 0) return null;

  return (
    <div className={`flex flex-wrap gap-1 ${className}`}>
      {tags.map((tag) => (
        <span
          key={tag.id}
          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800 border border-indigo-200"
        >
          {tag.name}
        </span>
      ))}
    </div>
  );
};

export default TagPills;
