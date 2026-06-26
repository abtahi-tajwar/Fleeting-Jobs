package com.fleetingjobs.service;

import java.io.IOException;
import java.io.InputStream;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

@Service
public class CategoryService {

    private final List<String> categories;

    public CategoryService(ObjectMapper objectMapper) throws IOException {
        ClassPathResource resource = new ClassPathResource("data/job_categories.json");
        try (InputStream inputStream = resource.getInputStream()) {
            Map<?, ?> payload = objectMapper.readValue(inputStream, Map.class);
            Object rawCategories = payload.get("categories");
            if (rawCategories instanceof List<?> list) {
                this.categories = list.stream().map(String::valueOf).toList();
            } else {
                this.categories = List.of();
            }
        }
    }

    public List<String> getCategories() {
        return Collections.unmodifiableList(categories);
    }
}
