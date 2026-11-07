// Bounded concurrency restoration queue with exponential backoff

const pino = require('pino');

class RestorationQueue {
    constructor(options = {}) {
        this.concurrency = options.concurrency || 2;
        this.maxRetries = options.maxRetries || 3;
        this.baseDelayMs = options.baseDelayMs || 1000;
        this.logger = pino({ level: process.env.LOG_LEVEL || 'info' });
        this.queue = [];
        this.activeCount = 0;
    }

    add(task) {
        return new Promise((resolve, reject) => {
            this.queue.push({
                task,
                retries: 0,
                resolve,
                reject
            });
            this.processNext();
        });
    }

    async processNext() {
        if (this.activeCount >= this.concurrency || this.queue.length === 0) {
            return;
        }

        const item = this.queue.shift();
        this.activeCount++;

        this.executeWithRetry(item).finally(() => {
            this.activeCount--;
            this.processNext();
        });
    }

    async executeWithRetry(item) {
        const { task, retries, resolve, reject } = item;
        try {
            const result = await task();
            resolve(result);
        } catch (err) {
            if (retries < this.maxRetries) {
                const nextRetry = retries + 1;
                const delay = this.baseDelayMs * Math.pow(2, retries);
                this.logger.warn(
                    { retries: nextRetry, maxRetries: this.maxRetries, delay, error: err.message },
                    'Task failed, scheduling exponential backoff retry'
                );
                setTimeout(() => {
                    this.queue.push({
                        task,
                        retries: nextRetry,
                        resolve,
                        reject
                    });
                    this.processNext();
                }, delay);
            } else {
                this.logger.error({ error: err.message }, 'Task exceeded max retries in queue');
                reject(err);
            }
        }
    }

    async drain() {
        while (this.queue.length > 0 || this.activeCount > 0) {
            await new Promise((r) => setTimeout(r, 100));
        }
    }
}

module.exports = RestorationQueue;
