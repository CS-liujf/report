import axios, { AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

const instance = axios.create({
  baseURL: import.meta.env.VITE_APP_BASEURL,
  timeout: 30 * 1000,
});

instance.interceptors.request.use(
    (config: AxiosRequestConfig) => config,
    (error:AxiosError) => {
      console.log(error);
    },
);

instance.interceptors.response.use(
    (response: AxiosResponse) => response.data,
    (error:AxiosError) => {
      console.log(error);
    },
);

export default instance;
