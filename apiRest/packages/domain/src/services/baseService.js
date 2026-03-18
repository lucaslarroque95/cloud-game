"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ServiceError = void 0;
exports.awsCall = awsCall;
// services/baseService.ts
class ServiceError extends Error {
    constructor(message) {
        super(message);
        this.name = "ServiceError";
    }
}
exports.ServiceError = ServiceError;
async function awsCall(action, errorMsg) {
    try {
        return await action();
    }
    catch (err) {
        const msg = err?.message ||
            err?.name ||
            "Unknown AWS error";
        throw new ServiceError(`${errorMsg}: ${msg}`);
    }
}
