package com.fleetingjobs.entity;

import java.util.Map;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "company_parsers")
public class CompanyParser {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "company_id", nullable = false, unique = true)
    private Company company;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "listing_page", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> listingPage;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "company_page", nullable = false, columnDefinition = "jsonb")
    private Map<String, Object> companyPage;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Company getCompany() {
        return company;
    }

    public void setCompany(Company company) {
        this.company = company;
    }

    public Map<String, Object> getListingPage() {
        return listingPage;
    }

    public void setListingPage(Map<String, Object> listingPage) {
        this.listingPage = listingPage;
    }

    public Map<String, Object> getCompanyPage() {
        return companyPage;
    }

    public void setCompanyPage(Map<String, Object> companyPage) {
        this.companyPage = companyPage;
    }
}
