// services/baseService.ts
export class ServiceError extends Error {
    constructor(message: string) {
      super(message);
      this.name = "ServiceError";
    }
  }
  
export async function awsCall<T>(
  action: () => Promise<T>,
  errorMsg: string
): Promise<T> {
  try {
    return await action();
  } catch (err: any) {
    const msg =
      err?.message ||
      err?.name ||
      "Unknown AWS error";

    throw new ServiceError(`${errorMsg}: ${msg}`);
  }
}