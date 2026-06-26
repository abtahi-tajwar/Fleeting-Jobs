package com.fleetingjobs.repository;

import java.util.List;
import java.util.Optional;

import com.fleetingjobs.entity.CompanyParser;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CompanyParserRepository extends JpaRepository<CompanyParser, Long> {

    @EntityGraph(attributePaths = "company")
    List<CompanyParser> findAllByOrderByIdAsc();

    @EntityGraph(attributePaths = "company")
    Optional<CompanyParser> findByCompanyId(Long companyId);

    boolean existsByCompanyId(Long companyId);
}
