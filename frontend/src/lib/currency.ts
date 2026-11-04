/**
 * Currency symbol resolver with international multi-market support (AUD, USD, GBP, INR, EUR).
 */
export function getCurrencySymbol(currency?: string): string {
  if (!currency) return '$';
  switch (currency.toUpperCase().trim()) {
    case 'GBP':
      return '£';
    case 'INR':
      return '₹';
    case 'EUR':
      return '€';
    case 'USD':
    case 'AUD':
    default:
      return '$';
  }
}
