export function useFormatters() {
  function formatPrice(value: number | null | undefined): string {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  }

  function formatNumber(value: number | null | undefined): string {
    if (value === null || value === undefined) return 'N/A';
    return new Intl.NumberFormat('en-US').format(value);
  }

  function formatPricePerSqft(value: number | null | undefined): string {
    if (value === null || value === undefined) return 'N/A';
    return `$${Math.round(value)}/sqft`;
  }

  function formatCompact(value: number | null | undefined): string {
    if (value === null || value === undefined) return 'N/A';

    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(0)}K`;
    }
    return value.toString();
  }

  function formatRelativeTime(isoString: string | null): string {
    if (!isoString) return 'Unknown';

    const now = new Date();
    const date = new Date(isoString);
    const hours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (hours < 1) {
      const minutes = Math.floor(hours * 60);
      return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    } else if (hours < 24) {
      const h = Math.floor(hours);
      return `${h} hour${h !== 1 ? 's' : ''} ago`;
    } else {
      const days = Math.floor(hours / 24);
      return `${days} day${days !== 1 ? 's' : ''} ago`;
    }
  }

  return {
    formatPrice,
    formatNumber,
    formatPricePerSqft,
    formatCompact,
    formatRelativeTime
  };
}
