package com.fleetingjobs.service;

import java.util.List;

import com.fleetingjobs.dto.Dto.CompanyCreateRequest;
import com.fleetingjobs.dto.Dto.CompanyResponse;
import com.fleetingjobs.entity.Company;
import com.fleetingjobs.repository.CompanyRepository;
import com.fleetingjobs.util.SlugUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class CompanyService {

    private final CompanyRepository companyRepository;

    public CompanyService(CompanyRepository companyRepository) {
        this.companyRepository = companyRepository;
    }

    @Transactional(readOnly = true)
    public List<CompanyResponse> listCompanies() {
        return companyRepository.findAllByOrderByNameAsc().stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional(readOnly = true)
    public CompanyResponse getCompany(Long id) {
        Company company = companyRepository.findWithParserById(id)
                .orElseThrow(() -> new IllegalArgumentException("Company not found"));
        return toResponse(company);
    }

    @Transactional
    public CompanyResponse createCompany(CompanyCreateRequest request) {
        String baseSlug = SlugUtils.slugify(request.name());
        String slug = baseSlug;
        int suffix = 1;
        while (companyRepository.existsBySlug(slug)) {
            slug = baseSlug + "-" + suffix;
            suffix++;
        }

        Company company = new Company();
        company.setName(request.name().trim());
        company.setSlug(slug);
        company.setListingUrl(request.listingUrl().trim());
        company.setSinglePostUrlFormat(request.singlePostUrlFormat().trim());

        return toResponse(companyRepository.save(company));
    }

    @Transactional(readOnly = true)
    public List<Company> listCompaniesWithParsers() {
        return companyRepository.findByParserIsNotNullOrderByNameAsc();
    }

    public long countCompanies() {
        return companyRepository.count();
    }

    private CompanyResponse toResponse(Company company) {
        return new CompanyResponse(
                company.getId(),
                company.getName(),
                company.getSlug(),
                company.getListingUrl(),
                company.getSinglePostUrlFormat(),
                company.getParser() != null
        );
    }
}
