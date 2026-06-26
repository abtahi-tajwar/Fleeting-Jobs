package com.fleetingjobs.repository;

import java.util.List;
import java.util.Optional;

import com.fleetingjobs.entity.Company;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CompanyRepository extends JpaRepository<Company, Long> {

    @EntityGraph(attributePaths = "parser")
    List<Company> findAllByOrderByNameAsc();

    @EntityGraph(attributePaths = "parser")
    Optional<Company> findWithParserById(Long id);

    boolean existsBySlug(String slug);

    @EntityGraph(attributePaths = "parser")
    List<Company> findByParserIsNotNullOrderByNameAsc();
}
