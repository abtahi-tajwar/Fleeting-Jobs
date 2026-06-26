package com.fleetingjobs.service;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.locks.ReentrantLock;

import com.fleetingjobs.dto.Dto.CompanyJobsDto;
import com.fleetingjobs.dto.Dto.JobDetailsDto;
import com.fleetingjobs.dto.Dto.JobListingDto;
import com.fleetingjobs.dto.Dto.ScanProgressDto;
import com.fleetingjobs.dto.Dto.ScanResultDto;
import com.fleetingjobs.entity.Company;
import com.fleetingjobs.worker.WorkerClient;
import org.springframework.stereotype.Service;

@Service
public class ScanService {

    private final CompanyService companyService;
    private final CategoryService categoryService;
    private final WorkerClient workerClient;
    private final ReentrantLock scanLock = new ReentrantLock();

    private ScanProgressDto progress = new ScanProgressDto("idle", "Ready", 0, 0);
    private ScanResultDto lastResult;

    public ScanService(
            CompanyService companyService,
            CategoryService categoryService,
            WorkerClient workerClient
    ) {
        this.companyService = companyService;
        this.categoryService = categoryService;
        this.workerClient = workerClient;
    }

    public ScanProgressDto getProgress() {
        return progress;
    }

    public ScanResultDto getLastResult() {
        return lastResult;
    }

    public boolean isRunning() {
        return scanLock.isLocked();
    }

    public ScanResultDto runScan() {
        if (!scanLock.tryLock()) {
            throw new IllegalStateException("A scan is already running");
        }

        try {
            List<Company> targets = companyService.listCompaniesWithParsers();
            if (targets.isEmpty()) {
                throw new IllegalArgumentException(
                        "No companies with parsers configured. Add a company and parser from the UI first."
                );
            }

            List<String> categories = categoryService.getCategories();
            List<CompanyJobsDto> companies = new ArrayList<>();
            List<JobDetailsDto> detailedJobs = new ArrayList<>();
            List<MatchedJobTarget> matchedJobs = new ArrayList<>();

            int totalSteps = targets.size();
            setProgress("running", "Starting scan", 0, totalSteps);

            for (int index = 0; index < targets.size(); index++) {
                Company company = targets.get(index);
                setProgress("running", "Parsing job listings: " + company.getName(), index, totalSteps);

                try {
                    String html = workerClient.scrape(company.getListingUrl());
                    List<JobListingDto> rawJobs = workerClient.parseListing(
                            html,
                            company.getListingUrl(),
                            company.getParser().getListingPage()
                    );
                    List<JobListingDto> matched = workerClient.filterJobs(rawJobs, categories);

                    CompanyJobsDto companyJobs = new CompanyJobsDto(
                            company.getName(),
                            company.getListingUrl(),
                            matched
                    );
                    companies.add(companyJobs);

                    for (JobListingDto job : matched) {
                        matchedJobs.add(new MatchedJobTarget(company, job));
                    }
                } catch (RuntimeException ex) {
                    companies.add(new CompanyJobsDto(
                            company.getName(),
                            company.getListingUrl(),
                            List.of(),
                            ex.getMessage()
                    ));
                }
            }

            int jobTotal = matchedJobs.size();
            setProgress("running", "Scraping matched job descriptions", 0, jobTotal);

            for (int jobIndex = 0; jobIndex < matchedJobs.size(); jobIndex++) {
                MatchedJobTarget target = matchedJobs.get(jobIndex);
                Company company = target.company();
                JobListingDto job = target.job();

                setProgress("running", "Analyzing job: " + job.title(), jobIndex, jobTotal);

                try {
                    String jobHtml = workerClient.scrape(job.url());
                    WorkerClient.ParseJobResponse parsed = workerClient.parseJob(
                            jobHtml,
                            company.getParser().getCompanyPage()
                    );

                    String description = parsed.description() == null ? "" : parsed.description().trim();
                    if (description.isBlank()) {
                        throw new IllegalArgumentException("Could not extract job description from page");
                    }

                    detailedJobs.add(workerClient.extractDetails(
                            job,
                            company.getName(),
                            company.getListingUrl(),
                            parsed.title(),
                            description
                    ));
                } catch (RuntimeException ex) {
                    detailedJobs.add(new JobDetailsDto(
                            job.title(),
                            job.url(),
                            company.getName(),
                            company.getListingUrl(),
                            job.matchedCategories(),
                            List.of(),
                            List.of(),
                            null,
                            null,
                            ex.getMessage()
                    ));
                }
            }

            ScanProgressDto completedProgress = new ScanProgressDto(
                    "completed",
                    "Scan completed",
                    totalSteps,
                    totalSteps
            );
            lastResult = new ScanResultDto("completed", companies, detailedJobs, completedProgress, null);
            progress = completedProgress;
            return lastResult;
        } finally {
            scanLock.unlock();
        }
    }

    private void setProgress(String status, String message, int current, int total) {
        progress = new ScanProgressDto(status, message, current, total);
    }

    private record MatchedJobTarget(Company company, JobListingDto job) {
    }
}
