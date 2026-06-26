package com.fleetingjobs.service;

import java.util.List;

import com.fleetingjobs.dto.Dto.CompanyParserCreateRequest;
import com.fleetingjobs.dto.Dto.CompanyParserResponse;
import com.fleetingjobs.entity.Company;
import com.fleetingjobs.entity.CompanyParser;
import com.fleetingjobs.repository.CompanyParserRepository;
import com.fleetingjobs.repository.CompanyRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class ParserService {

    private final CompanyParserRepository parserRepository;
    private final CompanyRepository companyRepository;

    public ParserService(CompanyParserRepository parserRepository, CompanyRepository companyRepository) {
        this.parserRepository = parserRepository;
        this.companyRepository = companyRepository;
    }

    @Transactional(readOnly = true)
    public List<CompanyParserResponse> listParsers() {
        return parserRepository.findAllByOrderByIdAsc().stream()
                .map(this::toResponse)
                .toList();
    }

    @Transactional
    public CompanyParserResponse createParser(CompanyParserCreateRequest request) {
        Company company = companyRepository.findWithParserById(request.companyId())
                .orElseThrow(() -> new IllegalArgumentException("Company with id " + request.companyId() + " not found"));

        if (company.getParser() != null || parserRepository.existsByCompanyId(request.companyId())) {
            throw new IllegalArgumentException("Parser already exists for company '" + company.getName() + "'");
        }

        CompanyParser parser = new CompanyParser();
        parser.setCompany(company);
        parser.setListingPage(request.listingPage());
        parser.setCompanyPage(request.companyPage());
        company.setParser(parser);

        CompanyParser saved = parserRepository.save(parser);
        return toResponse(saved);
    }

    public long countParsers() {
        return parserRepository.count();
    }

    private CompanyParserResponse toResponse(CompanyParser parser) {
        return new CompanyParserResponse(
                parser.getId(),
                parser.getCompany().getId(),
                parser.getListingPage(),
                parser.getCompanyPage(),
                parser.getCompany().getName()
        );
    }
}
