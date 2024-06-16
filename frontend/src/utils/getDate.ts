import {DateTime} from "luxon";

export const getDate = (date: string, format: string) => {
    return DateTime.fromISO(date).toFormat(format)
}