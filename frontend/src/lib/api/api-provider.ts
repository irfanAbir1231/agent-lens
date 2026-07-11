import { apiConfig } from "./config"; import { fastApiClient } from "./fastapi-client";
export const apiProvider={mode:apiConfig.mode,dataSourceLabel:apiConfig.mode==="mock"?"Mock API":"FastAPI",fastapi:fastApiClient} as const;
