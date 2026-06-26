package com.fleetingjobs.web;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.fleetingjobs.dto.Dto.AppConfigResponse;
import com.fleetingjobs.dto.Dto.CompanyCreateRequest;
import com.fleetingjobs.dto.Dto.CompanyResponse;
import com.fleetingjobs.service.CategoryService;
import com.fleetingjobs.service.CompanyService;
import com.fleetingjobs.service.ParserService;
import com.fleetingjobs.worker.WorkerClient;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/companies")
public class CompanyController {

    private final CompanyService companyService;

    public CompanyController(CompanyService companyService) {
        this.companyService = companyService;
    }

    @GetMapping
    public List<CompanyResponse> listCompanies() {
        return companyService.listCompanies();
    }

    @PostMapping
    public CompanyResponse createCompany(@Valid @RequestBody CompanyCreateRequest request) {
        return companyService.createCompany(request);
    }

    @GetMapping("/{companyId}")
    public CompanyResponse getCompany(@PathVariable Long companyId) {
        return companyService.getCompany(companyId);
    }
}

@RestController
@RequestMapping("/api/parsers")
class ParserController {

    private final ParserService parserService;

    ParserController(ParserService parserService) {
        this.parserService = parserService;
    }

    @GetMapping
    public List<com.fleetingjobs.dto.Dto.CompanyParserResponse> listParsers() {
        return parserService.listParsers();
    }

    @PostMapping
    public com.fleetingjobs.dto.Dto.CompanyParserResponse createParser(
            @Valid @RequestBody com.fleetingjobs.dto.Dto.CompanyParserCreateRequest request
    ) {
        return parserService.createParser(request);
    }
}

@RestController
@RequestMapping("/api")
class AppController {

    private final CategoryService categoryService;
    private final CompanyService companyService;
    private final ParserService parserService;
    private final WorkerClientHealth workerClientHealth;

    AppController(
            CategoryService categoryService,
            CompanyService companyService,
            ParserService parserService,
            WorkerClientHealth workerClientHealth
    ) {
        this.categoryService = categoryService;
        this.companyService = companyService;
        this.parserService = parserService;
        this.workerClientHealth = workerClientHealth;
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        Map<String, Object> payload = new HashMap<>();
        payload.put("status", "ok");
        payload.put("openai_configured", workerClientHealth.isWorkerReady());
        payload.put("database_connected", true);
        return payload;
    }

    @GetMapping("/config")
    public AppConfigResponse getConfig() {
        return new AppConfigResponse(
                categoryService.getCategories(),
                companyService.countCompanies(),
                parserService.countParsers()
        );
    }
}
