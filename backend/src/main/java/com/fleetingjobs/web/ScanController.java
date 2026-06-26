package com.fleetingjobs.web;

import java.util.HashMap;
import java.util.Map;

import com.fleetingjobs.dto.Dto.ScanResultDto;
import com.fleetingjobs.service.ScanService;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api")
public class ScanController {

    private final ScanService scanService;
    private final WorkerClientHealth workerClientHealth;

    public ScanController(ScanService scanService, WorkerClientHealth workerClientHealth) {
        this.scanService = scanService;
        this.workerClientHealth = workerClientHealth;
    }

    @GetMapping("/scan/status")
    public Map<String, Object> scanStatus() {
        Map<String, Object> payload = new HashMap<>();
        payload.put("running", scanService.isRunning());
        payload.put("progress", scanService.getProgress());
        payload.put("result", scanService.getLastResult());
        return payload;
    }

    @PostMapping("/scan")
    public ScanResultDto startScan() {
        if (!workerClientHealth.isWorkerReady()) {
            throw new ResponseStatusException(
                    HttpStatus.BAD_REQUEST,
                    "Python worker is not reachable or OPENAI_API_KEY is not configured in worker/.env"
            );
        }

        try {
            return scanService.runScan();
        } catch (IllegalArgumentException ex) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, ex.getMessage(), ex);
        } catch (IllegalStateException ex) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, ex.getMessage(), ex);
        }
    }

    @GetMapping("/results")
    public ScanResultDto getResults() {
        return scanService.getLastResult();
    }
}
