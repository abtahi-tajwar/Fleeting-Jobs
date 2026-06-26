package com.fleetingjobs.web;

import java.util.Map;

import com.fleetingjobs.worker.WorkerClient;
import org.springframework.stereotype.Component;

@Component
public class WorkerClientHealth {

    private final WorkerClient workerClient;

    public WorkerClientHealth(WorkerClient workerClient) {
        this.workerClient = workerClient;
    }

    public boolean isWorkerReady() {
        try {
            Map<?, ?> health = workerClient.getHealth();
            Object openaiConfigured = health.get("openai_configured");
            return Boolean.TRUE.equals(openaiConfigured);
        } catch (RuntimeException ex) {
            return false;
        }
    }
}
