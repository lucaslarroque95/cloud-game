"use strict";
// models/game.model.ts
Object.defineProperty(exports, "__esModule", { value: true });
exports.GameModel = void 0;
const crypto_1 = require("crypto");
const gameModel_types_1 = require("./gameModel.types");
class GameModel {
    constructor(props) {
        this.props = props;
    }
    // 🏗️ Factory: crear nuevo juego
    static create(config = {}) {
        const now = Math.floor(Date.now() / 1000);
        const ttl = 3600;
        const finalConfig = {
            ...gameModel_types_1.DEFAULT_GAME_CONFIG,
            ...config,
        };
        return new GameModel({
            gameId: (0, crypto_1.randomUUID)(),
            status: "PLAYING",
            config: finalConfig,
            players: {},
            board: Array(9).fill(""),
            turn: finalConfig.startingPlayer === "RANDOM"
                ? Math.random() > 0.5
                    ? "X"
                    : "O"
                : finalConfig.startingPlayer,
            createdAt: now,
            updatedAt: now,
            ttl: now + ttl,
        });
    }
    // 🔄 Reconstruir desde Dynamo / repo
    static fromPrimitives(data) {
        return new GameModel(data);
    }
    // 📤 Para persistencia / transporte
    toPrimitives() {
        return { ...this.props };
    }
    // 🧠 Getters útiles
    get gameId() {
        return this.props.gameId;
    }
    get status() {
        return this.props.status;
    }
    get turn() {
        return this.props.turn;
    }
    isFinished() {
        return this.props.status === "FINISHED";
    }
}
exports.GameModel = GameModel;
