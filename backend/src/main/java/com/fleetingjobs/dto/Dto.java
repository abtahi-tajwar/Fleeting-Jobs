package com.fleetingjobs.dto;

import java.util.List;
import java.util.Map;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public final class Dto {

    private Dto() {
    }

    public record CompanyCreateRequest(
            @NotBlank @Size(max = 255) String name,
            @NotBlank String listingUrl,
            @NotBlank String singlePostUrlFormat
    ) {
    }

    public record CompanyResponse(
            Long id,
            String name,
            String slug,
            String listingUrl,
            String singlePostUrlFormat,
            boolean hasParser
    ) {
    }

    public record CompanyParserCreateRequest(
            @NotNull Long companyId,
            @NotNull Map<String, Object> listingPage,
            @NotNull Map<String, Object> companyPage
    ) {
    }

    public record CompanyParserResponse(
            Long id,
            Long companyId,
            Map<String, Object> listingPage,
            Map<String, Object> companyPage,
            String companyName
    ) {
    }

    public record AppConfigResponse(
            List<String> categories,
            long companyCount,
            long parserCount
    ) {
    }

    public record JobListingDto(
            String title,
            String url,
            List<String> matchedCategories
    ) {
        public JobListingDto(String title, String url) {
            this(title, url, List.of());
        }
    }

    public record CompanyJobsDto(
            String companyName,
            String careerPageUrl,
            List<JobListingDto> jobs,
            String error
    ) {
        public CompanyJobsDto(String companyName, String careerPageUrl, List<JobListingDto> jobs) {
            this(companyName, careerPageUrl, jobs, null);
        }
    }

    public record JobDetailsDto(
            String title,
            String url,
            String companyName,
            String careerPageUrl,
            List<String> matchedCategories,
            List<String> requiredTechSkills,
            List<String> requiredSoftSkills,
            String location,
            String experienceRequired,
            String error
    ) {
        public JobDetailsDto(
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
            this(title, url, companyName, careerPageUrl, matchedCategories,
                    requiredTechSkills, requiredSoftSkills, location, experienceRequired, null);
        }
    }

    public record ScanProgressDto(
            String status,
            String message,
            int current,
            int total
    ) {
    }

    public record ScanResultDto(
            String status,
            List<CompanyJobsDto> companies,
            List<JobDetailsDto> jobs,
            ScanProgressDto progress,
            String error
    ) {
    }
}
