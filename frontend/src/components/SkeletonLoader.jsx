import React from 'react';

export function SkeletonCard() {
  return (
    <div className="border-2 border-gray-200 rounded-lg p-4 min-w-[140px] bg-white">
      <div className="skeleton skeleton-text" style={{ width: '40%', height: '1em', marginBottom: '1rem' }}></div>
      <div className="skeleton skeleton-text" style={{ width: '70%', height: '1.25em', marginBottom: '0.5rem' }}></div>
      <div className="skeleton skeleton-text" style={{ width: '50%', height: '0.875em', marginBottom: '1.5rem' }}></div>
      <div className="flex items-center justify-between">
        <div className="skeleton" style={{ width: '24px', height: '24px', borderRadius: '4px' }}></div>
        <div className="skeleton" style={{ width: '32px', height: '32px', borderRadius: '4px' }}></div>
      </div>
    </div>
  );
}

export function SkeletonWeek() {
  return (
    <div className="grid grid-cols-7 gap-4 min-w-max">
      {[...Array(7)].map((_, index) => (
        <SkeletonCard key={index} />
      ))}
    </div>
  );
}

export function SkeletonMonthCell() {
  return (
    <div className="border border-gray-200 rounded-lg p-3 min-h-[120px] bg-white">
      <div className="skeleton skeleton-text" style={{ width: '30%', height: '1em', marginBottom: '0.75rem' }}></div>
      <div className="skeleton skeleton-text" style={{ width: '60%', height: '0.75em', marginBottom: '0.5rem' }}></div>
      <div className="skeleton skeleton-text" style={{ width: '50%', height: '0.75em' }}></div>
    </div>
  );
}

export function SkeletonMonth() {
  return (
    <div className="p-6">
      <div className="grid grid-cols-7 gap-2 mb-2">
        {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day) => (
          <div key={day} className="text-center text-sm font-medium text-carbon-black/60 py-2">
            {day}
          </div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-2">
        {[...Array(35)].map((_, index) => (
          <SkeletonMonthCell key={index} />
        ))}
      </div>
    </div>
  );
}

export function SkeletonTable() {
  return (
    <div className="space-y-3">
      {[...Array(5)].map((_, index) => (
        <div key={index} className="border border-gray-200 rounded-lg p-4 bg-white">
          <div className="flex items-center gap-4">
            <div className="skeleton" style={{ width: '100px', height: '1em' }}></div>
            <div className="skeleton flex-1" style={{ height: '1em' }}></div>
            <div className="skeleton" style={{ width: '60px', height: '1em' }}></div>
            <div className="skeleton" style={{ width: '60px', height: '1em' }}></div>
            <div className="skeleton" style={{ width: '60px', height: '1em' }}></div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function SkeletonChatMessage() {
  return (
    <div className="p-4 bg-white border border-gray-200 rounded-lg mb-3">
      <div className="skeleton skeleton-text" style={{ width: '90%' }}></div>
      <div className="skeleton skeleton-text" style={{ width: '75%' }}></div>
      <div className="skeleton skeleton-text" style={{ width: '60%' }}></div>
    </div>
  );
}

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-2 p-4">
      <div className="flex gap-1">
        <div className="w-2 h-2 bg-persian-blue rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
        <div className="w-2 h-2 bg-persian-blue rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
        <div className="w-2 h-2 bg-persian-blue rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
      </div>
      <span className="text-sm text-gray-600">Generating your workout plan...</span>
    </div>
  );
}
