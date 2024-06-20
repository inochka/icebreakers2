export const getWord = (count: number) => {
    if (count === 1) return 'час';
    if (count > 1 && count < 5) return 'часа'
    return 'часов';
}