package com.fleetingjobs.bootstrap;

import java.util.List;
import java.util.Map;

import com.fleetingjobs.entity.Company;
import com.fleetingjobs.entity.CompanyParser;
import com.fleetingjobs.repository.CompanyRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DataSeeder implements CommandLineRunner {

    private final CompanyRepository companyRepository;

    public DataSeeder(CompanyRepository companyRepository) {
        this.companyRepository = companyRepository;
    }

    @Override
    public void run(String... args) {
        if (companyRepository.count() > 0) {
            return;
        }

        Company company = new Company();
        company.setName("RBC");
        company.setSlug("rbc");
        company.setListingUrl("https://jobs.rbc.com/ca/en/c/technology-analytics-research-jobs");
        company.setSinglePostUrlFormat("https://jobs.rbc.com/ca/en/job/{id}");

        CompanyParser parser = new CompanyParser();
        parser.setCompany(company);
        parser.setListingPage(Map.of(
                "job_links", Map.of(
                        "selector", "a",
                        "href_contains", "/job/"
                )
        ));
        parser.setCompanyPage(Map.of(
                "fields", Map.of(
                        "title", List.of("h1", ".job-title"),
                        "description", List.of(".job-description", "[data-testid='job-description']", "main")
                )
        ));
        company.setParser(parser);

        companyRepository.save(company);
    }
}
