import axios, { AxiosRequestConfig, AxiosResponse } from "axios";

interface IFetchData<D> extends AxiosRequestConfig<D> {
    data?: D
}

// const baseURL = import.meta.env.VITE_APP_BASE_URL

// @ts-ignore
export const requestApi = async ({method, url, params, data}: IFetchData<D>): Promise<AxiosResponse<D>> => {
    return await axios({
        baseURL: 'http://localhost:8000/', //'http://194.113.34.33:8000/',
        method,
        url,
        data,
        params,
    });
}