package com.fleetingjobs.worker;

import java.util.List;
import java.util.Map;

import com.fleetingjobs.dto.Dto.JobDetailsDto;
import com.fleetingjobs.dto.Dto.JobListingDto;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;

@Component
public class WorkerClient {

    private final RestClient restClient;

    public WorkerClient(RestClient workerRestClient) {
        this.restClient = workerRestClient;
    }

    public String scrape(String url) {
        ScrapeResponse response = post("/scrape", Map.of("url", url), ScrapeResponse.class);
        return response.html();
    }

    public List<JobListingDto> parseListing(String html, String baseUrl, Map<String, Object> listingPage) {
        ParseListingResponse response = post(
                "/parse/listing",
                Map.of("html", html, "base_url", baseUrl, "listing_page", listingPage),
                ParseListingResponse.class
        );
        return response.jobs().stream()
                .map(job -> new JobListingDto(job.title(), job.url()))
                .toList();
    }

    public ParseJobResponse parseJob(String html, Map<String, Object> companyPage) {
        return post(
                "/parse/job",
                Map.of("html", html, "company_page", companyPage),
                ParseJobResponse.class
        );
    }

    public List<JobListingDto> filterJobs(List<JobListingDto> jobs, List<String> categories) {
        List<Map<String, String>> jobPayload = jobs.stream()
                .map(job -> Map.of("title", job.title(), "url", job.url()))
                .toList();

        FilterJobsResponse response = post(
                "/llm/filter-jobs",
                Map.of("jobs", jobPayload, "categories", categories),
                FilterJobsResponse.class
        );

        return response.jobs().stream()
                .map(job -> new JobListingDto(job.title(), job.url(), job.matchedCategories()))
                .toList();
    }

    public JobDetailsDto extractDetails(
            JobListingDto job,
            String companyName,
            String careerPageUrl,
            String titleHint,
            String description
    ) {
        Map<String, Object> payload = new java.util.LinkedHashMap<>();
        payload.put("title", job.title());
        payload.put("url", job.url());
        payload.put("company_name", companyName);
        payload.put("career_page_url", careerPageUrl);
        payload.put("title_hint", titleHint);
        payload.put("description", description);
        payload.put("matched_categories", job.matchedCategories());

        ExtractDetailsResponse response = post(
                "/llm/extract-details",
                payload,
                ExtractDetailsResponse.class
        );

        return new JobDetailsDto(
                response.title(),
                response.url(),
                response.companyName(),
                response.careerPageUrl(),
                response.matchedCategories(),
                response.requiredTechSkills(),
                response.requiredSoftSkills(),
                response.location(),
                response.experienceRequired()
        );
    }

    public boolean isHealthy() {
        try {
            getHealth();
            return true;
        } catch (RuntimeException ex) {
            return false;
        }
    }

    public Map<?, ?> getHealth() {
        return restClient.get().uri("/health").retrieve().body(Map.class);
    }

    private <T> T post(String path, Object body, Class<T> responseType) {
        return restClient.post()
                .uri(path)
                .body(body)
                .retrieve()
                .body(responseType);
    }

    private record ScrapeResponse(String html) {
    }

    private record JobItem(String title, String url) {
    }

    private record ParseListingResponse(List<JobItem> jobs) {
    }

    record ParseJobResponse(String title, String description) {
    }

    private record MatchedJobItem(String title, String url, List<String> matchedCategories) {
    }

    private record FilterJobsResponse(List<MatchedJobItem> jobs) {
    }

    private record ExtractDetailsResponse(
            String title,
            String url,
            String companyName,
            String careerPageUrl,
            List<String> matchedCategories,
            List<String> requiredTechSkills,
            List<String> requiredSoftSkills,
            String location,
            String experienceRequired
    ) {
    }
}
