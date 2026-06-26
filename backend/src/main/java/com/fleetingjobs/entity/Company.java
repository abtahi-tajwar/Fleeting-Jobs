package com.fleetingjobs.entity;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;

@Entity
@Table(name = "companies")
public class Company {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, unique = true)
    private String slug;

    @Column(name = "listing_url", nullable = false, columnDefinition = "TEXT")
    private String listingUrl;

    @Column(name = "single_post_url_format", nullable = false, columnDefinition = "TEXT")
    private String singlePostUrlFormat;

    @OneToOne(mappedBy = "company", cascade = CascadeType.ALL, orphanRemoval = true)
    private CompanyParser parser;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getSlug() {
        return slug;
    }

    public void setSlug(String slug) {
        this.slug = slug;
    }

    public String getListingUrl() {
        return listingUrl;
    }

    public void setListingUrl(String listingUrl) {
        this.listingUrl = listingUrl;
    }

    public String getSinglePostUrlFormat() {
        return singlePostUrlFormat;
    }

    public void setSinglePostUrlFormat(String singlePostUrlFormat) {
        this.singlePostUrlFormat = singlePostUrlFormat;
    }

    public CompanyParser getParser() {
        return parser;
    }

    public void setParser(CompanyParser parser) {
        this.parser = parser;
    }
}
