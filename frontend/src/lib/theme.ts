// Confirmed Getnet brand colors only (site.getnet.com.br/guia-digital-marca):
// the red family, plus black/dark-gray neutrals. An earlier revision used an
// estimated neon set (pink/purple/cyan/lime/yellow) for chart series - none
// of those exist in the real brand guide, so charts use red + neutral
// charcoal shades instead.
export const BRAND_RED = '#EC0000'
export const BRAND_RED_2 = '#C1080F'
export const BRAND_RED_3 = '#95101E'
export const INK = '#2B2F38'
export const INK_MUTED = '#6F6F7A'

export const CHART_SERIES = [BRAND_RED, INK, BRAND_RED_2, INK_MUTED, BRAND_RED_3] as const

export function chartColorForIndex(index: number): string {
  return CHART_SERIES[index % CHART_SERIES.length]
}
