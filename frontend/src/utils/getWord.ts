export const getWord = (count: number) => {
    if (count === 1) return 'день';
    if (count > 1 && count < 5) return 'дня'
    return 'дней';
}